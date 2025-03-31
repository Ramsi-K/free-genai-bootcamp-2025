from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from .config import SQLITE_DB_PATH
import logging

logger = logging.getLogger(__name__)

# Ensure data directory exists
data_dir = Path(SQLITE_DB_PATH).parent
data_dir.mkdir(parents=True, exist_ok=True)

# Create async engine
engine = create_async_engine(
    f"sqlite+aiosqlite:///{SQLITE_DB_PATH}", echo=True, future=True
)

# Create async session factory
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# # Corrected dependency for routes
# async def get_db() -> AsyncSession:
#     async with async_session_factory() as session:
#         yield session


@asynccontextmanager
async def get_db():
    try:
        logger.info("Creating database session...")
        async with async_session_factory() as session:
            yield session
            logger.info("Database session closed.")
    except Exception as e:
        logger.exception(f"Error with database session: {e}")
        raise


# Database initialization
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
