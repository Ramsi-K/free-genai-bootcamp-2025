from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ...database import get_db
from ...models.word import Word
from ...schemas.word import Word as WordSchema, WordCreate

router = APIRouter()


@router.get("", response_model=List[WordSchema])
async def get_words(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    query = select(Word).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{word_id}", response_model=WordSchema)
async def get_word(word_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Word).filter(Word.id == word_id)
    result = await db.execute(query)
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word
