import sqlite3
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def init_shared_database(db_path: str) -> None:
    """Initialize SQLite database with required tables."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                thumbnail_url TEXT,
                processed_date INTEGER,
                transcript TEXT,
                metadata TEXT,
                difficulty_level TEXT DEFAULT 'intermediate'
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT,
                question TEXT,
                audio_path TEXT,
                options TEXT,
                correct_answer INTEGER,
                difficulty_level TEXT,
                FOREIGN KEY (video_id) REFERENCES videos (video_id)
            )
        """
        )
        conn.commit()


def save_video_data(db_path: str, data: Dict[str, Any]) -> None:
    """Save or update video data in database."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO videos 
            (video_id, title, thumbnail_url, processed_date, transcript, metadata, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["video_id"],
                data["title"],
                data["thumbnail_url"],
                data["processed_date"],
                data["transcript"],
                data["metadata"],
                data.get("difficulty_level", "intermediate"),
            ),
        )
        conn.commit()


def get_video_data(db_path: str, video_id: str) -> Dict[str, Any]:
    """Retrieve video data from database."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM videos WHERE video_id = ?", (video_id,)
        ).fetchone()
        return dict(row) if row else None
