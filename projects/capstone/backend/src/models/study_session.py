from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .activity_log import ActivityLog
    from .session_stats import SessionStats
    from .word_review_item import WordReviewItem


class StudySession(SQLModel, table=True):
    __tablename__ = "study_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    config_json: Optional[str] = None

    activity_logs: List["ActivityLog"] = Relationship(back_populates="session")
    session_stats: Optional["SessionStats"] = Relationship(
        back_populates="session", sa_relationship_kwargs={"uselist": False}
    )
    review_items: List["WordReviewItem"] = Relationship(
        back_populates="study_session"
    )
