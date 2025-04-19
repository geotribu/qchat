#! python3  # noqa: E265

"""
Plugin constants.
"""

# standard

# 3rd party

# QChat
QCHAT_NICKNAME_MINLENGTH: int = 3
ADMIN_MESSAGES_NICKNAME: str = "admin"
ADMIN_MESSAGES_AVATAR: str = "mIconWarning.svg"
ERROR_MESSAGES_COLOR: str = "#ff0000"
QCHAT_USER_AVATARS: dict[str, str] = {
    "Arrow Up": "mActionArrowUp.svg",
    "Calculate": "mActionCalculateField.svg",
    "Camera": "mIconCamera.svg",
    "Certificate": "mIconCertificate.svg",
    "Comment": "mIconInfo.svg",
    "Compressed": "mIconZip.svg",
    "Folder": "mIconFolder.svg",
    "GeoPackage": "mGeoPackage.svg",
    "GPU": "mIconGPU.svg",
    "HTML": "mActionAddHtml.svg",
    "Information": "mActionPropertiesWidget.svg",
    "Network Logger": "mIconNetworkLogger.svg",
    "Postgis": "mIconPostgis.svg",
    "Python": "mIconPythonFile.svg",
    "Pyramid": "mIconPyramid.svg",
    "Raster": "mIconRaster.svg",
    "Spatialite": "mIconSpatialite.svg",
    "Tooltip": "mActionMapTips.svg",
    "XYZ": "mIconXyz.svg",
}

# QChat cheatcodes
CHEATCODE_DIZZY: str = "givemesomecheese"
CHEATCODE_IAMAROBOT: str = "iamarobot"
CHEATCODE_10OCLOCK: str = "its10oclock"
CHEATCODE_QGIS_PRO_LICENSE: str = "qgisprolicense"

CHEATCODES = [
    CHEATCODE_DIZZY,
    CHEATCODE_IAMAROBOT,
    CHEATCODE_10OCLOCK,
    CHEATCODE_QGIS_PRO_LICENSE,
]

# QChat message types
QCHAT_MESSAGE_TYPE_UNCOMPLIANT = "uncompliant"
QCHAT_MESSAGE_TYPE_TEXT = "text"
QCHAT_MESSAGE_TYPE_IMAGE = "image"
QCHAT_MESSAGE_TYPE_NB_USERS = "nb_users"
QCHAT_MESSAGE_TYPE_NEWCOMER = "newcomer"
QCHAT_MESSAGE_TYPE_EXITER = "exiter"
QCHAT_MESSAGE_TYPE_LIKE = "like"
QCHAT_MESSAGE_TYPE_GEOJSON = "geojson"
QCHAT_MESSAGE_TYPE_CRS = "crs"
QCHAT_MESSAGE_TYPE_BBOX = "bbox"
