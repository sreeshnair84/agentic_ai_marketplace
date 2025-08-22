# Backend Services - Technical Specifications

## Overview

The Enterprise AI Platform consists of 8 core backend services built with FastAPI, each designed for specific functionality while maintaining seamless integration through the A2A (Agent-to-Agent) protocol.

## Service Inventory

| Service | Port | Framework | Purpose | A2A Enabled |
|---------|------|-----------|---------|-------------|
| Gateway | 8000 | FastAPI | API Gateway & Auth | ❌ |
| Agents | 8002 | FastAPI | AI Agent Management | ✅ |
| Orchestrator | 8003 | FastAPI | A2A Core & Workflows | ✅ |
| RAG | 8004 | FastAPI | Vector Search & Retrieval | ✅ |
| Tools | 8005 | FastAPI | MCP Tool Integration | ✅ |
| SQL Tool | 8006 | FastAPI | Database Operations | ❌ |
| Workflow Engine | 8007 | FastAPI | Process Automation | ❌ |
| Observability | 8008 | FastAPI | Monitoring & Tracing | ❌ |

## 1. Gateway Service (Port: 8000)

### Primary Responsibilities
- **Authentication & Authorization**: JWT-based auth with multiple providers
- **Request Routing**: Proxy requests to appropriate microservices
- **CORS Management**: Frontend domain configuration
- **Rate Limiting**: API protection and throttling
- **Input Validation**: Request sanitization and validation

### Key Dependencies
```txt
fastapi[all]
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
python-jose[cryptography]
passlib[bcrypt]
aioredis
httpx
```

### Environment Variables
```bash
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-secret-key-here
CORS_ORIGINS_STR=http://localhost:3000,*
```

### API Endpoints
```
POST   /auth/login          # User authentication
POST   /auth/register       # User registration
POST   /auth/refresh        # Token refresh
GET    /auth/me            # Current user info
POST   /auth/logout        # User logout
GET    /health             # Service health
```

### Architecture Pattern
```python
app/
├── main.py              # FastAPI application
├── api/
│   ├── auth.py         # Authentication routes
│   ├── users.py        # User management
│   └── proxy.py        # Service proxy routes
├── core/
│   ├── config.py       # Configuration
│   ├── security.py     # JWT & password handling
│   └── database.py     # Database connection
├── models/
│   ├── user.py         # User models
│   └── auth.py         # Auth models
└── services/
    ├── auth_service.py # Business logic
    └── user_service.py # User operations
```

## 2. Agents Service (Port: 8002)

### Primary Responsibilities
- **Agent Lifecycle Management**: Create, update, delete AI agents
- **Framework Integration**: LangChain, CrewAI, Semantic Kernel support
- **LLM Provider Management**: OpenAI, Google, Anthropic integration
- **A2A Protocol**: Agent capability registration and communication
- **Agent Execution**: Task processing and response generation

### Key Dependencies
```txt
fastapi[all]
langchain
langchain-core
langchain-community
crewai
semantic-kernel
autogen-agentchat
openai
anthropic
google-generativeai
websockets
aioredis
```

### A2A Protocol Implementation
```python
@dataclass
class AgentCapability:
    name: str
    description: str
    input_schema: Dict
    output_schema: Dict

@dataclass
class AgentCard:
    id: str
    name: str
    capabilities: List[AgentCapability]
    endpoints: Dict[str, str]
    health_url: str
    
# A2A Message Handler
async def handle_a2a_message(message: A2AMessage) -> A2AResponse:
    if message.method == "execute_task":
        return await execute_agent_task(message.params)
    elif message.method == "get_capabilities":
        return await get_agent_capabilities()
```

### API Endpoints
```
GET    /agents              # List all agents
POST   /agents              # Create new agent
GET    /agents/{id}         # Get agent details
PUT    /agents/{id}         # Update agent
DELETE /agents/{id}         # Delete agent
POST   /agents/{id}/execute # Execute agent task
GET    /agents/{id}/capabilities # A2A capabilities
POST   /a2a/message         # A2A message endpoint
```

## 3. Orchestrator Service (Port: 8003)

### Primary Responsibilities
- **A2A Protocol Core**: Central message routing and coordination
- **Multi-Agent Workflows**: Complex agent interaction patterns
- **Capability Discovery**: Agent capability registry
- **Message Queuing**: Reliable message delivery
- **Workflow Coordination**: Step-by-step execution management

### Key Dependencies
```txt
fastapi[all]
langchain
redis[hiredis]
aioredis
httpx
temporalio
prefect
pika  # RabbitMQ client
tenacity
croniter
```

### A2A Message Routing
```python
class A2AOrchestrator:
    def __init__(self):
        self.agent_registry: Dict[str, AgentCard] = {}
        self.message_queue = asyncio.Queue()
    
    async def register_agent(self, agent_card: AgentCard):
        self.agent_registry[agent_card.id] = agent_card
    
    async def route_message(self, target_agent: str, message: A2AMessage):
        if target_agent in self.agent_registry:
            agent = self.agent_registry[target_agent]
            return await self.send_http_message(agent.endpoints["a2a"], message)
```

### API Endpoints
```
POST   /orchestrator/register   # Register agent
POST   /orchestrator/message    # Send A2A message
GET    /orchestrator/agents     # List registered agents
POST   /workflows/execute       # Execute workflow
GET    /workflows/{id}/status   # Workflow status
```

## 4. RAG Service (Port: 8004)

### Primary Responsibilities
- **Document Processing**: PDF, DOCX, TXT ingestion
- **Vector Embeddings**: Text-to-vector conversion
- **Semantic Search**: Vector similarity search
- **Context Retrieval**: Relevant document chunk retrieval
- **A2A Integration**: RAG capabilities for other agents

### Key Dependencies
```txt
fastapi
pgvector
psycopg2-binary
asyncpg
sqlalchemy[asyncio]
sentence-transformers
numpy
openai
google-generativeai
pypdf
python-docx
aiofiles
```

### Vector Processing Pipeline
```python
class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = PGVectorStore()
    
    async def process_document(self, document: UploadFile):
        # 1. Extract text
        text = await self.extract_text(document)
        
        # 2. Chunk document
        chunks = self.chunk_text(text)
        
        # 3. Generate embeddings
        embeddings = self.embedding_model.encode(chunks)
        
        # 4. Store in vector database
        await self.vector_store.store_embeddings(chunks, embeddings)
    
    async def similarity_search(self, query: str, k: int = 5):
        query_embedding = self.embedding_model.encode([query])
        return await self.vector_store.similarity_search(query_embedding, k)
```

### API Endpoints
```
POST   /rag/documents          # Upload document
GET    /rag/documents          # List documents
POST   /rag/query              # Semantic search
DELETE /rag/documents/{id}     # Delete document
GET    /rag/embeddings/stats   # Embedding statistics
```

## 5. Tools Service (Port: 8005)

### Primary Responsibilities
- **MCP Integration**: Model Context Protocol server management
- **Tool Registry**: External tool discovery and registration
- **Tool Execution**: Secure tool invocation
- **Capability Management**: Tool capability exposure via A2A
- **Integration Hub**: Connect with external APIs and services

### Key Dependencies
```txt
fastapi[all]
httpx
aiohttp
mcp-client  # Model Context Protocol
websockets
aioredis
pydantic-extra-types
```

### MCP Integration
```python
class MCPToolService:
    def __init__(self):
        self.mcp_servers: Dict[str, MCPServer] = {}
        self.tool_registry: Dict[str, ToolCapability] = {}
    
    async def register_mcp_server(self, server_url: str):
        server = MCPServer(server_url)
        await server.connect()
        capabilities = await server.list_capabilities()
        
        for capability in capabilities:
            self.tool_registry[capability.name] = capability
            
    async def execute_tool(self, tool_name: str, params: Dict):
        if tool_name in self.tool_registry:
            server = self.get_server_for_tool(tool_name)
            return await server.execute_tool(tool_name, params)
```

### API Endpoints
```
GET    /tools                  # List all tools
POST   /tools                  # Register new tool
POST   /tools/{id}/execute     # Execute tool
GET    /tools/mcp/servers      # List MCP servers
POST   /tools/mcp/register     # Register MCP server
```

## 6. SQL Tool Service (Port: 8006)

### Primary Responsibilities
- **Database Connectivity**: Multi-database support (PostgreSQL, MySQL, SQLite, MSSQL)
- **Schema Introspection**: Database structure analysis
- **Query Execution**: Safe SQL query processing
- **Query Optimization**: Performance analysis and suggestions
- **Security**: SQL injection prevention and access control

### Key Dependencies
```txt
fastapi[all]
sqlalchemy[asyncio]
asyncpg
aiomysql
aiosqlite
aioodbc
psycopg2-binary
```

### Database Manager
```python
class DatabaseManager:
    def __init__(self):
        self.connections: Dict[str, AsyncEngine] = {}
        
    async def add_connection(self, name: str, connection_string: str):
        engine = create_async_engine(connection_string)
        self.connections[name] = engine
        
    async def execute_query(self, connection_name: str, query: str):
        if connection_name not in self.connections:
            raise ValueError(f"Connection {connection_name} not found")
            
        engine = self.connections[connection_name]
        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            return result.fetchall()
```

### API Endpoints
```
POST   /sql/connections        # Add database connection
GET    /sql/connections        # List connections
POST   /sql/execute            # Execute SQL query
GET    /sql/schema/{conn}      # Get database schema
POST   /sql/explain            # Query execution plan
```

## 7. Workflow Engine (Port: 8007)

### Primary Responsibilities
- **Workflow Definition**: Visual workflow creation and management
- **Step Execution**: Sequential and parallel task processing
- **Conditional Logic**: Decision-based workflow branching
- **Integration**: Agent and tool integration within workflows
- **State Management**: Workflow execution state tracking

### Key Dependencies
```txt
fastapi[all]
temporalio
prefect
celery[redis]
aioredis
sqlalchemy[asyncio]
croniter
```

### Workflow Execution Engine
```python
class WorkflowEngine:
    def __init__(self):
        self.executor = WorkflowExecutor()
        self.state_manager = WorkflowStateManager()
        
    async def execute_workflow(self, workflow_id: str, input_data: Dict):
        workflow = await self.get_workflow_definition(workflow_id)
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            input_data=input_data,
            status="running"
        )
        
        for step in workflow.steps:
            try:
                result = await self.execute_step(step, execution.variables)
                execution.step_results[step.id] = result
                execution.variables.update(result.get("variables", {}))
            except Exception as e:
                execution.status = "failed"
                execution.error_message = str(e)
                break
        
        execution.status = "completed"
        return execution
```

### API Endpoints
```
GET    /workflows              # List workflows
POST   /workflows              # Create workflow
PUT    /workflows/{id}         # Update workflow
POST   /workflows/{id}/execute # Execute workflow
GET    /workflows/{id}/status  # Execution status
```

## 8. Observability Service (Port: 8008)

### Primary Responsibilities
- **Distributed Tracing**: OpenTelemetry trace collection
- **Metrics Collection**: Prometheus metrics aggregation
- **A2A Monitoring**: Agent communication flow tracking
- **Performance Analytics**: Service performance analysis
- **Alerting**: Threshold-based alerting and notifications

### Key Dependencies
```txt
fastapi[all]
opentelemetry-api
opentelemetry-sdk
opentelemetry-instrumentation-fastapi
opentelemetry-exporter-jaeger
prometheus-client
structlog
python-json-logger
psutil
```

### Observability Architecture
```python
class ObservabilityService:
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self.metrics_registry = prometheus_client.CollectorRegistry()
        
    async def record_trace(self, trace_data: TraceData):
        with self.tracer.start_as_current_span(trace_data.operation_name) as span:
            span.set_attributes(trace_data.attributes)
            await self.store_trace(trace_data)
            
    async def record_a2a_message(self, message: A2AMessage, response: A2AResponse):
        trace_data = TraceData(
            operation_name="a2a_message",
            attributes={
                "method": message.method,
                "agent_from": message.sender,
                "agent_to": message.receiver,
                "duration": response.duration_ms
            }
        )
        await self.record_trace(trace_data)
```

### API Endpoints
```
GET    /observability/traces   # Get trace data
GET    /observability/metrics  # Get metrics
POST   /observability/traces   # Submit trace
GET    /observability/health   # Service health
GET    /observability/a2a      # A2A message flows
```

## Service Communication Patterns

### 1. A2A (Agent-to-Agent) Communication
```python
# Message format
{
    "jsonrpc": "2.0",
    "method": "execute_task",
    "params": {
        "task": "analyze_document",
        "context": {"document_id": "123"},
        "requirements": ["summarization", "key_points"]
    },
    "id": "req-456"
}
```

### 2. HTTP Service-to-Service
```python
# Internal service calls
async def call_rag_service(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://rag:8004/rag/query",
            json={"query": query, "k": 5}
        )
        return response.json()
```

### 3. Redis Pub/Sub for Real-time Updates
```python
# Publishing updates
await redis_client.publish("agent_status", json.dumps({
    "agent_id": "agent-123",
    "status": "executing",
    "task": "document_analysis"
}))
```

## Database Schema Integration

### Shared Tables
- `agents` - Agent definitions and configurations
- `tools` - Tool registry and configurations
- `workflows` - Workflow definitions
- `workflow_executions` - Execution state and results
- `users` - User management and authentication
- `projects` - Project organization

### Service-Specific Tables
- `rag_documents` - Document storage and metadata
- `observability_traces` - Trace data storage
- `tool_instances` - Tool instance configurations

## Security Considerations

### Authentication
- JWT tokens for API access
- Service-to-service authentication
- Role-based access control (RBAC)

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- Rate limiting and throttling
- Secure API key management

### Network Security
- Internal service communication encryption
- CORS configuration
- Request/response logging

## Performance Optimization

### Async/Await Pattern
All services use async/await for non-blocking I/O operations.

### Connection Pooling
Database and Redis connections use connection pooling for efficiency.

### Caching Strategy
- Redis for frequent data access
- In-memory caching for static data
- Query result caching

### Load Balancing
Services designed for horizontal scaling with load balancers.

## Current Implementation Status

### ✅ Fully Implemented Services
- **Gateway Service**: Complete with A2A chat, WebSocket support, MCP integration
- **Agents Service**: Agent management with A2A protocol, multiple AI providers
- **Tools Service**: MCP integration, tool execution, comprehensive tool library
- **Workflow Engine**: Basic workflow execution and management

### ⚠️ Partially Implemented Services  
- **Orchestrator Service**: A2A core implemented, workflow coordination needs enhancement
- **RAG Service**: Basic vector search, needs optimization
- **Observability Service**: Basic monitoring, needs comprehensive tracing

### 🔧 Services Needing Enhancement
- **SQL Tool Service**: Basic implementation, needs advanced features

### 🆕 New Features Discovered
- **Enhanced A2A Chat**: WebSocket-based real-time communication with streaming
- **Comprehensive MCP Support**: Full Model Context Protocol integration
- **Agent Template System**: Template-based agent creation and management
- **Advanced Tool Pipeline**: RAG pipeline builder, physical tool tester

## Technology Stack Summary

### Core Technologies
- **Backend Framework**: FastAPI with async/await
- **Database**: PostgreSQL with async SQLAlchemy
- **Vector Database**: PGVector extension
- **Message Queue**: Redis with async support
- **AI Frameworks**: LangChain, CrewAI, Semantic Kernel, AutoGen
- **AI Providers**: OpenAI, Google Gemini, Anthropic Claude

### Communication Protocols
- **A2A Protocol**: JSON-RPC 2.0 over HTTP/WebSocket
- **MCP Protocol**: Model Context Protocol for tool integration
- **WebSocket**: Real-time bidirectional communication
- **HTTP/2**: High-performance API communication

### Monitoring & Observability
- **OpenTelemetry**: Distributed tracing
- **Prometheus**: Metrics collection
- **Structured Logging**: JSON-based logging with correlation IDs

This backend architecture provides a robust, scalable foundation for enterprise AI applications with comprehensive A2A protocol support, real-time communication, and extensive tool integration capabilities.
