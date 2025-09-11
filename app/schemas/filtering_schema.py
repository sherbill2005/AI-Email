from pydantic import BaseModel
from typing import List

class FilterRequest(BaseModel):
    """
    Defines the shape of the request body for the low-level filtering endpoint.
    """
    email_content: str
    rule_ids: List[str]

class FilterResult(BaseModel):
    """
    Defines the shape for a single filtering result.
    """
    matched_rule: str
    score: float
    email_content: str

class RunFilterRequest(BaseModel):
    """
    Defines the request for running the full Gmail filtering process.
    """
    rule_ids: List[str]

class FilterResponse(BaseModel):
    """
    Defines the final shape of the response from the filtering endpoints.
    """
    results: List[FilterResult]
