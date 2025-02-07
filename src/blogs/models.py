from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.database import Base

class BlogPosts(Base):

    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, default="in-progress")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    author = relationship("User", back_populates="blog_posts")