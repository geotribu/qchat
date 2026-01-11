# standard
import base64
import json
import tempfile
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from uuid import uuid4

# PyQGIS
from qgis.core import Qgis, QgsApplication, QgsJsonExporter, QgsMapLayer, QgsProject
from qgis.gui import QgisInterface, QgsDockWidget
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QPoint, Qt, QTimer
from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import (
    QAction,
    QCompleter,
    QFileDialog,
    QMenu,
    QMessageBox,
    QTreeWidgetItem,
    QWidget,
)

# plugin
from qchat.__about__ import __title__
from qchat.constants import (
    ADMIN_MESSAGES_NICKNAME,
    CHEATCODE_10OCLOCK,
    CHEATCODE_DIZZY,
    CHEATCODE_FLICK,
    CHEATCODE_IAMAROBOT,
    CHEATCODE_QGIS_PRO_LICENSE,
    CHEATCODE_WIZZ,
    CHEATCODES,
    QCHAT_MESSAGE_TYPE_BBOX,
    QCHAT_MESSAGE_TYPE_CRS,
    QCHAT_MESSAGE_TYPE_GEOJSON,
    QCHAT_MESSAGE_TYPE_IMAGE,
    QCHAT_MESSAGE_TYPE_LIKE,
    QCHAT_MESSAGE_TYPE_NEWCOMER,
    QCHAT_MESSAGE_TYPE_POSITION,
    QCHAT_MESSAGE_TYPE_TEXT,
    QCHAT_NICKNAME_MAXLENGTH_DEFAULT,
    QCHAT_NICKNAME_MINLENGTH,
)
from qchat.gui.effects import dizzy, flick_of_the_wrist, wizz
from qchat.gui.qchat_tree_widget_items import (
    MESSAGE_COLUMN,
    QChatAdminTreeWidgetItem,
    QChatBboxTreeWidgetItem,
    QChatCrsTreeWidgetItem,
    QChatGeojsonTreeWidgetItem,
    QChatImageTreeWidgetItem,
    QChatPositionTreeWidgetItem,
    QChatTextTreeWidgetItem,
)
from qchat.logic.qchat_api_client import QChatApiClient
from qchat.logic.qchat_messages import (
    QChatBboxMessage,
    QChatCrsMessage,
    QChatExiterMessage,
    QChatGeojsonMessage,
    QChatImageMessage,
    QChatLikeMessage,
    QChatNbUsersMessage,
    QChatNewcomerMessage,
    QChatPositionMessage,
    QChatTextMessage,
    QChatUncompliantMessage,
)
from qchat.logic.qchat_websocket import QChatWebsocket
from qchat.logic.slash_commands import SlashCommandHandler
from qchat.toolbelt import PlgLogger, PlgOptionsManager
from qchat.toolbelt.commons import open_url_in_browser, play_resource_sound
from qchat.toolbelt.preferences import PlgSettingsStructure

# -- GLOBALS --
MARKER_VALUE = "---"


class QChatWidget(QgsDockWidget):
    initialized: bool = False
    connected: bool = False
    current_channel: Optional[str] = None

    qchat_client: QChatApiClient
    qchat_ws: QChatWebsocket

    min_author_length: int
    max_author_length: int

    def __init__(
        self,
        iface: QgisInterface,
        parent: Optional[QWidget] = None,
        auto_reconnect_channel: Optional[str] = None,
    ):
        """QWidget to see and post messages on chat

        :param parent: parent widget or application
        :type parent: QWidget
        """
        super().__init__(parent)
        self.iface = iface
        self.task_manager = QgsApplication.taskManager()
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()
        uic.loadUi(Path(__file__).parent / f"{Path(__file__).stem}.ui", self)

        # Initialize slash commands handler
        self.slash_command_handler = SlashCommandHandler()

        # Setup autocomplete for slash commands
        self.command_completer = QCompleter(
            self.slash_command_handler.get_command_list()
        )
        self.command_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.command_completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self.lne_message.setCompleter(self.command_completer)
        # Connect to activated signal to handle completion selection
        self.command_completer.activated.connect(self.on_command_activated)

        # set channel to autoreconnect to when widget will open
        self.auto_reconnect_channel = auto_reconnect_channel

        # rules and status signal listener
        self.btn_rules.pressed.connect(self.on_rules_button_clicked)
        self.btn_rules.setIcon(QIcon(QgsApplication.iconPath("processingResult.svg")))
        self.btn_status.pressed.connect(self.on_status_button_clicked)
        self.btn_status.setIcon(QIcon(QgsApplication.iconPath("mIconInfo.svg")))

        # open settings signal listener
        self.btn_settings.pressed.connect(self.on_settings_button_clicked)
        self.btn_settings.setIcon(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg")
        )

        # widget opened / closed signals
        self.opened.connect(self.on_widget_opened)
        self.closed.connect(self.on_widget_closed)

        # connect signal listener
        self.connected = False
        self.btn_connect.pressed.connect(self.on_connect_button_clicked)
        self.btn_connect.setIcon(QIcon(QgsApplication.iconPath("mIconConnect.svg")))

        # tree widget initialization
        self.twg_chat.setHeaderLabels(
            [
                self.tr("Date"),
                self.tr("Nickname"),
                self.tr("Message"),
            ]
        )
        self.twg_chat.itemClicked.connect(self.on_message_clicked)
        self.twg_chat.itemDoubleClicked.connect(self.on_message_double_clicked)
        self.twg_chat.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.twg_chat.customContextMenuRequested.connect(
            self.on_custom_context_menu_requested
        )

        # list users signal listener
        self.btn_list_users.pressed.connect(self.on_list_users_button_clicked)
        self.btn_list_users.setIcon(
            QIcon(QgsApplication.iconPath("processingResult.svg"))
        )

        self.ckb_autoscroll.setChecked(True)

        # clear chat signal listener
        self.btn_clear_chat.pressed.connect(self.on_clear_chat_button_clicked)
        self.btn_clear_chat.setIcon(
            QIcon(QgsApplication.iconPath("mActionDeleteSelectedFeatures.svg"))
        )

        # initialize websocket client
        self.qchat_ws = QChatWebsocket()
        self.qchat_ws.disconnected.connect(self.on_ws_disconnected)
        self.qchat_ws.error.connect(self.on_ws_error)
        self.qchat_ws.uncompliant_message_received.connect(
            self.on_uncompliant_message_received
        )
        self.qchat_ws.text_message_received.connect(self.on_text_message_received)
        self.qchat_ws.image_message_received.connect(self.on_image_message_received)
        self.qchat_ws.nb_users_message_received.connect(
            self.on_nb_users_message_received
        )
        self.qchat_ws.newcomer_message_received.connect(
            self.on_newcomer_message_received
        )
        self.qchat_ws.exiter_message_received.connect(self.on_exiter_message_received)
        self.qchat_ws.like_message_received.connect(self.on_like_message_received)
        self.qchat_ws.geojson_message_received.connect(self.on_geojson_message_received)
        self.qchat_ws.crs_message_received.connect(self.on_crs_message_received)
        self.qchat_ws.bbox_message_received.connect(self.on_bbox_message_received)
        self.qchat_ws.position_message_received.connect(
            self.on_position_message_received
        )

        # send message signal listener
        self.lne_message.returnPressed.connect(self.on_send_button_clicked)
        self.btn_send.pressed.connect(self.on_send_button_clicked)
        self.btn_send.setIcon(
            QIcon(QgsApplication.iconPath("mActionDoubleArrowRight.svg"))
        )

        # send image message signal listener
        self.btn_send_image.pressed.connect(self.on_send_image_button_clicked)
        self.btn_send_image.setIcon(
            QIcon(QgsApplication.iconPath("mActionAddImage.svg"))
        )

        # send QGIS screenshot message signal listener
        self.btn_send_screenshot.pressed.connect(self.on_send_screenshot_button_clicked)
        self.btn_send_screenshot.setIcon(
            QIcon(QgsApplication.iconPath("mActionAddImage.svg"))
        )

        # send extent message signal listener
        self.btn_send_extent.pressed.connect(self.on_send_bbox_button_clicked)
        self.btn_send_extent.setIcon(
            QIcon(QgsApplication.iconPath("mActionViewExtentInCanvas.svg"))
        )

        # send CRS message signal listener
        self.btn_send_crs.pressed.connect(self.on_send_crs_button_clicked)
        self.btn_send_crs.setIcon(
            QIcon(QgsApplication.iconPath("mActionSetProjection.svg"))
        )

    @property
    def settings(self) -> PlgSettingsStructure:
        return self.plg_settings.get_plg_settings()

    def load_settings(self) -> None:
        """Load options from QgsSettings into UI form."""
        parsed_instance_url = urlparse(self.settings.instance_uri)
        self.grb_instance.setTitle(
            self.tr("Instance: {uri}").format(uri=parsed_instance_url.netloc)
        )
        self.grb_user.setTitle(
            self.tr("User: {nickname}").format(nickname=self.settings.nickname)
        )
        self.btn_send.setIcon(QIcon(QgsApplication.iconPath(self.settings.avatar)))

    def on_widget_opened(self) -> None:
        """
        Action called when the widget is opened
        """

        # hack to bypass multiple widget opened triggers when moving widget
        if self.initialized:
            return
        self.initialized = True

        # fill fields from saved settings
        self.load_settings()

        # initialize QChat API client
        self.qchat_client = QChatApiClient(self.settings.instance_uri)

        # fetch rules for author min/max length
        try:
            rules = self.qchat_client.get_rules()
            self.min_author_length = rules["min_author_length"]
            self.max_author_length = rules["max_author_length"]
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.min_author_length = QCHAT_NICKNAME_MINLENGTH
            self.max_author_length = QCHAT_NICKNAME_MAXLENGTH_DEFAULT

        # clear channel combobox items
        self.cbb_channel.clear()  # delete all items from comboBox

        # load channels
        self.cbb_channel.addItem(MARKER_VALUE)
        try:
            channel = self.qchat_client.get_channels()
            for channel in channel:
                self.cbb_channel.addItem(channel)
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)
        finally:
            self.current_channel = MARKER_VALUE

        self.cbb_channel.currentIndexChanged.connect(self.on_channel_changed)

        # context menu on vector layer for sending as geojson in QChat
        self.iface.layerTreeView().contextMenuAboutToShow.connect(
            self.generate_qaction_send_geojson_layer
        )

        # Note: disabled for now since it messes with vectorizing lines.
        # context menu on right-click on the canvas for sending position in QChat
        # map_canvas = self.iface.mapCanvas()
        # map_canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # map_canvas.customContextMenuRequested.connect(
        #     self.custom_qchat_position_context_menu
        # )

        # auto reconnect to channel if needed
        if self.auto_reconnect_channel:
            self.cbb_channel.setCurrentText(self.auto_reconnect_channel)

    def on_rules_button_clicked(self) -> None:
        """
        Action called when clicking on "Rules" button
        """
        try:
            rules = self.qchat_client.get_rules()
            QMessageBox.information(
                self,
                self.tr("Instance rules"),
                self.tr(
                    """Instance rules ({instance_url}):

{rules}

Main language: {main_lang}
Max message length: {max_message_length}
Min nickname length: {min_nickname_length}
Max nickname length: {max_nickname_length}"""
                ).format(
                    instance_url=self.qchat_client.instance_uri,
                    rules=rules["rules"],
                    main_lang=rules["main_lang"],
                    max_message_length=rules["max_message_length"],
                    min_nickname_length=rules["min_author_length"],
                    max_nickname_length=rules["max_author_length"],
                ),
            )
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)

    def on_status_button_clicked(self) -> None:
        """
        Action called when clicking on "Status" button
        """
        try:
            status = self.qchat_client.get_status()
            user_txt = self.tr("user")
            text = self.tr(
                """Status: {status}

Channels:

{channels_status}"""
            ).format(
                status=status["status"],
                channels_status="\n".join(
                    [
                        f"- {r['name']} : {r['nb_connected_users']} {user_txt}{'s' if r['nb_connected_users'] > 1 else ''}"
                        for r in status["channels"]
                    ]
                ),
            )
            QMessageBox.information(self, self.tr("QChat instance status"), text)
        except Exception as exc:
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)

    def on_settings_button_clicked(self) -> None:
        """
        Action called when clicking on "Settings" button
        """
        # save current instance and nickname to check afterwards if they have changed
        old_instance = self.settings.instance_uri
        old_nickname = self.settings.nickname
        self.iface.showOptionsDialog(currentPage=f"mOptionsPage{__title__}")

        # get new instance and nickname settings
        new_instance = self.settings.instance_uri
        new_nickname = self.settings.nickname

        # disconnect if instance or nickname have changed
        if old_instance != new_instance or old_nickname != new_nickname:
            self.disconnect_from_channel(log=self.connected, close_ws=self.connected)
            self.on_widget_closed()
            self.on_widget_opened()

        # reload settings
        self.load_settings()

    def on_channel_changed(self) -> None:
        """
        Action called when channel index is changed in the channel combobox
        """
        if (
            not self.min_author_length
            <= len(self.settings.nickname)
            <= self.max_author_length
        ):
            self.log(
                message=self.tr(
                    "QChat nickname not set or too short (between {min} and {max} characters). Please open settings to fix it."
                ).format(min=self.min_author_length, max=self.max_author_length),
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_text=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        old_channel = self.current_channel
        new_channel = self.cbb_channel.currentText()
        old_is_marker = old_channel != MARKER_VALUE

        if new_channel == MARKER_VALUE:
            if self.connected:
                self.disconnect_from_channel(log=old_is_marker, close_ws=old_is_marker)
            self.current_channel = MARKER_VALUE
            return

        if self.connected:
            self.disconnect_from_channel(log=old_is_marker, close_ws=old_is_marker)

        self.connect_to_channel(new_channel)
        self.current_channel = new_channel

        # write new channel value to auto-reconnect channel in settings if needed
        settings = self.settings
        if settings.auto_reconnect:
            settings.auto_reconnect_channel = new_channel
            self.plg_settings.save_from_object(settings)

    def on_connect_button_clicked(self) -> None:
        """
        Action called when clicking on "Connect" / "Disconnect" button
        """
        if self.connected:
            self.disconnect_from_channel()
        else:
            if (
                not self.min_author_length
                <= len(self.settings.nickname)
                <= self.max_author_length
            ):
                self.log(
                    message=self.tr(
                        "QChat nickname not set or too short (between {min} and {max} characters). Please open settings to fix it."
                    ).format(min=self.min_author_length, max=self.max_author_length),
                    log_level=Qgis.MessageLevel.Warning,
                    push=self.settings.notify_push_info,
                    duration=self.settings.notify_push_duration,
                    button=True,
                    button_text=self.tr("Open Settings"),
                    button_connect=self.on_settings_button_clicked,
                )
                return

            channel = self.cbb_channel.currentText()

            if channel == MARKER_VALUE:
                return

            self.connect_to_channel(channel)

    def connect_to_channel(self, channel: str) -> None:
        """
        Connect widget to a specific channel
        """
        self.qchat_ws.open(self.settings.instance_uri, channel)
        self.qchat_ws.connected.connect(partial(self.on_ws_connected, channel))

    def on_ws_connected(self, channel: str) -> None:
        """
        Action called when websocket is connected from a channel
        """
        self.btn_connect.setText(self.tr("Disconnect"))
        self.btn_list_users.setEnabled(True)
        self.grb_user.setEnabled(True)
        self.current_channel = channel

        # write new channel value to auto-reconnect channel in settings if needed
        settings = self.settings
        if settings.auto_reconnect:
            settings.auto_reconnect_channel = channel
            self.plg_settings.save_from_object(settings)

        self.connected = True
        self.twg_chat.clear()
        if self.settings.display_admin_messages:
            self.add_admin_message(
                self.tr("Connected to channel '{channel}'").format(channel=channel)
            )

        # send newcomer message to websocket
        if not self.settings.incognito_mode:
            message = QChatNewcomerMessage(
                type=QCHAT_MESSAGE_TYPE_NEWCOMER,
                id=str(uuid4()),
                timestamp=int(datetime.now().timestamp()),
                newcomer=self.settings.nickname,
            )
            self.qchat_ws.send_message(message)

    def disconnect_from_channel(self, log: bool = True, close_ws: bool = True) -> None:
        """
        Disconnect widget from the current channel
        """
        if log and self.settings.display_admin_messages:
            self.add_admin_message(
                self.tr("Disconnected from channel '{channel}'").format(
                    channel=self.current_channel
                ),
            )
        self.btn_connect.setText(self.tr("Connect"))
        self.grb_qchat.setTitle(self.tr("QChat"))
        self.btn_list_users.setEnabled(False)
        self.grb_user.setEnabled(False)
        self.connected = False
        if close_ws:
            self.qchat_ws.connected.disconnect()
            self.qchat_ws.close()

    def on_ws_disconnected(self) -> None:
        """
        Action called when websocket is disconnected
        """
        if self.connected:
            self.disconnect_from_channel(log=True, close_ws=False)
            self.cbb_channel.setCurrentText(MARKER_VALUE)
        self.log(message="Websocket disconnected")

    def on_ws_error(self, error_code: int) -> None:
        """
        Action called when an error appears on the websocket
        """
        if self.settings.display_admin_messages:
            self.add_admin_message(self.qchat_ws.error_string())
        self.log(
            message=f"{error_code}: {self.qchat_ws.error_string()}",
            log_level=Qgis.MessageLevel.Critical,
        )

    # region websocket message received

    def on_uncompliant_message_received(self, message: QChatUncompliantMessage) -> None:
        self.log(
            message=self.tr("Uncompliant message: {reason}").format(
                reason=message.reason
            ),
            application=self.tr("QChat"),
            log_level=Qgis.MessageLevel.Critical,
            push=self.settings.notify_push_info,
            duration=self.settings.notify_push_duration,
        )

    def on_text_message_received(self, message: QChatTextMessage) -> None:
        """
        Launched when a text message is received from the websocket
        """
        # check if a cheatcode is activated
        if self.settings.activate_cheatcode:
            activated = self.check_cheatcode(message.text)
            if activated:
                return

        # do not display cheatcodes even if not activated
        if message.text in CHEATCODES:
            return

        item = QChatTextTreeWidgetItem(self.twg_chat, message)

        # check if message mentions current user
        words = message.text.split(" ")
        if f"@{self.settings.nickname}" in words or "@all" in words:
            if message.author != self.settings.nickname:
                self.log(
                    message=self.tr(
                        "You were mentionned by {sender}: {message}"
                    ).format(sender=message.author, message=message.text),
                    application=self.tr("QChat"),
                    log_level=Qgis.MessageLevel.Info,
                    push=self.settings.notify_push_info,
                    duration=self.settings.notify_push_duration,
                )

                # check if a notification sound should be played
                if self.settings.play_sounds:
                    play_resource_sound(
                        self.settings.ring_tone, self.settings.sound_volume
                    )

        self.add_tree_widget_item(item)

    def on_image_message_received(self, message: QChatImageMessage) -> None:
        """
        Launched when an image message is received from the websocket
        """
        item = QChatImageTreeWidgetItem(self.twg_chat, message)
        self.add_tree_widget_item(item)

    def on_nb_users_message_received(self, message: QChatNbUsersMessage) -> None:
        """
        Launched when a nb_users message is received from the websocket
        """
        self.grb_qchat.setTitle(
            self.tr("QChat - channel: {channel} - {nb_users} {user_txt}").format(
                channel=self.current_channel,
                nb_users=message.nb_users,
                user_txt=self.tr("user") if message.nb_users <= 1 else self.tr("users"),
            )
        )

    def on_newcomer_message_received(self, message: QChatNewcomerMessage) -> None:
        """
        Launched when a newcomer message is received from the websocket
        """
        if (
            self.settings.display_admin_messages
            and message.newcomer != self.settings.nickname
        ):
            self.add_admin_message(
                text=self.tr("{newcomer} has joined the channel").format(
                    newcomer=message.newcomer
                ),
                timestamp=message.timestamp,
            )

    def on_exiter_message_received(self, message: QChatExiterMessage) -> None:
        """
        Launched when an exiter message is received from the websocket
        """
        if (
            self.settings.display_admin_messages
            and message.exiter != self.settings.nickname
        ):
            self.add_admin_message(
                text=self.tr("{exiter} has left the channel").format(
                    exiter=message.exiter
                ),
                timestamp=message.timestamp,
            )

    def on_like_message_received(self, message: QChatLikeMessage) -> None:
        """
        Launched when a like message is received from the websocket
        """
        if message.liked_author == self.settings.nickname:
            self.log(
                message=self.tr("{liker_author} liked your message: {message}").format(
                    liker_author=message.liker_author, message=message.message
                ),
                application=self.tr("QChat"),
                log_level=Qgis.MessageLevel.Success,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            # play a notification sound if enabled
            if self.settings.play_sounds:
                play_resource_sound(self.settings.ring_tone, self.settings.sound_volume)

    def on_geojson_message_received(self, message: QChatGeojsonMessage) -> None:
        """
        Launched when a geojson message is received from the websocket
        """
        item = QChatGeojsonTreeWidgetItem(self.twg_chat, message)
        self.add_tree_widget_item(item)

    def on_crs_message_received(self, message: QChatCrsMessage) -> None:
        """
        Launched when a CRS message is received from the websocket
        """
        item = QChatCrsTreeWidgetItem(self.twg_chat, message)
        self.add_tree_widget_item(item)

    def on_bbox_message_received(self, message: QChatBboxMessage) -> None:
        """
        Launched when a BBOX message is received from the websocket
        """
        item = QChatBboxTreeWidgetItem(self.twg_chat, message, self.iface.mapCanvas())
        self.add_tree_widget_item(item)

    def on_position_message_received(self, message: QChatPositionMessage) -> None:
        """
        Launched when a POSITION message is received from the websocket
        """
        item = QChatPositionTreeWidgetItem(
            self.twg_chat, message, self.iface.mapCanvas()
        )
        self.add_tree_widget_item(item)

    # endregion

    def on_message_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Action called when clicking on a chat message
        """
        item.on_click(column)

    def on_message_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Action called when double clicking on a chat message
        """
        author = item.author
        # do nothing if double click on admin message
        if author == ADMIN_MESSAGES_NICKNAME or author == self.settings.nickname:
            return
        text = self.lne_message.text()
        self.lne_message.setText(f"{text}@{author} ")
        self.lne_message.setFocus()

    def on_like_message(self, liked_author: str, msg: str) -> None:
        """
        Action called when the "Like message" action is triggered
        This may happen on right-click on a message
        """
        message = QChatLikeMessage(
            type=QCHAT_MESSAGE_TYPE_LIKE,
            id=str(uuid4()),
            timestamp=int(datetime.now().timestamp()),
            liker_author=self.settings.nickname,
            liked_author=liked_author,
            message=msg,
        )
        self.qchat_ws.send_message(message)

    def on_custom_context_menu_requested(self, point: QPoint) -> None:
        """
        Action called when right clicking on a chat message
        """
        item = self.twg_chat.itemAt(point)

        menu = QMenu(self.tr("QChat Menu"), self)

        # if this is a geojson message
        if type(item) is QChatGeojsonTreeWidgetItem:
            load_geojson_action = QAction(
                QgsApplication.getThemeIcon("mActionAddLayer.svg"),
                self.tr("Load layer in QGIS"),
            )
            load_geojson_action.triggered.connect(
                partial(item.on_click, MESSAGE_COLUMN)
            )
            menu.addAction(load_geojson_action)

        # if this is a crs message
        if type(item) is QChatCrsTreeWidgetItem:
            set_crs_action = QAction(
                QgsApplication.getThemeIcon("mActionSetProjection.svg"),
                self.tr("Set current project CRS"),
            )
            set_crs_action.triggered.connect(partial(item.on_click, MESSAGE_COLUMN))
            menu.addAction(set_crs_action)

        # if this is a bbox message
        if type(item) is QChatBboxTreeWidgetItem:
            set_bbox_action = QAction(
                QgsApplication.getThemeIcon("mActionViewExtentInCanvas.svg"),
                self.tr("Set current extent"),
            )
            set_bbox_action.triggered.connect(partial(item.on_click, MESSAGE_COLUMN))
            menu.addAction(set_bbox_action)

        # like message action if possible
        if item.can_be_liked:
            like_action = QAction(
                QgsApplication.getThemeIcon("mActionInOverview.svg"),
                self.tr("Like message"),
            )
            like_action.triggered.connect(
                partial(self.on_like_message, item.author, item.liked_message)
            )
            menu.addAction(like_action)

        # mention author action if possible
        if item.can_be_mentioned:
            mention_action = QAction(
                QgsApplication.getThemeIcon("mMessageLogRead.svg"),
                self.tr("Mention user"),
            )
            mention_action.triggered.connect(
                partial(self.on_message_double_clicked, item, 2)
            )
            menu.addAction(mention_action)

        # copy message to clipboard action if possible
        if item.can_be_copied_to_clipboard:
            copy_action = QAction(
                QgsApplication.getThemeIcon("mActionEditCopy.svg"),
                self.tr("Copy message to clipboard"),
            )
            copy_action.triggered.connect(item.copy_to_clipboard)
            menu.addAction(copy_action)

        # hide message action
        hide_action = QAction(
            QgsApplication.getThemeIcon("mActionHideSelectedLayers.svg"),
            self.tr("Hide message"),
        )
        hide_action.triggered.connect(partial(self.on_hide_message, item))
        menu.addAction(hide_action)

        menu.exec(QCursor.pos())

    def on_hide_message(self, item: QTreeWidgetItem) -> None:
        """
        Action called when hide message menu action is triggered
        """
        root = self.twg_chat.invisibleRootItem()
        (item.parent() or root).removeChild(item)

    def on_list_users_button_clicked(self) -> None:
        """
        Action called when the list users button is clicked
        """
        if self.settings.incognito_mode:
            QMessageBox.warning(
                self,
                self.tr("Registered users"),
                self.tr(
                    "You're using incognito mode. Please disable it to see registered users."
                ),
            )
            return
        try:
            users = self.qchat_client.get_registered_users(self.current_channel)
            QMessageBox.information(
                self,
                self.tr("Registered users"),
                self.tr(
                    """Registered users in channel ({channel}):

{users}"""
                ).format(channel=self.current_channel, users=",".join(users)),
            )
        except Exception as exc:
            self.iface.messageBar().pushCritical(self.tr("QChat error"), str(exc))
            self.log(message=str(exc), log_level=Qgis.MessageLevel.Critical)

    def on_clear_chat_button_clicked(self) -> None:
        """
        Action called when the clear chat button is clicked
        """
        self.twg_chat.clear()

    def on_send_button_clicked(self) -> None:
        """
        Action called when the send button is clicked
        """

        # If the completer popup is visible, ignore this call
        # The activated signal will handle it instead
        if self.command_completer.popup().isVisible():
            return

        # retrieve nickname and message
        nickname = self.settings.nickname
        avatar = self.settings.avatar
        message_text = self.lne_message.text()

        if not nickname:
            self.log(
                message=self.tr("Nickname not set : please open settings and set it"),
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_text=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        if len(nickname) < QCHAT_NICKNAME_MINLENGTH:
            self.log(
                message=self.tr(
                    "Nickname too short: must be at least 3 characters. Please open settings and set it"
                ),
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_text=self.tr("Open Settings"),
                button_connect=self.on_settings_button_clicked,
            )
            return

        if not message_text:
            return

        # Check if message is a slash command
        if self.slash_command_handler.is_command(message_text):
            result = self.slash_command_handler.execute(message_text)

            if not result.success:
                # Show error
                self.log(
                    message=result.error or self.tr("Error executing command"),
                    log_level=Qgis.MessageLevel.Warning,
                    push=True,
                    duration=3,
                )
                self.lne_message.setText("")
                return

            # Clear input
            self.lne_message.setText("")

            # If there's a local action, execute it
            if result.local_action:
                action_result = result.local_action()
                if action_result and action_result[0] == "show_message":
                    # Show message locally via QMessageBox
                    QMessageBox.information(self, self.tr("QChat"), action_result[1])
                if action_result and action_result[0] == "show_message_bar":
                    # Show message locally in QGIS message bar
                    self.iface.messageBar().pushInfo(self.tr("QChat"), action_result[1])
                return

            # If there's a message text, send it to chat
            if result.message_text:
                message_text = result.message_text
            else:
                return

        # send message to websocket
        message = QChatTextMessage(
            type=QCHAT_MESSAGE_TYPE_TEXT,
            id=str(uuid4()),
            timestamp=int(datetime.now().timestamp()),
            author=nickname,
            avatar=avatar,
            text=message_text.strip(),
        )
        self.qchat_ws.send_message(message)
        self.lne_message.setText("")

    def on_command_activated(self, completion: str) -> None:
        """
        Handle when user selects a completion from QCompleter.
        This is called when the user presses Enter while the completion popup is active.
        We defer the send action slightly to ensure QCompleter finishes its text update.
        """
        # Use QTimer.singleShot to defer the action, allowing QCompleter to finish
        QTimer.singleShot(0, self.on_send_button_clicked)

    def on_send_image_button_clicked(self) -> None:
        """
        Action called when the send image button is clicked
        """

        # select some image files on disk
        files = QFileDialog.getOpenFileNames(
            parent=self,
            caption=self.tr("Select images to send to the chat"),
            filter="Images (*.png *.jpg *.jpeg)",
        )
        for fp in files[0]:
            # send the image through the websocket
            with open(fp, "rb") as file:
                data = file.read()
                message = QChatImageMessage(
                    type=QCHAT_MESSAGE_TYPE_IMAGE,
                    id=str(uuid4()),
                    timestamp=int(datetime.now().timestamp()),
                    author=self.settings.nickname,
                    avatar=self.settings.avatar,
                    image_data=base64.b64encode(data).decode("utf-8"),
                )
                self.qchat_ws.send_message(message)

    def on_send_screenshot_button_clicked(self) -> None:
        """
        Action called when the Send QGIS screenshot button is clicked
        """

        sc_fp = Path(tempfile.gettempdir()) / "qgis_screenshot.png"
        self.iface.mapCanvas().saveAsImage(str(sc_fp))
        with open(sc_fp, "rb") as file:
            data = file.read()
            message = QChatImageMessage(
                type=QCHAT_MESSAGE_TYPE_IMAGE,
                id=str(uuid4()),
                timestamp=int(datetime.now().timestamp()),
                author=self.settings.nickname,
                avatar=self.settings.avatar,
                image_data=base64.b64encode(data).decode("utf-8"),
            )
            self.qchat_ws.send_message(message)

    def on_send_bbox_button_clicked(self) -> None:
        """
        Action called when the Send extent button is clicked
        """
        crs = QgsProject.instance().crs()
        rect = self.iface.mapCanvas().extent()
        message = QChatBboxMessage(
            type=QCHAT_MESSAGE_TYPE_BBOX,
            id=str(uuid4()),
            timestamp=int(datetime.now().timestamp()),
            author=self.settings.nickname,
            avatar=self.settings.avatar,
            crs_wkt=crs.toWkt(),
            crs_authid=crs.authid(),
            xmin=rect.xMinimum(),
            xmax=rect.xMaximum(),
            ymin=rect.yMinimum(),
            ymax=rect.yMaximum(),
        )
        self.qchat_ws.send_message(message)

    def on_send_crs_button_clicked(self) -> None:
        """
        Action called when the Send CRS button is clicked
        """
        crs = QgsProject.instance().crs()
        message = QChatCrsMessage(
            type=QCHAT_MESSAGE_TYPE_CRS,
            id=str(uuid4()),
            timestamp=int(datetime.now().timestamp()),
            author=self.settings.nickname,
            avatar=self.settings.avatar,
            crs_wkt=crs.toWkt(),
            crs_authid=crs.authid(),
        )
        self.qchat_ws.send_message(message)

    def add_admin_message(self, text: str, timestamp: Optional[int] = None) -> None:
        """
        Adds an admin message to QTreeWidget chat
        """
        item = QChatAdminTreeWidgetItem(self.twg_chat, text, timestamp)
        self.add_tree_widget_item(item)

    def add_tree_widget_item(self, item: QTreeWidgetItem) -> None:
        self.twg_chat.addTopLevelItem(item)
        if self.ckb_autoscroll.isChecked():
            self.twg_chat.scrollToItem(item)

    def on_widget_closed(self) -> None:
        """
        Action called when the widget is closed
        """
        if self.connected:
            self.disconnect_from_channel()
        self.cbb_channel.currentIndexChanged.disconnect()
        self.initialized = False

        # remove context menu on vector layer for sending as geojson in QChat
        self.iface.layerTreeView().contextMenuAboutToShow.disconnect(
            self.generate_qaction_send_geojson_layer
        )

    def check_cheatcode(self, text: str) -> bool:
        """
        Checks if a received message contains a cheatcode
        Does action if necessary
        Returns true if a cheatcode has been activated
        """
        # make QGIS shuffle for a few seconds
        if text == CHEATCODE_DIZZY:
            dizzy()
            return True

        # make QGIS flick the wrist for a few seconds
        if text == CHEATCODE_FLICK:
            flick_of_the_wrist()
            return True

        # make the entire QGIS application shake like MSN wizz effect
        if text == CHEATCODE_WIZZ:
            wizz()
            return True

        # QGIS pro license expiration message
        if text == CHEATCODE_QGIS_PRO_LICENSE:
            self.log(
                message=self.tr("Your QGIS Pro license is about to expire"),
                application="QGIS Pro",
                log_level=Qgis.MessageLevel.Warning,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
                button=True,
                button_text=self.tr("Click here to renew it"),
                button_connect=self.on_renew_clicked,
            )
            return True
        # play sounds
        if self.settings.play_sounds:
            if text in [CHEATCODE_IAMAROBOT, CHEATCODE_10OCLOCK]:
                play_resource_sound(text, self.settings.sound_volume)
                return True
        return False

    def on_renew_clicked(self) -> None:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("QGIS")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            self.tr(
                """No... it was a joke!

QGIS is Free and Open Source software, forever.
Free to use, not to make.

Visit the website ?
"""
            )
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes)
        return_value = msg_box.exec()
        if return_value == QMessageBox.StandardButton.Yes:
            open_url_in_browser("https://qgis.org/funding/donate/")

    def generate_qaction_send_geojson_layer(self, menu: QMenu) -> None:
        menu.addSeparator()
        send_geojson_action = QAction(
            QgsApplication.getThemeIcon("mMessageLog.svg"),
            self.tr("Send on QChat"),
            self.iface.mainWindow(),
        )
        send_geojson_action.triggered.connect(self.on_send_geojson_layer_to_qchat)
        menu.addAction(send_geojson_action)

    def custom_qchat_position_context_menu(self, point: QPoint) -> None:
        # TODO: find a way to get the existing context menu,
        # that is being displayed on a right-click in the canvas.
        # Rather than creating a new menu, which basically makes
        # this menu being displayed after the previous one is closed.
        menu = QMenu()

        send_position_action = QAction(
            QgsApplication.getThemeIcon("mMessageLog.svg"),
            self.tr("Send position on QChat"),
            menu,
        )
        send_position_action.triggered.connect(
            lambda: self.on_send_position_to_qchat(point)
        )
        menu.addAction(send_position_action)

        menu.exec(self.iface.mapCanvas().mapToGlobal(point))

    def on_send_position_to_qchat(self, point: QPoint) -> None:
        if not self.connected:
            self.log(
                message=self.tr(
                    "Not connected to QChat. Please connect to a channel first"
                ),
                application="QChat",
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return

        map_point = (
            self.iface.mapCanvas()
            .getCoordinateTransform()
            .toMapCoordinates(point.x(), point.y())
        )

        message = QChatPositionMessage(
            type=QCHAT_MESSAGE_TYPE_POSITION,
            id=str(uuid4()),
            timestamp=int(datetime.now().timestamp()),
            author=self.settings.nickname,
            avatar=self.settings.avatar,
            crs_wkt="TODO",
            crs_authid="TODO",
            x=map_point.x(),
            y=map_point.y(),
        )
        self.qchat_ws.send_message(message)

    def on_send_geojson_layer_to_qchat(self) -> None:
        if not self.connected:
            self.log(
                message=self.tr(
                    "Not connected to QChat. Please connect to a channel first"
                ),
                application="QChat",
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return

        layer = self.iface.activeLayer()
        if not layer:
            self.log(
                message=self.tr("No active layer in current QGIS project"),
                application=self.tr("QChat"),
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return

        if layer.type() != QgsMapLayer.LayerType.VectorLayer:
            self.log(
                message=self.tr("Only vector layers can be sent on QChat"),
                application=self.tr("QChat"),
                log_level=Qgis.MessageLevel.Critical,
                push=self.settings.notify_push_info,
                duration=self.settings.notify_push_duration,
            )
            return

        if (
            not QMessageBox.warning(
                self,
                self.tr("Sure ?"),
                self.tr(
                    """The "{layer_name}" layer will be sent to QChat.

Are you sure ?"""
                ).format(layer_name=layer.name()),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            return

        exporter = QgsJsonExporter(layer)
        exporter.setSourceCrs(layer.crs())
        exporter.setDestinationCrs(layer.crs())
        exporter.setTransformGeometries(True)
        geojson_str = exporter.exportFeatures(layer.getFeatures())

        # save and read QML style to and from temp file
        save_style_path = Path(tempfile.gettempdir()) / "qchat_layer_style.qml"
        layer.saveNamedStyle(
            str(save_style_path),
            categories=QgsMapLayer.StyleCategory.AllStyleCategories,
        )
        with open(save_style_path, "r", encoding="utf-8") as file:
            qml_style = file.read()

        message = QChatGeojsonMessage(
            type=QCHAT_MESSAGE_TYPE_GEOJSON,
            id=str(uuid4()),
            timestamp=int(datetime.now().timestamp()),
            author=self.settings.nickname,
            avatar=self.settings.avatar,
            layer_name=layer.name(),
            crs_wkt=layer.crs().toWkt(),
            crs_authid=layer.crs().authid(),
            geojson=json.loads(geojson_str),
            style=qml_style,
        )
        self.qchat_ws.send_message(message)
