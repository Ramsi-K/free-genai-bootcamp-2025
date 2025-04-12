from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class StudyActivity(SQLModel, table=True):
    __tablename__ = "study_activities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    url: str = Field()
    thumbnail_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
