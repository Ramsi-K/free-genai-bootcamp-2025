from pydantic import BaseModel


class SampleSentenceBase(BaseModel):
    # word_id is provided by the path parameter in the route, not the body
    sentence_korean: str
    sentence_english: str


class SampleSentenceCreate(SampleSentenceBase):
    pass


class SampleSentenceResponse(SampleSentenceBase):
    id: int
    word_id: int  # Add word_id back to the response model

    class Config:
        # orm_mode is deprecated, use from_attributes=True in Pydantic v2
        from_attributes = True
