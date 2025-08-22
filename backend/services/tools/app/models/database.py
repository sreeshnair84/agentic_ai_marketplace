"""
SQLAlchemy database models for Tools service
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Integer, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import AsyncGenerator
import uuid
import os

Base = declarative_base()

# Global engine and session variables
engine = None
async_session_local = None

async def init_db():
    """Initialize database connection"""
    global engine, async_session_local
    
    # Database URL from environment - use the main platform database
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform")
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL logging
        pool_size=10,
        max_overflow=20
    )
    
    # Create session factory
    async_session_local = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    global async_session_local
    
    if async_session_local is None:
        await init_db()
    
    if async_session_local is not None:
        async with async_session_local() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        raise RuntimeError("Database not initialized")

class ToolTemplate(Base):
    """Tool template definitions"""
    __tablename__ = "tool_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False, default="1.0.0")
    is_active = Column(Boolean, nullable=False, default=True)
    icon = Column(String(255), nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=list)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)

    # Relationships
    fields = relationship("ToolTemplateField", back_populates="tool_template", cascade="all, delete-orphan")
    instances = relationship("ToolInstance", back_populates="template")

class ToolTemplateField(Base):
    """Tool template field definitions"""
    __tablename__ = "tool_template_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_template_id = Column(UUID(as_uuid=True), ForeignKey("tool_templates.id"), nullable=False)
    field_name = Column(String(255), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(String(50), nullable=False)
    field_description = Column(Text, nullable=True)
    is_required = Column(Boolean, nullable=False, default=False)
    is_secret = Column(Boolean, nullable=False, default=False)
    default_value = Column(Text, nullable=True)
    validation_rules = Column(JSON, nullable=True)
    field_options = Column(JSON, nullable=True)
    field_order = Column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tool_template = relationship("ToolTemplate", back_populates="fields")

class ToolInstance(Base):
    """Tool instance configurations"""
    __tablename__ = "tool_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_template_id = Column(UUID(as_uuid=True), ForeignKey("tool_templates.id"), nullable=False)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="inactive")
    configuration = Column(JSON, nullable=False, default=dict)
    environment_scope = Column(String(50), nullable=False, default="development")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Relationships
    template = relationship("ToolTemplate", back_populates="instances")


# Unified Model: LLM and Embedding
class Model(Base):
    """Unified model for LLM and Embedding configurations"""
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'llm' or 'embedding'
    endpoint_url = Column(String(500), nullable=True)
    api_key_env_var = Column(String(255), nullable=True)
    model_config = Column(JSON, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    supports_streaming = Column(Boolean, nullable=False, default=False)
    supports_functions = Column(Boolean, nullable=False, default=False)
    cost_per_token = Column(String(20), nullable=True)
    pricing_info = Column(JSON, nullable=True, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    # Embedding-specific fields
    dimensions = Column(Integer, nullable=True)
    max_input_tokens = Column(Integer, nullable=True)
    # Default model flag
    is_default = Column(Boolean, nullable=False, default=False)
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# EmbeddingModel removed; merged into LLMModel

class RAGPipeline(Base):
    """RAG pipeline configurations"""
    __tablename__ = "rag_pipelines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_instance_id = Column(UUID(as_uuid=True), ForeignKey("tool_instances.id"), nullable=False)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="inactive")
    data_sources = Column(JSON, nullable=False, default=list)
    vectorization_config = Column(JSON, nullable=False, default=dict)
    ingestion_config = Column(JSON, nullable=False, default=dict)
    retrieval_config = Column(JSON, nullable=False, default=dict)
    metadata_dict = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Relationships
    tool_instance = relationship("ToolInstance")
