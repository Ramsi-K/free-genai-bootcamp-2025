import sqlite3
from pathlib import Path

# Get correct paths
current_dir = Path(__file__).resolve().parent
backend_src = current_dir.parent
project_root = backend_src.parent.parent
db_path = project_root / "database" / "education.db"


def inspect_database():
    try:
        print(f"Attempting to connect to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("\n=== Database Schema ===\n")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))
            cursor.execute(f"PRAGMA table_info({table_name})")
            for col in cursor.fetchall():
                print(f"  {col[1]}: {col[2]}")

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    inspect_database()
