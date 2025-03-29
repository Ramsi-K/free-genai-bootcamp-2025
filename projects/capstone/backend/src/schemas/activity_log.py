from pydantic import BaseModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from ..models.activity_type import ActivityType

if TYPE_CHECKING:
    from .word import WordResponse


class ActivityLogBase(BaseModel):
    word_id: int
    session_id: int
    activity_type: ActivityType  # Changed from str to ActivityType enum
    input_text: Optional[str] = None
    correct: bool
    score: int
    image_path: Optional[str] = None


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(ActivityLogBase):
    id: int
    timestamp: datetime
    word: "WordResponse"

    class Config:
        orm_mode = True
        model_rebuild = True
