# Settings

The settings used by the plugin are integrated into the QGIS Preferences menu (Settings > Options > QChat).

## Environment variables

These parameters can be defined with environment variables, prefixed by `QGIS_QCHAT_` and with the parameter name uppercased. This allows plugin configuration to be shared through QGIS profiles and managed directly by the IT Department.

For example, to set the nickname and the instance URI on a Linux computer, you can add the following lines to your `.bashrc`, `.zshrc`, or `.profile` file:

```sh
export QGIS_QCHAT_NICKNAME="your_nickname"
export QGIS_QCHAT_REQUEST_URL_QUERY="your_instance_uri"
```

The following table lists some of the available parameters with their associated environment variable and default value:

| Parameter       | Environment variable        | Default value                |
| :-----------    | :-------------------------- | :--------------------------- |
| Auto reconnect  | `QGIS_QCHAT_AUTO_RECONNECT` | `true`                       |
| Avatar          | `QGIS_QCHAT_AVATAR`         | `mGeoPackage.svg`            |
| Instance URI    | `QGIS_QCHAT_INSTANCE_URI`   | `https://qchat.geotribu.net` |
| Nickname        | `QGIS_QCHAT_NICKNAME`       | System username grabbed by [getpass.getuser](https://docs.python.org/3/library/getpass.html#getpass.getuser) |
