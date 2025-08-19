"""
Pydantic schemas for agent management system
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from enum import Enum

class AgentFramework(str, Enum):
    LANGGRAPH = "langgraph"
    CREWAI = "crewai"
    AUTOGEN = "autogen"
    SEMANTIC_KERNEL = "semantic_kernel"
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

# Agent Template Schemas
class AgentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    framework: AgentFramework = AgentFramework.LANGGRAPH
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
    framework: Optional[AgentFramework] = None
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

# Tool Association Schemas
class ToolAssociationCreate(BaseModel):
    tool_template_id: uuid.UUID
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

# Conversation Schemas
class ConversationCreate(BaseModel):
    session_id: str
    conversation_data: Dict[str, Any] = {}
    metadata: Optional[Dict[str, Any]] = {}

class ConversationResponse(BaseModel):
    id: uuid.UUID
    agent_instance_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    session_id: str
    conversation_data: Dict[str, Any]
    metadata: Dict[str, Any]
    tools_used: List[str]
    performance_metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Agent Execution Schemas
class AgentExecutionRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    tool_preferences: Optional[Dict[str, Any]] = {}

class AgentExecutionResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str]
    execution_time_ms: int
    metadata: Dict[str, Any]
