from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class WordReviewItem(Base):
    __tablename__ = "word_review_items"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"))
    correct = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    word = relationship("Word", back_populates="review_items")
    study_session = relationship("StudySession", back_populates="review_items")
