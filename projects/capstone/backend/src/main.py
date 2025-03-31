from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.sql import select

from .api.routes.words import router as words_router
from .api.routes.groups import router as groups_router
from .api.routes.study_sessions import router as sessions_router
from .api.routes.activity_logs import router as logs_router
from .api.routes.mistakes import router as mistakes_router
from .api.routes.dashboard import router as dashboard_router
from .api.routes.admin import router as admin_router
from .api.routes.study_activities import router as study_activities_router

from .database import init_db, async_session_factory, get_db
from .models.word import Word
from .db.seed import seed_all  # Import the seeding function
import os
import logging  # Import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization check complete.")

    # Check if seeding is needed
    async with async_session_factory() as db:
        try:
            result = await db.execute(
                select(Word).limit(1)
            )  # Check if at least one word exists
            first_word = result.scalar_one_or_none()

            if first_word is None:
                logger.info(
                    "Database appears empty. Starting seeding process..."
                )
                try:
                    await seed_all()  # Call the seeding function
                    logger.info("Database seeding completed successfully.")
                except Exception as seed_e:
                    logger.error(
                        f"Database seeding failed: {seed_e}", exc_info=True
                    )
                    # Decide if the app should fail to start if seeding fails
                    # raise seed_e
            else:
                logger.info(
                    "Database already contains data. Skipping seeding."
                )

        except Exception as e:
            logger.error(
                f"Error during startup database check/seeding: {e}",
                exc_info=True,
            )
            # Decide if the app should fail to start on other DB errors
            # raise e
