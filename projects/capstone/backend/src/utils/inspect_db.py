import sqlite3
from pathlib import Path


# Get correct paths - point to hagxwon.db
current_dir = Path(__file__).resolve().parent
backend_src = current_dir.parent
project_root = backend_src.parent.parent
db_path = project_root / "data" / "hagxwon.db"


def inspect_database():
    try:
        print(f"Attempting to connect to database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables including indexes and foreign keys
        print("\n=== Database Schema ===\n")

        # List all tables
        cursor.execute(
            """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        )
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))

            # Get columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                pk = "PRIMARY KEY" if col[5] == 1 else ""
                print(f"  {col_name}: {col_type} {nullable} {pk}".strip())

            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fks = cursor.fetchall()
            if fks:
                print("\n  Foreign Keys:")
                for fk in fks:
                    print(f"    {fk[3]} -> {fk[2]}.{fk[4]}")

            # Get indexes
            cursor.execute(
                f"""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='{table_name}'
            """
            )
            indexes = cursor.fetchall()
            if indexes:
                print("\n  Indexes:")
                for idx in indexes:
                    print(f"    {idx[0]}")

        # Print record counts
        print("\n=== Table Record Counts ===\n")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} records")

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    inspect_database()
