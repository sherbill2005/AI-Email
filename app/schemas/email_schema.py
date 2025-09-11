from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    email_index: int


class SummarizeResponse(BaseModel):
    summaries: str
