from dataclasses import dataclass
from datetime import datetime
from typing import Union


@dataclass
class ChatQuestion:
    timestamp: datetime
    message_id: str
    live_chat_id: str
    channel_name: str
    channel_id: str
    is_chat_sponsor: bool
    text: str


@dataclass
class ModerationAction:
    timestamp: datetime
    live_chat_id: str
    moderator_channel_id: str
    moderator_channel: str
    action_type: str
    target_message_id: str | None
    message_id: str
    text: str


@dataclass
class MemberMilestone:
    timestamp: datetime
    message_id: str
    live_chat_id: str
    channel_name: str
    channel_id: str
    months: int


@dataclass
class ChatCommandInvocation:
    timestamp: datetime
    message_id: str
    live_chat_id: str
    channel_name: str
    channel_id: str
    is_chat_sponsor: bool
    command: str
    args: str


@dataclass
class ChatMessage:
    timestamp: datetime
    message_id: str
    live_chat_id: str
    channel_name: str
    channel_id: str
    is_chat_sponsor: bool
    text: str


ChatEvent = Union[
    ChatMessage,
    ChatQuestion,
    ModerationAction,
    MemberMilestone,
    ChatCommandInvocation,
]
