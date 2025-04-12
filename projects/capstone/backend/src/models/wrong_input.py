from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .word import Word


class WrongInput(SQLModel, table=True):
    __tablename__ = "wrong_inputs"

    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id")
    input_text: str = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    word: "Word" = Relationship(back_populates="wrong_inputs")
