from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    last_processed_history_id: Optional[str] = None


class UserResponse(UserBase):
    class Config:
        orm_mode = True
