from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WordStatsBase(BaseModel):
    word_id: int
    times_seen: int = 0
    times_correct: int = 0
    current_streak: int = 0
    ease_factor: float = Field(default=2.5, ge=1.3)
    interval_days: int = Field(default=1, ge=1)


class WordStatsCreate(WordStatsBase):
    pass


class WordStatsResponse(WordStatsBase):
    last_seen_at: Optional[datetime] = None
    next_due_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class WordStatsUpdate(BaseModel):
    times_seen: Optional[int] = None
    times_correct: Optional[int] = None
    current_streak: Optional[int] = None
    ease_factor: Optional[float] = Field(None, ge=1.3)
    interval_days: Optional[int] = Field(None, ge=1)
