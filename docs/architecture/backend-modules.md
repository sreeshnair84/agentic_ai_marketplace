# Backend Modules Architecture Documentation

## Overview
This document outlines the comprehensive architecture of the backend modules for the Agentic AI Acceleration. The platform is designed to facilitate sophisticated Agent-to-Agent (A2A) protocol interactions, MCP (Model Context Protocol) integrations, and enterprise-grade multi-agent orchestration. The backend follows a microservices architecture with dedicated services for each domain, enabling high scalability, maintainability, and independent deployment.

## System Architecture Overview
The Agentic AI Acceleration consists of 8 core services communicating through A2A protocol, REST APIs, and event-driven messaging:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Gateway       │    │  Observability  │
│   (Next.js)     │◄──►│   Service       │◄──►│    Service      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8008    │
└─────────────────┘    └─────────┬───────┘    └─────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
       ┌────────▼────────┐ ┌─────▼──────┐ ┌─────▼──────┐
       │   Orchestrator  │ │   Agents   │ │   Tools    │
       │    Service      │ │  Service   │ │  Service   │
       │   Port: 8003    │ │ Port: 8002 │ │ Port: 8005 │
       └────────┬────────┘ └─────┬──────┘ └─────┬──────┘
                │                │              │
       ┌────────▼────────┐ ┌─────▼──────┐ ┌─────▼──────┐
       │   Workflow      │ │    RAG     │ │ SQL Tool   │
       │   Engine        │ │  Service   │ │  Service   │
       │   Port: 8007    │ │ Port: 8004 │ │ Port: 8006 │
       └─────────────────┘ └────────────┘ └────────────┘
                │                │              │
       ┌────────▼────────────────▼──────────────▼──────┐
       │            Data Layer                         │
       │  PostgreSQL  │  Redis  │  ChromaDB │ Vector │
       │  Port: 5432  │ Port:   │ Port: 8000│   DB   │
       │              │  6379   │           │ Port:  │
       │              │         │           │ 8010   │
       └───────────────────────────────────────────────┘
```

## Modules Breakdown

### 1. Gateway Service (Port: 8000)
- **Purpose**: Acts as the unified API gateway, handling authentication, request routing, rate limiting, and CORS management.
- **A2A Protocol Role**: Central hub for A2A message routing and authentication
- **Key Components**:
  - **Request Router**: Routes requests to appropriate backend services
  - **Authentication Manager**: JWT-based authentication with refresh token support
  - **Rate Limiter**: Prevents API abuse and ensures fair usage
  - **A2A Message Gateway**: Routes A2A protocol messages between services
  - **Health Check Aggregator**: Aggregates health status from all services
- **Technologies**: FastAPI, SQLAlchemy, Redis, JWT
- **Database Schema**: Users, sessions, API keys, rate limit counters
- **Endpoints**:
  - `POST /auth/login`: User authentication
  - `POST /auth/refresh`: Token refresh
  - `GET /health`: Aggregated system health
  - `GET /health/detailed`: Detailed service health status
  - `POST /a2a/route`: A2A message routing
  - `GET /api/services`: Available service discovery

### 2. Agents Service (Port: 8002) - A2A Enhanced
- **Purpose**: Manages the complete lifecycle of AI agents with A2A protocol implementation, including creation, registration, execution, and inter-agent communication.
- **A2A Protocol Role**: Primary agent registration and communication hub
- **Key Components**:
  - **Agent Registry**: Maintains comprehensive agent cards with capabilities, inputs/outputs, and metadata
  - **A2A Protocol Engine**: Implements JSON-RPC 2.0 based A2A communication
  - **Agent Execution Context**: Provides secure sandboxed execution environment
  - **Framework Adapters**: Supports LangChain, LlamaIndex, CrewAI, and custom frameworks
  - **Capability Manager**: Dynamic capability registration and discovery
  - **Message Router**: Routes A2A messages between agents based on capabilities
- **Technologies**: FastAPI, LangChain, LlamaIndex, CrewAI, Redis (A2A), WebSockets
- **Database Schema**: 
  ```sql
  - agent_cards: A2A agent card definitions
  - agent_capabilities: Dynamic capability definitions
  - a2a_messages: Message logs and routing history
  - agent_executions: Execution logs and performance metrics
  - agent_collaborations: Inter-agent collaboration patterns
  ```
- **Enhanced Endpoints**:
  - `POST /api/agents`: Create new agent with A2A registration
  - `PUT /api/agents/:id`: Update agent and refresh A2A card
  - `GET /api/agents`: List agents with capability filtering
  - `POST /api/agents/:id/execute`: Execute agent with A2A context
  - `GET /a2a/cards`: List all agent cards for discovery
  - `POST /a2a/discover`: Semantic agent discovery
  - `POST /a2a/message`: Send A2A message to agent
  - `GET /a2a/message/stream`: WebSocket A2A message stream
  - `GET /api/agents/:id/capabilities`: Get agent capabilities
  - `POST /api/agents/:id/collaborate`: Initiate agent collaboration

### 3. Orchestrator Service (Port: 8003) - A2A Core
- **Purpose**: Central orchestration engine for complex multi-agent workflows with sophisticated A2A protocol coordination.
- **A2A Protocol Role**: Workflow orchestrator and agent coordination manager
- **Key Components**:
  - **Workflow Supervisor**: Orchestrates complex multi-agent interactions
  - **A2A Coordinator**: Manages agent-to-agent communication patterns
  - **Skill Router**: Intelligent routing based on agent capabilities and current load
  - **Execution Planner**: Plans optimal execution paths for multi-step workflows
  - **Context Manager**: Maintains conversation and execution context across agents
  - **Conflict Resolver**: Handles conflicts in agent responses and collaboration
- **Technologies**: FastAPI, Celery, Redis (coordination), A2A Protocol
- **Database Schema**:
  ```sql
  - orchestration_sessions: Active orchestration sessions
  - agent_assignments: Agent-to-task assignments
  - workflow_state: Real-time workflow execution state
  - collaboration_patterns: Learned collaboration patterns
  - context_store: Shared context between agents
  ```
- **Enhanced Endpoints**:
  - `POST /api/orchestrate`: Start new orchestration session
  - `GET /api/orchestrate/:id`: Get orchestration status
  - `POST /api/workflows`: Create workflow with A2A agents
  - `POST /api/workflows/:id/execute`: Execute workflow with orchestration
  - `GET /api/sessions/:id/agents`: Get assigned agents
  - `POST /api/coordinate`: Manual agent coordination
  - `GET /a2a/network`: Network topology visualization
  - `POST /a2a/broadcast`: Broadcast message to multiple agents

### 4. RAG Service (Port: 8004) - Vector Enhanced
- **Purpose**: Advanced Retrieval Augmented Generation with vector search, document processing, and A2A integration.
- **A2A Protocol Role**: Knowledge provider agent with semantic search capabilities
- **Key Components**:
  - **Document Parser**: Multi-format document ingestion (PDF, DOCX, TXT, MD, etc.)
  - **Vector Store Manager**: ChromaDB integration with multiple collections
  - **Embedding Engine**: Multiple embedding model support (OpenAI, Google, local)
  - **Semantic Search**: Advanced similarity and hybrid search
  - **A2A Knowledge Interface**: Exposes knowledge as A2A agent capability
  - **Index Manager**: Dynamic index creation and optimization
- **Technologies**: FastAPI, ChromaDB, OpenAI Embeddings, Sentence Transformers
- **Database Schema**:
  ```sql
  - documents: Document metadata and references
  - vector_collections: ChromaDB collection management
  - embedding_models: Configured embedding models
  - search_sessions: Search session history
  - knowledge_graphs: Document relationship graphs
  ```
- **Enhanced Endpoints**:
  - `POST /api/documents`: Upload and index documents
  - `GET /api/documents`: List indexed documents with metadata
  - `POST /api/search/semantic`: Semantic similarity search
  - `POST /api/search/hybrid`: Hybrid keyword + semantic search
  - `POST /api/query`: Natural language Q&A
  - `GET /api/collections`: List vector collections
  - `POST /api/collections`: Create new collection
  - `POST /a2a/ask`: A2A knowledge query interface
  - `GET /api/documents/:id/insights`: Document insights and summaries
  - `POST /api/index/optimize`: Optimize vector indexes

### 5. Tools Service (Port: 8005) - MCP Integration
- **Purpose**: Comprehensive tool management with MCP (Model Context Protocol) integration, external tool discovery, and A2A tool exposure.
- **A2A Protocol Role**: Tool provider agent with dynamic capability exposure
- **Key Components**:
  - **MCP Client Manager**: Connects to external MCP servers
  - **Tool Registry**: Centralizes all available tools with metadata
  - **Execution Engine**: Secure tool execution with sandboxing
  - **A2A Tool Interface**: Exposes tools as A2A agent capabilities
  - **Tool Discovery**: Automatic discovery of tools from MCP servers
  - **Security Manager**: Tool execution permissions and validation
- **Technologies**: FastAPI, MCP Protocol, Docker (sandboxing), WebSockets
- **Database Schema**:
  ```sql
  - tool_registry: All registered tools with metadata
  - mcp_servers: Connected MCP server configurations
  - tool_executions: Tool execution logs and results
  - tool_permissions: Security and access control
  - external_tools: External tool integrations
  ```
- **Enhanced Endpoints**:
  - `GET /api/tools`: List all available tools
  - `POST /api/tools/:id/execute`: Execute tool with parameters
  - `GET /api/mcp/servers`: List connected MCP servers
  - `POST /api/mcp/servers`: Register new MCP server
  - `GET /api/mcp/tools`: List tools from MCP servers
  - `POST /api/mcp/discover`: Discover tools from server
  - `GET /api/tools/:id/schema`: Get tool input/output schema
  - `POST /a2a/tools/execute`: A2A tool execution interface
  - `GET /api/tools/:id/health`: Check tool health status
  - `POST /api/tools/batch`: Batch tool execution

### 6. SQL Tool Service (Port: 8006)
- **Purpose**: Secure SQL query execution with multiple database support, schema introspection, and query optimization.
- **A2A Protocol Role**: Database query agent with SQL capabilities
- **Key Components**:
  - **Multi-Database Client**: Support for PostgreSQL, MySQL, SQLite, SQL Server
  - **Query Validator**: SQL injection prevention and query validation
  - **Schema Introspector**: Dynamic database schema discovery
  - **Query Optimizer**: Query performance analysis and suggestions
  - **A2A Query Interface**: Expose SQL capabilities to other agents
  - **Connection Manager**: Secure database connection pooling
- **Technologies**: FastAPI, SQLAlchemy, asyncpg, multiple DB drivers
- **Database Schema**:
  ```sql
  - database_connections: Configured database connections
  - query_history: SQL query execution history
  - schema_cache: Cached database schemas
  - query_performance: Query performance metrics
  ```
- **Enhanced Endpoints**:
  - `POST /api/sql/execute`: Execute SQL query
  - `GET /api/sql/schema`: Get database schema
  - `POST /api/sql/validate`: Validate SQL query
  - `GET /api/sql/connections`: List database connections
  - `POST /api/sql/connections`: Add new database connection
  - `GET /api/sql/history`: Query execution history
  - `POST /a2a/sql/query`: A2A SQL query interface
  - `GET /api/sql/optimize`: Query optimization suggestions

### 7. Workflow Engine Service (Port: 8007)
- **Purpose**: Advanced workflow orchestration with visual designer, A2A agent integration, and enterprise scheduling.
- **A2A Protocol Role**: Workflow coordinator with agent assignment capabilities
- **Key Components**:
  - **Visual Workflow Designer**: Drag-and-drop workflow creation
  - **Execution Engine**: Multi-threaded workflow execution with dependencies
  - **A2A Integration**: Seamless integration with A2A agents
  - **Scheduler**: Cron-based and event-driven workflow scheduling
  - **Template Manager**: Reusable workflow templates
  - **Error Handler**: Sophisticated error handling and recovery
- **Technologies**: FastAPI, Celery, Redis, Cron, WebSockets
- **Database Schema**:
  ```sql
  - workflow_definitions: Workflow structure and configuration
  - workflow_executions: Execution logs and status
  - workflow_templates: Reusable workflow templates
  - workflow_schedules: Scheduled workflow configurations
  - step_results: Individual step execution results
  ```
- **Enhanced Endpoints**:
  - `POST /api/workflows`: Create new workflow
  - `PUT /api/workflows/:id`: Update workflow definition
  - `GET /api/workflows`: List workflows with filtering
  - `POST /api/workflows/:id/execute`: Execute workflow
  - `GET /api/workflows/:id/status`: Get execution status
  - `GET /api/workflows/:id/results`: Get execution results
  - `POST /api/workflows/templates`: Create workflow template
  - `GET /api/workflows/templates`: List available templates
  - `POST /api/schedules`: Schedule workflow execution
  - `POST /a2a/workflows/assign`: Assign A2A agents to workflow

### 8. Observability Service (Port: 8008)
- **Purpose**: Comprehensive monitoring, tracing, and analytics for the entire platform with A2A protocol visibility.
- **A2A Protocol Role**: System monitor agent with analytics capabilities
- **Key Components**:
  - **OpenTelemetry Integration**: Distributed tracing across all services
  - **A2A Message Tracing**: Complete A2A communication flow tracking
  - **Metrics Collector**: Prometheus-compatible metrics collection
  - **Alert Manager**: Intelligent alerting based on system metrics
  - **Performance Analytics**: System and agent performance insights
  - **Health Dashboard**: Real-time system health visualization
- **Technologies**: FastAPI, OpenTelemetry, Prometheus, Jaeger, WebSockets
- **Database Schema**:
  ```sql
  - traces: Distributed trace data
  - spans: Individual operation spans
  - metrics: Performance and system metrics
  - alerts: Alert configurations and history
  - health_checks: Service health check results
  ```
- **Enhanced Endpoints**:
  - `GET /api/traces`: Query trace data
  - `GET /api/spans`: Get span details
  - `GET /api/metrics`: System metrics
  - `GET /api/health/services`: All services health status
  - `POST /api/alerts`: Configure alerts
  - `GET /api/alerts`: List active alerts
  - `GET /api/performance`: Performance analytics
  - `GET /a2a/traces`: A2A message flow tracing
  - `GET /api/dashboard/metrics`: Dashboard metrics

## A2A Protocol Integration

### A2A Message Flow Architecture
```
┌─────────────┐    A2A Message     ┌─────────────┐
│   Agent A   │ ──────────────────► │   Agent B   │
│  (Service)  │ ◄────────────────── │  (Service)  │
└─────────────┘    JSON-RPC 2.0    └─────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐                   ┌─────────────┐
│ Redis Queue │ ◄─────────────────► │ Redis Queue │
│ (A2A Hub)   │                   │ (A2A Hub)   │
└─────────────┘                   └─────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────────────────────────────────────────┐
│          Orchestrator Service                  │
│        (A2A Coordination Hub)                  │
└─────────────────────────────────────────────────┘
```

### A2A Protocol Features
- **JSON-RPC 2.0 Compliance**: Standard message format with request/response correlation
- **WebSocket Support**: Real-time bidirectional communication
- **Message Routing**: Intelligent routing based on agent capabilities
- **Load Balancing**: Automatic load distribution across agent instances
- **Fault Tolerance**: Automatic retry and failover mechanisms
- **Message Persistence**: Redis-based message queue with persistence
- **Tracing**: Full message flow tracing for debugging and monitoring

## Data Layer Architecture

### Database Strategy
The platform uses a multi-database approach optimized for different data types:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │     Redis       │  │    ChromaDB     │
│  (Primary DB)   │  │   (Cache/Queue) │  │  (Vector Store) │
│   Port: 5432    │  │   Port: 6379    │  │   Port: 8000    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Data Access Layer                      │
│  SQLAlchemy ORM │ Redis Client    │ ChromaDB Client    │
└─────────────────────────────────────────────────────────┘
```

### PostgreSQL Schema Organization
```sql
-- Core Platform Tables
- users, sessions, projects
- environment_variables, system_config

-- A2A Protocol Tables
- agent_cards: Agent capability definitions
- a2a_messages: Message routing and logs
- agent_collaborations: Inter-agent patterns

-- Service-Specific Tables
- agents, tools, workflows
- tool_templates, tool_instances
- workflow_definitions, workflow_executions

-- Observability Tables
- traces, spans, metrics
- health_checks, alerts

-- RAG and Vector Tables
- documents, vector_collections
- embedding_models, search_sessions
```

## System Integration Patterns

### Service Communication Patterns
1. **Synchronous HTTP**: Direct REST API calls for immediate responses
2. **Asynchronous A2A**: Message-based communication through Redis
3. **Event-Driven**: WebSocket connections for real-time updates
4. **Batch Processing**: Celery-based task queues for long-running operations

### External Integration Points
- **MCP Servers**: External tool providers via Model Context Protocol
- **LLM Providers**: OpenAI, Anthropic, Google, Azure OpenAI
- **Vector Databases**: ChromaDB, Pinecone, Weaviate
- **Monitoring Tools**: Prometheus, Jaeger, Grafana
- **Message Queues**: Redis, RabbitMQ, Apache Kafka

## Security Architecture

### Authentication & Authorization
- **JWT-based Authentication**: Stateless token-based auth
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **API Key Management**: Service-to-service authentication
- **A2A Message Security**: Encrypted inter-agent communication

### Security Layers
1. **Gateway Security**: Rate limiting, CORS, request validation
2. **Service Security**: Input validation, SQL injection prevention
3. **A2A Security**: Message encryption, agent authentication
4. **Data Security**: Encrypted storage, secure connections

## Performance & Scalability

### Horizontal Scaling Strategy
```
Load Balancer
     │
┌────▼────┐ ┌─────────┐ ┌─────────┐
│Gateway 1│ │Gateway 2│ │Gateway N│
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
┌────▼──────────▼───────────▼────┐
│      Service Mesh Network      │
│  (Agent, Tool, RAG Services)   │
└─────────────────────────────────┘
```

### Performance Optimizations
- **Connection Pooling**: Database and Redis connection pools
- **Caching Strategy**: Multi-layer caching (Redis, in-memory)
- **Async Processing**: AsyncIO for non-blocking operations
- **Query Optimization**: Optimized database queries and indexes
- **Resource Management**: CPU/memory limits per service

## Deployment Architecture

### Container Strategy
Each service is containerized with:
- **Base Image**: Python 3.11-slim with security updates
- **Health Checks**: Comprehensive health monitoring
- **Resource Limits**: CPU and memory constraints
- **Security Context**: Non-root user execution
- **Logging**: Structured logging to stdout

### Environment Management
- **Development**: Local Docker Compose setup
- **Staging**: Kubernetes cluster with testing data
- **Production**: Kubernetes with auto-scaling and monitoring

## Monitoring & Observability

### Comprehensive Monitoring Stack
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Prometheus │  │   Jaeger    │  │   Grafana   │
│  (Metrics)  │  │  (Tracing)  │  │(Dashboards)│
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────────┐
│           Observability Service                │
│          (Aggregation Layer)                   │
└─────────────────────────────────────────────────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Service   │  │   Service   │  │   Service   │
│  Metrics    │  │   Traces    │  │    Logs     │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Key Metrics Tracked
- **A2A Message Volume**: Messages per second, routing latency
- **Service Performance**: Response times, throughput, error rates
- **Resource Usage**: CPU, memory, disk, network utilization
- **Business Metrics**: Agent executions, workflow completions
- **Error Tracking**: Error frequencies, failure patterns

## Development Workflow

### Code Organization
```
backend/
├── services/
│   ├── gateway/           # API Gateway service
│   ├── agents/            # A2A Agent service
│   ├── orchestrator/      # Workflow orchestration
│   ├── tools/             # MCP tool integration
│   ├── rag/               # Vector search and RAG
│   ├── sqltool/           # SQL query service
│   ├── workflow-engine/   # Workflow management
│   └── observability/     # Monitoring service
├── shared/
│   ├── models/            # Shared data models
│   ├── utils/             # Common utilities
│   ├── a2a/               # A2A protocol implementation
│   └── config/            # Configuration management
└── tests/
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── e2e/               # End-to-end tests
```

### Quality Assurance
- **Code Quality**: Black, isort, flake8, mypy
- **Testing**: pytest with 80%+ coverage requirement
- **Security**: Bandit security scanning
- **Performance**: Load testing with Locust
- **Documentation**: Comprehensive API documentation

## Conclusion
The Agentic AI Acceleration's backend architecture is designed for enterprise-scale deployment with sophisticated A2A protocol support, MCP integration, and comprehensive observability. The microservices architecture enables independent scaling, development, and deployment while maintaining strong consistency through the A2A protocol and shared data layer. The platform supports both synchronous and asynchronous communication patterns, ensuring optimal performance for various use cases from real-time chat to complex batch workflows.