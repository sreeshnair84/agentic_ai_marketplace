"""
Database models for tool management system
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class ToolTemplate(Base):
    __tablename__ = "tool_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(100), nullable=False)  # 'rag', 'sql_agent', 'mcp', etc.
    description = Column(Text)
    schema_definition = Column(JSONB, nullable=False)
    default_config = Column(JSONB, default={})
    version = Column(String(50), default="1.0.0")
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), default=[])
    documentation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    instances = relationship("ToolInstance", back_populates="template", cascade="all, delete-orphan")
    agent_associations = relationship("ToolTemplateAgentTemplateAssociation", back_populates="tool_template")

class ToolInstance(Base):
    __tablename__ = "tool_instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("tool_templates.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    configuration = Column(JSONB, default={})
    credentials = Column(JSONB, default={})  # Encrypted credentials
    environment = Column(String(50), default="development")
    status = Column(String(50), default="inactive")
    resource_limits = Column(JSONB, default={})
    health_check_config = Column(JSONB, default={})
    last_health_check = Column(DateTime(timezone=True))
    health_status = Column(String(50), default="unknown")
    metrics = Column(JSONB, default={})
    llm_model_id = Column(String(36), ForeignKey("llm_models.id"), nullable=True)
    embedding_model_id = Column(String(36), ForeignKey("embedding_models.id"), nullable=True)
    error_log = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    template = relationship("ToolTemplate", back_populates="instances")
    executions = relationship("ToolInstanceExecution", back_populates="tool_instance")

class RAGPipeline(Base):
    __tablename__ = "rag_pipelines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    data_sources = Column(JSONB, default=[])
    processing_config = Column(JSONB, default={})
    chunking_strategy = Column(JSONB, default={})
    vectorization_config = Column(JSONB, default={})
    storage_config = Column(JSONB, default={})
    retrieval_config = Column(JSONB, default={})
    quality_config = Column(JSONB, default={})
    schedule_config = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    runs = relationship("RAGPipelineRun", back_populates="pipeline")

class RAGPipelineRun(Base):
    __tablename__ = "rag_pipeline_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("rag_pipelines.id"), nullable=False)
    run_type = Column(String(50), default="manual")
    status = Column(String(50), default="pending")
    progress = Column(JSONB, default={})
    metrics = Column(JSONB, default={})
    logs = Column(Text)
    error_details = Column(Text)
    input_data = Column(JSONB, default={})
    output_summary = Column(JSONB, default={})
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pipeline = relationship("RAGPipeline", back_populates="runs")

class AgentTemplate(Base):
    __tablename__ = "agent_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    framework = Column(String(100), default="langgraph")
    workflow_config = Column(JSONB, default={})
    persona_config = Column(JSONB, default={})
    capabilities = Column(ARRAY(String), default=[])
    constraints = Column(JSONB, default={})
    tool_template_requirements = Column(JSONB, default=[])
    optional_tool_templates = Column(JSONB, default=[])
    default_tool_bindings = Column(JSONB, default={})
    version = Column(String(50), default="1.0.0")
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), default=[])
    documentation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    instances = relationship("AgentInstance", back_populates="template")
    tool_associations = relationship("ToolTemplateAgentTemplateAssociation", back_populates="agent_template")

class AgentInstance(Base):
    __tablename__ = "agent_instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("agent_templates.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tool_instance_bindings = Column(JSONB, default={})
    runtime_config = Column(JSONB, default={})
    state_config = Column(JSONB, default={})
    conversation_history = Column(JSONB, default=[])
    performance_metrics = Column(JSONB, default={})
    security_config = Column(JSONB, default={})
    status = Column(String(50), default="inactive")
    environment = Column(String(50), default="development")
    last_activity = Column(DateTime(timezone=True))
    error_log = Column(Text)
    deployment_config = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    template = relationship("AgentTemplate", back_populates="instances")
    executions = relationship("ToolInstanceExecution", back_populates="agent_instance")
    conversations = relationship("AgentInstanceConversation", back_populates="agent_instance")

class ToolTemplateAgentTemplateAssociation(Base):
    __tablename__ = "tool_template_agent_template_associations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_template_id = Column(UUID(as_uuid=True), ForeignKey("tool_templates.id"), nullable=False)
    agent_template_id = Column(UUID(as_uuid=True), ForeignKey("agent_templates.id"), nullable=False)
    role_name = Column(String(255), nullable=False)
    configuration = Column(JSONB, default={})
    is_required = Column(Boolean, default=True)
    execution_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tool_template = relationship("ToolTemplate", back_populates="agent_associations")
    agent_template = relationship("AgentTemplate", back_populates="tool_associations")

class ToolInstanceExecution(Base):
    __tablename__ = "tool_instance_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_instance_id = Column(UUID(as_uuid=True), ForeignKey("tool_instances.id"), nullable=False)
    agent_instance_id = Column(UUID(as_uuid=True), ForeignKey("agent_instances.id"))
    execution_type = Column(String(100), nullable=False)
    input_data = Column(JSONB, default={})
    output_data = Column(JSONB, default={})
    status = Column(String(50), default="pending")
    error_details = Column(Text)
    execution_time_ms = Column(Integer)
    resource_usage = Column(JSONB, default={})
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    tool_instance = relationship("ToolInstance", back_populates="executions")
    agent_instance = relationship("AgentInstance", back_populates="executions")

class AgentInstanceConversation(Base):
    __tablename__ = "agent_instance_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_instance_id = Column(UUID(as_uuid=True), ForeignKey("agent_instances.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id = Column(String(255), nullable=False)
    conversation_data = Column(JSONB, default={})
    metadata_dict = Column(JSONB, default={})
    tools_used = Column(JSONB, default=[])
    performance_metrics = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    agent_instance = relationship("AgentInstance", back_populates="conversations")

# For compatibility with existing User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Add other user fields as needed
