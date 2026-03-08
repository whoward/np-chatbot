import json

from np_chatbot.logging import get_logger

log = get_logger(__name__)

class JSONLIterator:
    """An iterator supporting both sync and async iteration of JSONL records."""
    
    def __init__(self, io_obj):
        self.io_obj = io_obj

    # --- Synchronous Protocol ---
    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = self.io_obj.readline()
            
            if not line:
                raise StopIteration
            
            # Handle potential bytes from some stream readers
            if isinstance(line, bytes):
                line = line.decode('utf-8')
                
            line = line.strip()
            if line:
                return json.loads(line)

    # --- Asynchronous Protocol ---
    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            # Await the async readline operation
            line = await self.io_obj.readline()
            
            if not line:
                raise StopAsyncIteration
            
            # Handle potential bytes from some stream readers
            if isinstance(line, bytes):
                line = line.decode('utf-8')
                
            line = line.strip()
            if line:
                return json.loads(line)