from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Word(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    korean: str
    english: str
    part_of_speech: Optional[str] = None
    romanization: Optional[str] = None
    topik_level: Optional[int] = None
    source_type: Optional[str] = None
    source_details: Optional[str] = None
    added_by_agent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ...rest of models following same pattern for other tables...
