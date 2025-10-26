from __future__ import annotations
import datetime as dt
import uuid
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- Paramètres ---
SCOPES = ["https://www.googleapis.com/auth/calendar"]  # lecture/écriture
TIMEZONE = "Europe/Paris"  # adapte si besoin

def get_service() -> "Resource":
    """
    Renvoie un client Google Calendar authentifié via OAuth
    (token.json est créé/rafraîchi).
    Place 'credentials.json' (OAuth Desktop) à côté du script.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def add_event(
    service,
    summary: str,
    start: dt.datetime,
    end: dt.datetime,
    #location: str | None = None,
    description: str | None = None,
    # attendees_emails: list[str] | None = None,
    # add_meet: bool = False,
    calendar_id: str = "primary",
):
    """
    Crée un événement dans Google Agenda.

    start/end doivent être des datetimes *aware* (avec tzinfo) ou on fournit timezone séparément via TIMEZONE.
    """
    # S’assure qu’on envoie du RFC3339 (avec timezone)
    def to_rfc3339(d: dt.datetime) -> str:
        if d.tzinfo is None:
            # on suppose que ce sont des heures locales TIMEZONE ; sinon, passe des datetimes tz-aware
            from zoneinfo import ZoneInfo
            d = d.replace(tzinfo=ZoneInfo(TIMEZONE))
        return d.isoformat()

    event_body = {
        "summary": summary,
        # "location": location,
        "description": description,
        "start": {"dateTime": to_rfc3339(start), "timeZone": TIMEZONE},
        "end": {"dateTime": to_rfc3339(end), "timeZone": TIMEZONE},
        # Rappels personnalisés (ex: popup 10 min + email 24h)
        # "reminders": {
        #     "useDefault": False,
        #     "overrides": [
        #         {"method": "popup", "minutes": 10},
        #         {"method": "email", "minutes": 24 * 60},
        #     ],
        # },
    }

    # if attendees_emails:
    #     event_body["attendees"] = [{"email": e} for e in attendees_emails]

    # # Option : créer un lien Google Meet
    conference_data = None
    # if add_meet:
    #     conference_data = {
    #         "createRequest": {
    #             "requestId": f"req-{uuid.uuid4().hex}",
    #             "conferenceSolutionKey": {"type": "hangoutsMeet"},
    #         }
    #     }

    created = service.events().insert(
        calendarId=calendar_id,
        body=event_body,
        # conferenceData=None,
        # sendUpdates="all",            # notifie les invités (none / externalOnly / all)
        # supportsAttachments=True
    ).execute() #if add_meet else service.events().insert(
    #     calendarId=calendar_id,
    #     body=event_body,
    #     sendUpdates="all",
    #     supportsAttachments=True
    # ).execute()

    # Si Meet a été demandé mais non passé via le champ conferenceData de insert,
    # on peut aussi faire un patch après-coup (alternative) :
    # created = service.events().patch(..., conferenceData=conference_data, ...).execute()

    return created

if __name__ == "__main__":
    from zoneinfo import ZoneInfo
    service = get_service()

    # Exemple : événement aujourd’hui de 15:00 à 16:00 Europe/Paris
    start_dt 	= dt.datetime.now(ZoneInfo(TIMEZONE)).replace(hour=15, minute=0, second=0, microsecond=0)
    end_dt  	= start_dt.replace(hour=16)

    event = add_event(
        service=service,
        summary="Réunion projet Bidon",
        start=start_dt,
        end=end_dt,
        # location="Google Meet",
        description="Point d’avancement sprint",
        # attendees_emails=["alice@example.com", "bob@example.com"],
        # add_meet=True,  # génère un lien Meet
        calendar_id="primary",
    )

    html_link = event.get("htmlLink")
    meet_link = (event.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri")
                 if event.get("conferenceData") else None)

    print("Événement créé ✅")
    print("Agenda:", html_link)
    if meet_link:
        print("Meet:", meet_link)
