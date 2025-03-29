from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .word import Word


class SampleSentence(SQLModel, table=True):
    __tablename__ = "sample_sentences"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id")
    sentence_korean: str = Field(nullable=False)
    sentence_english: str = Field(nullable=False)

    word: "Word" = Relationship(back_populates="sample_sentences")
