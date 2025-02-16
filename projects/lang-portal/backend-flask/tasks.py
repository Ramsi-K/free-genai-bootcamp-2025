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