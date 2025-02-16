from invoke import task
from app import create_app
from models import db, Word, Group, StudyActivity
import os

@task
def init_db(ctx):
    """Initialize the database with tables and seed data"""
    try:
        # Create instance directory if it doesn't exist
        os.makedirs('instance', exist_ok=True)
        
        app = create_app()
        with app.app_context():
            # Create all tables from SQLAlchemy models
            db.create_all()
            
            # TODO: Add seed data loading here
            # This will be implemented in a separate task
            
            print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

@task
def seed_db(ctx):
    """Load seed data into the database"""
    try:
        app = create_app()
        with app.app_context():
            # Load data from JSON files
            from lib.db import load_seed_data
            load_seed_data(db, Word, Group, StudyActivity)
            print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        raise

@task
def verify_db(ctx):
    """Verify database contents"""
    try:
        app = create_app()
        with app.app_context():
            word_count = Word.query.count()
            group_count = Group.query.count()
            print(f"Database contains {word_count} words and {group_count} groups")
            
            if word_count == 0:
                print("No words found. Try running 'invoke seed-db'")
            else:
                first_word = Word.query.first()
                print("\nSample word:")
                print(f"Hangul: {first_word.hangul}")
                print(f"English: {first_word.english}")
                print(f"Type: {first_word.type}")
    except Exception as e:
        print(f"Error verifying database: {e}")
        raise