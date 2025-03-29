from pydantic import BaseModel
from datetime import datetime


class WrongInputBase(BaseModel):
    word_id: int
    input_text: str


class WrongInputCreate(WrongInputBase):
    pass


class WrongInputResponse(WrongInputBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
