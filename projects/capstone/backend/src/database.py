import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Ensure instance directory exists
os.makedirs("instance", exist_ok=True)

DATABASE_URL = "sqlite+aiosqlite:///./instance/words.db"
print(
    f"Using database at: {os.path.abspath('./instance/words.db')}"
)  # Debug log

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()


async def init_db():
    print("Initializing database...")  # Debug log
    import src.models  # Import models here to ensure all are registered

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")  # Debug log
    except Exception as e:
        print(f"Error initializing database: {e}")  # Debug log
        raise


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
