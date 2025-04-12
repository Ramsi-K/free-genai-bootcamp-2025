from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from .associations import word_group_map  # Import from single source of truth

if TYPE_CHECKING:
    from .group import WordGroup
    from .sample_sentence import SampleSentence
    from .activity_log import ActivityLog
    from .word_stats import WordStats
    from .wrong_input import WrongInput
    from .word_review_item import WordReviewItem


class Word(SQLModel, table=True):
    __tablename__ = "words"  # Explicitly set table name

    id: Optional[int] = Field(default=None, primary_key=True)
    korean: str = Field(nullable=False)
    english: str = Field(nullable=False)
    part_of_speech: Optional[str] = None
    romanization: Optional[str] = None
    topik_level: Optional[int] = None
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    added_by_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    groups: List["WordGroup"] = Relationship(
        back_populates="words",
        sa_relationship_kwargs={
            "secondary": word_group_map,
            # No cascade needed here usually, association table handles it
        },
    )
    sample_sentences: List["SampleSentence"] = Relationship(
        back_populates="word",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    activity_logs: List["ActivityLog"] = Relationship(
        back_populates="word",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    word_stats: Optional["WordStats"] = Relationship(
        back_populates="word",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },
    )
    wrong_inputs: List["WrongInput"] = Relationship(
        back_populates="word",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    review_items: List["WordReviewItem"] = Relationship(
        back_populates="word",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


@property
def created_at_utc(self):
    return datetime.now(timezone.utc)
