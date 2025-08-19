"""
A2A Protocol Models for Orchestrator
Based on https://github.com/a2aproject/a2a-samples
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import uuid


class TaskState(str, Enum):
    """Task state enumeration"""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"
    input_required = "input_required"
    unknown = "unknown"


class Role(str, Enum):
    """Message role enumeration"""
    user = "user"
    assistant = "assistant"
    system = "system"


class A2APartType(str, Enum):
    """A2A message part types"""
    text = "text"
    data = "data"
    image = "image"
    audio = "audio"
    video = "video"
    file = "file"


class A2AMessagePart(BaseModel):
    """A2A message part"""
    type: A2APartType
    text: Optional[str] = None
    data: Optional[str] = None  # Base64 encoded
    mime_type: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class A2AMessage(BaseModel):
    """A2A protocol message"""
    role: Role
    parts: List[A2AMessagePart]
    message_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    context_id: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class A2ATaskRequest(BaseModel):
    """A2A task request"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    context_id: Optional[str] = None
    accepted_output_modes: List[str] = ["text"]
    message: A2AMessage
    metadata: Optional[Dict[str, Any]] = None


class A2ATaskStatus(BaseModel):
    """A2A task status"""
    state: TaskState
    message: Optional[A2AMessage] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    error: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class A2AArtifact(BaseModel):
    """A2A task artifact"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # e.g., "text", "image", "document"
    parts: List[A2AMessagePart]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class A2ATask(BaseModel):
    """A2A task representation"""
    id: str
    context_id: Optional[str] = None
    status: A2ATaskStatus
    artifacts: Optional[List[A2AArtifact]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class A2ACapabilities(BaseModel):
    """A2A agent capabilities"""
    streaming: bool = True
    batch_processing: bool = True
    multi_modal: bool = True
    persistent_sessions: bool = True


class A2ASkill(BaseModel):
    """A2A agent skill definition"""
    id: str
    name: str
    description: str
    tags: List[str] = []
    examples: List[str] = []
    parameters: Optional[Dict[str, Any]] = None


class A2AAgentCard(BaseModel):
    """A2A agent card - describes agent capabilities"""
    name: str
    description: str
    version: str = "1.0.0"
    url: str
    default_input_modes: List[str] = ["text"]
    default_output_modes: List[str] = ["text"]
    capabilities: A2ACapabilities = Field(default_factory=A2ACapabilities)
    skills: List[A2ASkill] = []
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class RemoteAgentInfo(BaseModel):
    """Information about remote agents"""
    name: str
    description: str
    url: str
    card: A2AAgentCard
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, inactive, error


class OrchestrationContext(BaseModel):
    """Context for orchestration operations"""
    session_id: str
    context_id: Optional[str] = None
    user_query: str
    available_agents: List[RemoteAgentInfo] = []
    active_tasks: Dict[str, A2ATask] = {}
    conversation_history: List[A2AMessage] = []
    metadata: Optional[Dict[str, Any]] = None


class OrchestrationPlan(BaseModel):
    """Plan for multi-agent orchestration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    query: str
    steps: List[Dict[str, Any]] = []  # Orchestration steps
    selected_agents: List[str] = []  # Agent names
    dependencies: Dict[str, List[str]] = {}  # Task dependencies
    estimated_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrchestrationResult(BaseModel):
    """Result of orchestration execution"""
    plan_id: str
    session_id: str
    status: TaskState
    results: List[A2ATask] = []
    summary: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# JSON-RPC Models for A2A Protocol

class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None


class JsonRpcSuccessResponse(BaseModel):
    """JSON-RPC 2.0 success response"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Any


class JsonRpcErrorResponse(BaseModel):
    """JSON-RPC 2.0 error response"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    error: Dict[str, Any]


class MessageSendParams(BaseModel):
    """Parameters for A2A message/send method"""
    id: str
    session_id: Optional[str] = None
    context_id: Optional[str] = None
    accepted_output_modes: List[str] = ["text"]
    message: A2AMessage


class MessageStreamParams(BaseModel):
    """Parameters for A2A message/stream method"""
    id: str
    session_id: Optional[str] = None
    context_id: Optional[str] = None
    accepted_output_modes: List[str] = ["text"]
    message: A2AMessage


class A2AAgentCardBuilder:
    """Builder for creating A2A agent cards"""
    
    @staticmethod
    def create_orchestrator_card(host: str = "localhost", port: int = 8003) -> A2AAgentCard:
        """Create orchestrator agent card"""
        return A2AAgentCard(
            name="AgenticAI Orchestrator Agent",
            description="Multi-agent orchestration and workflow coordination for AgenticAI platform",
            version="1.0.0",
            url=f"http://{host}:{port}",
            default_input_modes=["text"],
            default_output_modes=["text"],
            capabilities=A2ACapabilities(
                streaming=True,
                batch_processing=True,
                multi_modal=True,
                persistent_sessions=True
            ),
            skills=[
                A2ASkill(
                    id="multi_agent_orchestration",
                    name="Multi-Agent Orchestration",
                    description="Coordinate multiple agents to complete complex tasks",
                    tags=["orchestration", "coordination", "planning"],
                    examples=[
                        "Coordinate data analysis across multiple agents",
                        "Plan and execute multi-step workflows",
                        "Distribute tasks to specialized agents"
                    ]
                ),
                A2ASkill(
                    id="agent_discovery",
                    name="Agent Discovery and Selection",
                    description="Discover and select appropriate agents for tasks",
                    tags=["discovery", "selection", "routing"],
                    examples=[
                        "Find the best agent for data processing",
                        "Route queries to appropriate specialists",
                        "Load balance across available agents"
                    ]
                ),
                A2ASkill(
                    id="workflow_execution",
                    name="Workflow Execution",
                    description="Execute complex workflows with dependencies",
                    tags=["workflow", "execution", "dependencies"],
                    examples=[
                        "Execute data pipeline workflows",
                        "Coordinate dependent task execution",
                        "Handle workflow error recovery"
                    ]
                ),
                A2ASkill(
                    id="session_management",
                    name="Session and Context Management",
                    description="Manage conversation sessions and context",
                    tags=["session", "context", "memory"],
                    examples=[
                        "Maintain conversation context across agents",
                        "Manage session state and history",
                        "Coordinate context sharing between agents"
                    ]
                )
            ],
            tags=["orchestrator", "coordinator", "agenticai", "gemini", "multiagent"],
            metadata={
                "ai_provider": "gemini",
                "model_name": "gemini-1.5-pro",
                "service_type": "orchestrator",
                "framework": "fastapi"
            }
        )
