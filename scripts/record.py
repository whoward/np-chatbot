import sys
import asyncio

from np_chatbot.logging import get_logger
from np_chatbot.youtube.client import Client

from google.protobuf import json_format

async def main(video_id):
    log = get_logger(__name__)
    
    youtube = Client()

    live_chat_id = youtube.fetch_live_chat_id(video_id)

    if live_chat_id is None:
        log.error("Unable to retrieve Live Chat ID for the specified video")

    log.info("live_chat_id", id=live_chat_id)

    with open(f"stream-{live_chat_id}.jsonl", "a", buffering=1) as f:
        async for message in youtube.chat_iterator(live_chat_id):
            serialized = json_format.MessageToJson(message, indent=0).replace('\n','').replace('\r','')
            print(serialized, file=f)


if __name__ == "__main__":
    video_id = sys.argv[1]

    asyncio.run(main(video_id))