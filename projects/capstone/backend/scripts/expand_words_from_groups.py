import json
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.word import Word
from src.database import async_session_factory


async def insert_missing_words_from_groups(json_path: str):
    async with async_session_factory() as db:
        print("\n📦 Expanding words from group JSON...\n")
        with open(json_path, "r", encoding="utf-8") as f:
            group_data = json.load(f)

        # Validate format
        if "groups" not in group_data or not isinstance(
            group_data["groups"], dict
        ):
            raise ValueError("Invalid format: missing 'groups' key in JSON")

        # Build lookup of existing Korean words
        existing = await db.execute(select(Word.korean))
        existing_korean_words = {w for (w,) in existing.fetchall()}

        new_words = []
        for group_name, group_info in group_data["groups"].items():
            for word_obj in group_info.get("words", []):
                hangul = word_obj.get("hangul")
                english = word_obj.get("english")

                if not hangul or not english:
                    continue

                if hangul in existing_korean_words:
                    continue

                # Create new Word instance
                word = Word(
                    korean=hangul,
                    english=(
                        ", ".join(english)
                        if isinstance(english, list)
                        else str(english)
                    ),
                    part_of_speech="noun",  # Default guess
                    romanization=word_obj.get("romanization"),
                    source_type="group_generated",
                    source_details=f"auto from group: {group_name}",
                    added_by_agent="seed_script",
                    created_at=datetime.utcnow(),
                )
                new_words.append(word)

        if new_words:
            print(f"🚀 Inserting {len(new_words)} new words...")
            db.add_all(new_words)
            await db.commit()
        else:
            print("✅ No new words to insert — DB already up to date.")


if __name__ == "__main__":
    asyncio.run(
        insert_missing_words_from_groups(
            "assets/data/processed/word_groups.json"
        )
    )
