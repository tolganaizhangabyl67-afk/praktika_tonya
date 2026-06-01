import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

async def create_event(summary: str, start_time: str, end_time: str) -> str:
    try:
        service = get_calendar_service()
        event = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "Asia/Almaty"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Almaty"}
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        return "✅ Оқиға жасалды: " + event.get("htmlLink", "")
    except Exception as e:
        logger.error("Calendar қатесі: " + str(e))
        return "❌ Қате: " + str(e)

async def list_events() -> str:
    try:
        from datetime import datetime, timezone
        service = get_calendar_service()
        now = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events:
            return "Жақындағы оқиғалар жоқ."
        result = "📅 Жақындағы оқиғалар:\n\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            result += "• " + event["summary"] + " — " + start + "\n"
        return result
    except Exception as e:
        return "❌ Қате: " + str(e)