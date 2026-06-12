from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.timestamp import TimestampSchema

class UserBase(BaseModel):
    name : str
    email : EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class UserResponse(TimestampSchema, UserBase):
    id: int

    class Config:
        from_attributes = True
