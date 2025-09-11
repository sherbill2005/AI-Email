from pydantic import BaseModel, Field
from typing import Optional

class PubSubMessage(BaseModel):
    """Represents the 'message' field within a Pub/Sub notification."""
    data: str = Field(..., description="Base64 encoded message data (contains emailAddress and historyId).")
    messageId: str = Field(..., description="Unique ID of the Pub/Sub message.")
    publishTime: str = Field(..., description="Timestamp when the message was published.")

class PubSubNotification(BaseModel):
    """Represents the full Pub/Sub push notification payload."""
    message: PubSubMessage
    subscription: str = Field(..., description="Name of the subscription that received the message.")
