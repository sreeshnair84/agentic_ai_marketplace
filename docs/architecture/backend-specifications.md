# Backend Services Specifications

> **Comprehensive technical specifications for Agentic AI Acceleration backend services with A2A Protocol and MCP Server integration**

## 1. Technology Stack & Service Architecture

### 1.1 Core Service Matrix

| Service | Port | Status | Primary Function | DNS/Health URL |
|---------|------|--------|------------------|----------------|
| Gateway | 8000 | ✅ Active | API routing, auth, rate limiting | `http://gateway:8000/health` |
| Agents | 8002 | ✅ Active | Multi-framework agent execution | `http://agents:8002/health` |
| Orchestrator | 8003 | ✅ Active | A2A protocol, workflow coordination | `http://orchestrator:8003/health` |
| RAG | 8004 | ✅ Active | Document processing, vector search | `http://rag:8004/health` |
| Tools | 8005 | ✅ Active | MCP integration, tool execution | `http://tools:8005/health` |
| SQL Tool | 8006 | ✅ Active | Database operations, query execution | `http://sqltool:8006/health` |
| Workflow Engine | 8007 | ✅ Active | Node-based workflow execution | `http://workflow-engine:8007/health` |
| Observability | 8008 | ✅ Active | Telemetry, monitoring, health checks | `http://observability:8008/health` |

### 1.2 Core Dependencies
```python
# requirements.txt - Standardized across all services
fastapi[all]==0.116.0
uvicorn[standard]==0.29.0
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
pydantic==2.6.0
pydantic-settings==2.2.0
httpx==0.27.0
aiofiles==23.2.0
python-json-logger==2.0.7
structlog==24.1.0
```

### 1.3 A2A Protocol & MCP Integration Stack
```python
# A2A Protocol Dependencies
websockets==12.0
asyncio-mqtt==0.16.1
aio-pika==9.4.0  # RabbitMQ async client
celery[redis]==5.3.6
kombu==5.3.5

# MCP Server Integration
mcp-server==0.1.0  # Model Context Protocol server
mcp-client==0.1.0  # MCP client library
jsonrpc-websocket==3.1.5
pydantic-core==2.18.2
```

### 1.4 Database & ORM
```python
# Database dependencies
sqlalchemy[asyncio]==2.0.28
asyncpg==0.29.0  # PostgreSQL async driver
alembic==1.13.1  # Database migrations
redis[hiredis]==5.0.2
aioredis==2.0.1
```

### 1.5 AI Frameworks Integration Matrix

| Framework | Version | Status | Use Case | A2A Card URL |
|-----------|---------|--------|----------|-------------|
| LangChain | 0.1.0 | ✅ Active | General-purpose agents | `/agents/cards/langchain` |
| LlamaIndex | 0.1.6 | ✅ Active | RAG-focused agents | `/agents/cards/llamaindex` |
| CrewAI | 0.28.8 | ✅ Active | Multi-agent collaboration | `/agents/cards/crewai` |
| Semantic Kernel | 0.5.1 | ✅ Active | Microsoft ecosystem integration | `/agents/cards/semantic-kernel` |

```python
# AI framework dependencies
langchain==0.1.0
langchain-openai==0.1.5
langchain-anthropic==0.1.4
langchain-community==0.0.20
llama-index==0.9.48
llama-index-llms-openai==0.1.6
semantic-kernel==0.5.1
crewai==0.28.8
openai==1.12.0
anthropic==0.19.1
google-generativeai==0.3.2
```

### 1.6 Observability & Monitoring
```python
# Observability dependencies
opentelemetry-api==1.23.0
opentelemetry-sdk==1.23.0
opentelemetry-instrumentation-fastapi==0.44b0
opentelemetry-instrumentation-httpx==0.44b0
opentelemetry-instrumentation-sqlalchemy==0.44b0
opentelemetry-instrumentation-redis==0.44b0
opentelemetry-exporter-jaeger==1.23.0
opentelemetry-exporter-prometheus==1.12.0rc1
prometheus-client==0.20.0
```

### 1.7 Message Queue & Communication
```python
# Messaging dependencies
celery[redis]==5.3.6
kombu==5.3.5
websockets==12.0
asyncio-mqtt==0.16.1
aio-pika==9.4.0  # RabbitMQ async client
```

### 1.8 Authentication & Security
```python
# Security dependencies
bcrypt==4.1.2
cryptography==42.0.4
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
authlib==1.3.0
python-oauth2==1.1.1
```

## 2. API Endpoint Specifications with Input/Output Signatures

### 2.1 Gateway Service Endpoints (`http://gateway:8000`)

#### Authentication Endpoints
```typescript
// POST /api/auth/login
interface LoginRequest {
  email: string;          // User email address
  password: string;       // User password
  rememberMe?: boolean;   // Optional: extend session duration
}

interface LoginResponse {
  token: string;          // JWT authentication token
  user: {
    id: string;          // User unique identifier
    email: string;       // User email
    role: string;        // User role (admin, user, viewer)
    firstName?: string;  // Optional: user first name
    lastName?: string;   // Optional: user last name
  };
  expiresAt: string;     // ISO date when token expires
}

// POST /api/auth/logout
interface LogoutRequest {
  token: string;         // JWT token to invalidate
}

interface LogoutResponse {
  success: boolean;      // Logout success status
  message: string;       // Status message
}
```

#### Proxy Endpoints
```typescript
// All proxied requests maintain original signatures but add:
interface ProxyHeaders {
  'X-User-ID': string;      // Forwarded user ID
  'X-User-Role': string;    // Forwarded user role
  'X-Trace-ID': string;     // Request tracing ID
  'X-Request-ID': string;   // Unique request identifier
}
```

### 2.2 Agents Service Endpoints (`http://agents:8002`)

#### Agent Management
```typescript
// POST /api/v1/agents
interface CreateAgentRequest {
  name: string;              // Agent display name
  description?: string;      // Agent description
  framework: 'langchain' | 'llamaindex' | 'crewai' | 'semantic_kernel';
  config: {
    model: string;           // AI model (gpt-4, claude-3, etc.)
    temperature: number;     // Response creativity (0.0-2.0)
    maxTokens: number;       // Maximum response tokens
    systemPrompt: string;    // Agent system instructions
    tools: string[];         // Tool IDs to attach
    streaming?: boolean;     // Enable streaming responses
  };
  skills: string[];          // Agent skill categories
  isTemplate?: boolean;      // Save as template
}

interface CreateAgentResponse {
  id: string;               // Generated agent ID
  name: string;             // Agent name
  framework: string;        // Framework used
  status: 'active' | 'inactive' | 'error';
  version: string;          // Agent version
  a2aCardUrl: string;       // A2A protocol card URL
  healthUrl: string;        // Agent health check URL
  createdAt: string;        // ISO creation timestamp
}

// POST /api/v1/agents/{agentId}/execute
interface ExecuteAgentRequest {
  message: string;          // User input message
  context?: any;            // Optional execution context
  sessionId?: string;       // Optional session ID
  streaming?: boolean;      // Enable streaming response
  metadata?: Record<string, any>; // Additional metadata
}

interface ExecuteAgentResponse {
  response: string;         // Agent response text
  agentId: string;         // Executing agent ID
  sessionId: string;       // Session identifier
  toolCalls?: Array<{
    toolId: string;        // Called tool ID
    input: any;            // Tool input parameters
    output: any;           // Tool execution result
    duration: number;      // Execution time in ms
  }>;
  citations?: Array<{
    source: string;        // Citation source
    title: string;         // Citation title
    url?: string;          // Optional source URL
    confidence: number;    // Citation confidence (0.0-1.0)
  }>;
  usage: {
    promptTokens: number;  // Input tokens used
    completionTokens: number; // Output tokens generated
    totalTokens: number;   // Total tokens consumed
  };
  metadata: Record<string, any>; // Response metadata
  traceId: string;         // Request trace ID
}
```

### 2.3 Tools Service Endpoints (`http://tools:8005`)

#### Tool Management & MCP Integration
```typescript
// GET /api/v1/tools
interface ListToolsResponse {
  tools: Array<{
    id: string;            // Tool unique identifier
    name: string;          // Tool display name
    description: string;   // Tool description
    type: 'mcp' | 'sql' | 'rag' | 'standard' | 'custom';
    parameters: {          // Tool input parameters schema
      [paramName: string]: {
        type: string;      // Parameter type (string, number, boolean, object)
        description: string; // Parameter description
        required: boolean; // Is parameter required
        example: any;      // Example value
      };
    };
    output: {              // Tool output schema
      type: string;        // Output type
      description: string; // Output description
      example: any;        // Example output
    };
    serverUrl?: string;    // MCP server URL (for MCP tools)
    healthUrl: string;     // Tool health check URL
    status: 'active' | 'inactive' | 'error';
    lastUpdated: string;   // ISO timestamp
  }>;
  total: number;           // Total tools count
  mcpServers: Array<{      // Connected MCP servers
    id: string;
    name: string;
    url: string;
    status: 'connected' | 'disconnected' | 'error';
    toolCount: number;
    capabilities: string[];
  }>;
}

// POST /api/v1/tools/{toolId}/execute
interface ExecuteToolRequest {
  parameters: Record<string, any>; // Tool-specific parameters
  context?: {
    sessionId?: string;    // Optional session context
    userId?: string;       // Optional user context
    traceId?: string;      // Optional trace ID
  };
  timeout?: number;        // Execution timeout in ms
}

interface ExecuteToolResponse {
  result: any;             // Tool execution result
  toolId: string;          // Executed tool ID
  executionTime: number;   // Execution duration in ms
  status: 'success' | 'error' | 'timeout';
  error?: string;          // Error message if failed
  metadata: {
    serverUrl?: string;    // MCP server URL (if applicable)
    version: string;       // Tool version
    capabilities: string[]; // Tool capabilities used
  };
  traceId: string;         // Request trace ID
}

// POST /api/v1/mcp/servers
interface RegisterMCPServerRequest {
  name: string;            // Server display name
  url: string;             // WebSocket URL
  apiKey?: string;         // Optional authentication key
  description?: string;    // Server description
  autoDiscovery: boolean;  // Enable automatic tool discovery
}

interface RegisterMCPServerResponse {
  id: string;              // Server ID
  name: string;            // Server name
  url: string;             // Server URL
  status: 'connected' | 'connecting' | 'error';
  toolsDiscovered: number; // Number of tools found
  capabilities: string[];  // Server capabilities
  healthUrl: string;       // Server health URL
}
```

### 2.4 Orchestrator Service Endpoints (`http://orchestrator:8003`)

#### A2A Protocol & Multi-Agent Orchestration
```typescript
// POST /api/v1/orchestration/execute
interface OrchestrationRequest {
  workflow: {
    id: string;            // Workflow template ID
    agents: Array<{
      id: string;          // Agent ID
      role: string;        // Agent role in workflow
      config?: any;        // Agent-specific config
    }>;
    coordination: 'sequential' | 'parallel' | 'dynamic';
    maxIterations?: number; // Maximum coordination cycles
  };
  input: {
    message: string;       // Initial input message
    context?: any;         // Additional context
    requirements?: string[]; // Specific requirements
  };
  options: {
    streaming?: boolean;   // Enable streaming updates
    timeout?: number;      // Execution timeout in ms
    a2aProtocol: boolean;  // Use A2A protocol
  };
}

interface OrchestrationResponse {
  executionId: string;     // Unique execution ID
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  result?: {
    finalOutput: string;   // Combined agent outputs
    agentOutputs: Array<{
      agentId: string;     // Agent ID
      role: string;        // Agent role
      output: string;      // Agent-specific output
      confidence: number;  // Output confidence
      executionTime: number; // Agent execution time
    }>;
    coordination: {
      totalIterations: number; // Coordination cycles used
      consensusReached: boolean; // Did agents reach consensus
      collaborationScore: number; // Collaboration effectiveness
    };
  };
  a2aMessages: Array<{     // A2A protocol messages
    from: string;          // Sender agent ID
    to: string;            // Receiver agent ID
    type: 'request' | 'response' | 'broadcast';
    content: any;          // Message content
    timestamp: string;     // ISO timestamp
    traceId: string;       // Message trace ID
  }>;
  traceId: string;         // Execution trace ID
  startTime: string;       // ISO start timestamp
  endTime?: string;        // ISO end timestamp (if completed)
}

// WebSocket: /api/v1/orchestration/stream/{executionId}
interface OrchestrationStreamEvent {
  type: 'agent_started' | 'agent_completed' | 'a2a_message' | 'coordination_update' | 'execution_completed';
  data: {
    agentId?: string;      // Relevant agent ID
    message?: string;      // Status message
    output?: any;          // Agent output (if applicable)
    a2aMessage?: any;      // A2A message (if applicable)
    timestamp: string;     // Event timestamp
  };
  executionId: string;     // Execution ID
  traceId: string;         // Trace ID
}
```

### 2.5 Workflow Engine Endpoints (`http://workflow-engine:8007`)

#### Node-Based Workflow Execution
```typescript
// POST /api/v1/workflows/execute
interface WorkflowExecutionRequest {
  workflowId: string;      // Workflow template ID
  input: Record<string, any>; // Workflow input variables
  nodes: Array<{
    id: string;            // Node ID
    type: 'agent' | 'tool' | 'condition' | 'parallel' | 'merge';
    config: {
      agentId?: string;    // Agent ID (for agent nodes)
      toolId?: string;     // Tool ID (for tool nodes)
      condition?: string;  // Condition expression (for condition nodes)
      parameters?: Record<string, any>; // Node parameters
    };
    position: { x: number; y: number }; // Visual position
  }>;
  edges: Array<{
    id: string;            // Edge ID
    source: string;        // Source node ID
    target: string;        // Target node ID
    condition?: string;    // Edge condition
  }>;
  options: {
    timeout?: number;      // Execution timeout
    maxRetries?: number;   // Maximum node retries
    parallelLimit?: number; // Parallel execution limit
  };
}

interface WorkflowExecutionResponse {
  executionId: string;     // Execution ID
  status: 'running' | 'completed' | 'failed' | 'paused';
  currentNode?: string;    // Currently executing node
  nodeStates: Record<string, {
    status: 'pending' | 'running' | 'completed' | 'failed';
    input?: any;           // Node input
    output?: any;          // Node output
    error?: string;        // Error message
    executionTime?: number; // Execution time in ms
    retryCount: number;    // Retry attempts
  }>;
  variables: Record<string, any>; // Workflow variables
  output?: Record<string, any>; // Final workflow output
  traceId: string;         // Execution trace ID
  startTime: string;       // Start timestamp
  endTime?: string;        // End timestamp
}
```

## 3. Project Structure

```
services/
├── gateway/                          # API Gateway Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Configuration settings
│   │   │   ├── security.py           # Security utilities
│   │   │   ├── middleware.py         # Custom middleware
│   │   │   └── dependencies.py       # Dependency injection
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── proxy.py
│   │   │   │   └── health.py
│   │   │   └── dependencies.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── proxy_service.py
│   │   │   └── discovery_service.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   └── common.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── redis.py
│   │   │   └── session.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── exceptions.py
│   │       └── validation.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   └── test_proxy.py
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── alembic.ini
│   └── pyproject.toml
├── orchestrator/                     # Multi-Agent Orchestrator
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── events.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestration.py
│   │   │   │   ├── workflows.py
│   │   │   │   └── skills.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator_service.py
│   │   │   ├── supervisor_service.py
│   │   │   ├── skill_router_service.py
│   │   │   ├── workflow_engine_service.py
│   │   │   └── a2a_protocol_service.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── agent_registry.py
│   │   │   ├── skill_registry.py
│   │   │   ├── workflow_definition.py
│   │   │   └── execution_context.py
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── message_queue.py
│   │   │   ├── event_bus.py
│   │   │   └── persistence.py
│   │   ├── protocols/
│   │   │   ├── __init__.py
│   │   │   ├── a2a/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── message_types.py
│   │   │   │   ├── protocol_handler.py
│   │   │   │   └── communication_service.py
│   │   │   └── mcp/
│   │   │       ├── __init__.py
│   │   │       ├── client.py
│   │   │       ├── tool_registry.py
│   │   │       └── server_discovery.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py
│   │   │   ├── agent.py
│   │   │   ├── skill.py
│   │   │   └── execution.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       └── exceptions.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── agents/                           # Agent Management Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agents.py
│   │   │   │   ├── templates.py
│   │   │   │   └── executions.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── agent_service.py
│   │   │   ├── framework_adapter_service.py
│   │   │   ├── execution_service.py
│   │   │   └── template_service.py
│   │   ├── frameworks/
│   │   │   ├── __init__.py
│   │   │   ├── base/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent_interface.py
│   │   │   │   ├── framework_interface.py
│   │   │   │   └── adapter_base.py
│   │   │   ├── langchain/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── langchain_adapter.py
│   │   │   │   ├── langchain_agent.py
│   │   │   │   └── langchain_tools.py
│   │   │   ├── llamaindex/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── llamaindex_adapter.py
│   │   │   │   ├── llamaindex_agent.py
│   │   │   │   └── llamaindex_tools.py
│   │   │   ├── crewai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── crewai_adapter.py
│   │   │   │   ├── crewai_agent.py
│   │   │   │   └── crewai_crew.py
│   │   │   └── semantic_kernel/
│   │   │       ├── __init__.py
│   │   │       ├── sk_adapter.py
│   │   │       ├── sk_agent.py
│   │   │       └── sk_plugins.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── skill.py
│   │   │   ├── execution.py
│   │   │   └── template.py
│   │   ├── repository/
│   │   │   ├── __init__.py
│   │   │   ├── agent_repository.py
│   │   │   ├── execution_repository.py
│   │   │   └── template_repository.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── performance.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── tools/                            # Tool Integration Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tools.py
│   │   │   │   ├── mcp.py
│   │   │   │   └── executions.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── tool_service.py
│   │   │   ├── mcp_service.py
│   │   │   ├── execution_service.py
│   │   │   └── registry_service.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── mcp/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── mcp_client.py
│   │   │   │   ├── server_discovery.py
│   │   │   │   ├── tool_mapper.py
│   │   │   │   └── protocol_handler.py
│   │   │   ├── standard/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file_tools.py
│   │   │   │   ├── web_tools.py
│   │   │   │   ├── math_tools.py
│   │   │   │   └── utility_tools.py
│   │   │   └── custom/
│   │   │       ├── __init__.py
│   │   │       ├── tool_loader.py
│   │   │       ├── execution_sandbox.py
│   │   │       └── security_validator.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── tool.py
│   │   │   ├── mcp_server.py
│   │   │   └── execution.py
│   │   └── repository/
│   │       ├── __init__.py
│   │       ├── tool_repository.py
│   │       └── mcp_server_repository.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── rag/                              # RAG Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── indexes.py
│   │   │   │   ├── search.py
│   │   │   │   └── qa.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── search_service.py
│   │   │   └── qa_service.py
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── text_processor.py
│   │   │   ├── pdf_processor.py
│   │   │   ├── docx_processor.py
│   │   │   ├── html_processor.py
│   │   │   └── markdown_processor.py
│   │   ├── vector_stores/
│   │   │   ├── __init__.py
│   │   │   ├── base_store.py
│   │   │   ├── pinecone_store.py
│   │   │   ├── weaviate_store.py
│   │   │   ├── chroma_store.py
│   │   │   └── postgres_store.py
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   ├── openai_embeddings.py
│   │   │   ├── huggingface_embeddings.py
│   │   │   └── azure_embeddings.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   ├── index.py
│   │   │   └── search_result.py
│   │   └── repository/
│   │       ├── __init__.py
│   │       ├── document_repository.py
│   │       └── index_repository.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── sqltool/                          # SQL Tool Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── connections.py
│   │   │   │   ├── queries.py
│   │   │   │   └── schema.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── connection_service.py
│   │   │   ├── query_service.py
│   │   │   ├── schema_service.py
│   │   │   └── security_service.py
│   │   ├── connectors/
│   │   │   ├── __init__.py
│   │   │   ├── base_connector.py
│   │   │   ├── postgres_connector.py
│   │   │   ├── mysql_connector.py
│   │   │   ├── mssql_connector.py
│   │   │   ├── oracle_connector.py
│   │   │   └── sqlite_connector.py
│   │   ├── query_builders/
│   │   │   ├── __init__.py
│   │   │   ├── sql_builder.py
│   │   │   ├── query_parser.py
│   │   │   ├── query_validator.py
│   │   │   └── result_formatter.py
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── sql_sanitizer.py
│   │   │   ├── permission_validator.py
│   │   │   └── audit_logger.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── query.py
│   │   │   └── schema.py
│   │   └── repository/
│   │       ├── __init__.py
│   │       ├── connection_repository.py
│   │       └── query_repository.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── workflow_engine/                  # Workflow Execution Engine
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── executions.py
│   │   │   │   ├── templates.py
│   │   │   │   └── monitoring.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── execution_service.py
│   │   │   ├── scheduler_service.py
│   │   │   ├── state_service.py
│   │   │   └── monitoring_service.py
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── workflow_engine.py
│   │   │   ├── node_executor.py
│   │   │   ├── condition_evaluator.py
│   │   │   ├── parallel_executor.py
│   │   │   └── error_handler.py
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── base_node.py
│   │   │   ├── agent_node.py
│   │   │   ├── tool_node.py
│   │   │   ├── condition_node.py
│   │   │   ├── parallel_node.py
│   │   │   └── merge_node.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py
│   │   │   ├── execution.py
│   │   │   ├── node.py
│   │   │   └── edge.py
│   │   └── repository/
│   │       ├── __init__.py
│   │       ├── workflow_repository.py
│   │       └── execution_repository.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
└── observability/                    # Observability Service
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   └── dependencies.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── v1/
    │   │   │   ├── __init__.py
    │   │   │   ├── traces.py
    │   │   │   ├── metrics.py
    │   │   │   ├── logs.py
    │   │   │   └── health.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── trace_service.py
    │   │   ├── metric_service.py
    │   │   ├── log_service.py
    │   │   ├── health_service.py
    │   │   └── alert_service.py
    │   ├── collectors/
    │   │   ├── __init__.py
    │   │   ├── trace_collector.py
    │   │   ├── metric_collector.py
    │   │   ├── log_collector.py
    │   │   └── event_collector.py
    │   ├── exporters/
    │   │   ├── __init__.py
    │   │   ├── jaeger_exporter.py
    │   │   ├── prometheus_exporter.py
    │   │   ├── elasticsearch_exporter.py
    │   │   └── webhook_exporter.py
    │   ├── processors/
    │   │   ├── __init__.py
    │   │   ├── trace_processor.py
    │   │   ├── metric_processor.py
    │   │   └── log_processor.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── trace.py
    │   │   ├── span.py
    │   │   ├── metric.py
    │   │   └── log.py
    │   └── repository/
    │       ├── __init__.py
    │       ├── trace_repository.py
    │       ├── metric_repository.py
    │       └── log_repository.py
    ├── tests/
    ├── requirements.txt
    ├── Dockerfile
    └── pyproject.toml
```

## 3. Database Schema

### 3.1 Prisma Schema
```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Users and Authentication
model User {
  id          String   @id @default(cuid())
  email       String   @unique
  username    String   @unique
  firstName   String?
  lastName    String?
  role        UserRole @default(USER)
  isActive    Boolean  @default(true)
  lastLoginAt DateTime?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  // Relations
  workflows     Workflow[]
  sessions      Session[]
  conversations Conversation[]

  @@map("users")
}

model Session {
  id        String   @id @default(cuid())
  userId    String
  token     String   @unique
  expiresAt DateTime
  createdAt DateTime @default(now())

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

enum UserRole {
  ADMIN
  USER
  VIEWER
}

// Agents
model Agent {
  id          String      @id @default(cuid())
  name        String
  description String?
  framework   Framework
  skills      String[]
  config      Json        @default("{}")
  systemPrompt String?
  status      AgentStatus @default(ACTIVE)
  version     String      @default("1.0.0")
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt

  // Relations
  executions     AgentExecution[]
  workflowNodes  WorkflowNode[]
  conversations  ConversationMessage[]

  @@map("agents")
}

model AgentTemplate {
  id            String    @id @default(cuid())
  name          String
  description   String?
  framework     Framework
  category      String
  skills        String[]
  defaultConfig Json      @default("{}")
  systemPrompt  String?
  isPublic      Boolean   @default(false)
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@map("agent_templates")
}

model AgentExecution {
  id        String            @id @default(cuid())
  agentId   String
  input     Json
  output    Json?
  status    ExecutionStatus   @default(RUNNING)
  startTime DateTime          @default(now())
  endTime   DateTime?
  duration  Int?
  traceId   String
  error     String?

  agent Agent @relation(fields: [agentId], references: [id], onDelete: Cascade)

  @@map("agent_executions")
}

enum Framework {
  LANGCHAIN
  LLAMAINDEX
  CREWAI
  SEMANTIC_KERNEL
}

enum AgentStatus {
  ACTIVE
  INACTIVE
  ERROR
}

enum ExecutionStatus {
  RUNNING
  COMPLETED
  FAILED
  CANCELLED
}

// Workflows
model Workflow {
  id          String         @id @default(cuid())
  name        String
  description String?
  definition  Json
  status      WorkflowStatus @default(DRAFT)
  version     String         @default("1.0.0")
  createdBy   String
  createdAt   DateTime       @default(now())
  updatedAt   DateTime       @updatedAt

  // Relations
  creator     User               @relation(fields: [createdBy], references: [id])
  nodes       WorkflowNode[]
  edges       WorkflowEdge[]
  executions  WorkflowExecution[]

  @@map("workflows")
}

model WorkflowNode {
  id         String   @id @default(cuid())
  workflowId String
  type       NodeType
  position   Json
  data       Json
  agentId    String?
  toolId     String?

  workflow Workflow @relation(fields: [workflowId], references: [id], onDelete: Cascade)
  agent    Agent?   @relation(fields: [agentId], references: [id])
  tool     Tool?    @relation(fields: [toolId], references: [id])

  sourceEdges WorkflowEdge[] @relation("SourceNode")
  targetEdges WorkflowEdge[] @relation("TargetNode")

  @@map("workflow_nodes")
}

model WorkflowEdge {
  id         String    @id @default(cuid())
  workflowId String
  sourceId   String
  targetId   String
  type       EdgeType  @default(DEFAULT)
  condition  String?

  workflow   Workflow     @relation(fields: [workflowId], references: [id], onDelete: Cascade)
  sourceNode WorkflowNode @relation("SourceNode", fields: [sourceId], references: [id])
  targetNode WorkflowNode @relation("TargetNode", fields: [targetId], references: [id])

  @@map("workflow_edges")
}

model WorkflowExecution {
  id          String            @id @default(cuid())
  workflowId  String
  status      ExecutionStatus   @default(RUNNING)
  input       Json
  output      Json?
  currentNode String?
  startTime   DateTime          @default(now())
  endTime     DateTime?
  traceId     String
  error       String?

  workflow Workflow @relation(fields: [workflowId], references: [id])

  @@map("workflow_executions")
}

enum WorkflowStatus {
  DRAFT
  ACTIVE
  INACTIVE
  ARCHIVED
}

enum NodeType {
  AGENT
  TOOL
  CONDITION
  PARALLEL
  MERGE
  START
  END
}

enum EdgeType {
  DEFAULT
  CONDITIONAL
}

// Tools
model Tool {
  id          String     @id @default(cuid())
  name        String
  description String?
  type        ToolType
  config      Json       @default("{}")
  parameters  Json       @default("[]")
  status      ToolStatus @default(ACTIVE)
  serverUrl   String?
  apiKey      String?
  createdAt   DateTime   @default(now())
  updatedAt   DateTime   @updatedAt

  // Relations
  executions    ToolExecution[]
  workflowNodes WorkflowNode[]
  mcpServers    MCPServer[]

  @@map("tools")
}

model MCPServer {
  id           String   @id @default(cuid())
  name         String
  url          String   @unique
  apiKey       String?
  capabilities String[]
  status       String   @default("active")
  toolId       String?
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt

  tool Tool? @relation(fields: [toolId], references: [id])

  @@map("mcp_servers")
}

model ToolExecution {
  id        String          @id @default(cuid())
  toolId    String
  input     Json
  output    Json?
  status    ExecutionStatus @default(RUNNING)
  startTime DateTime        @default(now())
  endTime   DateTime?
  duration  Int?
  traceId   String
  error     String?

  tool Tool @relation(fields: [toolId], references: [id])

  @@map("tool_executions")
}

enum ToolType {
  MCP
  SQL
  RAG
  STANDARD
  CUSTOM
}

enum ToolStatus {
  ACTIVE
  INACTIVE
  ERROR
}

// RAG Documents and Indexes
model RAGDocument {
  id             String   @id @default(cuid())
  filename       String
  originalName   String
  contentType    String
  size           Int
  content        String
  metadata       Json     @default("{}")
  embeddingModel String?
  vectorIndex    String?
  chunkCount     Int      @default(0)
  uploadedAt     DateTime @default(now())

  chunks RAGChunk[]

  @@map("rag_documents")
}

model RAGChunk {
  id         String  @id @default(cuid())
  documentId String
  content    String
  metadata   Json    @default("{}")
  embedding  Float[]
  startIndex Int
  endIndex   Int

  document RAGDocument @relation(fields: [documentId], references: [id], onDelete: Cascade)

  @@map("rag_chunks")
}

model RAGIndex {
  id             String   @id @default(cuid())
  name           String   @unique
  description    String?
  embeddingModel String
  dimensions     Int
  vectorStore    String
  config         Json     @default("{}")
  documentCount  Int      @default(0)
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  @@map("rag_indexes")
}

// SQL Connections
model SQLConnection {
  id              String   @id @default(cuid())
  name            String
  type            String   // postgres, mysql, mssql, etc.
  host            String
  port            Int
  database        String
  username        String
  passwordHash    String
  ssl             Boolean  @default(false)
  connectionPool  Json     @default("{}")
  isActive        Boolean  @default(true)
  lastTestedAt    DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  queries SQLQuery[]

  @@map("sql_connections")
}

model SQLQuery {
  id           String   @id @default(cuid())
  connectionId String
  query        String
  parameters   Json     @default("{}")
  result       Json?
  executionTime Int?
  status       String
  executedAt   DateTime @default(now())
  createdBy    String?

  connection SQLConnection @relation(fields: [connectionId], references: [id])

  @@map("sql_queries")
}

// Conversations and Chat
model Conversation {
  id         String   @id @default(cuid())
  sessionId  String   @unique
  workflowId String?
  userId     String?
  metadata   Json     @default("{}")
  status     String   @default("active")
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  user     User?                 @relation(fields: [userId], references: [id])
  messages ConversationMessage[]

  @@map("conversations")
}

model ConversationMessage {
  id             String   @id @default(cuid())
  conversationId String
  role           String   // user, assistant, agent, system
  content        String
  type           String   @default("text") // text, image, file, mermaid
  metadata       Json     @default("{}")
  agentId        String?
  toolId         String?
  timestamp      DateTime @default(now())

  conversation Conversation @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  agent        Agent?       @relation(fields: [agentId], references: [id])

  citations   Citation[]
  attachments Attachment[]

  @@map("conversation_messages")
}

model Citation {
  id        String @id @default(cuid())
  messageId String
  source    String
  title     String
  url       String?
  excerpt   String
  confidence Float  @default(0.0)

  message ConversationMessage @relation(fields: [messageId], references: [id], onDelete: Cascade)

  @@map("citations")
}

model Attachment {
  id        String @id @default(cuid())
  messageId String
  name      String
  type      String
  size      Int
  url       String

  message ConversationMessage @relation(fields: [messageId], references: [id], onDelete: Cascade)

  @@map("attachments")
}

// Observability
model ObservabilityEvent {
  id            String   @id @default(cuid())
  traceId       String
  spanId        String
  parentSpanId  String?
  operationName String
  serviceName   String
  startTime     DateTime
  endTime       DateTime?
  duration      Int?
  status        String
  tags          Json     @default("{}")
  logs          Json     @default("[]")

  @@index([traceId])
  @@index([serviceName])
  @@index([operationName])
  @@map("observability_events")
}

model SystemMetric {
  id        String   @id @default(cuid())
  name      String
  type      String   // counter, gauge, histogram
  value     Float
  labels    Json     @default("{}")
  timestamp DateTime @default(now())

  @@index([name])
  @@index([timestamp])
  @@map("system_metrics")
}

model SystemHealth {
  id           String   @id @default(cuid())
  serviceName  String   @unique
  status       String   // healthy, degraded, unhealthy
  responseTime Int
  errorRate    Float
  uptime       Float
  lastCheck    DateTime @default(now())

  @@map("system_health")
}
```

## 4. Service-Specific Implementation

### 4.1 Gateway Service Implementation

#### 4.1.1 Main Server Setup
```typescript
// services/gateway/src/server.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { authMiddleware } from './middleware/auth';
import { errorHandler } from './middleware/error-handler';
import { requestLogger } from './middleware/request-logger';
import { healthRoutes } from './routes/health';
import { authRoutes } from './routes/auth';
import { setupObservability } from './utils/observability';

const app = express();
const PORT = process.env.PORT || 3000;

// Setup observability
setupObservability('gateway-service');

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Body parsing and compression
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging
app.use(requestLogger);

// Health check (before auth)
app.use('/api/health', healthRoutes);

// Authentication routes
app.use('/api/auth', authRoutes);

// Protected routes with authentication
app.use('/api', authMiddleware);

// Service proxies
const services = {
  orchestrator: process.env.ORCHESTRATOR_URL || 'http://localhost:3002',
  agents: process.env.AGENTS_URL || 'http://localhost:3001',
  tools: process.env.TOOLS_URL || 'http://localhost:3003',
  rag: process.env.RAG_URL || 'http://localhost:3004',
  sqltool: process.env.SQLTOOL_URL || 'http://localhost:3005',
  'workflow-engine': process.env.WORKFLOW_ENGINE_URL || 'http://localhost:3006',
  observability: process.env.OBSERVABILITY_URL || 'http://localhost:3007',
};

// Setup service proxies
Object.entries(services).forEach(([service, target]) => {
  app.use(
    `/api/${service}`,
    createProxyMiddleware({
      target,
      changeOrigin: true,
      pathRewrite: {
        [`^/api/${service}`]: '/api',
      },
      onProxyReq: (proxyReq, req) => {
        // Forward user information
        if (req.user) {
          proxyReq.setHeader('X-User-ID', req.user.id);
          proxyReq.setHeader('X-User-Role', req.user.role);
        }
      },
    })
  );
});

// Error handling
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`Gateway service running on port ${PORT}`);
});
```

#### 4.1.2 Authentication Middleware
```typescript
// services/gateway/src/middleware/auth.ts
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { prisma } from '../config/database';

interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export async function authMiddleware(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
) {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
    
    const session = await prisma.session.findUnique({
      where: { token },
      include: { user: true }
    });
    
    if (!session || session.expiresAt < new Date()) {
      return res.status(401).json({ error: 'Invalid or expired token' });
    }
    
    req.user = {
      id: session.user.id,
      email: session.user.email,
      role: session.user.role
    };
    
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### 4.2 Agent Service Implementation

#### 4.2.1 Framework Adapter Base
```typescript
// services/agents/src/frameworks/base/framework.interface.ts
export interface AIFramework {
  name: string;
  version: string;
  
  initialize(config: FrameworkConfig): Promise<void>;
  createAgent(definition: AgentDefinition): Promise<FrameworkAgent>;
  executeAgent(agent: FrameworkAgent, input: AgentInput): Promise<AgentOutput>;
  getCapabilities(): FrameworkCapabilities;
  validateConfig(config: any): ValidationResult;
}

export interface FrameworkAgent {
  id: string;
  name: string;
  framework: string;
  config: any;
  tools: Tool[];
  memory?: Memory;
  
  execute(input: AgentInput): Promise<AgentOutput>;
  addTool(tool: Tool): void;
  removeTool(toolId: string): void;
  updateConfig(config: Partial<any>): void;
}

export interface AgentDefinition {
  name: string;
  description: string;
  systemPrompt: string;
  model: string;
  temperature: number;
  maxTokens: number;
  tools: string[];
  memory: boolean;
  streaming: boolean;
  skills: string[];
  [key: string]: any;
}

export interface AgentInput {
  message: string;
  context?: any;
  sessionId?: string;
  userId?: string;
  metadata?: Record<string, any>;
}

export interface AgentOutput {
  response: string;
  toolCalls?: ToolCall[];
  metadata?: Record<string, any>;
  citations?: Citation[];
  usage?: TokenUsage;
}
```

#### 4.2.2 LangChain Adapter Implementation
```typescript
// services/agents/src/frameworks/langchain/langchain.adapter.ts
import { ChatOpenAI } from '@langchain/openai';
import { ChatPromptTemplate, MessagesPlaceholder } from '@langchain/core/prompts';
import { AgentExecutor, createOpenAIFunctionsAgent } from 'langchain/agents';
import { AIFramework, FrameworkAgent, AgentDefinition } from '../base/framework.interface';
import { LangChainAgent } from './langchain.agent';

export class LangChainAdapter implements AIFramework {
  name = 'langchain';
  version = '0.1.0';
  
  async initialize(config: any): Promise<void> {
    // Initialize LangChain-specific configurations
    if (config.openaiApiKey) {
      process.env.OPENAI_API_KEY = config.openaiApiKey;
    }
  }
  
  async createAgent(definition: AgentDefinition): Promise<FrameworkAgent> {
    const model = new ChatOpenAI({
      modelName: definition.model || 'gpt-4',
      temperature: definition.temperature || 0.7,
      maxTokens: definition.maxTokens || 2000,
    });
    
    const prompt = ChatPromptTemplate.fromMessages([
      ['system', definition.systemPrompt],
      new MessagesPlaceholder('chat_history'),
      ['human', '{input}'],
      new MessagesPlaceholder('agent_scratchpad'),
    ]);
    
    // Load tools based on definition
    const tools = await this.loadTools(definition.tools);
    
    const agent = await createOpenAIFunctionsAgent({
      llm: model,
      tools,
      prompt,
    });
    
    const agentExecutor = new AgentExecutor({
      agent,
      tools,
      verbose: true,
      returnIntermediateSteps: true,
    });
    
    return new LangChainAgent({
      id: definition.name,
      name: definition.name,
      framework: this.name,
      config: definition,
      executor: agentExecutor,
      tools,
    });
  }
  
  async executeAgent(agent: FrameworkAgent, input: AgentInput): Promise<AgentOutput> {
    const langchainAgent = agent as LangChainAgent;
    return await langchainAgent.execute(input);
  }
  
  getCapabilities() {
    return {
      streaming: true,
      toolCalling: true,
      memory: true,
      multiModal: true,
      frameworks: ['openai', 'anthropic', 'huggingface'],
    };
  }
  
  validateConfig(config: any) {
    const errors: string[] = [];
    
    if (!config.model) {
      errors.push('Model is required');
    }
    
    if (config.temperature < 0 || config.temperature > 2) {
      errors.push('Temperature must be between 0 and 2');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  }
  
  private async loadTools(toolIds: string[]) {
    // Implementation to load and initialize tools
    const tools = [];
    
    for (const toolId of toolIds) {
      const tool = await this.createTool(toolId);
      if (tool) {
        tools.push(tool);
      }
    }
    
    return tools;
  }
  
  private async createTool(toolId: string) {
    // Tool creation logic based on tool ID
    // This would integrate with the tools service
    return null;
  }
}
```

### 4.3 Tools Service Implementation

#### 4.3.1 MCP Integration
```typescript
// services/tools/src/integrations/mcp/mcp-client.ts
import WebSocket from 'ws';
import { Tool, MCPServer, MCPRequest, MCPResponse } from '../../types';

export class MCPClient {
  private ws: WebSocket | null = null;
  private requestId = 0;
  private pendingRequests = new Map<number, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }>();
  
  constructor(private serverUrl: string, private apiKey?: string) {}
  
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.serverUrl, {
        headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : undefined
      });
      
      this.ws.on('open', () => {
        resolve();
      });
      
      this.ws.on('error', (error) => {
        reject(error);
      });
      
      this.ws.on('message', (data) => {
        this.handleMessage(JSON.parse(data.toString()));
      });
    });
  }
  
  async disconnect(): Promise<void> {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  async listTools(): Promise<Tool[]> {
    const response = await this.sendRequest({
      method: 'tools/list',
      params: {}
    });
    
    return response.tools.map((tool: any) => ({
      id: tool.name,
      name: tool.name,
      description: tool.description,
      type: 'mcp' as const,
      parameters: tool.inputSchema?.properties || {},
      config: {
        serverUrl: this.serverUrl,
        method: tool.name
      }
    }));
  }
  
  async executeTool(toolName: string, parameters: any): Promise<any> {
    const response = await this.sendRequest({
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: parameters
      }
    });
    
    return response.content;
  }
  
  private async sendRequest(request: MCPRequest): Promise<MCPResponse> {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket not connected'));
        return;
      }
      
      const id = ++this.requestId;
      const message = {
        jsonrpc: '2.0',
        id,
        ...request
      };
      
      this.pendingRequests.set(id, { resolve, reject });
      this.ws.send(JSON.stringify(message));
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }
  
  private handleMessage(message: any): void {
    if (message.id && this.pendingRequests.has(message.id)) {
      const { resolve, reject } = this.pendingRequests.get(message.id)!;
      this.pendingRequests.delete(message.id);
      
      if (message.error) {
        reject(new Error(message.error.message));
      } else {
        resolve(message.result);
      }
    }
  }
}
```

### 4.4 Orchestrator Service Implementation

#### 4.4.1 A2A Protocol Handler
```typescript
// services/orchestrator/src/protocols/a2a/protocol.handler.ts
import { EventEmitter } from 'events';
import { A2AMessage, A2AProtocol } from './message.types';
import { RedisClient } from '../../infrastructure/redis';
import { Logger } from '../../utils/logger';

export class A2AProtocolHandler extends EventEmitter implements A2AProtocol {
  private redis: RedisClient;
  private logger: Logger;
  private subscribers = new Map<string, Set<(message: A2AMessage) => void>>();
  
  constructor(redis: RedisClient, logger: Logger) {
    super();
    this.redis = redis;
    this.logger = logger;
    
    // Setup Redis pub/sub for distributed messaging
    this.setupRedisSubscription();
  }
  
  async sendMessage(message: A2AMessage): Promise<void> {
    try {
      // Add tracing information
      message.traceId = message.traceId || this.generateTraceId();
      message.timestamp = new Date();
      
      // Validate message
      this.validateMessage(message);
      
      // Log the message
      this.logger.info('Sending A2A message', {
        from: message.from,
        to: message.to,
        type: message.type,
        traceId: message.traceId
      });
      
      // Send via Redis pub/sub
      await this.redis.publish(`a2a:${message.to}`, JSON.stringify(message));
      
      // Emit local event
      this.emit('message:sent', message);
      
    } catch (error) {
      this.logger.error('Failed to send A2A message', { error, message });
      throw error;
    }
  }
  
  subscribe(agentId: string, handler: (message: A2AMessage) => void): void {
    if (!this.subscribers.has(agentId)) {
      this.subscribers.set(agentId, new Set());
    }
    
    this.subscribers.get(agentId)!.add(handler);
    
    // Subscribe to Redis channel for this agent
    this.redis.subscribe(`a2a:${agentId}`);
  }
  
  unsubscribe(agentId: string, handler: (message: A2AMessage) => void): void {
    const handlers = this.subscribers.get(agentId);
    if (handlers) {
      handlers.delete(handler);
      
      if (handlers.size === 0) {
        this.subscribers.delete(agentId);
        this.redis.unsubscribe(`a2a:${agentId}`);
      }
    }
  }
  
  async broadcast(message: Omit<A2AMessage, 'to'>): Promise<void> {
    const broadcastMessage: A2AMessage = {
      ...message,
      to: '*',
      traceId: message.traceId || this.generateTraceId(),
      timestamp: new Date()
    };
    
    this.logger.info('Broadcasting A2A message', {
      from: message.from,
      type: message.type,
      traceId: broadcastMessage.traceId
    });
    
    await this.redis.publish('a2a:broadcast', JSON.stringify(broadcastMessage));
  }
  
  private setupRedisSubscription(): void {
    this.redis.onMessage((channel: string, message: string) => {
      try {
        const parsedMessage: A2AMessage = JSON.parse(message);
        
        if (channel === 'a2a:broadcast') {
          // Handle broadcast messages
          this.handleBroadcastMessage(parsedMessage);
        } else {
          // Handle direct messages
          const agentId = channel.replace('a2a:', '');
          this.handleDirectMessage(agentId, parsedMessage);
        }
        
      } catch (error) {
        this.logger.error('Failed to parse A2A message', { error, channel, message });
      }
    });
  }
  
  private handleDirectMessage(agentId: string, message: A2AMessage): void {
    const handlers = this.subscribers.get(agentId);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          this.logger.error('Error in A2A message handler', { error, agentId, message });
        }
      });
    }
    
    this.emit('message:received', message);
  }
  
  private handleBroadcastMessage(message: A2AMessage): void {
    // Deliver to all subscribed agents except the sender
    this.subscribers.forEach((handlers, agentId) => {
      if (agentId !== message.from) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            this.logger.error('Error in broadcast handler', { error, agentId, message });
          }
        });
      }
    });
    
    this.emit('message:broadcast', message);
  }
  
  private validateMessage(message: A2AMessage): void {
    if (!message.from) {
      throw new Error('Message must have a "from" field');
    }
    
    if (!message.to) {
      throw new Error('Message must have a "to" field');
    }
    
    if (!message.type) {
      throw new Error('Message must have a "type" field');
    }
    
    if (!['request', 'response', 'broadcast'].includes(message.type)) {
      throw new Error('Invalid message type');
    }
  }
  
  private generateTraceId(): string {
    return `a2a-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

### 4.5 Observability Service Implementation

#### 4.5.1 OpenTelemetry Setup
```typescript
// services/observability/src/utils/telemetry.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';

export function setupTelemetry(serviceName: string) {
  const jaegerExporter = new JaegerExporter({
    endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
  });
  
  const prometheusExporter = new PrometheusExporter({
    port: parseInt(process.env.PROMETHEUS_PORT || '9090'),
  });
  
  const sdk = new NodeSDK({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
      [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
    }),
    traceExporter: jaegerExporter,
    metricReader: new PeriodicExportingMetricReader({
      exporter: prometheusExporter,
      exportIntervalMillis: 1000,
    }),
    instrumentations: [getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-http': {
        enabled: true,
        ignoreIncomingRequestHook: (req) => {
          return req.url?.includes('/health') || false;
        },
      },
      '@opentelemetry/instrumentation-express': {
        enabled: true,
      },
      '@opentelemetry/instrumentation-redis': {
        enabled: true,
      },
    })],
  });
  
  sdk.start();
  
  return sdk;
}
```

This comprehensive backend specification provides detailed implementation guidance for each service. Teams can use these specifications with GitHub Copilot to build robust, scalable microservices that work together to create the complete Agentic AI Acceleration.
