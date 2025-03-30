import sqlite3
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel

from ..database import engine, async_session_factory
from ..models.word import Word
from ..models.word_stats import WordStats
from ..models.wrong_input import WrongInput
from ..models.group import WordGroup
from ..models.study_session import StudySession
from ..models.session_stats import SessionStats
from ..models.activity_log import ActivityLog
from ..models.sample_sentence import SampleSentence
from ..models.associations import word_group_map
from ..models.activity_type import ActivityType

# from ..models.word_review_item import WordReviewItem


def reset_all():
    """Reset the entire database."""
    try:
        conn = sqlite3.connect(str(Path(engine.url.database)))
        cursor = conn.cursor()

        # Get all tables
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        )
        tables = cursor.fetchall()

        # Delete data from each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")

        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception(f"Database error: {e}")


def reset_session(session_id: int):
    """Reset a specific study session."""
    try:
        conn = sqlite3.connect(str(Path(engine.url.database)))
        cursor = conn.cursor()

        # Check if session exists
        cursor.execute(
            "SELECT id FROM study_sessions WHERE id = ?", (session_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Session {session_id} not found")

        # Delete related data
        cursor.execute(
            "DELETE FROM activity_logs WHERE session_id = ?", (session_id,)
        )
        cursor.execute(
            "DELETE FROM session_stats WHERE session_id = ?", (session_id,)
        )
        cursor.execute(
            "DELETE FROM study_sessions WHERE id = ?", (session_id,)
        )

        conn.commit()
        conn.close()
    except Exception as e:
        raise Exception(f"Database error: {e}")


async def init_db(drop_existing: bool = False):
    """Initialize the database."""
    async with engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
