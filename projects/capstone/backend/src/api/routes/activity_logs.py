from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ...database import get_db
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
    db: AsyncSession = Depends(get_db),
):
    """List activity logs with optional filters"""
    query = select(ActivityLog)

    if session_id:
        query = query.filter(ActivityLog.session_id == session_id)
    if word_id:
        query = query.filter(ActivityLog.word_id == word_id)
    if activity_type:
        query = query.filter(ActivityLog.activity_type == activity_type.value)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ActivityLogResponse, status_code=201)
async def create_activity_log(
    log: ActivityLogCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new activity log entry"""
    db_log = ActivityLog(**log.dict())
    db.add(db_log)

    try:
        await db.commit()
        await db.refresh(db_log)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to create activity log. Verify session_id and word_id exist.",
        )

    return db_log
