import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from ...database import get_db
from ...models.wrong_input import WrongInput
from ...models.word_stats import WordStats
from ...models.word import Word
from ...schemas.wrong_input import WrongInputCreate, WrongInputResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["mistakes"])


@router.get(
    "/words/{word_id}/mistakes", response_model=List[WrongInputResponse]
)
async def get_word_mistakes(
    word_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all wrong inputs for a specific word"""
    # First verify word exists
    word_exists = await db.execute(
        select(func.count()).select_from(Word).filter(Word.id == word_id)
    )
    if word_exists.scalar() == 0:
        raise HTTPException(status_code=404, detail="Word not found")

    # Get wrong inputs
    query = (
        select(WrongInput)
        .filter(WrongInput.word_id == word_id)
        .order_by(WrongInput.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/mistakes", response_model=WrongInputResponse, status_code=201)
async def log_mistake(
    mistake: WrongInputCreate, db: AsyncSession = Depends(get_db)
):
    """Log a wrong input and update word stats"""
    logger.info(
        f"Logging mistake for word {mistake.word_id}: {mistake.input_text}"
    )

    try:
        # Create wrong input entry
        db_mistake = WrongInput(**mistake.dict())
        db.add(db_mistake)

        # Update word stats
        result = await db.execute(
            select(WordStats).filter(WordStats.word_id == mistake.word_id)
        )
        word_stats = result.scalar_one_or_none()

        if word_stats:
            logger.info(
                f"Current streak: {word_stats.current_streak}, Ease factor: {word_stats.ease_factor}"
            )
            # Reset streak since there was a mistake
            word_stats.current_streak = 0
            # Adjust ease factor
            word_stats.ease_factor = max(1.3, word_stats.ease_factor - 0.2)
            # Reduce interval
            word_stats.interval_days = max(1, word_stats.interval_days // 2)
            logger.info(
                f"Updated: Streak reset, New ease factor: {word_stats.ease_factor}"
            )

        await db.commit()
        await db.refresh(db_mistake)
        return db_mistake

    except Exception as e:
        logger.error(f"Failed to log mistake: {str(e)}")
        raise


@router.get("/mistakes/stats", response_model=dict)
async def get_mistake_stats(word_id: int, db: AsyncSession = Depends(get_db)):
    """Get mistake statistics for a word"""
    # Count total mistakes
    mistakes_count = await db.execute(
        select(func.count())
        .select_from(WrongInput)
        .filter(WrongInput.word_id == word_id)
    )

    # Get most recent mistakes
    recent_mistakes = await db.execute(
        select(WrongInput)
        .filter(WrongInput.word_id == word_id)
        .order_by(WrongInput.timestamp.desc())
        .limit(5)
    )

    return {
        "total_mistakes": mistakes_count.scalar(),
        "recent_mistakes": [m.input_text for m in recent_mistakes.scalars()],
        "last_mistake_at": (
            recent_mistakes.first().timestamp
            if recent_mistakes.first()
            else None
        ),
    }
