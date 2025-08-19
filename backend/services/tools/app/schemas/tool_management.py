"""
Pydantic schemas for tool management system
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from enum import Enum

class ToolType(str, Enum):
    RAG = "rag"
    SQL_AGENT = "sql_agent"
    MCP = "mcp"
    CODE_INTERPRETER = "code_interpreter"
    WEB_SCRAPER = "web_scraper"
    FILE_PROCESSOR = "file_processor"
    API_INTEGRATION = "api_integration"
    CUSTOM = "custom"

class InstanceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPLOYING = "deploying"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# Tool Template Schemas
class ToolTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: ToolType
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    default_config: Optional[Dict[str, Any]] = {}
    version: Optional[str] = "1.0.0"
    is_active: Optional[bool] = True
    tags: Optional[List[str]] = []
    documentation: Optional[str] = None

class ToolTemplateCreate(ToolTemplateBase):
    pass

class ToolTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[ToolType] = None
    description: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    documentation: Optional[str] = None

class ToolTemplateResponse(ToolTemplateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

# Tool Instance Schemas
class ToolInstanceBase(BaseModel):
    template_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Dict[str, Any] = {}
    credentials: Optional[Dict[str, Any]] = {}
    environment: Environment = Environment.DEVELOPMENT
    status: InstanceStatus = InstanceStatus.INACTIVE
    resource_limits: Optional[Dict[str, Any]] = {}
    health_check_config: Optional[Dict[str, Any]] = {}

class ToolInstanceCreate(ToolInstanceBase):
    pass

class ToolInstanceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    environment: Optional[Environment] = None
    status: Optional[InstanceStatus] = None
    resource_limits: Optional[Dict[str, Any]] = None
    health_check_config: Optional[Dict[str, Any]] = None

class ToolInstanceResponse(ToolInstanceBase):
    id: uuid.UUID
    health_status: Optional[str] = None
    last_health_check: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = {}
    error_log: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    template: Optional[ToolTemplateResponse] = None

    class Config:
        from_attributes = True

# RAG Pipeline Schemas
class RAGPipelineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    data_sources: List[Dict[str, Any]] = []
    processing_config: Dict[str, Any] = {}
    chunking_strategy: Dict[str, Any] = {}
    vectorization_config: Dict[str, Any] = {}
    storage_config: Dict[str, Any] = {}
    retrieval_config: Dict[str, Any] = {}
    quality_config: Optional[Dict[str, Any]] = {}
    schedule_config: Optional[Dict[str, Any]] = {}
    is_active: Optional[bool] = True

class RAGPipelineCreate(RAGPipelineBase):
    pass

class RAGPipelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    data_sources: Optional[List[Dict[str, Any]]] = None
    processing_config: Optional[Dict[str, Any]] = None
    chunking_strategy: Optional[Dict[str, Any]] = None
    vectorization_config: Optional[Dict[str, Any]] = None
    storage_config: Optional[Dict[str, Any]] = None
    retrieval_config: Optional[Dict[str, Any]] = None
    quality_config: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class RAGPipelineResponse(RAGPipelineBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

# Agent Template Schemas
class AgentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    framework: str = "langgraph"
    workflow_config: Dict[str, Any] = {}
    persona_config: Optional[Dict[str, Any]] = {}
    capabilities: Optional[List[str]] = []
    constraints: Optional[Dict[str, Any]] = {}
    tool_template_requirements: Optional[List[Dict[str, Any]]] = []
    optional_tool_templates: Optional[List[Dict[str, Any]]] = []
    default_tool_bindings: Optional[Dict[str, Any]] = {}
    version: Optional[str] = "1.0.0"
    is_active: Optional[bool] = True
    tags: Optional[List[str]] = []
    documentation: Optional[str] = None

class AgentTemplateCreate(AgentTemplateBase):
    pass

class AgentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    framework: Optional[str] = None
    workflow_config: Optional[Dict[str, Any]] = None
    persona_config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    constraints: Optional[Dict[str, Any]] = None
    tool_template_requirements: Optional[List[Dict[str, Any]]] = None
    optional_tool_templates: Optional[List[Dict[str, Any]]] = None
    default_tool_bindings: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    documentation: Optional[str] = None

class AgentTemplateResponse(AgentTemplateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True

# Agent Instance Schemas
class AgentInstanceBase(BaseModel):
    template_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tool_instance_bindings: Dict[str, Any] = {}
    runtime_config: Optional[Dict[str, Any]] = {}
    state_config: Optional[Dict[str, Any]] = {}
    security_config: Optional[Dict[str, Any]] = {}
    status: InstanceStatus = InstanceStatus.INACTIVE
    environment: Environment = Environment.DEVELOPMENT
    deployment_config: Optional[Dict[str, Any]] = {}

class AgentInstanceCreate(AgentInstanceBase):
    pass

class AgentInstanceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tool_instance_bindings: Optional[Dict[str, Any]] = None
    runtime_config: Optional[Dict[str, Any]] = None
    state_config: Optional[Dict[str, Any]] = None
    security_config: Optional[Dict[str, Any]] = None
    status: Optional[InstanceStatus] = None
    environment: Optional[Environment] = None
    deployment_config: Optional[Dict[str, Any]] = None

class AgentInstanceResponse(AgentInstanceBase):
    id: uuid.UUID
    conversation_history: Optional[List[Dict[str, Any]]] = []
    performance_metrics: Optional[Dict[str, Any]] = {}
    last_activity: Optional[datetime] = None
    error_log: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    template: Optional[AgentTemplateResponse] = None

    class Config:
        from_attributes = True

# Tool Execution Schemas
class ToolExecutionCreate(BaseModel):
    execution_type: str
    input_data: Dict[str, Any] = {}

class ToolExecutionResponse(BaseModel):
    id: uuid.UUID
    status: str
    output_data: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    error_details: Optional[str] = None

    class Config:
        from_attributes = True

# Validation and Health Check Schemas
class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

class HealthCheckResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

# RAG Pipeline Run Schemas
class RAGPipelineRunCreate(BaseModel):
    run_type: str = "manual"
    input_data: Optional[Dict[str, Any]] = {}

class RAGPipelineRunResponse(BaseModel):
    id: uuid.UUID
    pipeline_id: uuid.UUID
    run_type: str
    status: str
    progress: Optional[Dict[str, Any]] = {}
    metrics: Optional[Dict[str, Any]] = {}
    logs: Optional[str] = None
    error_details: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = {}
    output_summary: Optional[Dict[str, Any]] = {}
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Tool Association Schemas
class ToolAssociationCreate(BaseModel):
    tool_template_id: uuid.UUID
    agent_template_id: uuid.UUID
    role_name: str
    configuration: Optional[Dict[str, Any]] = {}
    is_required: bool = True
    execution_order: int = 0

class ToolAssociationResponse(BaseModel):
    id: uuid.UUID
    tool_template_id: uuid.UUID
    agent_template_id: uuid.UUID
    role_name: str
    configuration: Dict[str, Any]
    is_required: bool
    execution_order: int
    created_at: datetime

    class Config:
        from_attributes = True

# RAG Pipeline Schemas
class RAGPipelineStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class DataSource(str, Enum):
    TEXT = "text"
    FILE_UPLOAD = "file_upload"
    WEB_SCRAPING = "web_scraping"
    API_EXTRACTION = "api_extraction"

class IngestionMethod(str, Enum):
    IMMEDIATE = "immediate"
    BATCH = "batch"
    STREAMING = "streaming"
    SCHEDULED = "scheduled"

class RAGPipelineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tool_instance_id: uuid.UUID
    data_sources: List[Dict[str, Any]] = []
    vectorization_config: Dict[str, Any] = {}
    ingestion_config: Dict[str, Any] = {}
    retrieval_config: Dict[str, Any] = {}
    metadata: Optional[Dict[str, Any]] = {}

class RAGPipelineCreate(RAGPipelineBase):
    pass

class RAGPipelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    data_sources: Optional[List[Dict[str, Any]]] = None
    vectorization_config: Optional[Dict[str, Any]] = None
    ingestion_config: Optional[Dict[str, Any]] = None
    retrieval_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class RAGPipelineResponse(BaseModel):
    id: uuid.UUID
    tool_instance_id: uuid.UUID
    name: str
    display_name: str
    description: Optional[str]
    status: RAGPipelineStatus
    data_sources: List[Dict[str, Any]]
    vectorization_config: Dict[str, Any]
    ingestion_config: Dict[str, Any]
    retrieval_config: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True

class DataIngestionRequest(BaseModel):
    pipeline_id: uuid.UUID
    source_type: DataSource
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class VectorizationRequest(BaseModel):
    pipeline_id: uuid.UUID
    embedding_model: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    batch_size: int = 10
