import sqlite3
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from ..database import engine

# from ..models.word_review_item import WordReviewItem


def reset_all():
    logging.basicConfig(filename="database.log", level=logging.ERROR)
    """Reset the entire database and reinitialize with initial data."""
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

        # Reinitialize the database with initial data
        import asyncio

        asyncio.run(init_db(drop_existing=False))
    except Exception as e:
        raise Exception(f"Database error: {e}")


def reset_session(session_id: int):
    logging.basicConfig(filename="database.log", level=logging.ERROR)
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


async def seed_db(conn: AsyncSession):
    logging.basicConfig(filename="database.log", level=logging.ERROR)
    """Seed the database with initial data."""
    try:
        from .seed import seed_all

        await seed_all()
        print("Database seeded successfully")
    except Exception as e:
        print(f"Error seeding database: {e}")


async def init_db(drop_existing: bool = False):
    logging.basicConfig(filename="database.log", level=logging.ERROR)
    try:
        async with engine.begin() as conn:
            if drop_existing:
                await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

            # Seed the database with initial data
            await seed_db(conn)
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        print(f"Error initializing database: {e}")
    """Initialize the database."""
    async with engine.begin() as conn:
        if drop_existing:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

        # Seed the database with initial data
        await seed_db(conn)
