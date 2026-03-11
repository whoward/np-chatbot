from ...logging import get_logger
from ...events import ChatQuestion
from .workbook import Workbook

log = get_logger(__name__)

class WorkbookIterator:
    def __init__(self, inner_iterator, workbook_id, workbook_name):
        self.inner_iterator = inner_iterator

        self.workbook = Workbook(workbook_id=workbook_id, workbook_name=workbook_name)

    def _handle(self, event):
        if type(event) == ChatQuestion:
            self.workbook.add_question(event)
    
    def _handle_with_exception_handling(self, event):
        try:
            self._handle(event)
        except Exception as e:
            log.error("Failed to push handle event", exc_info=e)

    # --- Synchronous Protocol ---
    def __iter__(self):
        self.workbook.verify_access()
        return self

    def __next__(self):
        event = next(self.inner_iterator)
        self._handle_with_exception_handling(event)
        return event

    # --- Asynchronous Protocol ---
    def __aiter__(self):
        self.workbook.verify_access()
        return self

    async def __anext__(self):
        # anext() is the async equivalent of next()
        event = await anext(self.inner_iterator)
        self._handle_with_exception_handling(event)
        return event
