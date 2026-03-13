from pydantic import BaseModel, computed_field
from datetime import datetime

class BaseMessage(BaseModel):
    message_id: str
    video_id: str
    live_chat_id: str
    timestamp: datetime

    @computed_field
    @property
    def type(self) -> str:
        return self.__class__.__name__

class ChatQuestion(BaseMessage):
    author_id: str
    author_name: str
    is_chat_sponsor: bool
    text: str

class ChatCommandInvocation(BaseMessage):
    author_id: str
    author_name: str
    is_chat_sponsor: bool
    command: str
    args: str

class UserBannedEvent(BaseMessage):
    moderator_id: str
    moderator_name: str
    ban_type: str
    ban_duration_seconds: int | None
    banned_user_id: str
    banned_user_name: str

class MemberMilestone(BaseMessage):
    author_id: str
    author_name: str
    comment: str | None
    level: str
    months: int