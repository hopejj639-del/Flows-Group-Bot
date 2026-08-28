# Filename: app/database.py
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# System Architect Note: 
# Switched from asyncpg to psycopg to fully support Supabase Transaction Pooler (Port 6543).
# Psycopg seamlessly handles PgBouncer/Transaction mode without prepared statement errors.
engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args={
        "sslmode": "require",  
        "application_name": "flows_group_bot",
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully via Supabase Pooler (psycopg).")
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        raise

async def get_db_session() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
