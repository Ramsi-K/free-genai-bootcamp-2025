from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from typing import List
from ...database import get_db
from contextlib import asynccontextmanager
from ...models.word import Word
from ...models.sample_sentence import SampleSentence
from ...models.word_stats import WordStats
from ...schemas.word import WordCreate, WordUpdate, WordResponse
from ...schemas.sample_sentence import (
    SampleSentenceCreate,
    SampleSentenceResponse,
)
from ...schemas.word_stats import WordStatsResponse, WordStatsUpdate
import logging

router = APIRouter(prefix="/words", tags=["words"])

# Create a logger for this module
logger = logging.getLogger(__name__)


@router.get("", response_model=List[WordResponse])
async def list_words(
    skip: int = 0,
    limit: int = 100,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """List all words with pagination"""
    async with db_cm as db:
        query = select(Word).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


@router.get("/{word_id}", response_model=WordResponse)
async def get_word(word_id: int, db_cm: asynccontextmanager = Depends(get_db)):
    """Get a single word by ID"""
    async with db_cm as db:
        result = await db.execute(select(Word).filter(Word.id == word_id))
        word = result.scalar_one_or_none()
        if not word:
            raise HTTPException(status_code=404, detail="Word not found")
        return word


@router.post("", response_model=WordResponse, status_code=201)
async def create_word(
    word: WordCreate, db_cm: asynccontextmanager = Depends(get_db)
):
    """Create a new word"""
    async with db_cm as db:
        db_word = Word(**word.dict())
        db.add(db_word)
        try:
            await db.commit()
            await db.refresh(db_word)
            # Consider creating WordStats here too if it should always exist
            return db_word
        except Exception as e:  # Catch potential IntegrityError for duplicates
            await db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create word: {e}")

            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(
                    status_code=409, detail="Word already exists"
                )
            raise HTTPException(
                status_code=500, detail="Failed to create word"
            ) from e


@router.put("/{word_id}", response_model=WordResponse)
async def update_word(
    word_id: int,
    word: WordUpdate,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Update an existing word"""
    async with db_cm as db:
        result = await db.execute(select(Word).filter(Word.id == word_id))
        db_word = result.scalar_one_or_none()
        if not db_word:
            raise HTTPException(status_code=404, detail="Word not found")

        update_data = word.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_word, key, value)
        try:
            await db.commit()
            await db.refresh(db_word)
            return db_word
        except Exception as e:
            await db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update word {word_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update word"
            ) from e


@router.delete("/{word_id}")
async def delete_word(
    word_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Delete a word"""
    async with db_cm as db:
        result = await db.execute(select(Word).filter(Word.id == word_id))
        word = result.scalar_one_or_none()
        if not word:
            raise HTTPException(status_code=404, detail="Word not found")

        try:
            # Cascading deletes should handle related sentences, stats, group maps etc.
            await db.delete(word)
            await db.commit()
            return {"message": f"Word {word_id} deleted successfully"}
        except Exception as e:
            await db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to delete word {word_id}: {e}")
            # Handle potential foreign key constraints if not cascaded properly
            raise HTTPException(
                status_code=500, detail="Failed to delete word"
            ) from e


@router.get(
    "/{word_id}/sentences", response_model=List[SampleSentenceResponse]
)
async def get_word_sentences(
    word_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Get all sample sentences for a word"""
    async with db_cm as db:
        # First verify word exists
        result = await db.execute(
            select(Word.id).filter(Word.id == word_id)
        )  # Only select ID
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Word not found")

        # Get sentences
        result = await db.execute(
            select(SampleSentence).filter(SampleSentence.word_id == word_id)
        )
        logger.info(f"Retrieved sentences for word_id: {word_id}")
        return result.scalars().all()


@router.post("/{word_id}/sentences", response_model=SampleSentenceResponse)
async def add_word_sentence(
    word_id: int,
    sentence: SampleSentenceCreate,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Add a sample sentence to a word"""
    async with db_cm as db:
        # First verify word exists
        result = await db.execute(
            select(Word.id).filter(Word.id == word_id)
        )  # Only select ID
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Word not found")

        # Create sentence
        db_sentence = SampleSentence(word_id=word_id, **sentence.dict())
        db.add(db_sentence)
        try:
            await db.commit()
            await db.refresh(db_sentence)
            return db_sentence
        except Exception as e:
            await db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to add sentence for word {word_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to add sentence"
            ) from e


@router.get("/{word_id}/stats", response_model=WordStatsResponse)
async def get_word_stats(
    word_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Get learning statistics for a specific word"""
    async with db_cm as db:
        # Query WordStats directly
        result = await db.execute(
            select(WordStats).filter(WordStats.word_id == word_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            # Check if word exists
            word_res = await db.execute(
                select(Word.id).filter(Word.id == word_id)
            )
            if not word_res.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Word not found")
            # If word exists but stats don't, create them
            db_stats = WordStats(word_id=word_id)
            db.add(db_stats)
            await db.commit()
            await db.refresh(db_stats)
            return db_stats

        return stats


@router.patch("/{word_id}/stats", response_model=WordStatsResponse)
async def update_word_stats(
    word_id: int,
    stats_update: WordStatsUpdate,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Update learning statistics for a word (partial update)"""
    async with db_cm as db:
        result = await db.execute(
            select(WordStats).filter(WordStats.word_id == word_id)
        )
        db_stats = result.scalar_one_or_none()
        if not db_stats:
            # Check if word exists
            word_res = await db.execute(
                select(Word.id).filter(Word.id == word_id)
            )
            if not word_res.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Word not found")
            # Optionally create stats if they don't exist? For now, 404.
            raise HTTPException(status_code=404, detail="Word stats not found")

        # Update stats
        update_data = stats_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_stats, key, value)

        try:
            await db.commit()
            await db.refresh(db_stats)
            return db_stats
        except Exception as e:
            await db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update stats for word {word_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update word stats"
            ) from e
