"""
SQLAlchemy database models for Tools service
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Integer, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

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

class LLMModel(Base):
    """LLM model configurations"""
    __tablename__ = "llm_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)
    endpoint_url = Column(String(500), nullable=True)
    api_key_env_var = Column(String(255), nullable=True)
    model_config = Column(JSON, nullable=True)  # This matches the actual database column
    max_tokens = Column(Integer, nullable=True)
    supports_streaming = Column(Boolean, nullable=False, default=False)
    supports_functions = Column(Boolean, nullable=False, default=False)
    cost_per_token = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EmbeddingModel(Base):
    """Embedding model configurations"""
    __tablename__ = "embedding_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    endpoint_url = Column(String(500), nullable=True)
    api_key_env_var = Column(String(255), nullable=True)
    model_config = Column(JSON, nullable=True)  # This matches the actual database column
    dimensions = Column(Integer, nullable=True)
    max_input_tokens = Column(Integer, nullable=True)
    cost_per_token = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
