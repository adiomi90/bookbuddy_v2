from sqlalchemy import DateTime, Integer, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.deps import Base
from typing import List, Optional
from datetime import datetime

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column (DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),
                                             onupdate=func.now(), nullable=False)
    
   
    owner: Mapped["User"] = relationship(back_populates="comments")
    posts: Mapped["Post"] = relationship(back_populates="comments")

    parent: Mapped["Comment | None"] = relationship(back_populates="replies", remote_side=[id])
    replies: Mapped[List["Comment"]] = relationship(back_populates="parent", lazy="selectin", order_by="Comment.created_at")