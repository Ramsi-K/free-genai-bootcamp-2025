from sqlmodel import SQLModel, Field


class WordModel(SQLModel, table=True):
    id: int = Field(primary_key=True)
    word: str
    romanization: str
    pos: str
    meaning: str
