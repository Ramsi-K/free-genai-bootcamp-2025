from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WordBase(BaseModel):
    korean: str
    english: str
    part_of_speech: Optional[str] = None
    romanization: Optional[str] = None
    topik_level: Optional[int] = Field(None, ge=1, le=6)
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    added_by_agent: Optional[str] = None


class WordCreate(WordBase):
    pass


class WordResponse(WordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WordUpdate(WordBase):
    korean: Optional[str] = None
    english: Optional[str] = None
    part_of_speech: Optional[str] = None
    romanization: Optional[str] = None
    topik_level: Optional[int] = Field(None, ge=1, le=6)
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    added_by_agent: Optional[str] = None
