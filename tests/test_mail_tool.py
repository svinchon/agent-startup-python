import unittest
from unittest.mock import MagicMock, patch

from src.google_mail_tool import list_unread_emails


class TestGoogleMailTool(unittest.TestCase):
    @patch("src.google_mail_tool.authenticate_google")
    @patch("src.google_mail_tool.build")
    def test_list_unread_emails(self, mock_build, mock_authenticate_google):
        # Mock the credentials
        mock_authenticate_google.return_value = MagicMock()

        # Mock the service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the messages
        mock_messages = {
            "messages": [
                {"id": "1"},
                {"id": "2"},
            ]
        }
        mock_service.users().messages().list().execute.return_value = mock_messages

        # Mock the message get
        def get_message(userId, id):
            mock_msg = MagicMock()
            if id == "1":
                mock_msg.execute.return_value = {
                    "payload": {
                        "headers": [
                            {"name": "Subject", "value": "Subject 1"},
                            {"name": "From", "value": "Sender 1"},
                        ]
                    },
                    "labelIds": ["UNREAD", "INBOX"],
                }
            elif id == "2":
                mock_msg.execute.return_value = {
                    "payload": {
                        "headers": [
                            {"name": "Subject", "value": "Subject 2"},
                            {"name": "From", "value": "Sender 2"},
                        ]
                    },
                    "labelIds": ["UNREAD", "INBOX"],
                }
            else:
                mock_msg.execute.return_value = None
            return mock_msg

        mock_service.users().messages().get.side_effect = get_message

        # Call the function
        result = list_unread_emails(2)

        # Assert the result
        expected_result = "From: Sender 1\nSubject: Subject 1\nLabels: ['UNREAD', 'INBOX']\n---\nFrom: Sender 2\nSubject: Subject 2\nLabels: ['UNREAD', 'INBOX']"
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
