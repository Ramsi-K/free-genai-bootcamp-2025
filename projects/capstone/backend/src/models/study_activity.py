from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class StudyActivity(Base):
    __tablename__ = "study_activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String)
    thumbnail_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
