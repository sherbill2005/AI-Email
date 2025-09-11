from pydantic import BaseModel, Field, field_validator
from typing import Optional


class RuleModel(BaseModel):
    id: str = Field(None, alias="_id")
    name: str
    description: str



    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
