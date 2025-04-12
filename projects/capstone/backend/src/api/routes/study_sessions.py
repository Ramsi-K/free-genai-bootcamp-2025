import logging
from fastapi import APIRouter, Depends, HTTPException

# Removed unused AsyncSession import
from sqlalchemy import select
from typing import List
from datetime import datetime
from ...database import get_db
from contextlib import asynccontextmanager  # Added import
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
    skip: int = 0,
    limit: int = 100,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """List all study sessions with pagination"""
    async with db_cm as db:
        query = select(StudySession).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


@router.post("", response_model=StudySessionResponse, status_code=201)
async def start_session(
    session: StudySessionCreate, db_cm: asynccontextmanager = Depends(get_db)
):
    """Start a new study session"""
    logger.info(
        f"Starting new study session with config: {session.config_json}"
    )
    async with db_cm as db:
        try:
            # Create session
            db_session = StudySession(**session.dict())
            db.add(db_session)
            await db.commit()
            await db.refresh(db_session)

            # Initialize session stats
            stats = SessionStats(session_id=db_session.id)
            db.add(stats)
            await db.commit()  # Commit again for stats

            logger.info(f"Session {db_session.id} created successfully")
            await db.refresh(
                db_session
            )  # Refresh again to load stats relationship if needed by response model
            return db_session
        except Exception as e:
            await db.rollback()  # Rollback on error
            logger.error(f"Failed to create session: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create session"
            )


@router.patch("/{session_id}", response_model=StudySessionResponse)
async def update_session(
    session_id: int,
    session: StudySessionUpdate,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Update a study session (e.g., end it)"""
    async with db_cm as db:
        result = await db.execute(
            select(StudySession).filter(StudySession.id == session_id)
        )
        db_session = result.scalar_one_or_none()
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update session
        update_data = session.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_session, key, value)

        # Ensure ended_at is set if provided
        if "ended_at" in update_data and update_data["ended_at"]:
            db_session.ended_at = update_data["ended_at"]

        try:
            await db.commit()
            await db.refresh(db_session)
            return db_session
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update session {session_id}: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to update session"
            )


@router.delete("/{session_id}")
async def delete_session(
    session_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Delete a study session and all related data"""
    async with db_cm as db:
        result = await db.execute(
            select(StudySession).filter(StudySession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        try:
            # Note: Cascading deletes should handle related stats, logs etc. if configured in models
            await db.delete(session)
            await db.commit()
            return {"message": f"Session {session_id} deleted successfully"}
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to delete session"
            )


@router.get("/{session_id}/stats", response_model=SessionStatsResponse)
async def get_session_stats(
    session_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Get statistics for a study session"""
    async with db_cm as db:
        result = await db.execute(
            select(SessionStats).filter(SessionStats.session_id == session_id)
        )
        stats = result.scalar_one_or_none()
        if not stats:
            # Check if session exists to give better error
            session_res = await db.execute(
                select(StudySession.id).filter(StudySession.id == session_id)
            )
            if not session_res.scalar_one_or_none():
                raise HTTPException(
                    status_code=404, detail="Session not found"
                )
            # If session exists but stats don't, it's an internal issue or stats weren't created
            logger.warning(
                f"Stats not found for existing session {session_id}"
            )
            raise HTTPException(
                status_code=404, detail="Session stats not found"
            )
        return stats


@router.patch("/{session_id}/stats", response_model=SessionStatsResponse)
async def update_session_stats(
    session_id: int,
    stats_update: SessionStatsBase,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Update statistics for an ongoing session"""
    logger.info(
        f"Updating stats for session {session_id}: {stats_update.dict()}"
    )
    async with db_cm as db:
        result = await db.execute(
            select(SessionStats).filter(SessionStats.session_id == session_id)
        )
        db_stats = result.scalar_one_or_none()
        if not db_stats:
            # Check if session exists
            session_res = await db.execute(
                select(StudySession.id).filter(StudySession.id == session_id)
            )
            if not session_res.scalar_one_or_none():
                raise HTTPException(
                    status_code=404, detail="Session not found"
                )
            logger.warning(
                f"Stats not found for existing session {session_id} during update attempt."
            )
            raise HTTPException(
                status_code=404, detail="Session stats not found"
            )

        # Update stats
        update_data = stats_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_stats, key, value)

        # Recalculate accuracy if relevant fields were updated
        if "total_correct" in update_data or "total_shown" in update_data:
            if db_stats.total_shown > 0:
                db_stats.accuracy = (
                    db_stats.total_correct / db_stats.total_shown
                )
            else:
                db_stats.accuracy = 0.0  # Avoid division by zero

        try:
            await db.commit()
            await db.refresh(db_stats)
            logger.info(
                f"Stats updated for session {session_id}. New accuracy: {db_stats.accuracy:.2f}"
            )
            return db_stats
        except Exception as e:
            await db.rollback()
            logger.error(
                f"Failed to update stats for session {session_id}: {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail="Failed to update session stats"
            )
