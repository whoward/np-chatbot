import asyncio
import random
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone

from np_chatbot.types import (
    ChatCommandInvocation,
    ChatMessage,
    ChatQuestion,
    MemberMilestone,
    ModerationAction,
)


async def mock_chat_iterator(
    *,
    rate: float = 2.0,
    p_ask: float = 0.1,
    p_command: float = 0.05,
    p_milestone: float = 0.02,
    p_moderation: float = 0.01,
    live_chat_id: str = "mock_live_chat_id",
) -> AsyncIterator[ChatMessage | ChatQuestion | ModerationAction | MemberMilestone | ChatCommandInvocation]:
    start = datetime.now(timezone.utc)
    msg_id = 0
    while True:
        await asyncio.sleep(1.0 / rate)
        msg_id += 1
        ts = start + timedelta(seconds=(msg_id - 1) / rate)
        r = random.random()
        cum = p_ask
        if r < cum:
            yield ChatQuestion(
                timestamp=ts,
                message_id=f"msg_{msg_id}",
                live_chat_id=live_chat_id,
                channel_name=f"Viewer{msg_id}",
                channel_id=f"channel_{msg_id}",
                is_chat_sponsor=random.choice([True, False]),
                text=random.choice(["what time is it?", "how does X work?"]),
            )
            continue
        cum += p_command
        if r < cum:
            yield ChatCommandInvocation(
                timestamp=ts,
                message_id=f"msg_{msg_id}",
                live_chat_id=live_chat_id,
                channel_name=f"Viewer{msg_id}",
                channel_id=f"channel_{msg_id}",
                is_chat_sponsor=random.choice([True, False]),
                command=random.choice(["!hello", "!discord"]),
                args="",
            )
            continue
        cum += p_milestone
        if r < cum:
            yield MemberMilestone(
                timestamp=ts,
                message_id=f"msg_{msg_id}",
                live_chat_id=live_chat_id,
                channel_name=f"Member{msg_id}",
                channel_id=f"channel_{msg_id}",
                months=random.randint(1, 24),
            )
            continue
        cum += p_moderation
        if r < cum:
            yield ModerationAction(
                timestamp=ts,
                live_chat_id=live_chat_id,
                moderator_channel_id="channel_mod_1",
                moderator_channel="Moderator",
                action_type="timeout",
                target_message_id=f"msg_{msg_id - 1}",
                message_id=f"msg_{msg_id}",
                text="",
            )
            continue
        yield ChatMessage(
            timestamp=ts,
            message_id=f"msg_{msg_id}",
            live_chat_id=live_chat_id,
            channel_name=f"Viewer{msg_id}",
            channel_id=f"channel_{msg_id}",
            is_chat_sponsor=random.choice([True, False]),
            text=random.choice(["hello!", "great stream", "lol"]),
        )
