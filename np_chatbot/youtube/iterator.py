import asyncio
import threading
import signal

from .stream import Stream, END_OF_STREAM

from ..logging import get_logger

log = get_logger(__name__)

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
    def __init__(self, live_chat_id, next_page_token=None, backoff_sleep_seconds=15.0):
        self.started = False
        self.queue = AsyncQueueBridge()
        self.interrupt_event = threading.Event()
        self.stream = Stream(
            queue = self.queue,
            interrupt_event = self.interrupt_event, 
            next_page_token = next_page_token, 
            live_chat_id = live_chat_id, 
            backoff_sleep_seconds = backoff_sleep_seconds, 
        )

    def __aiter__(self):
        if not self.started:
            log.debug("starting youtube streaming thread")
            
            thread = threading.Thread(target=self.stream.run, daemon=True)
            thread.start()

            self.started = True
            
        return self

    async def __anext__(self):
        item = await self.queue.get()
        if item is END_OF_STREAM:
            raise StopAsyncIteration
        return item

    def interrupt(self):
        self.interrupt_event.set()
