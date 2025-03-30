# from pydantic import BaseModel
# from typing import Optional, TYPE_CHECKING
# from datetime import datetime
# from ..models.activity_type import ActivityType

# if TYPE_CHECKING:
#     from .word import WordResponse


# class ActivityLogBase(BaseModel):
#     word_id: int
#     session_id: int
#     activity_type: ActivityType  # Changed from str to ActivityType enum
#     input_text: Optional[str] = None
#     correct: bool
#     score: int
#     image_path: Optional[str] = None


# class ActivityLogCreate(ActivityLogBase):
#     pass


# class ActivityLogResponse(ActivityLogBase):
#     id: int
#     timestamp: datetime
#     word: "WordResponse"

#     class Config:
#         orm_mode = True
#         model_rebuild = True


from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .word import WordResponse
from .study_session import StudySessionResponse


class ActivityLogBase(BaseModel):
    session_id: int
    word_id: int
    activity_type: str
    correct: bool
    score: int


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(ActivityLogBase):
    id: int
    timestamp: datetime
    word: Optional[WordResponse] = None
    session: Optional[StudySessionResponse] = None

    class Config:
        from_attributes = True
