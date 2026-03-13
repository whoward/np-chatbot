import grpc
import time

from google.protobuf.json_format import MessageToDict

from ...logging import get_logger

from .chat_stream_client import ChatStreamClient, EndOfStream

END_OF_STREAM = object()

log = get_logger(__name__)

class Stream:
    def __init__(self, queue, interrupt_event, next_page_token, video_id, backoff_sleep_seconds):
        self.queue = queue
        self.interrupt_event = interrupt_event
        self.next_page_token = next_page_token
        self.backoff_sleep_seconds = backoff_sleep_seconds
        
        self.client = ChatStreamClient(video_id)
    
    def run(self):
        try:
            self._do_run()
        except Exception as e:
            log.error("Fatal error in youtube consumer thread", exc_info=e)
        finally:
            self.client.close()
            self.queue.put(END_OF_STREAM)

    def _do_run(self):
        while self._should_continue_streaming:
            try:
                self._receive_from_stream()
            except EndOfStream as e:
                log.info("end of stream detected", reason=str(e))
                break
            
            log.debug("sleeping to allow messages to accumulate", duration=self.backoff_sleep_seconds)
            self.interrupt_event.wait(self.backoff_sleep_seconds)
    
    def _receive_from_stream(self):
        log.debug("starting stream request", next_page_token=self.next_page_token)
        start_time = time.perf_counter()

        for response in self.client.stream_with_retry(self.next_page_token):
            log.debug("received items from stream", item_count=len(response.items))
            
            for item in response.items:
                serialized = MessageToDict(item, preserving_proto_field_name=False)

                # add the videoId and liveChatId key to each serialized object
                serialized["videoId"] = self.client.video_id
                serialized["liveChatId"] = self.client.live_chat_id

                self.queue.put(serialized)

            self.next_page_token = response.next_page_token
        
        duration = time.perf_counter() - start_time
        log.debug("end of stream request", duration_seconds=round(duration, 2), next_page_token=self.next_page_token)

    @property
    def _should_continue_streaming(self):
        return not self.interrupt_event.is_set()
