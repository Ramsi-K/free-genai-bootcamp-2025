import sqlite3
import os

def run_migrations():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'word_bank.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get list of migration files
        migrations_dir = os.path.join(os.path.dirname(__file__), 'sql', 'migrations')
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        # Run each migration
        for migration_file in migration_files:
            print(f"Running migration: {migration_file}")
            with open(os.path.join(migrations_dir, migration_file)) as f:
                migration_sql = f.read()
                conn.executescript(migration_sql)
                conn.commit()
        
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Error running migrations: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations()
