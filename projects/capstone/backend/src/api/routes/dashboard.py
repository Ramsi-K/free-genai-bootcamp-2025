from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ...database import get_db
from ...models.study_session import StudySession
from ...models.word_review_item import WordReviewItem
from ...models.word import Word
from ...models.group import Group

router = APIRouter()


@router.get("/last_study_session")
async def get_last_study_session(db: AsyncSession = Depends(get_db)):
    query = (
        select(StudySession).order_by(StudySession.created_at.desc()).limit(1)
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    return session


@router.get("/study_progress")
async def get_study_progress(db: AsyncSession = Depends(get_db)):
    query = select(
        func.count(WordReviewItem.id)
        .filter(WordReviewItem.correct == True)
        .label("correct"),
        func.count(WordReviewItem.id)
        .filter(WordReviewItem.correct == False)
        .label("incorrect"),
    )
    result = await db.execute(query)
    stats = result.one()
    return {"correct": stats.correct, "incorrect": stats.incorrect}


@router.get("/quick-stats")
async def get_quick_stats(db: AsyncSession = Depends(get_db)):
    words_query = select(func.count().label("total_words")).select_from(Word)
    groups_query = select(func.count().label("total_groups")).select_from(
        Group
    )
    sessions_query = select(func.count().label("total_sessions")).select_from(
        StudySession
    )

    words_count = await db.scalar(words_query)
    groups_count = await db.scalar(groups_query)
    sessions_count = await db.scalar(sessions_query)

    return {
        "total_words": words_count,
        "total_groups": groups_count,
        "total_sessions": sessions_count,
    }
