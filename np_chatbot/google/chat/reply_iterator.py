from googleapiclient.discovery import build

from ...logging import get_logger
from ...events import ChatQuestion

from ..credentials_manager import CredentialsManager

log = get_logger(__name__)

class ReplyIterator:
    def __init__(self, inner_iterator):
        self.inner_iterator = inner_iterator

    def _handle(self, event):
        if type(event) == ChatQuestion:
            self._post(chat_id=event.live_chat_id, text=f"Got you {event.author_name}")
    
    def _handle_with_exception_handling(self, event):
        try:
            self._handle(event)
        except Exception as e:
            log.error("Failed to handle event", exc_info=e)

    def _post(self, chat_id, text):
        try:
            request = self._client.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": text
                        }
                    }
                }
            )
            response = request.execute()
            log.info("message sent", id=response.get("id"), text=text)
        except Exception as e:
            log.error("failed to post message", exc_info=e)
    
    @property
    def _client(self):
        return build("youtube", "v3", credentials = CredentialsManager().credentials)

    # --- Synchronous Protocol ---
    def __iter__(self):
        return self

    def __next__(self):
        event = next(self.inner_iterator)
        self._handle_with_exception_handling(event)
        return event

    # --- Asynchronous Protocol ---
    def __aiter__(self):
        return self

    async def __anext__(self):
        # anext() is the async equivalent of next()
        event = await anext(self.inner_iterator)
        self._handle_with_exception_handling(event)
        return event
