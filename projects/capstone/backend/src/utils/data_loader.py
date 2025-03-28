import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.word import Word
from ..models.group import Group


async def load_initial_data(session: AsyncSession):
    data_path = os.path.join("assets", "data", "processed")

    # Load words
    with open(
        os.path.join(data_path, "words.json"), "r", encoding="utf-8"
    ) as f:
        words_data = json.load(f)
        for word_data in words_data:
            word = Word(**word_data)
            session.add(word)

    # Load groups
    with open(
        os.path.join(data_path, "groups.json"), "r", encoding="utf-8"
    ) as f:
        groups_data = json.load(f)
        for group_data in groups_data:
            group = Group(**group_data)
            session.add(group)

    await session.commit()
