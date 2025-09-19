# standard
from typing import List, Optional

# PyQGIS
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QCoreApplication, QUrl
from qgis.PyQt.QtGui import QFont, QFontDatabase

# project
from qchat.toolbelt import PlgLogger, PlgOptionsManager
from qchat.toolbelt.preferences import PlgSettingsStructure


class PlgFontHelper:
    """Some helpers related to font management to avoid code duplication."""

    def __init__(self):
        """Instanciate helper"""
        self.log = PlgLogger().log
        self.plg_settings = PlgOptionsManager()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def is_font_available(self, font_family: str) -> bool:
        """Check if the specified font family is part of available font in database.

        :param font_family: _description_
        :type font_family: str
        :return: _description_
        :rtype: bool
        """
        available_fonts = QFontDatabase().families()
        return font_family in available_fonts

    def check_emoji_font(self) -> bool:
        """Check if the font used for displaying emojis is installed. If not, try to
            download it.

        :return: _description_
        :rtype: _type_
        """
        plg_settings = self.plg_settings.get_plg_settings()

        if self.is_font_available(font_family=plg_settings.messages_font_family):
            self.log(
                message=self.tr(
                    "Required font to display emojis is already installed: {}".format(
                        plg_settings.messages_font_family
                    )
                ),
                push=False,
                log_level=Qgis.MessageLevel.NoLevel,
            )
            return True
        else:
            self.log(
                message="Required font for emojis needs to be installed: {}".format(
                    plg_settings.messages_font_family
                ),
                push=False,
            )

    def download_font(
        self,
        font_family_name: Optional[str] = None,
        font_download_url: Optional[str] = None,
    ):
        """_summary_

        :param font_family_name: _description_, defaults to None
        :type font_family_name: Optional[str], optional
        :param font_download_url: _description_, defaults to None
        :type font_download_url: Optional[str], optional
        """
        plg_settings = self.plg_settings.get_plg_settings()
        if font_family_name is None:
            font_download_url = plg_settings.default_font_emoji_family
        if font_download_url is None:
            font_download_url = plg_settings.default_font_emoji_download_url

        font_manager = QgsApplication.fontManager()
        font_manager.fontDownloadErrorOccurred.connect(self.on_font_download_failed)  # type: ignore
        font_manager.fontDownloaded.connect(self.on_font_download_success)  # type: ignore
        auto_downloaded = font_manager.tryToDownloadFontFamily(family=font_family_name)
        if not auto_downloaded:
            self.log(message="not downloaded", log_level=Qgis.MessageLevel.Warning)

        font_manager.downloadAndInstallFont(
            url=QUrl(plg_settings.default_font_emoji_download_url),
            identifier="qchat-emoji-font",
        )

    def on_font_download_failed(self, error_message: Optional[str] = None):
        """Handle pyqtsignal emitted by QgsFontManager when font downloading failed.

        :param error_message: error message, defaults to None
        :type error_message: Optional[str], optional
        """
        plg_settings = self.plg_settings.get_plg_settings()
        self.log(
            message=self.tr(
                "Downloading the font {} from {} failed. Since it's required to "
                "correctly display emojis, consider to add it manually to your system. "
                "Trace: {}".format(
                    plg_settings.messages_font_family,
                    plg_settings.default_font_emoji_download_url,
                    error_message,
                )
            ),
            log_level=Qgis.MessageLevel.Critical,
            push=True,
        )

    def on_font_download_success(self, families: List[str], licensedetails: str):
        """When a font has downloaded and been locally loaded.

        :param families: specifies the font families contained in the downloaded font.
        :type families: List[str]
        :param licensedetails: corresponding font license details
        :type licensedetails: str        self.font_helper.is_font_available()
        """
        self.log(
            message=self.tr(
                "Downloading the font {} successed.".format(
                    families,
                )
            ),
            log_level=Qgis.MessageLevel.Success,
            push=True,
            button=True,
            button_text=self.tr("Font license..."),
            button_more_text=licensedetails,
        )

    def get_font_from_settings(
        self, plugin_settings: Optional[PlgSettingsStructure] = None
    ) -> QFont:
        """Retrieve font defined in plugin settings. If the saved font is not available,
        fallback to the generic Sans Serif.

        :param plugin_settings: plugin settings object. If not specified, it's dynamically loaded.
        :type plugin_settings: Optional[PlgSettingsStructure]

        :return: font object ready to use
        :rtype: QFont
        """
        if plugin_settings is None:
            plugin_settings = self.plg_settings.get_plg_settings()

        try:
            msg_font = QFont()
            msg_font.fromString(
                f"{plugin_settings.messages_font_family}, {plugin_settings.messages_font_size_pts}"
            )
            if not msg_font:
                raise ValueError("QFont failed to instanciate from given string.")
        except Exception as err:
            self.log(
                message=self.tr(
                    "Unable to retrieve the font saved in settings: {}. "
                    "Fallback to Arial. Trace: {}".format(
                        plugin_settings.messages_font_family, err
                    )
                ),
                log_level=Qgis.MessageLevel.Warning,
                push=True,
            )
            msg_font = QFont()
            msg_font.fromString("Sans Serif")

        return msg_font
