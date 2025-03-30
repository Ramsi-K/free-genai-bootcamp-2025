from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ...database import get_db  # Import the corrected get_db
from ...models.word import Word
from ...models.sample_sentence import SampleSentence
from ...models.word_stats import WordStats
from ...schemas.word import WordCreate, WordUpdate, WordResponse
from ...schemas.sample_sentence import (
    SampleSentenceCreate,
    SampleSentenceResponse,
)
from ...schemas.word_stats import WordStatsResponse, WordStatsUpdate

router = APIRouter(prefix="/words", tags=["words"])


@router.get("", response_model=List[WordResponse])
async def list_words(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """List all words with pagination"""
    query = select(Word).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{word_id}", response_model=WordResponse)
async def get_word(word_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single word by ID"""
    result = await db.execute(select(Word).filter(Word.id == word_id))
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


@router.post("", response_model=WordResponse, status_code=201)
async def create_word(word: WordCreate, db: AsyncSession = Depends(get_db)):
    """Create a new word"""
    db_word = Word(**word.dict())
    db.add(db_word)
    await db.commit()
    await db.refresh(db_word)
    return db_word


@router.put("/{word_id}", response_model=WordResponse)
async def update_word(
    word_id: int, word: WordUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing word"""
    result = await db.execute(select(Word).filter(Word.id == word_id))
    db_word = result.scalar_one_or_none()
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")

    for key, value in word.dict(exclude_unset=True).items():
        setattr(db_word, key, value)
    await db.commit()
    await db.refresh(db_word)
    return db_word


@router.delete("/{word_id}")
async def delete_word(word_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a word"""
    result = await db.execute(select(Word).filter(Word.id == word_id))
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    await db.delete(word)
    await db.commit()
    return {"message": f"Word {word_id} deleted successfully"}


@router.get(
    "/{word_id}/sentences", response_model=List[SampleSentenceResponse]
)
async def get_word_sentences(word_id: int, db: AsyncSession = Depends(get_db)):
    """Get all sample sentences for a word"""
    # First verify word exists
    result = await db.execute(select(Word).filter(Word.id == word_id))
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    # Get sentences
    result = await db.execute(
        select(SampleSentence).filter(SampleSentence.word_id == word_id)
    )
    return result.scalars().all()


@router.post("/{word_id}/sentences", response_model=SampleSentenceResponse)
async def add_word_sentence(
    word_id: int,
    sentence: SampleSentenceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a sample sentence to a word"""
    # First verify word exists
    result = await db.execute(select(Word).filter(Word.id == word_id))
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    # Create sentence
    db_sentence = SampleSentence(word_id=word_id, **sentence.dict())
    db.add(db_sentence)
    await db.commit()
    await db.refresh(db_sentence)
    return db_sentence


@router.get("/{word_id}/stats", response_model=WordStatsResponse)
async def get_word_stats(word_id: int, db: AsyncSession = Depends(get_db)):
    """Get learning statistics for a specific word"""
    result = await db.execute(select(Word).filter(Word.id == word_id))
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    if not word.word_stats:
        raise HTTPException(
            status_code=404, detail="No stats found for this word"
        )
    return word.word_stats


@router.patch("/{word_id}/stats", response_model=WordStatsResponse)
async def update_word_stats(
    word_id: int, stats: WordStatsUpdate, db: AsyncSession = Depends(get_db)
):
    """Update learning statistics for a word (partial update)"""
    result = await db.execute(
        select(WordStats).filter(WordStats.word_id == word_id)
    )
    db_stats = result.scalar_one_or_none()
    if not db_stats:
        raise HTTPException(status_code=404, detail="Word stats not found")

    # Update stats
    for key, value in stats.dict(exclude_unset=True).items():
        setattr(db_stats, key, value)

    await db.commit()
    await db.refresh(db_stats)
    return db_stats
