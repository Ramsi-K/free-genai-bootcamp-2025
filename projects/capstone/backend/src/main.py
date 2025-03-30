from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.words import router as words_router
from .api.routes.groups import router as groups_router
from .api.routes.study_sessions import router as sessions_router
from .api.routes.activity_logs import router as logs_router
from .api.routes.mistakes import router as mistakes_router
from .api.routes.dashboard import router as dashboard_router
from .api.routes.admin import router as admin_router
from .api.routes.study_activities import router as study_activities_router

from .db.seed import seed_all  # Import the actual seeder you have
from .database import init_db, async_session_factory
from sqlalchemy.sql import select
from .models.word import Word
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
app.include_router(words_router, prefix="/api")
app.include_router(groups_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(mistakes_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(study_activities_router, prefix="/api")


@app.get("/debug/routes")
async def list_routes():
    return [
        {
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods),
        }
        for route in app.routes
    ]


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data if needed"""
    print("Initializing database...")
    await init_db()

    # Use the session factory directly for seeding
    async with async_session_factory() as db:
        try:
            result = await db.execute(select(Word))
            words = result.scalars().all()
            print(f"Found {len(words)} words in database")

            if len(words) == 0:
                print("Seeding initial data...")
                # Pass the db session directly instead of trying to get a new one
                await seed_all(db)
                await db.commit()
                print("Data seeding complete")

            # Get updated count
            result = await db.execute(select(Word))
            words = result.scalars().all()
            print(f"Database now contains {len(words)} words")

        except Exception as e:
            print(f"Error during startup: {str(e)}")
            raise
