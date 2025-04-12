import logging
from fastapi import APIRouter, Depends, HTTPException

# Removed unused AsyncSession import
from sqlalchemy import select, func
from typing import List
from ...database import get_db
from contextlib import asynccontextmanager  # Added import
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
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Get all wrong inputs for a specific word"""
    async with db_cm as db:
        # First verify word exists
        word_exists_res = await db.execute(
            select(func.count(Word.id)).filter(
                Word.id == word_id
            )  # Count specific column
        )
        if word_exists_res.scalar() == 0:
            raise HTTPException(status_code=404, detail="Word not found")

        # Get wrong inputs
        query = (
            select(WrongInput)
            .filter(WrongInput.word_id == word_id)
            .order_by(WrongInput.timestamp.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


@router.post("/mistakes", response_model=WrongInputResponse, status_code=201)
async def log_mistake(
    mistake: WrongInputCreate, db_cm: asynccontextmanager = Depends(get_db)
):
    """Log a wrong input and update word stats"""
    logger.info(
        f"Logging mistake for word {mistake.word_id}: {mistake.input_text}"
    )
    async with db_cm as db:
        try:
            # Verify word exists first
            word_res = await db.execute(
                select(Word.id).filter(Word.id == mistake.word_id)
            )
            if not word_res.scalar_one_or_none():
                raise HTTPException(
                    status_code=404,
                    detail=f"Word with id {mistake.word_id} not found",
                )

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
                # Adjust ease factor (ensure it doesn't go below minimum)
                word_stats.ease_factor = max(1.3, word_stats.ease_factor - 0.2)
                # Reduce interval (ensure it doesn't go below minimum)
                word_stats.interval_days = max(
                    1, word_stats.interval_days // 2
                )
                logger.info(
                    f"Updated: Streak reset, New ease factor: {word_stats.ease_factor}, New interval: {word_stats.interval_days}"
                )
            else:
                # Handle case where WordStats might not exist yet for the word
                logger.warning(
                    f"No WordStats found for word_id {mistake.word_id}. Cannot update stats."
                )

            await db.commit()
            await db.refresh(db_mistake)
            return db_mistake

        except Exception as e:
            await db.rollback()  # Rollback on error
            logger.error(f"Failed to log mistake: {e}")
            # Check for specific errors like foreign key violation if word_id is invalid
            raise HTTPException(
                status_code=500, detail="Failed to log mistake"
            )


@router.get("/mistakes/stats", response_model=dict)
async def get_mistake_stats(
    word_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Get mistake statistics for a word"""
    async with db_cm as db:
        # Verify word exists
        word_exists_res = await db.execute(
            select(func.count(Word.id)).filter(Word.id == word_id)
        )
        if word_exists_res.scalar() == 0:
            raise HTTPException(status_code=404, detail="Word not found")

        # Count total mistakes
        mistakes_count_res = await db.execute(
            select(func.count(WrongInput.id)).filter(  # Count specific column
                WrongInput.word_id == word_id
            )
        )
        total_mistakes = mistakes_count_res.scalar()

        # Get most recent mistakes
        recent_mistakes_res = await db.execute(
            select(WrongInput)
            .filter(WrongInput.word_id == word_id)
            .order_by(WrongInput.timestamp.desc())
            .limit(5)
        )
        recent_mistakes_list = recent_mistakes_res.scalars().all()

        # Get the timestamp of the very first mistake record found by the query
        last_mistake_timestamp = (
            recent_mistakes_list[0].timestamp if recent_mistakes_list else None
        )

        return {
            "total_mistakes": total_mistakes,
            "recent_mistakes": [m.input_text for m in recent_mistakes_list],
            "last_mistake_at": last_mistake_timestamp,
        }
