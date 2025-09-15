# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## 1.0.2 - 2025-09-15

* fix(nickname): make `getuser` compliant with qchat by @gounux in <https://github.com/geotribu/qchat/pull/24>

## 1.0.1 - 2025-09-13

* fix(conflict): rename plugin's toolbar to avoid conflicts with QTribu by @Guts in <https://github.com/geotribu/qchat/pull/21>
* feature(qchat): use system username as default nickname by @Guts in <https://github.com/geotribu/qchat/pull/19>
* refactor(consistency): move and rename QField plugin installation URL to constants module by @Guts in <https://github.com/geotribu/qchat/pull/22>
* feature(message): display date tooltip on each message by @gounux in <https://github.com/geotribu/qchat/pull/23>
* add(docs): how to use env vars to override plugin's preferences by @Guts in <https://github.com/geotribu/qchat/pull/20>

## 1.0.0 - 2025-09-03

* First QChat non-beta version.

## 1.0.0-beta2 - 2025-07-18

* Fix websocket behavior when switching channel.

## 1.0.0-beta1 - 2025-07-15

* First release generated with the [QGIS Plugins templater](https://oslandia.gitlab.io/qgis/template-qgis-plugin/).
* Port QChat code from the [QTribu plugin](https://github.com/geotribu/qtribu).
* Use `channels` instead of `rooms`.
* Add empty de, es and fr translations.
* Update unique default instance to `qchat.geotribu.net`.
