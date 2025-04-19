#! python3  # noqa: E265

"""Main plugin module."""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import QgsApplication, QgsSettings
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QLocale, Qt, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction

# project
from qchat.__about__ import DIR_PLUGIN_ROOT, __icon_path__, __title__, __uri_homepage__
from qchat.gui.dck_qchat import QChatWidget
from qchat.gui.dlg_settings import PlgOptionsFactory
from qchat.toolbelt import PlgLogger
from qchat.toolbelt.preferences import PlgOptionsManager

# ############################################################################
# ########## Classes ###############
# ##################################


class QChatPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log

        # translation
        # initialize the locale
        self.locale: str = QgsSettings().value("locale/userLocale", QLocale().name())[
            0:2
        ]
        locale_path: Path = (
            DIR_PLUGIN_ROOT
            / "resources"
            / "i18n"
            / f"{__title__.lower()}_{self.locale}.qm"
        )
        self.log(message=f"Translation: {self.locale}, {locale_path}", log_level=4)
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path.resolve()))
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # toolbar
        self.toolbar = self.iface.addToolBar(name=self.tr("QChat toolbar"))

        # -- QChat
        self.qchat_widget = None

        # -- Actions
        self.action_open_chat = QAction(
            QgsApplication.getThemeIcon("mMessageLog.svg"),
            self.tr("QChat"),
            self.iface.mainWindow(),
        )
        self.action_open_chat.setToolTip(self.tr("QChat"))
        self.action_open_chat.triggered.connect(self.open_chat)

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )

        self.action_help = QAction(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
            self.tr("Help"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        # -- Menu
        self.iface.addPluginToWebMenu(__title__, self.action_open_chat)
        self.iface.addPluginToWebMenu(__title__, self.action_settings)
        self.iface.addPluginToWebMenu(__title__, self.action_help)

        # -- Toolbar
        self.toolbar.addAction(self.action_open_chat)
        self.toolbar.addAction(self.action_settings)

        # documentation
        self.iface.pluginHelpMenu().addSeparator()
        self.action_help_plugin_menu_documentation = QAction(
            QIcon(str(__icon_path__)),
            f"{__title__} - Documentation",
            self.iface.mainWindow(),
        )
        self.action_help_plugin_menu_documentation.triggered.connect(
            partial(QDesktopServices.openUrl, QUrl(__uri_homepage__))
        )

        self.iface.pluginHelpMenu().addAction(
            self.action_help_plugin_menu_documentation
        )

        self.iface.initializationCompleted.connect(self.post_ui_init)

    def post_ui_init(self):
        """Run after plugin's UI has been initialized."""

        # auto reconnect to room if needed
        settings = PlgOptionsManager().get_plg_settings()
        if settings.qchat_auto_reconnect and settings.qchat_auto_reconnect_room:
            if not self.qchat_widget:
                self.qchat_widget = QChatWidget(
                    iface=self.iface,
                    parent=self.iface.mainWindow(),
                    auto_reconnect_room=settings.qchat_auto_reconnect_room,
                )
                self.iface.addDockWidget(int(Qt.RightDockWidgetArea), self.qchat_widget)
            self.qchat_widget.show()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginWebMenu(__title__, self.action_open_chat)
        self.iface.removePluginWebMenu(__title__, self.action_help)
        self.iface.removePluginWebMenu(__title__, self.action_settings)

        # -- Clean up toolbar
        del self.toolbar
        del self.qchat_widget

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove from QGIS help/extensions menu
        if self.action_help_plugin_menu_documentation:
            self.iface.pluginHelpMenu().removeAction(
                self.action_help_plugin_menu_documentation
            )

        # remove actions
        del self.action_open_chat
        del self.action_settings
        del self.action_help

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.log(
                message=self.tr("Everything ran OK."),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr("Houston, we've got a problem: {}".format(err)),
                log_level=2,
                push=True,
            )

    def open_chat(self) -> None:
        if not self.qchat_widget:
            self.qchat_widget = QChatWidget(
                iface=self.iface, parent=self.iface.mainWindow()
            )
            self.iface.addDockWidget(int(Qt.RightDockWidgetArea), self.qchat_widget)
        self.qchat_widget.show()
