import grpc
import time
import random

from dataclasses import dataclass
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as AuthRequest
from jsonpath import pointer

from ...logging import get_logger

from ..credentials_manager import CredentialsManager

from .proto import stream_list_pb2, stream_list_pb2_grpc

log = get_logger(__name__)

@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int
    base_delay: float
    should_refresh_auth: bool = False

class EndOfStream(Exception):
    """This exception is meant to signal when the client has determined the stream is no longer available"""

GRPC_RETRY_CONFIG = {
    grpc.StatusCode.UNAUTHENTICATED: RetryPolicy(
        max_retries=2, 
        base_delay=1.0, 
        should_refresh_auth=True
    ),
    grpc.StatusCode.UNAVAILABLE: RetryPolicy(
        max_retries=5, 
        base_delay=1.0
    ),
    grpc.StatusCode.RESOURCE_EXHAUSTED: RetryPolicy(
        max_retries=3, 
        base_delay=5.0
    ),
    grpc.StatusCode.DEADLINE_EXCEEDED: RetryPolicy(
        max_retries=3, 
        base_delay=1.0
    ),
}

DEFAULT_POLICY = RetryPolicy(max_retries=0, base_delay=0)

class ChatStreamClient:
    def __init__(self, video_id):
        self.video_id = video_id
        self.live_chat_id = None
        self.channel = grpc.secure_channel("dns:///youtube.googleapis.com:443", grpc.ssl_channel_credentials())
        self.stub = stream_list_pb2_grpc.V3DataLiveChatMessageServiceStub(self.channel)

    def stream_with_retry(self, page_token):
        self._ensure_live_chat_id()

        retries = 0
        
        while True:
            try:
                token = CredentialsManager().token

                metadata = (("authorization", f"Bearer {token}"),)
                
                request = stream_list_pb2.LiveChatMessageListRequest(
                    part=["id", "snippet", "authorDetails"],
                    live_chat_id=self.live_chat_id,
                    max_results=500,
                    page_token=page_token
                )
                
                yield from self.stub.StreamList(request, metadata=metadata)
                return 

            except grpc.RpcError as e:
                code = e.code()

                # the FAILED_PRECONDITION code gets special treatment, it usually means
                # the stream has ended so we immediately refetch the live chat id
                if code == grpc.StatusCode.FAILED_PRECONDITION:
                    self._ensure_live_chat_id()

                    # if we've reached this point we have successfully refetched the
                    # live_chat_id.  retry up to 2 times before failing.
                    if retries >= 2:
                        retries += 1
                        continue

                # Get policy or a default 'no-retry' policy
                policy = GRPC_RETRY_CONFIG.get(code, DEFAULT_POLICY)

                if retries >= policy.max_retries:
                    log.error("gRPC retry limit exceeded", code=code, details=e.details())
                    raise

                if policy.should_refresh_auth:
                    CredentialsManager().refresh()
                
                retries += 1

                # Exponential backoff using policy attributes
                sleep_time = (policy.base_delay * (2 ** retries)) + (random.uniform(0, 1))
                
                log.warning(
                    "gRPC error encountered", 
                    code=code, 
                    attempt=retries, 
                    max=policy.max_retries, 
                    next_delay=round(sleep_time, 2)
                )
                
                time.sleep(sleep_time)

    def close(self):
        self.channel.close()

    def _ensure_live_chat_id(self):
        # if the live chat id does not exist then fetch it
        if self.live_chat_id is None:
            self._load_live_chat_id()

        # if the chat still doesn't exist then we can assume the stream has ended
        if self.live_chat_id is None:
            raise EndOfStream("unable to retrieve live_chat_id")

    def _load_live_chat_id(self):
        log.debug("loading live_chat_id for video", video_id = self.video_id)

        client = build("youtube", "v3", credentials = CredentialsManager().credentials)

        resp = client.videos().list(part="liveStreamingDetails", id=self.video_id).execute()

        self.live_chat_id = pointer.resolve("/items/0/liveStreamingDetails/activeLiveChatId", resp, default=None)

        log.info("loaded live_chat_id for video", video_id = self.video_id, live_chat_id = self.live_chat_id)
