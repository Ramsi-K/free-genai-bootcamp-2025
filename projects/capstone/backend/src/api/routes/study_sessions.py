from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...database import get_db
from ...models.word import Word
from ...models.study_session import StudySession
from ...models.word_review_item import WordReviewItem

router = APIRouter()


@router.post("/{id}/review")
async def create_word_review(
    id: int, word_id: int, correct: bool, db: AsyncSession = Depends(get_db)
):
    review = WordReviewItem(
        word_id=word_id, study_session_id=id, correct=correct
    )
    db.add(review)
    await db.commit()
    return {"status": "success", "message": "Review recorded."}


@router.get("/{id}/words")
async def get_session_words(
    id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Word)
        .join(WordReviewItem)
        .filter(WordReviewItem.study_session_id == id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("")
async def create_study_session(
    group_id: int, study_activity_id: int, db: AsyncSession = Depends(get_db)
):
    session = StudySession(
        group_id=group_id, study_activity_id=study_activity_id
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"id": session.id, "group_id": session.group_id}
