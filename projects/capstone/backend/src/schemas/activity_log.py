from pydantic import BaseModel
from datetime import datetime


class ActivityLogCreate(BaseModel):
    session_id: int
    word_id: int
    activity_type: str
    correct: bool
    score: int


class ActivityLogResponse(BaseModel):
    id: int
    session_id: int
    word_id: int
    activity_type: str
    correct: bool
    score: int
    timestamp: datetime


class WordStatsResponse(BaseModel):
    total_activities: int
    total_score: int
    average_score: float
    correct_percentage: float
