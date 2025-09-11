from fastapi import APIRouter, Request, status, Response
from app.services.gmail_webhook import GmailWebhookHandler
from app.schemas.pubsub_schema import PubSubNotification
from app.schemas.processed_email_schema import ProcessedEmail # Re-add this import
from typing import List # Re-add this import

router = APIRouter()

@router.post("/gmail-webhook")
async def gmail_webhook(notification: PubSubNotification):
    """
    Receives push notifications from Google Pub/Sub and hands them off
    to a handler class for processing.

    This endpoint always returns a 200 OK to acknowledge receipt
    and prevent Google from resending the notification.
    """
    payload_data = notification.message.data

    try:
        handler_payload = {"message": {"data": payload_data}}
        handler = GmailWebhookHandler(payload=handler_payload)
        handler.process()

    except Exception as e:
        print(f"Error during webhook processing in API layer: {e}")

    # 3. ALWAYS return a 200 OK to Google Pub/Sub.
    print("[API] Returning 200 OK to Pub/Sub.") # New log
    return Response(status_code=status.HTTP_200_OK)


@router.get("/processed-emails", response_model=List[ProcessedEmail], tags=["Webhook"])
async def get_processed_emails(limit: int = 20):
    """
    Retrieves the latest processed emails and their scores from the database.
    """

    from app.db_utils.mongo import db # Re-add this import
    results = db.processed_emails.find().sort("_id", -1).limit(limit)
    return [ProcessedEmail(**r) for r in results]