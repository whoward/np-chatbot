import json

from .logging import get_logger

log = get_logger(__name__)

class RecordingIterator:
    def __init__(self, inner_iterator, filename):
        self.inner_iterator = inner_iterator
        self.filename = filename
        self._file = None

    def _open_file(self):
        if self._file is None:
            log.debug("opening recording file", filename=self.filename)
            self._file = open(self.filename, 'a', encoding='utf-8')

    def _close_file(self):
        if self._file:
            log.debug("closing recording file", filename=self.filename)
            self._file.close()
            self._file = None

    def _record(self, item):
        if not isinstance(item, dict):
            log.error(f"Expected dict, got {type(item).__name__}")
            return
        
        self._open_file()
        self._file.write(json.dumps(item) + '\n')
        self._file.flush() 

    # --- Synchronous Protocol ---
    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = next(self.inner_iterator)
            self._record(item)
            return item
        except StopIteration:
            self._close_file()
            raise

    # --- Asynchronous Protocol ---
    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            # anext() is the async equivalent of next()
            item = await anext(self.inner_iterator)
            self._record(item)
            return item
        except StopAsyncIteration:
            self._close_file()
            raise

    # --- Safety Net ---
    def __del__(self):
        """Ensures the file handle is closed when the object is garbage collected."""
        self._close_file()