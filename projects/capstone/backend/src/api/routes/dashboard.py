from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from ...database import get_db
from contextlib import asynccontextmanager  # Added import
from ...models.study_session import StudySession
from ...models.word_review_item import WordReviewItem
from ...models.word import Word
from ...models.word_stats import WordStats
from ...models.activity_log import ActivityLog
from ...models.wrong_input import WrongInput

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/last_study_session")
async def get_last_study_session(db_cm: asynccontextmanager = Depends(get_db)):
    """Get the last study session"""
    async with db_cm as db:
        query = (
            select(StudySession)
            .order_by(StudySession.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        return session


@router.get("/study_progress")
async def get_study_progress(db_cm: asynccontextmanager = Depends(get_db)):
    """Get study progress"""
    async with db_cm as db:
        query = (
            select(
                func.count(Word.id).label("total_words"),
                func.count(WordStats.word_id).label("words_with_stats"),
                func.count(WordReviewItem.id).label("words_in_review"),
            )
            .outerjoin(WordStats, Word.id == WordStats.word_id)
            .outerjoin(WordReviewItem, Word.id == WordReviewItem.word_id)
            .group_by(Word.id, WordStats.word_id, WordReviewItem.id)
        )
        result = await db.execute(query)
        total_words_count, words_with_stats_count, words_in_review_count = (
            result.one()
        )

        return {
            "total_words": total_words_count,
            "words_with_stats": words_with_stats_count,
            "words_in_review": words_in_review_count,
        }


@router.get("/quick-stats")
async def get_quick_stats(db_cm: asynccontextmanager = Depends(get_db)):
    """Get quick stats"""
    async with db_cm as db:
        # Total words
        total_words_res = await db.execute(select(func.count(Word.id)))
        total_words_count = total_words_res.scalar()

        # Total sessions
        total_sessions_res = await db.execute(
            select(func.count(StudySession.id))
        )
        total_sessions_count = total_sessions_res.scalar()

        # Total mistakes
        total_mistakes_res = await db.execute(
            select(func.count(WrongInput.id))
        )
        total_mistakes_count = total_mistakes_res.scalar()

        return {
            "total_words": total_words_count,
            "total_sessions": total_sessions_count,
            "total_mistakes": total_mistakes_count,
        }


@router.get("/srs-overview")
async def get_srs_overview(db_cm: asynccontextmanager = Depends(get_db)):
    """Get SRS system overview"""
    async with db_cm as db:
        # Total words in review
        total_in_review_res = await db.execute(
            select(func.count(WordReviewItem.id))
        )
        total_in_review_count = total_in_review_res.scalar()

        # Words due today
        today = datetime.now(timezone.utc).date()
        words_due_today_res = await db.execute(
            select(func.count(WordReviewItem.id)).filter(
                WordReviewItem.due_date == today
            )
        )
        words_due_today_count = words_due_today_res.scalar()

        # Words due in the future
        words_due_future_res = await db.execute(
            select(func.count(WordReviewItem.id)).filter(
                WordReviewItem.due_date > today
            )
        )
        words_due_future_count = words_due_future_res.scalar()

        return {
            "total_in_review": total_in_review_count,
            "words_due_today": words_due_today_count,
            "words_due_future": words_due_future_count,
        }


@router.get("/recent-activity")
async def get_recent_activity(db_cm: asynccontextmanager = Depends(get_db)):
    """Get activity stats for recent days"""
    async with db_cm as db:
        today = datetime.now(timezone.utc).date()
        activity_counts = defaultdict(int)

        for i in range(7):
            current_date = today - timedelta(days=i)
            start_of_day = datetime(
                current_date.year, current_date.month, current_date.day
            ).replace(tzinfo=timezone.utc)
            end_of_day = start_of_day + timedelta(days=1)

            activity_count_res = await db.execute(
                select(func.count(ActivityLog.id))  # Count specific column
                .filter(ActivityLog.timestamp >= start_of_day)
                .filter(ActivityLog.timestamp < end_of_day)
            )
            activity_counts[current_date.isoformat()] = (
                activity_count_res.scalar()
            )

        return activity_counts


@router.get("/srs-forecast")
async def get_srs_forecast(db_cm: asynccontextmanager = Depends(get_db)):
    """Get upcoming SRS reviews forecast"""
    async with db_cm as db:
        today = datetime.now(timezone.utc).date()
        forecast = defaultdict(int)

        for i in range(14):
            future_date = today + timedelta(days=i)
            due_count_res = await db.execute(
                select(
                    func.count(WordReviewItem.id)
                ).filter(  # Count specific column
                    WordReviewItem.due_date == future_date
                )
            )
            forecast[future_date.isoformat()] = due_count_res.scalar()

        return forecast


@router.get("/charts/learning-progress")
async def get_learning_progress(db_cm: asynccontextmanager = Depends(get_db)):
    """Get daily progress data for line chart"""
    async with db_cm as db:
        today = datetime.now(timezone.utc).date()
        progress_data = defaultdict(int)

        for i in range(7):
            current_date = today - timedelta(days=i)
            start_of_day = datetime(
                current_date.year, current_date.month, current_date.day
            ).replace(tzinfo=timezone.utc)
            end_of_day = start_of_day + timedelta(days=1)

            new_words_count_res = await db.execute(
                select(func.count(Word.id))  # Count specific column
                .filter(Word.created_at >= start_of_day)
                .filter(Word.created_at < end_of_day)
            )
            progress_data[current_date.isoformat()] = (
                new_words_count_res.scalar()
            )

        return progress_data


@router.get("/charts/activity-distribution")
async def get_activity_distribution(
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Get activity type distribution for pie chart"""
    async with db_cm as db:
        activity_counts_res = await db.execute(
            select(
                ActivityLog.activity_type, func.count(ActivityLog.id)
            )  # Count specific column
            .group_by(ActivityLog.activity_type)
            .order_by(func.count(ActivityLog.id).desc())
        )
        return {
            activity_type: count
            for activity_type, count in activity_counts_res.fetchall()
        }


@router.get("/charts/topik-progress")
async def get_topik_progress(db_cm: asynccontextmanager = Depends(get_db)):
    """Get TOPIK level progress for radar chart"""
    async with db_cm as db:
        topik_levels = [1, 2, 3, 4, 5, 6]
        topik_counts = {}

        for level in topik_levels:
            count_res = await db.execute(
                select(func.count(Word.id)).filter(  # Count specific column
                    Word.topik_level == level
                )
            )
            topik_counts[f"TOPIK {level}"] = count_res.scalar()

        return topik_counts


@router.get("/charts/study-time")
async def get_study_time_stats(db_cm: asynccontextmanager = Depends(get_db)):
    """Get study time distribution for bar chart"""
    async with db_cm as db:
        today = datetime.now(timezone.utc).date()
        study_time_data = defaultdict(int)

        for i in range(7):
            current_date = today - timedelta(days=i)
            start_of_day = datetime(
                current_date.year, current_date.month, current_date.day
            ).replace(tzinfo=timezone.utc)
            end_of_day = start_of_day + timedelta(days=1)

            # This counts sessions started, not duration. If duration is needed,
            # it requires summing session durations (ended_at - created_at).
            # Assuming count of sessions started per day is intended for now.
            study_sessions_count_res = await db.execute(
                select(func.count(StudySession.id))  # Count specific column
                .filter(StudySession.created_at >= start_of_day)
                .filter(StudySession.created_at < end_of_day)
            )
            study_time_data[current_date.isoformat()] = (
                study_sessions_count_res.scalar()
            )

        return study_time_data
