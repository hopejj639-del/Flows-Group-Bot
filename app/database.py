# Filename: app/database.py
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings

logger = logging.getLogger(__name__)

# System Architect Note: 
# Using Supabase Connection Pooler (Port 6543) in Transaction Mode.
# We MUST use NullPool to prevent SQLAlchemy from maintaining its own pool,
# and we MUST disable prepared statements to prevent asyncpg from crashing with PgBouncer.
engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,  # Delegates connection pooling entirely to Supabase
    connect_args={
        "ssl": "require",  # Enforce encrypted connection for cloud databases
        "server_settings": {
            "application_name": "flows_group_bot", # Helps in identifying connections on Supabase Dashboard
        },
        "prepared_statement_cache_size": 0,  # Required fix for Supabase transaction pooler
        "statement_cache_size": 0            # Required fix for Supabase transaction pooler
    }
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
            logger.info("Database tables initialized successfully via Supabase Pooler.")
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
