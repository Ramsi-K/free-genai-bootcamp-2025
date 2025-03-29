import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from ...database import get_db
from ...models.study_session import StudySession
from ...models.session_stats import SessionStats
from ...schemas.study_session import (
    StudySessionCreate,
    StudySessionUpdate,
    StudySessionResponse,
)
from ...schemas.session_stats import SessionStatsResponse, SessionStatsBase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["study_sessions"])


@router.get("", response_model=List[StudySessionResponse])
async def list_sessions(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """List all study sessions with pagination"""
    query = select(StudySession).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=StudySessionResponse, status_code=201)
async def start_session(
    session: StudySessionCreate, db: AsyncSession = Depends(get_db)
):
    """Start a new study session"""
    logger.info(
        f"Starting new study session with config: {session.config_json}"
    )

    try:
        # Create session
        db_session = StudySession(**session.dict())
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)

        # Initialize session stats
        stats = SessionStats(session_id=db_session.id)
        db.add(stats)
        await db.commit()

        logger.info(f"Session {db_session.id} created successfully")
        return db_session
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        raise


@router.patch("/{session_id}", response_model=StudySessionResponse)
async def update_session(
    session_id: int,
    session: StudySessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a study session (e.g., end it)"""
    result = await db.execute(
        select(StudySession).filter(StudySession.id == session_id)
    )
    db_session = result.scalar_one_or_none()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update session
    for key, value in session.dict(exclude_unset=True).items():
        setattr(db_session, key, value)

    if session.ended_at:  # If ending session, set ended_at
        db_session.ended_at = session.ended_at

    await db.commit()
    await db.refresh(db_session)
    return db_session


@router.delete("/{session_id}")
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a study session and all related data"""
    result = await db.execute(
        select(StudySession).filter(StudySession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()
    return {"message": f"Session {session_id} deleted successfully"}


@router.get("/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session_id: int, db: AsyncSession = Depends(get_db)
):
    """Get statistics for a study session"""
    result = await db.execute(
        select(SessionStats).filter(SessionStats.session_id == session_id)
    )
    stats = result.scalar_one_or_none()
    if not stats:
        raise HTTPException(status_code=404, detail="Session stats not found")
    return stats


@router.patch("/{session_id}/stats", response_model=SessionStatsResponse)
async def update_session_stats(
    session_id: int,
    stats: SessionStatsBase,
    db: AsyncSession = Depends(get_db),
):
    """Update statistics for an ongoing session"""
    logger.info(f"Updating stats for session {session_id}: {stats.dict()}")

    result = await db.execute(
        select(SessionStats).filter(SessionStats.session_id == session_id)
    )
    db_stats = result.scalar_one_or_none()
    if not db_stats:
        raise HTTPException(status_code=404, detail="Session stats not found")

    # Update stats
    for key, value in stats.dict(exclude_unset=True).items():
        setattr(db_stats, key, value)

    # Recalculate accuracy
    if db_stats.total_shown > 0:
        db_stats.accuracy = db_stats.total_correct / db_stats.total_shown

    await db.commit()
    await db.refresh(db_stats)

    logger.info(f"Stats updated. New accuracy: {db_stats.accuracy:.2f}")
    return db_stats
