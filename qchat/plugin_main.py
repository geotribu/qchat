#! python3  # noqa: E265

"""Main plugin module."""

# standard
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.core import Qgis, QgsApplication, QgsSettings
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QLocale, Qt, QTranslator, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar

# project
from qchat.__about__ import DIR_PLUGIN_ROOT, __icon_path__, __title__, __uri_homepage__
from qchat.constants import QFIELD_PLUGIN_INSTALLATION_URL
from qchat.gui.dlg_settings import PlgOptionsFactory
from qchat.toolbelt import PlgLogger
from qchat.toolbelt.commons import open_url_in_browser
from qchat.toolbelt.preferences import PlgOptionsManager

# conditional imports
try:
    from qchat.gui.dck_qchat import QChatWidget

    EXTERNAL_DEPENDENCIES_AVAILABLE: bool = True
except ImportError:
    EXTERNAL_DEPENDENCIES_AVAILABLE: bool = False

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

        # -- Toolbar
        self.qchat_toolbar: QToolBar = self.iface.addToolBar(name=f"{__title__}")
        self.qchat_toolbar.setObjectName(f"{__title__}Toolbar")

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

        self.action_open_qfield_qchat = QAction(
            QIcon(str(DIR_PLUGIN_ROOT / "resources/images/qfield.svg")),
            self.tr("QChat in QField"),
            self.iface.mainWindow(),
        )
        self.action_open_qfield_qchat.setToolTip(self.tr("QChat in QField"))
        self.action_open_qfield_qchat.triggered.connect(
            partial(
                open_url_in_browser,
                "https://github.com/geotribu/qchat-qfield-plugin",
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

        # -- Menu
        self.iface.addPluginToWebMenu(__title__, self.action_open_chat)
        self.iface.addPluginToWebMenu(__title__, self.action_open_qfield_qchat)
        self.iface.addPluginToWebMenu(__title__, self.action_settings)
        self.iface.addPluginToWebMenu(__title__, self.action_help)

        # -- Toolbar
        self.qchat_toolbar.addAction(self.action_open_chat)

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

        if not self.check_dependencies():
            return

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
        self.iface.removePluginWebMenu(__title__, self.action_open_qfield_qchat)
        self.iface.removePluginWebMenu(__title__, self.action_settings)
        self.iface.removePluginWebMenu(__title__, self.action_help)

        # -- Clean up toolbar
        del self.qchat_toolbar
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
        del self.action_open_qfield_qchat
        del self.action_settings
        del self.action_help

    def post_ui_init(self):
        """Run after plugin's UI has been initialized.

        :raises Exception: if there is no item in the feed
        """
        # auto reconnect to channel if needed
        settings = PlgOptionsManager().get_plg_settings()
        if settings.auto_reconnect and settings.auto_reconnect_channel:
            if not self.qchat_widget:
                self.qchat_widget = QChatWidget(
                    iface=self.iface,
                    parent=self.iface.mainWindow(),
                    auto_reconnect_channel=settings.auto_reconnect_channel,
                )
                self.iface.addDockWidget(
                    Qt.DockWidgetArea.RightDockWidgetArea, self.qchat_widget
                )
            self.qchat_widget.show()

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

    def check_dependencies(self) -> bool:
        """Check if all dependencies are satisfied. If not, warn the user and disable plugin.

        :return: dependencies status
        :rtype: bool
        """
        # if import failed
        if not EXTERNAL_DEPENDENCIES_AVAILABLE:
            self.log(
                message=self.tr(
                    "Error importing some of dependencies. "
                    "QChat related functions have been disabled."
                ),
                log_level=Qgis.MessageLevel.Critical,
                push=True,
                duration=0,
                button=True,
                button_text=self.tr("What to do ?"),
                button_connect=partial(
                    QDesktopServices.openUrl,
                    QUrl(QFIELD_PLUGIN_INSTALLATION_URL),
                ),
            )
            # disable plugin widgets
            self.action_open_chat.setEnabled(False)

            # add tooltip over menu
            msg_disable = self.tr(
                "Plugin disabled. Please install all dependencies and then restart QGIS."
                " Refer to the documentation for more information."
            )
            self.action_open_chat.setToolTip(msg_disable)
            return False
        else:
            self.log(message=self.tr("Dependencies satisfied"), log_level=3)
            return True

    def open_chat(self) -> None:
        if not self.qchat_widget:
            self.qchat_widget = QChatWidget(
                iface=self.iface, parent=self.iface.mainWindow()
            )
            self.iface.addDockWidget(
                Qt.DockWidgetArea.RightDockWidgetArea, self.qchat_widget
            )
        self.qchat_widget.show()
