
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_auth import authenticate_google

def send_email(to: str, subject: str, message_text: str):
    """
    Sends an email using Gmail.

    Args:
        to: The recipient's email address.
        subject: The subject of the email.
        message_text: The body of the email.
    """
    creds = authenticate_google()
    if not creds:
        return "Authentication failed. Please ensure credentials.json is set up correctly."

    try:
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(message_text)
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": raw_message}
        # pylint: disable=E1101
        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        return send_message

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
