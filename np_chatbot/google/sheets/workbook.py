from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...settings import get_settings
from ...logging import get_logger

from ..credentials_manager import CredentialsManager

log = get_logger(__name__)

ZONE = get_settings().timezone

QUESTIONS_COLUMNS = [ "Name", "Current Member?", "Date", f"Time ({ZONE})", "Question" ]

class Workbook:
    def __init__(self, workbook_name, workbook_id):
        self.title = workbook_name
        self.spreadsheet_id = workbook_id

    def add_question(self, chat_question):
        self._ensure_spreadsheet()

        log.info("pushing question into workbook", question_id=chat_question.message_id)

        ts = chat_question.timestamp.astimezone(ZONE)

        values_to_append = [
            [
                chat_question.author_name, 
                "Yes" if chat_question.is_chat_sponsor else "No",
                ts.strftime("%Y-%m-%d"),
                ts.strftime("%I:%M%p"),
                chat_question.text
            ]
        ]
        
        self._service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range="Questions!A1",
            valueInputOption="USER_ENTERED",
            body={'values': values_to_append}
        ).execute()

    def verify_access(self):
        self._ensure_spreadsheet()

        try:
            # Get current title first
            sheet_metadata = self._service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            current_title = sheet_metadata['properties']['title']

            # Attempt to "update" the title to itself
            body = {
                'requests': [{
                    'updateSpreadsheetProperties': {
                        'properties': {'title': current_title},
                        'fields': 'title'
                    }
                }]
            }
            self._service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()
        except HttpError as e:
            if e.resp.status in [403, 404]:
                raise RuntimeError(f"spreadsheet with id '{self.spreadsheet_id}' does not exist or is not editable")
            raise e

    def _ensure_spreadsheet(self):
        if self.spreadsheet_id is not None:
            return

        body = {
            'properties': {
                'title': self.title
            },
            'sheets': [
                {
                    'properties': {
                        'title': 'Questions'
                    }
                }
            ]
        }

        response = self._service.spreadsheets().create(
            body=body,
            fields='spreadsheetId,spreadsheetUrl',
        ).execute()

        self.spreadsheet_id = response.get('spreadsheetId')

        spreadsheet_url = response.get('spreadsheetUrl')

        log.info("created new google sheet", url=spreadsheet_url, id=self.spreadsheet_id)

        self._service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range="Questions!A1",
            valueInputOption="USER_ENTERED",
            body={ 'values': [QUESTIONS_COLUMNS] }
        ).execute()

    @property
    def _service(self):
        return build('sheets', 'v4', credentials = CredentialsManager().credentials)
