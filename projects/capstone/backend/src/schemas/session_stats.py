from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionStatsBase(BaseModel):
    total_words: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    accuracy: float = 0.0
    average_response_time: float = 0.0


class SessionStatsCreate(SessionStatsBase):
    study_session_id: int


class SessionStatsResponse(SessionStatsBase):
    id: int
    study_session_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Note: The error was from trying to import SessionStatsUpdate which wasn't needed
# We'll use SessionStatsBase for updates instead
