from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import (
    words_router,
    groups_router,
    sessions_router,
    logs_router,
    mistakes_router,
    dashboard_router,
)
from .db.seed import seed_all  # Import the actual seeder you have
from .database import init_db, async_session_factory
from sqlalchemy.sql import select
from .models import Word
import os

app = FastAPI(title="HagXwon API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with proper prefixes
app.include_router(words_router, prefix="/api/words")
app.include_router(groups_router, prefix="/api/groups")
app.include_router(sessions_router, prefix="/api/sessions")
app.include_router(logs_router, prefix="/api/logs")
app.include_router(mistakes_router, prefix="/api/mistakes")
app.include_router(dashboard_router, prefix="/api/dashboard")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data if needed"""
    print("Initializing database...")
    await init_db()

    async with async_session_factory() as db:
        try:
            result = await db.execute(select(Word))
            words = result.scalars().all()
            print(f"Found {len(words)} words in database")

            if len(words) == 0:
                print("Seeding initial data...")
                await seed_all(db)  # Changed from seed_db() to seed_all(db)
                print("Data seeding complete")

            # Get updated count
            result = await db.execute(select(Word))
            words = result.scalars().all()
            print(f"Database now contains {len(words)} words")

        except Exception as e:
            print(f"Error during startup: {str(e)}")
            raise
