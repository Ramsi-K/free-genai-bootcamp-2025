from pydantic import BaseModel
from datetime import datetime


class StudySession(BaseModel):
    id: int
    group_id: int
    study_activity_id: int
    created_at: datetime

    class Config:
        from_attributes = True
