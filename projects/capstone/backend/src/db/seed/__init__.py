import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from .words import load_words
from .sentences import load_sentences
from .groups import load_groups

logger = logging.getLogger(__name__)


async def seed_all():
    """Run all seeding operations in correct order"""
    async with get_db() as db:
        try:
            start_time = datetime.now()
            logger.info("Starting database seeding...")

            # Pass db session to each seed function
            await load_words(db)
            await load_sentences(db)
            await load_groups(db)

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Seeding completed in {duration:.2f} seconds")
        except Exception as e:
            logger.error(f"Seeding failed: {str(e)}")
            raise


__all__ = ["load_words", "load_sentences", "load_groups", "seed_all"]
