import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.group import WordGroup
from ...models.word import word_group_map


async def load_groups(
    db: AsyncSession, db_path: str = "assets/data/processed/word_groups.json"
) -> None:
    """Seed database with word groups and their word associations"""
    try:
        print("\nLoading word groups...")
        start_time = datetime.now()

        with open(db_path, "r", encoding="utf-8") as f:
            groups_data = json.load(f)

        # Create groups
        for group in groups_data:
            db_group = WordGroup(
                name=group["name"],
                description=group.get("description"),
                source_type=group.get("source_type"),
                source_details=group.get("source_details"),
            )
            db.add(db_group)
            await db.flush()

            # Add word associations if any
            if "word_ids" in group:
                values = [
                    {"word_id": word_id, "group_id": db_group.id}
                    for word_id in group["word_ids"]
                ]
                await db.execute(word_group_map.insert(), values)

        await db.commit()

        end_time = datetime.now()
        print(f"Successfully loaded {len(groups_data)} groups")
        duration = (end_time - start_time).total_seconds()
        print(f"Duration: {duration:.2f} seconds")

    except Exception as e:
        print(f"Error loading groups: {str(e)}")
        raise
