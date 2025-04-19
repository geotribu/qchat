#! python3  # noqa: E265

"""
Plugin settings form integrated into QGIS 'Options' menu.
"""

# standard
import platform
from functools import partial
from pathlib import Path
from urllib.parse import quote

# PyQGIS
from qgis.core import Qgis, QgsApplication
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import QMessageBox

# project
from qchat.__about__ import (
    __icon_path__,
    __title__,
    __uri_homepage__,
    __uri_tracker__,
    __version__,
)
from qchat.constants import QCHAT_USER_AVATARS
from qchat.gui.gui_commons import QVAL_ALPHANUM
from qchat.logic.qchat_api_client import QChatApiClient
from qchat.toolbelt import PlgLogger, PlgOptionsManager
from qchat.toolbelt.commons import open_url_in_browser, play_resource_sound
from qchat.toolbelt.preferences import PlgSettingsStructure

# ############################################################################
# ########## Globals ###############
# ##################################

FORM_CLASS, _ = uic.loadUiType(
    Path(__file__).parent / "{}.ui".format(Path(__file__).stem)
)


# ############################################################################
# ########## Classes ###############
# ##################################


class ConfigOptionsPage(FORM_CLASS, QgsOptionsPageWidget):
    """Settings form embedded into QGIS 'options' menu."""

    def __init__(self, parent):
        super().__init__(parent)
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

        # load UI and set objectName
        self.setupUi(self)
        self.setObjectName("mOptionsPage{}".format(__title__))

        report_context_message = quote(
            "> Reported from plugin settings\n\n"
            f"- operating system: {platform.system()} "
            f"{platform.release()}_{platform.version()}\n"
            f"- QGIS: {Qgis.QGIS_VERSION}"
            f"- plugin version: {__version__}\n"
        )

        # header
        self.lbl_title.setText(f"{__title__} - Version {__version__}")

        self.btn_rules.pressed.connect(self.show_instance_rules)
        self.btn_rules.setIcon(QIcon(QgsApplication.iconPath("processingResult.svg")))
        self.btn_discover.pressed.connect(self.discover_instances)
        self.btn_discover.setIcon(QIcon(QgsApplication.iconPath("mIconListView.svg")))

        # customization
        self.btn_help.setIcon(QIcon(QgsApplication.iconPath("mActionHelpContents.svg")))
        self.btn_help.pressed.connect(
            partial(open_url_in_browser, QUrl(__uri_homepage__))
        )

        self.btn_report.setIcon(
            QIcon(QgsApplication.iconPath("console/iconSyntaxErrorConsole.svg"))
        )

        self.btn_report.pressed.connect(
            partial(
                open_url_in_browser,
                QUrl(
                    f"{__uri_tracker__}new/?"
                    "template=10_bug_report.yml"
                    f"&about-info={report_context_message}"
                ),
            )
        )

        self.btn_reset.setIcon(QIcon(QgsApplication.iconPath("mActionUndo.svg")))
        self.btn_reset.pressed.connect(self.reset_settings)

        # check inputs
        self.lne_qchat_nickname.setValidator(QVAL_ALPHANUM)

        # avatar combobox
        self.cbb_avatars_populate()

        # play sound on ringtone changed
        self.cbb_ring_tone.currentIndexChanged.connect(self.on_ring_tone_changed)

        # load previously saved settings
        self.load_settings()

    def apply(self):
        """Called to permanently apply the settings shown in the options page (e.g. \
        save them to QgsSettings objects). This is usually called when the options \
        dialog is accepted."""
        settings = self.plg_settings.get_plg_settings()

        settings.author_nickname = self.lne_qchat_nickname.text()
        settings.author_avatar = QCHAT_USER_AVATARS.get(
            self.cbb_qchat_avatar.currentText(), "mIconInfo.svg"
        )

        instance = self.cbb_qchat_instance_uri.currentText()
        if instance.endswith("/"):
            settings.qchat_instance_uri = instance[0:-1]
        else:
            settings.qchat_instance_uri = instance
        settings.qchat_auto_reconnect = self.ckb_auto_reconnect.isChecked()
        settings.qchat_activate_cheatcode = self.ckb_cheatcodes.isChecked()
        settings.qchat_display_admin_messages = (
            self.ckb_display_admin_messages.isChecked()
        )
        settings.qchat_show_avatars = self.ckb_show_avatars.isChecked()
        settings.qchat_incognito_mode = self.ckb_incognito_mode.isChecked()
        settings.qchat_play_sounds = self.ckb_play_sounds.isChecked()
        settings.qchat_sound_volume = self.hsl_sound_volume.value()
        settings.qchat_ring_tone = self.cbb_ring_tone.currentText()
        settings.qchat_color_mention = self.cbt_color_mention.color().name()
        settings.qchat_color_self = self.cbt_color_self.color().name()
        settings.qchat_color_admin = self.cbt_color_admin.color().name()

        # misc
        settings.debug_mode = self.opt_debug.isChecked()
        settings.version = __version__

        # dump new settings into QgsSettings
        self.plg_settings.save_from_object(settings)

        if __debug__:
            self.log(
                message="DEBUG - Settings successfully saved.",
                log_level=4,
            )

    def load_settings(self):
        """Load options from QgsSettings into UI form."""
        settings = self.plg_settings.get_plg_settings()

        # author
        self.lne_qchat_nickname.setText(settings.author_nickname)

        # retrieve avatar amon values
        if settings.author_avatar in QCHAT_USER_AVATARS.values():
            self.cbb_qchat_avatar.setCurrentIndex(
                list(QCHAT_USER_AVATARS.values()).index(settings.author_avatar)
            )
        else:
            self.log(
                message="Avatar {} has not been found among available one: {}".format(
                    settings.author_avatar, ", ".join(QCHAT_USER_AVATARS.values())
                ),
                log_level=Qgis.MessageLevel.Warning,
                push=True,
            )
            self.cbb_qchat_avatar.setCurrentIndex(4)

        instance_index = self.cbb_qchat_instance_uri.findText(
            settings.qchat_instance_uri, Qt.MatchFixedString
        )
        if instance_index >= 0:
            self.cbb_qchat_instance_uri.setCurrentIndex(instance_index)
        else:
            self.cbb_qchat_instance_uri.setCurrentText(settings.qchat_instance_uri)
        self.ckb_auto_reconnect.setChecked(settings.qchat_auto_reconnect)
        self.ckb_cheatcodes.setChecked(settings.qchat_activate_cheatcode)
        self.ckb_display_admin_messages.setChecked(
            settings.qchat_display_admin_messages
        )
        self.ckb_show_avatars.setChecked(settings.qchat_show_avatars)
        self.ckb_incognito_mode.setChecked(settings.qchat_incognito_mode)
        self.ckb_play_sounds.setChecked(settings.qchat_play_sounds)
        self.hsl_sound_volume.setValue(settings.qchat_sound_volume)
        beep_index = self.cbb_ring_tone.findText(
            settings.qchat_ring_tone, Qt.MatchFixedString
        )
        if beep_index >= 0:
            self.cbb_ring_tone.setCurrentIndex(beep_index)
        self.cbt_color_mention.setColor(QColor(settings.qchat_color_mention))
        self.cbt_color_self.setColor(QColor(settings.qchat_color_self))
        self.cbt_color_admin.setColor(QColor(settings.qchat_color_admin))

        # global
        self.opt_debug.setChecked(settings.debug_mode)
        self.lbl_version_saved_value.setText(settings.version)

    def show_instance_rules(self) -> None:
        """
        Action called when clicking on the "Instance rules" button
        """
        instance_url = self.cbb_qchat_instance_uri.currentText()
        try:
            client = QChatApiClient(instance_url)
            rules = client.get_rules()
            print(rules)
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
                    instance_url=instance_url,
                    rules=rules["rules"],
                    main_lang=rules["main_lang"],
                    max_message_length=rules["max_message_length"],
                    min_nickname_length=rules["min_author_length"],
                    max_nickname_length=rules["max_author_length"],
                ),
            )
        except Exception as e:
            self.log(message=str(e), log_level=Qgis.MessageLevel.Critical)

    def discover_instances(self) -> None:
        """
        Action called when clicking on the "Discover instances" button
        """
        try:
            client = QChatApiClient(self.cbb_qchat_instance_uri.currentText())
            instances = client.get_registered_instances()
            msg = ""
            for lang, lang_instances in instances.items():
                msg += f"[{lang}]:\n"
                for li in lang_instances:
                    msg += f"- {li}\n"
                msg += "\n"
            QMessageBox.information(
                self,
                self.tr("Registered instances"),
                msg,
            )
        except Exception as e:
            self.log(message=str(e), log_level=Qgis.MessageLevel.Critical)

    def on_ring_tone_changed(self) -> None:
        """
        Action called when ringtone value is changed
        """
        play_resource_sound(
            self.cbb_ring_tone.currentText(), self.hsl_sound_volume.value()
        )

    def reset_settings(self):
        """Reset settings to default values (set in preferences.py module)."""
        default_settings = PlgSettingsStructure()

        # dump default settings into QgsSettings
        self.plg_settings.save_from_object(default_settings)

        # update the form
        self.load_settings()

    def cbb_avatars_populate(self) -> None:
        """Populate combobox of avatars."""
        # save current index
        current_item_idx = self.cbb_qchat_avatar.currentIndex()

        # clear
        self.cbb_qchat_avatar.clear()

        # populate
        for avatar_description, avatar_path in QCHAT_USER_AVATARS.items():
            # avatar
            self.cbb_qchat_avatar.addItem(
                QIcon(QgsApplication.iconPath(avatar_path)),
                avatar_description,
            )

        # restore current index
        self.cbb_qchat_avatar.setCurrentIndex(current_item_idx)


class PlgOptionsFactory(QgsOptionsWidgetFactory):
    """Factory for options widget."""

    def __init__(self):
        """Constructor."""
        super().__init__()

    def icon(self) -> QIcon:
        """Returns plugin icon, used to as tab icon in QGIS options tab widget.

        :return: _description_
        :rtype: QIcon
        """
        return QIcon(str(__icon_path__))

    def createWidget(self, parent) -> ConfigOptionsPage:
        """Create settings widget.

        :param parent: Qt parent where to include the options page.
        :type parent: QObject

        :return: options page for tab widget
        :rtype: ConfigOptionsPage
        """
        return ConfigOptionsPage(parent)

    def title(self) -> str:
        """Returns plugin title, used to name the tab in QGIS options tab widget.

        :return: plugin title from about module
        :rtype: str
        """
        return __title__

    def helpId(self) -> str:
        """Returns plugin help URL.

        :return: plugin homepage url from about module
        :rtype: str
        """
        return __uri_homepage__
