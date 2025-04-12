from sqlmodel import SQLModel, Table, Column, Integer, ForeignKey

word_group_map = Table(
    "word_group_map",
    SQLModel.metadata,
    Column("word_id", Integer, ForeignKey("words.id", ondelete="CASCADE")),
    Column(
        "group_id", Integer, ForeignKey("word_groups.id", ondelete="CASCADE")
    ),
)
