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
    from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer  # noqa QGS103
    qt6_player = QMediaPlayer()
    qt6_audio_output = QAudioOutput()
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
            f"File '{resource}.mp3' not found in resources/sounds folder"
        )
    play_sound(f"{file_path.resolve()}", volume)


def play_sound(file: str, volume: int) -> None:
    """Play a sound using QtMultimedia QMediaPlayer."""
    if QMediaPlayer is None:
        PlgLogger.log(
            message="QMediaPlayer is not available. Sound cannot be played.",
            log_level=Qgis.MessageLevel.Warning,
        )
        return

    url = QUrl.fromLocalFile(file)
    # play sound
    if int(QT_VERSION_STR.split(".")[0]) == 5:
        qt5_player = QMediaPlayer()
        qt5_player.setMedia(QMediaContent(url))
        qt5_player.setVolume(volume)
        qt5_player.audioAvailableChanged.connect(lambda: qt5_player.play())
        qt5_player.play()
    elif int(QT_VERSION_STR.split(".")[0]) == 6:
        # expects a float between 0 and 1
        qt6_audio_output.setVolume(volume / 100.0)
        qt6_player.setAudioOutput(qt6_audio_output)
        qt6_player.setSource(url)
        qt6_player.play()
