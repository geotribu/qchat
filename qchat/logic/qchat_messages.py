from dataclasses import dataclass


@dataclass(init=True, frozen=True)
class QChatMessage:
    type: str
    id: str
    timestamp: int


@dataclass(init=True, frozen=True)
class QChatUncompliantMessage(QChatMessage):
    reason: str


@dataclass(init=True, frozen=True)
class QChatTextMessage(QChatMessage):
    author: str
    avatar: str | None
    text: str
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatImageMessage(QChatMessage):
    author: str
    avatar: str | None
    image_data: str
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatNbUsersMessage(QChatMessage):
    nb_users: int


@dataclass(init=True, frozen=True)
class QChatNewcomerMessage(QChatMessage):
    newcomer: str


@dataclass(init=True, frozen=True)
class QChatExiterMessage(QChatMessage):
    exiter: str


@dataclass(init=True, frozen=True)
class QChatLikeMessage(QChatMessage):
    liker_author: str
    liked_author: str
    message: str


@dataclass(init=True, frozen=True)
class QChatGeojsonMessage(QChatMessage):
    author: str
    avatar: str | None
    layer_name: str
    crs_wkt: str
    crs_authid: str
    geojson: dict
    style: str | None
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatCrsMessage(QChatMessage):
    author: str
    avatar: str | None
    crs_wkt: str
    crs_authid: str
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatBboxMessage(QChatMessage):
    author: str
    avatar: str | None
    crs_wkt: str
    crs_authid: str
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatPositionMessage(QChatMessage):
    author: str
    avatar: str | None
    crs_wkt: str
    crs_authid: str
    x: float
    y: float
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatModelMessage(QChatMessage):
    author: str
    avatar: str | None
    model_name: str
    model_group: str | None
    raw_xml: str
    in_reply_to_id: str | None = None


@dataclass(init=True, frozen=True)
class QChatScriptMessage(QChatMessage):
    author: str
    avatar: str | None
    name: str
    raw_pycode: str
    in_reply_to_id: str | None = None
