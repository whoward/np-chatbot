from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build

from jsonpath import pointer

from .iterator import Iterator

import os.path

# Define the scopes you added in the Cloud Console
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

# TODO: can we make this async?
def load_credentials():
    creds = None
    # 1. Check if we already have a 'token.json' (saved session)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 2. If no valid credentials (first time or expired), log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Silently refresh the token if it's expired
            creds.refresh(Request())
        else:
            # This loads the file you downloaded from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # 3. Save the credentials (including refresh token) for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

class Client:
    def __init__(self, credentials = None):
        if credentials is None:
            self.credentials = load_credentials()
        else:
            self.credentials = credentials

        self._client = build("youtube", "v3", credentials=self.credentials)

    # TODO: can we make this async?
    def fetch_live_chat_id(self, video_id):
        resp = self._client.videos().list(part="liveStreamingDetails", id=video_id).execute()

        return pointer.resolve("/items/0/liveStreamingDetails/activeLiveChatId", resp, default=None)

    def chat_iterator(self, live_chat_id):
        return Iterator(live_chat_id=live_chat_id, credentials=self.credentials)