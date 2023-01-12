from dataclasses import field
from typing import List, Optional

import marshmallow
import marshmallow_dataclass
from marshmallow_dataclass import dataclass


@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    language_code: Optional[str]

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class Chat:
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    type: str

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class Entities:
    offset: int
    length: int
    type: str

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class Message:
    message_id: int
    message_from: MessageFrom = field(metadata={"data_key": "from"})
    chat: Chat
    date: Optional[int]
    text: Optional[str]
    entities: Optional[List[Entities]]

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class Update:
    update_id: int
    message: Message

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[Update]

    class Meta:
        unknown = marshmallow.EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    class Meta:
        unknown = marshmallow.EXCLUDE


GET_UPDATES_SCHEMA = marshmallow_dataclass.class_schema(GetUpdatesResponse)
SEND_MESSAGE_RESPONSE_SCHEMA = marshmallow_dataclass.class_schema(SendMessageResponse)
