"""
SQLAlchemy database models for Workflow Engine service
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, JSON, Integer, ForeignKey, ARRAY, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

class WorkflowStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowDefinition(Base):
    """Workflow definition storage"""
    __tablename__ = "workflow_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    status = Column(SQLEnum(WorkflowStatus), nullable=False, default=WorkflowStatus.DRAFT)
    
    # Workflow definition
    steps = Column(JSON, nullable=False, default=list)  # List of workflow steps
    variables = Column(JSON, nullable=False, default=dict)  # Default variables
    timeout_seconds = Column(Integer, nullable=True, default=3600)
    
    # Project and categorization
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=list)
    
    # Configuration
    is_template = Column(Boolean, nullable=False, default=False)
    is_public = Column(Boolean, nullable=False, default=False)
    retry_config = Column(JSON, nullable=True)  # Global retry configuration
    notification_config = Column(JSON, nullable=True)  # Notification settings
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)

    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow")

class WorkflowExecution(Base):
    """Workflow execution history and state"""
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id"), nullable=False)
    execution_name = Column(String(255), nullable=True)  # Optional friendly name
    
    # Execution state
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING)
    current_step = Column(String(255), nullable=True)
    
    # Input/Output data
    input_data = Column(JSON, nullable=False, default=dict)
    output_data = Column(JSON, nullable=False, default=dict)
    variables = Column(JSON, nullable=False, default=dict)  # Runtime variables
    
    # Step tracking
    step_results = Column(JSON, nullable=False, default=dict)  # Results from each step
    step_statuses = Column(JSON, nullable=False, default=dict)  # Status of each step
    step_timings = Column(JSON, nullable=False, default=dict)  # Timing information
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    priority = Column(Integer, nullable=False, default=0)  # Execution priority
    timeout_seconds = Column(Integer, nullable=True)  # Override timeout
    
    # Project and user context
    tags = Column(ARRAY(String), nullable=True, default=list)
    executed_by = Column(String(255), nullable=True)
    execution_context = Column(JSON, nullable=True)  # Additional context data
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workflow = relationship("WorkflowDefinition", back_populates="executions")

class WorkflowTemplate(Base):
    """Workflow templates for common patterns"""
    __tablename__ = "workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    
    # Template definition
    template_definition = Column(JSON, nullable=False)  # Template structure
    parameters = Column(JSON, nullable=False, default=list)  # Template parameters
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True, default=list)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Usage tracking
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)

class WorkflowSchedule(Base):
    """Scheduled workflow executions"""
    __tablename__ = "workflow_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Schedule configuration
    cron_expression = Column(String(255), nullable=True)  # Cron schedule
    interval_seconds = Column(Integer, nullable=True)  # Simple interval
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Execution configuration
    is_active = Column(Boolean, nullable=False, default=True)
    max_concurrent_executions = Column(Integer, nullable=False, default=1)
    retry_failed = Column(Boolean, nullable=False, default=False)
    
    # Input data for scheduled executions
    default_input = Column(JSON, nullable=False, default=dict)
    default_variables = Column(JSON, nullable=False, default=dict)
    
    # Project context
    tags = Column(ARRAY(String), nullable=True, default=list)
    
    # Timing
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
