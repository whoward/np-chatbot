import grpc
import time

from ..logging import get_logger
from .proto import stream_list_pb2, stream_list_pb2_grpc

END_OF_STREAM = object()

log = get_logger(__name__)

def stream(queue, interrupt_event, next_page_token, live_chat_id, backoff_sleep_seconds, credentials):
    try:
        creds = grpc.ssl_channel_credentials()

        with grpc.secure_channel("dns:///youtube.googleapis.com:443", creds) as channel:
            stub = stream_list_pb2_grpc.V3DataLiveChatMessageServiceStub(channel)

            metadata = (("authorization", "Bearer " + credentials.token),)

            while not interrupt_event.is_set():
                log.debug("starting stream request", next_page_token=next_page_token)

                request = stream_list_pb2.LiveChatMessageListRequest(
                    part=["id", "snippet", "authorDetails"],
                    live_chat_id=live_chat_id,
                    max_results=500,
                    page_token=next_page_token,
                )

                for response in stub.StreamList(request, metadata=metadata):
                    log.debug("received items from stream", item_count=len(response.items))

                    # TODO: if the item is an "end of stream item" we need to push an END_OF_STREAM
                    for item in response.items:
                        queue.put(item)

                    next_page_token = response.next_page_token

                    if not next_page_token:
                        break
                
                # TODO: record timestamp before/after loop and determine and log how 
                # long Google kept the connection open

                log.debug(f"end of stream, will restart in {backoff_sleep_seconds} seconds")

                time.sleep(backoff_sleep_seconds)
    except BaseException as e:
        log.error("error in youtube consumer thread", exc_info=e)
    finally:
        queue.put(END_OF_STREAM)
