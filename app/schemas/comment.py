from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse
from app.schemas.timestamp import TimestampSchema
from sqlalchemy.orm import relationship


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)


class CommentResponse(TimestampSchema, CommentBase):
    id: int
    user_id: int
    post_id: int

    class Config:
        from_attributes = True
