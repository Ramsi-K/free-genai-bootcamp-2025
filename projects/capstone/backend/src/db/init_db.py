from sqlmodel import SQLModel, create_engine
from pathlib import Path
import sqlite3
import logging
import sys
from typing import Optional
from datetime import datetime
from ..config import SQLITE_DB_PATH
from ..database import engine


# Set up logging with both file and console handlers
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler("database.log")
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )

    # Console handler with simpler format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("%(message)s")  # Simpler format for CLI
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()

SCHEMA_SQL = """
-- Drop existing tables if they exist
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS sample_sentences;
DROP TABLE IF EXISTS word_groups;
DROP TABLE IF EXISTS word_group_map;
DROP TABLE IF EXISTS study_sessions;
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS session_stats;
DROP TABLE IF EXISTS word_stats;
DROP TABLE IF EXISTS wrong_inputs;
DROP TABLE IF EXISTS session_words_shown;

-- Create tables
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    korean TEXT NOT NULL,
    english TEXT NOT NULL,
    part_of_speech TEXT,
    romanization TEXT,
    topik_level INTEGER NULL,  -- Made explicitly nullable
    source_type TEXT,
    source_details TEXT,
    added_by_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (topik_level IS NULL OR (topik_level BETWEEN 1 AND 6))  -- Moved constraint to table level
);

CREATE TABLE IF NOT EXISTS sample_sentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    sentence_korean TEXT NOT NULL,
    sentence_english TEXT NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS word_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    source_type TEXT,
    source_details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_editable BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS word_group_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES word_groups(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    config_json TEXT
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    input_text TEXT,
    correct BOOLEAN NOT NULL,
    score INTEGER NOT NULL,
    image_path TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    total_shown INTEGER NOT NULL DEFAULT 0,
    total_correct INTEGER NOT NULL DEFAULT 0,
    accuracy REAL NOT NULL DEFAULT 0.0,
    level INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS word_stats (
    word_id INTEGER PRIMARY KEY,
    times_seen INTEGER NOT NULL DEFAULT 0,
    times_correct INTEGER NOT NULL DEFAULT 0,
    current_streak INTEGER NOT NULL DEFAULT 0,
    last_seen_at DATETIME,
    next_due_at DATETIME,
    ease_factor REAL NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS wrong_inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    input_text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session_words_shown (
    session_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES session_stats(id) ON DELETE CASCADE,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    PRIMARY KEY (session_id, word_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_word_group_map_word_id ON word_group_map(word_id);
CREATE INDEX IF NOT EXISTS idx_word_group_map_group_id ON word_group_map(group_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_session_id ON activity_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_word_id ON activity_logs(word_id);
CREATE INDEX IF NOT EXISTS idx_session_stats_session_id ON session_stats(session_id);
CREATE INDEX IF NOT EXISTS idx_wrong_inputs_word_id ON wrong_inputs(word_id);
CREATE INDEX IF NOT EXISTS idx_words_topik_level ON words(topik_level);
CREATE INDEX IF NOT EXISTS idx_words_created_at ON words(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_word_stats_next_due ON word_stats(next_due_at);
CREATE INDEX IF NOT EXISTS idx_word_stats_last_seen ON word_stats(last_seen_at);
CREATE INDEX IF NOT EXISTS idx_wrong_inputs_timestamp ON wrong_inputs(timestamp);
CREATE INDEX IF NOT EXISTS idx_study_sessions_started ON study_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_study_sessions_ended ON study_sessions(ended_at);
CREATE INDEX IF NOT EXISTS idx_word_groups_name ON word_groups(name);
CREATE INDEX IF NOT EXISTS idx_session_words_shown_session ON session_words_shown(session_id);
CREATE INDEX IF NOT EXISTS idx_session_words_shown_word ON session_words_shown(word_id);
"""


def print_operation_summary(operation: str, details: dict):
    """Print a formatted CLI summary of database operations"""
    print("\n" + "=" * 50)
    print(f"Operation: {operation}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    for key, value in details.items():
        print(f"{key}: {value}")
    print("=" * 50 + "\n")


async def init_db(drop_existing: bool = False):
    """Initialize database with all tables"""
    try:
        start_time = datetime.now()
        print("\nInitializing database...")
        logger.info(f"Initializing database at {SQLITE_DB_PATH}")

        # Ensure database directory exists
        db_dir = Path(SQLITE_DB_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # Create tables using SQLModel
        async with engine.begin() as conn:
            if drop_existing:
                await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)

        end_time = datetime.now()
        print_operation_summary(
            "Database Initialization",
            {
                "Status": "Success",
                "Location": SQLITE_DB_PATH,
                "Duration": f"{(end_time - start_time).total_seconds():.2f} seconds",
            },
        )

        logger.info("Database initialization completed successfully")

    except Exception as e:
        print_operation_summary(
            "Database Initialization",
            {"Status": "FAILED", "Error": str(e), "Location": SQLITE_DB_PATH},
        )
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise


def reset_all() -> None:
    """Reset entire database by dropping and recreating all tables"""
    try:
        start_time = datetime.now()
        print("\nResetting entire database...")
        logger.info("Starting complete database reset")
        init_db(drop_existing=True)
        end_time = datetime.now()
        print_operation_summary(
            "Database Reset",
            {
                "Status": "Success",
                "Duration": f"{(end_time - start_time).total_seconds():.2f} seconds",
            },
        )
        logger.info("Database reset completed successfully")
    except Exception as e:
        print_operation_summary(
            "Database Reset", {"Status": "FAILED", "Error": str(e)}
        )
        logger.error(f"Error during database reset: {e}", exc_info=True)
        raise


def reset_session(session_id: int) -> None:
    """Reset specific study session and all related data"""
    try:
        start_time = datetime.now()
        print(f"\nResetting session {session_id}...")
        logger.info(f"Starting reset of session {session_id}")
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()

        # Get session info before deletion
        cursor.execute(
            "SELECT started_at FROM study_sessions WHERE id = ?", (session_id,)
        )
        session_info = cursor.fetchone()
        if not session_info:
            raise ValueError(f"Session {session_id} not found")

        cursor.execute(
            "SELECT COUNT(*) FROM activity_logs WHERE session_id = ?",
            (session_id,),
        )
        activities_count = cursor.fetchone()[0]

        # Start transaction
        cursor.execute("BEGIN TRANSACTION")

        try:
            # Log affected records count before deletion
            logger.info(
                f"Removing {activities_count} activity logs for session {session_id}"
            )

            # Delete all related records in correct order (respecting foreign keys)
            cursor.execute(
                "DELETE FROM activity_logs WHERE session_id = ?", (session_id,)
            )
            cursor.execute(
                "DELETE FROM session_stats WHERE session_id = ?", (session_id,)
            )

            # Update word stats with safety check
            update_result = cursor.execute(
                """
                UPDATE word_stats 
                SET times_seen = CASE 
                        WHEN times_seen > 0 THEN times_seen - 1 
                        ELSE 0 
                    END,
                    times_correct = CASE 
                        WHEN times_correct > 0 THEN times_correct - 1 
                        ELSE 0 
                    END
                WHERE word_id IN (
                    SELECT DISTINCT word_id 
                    FROM activity_logs 
                    WHERE session_id = ?
                )
            """,
                (session_id,),
            )

            affected_stats = update_result.rowcount
            logger.info(f"Updated stats for {affected_stats} words")

            # Finally delete the session itself
            cursor.execute(
                "DELETE FROM study_sessions WHERE id = ?", (session_id,)
            )

            # Commit transaction
            conn.commit()
            end_time = datetime.now()
            print_operation_summary(
                "Session Reset",
                {
                    "Status": "Success",
                    "Session ID": session_id,
                    "Session Start": session_info[0],
                    "Activities Removed": activities_count,
                    "Stats Updated": affected_stats,
                    "Duration": f"{(end_time - start_time).total_seconds():.2f} seconds",
                },
            )
            logger.info(f"Successfully reset session {session_id}")

        except sqlite3.Error as e:
            cursor.execute("ROLLBACK")
            print_operation_summary(
                "Session Reset",
                {
                    "Status": "FAILED",
                    "Session ID": session_id,
                    "Error": str(e),
                },
            )
            logger.error(
                f"Database error during session reset: {e}", exc_info=True
            )
            raise e

        finally:
            conn.close()

    except Exception as e:
        print_operation_summary(
            "Session Reset",
            {"Status": "FAILED", "Session ID": session_id, "Error": str(e)},
        )
        logger.error(
            f"Error resetting session {session_id}: {e}", exc_info=True
        )
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Database management utilities"
    )
    parser.add_argument(
        "--reset-all", action="store_true", help="Reset entire database"
    )
    parser.add_argument(
        "--reset-session", type=int, help="Reset specific session ID"
    )
    parser.add_argument(
        "--init", action="store_true", help="Initialize database"
    )

    args = parser.parse_args()

    if args.reset_all:
        reset_all()
    elif args.reset_session is not None:
        reset_session(args.reset_session)
    elif args.init:
        init_db()
    else:
        parser.print_help()
