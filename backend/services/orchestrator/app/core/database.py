"""
Database configuration and models for the Orchestrator service
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, JSON, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional, Dict, Any, AsyncGenerator
import uuid

from .config import get_settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class Workflow(Base):
    """Workflow model - uses existing table from migration"""
    __tablename__ = "workflow_definitions"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    steps: Mapped[list] = mapped_column(JSON, default=list)
    variables: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer, default=3600)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    project_tags: Mapped[Optional[list]] = mapped_column(JSON)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    retry_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    notification_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[Optional[str]] = mapped_column(String(255))
    updated_by: Mapped[Optional[str]] = mapped_column(String(255))


class WorkflowExecution(Base):
    """Workflow execution model - uses existing table from migration"""
    __tablename__ = "workflow_executions"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("workflow_definitions.id"), nullable=False)
    execution_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    current_step: Mapped[Optional[str]] = mapped_column(String(255))
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    output_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    variables: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    step_results: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    step_statuses: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    step_timings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    project_tags: Mapped[Optional[list]] = mapped_column(JSON)
    executed_by: Mapped[Optional[str]] = mapped_column(String(255))
    execution_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("workflow_executions.id"), nullable=False)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_id: Mapped[Optional[str]] = mapped_column(String(255))
    tool_name: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AgentSession(Base):
    """Agent session model for A2A protocol"""
    __tablename__ = "agent_sessions"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    session_data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


# Database setup
engine = None
SessionLocal = None


async def init_db():
    """Initialize database connection - create tables if they don't exist"""
    global engine, SessionLocal
    
    settings = get_settings()
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True
    )
    
    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create tables only if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
