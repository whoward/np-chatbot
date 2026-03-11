import os
import json
import threading

from functools import lru_cache

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as AuthRequest
from google_auth_oauthlib.flow import InstalledAppFlow

from ..logging import get_logger

log = get_logger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/drive.file',
]

@lru_cache(maxsize=None)
class CredentialsManager:
    def __init__(self, token_path="token.json"):
        self.token_path = token_path
        self._credentials = self._initialize_credentials()
        self._lock = threading.Lock()

        if self._credentials is None:
            raise ValueError("credentials could not be obtaine")

    @property
    def credentials(self):
        with self._lock:
            return self._credentials

    @property
    def token(self):
        with self._lock:
            return self._credentials.token

    def refresh(self):
        with self._lock:
            log.info("refreshing oauth2 token")
            self._do_refresh()

    def _do_refresh(self):
        try:
            self._credentials.refresh(AuthRequest())
            
            self._save_to_disk(self._credentials)

            return self._credentials.token
        except Exception as e:
            log.error("Failed to refresh token", exc_info=e)
            raise

    def _save_to_disk(self, creds):
        log.debug("saving credentials to disk")
        with open(self.token_path, "w") as f:
            f.write(creds.to_json())

    def _initialize_credentials(self):
        creds = None
        
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path)

        if not creds or not creds.valid:
            # Silently refresh the token if it's expired and we can refresh it, otherwise
            # open a browser window to get a token using an OAuth authorization_code grant
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(AuthRequest())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials (including refresh token) for next time
            self._save_to_disk(creds)

        return creds