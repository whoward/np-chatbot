import aiofiles
import argparse
import asyncio
import signal
import sys

from np_chatbot.logging import get_logger
from np_chatbot.recording_iterator import RecordingIterator
from np_chatbot.jsonl_iterator import JSONLIterator
from np_chatbot.google.chat.iterator import Iterator as ChatIterator
from np_chatbot.google.chat.event_iterator import EventIterator

log = get_logger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="NP Chatbot")

    # Optional flag for recording
    parser.add_argument(
        "--record", 
        metavar="PATH", 
        help="Path to a file where the chat stream will be recorded"
    )

    # Mutually exclusive group for Replay vs Video
    # setting required=True ensures at least one is provided
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument(
        "--replay", 
        metavar="PATH", 
        help="Replays a previous recording from the specified path"
    )
    
    group.add_argument(
        "--video", 
        metavar="VIDEO_ID", 
        help="Specifies a video ID to run"
    )

    return parser.parse_args()

def build_chat_iterator(video_id):
    iterator = ChatIterator(video_id)
    
    # handle the interrupt signal (Ctrl+C) by interrupting the iterator
    # to cause it to eventually stop consuming the chat stream
    def handle_signal(sig, frame):
        log.info("SIGINT received! Stopping chat consumer...")
        iterator.interrupt()

    signal.signal(signal.SIGINT, handle_signal)

    return iterator

async def main(args):
    # define the source iterator, which is either a replay file or a video stream
    if args.replay:
        io = await aiofiles.open(args.replay, "r")
        iterator = aiter(JSONLIterator(io))
    else:
        iterator = aiter(build_chat_iterator(args.video))

    if args.record:
        iterator = aiter(RecordingIterator(iterator, args.record))

    iterator = aiter(EventIterator(iterator))

    # print(iterator)

    # iterate through the iterator (don't do anything with the message)
    async for message in iterator:
        print(message.model_dump_json())

if __name__ == "__main__":
    args = parse_arguments()

    asyncio.run(main(args))
