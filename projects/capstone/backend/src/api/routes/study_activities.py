from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...database import get_db  # Import get_db
from ...models.study_activity import StudyActivity
from ...models.study_session import StudySession
from ...schemas.study_activity import (
    StudyActivityCreate,
    StudyActivity as StudyActivitySchema,
)

router = APIRouter(prefix="/study_activities", tags=["study_activities"])


@router.get("/{id}")
async def get_study_activity(id: int, db: AsyncSession = Depends(get_db)):
    """Get a study activity by ID"""
    query = select(StudyActivity).filter(StudyActivity.id == id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Study activity not found")
    return activity


@router.get("/{id}/study_sessions")
async def get_activity_sessions(
    id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all study sessions for a study activity"""
    query = (
        select(StudySession)
        .filter(StudySession.study_activity_id == id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("")
async def create_study_activity(
    activity: StudyActivityCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new study activity"""
    db_activity = StudyActivity(**activity.dict())
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity


@router.get("")
async def get_study_activities(db: AsyncSession = Depends(get_db)):
    """Get all study activities"""
    query = select(StudyActivity)
    result = await db.execute(query)
    return result.scalars().all()
