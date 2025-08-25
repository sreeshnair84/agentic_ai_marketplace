"""
Database configuration and models for the Agents service
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Text, JSON, Boolean, Integer, ForeignKey, Enum
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncGenerator
import uuid
import enum

from .config import get_settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class AgentType(enum.Enum):
    """Agent type enumeration"""
    CONVERSATIONAL = "conversational"
    TASK_ORIENTED = "task_oriented"
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    COLLABORATIVE = "collaborative"


class AgentStatus(enum.Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AIProvider(enum.Enum):
    """AI provider enumeration"""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    agent_type: Mapped[AgentType] = mapped_column(Enum(AgentType), nullable=False)
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), default=AgentStatus.INACTIVE)
    
    # AI Model configuration
    ai_provider: Mapped[AIProvider] = mapped_column(Enum(AIProvider), default=AIProvider.GEMINI)
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-1.5-pro")
    model_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    llm_model_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("llm_models.id"), nullable=True)
    
    # Agent configuration
    capabilities: Mapped[List[str]] = mapped_column(JSON, default=list)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    temperature: Mapped[float] = mapped_column(Integer, default=0.7)
    
    # Metadata
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # A2A Protocol settings
    a2a_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    a2a_address: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships
    executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="agent")


class AgentExecution(Base):
    """Agent execution model"""
    __tablename__ = "agent_executions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"), nullable=False)
    task_id: Mapped[Optional[str]] = mapped_column(String(255))  # From orchestrator
    
    # Execution data
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Status and timing
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Token usage tracking
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    total_cost: Mapped[Optional[float]] = mapped_column(Integer)  # In USD
    
    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="executions")


class AgentCapability(Base):
    """Agent capability model"""
    __tablename__ = "agent_capabilities"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    parameters_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class A2AMessage(Base):
    """A2A (Agent-to-Agent) message model"""
    __tablename__ = "a2a_messages"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_agent_id: Mapped[str] = mapped_column(String, nullable=False)
    to_agent_id: Mapped[str] = mapped_column(String, nullable=False)
    
    # Message content
    message_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Status and timing
    status: Mapped[str] = mapped_column(String(50), default="pending")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Error handling
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


class AgentSession(Base):
    """Agent session for stateful conversations"""
    __tablename__ = "agent_sessions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Session data
    conversation_history: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    session_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Session management
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


# Database setup
engine = None
SessionLocal = None


async def init_db():
    """Initialize database connection and create tables"""
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
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
