from ...settings import get_settings
from ...events import *
from jsonpath import pointer

settings = get_settings()

COMMAND_PREFIX_REGEX = settings.command_prefix_regex
QUESTION_PREFIX_REGEX = settings.question_prefix_regex

def p(doc, path, default=None):
    return pointer.resolve(path, doc, default=default)

def parse_member_milestone(ev):
    if p(ev, "/snippet/type") != "MEMBER_MILESTONE_CHAT_EVENT":
        return

    return MemberMilestone(
        message_id = p(ev, "/id"),
        video_id = p(ev, "/videoId"),
        timestamp = p(ev, "/snippet/publishedAt"),
        author_id = p(ev, "/authorDetails/channelId"),
        author_name = p(ev, "/authorDetails/displayName"),
        comment = p(ev, "/snippet/memberMilestoneChatDetails/userComment"),
        level = p(ev, "/snippet/memberMilestoneChatDetails/memberLevelName"),
        months = p(ev, "/snippet/memberMilestoneChatDetails/memberMonth"),
    )

def parse_user_banned_event(ev):
    if p(ev, "/snippet/type") != "USER_BANNED_EVENT":
        return
    
    return UserBannedEvent(
        message_id = p(ev, "/id"),
        video_id = p(ev, "/videoId"),
        timestamp = p(ev, "/snippet/publishedAt"),
        moderator_id = p(ev, "/authorDetails/channelId"),
        moderator_name = p(ev, "/authorDetails/displayName"),
        ban_type = p(ev, "/snippet/userBannedDetails/banType"),
        ban_duration_seconds = p(ev, "/snippet/userBannedDetails/banDurationSeconds"),
        banned_user_id = p(ev, "/snippet/userBannedDetails/bannedUserDetails/channelId"),
        banned_user_name = p(ev, "/snippet/userBannedDetails/bannedUserDetails/displayName"),
    )

def parse_chat_command(ev):
    if p(ev, "/snippet/type") != "TEXT_MESSAGE_EVENT":
        return
    
    text = p(ev, "/snippet/textMessageDetails/messageText")

    match = COMMAND_PREFIX_REGEX.match(text)

    if match is None:
        return

    command = match.group("command")

    args = text[match.end():]

    return ChatCommandInvocation(
        message_id = p(ev, "/id"),
        video_id = p(ev, "/videoId"),
        timestamp = p(ev, "/snippet/publishedAt"),
        author_id = p(ev, "/authorDetails/channelId"),
        author_name = p(ev, "/authorDetails/displayName"),
        is_chat_sponsor = p(ev, "/authorDetails/isChatSponsor", False),
        command = command,
        args = args,
    )

def parse_chat_question(ev):
    if p(ev, "/snippet/type") != "TEXT_MESSAGE_EVENT":
        return
    
    text = p(ev, "/snippet/textMessageDetails/messageText")

    match = QUESTION_PREFIX_REGEX.match(text)

    if match is None:
        return

    question = text[match.end():]
    
    return ChatQuestion(
        message_id = p(ev, "/id"),
        video_id = p(ev, "/videoId"),
        timestamp = p(ev, "/snippet/publishedAt"),
        author_id = p(ev, "/authorDetails/channelId"),
        author_name = p(ev, "/authorDetails/displayName"),
        is_chat_sponsor = p(ev, "/authorDetails/isChatSponsor", False),
        text = question,
    )

ORDERED_STRATEGIES = [
    parse_user_banned_event,
    parse_member_milestone,
    parse_chat_question,
    parse_chat_command,
]

# iterates through the ordered parsing strategy fucntions attempting to
# parse the event to a high level event.  the first strategy which returns
# something has that value returned.
def parse(event):
    for strategy in ORDERED_STRATEGIES:
        # TODO: handle pydantic validation error
        result = strategy(event)

        if result is not None:
            return result

    return None
    

class EventIterator:
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return self

    def __aiter__(self):            
        return self

    def __next__(self):
        while True:
            next_value = next(self.iterator)

            parsed = parse(next_value)

            if parsed is not None:
                return parsed

    async def __anext__(self):
        while True:
            next_value = await next(self.iterator)

            parsed = parse(next_value)

            if parsed is not None:
                return parsed
