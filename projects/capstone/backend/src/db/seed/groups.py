import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.group import WordGroup
from ...models.word import Word, word_group_map


async def load_groups(
    db: AsyncSession, db_path: str = "assets/data/processed/word_groups.json"
) -> None:
    """Seed database with word groups and their word associations"""
    try:
        print("\n🌱 Loading word groups...")
        start_time = datetime.now()

        with open(db_path, "r", encoding="utf-8") as f:
            groups_data = json.load(f)

        # Load all existing words (map: korean -> Word object)
        existing_words = await db.execute(select(Word))
        word_lookup = {word.korean: word for word in existing_words.scalars()}

        group_count = 0
        link_count = 0

        for group_name, group_info in groups_data["groups"].items():
            db_group = WordGroup(
                name=group_name,
                description=group_info.get("description"),
                source_type=group_info.get("source_type"),
                source_details=group_info.get("source_details"),
            )
            db.add(db_group)
            await db.flush()

            word_ids = []
            for word_obj in group_info.get("words", []):
                hangul = word_obj.get("hangul")
                english = word_obj.get("english")
                romanization = word_obj.get("romanization")

                if not hangul or not english:
                    print(f"⚠️ Skipping invalid word: {word_obj}")
                    continue

                # Insert missing words
                if hangul not in word_lookup:
                    new_word = Word(
                        korean=hangul,
                        english=(
                            ", ".join(english)
                            if isinstance(english, list)
                            else str(english)
                        ),
                        part_of_speech="noun",
                        romanization=romanization,
                        source_type="group_generated",
                        source_details=f"auto from group: {group_name}",
                        added_by_agent="seed_script",
                        created_at=datetime.utcnow(),
                    )
                    db.add(new_word)
                    await db.flush()
                    word_lookup[hangul] = new_word

                word_ids.append(word_lookup[hangul].id)

            if word_ids:
                values = [
                    {"word_id": wid, "group_id": db_group.id}
                    for wid in word_ids
                ]
                await db.execute(word_group_map.insert(), values)
                link_count += len(word_ids)

            group_count += 1

        await db.commit()

        duration = (datetime.now() - start_time).total_seconds()
        print(
            f"✅ Loaded {group_count} groups and {link_count} links in {duration:.2f}s"
        )

    except Exception as e:
        print(f"❌ Error loading groups: {str(e)}")
        raise
