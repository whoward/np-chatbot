import asyncio
import threading
import signal

from .stream import stream, END_OF_STREAM

from ..logging import get_logger

class AsyncQueueBridge:
    """A thread-safe bridge that looks like queue.Queue to threads."""
    def __init__(self):
        self._loop = asyncio.get_running_loop()
        self._async_queue = asyncio.Queue()

    def put(self, item):
        """Thread-safe put: matches queue.Queue interface."""
        self._loop.call_soon_threadsafe(self._async_queue.put_nowait, item)

    async def get(self):
        """Async get: used by the iterator."""
        return await self._async_queue.get()

class Iterator:
    def __init__(self, live_chat_id, credentials, next_page_token=None, backoff_sleep_seconds=15.0):
        self.queue = AsyncQueueBridge()
        self.interrupt_event = threading.Event()
        self.started = False

        self.live_chat_id = live_chat_id
        self.credentials = credentials
        self.next_page_token = next_page_token
        self.backoff_sleep_seconds = backoff_sleep_seconds

        self.log = get_logger(f"YouTube Iterator for {live_chat_id}")

    def __aiter__(self):
        if not self.started:
            self.log.debug("starting youtube streaming thread")

            # Register SIGINT handler in the main thread
            # TODO: move to main script
            signal.signal(signal.SIGINT, self.interrupt)

            kwargs = {
                "queue": self.queue,
                "interrupt_event": self.interrupt_event,
                "next_page_token": self.next_page_token,
                "credentials": self.credentials,
                "live_chat_id": self.live_chat_id,
                "backoff_sleep_seconds": self.backoff_sleep_seconds
            }
            
            thread = threading.Thread(target=stream, kwargs=kwargs, daemon=True)
            thread.start()

            self.started = True
            
        return self

    async def __anext__(self):
        item = await self.queue.get()
        if item is END_OF_STREAM:
            raise StopAsyncIteration
        return item

    def interrupt(self, sig, frame):
        # TODO: move this print statement to the main script
        print("\nSIGINT received! Stopping thread...")
        self.interrupt_event.set()
