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
from np_chatbot.google.chat.reply_iterator import ReplyIterator
from np_chatbot.google.sheets.workbook_iterator import WorkbookIterator

log = get_logger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="NP Chatbot")

    # Optional flag for recording
    parser.add_argument(
        "--record", 
        metavar="PATH", 
        help="Path to a file where the chat stream will be recorded"
    )

    # Optional flag for specifying next_page_token
    parser.add_argument(
        "--next-page-token",
        metavar="TOKEN",
        help="Cursor value for the chat iterator to pick up where it left off"
    )

    parser.add_argument(
        "--silent",
        help="When set the bot will never post replies to user activity in chat",
        action="store_true",
        default=False
    )

    # Mutually exclusive group for Replay vs Video
    # setting required=True ensures at least one is provided
    source_group = parser.add_mutually_exclusive_group(required=True)
    
    source_group.add_argument(
        "--replay", 
        metavar="PATH", 
        help="Replays a previous recording from the specified path"
    )
    
    source_group.add_argument(
        "--video", 
        metavar="VIDEO_ID", 
        help="Specifies a video ID to run"
    )

    # Mutually exclusive group for spreadsheet-id and spreadsheet-name
    # setting required=False means neither needs to be set
    spreadsheet_group = parser.add_mutually_exclusive_group(required=False)

    spreadsheet_group.add_argument(
        "--spreadsheet-id",
        metavar="SPREADSHEET_ID",
        help="ID of the spreadsheet to push data to"
    )

    spreadsheet_group.add_argument(
        "--spreadsheet-name",
        metavar="NAME",
        help="Name of the spreadsheet to create"
    )

    return parser.parse_args()

def build_chat_iterator(args):
    iterator = ChatIterator(
        video_id=args.video,
        next_page_token=args.next_page_token,
    )
    
    # handle the interrupt signal (Ctrl+C) by interrupting the iterator
    # to cause it to eventually stop consuming the chat stream
    def handle_signal(sig, frame):
        log.info("SIGINT received! Stopping chat consumer...")
        iterator.interrupt()
        # TODO: find a way to wait up to 30 seconds before running sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)

    return iterator

async def main(args):
    # define the source iterator, which is either a replay file or a video stream
    if args.replay:
        io = await aiofiles.open(args.replay, "r")
        iterator = aiter(JSONLIterator(io))
    else:
        iterator = aiter(build_chat_iterator(args))

    # if the user has specified they want to record the stream add a recording iterator
    if args.record:
        iterator = aiter(RecordingIterator(iterator, args.record))

    # add a event parsing iterator to parse low level events into high level events
    iterator = aiter(EventIterator(iterator))

    # if either a spreadsheet_id or spreadsheet_name is specified then add a spreadsheet iterator to the chain
    if args.spreadsheet_id or args.spreadsheet_name:
        iterator = aiter(WorkbookIterator(
            inner_iterator=iterator, 
            workbook_id=args.spreadsheet_id, 
            workbook_name=args.spreadsheet_name
        ))

    if not args.silent and args.replay is None:
        iterator = aiter(ReplyIterator(iterator))

    # iterate through the iterator (don't do anything with the message)
    async for message in iterator:
        print(message.model_dump_json())
        pass

if __name__ == "__main__":
    args = parse_arguments()

    asyncio.run(main(args))
