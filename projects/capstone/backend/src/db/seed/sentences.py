import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.sample_sentence import SampleSentence


async def load_sentences(
    db: AsyncSession,
    db_path: str = "assets/data/processed/korean_sentences_2000.json",
) -> None:
    """Seed database with sample sentences"""
    try:
        print("\nLoading sample sentences...")
        start_time = datetime.now()

        with open(db_path, "r", encoding="utf-8") as f:
            sentences_data = json.load(f)

        for item in sentences_data:
            sentence = SampleSentence(
                word_id=item["word_id"],
                sentence_korean=item["example_kr"],
                sentence_english=item["example_en"],
            )
            db.add(sentence)
        await db.commit()

        end_time = datetime.now()
        print(f"Successfully loaded {len(sentences_data)} sentences")
        print(
            f"Duration: {(end_time - start_time).total_seconds():.2f} seconds"
        )

    except Exception as e:
        print(f"Error loading sentences: {str(e)}")
        raise
