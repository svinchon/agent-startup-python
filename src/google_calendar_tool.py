import datetime
import datetime as dt
import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

TIMEZONE = "Europe/Paris"

def add_event(
    creds: Credentials,
    summary: str,
    description: str,
    start_time: dt.datetime,
    end_time: dt.datetime
):
    """
    Creates a Google Calendar event.
    Assumes start_time and end_time are in local TIMEZONE if tz-naive.
    Assumes calendar_id is "primary".
    Assumes timezone is TIMEZONE.
    
    Args:
        creds: The authenticated Google credentials.
        summary: The summary or title of the event.
        description: The description of the event.
        start_time: The start time of the event in 'YYYY-MM-DDTHH:MM:SS' format.
        end_time: The end time of the event in 'YYYY-MM-DDTHH:MM:SS' format.
    """
    try:
        service = build("calendar", "v3", credentials=creds)
        def to_rfc3339(d: dt.datetime) -> str:
            if d.tzinfo is None:
                from zoneinfo import ZoneInfo
                d = d.replace(tzinfo=ZoneInfo(TIMEZONE))
            return d.isoformat()

        event_body = {
            "summary": summary,
            "description": description,
            "start": {
                'dateTime': to_rfc3339(start_time),
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': to_rfc3339(end_time),
                'timeZone': TIMEZONE,
            },
        }

        created = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()
        return created

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def get_upcoming_events(creds: Credentials, count: int):
    """Gets the upcoming events from the user's calendar."""
    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=count,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            return "No upcoming events found."
        
        ret = "Upcoming events:\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            ret += f"{start} - {event['summary']}\n"
        return ret
    except HttpError as error:
        return f"An error occurred: {error}"

if __name__ == "__main__":
    # This part will not work without credentials.
    # You would need to load credentials from a file or another source to test this directly.
    print("To test this module directly, you need to provide Google API credentials.")