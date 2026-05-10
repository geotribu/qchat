from dataclasses import dataclass
from typing import Optional


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
    avatar: Optional[str]
    text: str
    in_reply_to_id: Optional[str] = None


@dataclass(init=True, frozen=True)
class QChatImageMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    image_data: str
    in_reply_to_id: Optional[str] = None


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
    avatar: Optional[str]
    layer_name: str
    crs_wkt: str
    crs_authid: str
    geojson: dict
    style: Optional[str]
    in_reply_to_id: Optional[str] = None


@dataclass(init=True, frozen=True)
class QChatCrsMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    crs_wkt: str
    crs_authid: str
    in_reply_to_id: Optional[str] = None


@dataclass(init=True, frozen=True)
class QChatBboxMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    crs_wkt: str
    crs_authid: str
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    in_reply_to_id: Optional[str] = None


@dataclass(init=True, frozen=True)
class QChatPositionMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    crs_wkt: str
    crs_authid: str
    x: float
    y: float
    in_reply_to_id: Optional[str] = None


@dataclass(init=True, frozen=True)
class QChatModelMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    model_name: str
    model_group: Optional[str]
    raw_xml: str


@dataclass(init=True, frozen=True)
class QChatScriptMessage(QChatMessage):
    author: str
    avatar: Optional[str]
    name: str
    raw_pycode: str
