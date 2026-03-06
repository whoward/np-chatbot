from googleapiclient.discovery import build

from jsonpath import pointer

from .iterator import Iterator
from .credentials_manager import CredentialsManager

class Client:
    def __init__(self):
        pass

    # TODO: can we make this async?
    def fetch_live_chat_id(self, video_id):
        client = build("youtube", "v3", credentials = CredentialsManager().credentials)

        resp = client.videos().list(part="liveStreamingDetails", id=video_id).execute()

        return pointer.resolve("/items/0/liveStreamingDetails/activeLiveChatId", resp, default=None)

    def chat_iterator(self, live_chat_id):
        return Iterator(live_chat_id=live_chat_id)