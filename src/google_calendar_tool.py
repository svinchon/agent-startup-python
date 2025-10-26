
import datetime
import datetime as dt
import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_auth import authenticate_google

TIMEZONE = "Europe/Paris"

def add_event(
    summary: str,
    description: str,
    start_time: dt.datetime,
    end_time: dt.datetime #,
    # timezone: str = 'Europe/Paris'
    # calendar_id: str = "primary",
):
    """
    Creates a Google Calendar event.
    Assumes start_time and end_time are in local TIMEZONE if tz-naive.
    Assumes calendar_id is "primary".
    Assumes timezone is TIMEZONE.
    
    Args:
        summary: The summary or title of the event.
        description: The description of the event.
        start_time: The start time of the event in 'YYYY-MM-DDTHH:MM:SS' format.
        end_time: The end time of the event in 'YYYY-MM-DDTHH:MM:SS' format.
        timezone: The timezone for the event (default is 'Europe/Paris').
    """
    print(f"""
    Creating event with:
    summary={summary},
    description={description},
    start_time={start_time},
    end_time={end_time}
    """
    )
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."
    try:
        service = build("calendar", "v3", credentials=creds)
        def to_rfc3339(d: dt.datetime) -> str:
            if d.tzinfo is None:
                # on suppose que ce sont des heures locales TIMEZONE
                # sinon, passe des datetimes tz-aware
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

def get_upcoming_events(count: int):
    """Affiche les prochains événements du calendrier de
    l'utilisateur."""
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."
    try:
        service = build("calendar", "v3", credentials=creds)
        # Appelle l'API Calendar
        now = datetime.datetime.utcnow().isoformat() + "Z" # 'Z' indique UTC
        print("Récupération des prochains événements")
        events_result = (
            service.events()
               .list(
                   calendarId="primary",
                   timeMin=now,
                   maxResults=10,
                   singleEvents=True,
                   orderBy="startTime",
               )
               .execute()
           )
        events = events_result.get("items", [])
        if not events:
            print("Aucun événement à venir trouvé.")
            return
        # Affiche les prochains événements
        ret = "Evenements à venir:\n"
        for event in events[0:count]:
            start = event["start"].get("dateTime", event["start"].get("date"))
            ret += f"{start} - {event['summary']}\n"
        return ret
    except HttpError as error:
        return(f"Une erreur s'est produite : {error}")

if __name__ == "__main__":
    # Exemple d'utilisation
    from zoneinfo import ZoneInfo

    start_dt 	= dt.datetime.now(ZoneInfo(TIMEZONE)).replace(hour=15, minute=0, second=0, microsecond=0)
    end_dt  	= start_dt.replace(hour=16)

    event = add_event(
        summary="Réunion projet Bidon",
        description="Point d’avancement sprint",
        start_time=start_dt,
        end_time=end_dt
    )
    print("Événement créé :", event)

    print(get_upcoming_events(2))
