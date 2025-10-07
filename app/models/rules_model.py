from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional, List

class RulesPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RuleModel(BaseModel):
    id: str = Field(None, alias="_id")
    user_id: str
    name: str
    description: str
    priority: Optional[str] = "low"
    sub_rules: List['RuleModel'] = []


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        validate_assignment = True
        smart_union = True