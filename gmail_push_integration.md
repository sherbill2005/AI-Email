# Integrating Gmail Push Notifications for Real-Time Email Processing

This document outlines the step-by-step process for configuring the application to receive real-time push notifications from the Gmail API, process incoming emails automatically, and display the results.

## Goal
To create a fully automated pipeline where a new email in a specified Gmail inbox triggers our service to fetch it, analyze it against our filtering rules, and store the score.

---

## Phase 1: Google Cloud Platform Configuration

This phase sets up the necessary communication channel for Gmail to notify our application.

1.  **Enable Cloud Pub/Sub API:**
    *   Go to your Google Cloud Project console.
    *   Navigate to "APIs & Services" > "Library".
    *   Search for "Cloud Pub/Sub API" and enable it for your project.

2.  **Create a Pub/Sub Topic:**
    *   In the Cloud Console, navigate to "Pub/Sub" > "Topics".
    *   Click "Create Topic".
    *   Give it a Topic ID, for example, `gmail-inbox-changes`.
    *   Ensure "Add a default subscription" is **unchecked**. We will create a push subscription manually.
    *   Click "Create".

3.  **Grant Gmail Permission to Publish:**
    *   Go to the "Topics" page, find your new topic (`gmail-inbox-changes`).
    *   Click the three dots on the right and select "View permissions".
    *   Click "Add Principal".
    *   In the "New principals" field, add the Gmail API service account: `gmail-api-push@system.gserviceaccount.com`.
    *   In the "Assign roles" field, select the role `Pub/Sub Publisher`.
    *   Click "Save".

4.  **Create a Pub/Sub Push Subscription:**
    *   In the Cloud Console, navigate to "Pub/Sub" > "Subscriptions".
    *   Click "Create Subscription".
    *   Give it a Subscription ID, for example, `gmail-webhook-subscription`.
    *   Select the topic you created (`projects/.../topics/gmail-inbox-changes`).
    *   For "Delivery Type", select **Push**.
    *   In the "Endpoint URL" field, enter a placeholder URL for now. This is the URL of our FastAPI webhook. It will look like `https://your-app-domain.com/api/v1/gmail-webhook`.
    *   Leave the other settings as default and click "Create".

---

## Phase 2: FastAPI Backend Implementation

This phase involves writing the code to handle the incoming notifications.

1.  **Define a New Data Model:**
    Create a new schema in a file like `app/schemas/processed_email_schema.py` to define how we store the results.

    ```python
    from pydantic import BaseModel, Field
    from typing import List, Dict

    class ProcessedEmail(BaseModel):
        message_id: str = Field(..., description="The unique ID of the Gmail message.")
        sender: str = Field(..., description="The sender's email address.")
        subject: str = Field(..., description="The email subject.")
        snippet: str = Field(..., description="A short snippet of the email body.")
        scores: List[Dict] = Field(..., description="A list of scores from the filtering rules.")
    ```

2.  **Create the Webhook Endpoint:**
    In a new API file, create the endpoint that Google Pub/Sub will call.

    ```python
    # In a new file, e.g., app/apis/v1/gmail_webhook_api.py
    import base64
    import json
    from fastapi import APIRouter, Request, status, Response

    # Assume we have these services ready to be imported and used
    # from app.services.google_services.gmail_service import GmailService
    # from app.services.filtering_service import EmailFilteringService
    # from app.db_utils.mongo import db

    router = APIRouter()

    @router.post("/gmail-webhook")
    async def gmail_webhook(request: Request):
        """
        Receives push notifications from Google Pub/Sub when a new email arrives.
        """
        payload = await request.json()
        
        # 1. Acknowledge the message immediately to prevent retries
        if not payload or "message" not in payload:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Decode the message from Pub/Sub
            message_data = base64.b64decode(payload["message"]["data"]).decode("utf-8")
            message_json = json.loads(message_data)
            
            history_id = message_json.get("historyId")
            email_address = message_json.get("emailAddress")

            if not history_id or not email_address:
                raise ValueError("Invalid notification payload")

            # 3. Use Gmail API to get the new message details from the historyId
            # gmail_service = GmailService(user_email=email_address)
            # new_message_id = gmail_service.get_latest_message_id_from_history(history_id)
            # message_content = gmail_service.get_message_by_id(new_message_id)

            # 4. Process the email with the filtering service
            # filtering_service = EmailFilteringService()
            # scores = filtering_service.filter_email(message_content)

            # 5. Store the results in MongoDB
            # processed_email_data = {
            #     "message_id": new_message_id,
            #     "sender": message_content["sender"],
            #     "subject": message_content["subject"],
            #     "snippet": message_content["snippet"],
            #     "scores": scores
            # }
            # db.processed_emails.insert_one(processed_email_data)

            print(f"Successfully processed email {new_message_id} for {email_address}")

        except Exception as e:
            print(f"Error processing webhook: {e}")
            # Even on error, return 200 to prevent Google from retrying a failing message
            # You might want more robust error handling here (e.g., sending to a dead-letter queue)
        
        return Response(status_code=status.HTTP_200_OK)

    ```

---

## Phase 3: Activation and Local Development

This phase connects Gmail to our running application.

1.  **Expose Local Server with `ngrok`:**
    *   Run your FastAPI application locally.
    *   In a new terminal, run `ngrok http 8000` (assuming your app runs on port 8000).
    *   `ngrok` will give you a public "Forwarding" URL (e.g., `https://1a2b-3c4d-5e6f.ngrok.io`).

2.  **Update Subscription with `ngrok` URL:**
    *   Go back to your Pub/Sub subscription in the Google Cloud Console.
    *   Edit the subscription and update the "Endpoint URL" to your `ngrok` URL, making sure to append the endpoint path: `https://1a2b-3c4d-5e6f.ngrok.io/api/v1/gmail-webhook`.

3.  **Run the `watch()` command:**
    Create and run a simple Python script to tell Gmail to start sending notifications.

    ```python
    # In a script like `start_watch.py`
    # from app.services.google_services.gmail_service import GmailService

    def start_gmail_watch():
        """
        Tells Gmail to start sending notifications for the user's inbox
        to our configured Pub/Sub topic.
        """
        try:
            # This assumes GmailService is initialized with user credentials
            # gmail_service = GmailService(user_email="your-email@gmail.com")
            
            # The topic name must match what you created in Phase 1
            topic_name = "projects/your-gcp-project-id/topics/gmail-inbox-changes"
            
            # response = gmail_service.get_client().users().watch(
            #     userId="me",
            #     body={
            #         "topicName": topic_name,
            #         "labelIds": ["INBOX"]
            #     }
            # ).execute()
            # print(f"Successfully started watching inbox. History ID: {response['historyId']}")
            pass # Placeholder for actual implementation
        except Exception as e:
            print(f"An error occurred: {e}")

    if __name__ == "__main__":
        start_gmail_watch()
    ```
    Run this script once to activate the notification channel.

---

## Phase 4: Displaying the Output

After emails are processed and their scores are stored in MongoDB, you need a way to view them.

1.  **Create a "Get Results" Endpoint:**
    Add a new `GET` endpoint to your API to fetch the records from the `processed_emails` collection in the database.

    ```python
    # In the same API file: app/apis/v1/gmail_webhook_api.py
    from typing import List
    # from app.schemas.processed_email_schema import ProcessedEmail

    @router.get("/processed-emails", response_model=List[ProcessedEmail])
    async def get_processed_emails(limit: int = 20):
        """
        Retrieves the latest processed emails and their scores from the database.
        """
        # results = db.processed_emails.find().sort("_id", -1).limit(limit)
        # return list(results)
        return [] # Placeholder for actual implementation
    ```

2.  **View the Output:**
    Once the system is running, you can call this endpoint (`GET /api/v1/processed-emails`) using your browser or an API client like Postman to see the results. The output will be a JSON array containing the processed emails and their scores, with the most recent ones first.

    **Example JSON Output:**
    ```json
    [
        {
            "message_id": "18a4d9f8c7b6a5e4",
            "sender": "newsletter@example.com",
            "subject": "Weekly Tech Updates",
            "snippet": "Your weekly summary of the latest in tech, AI, and software development...",
            "scores": [
                {
                    "rule_name": "Urgent Marketing",
                    "score": 0.12,
                    "classification": "Not Urgent"
                },
                {
                    "rule_name": "Project Alpha Comms",
                    "score": 0.89,
                    "classification": "Important"
                }
            ]
        },
        {
            "message_id": "18a4d9f6b5a4c3d2",
            "sender": "teammate@yourcompany.com",
            "subject": "Re: Project Planning",
            "snippet": "Thanks for the document, I will take a look and get back to you shortly.",
            "scores": [
                {
                    "rule_name": "Urgent Marketing",
                    "score": 0.05,
                    "classification": "Not Urgent"
                },
                {
                    "rule_name": "Project Alpha Comms",
                    "score": 0.95,
                    "classification": "Important"
                }
            ]
        }
    ]
    ```
