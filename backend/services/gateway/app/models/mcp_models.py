"""
Pydantic models for MCP Registry and Gateway
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# =====================================================
# ENUMS
# =====================================================

class MCPTransportType(str, Enum):
    streamable = "streamable"
    sse = "sse"
    stdio = "stdio"
    http = "http"

class MCPServerStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    error = "error"
    testing = "testing"

class MCPHealthStatus(str, Enum):
    healthy = "healthy"
    unhealthy = "unhealthy"
    unknown = "unknown"
    degraded = "degraded"

class MCPEndpointStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    draft = "draft"
    error = "error"

class MCPExecutionStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    timeout = "timeout"
    cancelled = "cancelled"

# =====================================================
# MCP SERVER MODELS
# =====================================================

class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    server_url: str = Field(..., min_length=1, max_length=500)
    transport_type: MCPTransportType = MCPTransportType.streamable
    authentication_config: Dict[str, Any] = Field(default_factory=dict)
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0.0"
    status: MCPServerStatus = MCPServerStatus.inactive
    health_check_url: Optional[str] = None
    connection_config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    project_tags: List[str] = Field(default_factory=list)
    is_active: bool = True

class MCPServerCreate(MCPServerBase):
    pass

class MCPServerUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    server_url: Optional[str] = None
    transport_type: Optional[MCPTransportType] = None
    authentication_config: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    status: Optional[MCPServerStatus] = None
    health_check_url: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    project_tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class MCPServerResponse(MCPServerBase):
    id: str
    health_status: MCPHealthStatus = MCPHealthStatus.unknown
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# MCP TOOL MODELS
# =====================================================

class MCPToolBase(BaseModel):
    server_id: str
    tool_name: str = Field(..., min_length=1, max_length=255)
    display_name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    tool_config: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    is_available: bool = True
    tags: List[str] = Field(default_factory=list)

class MCPToolCreate(MCPToolBase):
    pass

class MCPToolUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    tool_config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    version: Optional[str] = None
    is_available: Optional[bool] = None
    tags: Optional[List[str]] = None

class MCPToolResponse(MCPToolBase):
    id: str
    usage_count: int = 0
    success_rate: float = 0.0
    avg_execution_time: int = 0
    last_discovered: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# MCP ENDPOINT MODELS
# =====================================================

class MCPEndpointBase(BaseModel):
    endpoint_name: str = Field(..., min_length=1, max_length=255)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    endpoint_path: str = Field(..., pattern=r'^/[a-zA-Z0-9\-_/]+$')
    transport_config: Dict[str, Any] = Field(default_factory=dict)
    authentication_required: bool = False
    authentication_config: Dict[str, Any] = Field(default_factory=dict)
    rate_limiting: Dict[str, Any] = Field(default_factory=dict)
    timeout_config: Dict[str, Any] = Field(default_factory=dict)
    middleware_config: List[Dict[str, Any]] = Field(default_factory=list)
    status: MCPEndpointStatus = MCPEndpointStatus.inactive
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    project_tags: List[str] = Field(default_factory=list)
    is_public: bool = False

    @field_validator('endpoint_path')
    @classmethod
    def validate_endpoint_path(cls, v):
        if not v.startswith('/'):
            raise ValueError('Endpoint path must start with /')
        return v

class MCPEndpointCreate(MCPEndpointBase):
    pass

class MCPEndpointUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    endpoint_path: Optional[str] = None
    transport_config: Optional[Dict[str, Any]] = None
    authentication_required: Optional[bool] = None
    authentication_config: Optional[Dict[str, Any]] = None
    rate_limiting: Optional[Dict[str, Any]] = None
    timeout_config: Optional[Dict[str, Any]] = None
    middleware_config: Optional[List[Dict[str, Any]]] = None
    status: Optional[MCPEndpointStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    project_tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

    @field_validator('endpoint_path')
    @classmethod
    def validate_endpoint_path(cls, v):
        if v is not None and not v.startswith('/'):
            raise ValueError('Endpoint path must start with /')
        return v

class MCPEndpointResponse(MCPEndpointBase):
    id: str
    endpoint_url: str
    health_status: MCPHealthStatus = MCPHealthStatus.unknown
    usage_analytics: Dict[str, Any] = Field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# MCP TOOL BINDING MODELS
# =====================================================

class MCPToolBindingBase(BaseModel):
    tool_registry_id: Optional[str] = None
    server_id: Optional[str] = None
    tool_name: str = Field(..., min_length=1, max_length=255)
    binding_name: Optional[str] = None
    binding_config: Dict[str, Any] = Field(default_factory=dict)
    parameter_mapping: Dict[str, Any] = Field(default_factory=dict)
    middleware_config: List[Dict[str, Any]] = Field(default_factory=list)
    execution_order: int = 0
    is_enabled: bool = True
    conditional_execution: Dict[str, Any] = Field(default_factory=dict)
    error_handling: Dict[str, Any] = Field(default_factory=dict)
    retry_config: Dict[str, Any] = Field(default_factory=dict)

class MCPToolBindingCreate(MCPToolBindingBase):
    pass

class MCPToolBindingUpdate(BaseModel):
    tool_registry_id: Optional[str] = None
    server_id: Optional[str] = None
    tool_name: Optional[str] = None
    binding_name: Optional[str] = None
    binding_config: Optional[Dict[str, Any]] = None
    parameter_mapping: Optional[Dict[str, Any]] = None
    middleware_config: Optional[List[Dict[str, Any]]] = None
    execution_order: Optional[int] = None
    is_enabled: Optional[bool] = None
    conditional_execution: Optional[Dict[str, Any]] = None
    error_handling: Optional[Dict[str, Any]] = None
    retry_config: Optional[Dict[str, Any]] = None

class MCPToolBindingResponse(MCPToolBindingBase):
    id: str
    endpoint_id: str
    tool_display_name: Optional[str] = None
    tool_description: Optional[str] = None
    server_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# =====================================================
# EXECUTION MODELS
# =====================================================

class MCPExecutionRequest(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    user_context: Dict[str, Any] = Field(default_factory=dict)
    execution_config: Dict[str, Any] = Field(default_factory=dict)

class MCPExecutionLogResponse(BaseModel):
    id: str
    endpoint_id: Optional[str] = None
    endpoint_name: Optional[str] = None
    tool_name: str
    execution_id: str
    execution_status: MCPExecutionStatus
    execution_time_ms: Optional[int] = None
    server_name: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =====================================================
# TEST RESULT MODELS
# =====================================================

class MCPTestResultResponse(BaseModel):
    id: str
    tool_registry_id: str
    server_id: str
    test_name: str
    test_description: Optional[str] = None
    test_input: Dict[str, Any]
    expected_output: Dict[str, Any] = Field(default_factory=dict)
    actual_output: Dict[str, Any] = Field(default_factory=dict)
    test_status: str
    error_details: Optional[str] = None
    execution_time_ms: Optional[int] = None
    assertions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# =====================================================
# HEALTH AND ANALYTICS MODELS
# =====================================================

class MCPHealthResponse(BaseModel):
    overall_status: str
    components: Dict[str, Any]
    timestamp: str

class MCPAnalyticsResponse(BaseModel):
    endpoint_id: str
    period_days: int
    summary: Dict[str, Any]
    daily_stats: List[Dict[str, Any]]

# =====================================================
# DISCOVERY AND INTEGRATION MODELS
# =====================================================

class MCPServerDiscoveryRequest(BaseModel):
    server_url: str
    transport_type: MCPTransportType = MCPTransportType.streamable
    authentication_config: Dict[str, Any] = Field(default_factory=dict)
    connection_config: Dict[str, Any] = Field(default_factory=dict)

class MCPToolDiscoveryResponse(BaseModel):
    server_id: str
    discovered_tools: List[MCPToolResponse]
    discovery_time: datetime
    total_discovered: int
    errors: List[str] = Field(default_factory=list)

class MCPEndpointTestRequest(BaseModel):
    test_data: Dict[str, Any] = Field(default_factory=dict)
    include_analytics: bool = False
    dry_run: bool = False

class MCPEndpointTestResponse(BaseModel):
    endpoint_id: str
    test_status: str
    execution_results: List[Dict[str, Any]]
    total_execution_time_ms: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    analytics: Optional[Dict[str, Any]] = None
