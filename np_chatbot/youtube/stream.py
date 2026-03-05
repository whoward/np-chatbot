import grpc
import time

from ..logging import get_logger
from .proto import stream_list_pb2, stream_list_pb2_grpc

END_OF_STREAM = object()

log = get_logger(__name__)

class Stream:
    def __init__(self, queue, interrupt_event, next_page_token, live_chat_id, backoff_sleep_seconds, credentials):
        self.queue = queue
        self.interrupt_event = interrupt_event
        self.next_page_token = next_page_token
        self.live_chat_id = live_chat_id
        self.backoff_sleep_seconds = backoff_sleep_seconds
        self.credentials = credentials
    
    def run(self):
        try:
            self._do_run()
        except BaseException as e:
            log.error("error in youtube consumer thread", exc_info=e)
        finally:
            self.queue.put(END_OF_STREAM)

    def _do_run(self):
        with self._channel() as channel:
            while self._should_continue_streaming:
                # use the streaming API to receive messages for a while. Google does not keep
                # the connection open forever and will eventually close it when chat becomes
                # idle or a max duration has been reached, so we need to loop back and run it
                # again later
                self._receive_from_stream(channel)

                # in order to keep API quota low we should wait a bit before starting the stream again
                log.debug("sleeping to allow messages to accumulate", duration=self.backoff_sleep_seconds)
                self.interrupt_event.wait(self.backoff_sleep_seconds)
    
    def _receive_from_stream(self, channel):
        log.debug("starting stream request", next_page_token=self.next_page_token)

        start_time = time.perf_counter()

        for response in self._stream(channel):
            log.debug("received items from stream", item_count=len(response.items))

            # TODO: if the item is an "end of stream item" we need to push an END_OF_STREAM
            # and set something in _should_continue_streaming() to stop streaming
            for item in response.items:
                self.queue.put(item)

            self.next_page_token = response.next_page_token
        
        end_time = time.perf_counter()

        duration = end_time - start_time
        
        log.debug("end of stream request", duration_seconds=round(duration, 2))

    @property
    def _should_continue_streaming(self):
        return not self.interrupt_event.is_set() or not self.next_page_token

    def _channel(self):
        creds = grpc.ssl_channel_credentials()

        return grpc.secure_channel("dns:///youtube.googleapis.com:443", creds)

    def _stream(self, channel):
        stub = stream_list_pb2_grpc.V3DataLiveChatMessageServiceStub(channel)

        metadata = (("authorization", "Bearer " + self.credentials.token),)

        request = stream_list_pb2.LiveChatMessageListRequest(
            part = [ "id", "snippet", "authorDetails" ],
            live_chat_id = self.live_chat_id,
            max_results = 500,
            page_token = self.next_page_token
        )

        return stub.StreamList(request, metadata = metadata)
