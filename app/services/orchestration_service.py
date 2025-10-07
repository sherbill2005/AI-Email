from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient
from app.services.ai_model_services import LangchainSummarizer, ZeroShotClassifier
from app.services.rules_services import RuleService
from app.services.filtering_service import EmailFilteringService
from app.db_utils.mongo import db
from app.models.user_model import User
from app.models.rules_model import RuleModel

class EmailProcessingOrchestrator:
    def __init__(self):
        self.ai_summarizer = LangchainSummarizer()
        self.rule_service = RuleService()
        self.zero_shot_classifier = ZeroShotClassifier()
        self.email_filtering_service = EmailFilteringService(
            rule_service=self.rule_service,
            classifier=self.zero_shot_classifier
        )

    def summarize_by_index(self, email_index: int) -> str:
        # This method is now broken as it relies on a single-user gmail_client
        # It needs to be updated to be user-aware
        raise NotImplementedError("summarize_by_index is not implemented for multi-user yet")

    def process_incoming_email_notification(self, history_id: str, email_address: str):
        print("\n--- [Orchestrator] Starting Email Notification Processing ---")

        user_doc = db.users.find_one({"email": email_address})
        if not user_doc:
            print(f"[Orchestrator] User {email_address} not found. Skipping processing.")
            return
        
        user = User(
            email=user_doc['email'],
            name=user_doc.get('name'),
            last_processed_history_id=user_doc.get('last_processed_history_id'),
            encrypted_google_refresh_token=user_doc.get('encrypted_google_refresh_token'),
            _id=user_doc.get('_id')
        )

        if not user.encrypted_google_refresh_token:
            print(f"[Orchestrator] User {email_address} has no refresh token. Skipping processing.")
            return

        auth_handler = GoogleAuthHandler()
        credentials = auth_handler.get_credentials_from_refresh_token(user.encrypted_google_refresh_token)
        gmail_client = GmailClient(credentials)

        last_processed_history_id = user.last_processed_history_id

        if last_processed_history_id and int(history_id) <= int(last_processed_history_id):
            print(f"[Orchestrator] Received old or duplicate history ID {history_id}. Current is {last_processed_history_id}. Skipping.")
            return

        if last_processed_history_id is None:
            db.users.update_one({"email": email_address}, {"$set": {"last_processed_history_id": history_id}})
            print(f"[Orchestrator] First notification for {email_address}. Storing history ID {history_id}.")
            return

        new_message_ids = gmail_client.get_new_message_ids_from_history(last_processed_history_id)
        if not new_message_ids:
            print(f"[Orchestrator] No new messages found since history ID {last_processed_history_id}. Acknowledging notification.")
            db.users.update_one({"email": email_address}, {"$set": {"last_processed_history_id": history_id}})
            return

        all_rules = self.rule_service.get_all_rules(user_id=str(user._id))

        for message_id in new_message_ids:
            message_content = gmail_client.get_email_by_id(message_id)
            if not message_content:
                print(f"[Orchestrator] Could not fetch content for message ID: {message_id}. Skipping.")
                continue

            snippet = message_content.get('snippet', '')
            headers = message_content.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")

            if not all_rules:
                final_aggregated_score = 0.0
            else:
                email_full_content = f"Subject: {subject}\n\n{snippet}"
                final_aggregated_score = self.email_filtering_service.filter_emails_by_rules(email_full_content, all_rules)

            processed_email_data = {
                "user_id": str(user._id),
                "message_id": message_id,
                "sender": sender,
                "subject": subject,
                "snippet": snippet,
                "aggregated_score": final_aggregated_score
            }

            print(f"[Orchestrator] Processing Email | Subject: '{subject}' | Score: {final_aggregated_score:.2f}%")

            storage_threshold = 50.0
            if final_aggregated_score >= storage_threshold:
                print(f"  - Action: Saving to database.")
                db.processed_emails.insert_one(processed_email_data)
            else:
                print(f"  - Action: Skipping (score below {storage_threshold}%).")

        db.users.update_one({"email": email_address}, {"$set": {"last_processed_history_id": history_id}})
        print("--- [Orchestrator] Finished Processing Notification ---")
