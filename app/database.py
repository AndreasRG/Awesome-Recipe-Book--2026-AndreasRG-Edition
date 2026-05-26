# -*- coding: utf-8 -*-
"""
Database configuration module using SQLAlchemy ORM with async support.
"""

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Resolve the database connection string from environment first.
# In deployment, a dedicated database VM is expected to provide this URL.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://recipe_user:admin123@27.0.0.6:5432/recipe_db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

# Base ORM class
Base = declarative_base()


async def get_db_session():
    """Provide a database session to FastAPI routes.

    This function is used as a dependency in FastAPI routes so that each
    request gets its own async session. The session is closed and rolled back
    automatically if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables ensured.")


async def close_db():
    """Close database connection on shutdown."""
    try:
        await engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
