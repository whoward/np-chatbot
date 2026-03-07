import sys
import asyncio
import signal

from np_chatbot.logging import get_logger
from np_chatbot.youtube.iterator import Iterator

from google.protobuf import json_format

async def main(video_id):
    log = get_logger(__name__)

    iterator = Iterator(video_id)
        
    # handle the interrupt signal (Ctrl+C) by interrupting the iterator
    # to cause it to eventually stop consuming the chat stream
    def handle_signal(sig, frame):
        print("\nSIGINT received! Stopping chat consumer...")
        iterator.interrupt()

    signal.signal(signal.SIGINT, handle_signal)

    with open(f"stream-{video_id}.jsonl", "a", buffering=1) as f:
        async for message in iterator:
            serialized = json_format.MessageToJson(message, indent=0).replace('\n','').replace('\r','')
            print(serialized, file=f)


if __name__ == "__main__":
    video_id = sys.argv[1]

    asyncio.run(main(video_id))