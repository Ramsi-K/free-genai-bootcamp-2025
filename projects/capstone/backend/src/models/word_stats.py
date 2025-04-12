from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .word import Word  # Import the Word class


class WordStats(SQLModel, table=True):
    __tablename__ = "word_stats"

    word_id: int = Field(foreign_key="words.id", primary_key=True)
    times_seen: int = Field(default=0)
    times_correct: int = Field(default=0)
    current_streak: int = Field(default=0)
    last_seen_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None
    ease_factor: float = Field(default=2.5)
    interval_days: int = Field(default=1)

    word: "Word" = Relationship(back_populates="word_stats")
