from pydantic import BaseModel, Field
from typing import List, Dict

class ProcessedEmail(BaseModel):
    message_id: str = Field(..., description="The message ID")
    sender: str = Field(..., description="The sender email")
    subject: str = Field(..., description="The subject")
    snippet: str = Field(..., description="The snippet of the email body")
    scores: List[Dict] = Field(..., description="The scores of the email body")