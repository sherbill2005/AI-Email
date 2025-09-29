from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from google.auth.transport.requests import Request
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

BASE_DIR = Path(__file__).resolve().parents[3]
class GoogleAuthHandler:
    def __init__(self, creds_path: str = BASE_DIR / "credentials.json", token_path: str = BASE_DIR / "token.json"):
        self.creds_path = creds_path
        self.token_path = token_path
        self.creds = None

    def get_credentials(self) -> Credentials:
        if os.path.exists(self.token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"Error reading or parsing token file: {e}")
                self.creds = None

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        return self.creds
