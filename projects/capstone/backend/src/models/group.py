from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from .word import words_groups


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    words_count = Column(Integer, default=0)

    words = relationship(
        "Word", secondary=words_groups, back_populates="groups"
    )
    study_sessions = relationship("StudySession", back_populates="group")
