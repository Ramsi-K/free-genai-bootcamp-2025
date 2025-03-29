from pydantic import BaseModel


class SampleSentenceBase(BaseModel):
    word_id: int
    sentence_korean: str
    sentence_english: str


class SampleSentenceCreate(SampleSentenceBase):
    pass


class SampleSentenceResponse(SampleSentenceBase):
    id: int

    class Config:
        orm_mode = True
