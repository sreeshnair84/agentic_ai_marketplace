"""
Pydantic models for Tools, Templates, and Instances
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

# New models for enhanced tool registry
class InputOutputSignature(BaseModel):
    """Input/Output signature definition for tools"""
    schema: Dict[str, Any] = Field(description="JSON schema for input/output")
    content_types: List[str] = Field(default_factory=lambda: ["application/json"], description="Supported content types")
    size_limits: Optional[Dict[str, str]] = Field(default=None, description="Size limitations")


class HealthCheckConfig(BaseModel):
    """Health check configuration for tools"""
    enabled: bool = Field(default=True, description="Whether health checks are enabled")
    endpoint: str = Field(default="/health", description="Health check endpoint")
    method: str = Field(default="GET", description="HTTP method for health check")
    expected_status: int = Field(default=200, description="Expected HTTP status code")
    interval_seconds: int = Field(default=60, description="Health check interval")
    timeout_seconds: int = Field(default=10, description="Health check timeout")


class RuntimeConfig(BaseModel):
    """Runtime environment configuration for tools"""
    environment: str = Field(description="Runtime environment (python|nodejs|docker|native)")
    requirements: List[str] = Field(default_factory=list, description="Runtime requirements")
    timeout_seconds: int = Field(default=300, description="Execution timeout")
    memory_limit: str = Field(default="512MB", description="Memory limit")
    cpu_limit: str = Field(default="1000m", description="CPU limit")


class MCPConfig(BaseModel):
    """MCP server configuration"""
    server_name: str = Field(description="MCP server name")
    server_url: str = Field(description="MCP server URL")
    protocol_version: str = Field(default="1.0", description="MCP protocol version")
    transport: str = Field(default="http", description="Transport type (stdio|http|websocket)")
    capabilities: List[str] = Field(default_factory=list, description="MCP capabilities")


class ConfigurationField(BaseModel):
    """Configuration field definition for tools"""
    name: str = Field(description="Configuration field name")
    type: str = Field(description="Field type (password|select|text|number|boolean)")
    required: bool = Field(default=False, description="Whether field is required")
    description: str = Field(description="Field description")
    validation: Optional[str] = Field(default=None, description="Validation pattern")
    options: Optional[List[str]] = Field(default=None, description="Available options for select type")
    default: Optional[str] = Field(default=None, description="Default value")


class UsageMetrics(BaseModel):
    """Usage metrics for monitoring tools"""
    total_executions: int = Field(default=0, description="Total number of executions")
    success_rate: float = Field(default=1.0, description="Success rate (0-1)")
    avg_execution_time: float = Field(default=0.0, description="Average execution time in seconds")
    last_executed: Optional[datetime] = Field(default=None, description="Last execution timestamp")

class ToolCategory(str, Enum):
    MCP = "mcp"
    CUSTOM = "custom"
    API = "api"
    LLM = "llm"
    RAG = "rag"
    WORKFLOW = "workflow"
    COMMUNICATION = "Communication"

class FieldType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    URL = "url"
    EMAIL = "email"
    PASSWORD = "password"
    JSON = "json"

class ToolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"

class EnvironmentScope(str, Enum):
    GLOBAL = "global"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# Tool Template Field Models
class ToolTemplateFieldBase(BaseModel):
    field_name: str = Field(..., min_length=1, max_length=255)
    field_label: str = Field(..., min_length=1, max_length=255)
    field_type: FieldType
    field_description: Optional[str] = None
    is_required: bool = False
    is_secret: bool = False
    default_value: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    field_options: Optional[Dict[str, Any]] = None
    field_order: int = 0

class ToolTemplateFieldCreate(ToolTemplateFieldBase):
    pass

class ToolTemplateFieldResponse(ToolTemplateFieldBase):
    id: UUID
    tool_template_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Tool Template Models
class ToolTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: ToolCategory
    type: str = Field(..., min_length=1, max_length=50)
    version: str = "1.0.0"
    is_active: bool = True
    icon: Optional[str] = None
    tags: Optional[List[str]] = None

class ToolTemplateCreate(ToolTemplateBase):
    fields: Optional[List[ToolTemplateFieldCreate]] = None

class ToolTemplateUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ToolCategory] = None
    type: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = None
    tags: Optional[List[str]] = None

class ToolTemplateResponse(ToolTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    fields: Optional[List[ToolTemplateFieldResponse]] = None

    class Config:
        from_attributes = True

# Tool Instance Models
class ToolInstanceBase(BaseModel):
    tool_template_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: ToolStatus = ToolStatus.INACTIVE
    configuration: Dict[str, Any] = Field(default_factory=dict)
    environment_scope: EnvironmentScope

class ToolInstanceCreate(ToolInstanceBase):
    pass

class ToolInstanceUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ToolStatus] = None
    configuration: Optional[Dict[str, Any]] = None
    environment_scope: Optional[EnvironmentScope] = None

class ToolInstanceResponse(ToolInstanceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    template: Optional[ToolTemplateResponse] = None

    class Config:
        from_attributes = True

# LLM Model Models
class LLMModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., min_length=1, max_length=100)
    model_type: str = Field(..., min_length=1, max_length=50)
    endpoint_url: Optional[str] = None
    api_key_env_var: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    supports_streaming: bool = False
    supports_functions: bool = False
    cost_per_token: Optional[float] = None
    is_active: bool = True

class LLMModelCreate(LLMModelBase):
    pass

class LLMModelResponse(LLMModelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Enhanced Tool Registry Models
class EnhancedToolRegistryBase(BaseModel):
    """Enhanced tool definition with complete registry specification"""
    id: Optional[str] = Field(default=None, description="Unique tool identifier")
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: ToolCategory
    type: str = Field(..., min_length=1, max_length=50)
    version: str = "1.0.0"
    
    # Endpoints and Discovery
    endpoint_url: Optional[str] = Field(default=None, description="Tool execution endpoint")
    dns_name: Optional[str] = Field(default=None, description="DNS name for service discovery")
    health_url: Optional[str] = Field(default=None, description="Health check URL")
    documentation_url: Optional[str] = Field(default=None, description="Documentation URL")
    
    # Input/Output Signatures
    input_signature: Optional[InputOutputSignature] = Field(default=None, description="Input signature schema")
    output_signature: Optional[InputOutputSignature] = Field(default=None, description="Output signature schema")
    
    # MCP Integration
    mcp_config: Optional[MCPConfig] = Field(default=None, description="MCP configuration if applicable")
    
    # Configuration and Runtime
    configuration_fields: List[ConfigurationField] = Field(default_factory=list, description="Tool configuration fields")
    runtime: Optional[RuntimeConfig] = Field(default=None, description="Runtime environment configuration")
    
    # Health and Monitoring
    health_check: Optional[HealthCheckConfig] = Field(default=None, description="Health monitoring configuration")
    usage_metrics: Optional[UsageMetrics] = Field(default=None, description="Usage and performance metrics")
    
    # Metadata
    tags: Optional[List[str]] = None
    status: ToolStatus = ToolStatus.INACTIVE
    is_active: bool = True
    icon: Optional[str] = None
    
    # Extended metadata
    author: Optional[str] = Field(default=None, description="Tool author/creator")
    organization: Optional[str] = Field(default=None, description="Organization name")
    environment: Optional[str] = Field(default=None, description="Deployment environment")


class EnhancedToolRegistryCreate(EnhancedToolRegistryBase):
    pass


class EnhancedToolRegistryUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ToolCategory] = None
    type: Optional[str] = None
    version: Optional[str] = None
    endpoint_url: Optional[str] = None
    input_signature: Optional[InputOutputSignature] = None
    output_signature: Optional[InputOutputSignature] = None
    configuration_fields: Optional[List[ConfigurationField]] = None
    status: Optional[ToolStatus] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class EnhancedToolRegistryResponse(EnhancedToolRegistryBase):
    id: UUID = Field(description="Unique tool identifier")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


# Keep existing models for backward compatibility
# Embedding Model Models
class EmbeddingModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., min_length=1, max_length=100)
    endpoint_url: Optional[str] = None
    api_key_env_var: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    dimensions: Optional[int] = None
    max_input_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None
    is_active: bool = True

class EmbeddingModelCreate(EmbeddingModelBase):
    pass

class EmbeddingModelResponse(EmbeddingModelBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
