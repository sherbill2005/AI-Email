from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient

auth_handler = GoogleAuthHandler()
client = GmailClient(auth_handler)
emails = client.fetch_latest_email_subject(5)
print(emails)