import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Word, Group, StudyActivity


async def load_initial_data(session: AsyncSession):
    print("\n=== Starting Data Loading Process ===")

    try:
        word_groups_path = os.path.join(
            "assets", "data", "processed", "word_groups.json"
        )
        print(f"Loading word groups from: {os.path.abspath(word_groups_path)}")

        if not os.path.exists(word_groups_path):
            print(f"ERROR: {word_groups_path} not found!")
            return

        with open(word_groups_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            groups_data = data.get("groups", {})
            print(f"Found {len(groups_data)} groups")

            for group_name, group_info in groups_data.items():
                # Create theme group
                group = Group(
                    name=group_name,
                    group_type="theme",
                    words_count=len(group_info.get("words", [])),
                )
                session.add(group)
                await session.flush()

                # Add words for this group
                for word_info in group_info.get("words", []):
                    if all(
                        k in word_info
                        for k in ["hangul", "romanization", "english"]
                    ):
                        word = Word(
                            hangul=word_info["hangul"],
                            romanization=word_info["romanization"],
                            english=word_info["english"][
                                0
                            ],  # Take first English translation
                            type="word",
                        )
                        session.add(word)
                        word.groups.append(group)
                        await session.flush()

        await session.commit()
        print("Successfully loaded groups and words")

    except Exception as e:
        print(f"Error loading groups: {e}")
        await session.rollback()
        raise

    # Create study activities
    activities = [
        {
            "name": "Flashcards",
            "url": "/flashcards",
            "thumbnail_url": "/images/flashcards.png",
        },
        {
            "name": "Writing Practice",
            "url": "/writing",
            "thumbnail_url": "/images/writing.png",
        },
        {
            "name": "Word Muncher",
            "url": "/games/muncher",
            "thumbnail_url": "/images/muncher.png",
        },
    ]

    try:
        for activity_data in activities:
            activity = StudyActivity(**activity_data)
            session.add(activity)
        await session.commit()
        print("Successfully created study activities")
    except Exception as e:
        print(f"ERROR creating study activities: {e}")
        await session.rollback()

    print("=== Data Loading Complete ===\n")
