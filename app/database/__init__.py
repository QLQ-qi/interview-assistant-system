"""Database module - supports both PostgreSQL and SQLite"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Auto-detect database backend
_db_url = settings.DATABASE_URL
if "postgresql" in _db_url:
    if _db_url.startswith("postgresql://"):
        _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(
        _db_url,
        echo=settings.DEBUG,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )
    logger.info("Using PostgreSQL database")
else:
    if _db_url.startswith("sqlite://"):
        _db_url = _db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    engine = create_async_engine(
        _db_url,
        echo=settings.DEBUG,
    )
    logger.info("Using SQLite database")

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
