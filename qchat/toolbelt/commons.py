# standard
from pathlib import Path

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices

# 3rd party
from qgis.PyQt.QtMultimedia import QMediaContent, QMediaPlayer

# project
from qchat.__about__ import DIR_PLUGIN_ROOT

web_viewer = None


def open_url_in_browser(url: str) -> bool:
    """Opens an url in a browser using user's desktop environment

    :param url: url to open
    :type url: str

    :return: true if successful otherwise false
    :rtype: bool
    """
    return QDesktopServices.openUrl(QUrl(url))


def play_resource_sound(resource: str, volume: int) -> None:
    """
    Play a sound inside QGIS
    The file_name param must be the name (without extension) of a .mp3 audio file inside resources/sounds folder
    """
    file_path = str(DIR_PLUGIN_ROOT / f"resources/sounds/{resource}.mp3")
    if not Path(file_path).is_file():
        raise FileNotFoundError(
            f"File '{resource}.wav' not found in resources/sounds folder"
        )
    play_sound(file_path, volume)


def play_sound(file: str, volume: int) -> None:
    """
    Play a sound using QtMultimedia QMediaPlayer
    """
    url = QUrl.fromLocalFile(file)
    player = QMediaPlayer()
    player.setMedia(QMediaContent(url))
    player.setVolume(volume)
    player.audioAvailableChanged.connect(lambda: player.play())
    player.play()
