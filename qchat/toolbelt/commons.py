# standard

# 3rd party
from qgis.core import Qgis
from qgis.PyQt.QtCore import QT_VERSION_STR, QUrl
from qgis.PyQt.QtGui import QDesktopServices

from qchat.__about__ import DIR_PLUGIN_ROOT
from qchat.toolbelt.log_handler import PlgLogger

# conditional import depending on Qt version
if int(QT_VERSION_STR.split(".")[0]) == 5:
    from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer  # noqa QGS103
elif int(QT_VERSION_STR.split(".")[0]) == 6:
    # see: https://doc.qt.io/qt-6/qtmultimedia-changes-qt6.html
    QMediaContent = QUrl
    from PyQt6.QtMultimedia import QMediaPlayer  # noqa QGS103
else:
    QMediaPlayer = None


def open_url_in_browser(url: str) -> bool:
    """Opens an url in a browser using user's desktop environment.

    :param url: url to open
    :type url: str

    :return: true if successful otherwise false
    :rtype: bool
    """
    return QDesktopServices.openUrl(QUrl(url))


def play_resource_sound(resource: str, volume: int) -> None:
    """Play a sound inside QGIS.

    The file_name param must be the name (without extension) of a .mp3 audio file
    inside resources/sounds folder
    """
    file_path = DIR_PLUGIN_ROOT / f"resources/sounds/{resource}.mp3"
    if not file_path.exists():
        raise FileNotFoundError(
            f"File '{resource}.wav' not found in resources/sounds folder"
        )
    play_sound(f"{file_path.resolve()}", volume)


def play_sound(file: str, volume: int) -> None:
    """Play a sound using QtMultimedia QMediaPlayer."""
    url = QUrl.fromLocalFile(file)
    if QMediaPlayer is None:
        PlgLogger.log(
            message="QMediaPlayer is not available. Sound cannot be played.",
            log_level=Qgis.MessageLevel.Warning,
        )
        return

    # play sound
    player = QMediaPlayer()
    player.setMedia(QMediaContent(url))
    player.setVolume(volume)
    player.audioAvailableChanged.connect(lambda: player.play())
    player.play()
