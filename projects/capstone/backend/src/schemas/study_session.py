from pydantic import BaseModel
from typing import Optional, Dict, List, ForwardRef
from datetime import datetime
from .word import WordResponse
from .session_stats import SessionStatsResponse  # Update this import

# Forward references for circular imports
ActivityLogResponse = ForwardRef("ActivityLogResponse")


class StudySessionBase(BaseModel):
    config_json: Optional[Dict] = None


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionUpdate(BaseModel):
    ended_at: datetime
    config_json: Optional[Dict] = None


class StudySessionResponse(StudySessionBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    activity_logs: List["ActivityLogResponse"] = []
    session_stats: Optional["SessionStatsResponse"] = None

    class Config:
        orm_mode = True


class StudySession(BaseModel):
    id: int
    group_id: int
    study_activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Update forward references after class definitions
from .activity_log import ActivityLogResponse  # noqa: E402

StudySessionResponse.model_rebuild()
