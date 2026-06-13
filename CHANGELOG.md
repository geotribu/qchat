# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## 1.6.0 - 2026-06-13

### Features and enhancements 🎉

* build(deps): update pytest-cov requirement from >=4 to >=7.1.0 in /requirements by @dependabot[bot] in https://github.com/geotribu/qchat/pull/78
* build(deps): update myst-parser requirement from >=2 to >=5.1.0 in /requirements by @dependabot[bot] in https://github.com/geotribu/qchat/pull/80
* build(deps): update sphinx-rtd-theme requirement from >=2 to >=3.1.0 in /requirements by @dependabot[bot] in https://github.com/geotribu/qchat/pull/79
* build(deps-dev): update flake8-builtins requirement from >=2.2 to >=3.1.0 in /requirements by @dependabot[bot] in https://github.com/geotribu/qchat/pull/82
* build(deps): update packaging requirement from >=23 to >=26.2 in /requirements by @dependabot[bot] in https://github.com/geotribu/qchat/pull/81
* feat: add users to text autocomplete by @gounux in https://github.com/geotribu/qchat/pull/77
* feature: add `/grid` slash command by @gounux in https://github.com/geotribu/qchat/pull/45
* feat: (re)enable send and receive position messages by @gounux in https://github.com/geotribu/qchat/pull/85
* feat: add send and receive support for models and scripts messages by @gounux in https://github.com/geotribu/qchat/pull/84

### Tooling 🔧

* chore: bump tooling python versions to `3.12` by @gounux in https://github.com/geotribu/qchat/pull/83

## 1.5.0 - 2026-05-30

### Features and enhancements 🎉

* feat: auto-wrap text messages column in the treewidget by @gounux in https://github.com/geotribu/qchat/pull/74
* ui: change message style of geo messages by @gounux in https://github.com/geotribu/qchat/pull/75

### Other Changes

* fix: fix `QtMultimedia` import on Qt6 by @gounux in https://github.com/geotribu/qchat/pull/73

## 1.4.0 - 2026-05-09

### Features and enhancements 🎉

* feat(qchat): add `/vortex` slash command by @gounux in https://github.com/geotribu/qchat/pull/65

### Tooling 🔧

* build(deps): bump dawidd6/action-download-artifact from 12 to 13 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/57
* build(deps): bump actions/upload-artifact from 6 to 7 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/59
* build(deps): bump dawidd6/action-download-artifact from 13 to 16 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/58
* build(deps): bump actions/download-artifact from 7 to 8 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/60
* build(deps): bump actions/configure-pages from 5 to 6 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/63
* build(deps): bump dawidd6/action-download-artifact from 16 to 19 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/62
* build(deps): bump actions/deploy-pages from 4 to 5 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/61
* build(deps): bump actions/upload-pages-artifact from 4 to 5 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/68
* build(deps): bump dawidd6/action-download-artifact from 19 to 21 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/67
* build(deps): bump softprops/action-gh-release from 2 to 3 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/69
* ci(qchat): move linter to official `pyqgis4-checker` image by @gounux in https://github.com/geotribu/qchat/pull/66

### Other Changes

* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/geotribu/qchat/pull/64
* tooling(pre-commit): add `bandit` pre-commit hook by @gounux in https://github.com/geotribu/qchat/pull/70

## 1.3.0 - 2026-01-25

### Features and enhancements 🎉

* back to 00's msn by @lbartoletti in https://github.com/geotribu/qchat/pull/52
* feature: display a confirmation message based on a new setting by @gounux in https://github.com/geotribu/qchat/pull/54

### Tooling 🔧

* ci: publish matrix message on new release by @gounux in https://github.com/geotribu/qchat/pull/55

### Other Changes

* fix(qchat): consider flick message in constants by @gounux in https://github.com/geotribu/qchat/pull/53

## 1.2.0 - 2026-01-10

### Features and enhancements 🎉

* feat: add `/dizz` and `/flick` slash commands by @gounux in https://github.com/geotribu/qchat/pull/44

### Tooling 🔧

* build(deps): bump actions/checkout from 5 to 6 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/43
* build(deps): bump actions/download-artifact from 6 to 7 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/46
* build(deps): bump actions/cache from 4 to 5 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/47
* build(deps): bump dawidd6/action-download-artifact from 11 to 12 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/48
* build(deps): bump actions/upload-artifact from 5 to 6 by @dependabot[bot] in https://github.com/geotribu/qchat/pull/49

### Other Changes

* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in https://github.com/geotribu/qchat/pull/50

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
