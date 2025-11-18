import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def decode_message(payload):
    """Decode Gmail API Base64URL encoded message body."""
    if "data" in payload["body"] and payload["body"]["data"]:
        data = payload["body"]["data"]
        decoded_bytes = base64.urlsafe_b64decode(data)
        try:
            return decoded_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return decoded_bytes.decode("latin-1", errors="replace")

    # If multipart email
    if "parts" in payload:
        for part in payload["parts"]:
            text = decode_message(part)
            if text:
                return text

    return ""


def main():
    creds = None
    sms = []

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        print("Messages:")
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"], format="full").execute()

            payload = msg["payload"]
            text = decode_message(payload)

            sms.append(text)

            print("\n====================")
            print(f"Message ID: {message['id']}")
            print(text)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
