from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient

def start_gmail_watch():
    """
    Executes a one-time command to tell Gmail to start sending push
    notifications to our configured Pub/Sub topic.
    """
    print("-- Starting Gmail Watch Setup --")
    try:
        project_id = "gen-lang-client-0042356091"
        topic_id = "gmail-inbox-changes"
        topic_name = f"projects/{project_id}/topics/{topic_id}"

        print("1. Authenticating with Google...")
        auth_handler = GoogleAuthHandler()
        client = GmailClient(auth_handler=auth_handler)
        print("   Authentication successful.")

        print(f"2. Sending watch request to Google for topic: {topic_name}")
        response = client.watch(topic_name=topic_name)
        print("   Watch request successful!")

        print("3. Google API Response:")
        print(f"   History ID: {response['historyId']}")
        print(f"   Expiration: {response['expiration']}")
        print("------------------------------------")
        print("\nSetup complete. Your app is now listening for Gmail notifications.")
        print("Send a new email to trigger the webhook.")

    except Exception as e:
        print(f"\nAn error occurred during setup: {e}")
        print("Please check your credentials and Google Cloud configuration.")

def stop_gmail_watch():
    """
    Stops all active watch notifications for the user's inbox.
    """
    print("-- Stopping Gmail Watch Notifications --")
    try:
        auth_handler = GoogleAuthHandler()
        client = GmailClient(auth_handler=auth_handler)
        
        client.service.users().stop(userId='me').execute()
        print("Successfully stopped all active watch notifications.")
    except Exception as e:
        print(f"An error occurred while stopping watch: {e}")

if __name__ == "__main__":
    start_gmail_watch()
