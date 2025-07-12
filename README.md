# QChat - QGIS Plugin

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![flake8](https://img.shields.io/badge/linter-flake8-green)](https://flake8.pycqa.org/)

:speech_balloon: QChat: let's chat with your GIS fellows in QGIS !

:sound: Audio sounds come from [pixabay.com](https://pixabay.com) (see [terms of license](https://pixabay.com/service/license-summary/))

## CI/CD

Plugin is linted, tested, packaged and published with GitHub.

If you mean to deploy it to the [official QGIS plugins repository](https://plugins.qgis.org/), remember to set your OSGeo credentials (`OSGEO_USER_NAME` and `OSGEO_USER_PASSWORD`) as environment variables in your CI/CD tool.


### Documentation

The documentation is located in `docs` subfolder, written in Markdown using [myst-parser](https://myst-parser.readthedocs.io/), structured in two main parts, Usage and Contribution, generated using Sphinx (have a look to [the configuration file](./docs/conf.py)) and is automatically generated through the CI and published on Pages: <https://github.com/geotribu/qchat> (see [post generation steps](#2-build-the-documentation-locally) below).

----

## Next steps post generation

### 2. Adjust URL and build the documentation locally

> [!NOTE]
> Since it's very hard to determine which the final documentation URL will be, the templater does not set it up. You have to do it manually.
> The final URL should be something like this: <https://{user_org}.github.io/{project_slug}>. You can find it in Pages settings of your repository: <https://github.com/geotribu/qchat/settings/pages>.

1. Have a look to the [plugin's metadata.txt file](qchat/metadata.txt): review it, complete it or fix it if needed (URLs, etc.)., especially the `homepage` URL which should be to your GitLab or GitHub Pages.
1. Update the base URL of custom repository in [installation doc page](./docs/usage/installation.md).
1. Change the plugin's icon stored in `qchat/resources/images`
1. Follow the [embedded documentation to build plugin documentation locally](./docs/development/documentation.md)

----

## License

Distributed under the terms of the [`GPLv2+` license](LICENSE).

----

## Contribution

See [contribution guidelines](CONTRIBUTING.md).
