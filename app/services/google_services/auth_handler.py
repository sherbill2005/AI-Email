from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.services.auth_services import decrypt_token
from app.core.config import settings
import google.oauth2.credentials
import google.auth.transport.requests

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GoogleAuthHandler:
    def __init__(self):
        pass

    def get_credentials_from_refresh_token(self, encrypted_refresh_token: str) -> Credentials:
        refresh_token = decrypt_token(encrypted_refresh_token)

        creds = google.oauth2.credentials.Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )

        # If the credentials are not valid (e.g., expired access token), refresh them.
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())

        return creds