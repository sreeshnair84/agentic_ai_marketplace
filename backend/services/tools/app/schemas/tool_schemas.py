"""
Pydantic schemas for tool management
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid

# Tool Template Schemas

class ToolTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    template_type: str = Field(..., alias="type")
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    default_config: Optional[Dict[str, Any]] = {}
    version: Optional[str] = "1.0.0"
    is_active: bool = True
    tags: Optional[List[str]] = []
    documentation: Optional[str] = None

class ToolTemplateCreate(ToolTemplateBase):
    created_by: Optional[str] = None

class ToolTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    documentation: Optional[str] = None

class ToolTemplateResponse(ToolTemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    model_config: ConfigDict = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )

# Tool Instance Schemas

class ToolInstanceBase(BaseModel):
    template_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Dict[str, Any]
    credentials: Optional[Dict[str, Any]] = {}
    environment: Optional[str] = "development"
    resource_limits: Optional[Dict[str, Any]] = {}

class ToolInstanceCreate(ToolInstanceBase):
    created_by: Optional[str] = None

class ToolInstanceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None
    resource_limits: Optional[Dict[str, Any]] = None

class ToolInstanceResponse(ToolInstanceBase):
    id: str
    status: str
    health_status: Optional[str] = None
    last_health_check: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = {}
    error_log: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    template: Optional[ToolTemplateResponse] = None
    
    model_config: ConfigDict = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: lambda v: str(v)
        }
    )

# Tool Execution Schemas

class ToolExecutionRequest(BaseModel):
    execution_type: Optional[str] = "manual"
    execution_parameters: Dict[str, Any]
    timeout: Optional[int] = 300  # 5 minutes default

class ToolExecutionResponse(BaseModel):
    execution_id: str
    status: str  # "completed", "failed", "timeout"
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}

# RAG Pipeline Schemas

class RAGDataSource(BaseModel):
    type: str = Field(..., pattern="^(text|file|url|database|api)$")
    source: str
    metadata: Optional[Dict[str, Any]] = {}

class RAGPipelineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    data_sources: List[RAGDataSource] = []
    ingestion_config: Dict[str, Any] = {}
    vectorization_config: Dict[str, Any] = {}

class RAGPipelineCreate(RAGPipelineBase):
    tool_instance_id: str
    created_by: Optional[str] = None

class RAGPipelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    data_sources: Optional[List[RAGDataSource]] = None
    ingestion_config: Optional[Dict[str, Any]] = None
    vectorization_config: Optional[Dict[str, Any]] = None

class RAGPipelineResponse(RAGPipelineBase):
    id: str
    tool_instance_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    model_config: ConfigDict = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )

# Agent Template Schemas

class AgentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    framework: str = Field(default="langgraph", pattern="^(langgraph|crewai|autogen|semantic_kernel)$")
    workflow_definition: Dict[str, Any] = {}
    default_configuration: Dict[str, Any] = {}
    tool_associations: List[str] = []

class AgentTemplateCreate(AgentTemplateBase):
    created_by: Optional[str] = None

class AgentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    framework: Optional[str] = None
    workflow_definition: Optional[Dict[str, Any]] = None
    default_configuration: Optional[Dict[str, Any]] = None
    tool_associations: Optional[List[str]] = None

class AgentTemplateResponse(AgentTemplateBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    model_config: ConfigDict = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )

# Validation Schemas

class ConfigurationValidationRequest(BaseModel):
    template_id: str
    configuration: Dict[str, Any]

class ConfigurationValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: Optional[List[str]] = []

# Search and Filter Schemas

class ToolTemplateFilter(BaseModel):
    template_type: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    search_term: Optional[str] = None

class ToolInstanceFilter(BaseModel):
    template_id: Optional[str] = None
    status: Optional[str] = None
    environment: Optional[str] = None
    health_status: Optional[str] = None
    search_term: Optional[str] = None

# Metrics Schemas

class ToolInstanceMetrics(BaseModel):
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    last_execution_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ToolTemplateStats(BaseModel):
    total_templates: int = 0
    active_templates: int = 0
    templates_by_type: Dict[str, int] = {}
    total_instances: int = 0
    active_instances: int = 0

# File Upload Schemas

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    content_type: str
    upload_status: str
    processing_status: Optional[str] = None
    
class DocumentIngestionRequest(BaseModel):
    pipeline_id: str
    files: List[str]  # File IDs
    metadata: Optional[Dict[str, Any]] = {}
    processing_options: Optional[Dict[str, Any]] = {}

class DocumentIngestionResponse(BaseModel):
    ingestion_id: str
    pipeline_id: str
    status: str
    files_processed: int
    chunks_created: int
    vectors_generated: int
    processing_time_ms: float
    errors: Optional[List[str]] = []

# Test Schemas

class ToolTestRequest(BaseModel):
    test_type: str = "basic"  # "basic", "integration", "performance"
    test_parameters: Optional[Dict[str, Any]] = {}
    timeout: Optional[int] = 60

class ToolTestResponse(BaseModel):
    test_id: str
    test_type: str
    status: str  # "passed", "failed", "timeout"
    results: Dict[str, Any]
    recommendations: List[str] = []
    execution_time_ms: float
    timestamp: datetime
    
    model_config: ConfigDict = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

# Batch Operation Schemas

class BatchToolOperation(BaseModel):
    operation: str  # "activate", "deactivate", "delete", "test"
    tool_instance_ids: List[str]
    parameters: Optional[Dict[str, Any]] = {}

class BatchOperationResponse(BaseModel):
    operation_id: str
    operation: str
    total_items: int
    successful_items: int
    failed_items: int
    results: List[Dict[str, Any]]
    completed_at: datetime
    
    model_config: ConfigDict = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

# Error Response Schema

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config: ConfigDict = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
