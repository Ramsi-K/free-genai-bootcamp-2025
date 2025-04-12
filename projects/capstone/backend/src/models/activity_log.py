# from sqlmodel import SQLModel, Field, Relationship
# from typing import Optional, TYPE_CHECKING
# from datetime import datetime

# if TYPE_CHECKING:
#     from .study_session import StudySession
#     from .word import Word

# from .activity_type import ActivityType


# class ActivityLog(SQLModel, table=True):
#     __tablename__ = "activity_logs"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     session_id: int = Field(foreign_key="study_sessions.id")
#     word_id: int = Field(foreign_key="words.id")
#     activity_type: str = Field(nullable=False)
#     input_text: Optional[str] = None
#     correct: bool = Field(nullable=False)
#     score: int = Field(nullable=False)
#     image_path: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow)

#     session: "StudySession" = Relationship(back_populates="activity_logs")
#     word: "Word" = Relationship(back_populates="activity_logs")

#     @property
#     def activity_type_enum(self) -> ActivityType:
#         return ActivityType(self.activity_type)

#     @activity_type_enum.setter
#     def activity_type_enum(self, value: ActivityType):
#         self.activity_type = value.value
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from .activity_type import ActivityType

if TYPE_CHECKING:
    from .word import Word
    from .study_session import StudySession


class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="study_sessions.id")
    word_id: int = Field(foreign_key="words.id")
    activity_type: str = Field(nullable=False)
    correct: bool = Field(default=False)
    score: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    word: "Word" = Relationship(back_populates="activity_logs")
    session: "StudySession" = Relationship(back_populates="activity_logs")
