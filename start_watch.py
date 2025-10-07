import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# The SCOPES define the permissions we are asking for.
# If you modify these, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate():
    """Performs the authentication flow for a desktop app."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found. Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def start_gmail_watch():
    """
    Executes a one-time command to tell Gmail to start sending push
    notifications to our configured Pub/Sub topic.
    """
    print("\n-- Starting Gmail Watch Setup --")
    try:
        creds = authenticate()
        service = build("gmail", "v1", credentials=creds)

        project_id = "emailreader-472512"
        topic_id = "gmail-inbox-changes"
        topic_name = f"projects/{project_id}/topics/{topic_id}"

        print(f"1. Sending watch request to Google for topic: {topic_name}")
        request = {"labelIds": ["INBOX"], "topicName": topic_name}
        response = service.users().watch(userId="me", body=request).execute()
        print("   Watch request successful!")

        print("2. Google API Response:")
        print(f"   History ID: {response['historyId']}")
        print(f"   Expiration (timestamp): {response['expiration']}")
        print("------------------------------------")
        print("\nSetup complete. Your app is now listening for Gmail notifications.")

    except Exception as e:
        print(f"\nAn error occurred during setup: {e}")
        print("Please check your credentials.json and Google Cloud configuration.")

def stop_gmail_watch():
    """
    Stops all active watch notifications for the user's inbox.
    """
    print("-- Stopping Gmail Watch Notifications --")
    try:
        creds = authenticate()
        service = build("gmail", "v1", credentials=creds)
        service.users().stop(userId='me').execute()
        print("Successfully stopped all active watch notifications.")
    except Exception as e:
        print(f"An error occurred while stopping watch: {e}")

if __name__ == "__main__":
    # The script will first stop any existing watch, then start a new one.
    stop_gmail_watch()
    start_gmail_watch()