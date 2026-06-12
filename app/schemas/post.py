from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.timestamp import TimestampSchema


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostResponse(TimestampSchema, PostBase):
    id: int

    class Config:
        from_attributes = True
