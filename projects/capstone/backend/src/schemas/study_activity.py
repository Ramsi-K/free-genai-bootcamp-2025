from pydantic import BaseModel
from datetime import datetime


class StudyActivityBase(BaseModel):
    name: str
    url: str
    thumbnail_url: str | None = None


class StudyActivityCreate(StudyActivityBase):
    pass


class StudyActivity(StudyActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
