from pydantic import BaseModel
from typing import Optional, List


class RuleBase(BaseModel):
    name: str
    description: str
    priority: Optional[str] = "low"
    sub_rules: List['RuleBase'] = []

class RuleCreate(RuleBase):
    pass

class RuleUpdate(RuleBase):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    sub_rules: Optional[List['RuleBase']] = None

class RuleResponse(RuleBase):
    id : str
    class Config:
        from_attributes = True
        validate_assignment = False
        smart_union = True