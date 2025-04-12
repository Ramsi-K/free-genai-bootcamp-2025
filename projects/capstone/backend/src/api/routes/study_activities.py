from fastapi import APIRouter, Depends, HTTPException

# Removed unused AsyncSession import
from sqlalchemy import select
from ...database import get_db
from contextlib import asynccontextmanager  # Added import
from ...models.study_activity import StudyActivity
from ...models.study_session import StudySession
from ...schemas.study_activity import (
    StudyActivityCreate,
    # Removed unused StudyActivitySchema import
)

router = APIRouter(prefix="/study_activities", tags=["study_activities"])


@router.get("/{id}")
async def get_study_activity(
    id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Get a study activity by ID"""
    async with db_cm as db:
        query = select(StudyActivity).filter(StudyActivity.id == id)
        result = await db.execute(query)
        activity = result.scalar_one_or_none()
        if not activity:
            raise HTTPException(
                status_code=404, detail="Study activity not found"
            )
        return activity


@router.get("/{id}/study_sessions")
async def get_activity_sessions(
    id: int,
    skip: int = 0,
    limit: int = 100,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Get all study sessions for a study activity"""
    async with db_cm as db:
        # Verify activity exists first
        activity_res = await db.execute(
            select(StudyActivity.id).filter(StudyActivity.id == id)
        )
        if not activity_res.scalar_one_or_none():
            raise HTTPException(
                status_code=404, detail="Study activity not found"
            )

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
    activity: StudyActivityCreate, db_cm: asynccontextmanager = Depends(get_db)
):
    """Create a new study activity"""
    async with db_cm as db:
        db_activity = StudyActivity(**activity.dict())
        db.add(db_activity)
        try:
            await db.commit()
            await db.refresh(db_activity)
            return db_activity
        except Exception as e:  # Catch potential IntegrityError
            await db.rollback()
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create study activity: {e}")
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(
                    status_code=409, detail="Study activity already exists"
                )
            raise HTTPException(
                status_code=500, detail="Failed to create study activity"
            )


@router.get("")
async def get_study_activities(db_cm: asynccontextmanager = Depends(get_db)):
    """Get all study activities"""
    async with db_cm as db:
        query = select(StudyActivity)
        result = await db.execute(query)
        return result.scalars().all()
