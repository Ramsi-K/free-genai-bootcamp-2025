from sqlalchemy.ext.asyncio import AsyncSession
from ...models.word import Word


async def load_words(db: AsyncSession) -> None:
    """Seed database with initial words"""
    from pathlib import Path
    import json

    word_data_path = Path("assets/data/processed/korean_words_2000.json")

    try:
        with open(word_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            # Convert raw JSON data to expected schema
            word = Word(
                korean=item.get("korean", ""),  # Add default values
                english=item.get("meaning", ""),
                part_of_speech=item.get("part_of_speech"),
                romanization=item.get("romanization"),
                topik_level=item.get("topik_level"),
                source_type="initial_seed",
                source_details="korean_words_2000.json",
            )
            db.add(word)

        await db.commit()
        print(f"Successfully seeded {len(data)} words")

    except Exception as e:
        print(f"Error seeding words: {str(e)}")
        await db.rollback()
        raise
