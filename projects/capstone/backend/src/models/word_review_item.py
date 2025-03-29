from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .word import Word
    from .study_session import StudySession


class WordReviewItem(SQLModel, table=True):
    __tablename__ = "word_review_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id")
    study_session_id: int = Field(foreign_key="study_sessions.id")
    correct: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    word: "Word" = Relationship(back_populates="review_items")
    study_session: "StudySession" = Relationship(back_populates="review_items")
