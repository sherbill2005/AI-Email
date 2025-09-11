from pydantic import BaseModel
from typing import Optional


class RuleBase(BaseModel):
    name: str
    description: str

class RuleCreate(RuleBase):
    pass

class RuleUpdate(RuleBase):
    name: Optional[str] = None
    description: Optional[str] = None

class RuleResponse(RuleBase):
    id : str
    class Config:
        from_attributes = True