# Agentic AI Acceleration - Backend Services

This directory contains the backend services for the Agentic AI Acceleration.

## Services

### 1. API Gateway (`services/gateway`)
- **Port**: 8000
- **Purpose**: Entry point for all API requests, handles authentication, and routes requests to appropriate services
- **Key Features**:
  - JWT-based authentication
  - Request routing and proxying
  - Rate limiting and security
  - Health checks and monitoring

### 2. Orchestrator (`services/orchestrator`)
- **Port**: 8001
- **Purpose**: Manages multi-agent workflows and task coordination
- **Key Features**:
  - Workflow definition and execution
  - A2A (Agent-to-Agent) protocol implementation
  - Task queue management
  - Agent coordination

### 3. Agents Service (`services/agents`) - TODO
- **Port**: 8002
- **Purpose**: Agent registry and management
- **Key Features**:
  - Agent registration and discovery
  - Agent lifecycle management
  - Capability management

### 4. Tools Service (`services/tools`) - TODO
- **Port**: 8003
- **Purpose**: Tool registry and MCP integration
- **Key Features**:
  - MCP (Model Context Protocol) client
  - Tool discovery and execution
  - Standard tools library

### 5. RAG Service (`services/rag`) - TODO
- **Port**: 8004
- **Purpose**: Retrieval-Augmented Generation
- **Key Features**:
  - Document indexing and search
  - Vector database integration
  - Knowledge retrieval

### 6. SQL Tool Service (`services/sqltool`) - TODO
- **Port**: 8005
- **Purpose**: Database query and management
- **Key Features**:
  - SQL query execution
  - Database schema management
  - Query optimization

### 7. Observability Service (`services/observability`) - TODO
- **Port**: 8006
- **Purpose**: Monitoring and observability
- **Key Features**:
  - Metrics collection
  - Distributed tracing
  - Log aggregation

### 8. Workflow Engine (`services/workflow-engine`) - TODO
- **Port**: 8007
- **Purpose**: Workflow execution engine
- **Key Features**:
  - Workflow runtime
  - State management
  - Error handling and retries

## Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

### Quick Start

1. **Run the setup script**:
   ```bash
   python setup_dev.py
   ```

2. **Set up environment variables**:
   Copy `.env.example` to `.env` in each service directory and configure:
   ```bash
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/agenticai_gateway
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Security
   SECRET_KEY=your-secret-key-here
   ```

3. **Start services individually**:
   ```bash
   # Gateway
   cd services/gateway
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload --port 8000
   
   # Orchestrator
   cd services/orchestrator
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload --port 8001
   ```

### Docker Development

```bash
# Build and run all services
docker-compose up --build

# Run specific service
docker-compose up gateway orchestrator
```

## API Documentation

Once services are running, access API documentation:
- Gateway: http://localhost:8000/docs
- Orchestrator: http://localhost:8001/docs

## Architecture

### Service Communication
- **API Gateway**: Entry point, handles auth and routing
- **Orchestrator**: Coordinates workflows between services
- **Service Mesh**: Internal service-to-service communication
- **Message Queue**: Async task processing (Redis/RabbitMQ)

### Data Flow
1. Frontend requests → API Gateway
2. Gateway authenticates and routes to appropriate service
3. Orchestrator manages multi-service workflows
4. Services communicate via HTTP APIs and message queues
5. Results flow back through Gateway to frontend

### Protocols
- **HTTP/REST**: Synchronous service communication
- **A2A Protocol**: Agent-to-Agent communication
- **MCP**: Model Context Protocol for tool integration
- **WebSocket**: Real-time updates (future)

## Testing

```bash
# Run tests for a service
cd services/gateway
source venv/bin/activate
pytest

# Run integration tests
cd tests/integration
python -m pytest
```

## Deployment

See `/infra` directory for:
- Kubernetes manifests
- Terraform infrastructure
- Docker configurations
- Helm charts

## Contributing

1. Follow the established project structure
2. Add comprehensive tests
3. Update documentation
4. Follow Python coding standards (Black, isort, flake8)

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated and dependencies installed
2. **Database connection**: Check PostgreSQL is running and credentials are correct
3. **Port conflicts**: Ensure ports 8000-8007 are available
4. **Redis connection**: Verify Redis is running on port 6379

### Logs

Services log to stdout by default. In development, logs include:
- Request/response details
- Database queries (when DEBUG=True)
- Service communication
- Error traces
