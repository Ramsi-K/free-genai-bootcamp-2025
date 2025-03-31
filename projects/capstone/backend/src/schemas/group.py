from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .word import WordResponse


class WordGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    is_editable: bool = True


class WordGroupCreate(WordGroupBase):
    pass


class WordGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    is_editable: Optional[bool] = None


class WordGroupResponse(WordGroupBase):
    id: int
    created_at: datetime
    words: List["WordResponse"] = []

    class Config:
        from_attributes = True
