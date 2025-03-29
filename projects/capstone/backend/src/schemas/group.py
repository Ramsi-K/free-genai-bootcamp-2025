from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .word import WordResponse  # Add missing import


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    words_count: int = 0


class GroupCreate(GroupBase):
    pass


class GroupResponse(GroupBase):
    id: int
    created_at: datetime
    words: List["WordResponse"] = []

    class Config:
        from_attributes = True
