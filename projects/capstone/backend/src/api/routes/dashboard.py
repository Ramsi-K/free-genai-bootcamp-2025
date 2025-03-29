from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from ...database import get_db
from ...models.study_session import StudySession
from ...models.word_review_item import WordReviewItem
from ...models.word import Word
from ...models.word_stats import WordStats
from ...models.activity_log import ActivityLog
from ...models.wrong_input import WrongInput
from ...models.group import WordGroup  # Changed from Group to WordGroup

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


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
        .filter(WordReviewItem.correct.is_(True))
        .label("correct"),
        func.count(WordReviewItem.id)
        .filter(WordReviewItem.correct.is_(False))
        .label("incorrect"),
    )
    result = await db.execute(query)
    stats = result.one()
    return {"correct": stats.correct, "incorrect": stats.incorrect}


@router.get("/quick-stats")
async def get_quick_stats(db: AsyncSession = Depends(get_db)):
    words_query = select(func.count().label("total_words")).select_from(Word)
    groups_query = select(func.count().label("total_groups")).select_from(
        WordGroup  # Changed from Group to WordGroup
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


@router.get("/srs-overview")
async def get_srs_overview(db: AsyncSession = Depends(get_db)):
    """Get SRS system overview"""
    now = datetime.now(timezone.utc)

    # Get words due for review
    due_words = await db.execute(
        select(func.count(WordStats.word_id)).filter(
            WordStats.next_due_at <= now
        )
    )

    # Get mastered words (streak > 5)
    mastered = await db.execute(
        select(func.count(WordStats.word_id)).filter(
            WordStats.current_streak >= 5
        )
    )

    # Get problem words (ease_factor near minimum)
    struggling = await db.execute(
        select(func.count(WordStats.word_id)).filter(
            WordStats.ease_factor <= 1.5
        )
    )

    return {
        "total_active": await db.execute(
            select(func.count(WordStats.word_id))
        ),
        "due_today": due_words.scalar(),
        "mastered_words": mastered.scalar(),
        "struggling_words": struggling.scalar(),
    }


@router.get("/recent-activity")
async def get_recent_activity(
    days: int = 7, db: AsyncSession = Depends(get_db)
):
    """Get activity stats for recent days"""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Get activity counts by type
    activities = await db.execute(
        select(
            ActivityLog.activity_type,
            func.count(ActivityLog.id).label("count"),
            func.avg(ActivityLog.correct).label("accuracy"),
        )
        .filter(ActivityLog.timestamp >= since)
        .group_by(ActivityLog.activity_type)
    )

    # Get recent mistakes
    mistakes = await db.execute(
        select(WrongInput)
        .filter(WrongInput.timestamp >= since)
        .order_by(WrongInput.timestamp.desc())
        .limit(10)
    )

    return {
        "activity_summary": [
            {
                "type": activity.activity_type,
                "count": activity.count,
                "accuracy": float(activity.accuracy),
            }
            for activity in activities.all()
        ],
        "recent_mistakes": [
            {
                "word_id": mistake.word_id,
                "input": mistake.input_text,
                "timestamp": mistake.timestamp,
            }
            for mistake in mistakes.scalars()
        ],
    }


@router.get("/srs-forecast")
async def get_srs_forecast(days: int = 7, db: AsyncSession = Depends(get_db)):
    """Get upcoming SRS reviews forecast"""
    now = datetime.now(timezone.utc)
    forecast = []

    for day in range(days):
        target_date = now + timedelta(days=day)
        due = await db.execute(
            select(func.count(WordStats.word_id)).filter(
                WordStats.next_due_at >= target_date,
                WordStats.next_due_at < target_date + timedelta(days=1),
            )
        )
        forecast.append(
            {"date": target_date.date(), "due_reviews": due.scalar()}
        )

    return forecast


@router.get("/charts/learning-progress")
async def get_learning_progress(db: AsyncSession = Depends(get_db)):
    """Get daily progress data for line chart"""
    since = datetime.now(timezone.utc) - timedelta(days=30)

    # Get daily stats
    stats = await db.execute(
        select(
            func.date(ActivityLog.timestamp),
            func.count(ActivityLog.id),
            func.sum(case((ActivityLog.correct.is_(True), 1), else_=0)),
        )
        .filter(ActivityLog.timestamp >= since)
        .group_by(func.date(ActivityLog.timestamp))
    )

    return {
        "chart_type": "line",
        "labels": [row[0].strftime("%Y-%m-%d") for row in stats],
        "datasets": [
            {"label": "Total Attempts", "data": [row[1] for row in stats]},
            {"label": "Correct Answers", "data": [row[2] for row in stats]},
        ],
    }


@router.get("/charts/activity-distribution")
async def get_activity_distribution(db: AsyncSession = Depends(get_db)):
    """Get activity type distribution for pie chart"""
    activities = await db.execute(
        select(
            ActivityLog.activity_type,
            func.count(ActivityLog.id).label("count"),
        ).group_by(ActivityLog.activity_type)
    )

    return {
        "chart_type": "pie",
        "labels": [act.activity_type for act in activities],
        "data": [act.count for act in activities],
    }


@router.get("/charts/topik-progress")
async def get_topik_progress(db: AsyncSession = Depends(get_db)):
    """Get TOPIK level progress for radar chart"""
    # Get accuracy by TOPIK level
    stats = await db.execute(
        select(
            Word.topik_level,
            func.avg(case((ActivityLog.correct.is_(True), 1), else_=0)),
        )
        .join(ActivityLog.word)
        .group_by(Word.topik_level)
    )

    return {
        "chart_type": "radar",
        "labels": [
            "TOPIK 1",
            "TOPIK 2",
            "TOPIK 3",
            "TOPIK 4",
            "TOPIK 5",
            "TOPIK 6",
        ],
        "data": [float(row[1] or 0) for row in stats],
    }


@router.get("/charts/study-time")
async def get_study_time_stats(db: AsyncSession = Depends(get_db)):
    """Get study time distribution for bar chart"""
    sessions = await db.execute(
        select(
            func.strftime("%H", StudySession.started_at),
            func.count(StudySession.id),
        ).group_by(func.strftime("%H", StudySession.started_at))
    )

    return {
        "chart_type": "bar",
        "labels": [f"{hour}:00" for hour in range(24)],
        "data": defaultdict(int, {row[0]: row[1] for row in sessions}),
    }
