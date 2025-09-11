import base64
import json
from app.services.orchestration_service import EmailProcessingOrchestrator # New Import

class GmailWebhookHandler:
    """
    Handles the processing of a Gmail push notification payload.
    Delegates the core processing logic to the EmailProcessingOrchestrator.
    """
    def __init__(self, payload: dict):
        self.payload = payload
        self.message_json = None

    def process(self):
        try:
            print("\n--- [Webhook Handler] Receiving Notification ---")
            self._decode_and_validate_message()
            print(f"[Webhook Handler] Decoded message: {self.message_json}")

            history_id = self.message_json.get("historyId")
            email_address = self.message_json.get("emailAddress")
            print(f"[Webhook Handler] Extracted History ID: {history_id} for {email_address}")

            # Delegate processing to the Orchestrator
            orchestrator = EmailProcessingOrchestrator()
            orchestrator.process_incoming_email_notification(history_id, email_address)

            print("--- [Webhook Handler] Notification Handled ---")

        except ValueError as e:
            print(f"[Webhook Handler] Validation Error: {e}")
            raise
        except Exception as e:
            print(f"[Webhook Handler] Unexpected Error: {e}")
            raise

    def _decode_and_validate_message(self):
        if not self.payload or "message" not in self.payload or "data" not in self.payload.get("message", {}):
            raise ValueError("Invalid Pub/Sub payload: missing 'message' or 'data'.")

        message_data = base64.b64decode(self.payload["message"]["data"]).decode("utf-8")
        self.message_json = json.loads(message_data)

        if "emailAddress" not in self.message_json or "historyId" not in self.message_json:
            raise ValueError("Decoded message is invalid: missing 'emailAddress' or 'historyId'.")
