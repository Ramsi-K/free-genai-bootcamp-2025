from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db, Base, engine
from ...models.word_review_item import WordReviewItem
from ...models.study_session import StudySession

router = APIRouter()


@router.post("/reset_history")
async def reset_history(db: AsyncSession = Depends(get_db)):
    await db.execute(WordReviewItem.__table__.delete())
    await db.execute(StudySession.__table__.delete())
    await db.commit()
    return {"status": "success", "message": "Study history reset."}


@router.post("/full_reset")
async def full_reset(db: AsyncSession = Depends(get_db)):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"status": "success", "message": "Database fully reset."}
