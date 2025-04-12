import asyncio
from src.db.seed.groups import load_groups
from src.database import async_session_factory


async def run():
    async with async_session_factory() as db:
        await load_groups(db)


if __name__ == "__main__":
    asyncio.run(run())
