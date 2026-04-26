# Installation

## Stable version (recommended)

This plugin is published on the official QGIS plugins repository: <https://plugins.qgis.org/plugins/qchat/>.

Note that QChat is compatible with QGIS >= 3.40.

## Dependencies

Some features of the plugin rely on third-party software dependencies, that are not included in the QGIS packaging on certain platforms:

- (Py)QtWebSockets: websocket communications with gischat backends.

### Windows

The required third-party dependencies should be packaged with QGIS on Windows. So no additional installations to perform.

### Linux

Open a terminal and run the following command:

```sh
sudo apt install python3-pyqt5.qtwebsockets
```

Then restart QGIS, you should be able to use QChat.

> The above example is for Ubuntu 22.04. Adapt to your distribution.

## Beta versions released

Enable experimental extensions in the QGIS plugins manager settings panel.
