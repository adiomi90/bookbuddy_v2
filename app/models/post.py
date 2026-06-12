from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.deps import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now(),
                        nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    owner = relationship("User", back_populates="posts")
    comments= relationship("Comment", back_populates="posts")