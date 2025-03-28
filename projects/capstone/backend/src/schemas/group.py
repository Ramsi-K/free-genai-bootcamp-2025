from pydantic import BaseModel


class GroupBase(BaseModel):
    name: str
    words_count: int = 0


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int

    class Config:
        from_attributes = True
