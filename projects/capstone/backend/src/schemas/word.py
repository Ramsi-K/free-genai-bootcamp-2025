from pydantic import BaseModel
from typing import Optional, List


class WordExample(BaseModel):
    korean: str
    english: str


class WordBase(BaseModel):
    hangul: str
    romanization: str
    english: str
    type: str
    example_korean: str
    example_english: str


class WordCreate(WordBase):
    pass


class Word(WordBase):
    id: int

    class Config:
        from_attributes = True
