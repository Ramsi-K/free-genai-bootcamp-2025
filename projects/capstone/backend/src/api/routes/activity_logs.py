from fastapi import APIRouter, Depends, HTTPException

# Removed unused AsyncSession import
from sqlalchemy import select
from typing import List, Optional
from ...database import get_db
from contextlib import asynccontextmanager  # Added import
from ...models.activity_log import ActivityLog
from ...models.activity_type import ActivityType
from ...schemas.activity_log import ActivityLogCreate, ActivityLogResponse

router = APIRouter(prefix="/logs", tags=["activity_logs"])


@router.get("", response_model=List[ActivityLogResponse])
async def list_activity_logs(
    skip: int = 0,
    limit: int = 100,
    session_id: Optional[int] = None,
    word_id: Optional[int] = None,
    activity_type: Optional[ActivityType] = None,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """List activity logs with optional filters"""
    async with db_cm as db:
        query = select(ActivityLog)

        if session_id:
            query = query.filter(ActivityLog.session_id == session_id)
        if word_id:
            query = query.filter(ActivityLog.word_id == word_id)
        if activity_type:
            query = query.filter(
                ActivityLog.activity_type == activity_type.value
            )

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


@router.post("", response_model=ActivityLogResponse, status_code=201)
async def create_activity_log(
    log: ActivityLogCreate, db_cm: asynccontextmanager = Depends(get_db)
):
    """Create a new activity log entry"""
    async with db_cm as db:
        db_log = ActivityLog(**log.dict())
        db.add(db_log)

        try:
            await db.commit()
            await db.refresh(db_log)
            return db_log
        except (
            Exception
        ) as e:  # Catch specific exceptions if possible (e.g., IntegrityError)
            await db.rollback()
            # Log the error for debugging
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create activity log: {e}")
            # Provide a more informative error message if possible
            detail = "Failed to create activity log."
            if "FOREIGN KEY constraint failed" in str(e):
                detail += " Ensure session_id and word_id exist."
            elif "UNIQUE constraint failed" in str(e):
                detail += " Duplicate entry detected."  # Example
            raise HTTPException(
                status_code=400,  # Or 500 for unexpected errors
                detail=detail,
            )
