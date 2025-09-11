from app.services.google_services.auth_handler import GoogleAuthHandler
from app.services.google_services.handler import GmailClient
from app.services.ai_model_services import LangchainSummarizer, ZeroShotClassifier
from app.services.rules_services import RuleService
from app.services.filtering_service import EmailFilteringService
from app.db_utils.mongo import db
from app.models.user_model import User

class EmailProcessingOrchestrator:
    def __init__(self):
        # Services for Gmail interaction and summarization
        self.auth_handler = GoogleAuthHandler()
        self.gmail_client = GmailClient(self.auth_handler)
        self.ai_summarizer = LangchainSummarizer()

        # Services for email filtering
        self.rule_service = RuleService()
        self.zero_shot_classifier = ZeroShotClassifier()
        self.email_filtering_service = EmailFilteringService(
            rule_service=self.rule_service,
            classifier=self.zero_shot_classifier
        )

    def summarize_by_index(self, email_index: int) -> str:
        emails = self.gmail_client.fetch_latest_email_subject()

        selected_email = emails[email_index]
        summary = self.ai_summarizer.summarize_email(selected_email)
        print(summary)
        return summary

    def process_incoming_email_notification(self, history_id: str, email_address: str):
        """
        Processes an incoming Gmail push notification.
        Fetches the email, filters it, and saves it to the database if rules match.
        This process is designed to be idempotent.
        """
        print("\n--- [Orchestrator] Starting Email Notification Processing ---")
        print(f"[Orchestrator] Processing history ID: {history_id} for {email_address}")

        # 0. Fetch user and last processed history ID
        user_doc = db.users.find_one({"email": email_address})
        if not user_doc:
            print(f"[Orchestrator] User {email_address} not found. Skipping processing.")
            return
        
        user = User(
            email=user_doc['email'],
            name=user_doc.get('name'),
            last_processed_history_id=user_doc.get('last_processed_history_id'),
            _id=user_doc.get('_id')
        )
        last_processed_history_id = user.last_processed_history_id

        # Idempotency Check: Only process if the new history ID is greater than the last one.
        if last_processed_history_id and int(history_id) <= int(last_processed_history_id):
            print(f"[Orchestrator] Received old or duplicate history ID {history_id}. Current is {last_processed_history_id}. Skipping.")
            return

        # Handle first-time notification for a user
        if last_processed_history_id is None:
            db.users.update_one({"email": email_address}, {"$set": {"last_processed_history_id": history_id}})
            print(f"[Orchestrator] First notification for {email_address}. Storing history ID {history_id} to start processing from the next email.")
            return

        # 1. Get new messages since the last processed history ID
        new_message_id = self.gmail_client.get_latest_message_id_from_history(last_processed_history_id)
        if not new_message_id:
            print(f"[Orchestrator] No new messages found for history ID: {history_id}. This might be an out-of-order notification. Skipping.")
            # We DO NOT update the history ID here to prevent rewinding.
            return

        # 2. Fetch the full email content by its ID.
        message_content = self.gmail_client.get_email_by_id(new_message_id)
        if not message_content:
            print(f"[Orchestrator] Could not fetch content for message ID: {new_message_id}. Skipping.")
            return

        # 3. Parse the details from the raw email data.
        snippet = message_content.get('snippet', '')
        headers = message_content.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")

        # 4. Get rules and filter email
        all_rules = self.rule_service.get_all_rules()
        if not all_rules:
            print("[Orchestrator] No rules found in the database. Skipping filtering.")
            scores = []
        else:
            rule_ids_to_apply = [str(rule.id) for rule in all_rules]
            email_full_content = f"Subject: {subject}\n\n{snippet}"
            scores = self.email_filtering_service.filter_emails_by_rules(email_full_content, rule_ids_to_apply)

        # 5. Prepare data for database insertion and save if rules matched.
        processed_email_data = {
            "message_id": new_message_id,
            "sender": sender,
            "subject": subject,
            "snippet": snippet,
            "scores": scores
        }

        matched_any_rule = any(score['classification'] == 'Matched' for score in scores)

        if matched_any_rule:
            print("[Orchestrator] Saving processed email to MongoDB (at least one rule matched)...")
            db.processed_emails.insert_one(processed_email_data)
            print("[Orchestrator] Processed email saved to MongoDB.")
        else:
            print("[Orchestrator] No rules matched. Skipping saving to MongoDB.")

        # 6. Update user's last processed history ID to the current one
        db.users.update_one({"email": email_address}, {"$set": {"last_processed_history_id": history_id}})
        print(f"[Orchestrator] Updated last_processed_history_id for {email_address} to {history_id}")

        print("--- [Orchestrator] Email Processing Complete ---")
        print(f"  Sender: {sender}")
        print(f"  Subject: {subject}")
        print(f"  Snippet: {snippet[:100]}...")
        print(f"  Scores: {scores}")
        print("------------------------------------")