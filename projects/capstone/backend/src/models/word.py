from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..database import Base

words_groups = Table(
    "words_groups",
    Base.metadata,
    Column("word_id", Integer, ForeignKey("words.id")),
    Column("group_id", Integer, ForeignKey("groups.id")),
)


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    hangul = Column(String)
    romanization = Column(String)
    english = Column(String)
    type = Column(String)
    example_korean = Column(String)
    example_english = Column(String)

    groups = relationship(
        "Group", secondary=words_groups, back_populates="words"
    )
    review_items = relationship("WordReviewItem", back_populates="word")
