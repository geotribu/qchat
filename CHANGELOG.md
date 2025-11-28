# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## 1.1.1 - 2025-11-28

### Documentation 📖

* compat: set min qgis version to 3.40 by @gounux in https://github.com/geotribu/qchat/pull/41

## 1.1.0 - 2025-11-28

### Features and enhancements 🎉

* update(ui): new icon by @Guts in https://github.com/geotribu/qchat/pull/30
* feat(ui): ask for confirmation before sending a vector layer to QChat by @gounux in https://github.com/geotribu/qchat/pull/33
* fix(ui): disable sending position on canvas right-clic by @gounux in https://github.com/geotribu/qchat/pull/37
* feat: Add Discord-style slash commands to QChat by @lbartoletti in https://github.com/geotribu/qchat/pull/35
* Cleanier versions for the logo by @sylvainbeo in https://github.com/geotribu/qchat/pull/39

### Tooling 🔧

* build(deps): bump actions/setup-python from 5 to 6 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/28
* build(deps): bump actions/labeler from 5 to 6 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/27
* build(deps): bump actions/download-artifact from 5 to 6 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/31
* build(deps): bump actions/upload-artifact from 4 to 5 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/32

### Documentation 📖

* Documentation: add slash commands by @lbartoletti in https://github.com/geotribu/qchat/pull/40

### Other Changes

* update(tooling): remove black in favor of ruff format by @Guts in https://github.com/geotribu/qchat/pull/26
* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/geotribu/qchat/pull/29
* style(icon): Add CAD icon from cadtools by @lbartoletti in https://github.com/geotribu/qchat/pull/34

## New Contributors

* @pre-commit-ci[bot] made their first contribution in https://github.com/geotribu/qchat/pull/29
* @lbartoletti made their first contribution in https://github.com/geotribu/qchat/pull/34
* @sylvainbeo made their first contribution in https://github.com/geotribu/qchat/pull/39

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
