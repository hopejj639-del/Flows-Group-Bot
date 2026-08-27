# Filename: app/database.py
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# Create the Async Engine using asyncpg.
# pool_pre_ping ensures connections aren't dropped silently by Supabase.
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# AsyncSession factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def init_db():
    """
    Initializes database tables. In a real production environment, 
    Alembic migrations should be used instead of sync_create_all.
    """
    try:
        async with engine.begin() as conn:
            # Create all tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        raise

async def get_db_session() -> AsyncSession: # type: ignore
    """
    Dependency/Helper to get a database session.
    Ensures safe resource teardown.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()