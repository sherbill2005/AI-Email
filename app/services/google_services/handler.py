# app/services/google_services/gmail_client.py
import json

from googleapiclient.discovery import build
from app.services.google_services.auth_handler import GoogleAuthHandler


class GmailClient:
    def __init__(self, auth_handler: GoogleAuthHandler):
        self.auth = auth_handler
        self.creds = self.auth.get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def fetch_latest_email_subject(self, max_results: int = 10) -> list[str]:
        result = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = result.get('messages', [])

        email_subjects = []
        for msg in messages:
            msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='metadata',
                                                           metadataHeaders=['Subject']).execute()
            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            email_subjects.append(subject)

        return email_subjects


    def get_today_emails(self, max_results: int =10):
        results = self.service.users().messages().list(
            userId='me',
            q='newer_than:1d',
            maxResults=max_results,
        ).execute()
        messages = results.get('messages', [])

        email_content = []
        if not messages:
            return []
        for message in messages:
            msg_data = self.service.users().messages().get(userId='me', id=message['id']).execute()
            snippet = msg_data.get('snippet', '')
            email_content.append(snippet)
        return email_content

    def get_latest_message_id_from_history(self, start_history_id: str) -> str | None:
        """
        Fetches the latest message ID from history events since start_history_id.
        """
        history_events = self._get_history_events(start_history_id)
        
        for event in history_events:
            if 'messagesAdded' in event:
                # Assuming the first message in the list is the newest
                return event['messagesAdded'][0]['message']['id']
        return None

    def _get_history_events(self, start_history_id: str) -> list[dict]:
        """
        Fetches history events from the Gmail API, handling pagination.
        Filters for 'messageAdded' events.
        """
        history_events = []
        page_token = None
        
        while True:
            request_body = {
                'userId': 'me',
                'historyTypes': ['messageAdded'], # Only interested in added messages
                'labelId': 'INBOX', # Only interested in inbox changes
                'pageToken': page_token
            }
            if start_history_id is not None: # More explicit check
                request_body['startHistoryId'] = start_history_id

            response = self.service.users().history().list(**request_body).execute()
            
            if 'history' in response:
                history_events.extend(response['history'])
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        return history_events

    def get_email_by_id(self, message_id: str):
        msg_data = self.service.users().messages().get(userId='me', id=message_id).execute()
        return msg_data

    def watch(self, topic_name:str):
        request = {
            'labelIds': ['INBOX'],
             'topicName': topic_name,
        }
        print(f"Sending watch request to google for topic: {topic_name}")
        return self.service.users().watch(userId='me', body=request).execute()