from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .associations import word_group_map  # Import from single source of truth

if TYPE_CHECKING:
    from .word import Word


class WordGroup(SQLModel, table=True):
    __tablename__ = "word_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    source_type: Optional[str] = Field(default=None)
    source_details: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_editable: bool = Field(default=True)
    group_type: Optional[str] = Field(
        default=None
    )  # Added group_type attribute

    words: List["Word"] = Relationship(
        back_populates="groups",
        sa_relationship_kwargs={
            "secondary": word_group_map,
        },
    )
