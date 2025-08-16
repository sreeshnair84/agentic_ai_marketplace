"""
Pydantic models for Workflow Engine service
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

# New models for enhanced workflow registry
class InputOutputSignature(BaseModel):
    """Input/Output signature definition for workflows"""
    schema: Dict[str, Any] = Field(description="JSON schema for input/output")


class TriggerConfig(BaseModel):
    """Trigger configuration for workflows"""
    type: str = Field(description="Trigger type (webhook|schedule|event|manual)")
    config: Dict[str, Any] = Field(description="Trigger-specific configuration")


class WorkflowDependencies(BaseModel):
    """Dependencies for workflow execution"""
    agents: List[str] = Field(default_factory=list, description="Required agent IDs")
    tools: List[str] = Field(default_factory=list, description="Required tool IDs")
    external_services: List[str] = Field(default_factory=list, description="Required external services")


class StepMapping(BaseModel):
    """Input/Output mapping for workflow steps"""
    input_mapping: Optional[Dict[str, str]] = Field(default=None, description="Input data mapping")
    output_mapping: Optional[Dict[str, str]] = Field(default=None, description="Output data mapping")


class ErrorHandling(BaseModel):
    """Error handling configuration for steps"""
    retry_count: int = Field(default=0, description="Number of retry attempts")
    retry_delay: int = Field(default=5, description="Delay between retries in seconds")
    on_failure: str = Field(default="fail", description="Action on failure (skip|fail|retry)")

# Enums
class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepType(str, Enum):
    AGENT_CALL = "agent_call"
    TOOL_CALL = "tool_call"
    HTTP_REQUEST = "http_request"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    DELAY = "delay"
    SCRIPT = "script"

# Step Models
class WorkflowStep(BaseModel):
    id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Human-readable step name")
    type: StepType = Field(..., description="Type of step to execute")
    
    # Enhanced step configuration
    agent_id: Optional[str] = Field(default=None, description="Agent ID for agent_call steps")
    tool_id: Optional[str] = Field(default=None, description="Tool ID for tool_call steps")
    config: Dict[str, Any] = Field(default_factory=dict, description="Step configuration")
    
    # Step relationships and flow
    depends_on: List[str] = Field(default_factory=list, description="Step dependencies")
    
    # Input/Output mapping
    input_mapping: Optional[Dict[str, str]] = Field(default=None, description="Input data mapping using JSONPath")
    output_mapping: Optional[Dict[str, str]] = Field(default=None, description="Output data mapping using JSONPath")
    
    # Error handling and retry logic
    error_handling: Optional[ErrorHandling] = Field(default=None, description="Error handling configuration")
    
    # Execution control
    timeout_seconds: Optional[int] = Field(300, description="Step timeout")
    retry_attempts: int = Field(0, description="Number of retry attempts")
    retry_delay_seconds: int = Field(5, description="Delay between retries")
    condition: Optional[str] = Field(None, description="Execution condition")

# Workflow Definition Models
class WorkflowDefinitionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: str = Field("1.0.0", max_length=20)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    category: Optional[str] = Field(None, max_length=100)
    
    # Service Discovery
    execution_url: Optional[str] = Field(default=None, description="Workflow execution endpoint")
    dns_name: Optional[str] = Field(default=None, description="DNS name for service discovery")
    status_url: Optional[str] = Field(default=None, description="Status monitoring endpoint")
    
    # Input/Output Signatures
    input_signature: Optional[InputOutputSignature] = Field(default=None, description="Input signature schema")
    output_signature: Optional[InputOutputSignature] = Field(default=None, description="Output signature schema")
    
    # Workflow Definition
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Default variables")
    
    # Triggers and Scheduling
    triggers: List[TriggerConfig] = Field(default_factory=list, description="Workflow triggers")
    
    # Dependencies
    dependencies: Optional[WorkflowDependencies] = Field(default=None, description="External dependencies")
    
    # Execution Configuration
    timeout_seconds: Optional[int] = Field(3600, description="Overall workflow timeout")
    retry_config: Optional[Dict[str, Any]] = None
    notification_config: Optional[Dict[str, Any]] = None
    
    # Metadata and Classification
    tags: List[str] = Field(default_factory=list)
    project_tags: List[str] = Field(default_factory=list, description="Project tags for filtering")
    is_template: bool = Field(False, description="Whether this is a template")
    is_public: bool = Field(False, description="Whether this workflow is public")
    
    # Extended metadata
    author: Optional[str] = Field(default=None, description="Workflow author/creator")
    organization: Optional[str] = Field(default=None, description="Organization name")
    environment: Optional[str] = Field(default=None, description="Deployment environment")

class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    pass

class WorkflowDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    steps: Optional[List[WorkflowStep]] = None
    variables: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    project_tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    is_public: Optional[bool] = None
    retry_config: Optional[Dict[str, Any]] = None
    notification_config: Optional[Dict[str, Any]] = None

class WorkflowDefinitionResponse(WorkflowDefinitionBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# Workflow Execution Models
class WorkflowExecutionRequest(BaseModel):
    workflow_id: UUID = Field(..., description="ID of workflow to execute")
    execution_name: Optional[str] = Field(None, description="Optional friendly name")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Runtime variables")
    timeout_seconds: Optional[int] = None
    priority: int = Field(0, description="Execution priority")
    project_tags: List[str] = Field(default_factory=list)
    execution_context: Optional[Dict[str, Any]] = None

class WorkflowExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    execution_name: Optional[str] = None
    status: ExecutionStatus
    current_step: Optional[str] = None
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    variables: Dict[str, Any]
    step_results: Dict[str, Any]
    step_statuses: Dict[str, Any]
    step_timings: Dict[str, Any]
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    priority: int
    timeout_seconds: Optional[int] = None
    project_tags: List[str]
    executed_by: Optional[str] = None
    execution_context: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Workflow Template Models
class WorkflowTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    template_definition: Dict[str, Any] = Field(..., description="Template structure")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="Template parameters")
    tags: List[str] = Field(default_factory=list)
    project_tags: List[str] = Field(default_factory=list)
    is_active: bool = True

class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass

class WorkflowTemplateResponse(WorkflowTemplateBase):
    id: UUID
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

# Workflow Schedule Models
class WorkflowScheduleBase(BaseModel):
    workflow_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    timezone: str = Field("UTC", max_length=50)
    is_active: bool = True
    max_concurrent_executions: int = Field(1, ge=1)
    retry_failed: bool = False
    default_input: Dict[str, Any] = Field(default_factory=dict)
    default_variables: Dict[str, Any] = Field(default_factory=dict)
    project_tags: List[str] = Field(default_factory=list)

class WorkflowScheduleCreate(WorkflowScheduleBase):
    pass

class WorkflowScheduleResponse(WorkflowScheduleBase):
    id: UUID
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

# Summary Models for Lists
class WorkflowSummary(BaseModel):
    """Simplified workflow info for listing"""
    id: UUID
    name: str
    display_name: str
    description: Optional[str] = None
    status: WorkflowStatus
    category: Optional[str] = None
    tags: List[str]
    project_tags: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

class ExecutionSummary(BaseModel):
    """Simplified execution info for listing"""
    id: UUID
    workflow_id: UUID
    execution_name: Optional[str] = None
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    error_message: Optional[str] = None
