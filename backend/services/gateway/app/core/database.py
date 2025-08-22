"""
Database configuration and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from typing import AsyncGenerator

from .config import get_settings

# Create database metadata
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Import all models to ensure they're registered with SQLAlchemy
def _import_all_models():
    """Import all models to ensure they're registered with SQLAlchemy"""
    try:
        from ..models import (
            Project, SampleQueryCategory, SampleQuery, DemoSampleQuery,
            ChatSession, ChatMessage, AgentCommunication, FileAttachment,
            VoiceRecord, WebSocketConnection
        )
    except ImportError:
        # Models may not be available during initial setup
        pass

# Global engine variable
engine = None
async_session_local = None


async def init_db():
    """Initialize database connection"""
    global engine, async_session_local
    
    settings = get_settings()
    
    # Import all models to ensure they're registered with SQLAlchemy
    _import_all_models()
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=settings.DEBUG,
    )
    
    # Create session factory
    async_session_local = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def init_database():
    """Initialize database connection (alias for backward compatibility)"""
    await init_db()


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    global async_session_local
    
    if async_session_local is None:
        await init_db()
    
    if async_session_local is None:
        raise RuntimeError("Database not initialized")
    
    async with async_session_local() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database():
    """Close database connection"""
    global engine
    if engine:
        await engine.dispose()
        engine = None
