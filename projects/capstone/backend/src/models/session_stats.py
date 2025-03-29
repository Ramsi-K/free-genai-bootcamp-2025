from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    Table,
    Column,
    Integer,
    ForeignKey,
)
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .word import Word

if TYPE_CHECKING:
    from .study_session import StudySession

# Association table for words shown in session
session_words_shown = Table(
    "session_words_shown",
    SQLModel.metadata,
    Column("session_id", Integer, ForeignKey("session_stats.id")),
    Column("word_id", Integer, ForeignKey("words.id")),
)


class SessionStats(SQLModel, table=True):
    __tablename__ = "session_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="study_sessions.id")
    total_shown: int = Field(default=0)
    total_correct: int = Field(default=0)
    accuracy: float = Field(default=0.0)
    level: int = Field(default=1)

    session: "StudySession" = Relationship(back_populates="session_stats")
    words_shown: List["Word"] = Relationship(
        sa_relationship_kwargs={
            "secondary": session_words_shown,
            "backref": "shown_in_sessions",
        }
    )
