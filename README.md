# Agentic AI Acceleration

## Overview
The Agentic AI Acceleration is an enterprise-grade solution for building and orchestrating multi-agent AI systems with **Agent-to-Agent (A2A) Protocol** support. The platform implements JSON-RPC 2.0 communication between agents, **Model Context Protocol (MCP)** integration for tools, and comprehensive observability for monitoring agent interactions.

## 🚀 Key Features
- **A2A Protocol**: Agent-to-Agent communication with JSON-RPC 2.0
- **MCP Integration**: Model Context Protocol for standardized tool access
- **Multi-Framework Support**: LangChain, LlamaIndex, CrewAI, Semantic Kernel
- **Vector RAG**: ChromaDB integration for document retrieval
- **Real-time Observability**: OpenTelemetry tracing and Prometheus metrics
- **Enterprise Ready**: PostgreSQL, Redis, Docker, Kubernetes support

## 📚 Documentation Structure
```
docs/
├── requirements/
│   ├── system-requirements.md     # Complete system overview
│   ├── backend-requirements.md    # Backend service specifications
│   └── frontend-requirements.md   # Frontend application specifications
├── architecture/
│   ├── backend-modules.md         # Backend service architecture
│   ├── multiagent-orchestration.md # A2A orchestration patterns
│   └── data-flow-sequences.md     # System data flow diagrams
├── api/
│   ├── agents.yml                 # Agent service API specs
│   ├── tools.yml                  # Tools service API specs
│   └── workflows.yml              # Workflow API specifications
├── ui/
│   ├── components-inventory.md    # Frontend component library
│   └── screen-wireframes.md       # UI screen specifications
└── operations/
    ├── deployment.md              # Production deployment guide
    └── FASTAPI_SETUP.md          # FastAPI service setup
```

## Table of Contents
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Service Ports](#service-ports)
- [Requirements](#requirements)
- [Development](#development)
- [Scripts & Utilities](#scripts--utilities)
- [Testing](#testing)
- [Deployment](#deployment)

## Getting Started

### Prerequisites
- **Python 3.11+** for backend services
- **Node.js 18+** and **pnpm** for frontend
- **Docker & Docker Compose** for containerization
- **PostgreSQL 15+** for data persistence
- **Redis 7+** for caching and A2A communication

### Quick Start
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd agenticai-multiagent-platform
   ```

2. **One-Step Setup (Recommended)**
   ```bash
   # Run the consolidated setup script
   python initial_setup.py
   ```
   This single script handles:
   - Database creation and schema setup
   - Sample data population
   - Backend service dependencies
   - Environment configuration

3. **Alternative Manual Setup**
   ```bash
   # Copy environment templates
   cp .env.example .env
   
   # Set required API keys
   export GOOGLE_API_KEY="your-google-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   
   # Start infrastructure services
   docker-compose up postgres redis chromadb -d
   ```

4. **Install Backend Dependencies**
   ```bash
   # Navigate to each service and install dependencies
   cd backend/services/gateway
   pip install -r requirements.txt
   
   cd ../agents
   pip install -r requirements.txt
   
   cd ../orchestrator
   pip install -r requirements.txt
   ```

5. **Install Frontend Dependencies**
   ```bash
   cd frontend
   pnpm install
   ```

4. **Start Services**
   ```bash
   # Backend services (in separate terminals)
   cd backend/services/gateway && uvicorn app.main:app --host 0.0.0.0 --port 8000
   cd backend/services/agents && uvicorn app.main:app --host 0.0.0.0 --port 8002
   cd backend/services/orchestrator && uvicorn app.main:app --host 0.0.0.0 --port 8003
   
   # Frontend
   cd frontend && pnpm dev
   ```

5. **Verify Setup**
   ```bash
   # Quick verification
   python scripts/testing/test_basic_endpoints.py
   
   # Database health check
   python scripts/debug/check_db.py
   ```

6. **Access the Platform**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Default Admin: `admin@agenticai.local` / `admin123`

## Service Ports
```
Frontend (Next.js):      3000
API Gateway:             8000
Agents Service:          8002  (A2A Protocol)
Orchestrator:            8003  (A2A Core)
RAG Service:             8004  (Vector Search)
Tools Service:           8005  (MCP Integration)
SQL Tool Service:        8006
Workflow Engine:         8007
Observability:           8008
PostgreSQL:              5432
Redis:                   6379
ChromaDB:                8010
```

## Requirements
For detailed requirements documentation, see:

- **[System Requirements](docs/requirements/system-requirements.md)**: Complete system overview with A2A protocol specifications
- **[Backend Requirements](docs/requirements/backend-requirements.md)**: FastAPI services, A2A protocol, MCP integration, dependencies
- **[Frontend Requirements](docs/requirements/frontend-requirements.md)**: Next.js application, UI components, real-time features

## Architecture
The platform implements a microservices architecture with **A2A (Agent-to-Agent) Protocol** for inter-service communication:

### Core Components
- **Frontend**: Next.js 14+ with TypeScript, Tailwind CSS, shadcn/ui
- **Backend Services**: FastAPI/Python microservices with A2A Protocol support
- **Database**: PostgreSQL with async SQLAlchemy ORM
- **Message Queue**: Redis for async processing and A2A communication
- **Vector Database**: ChromaDB for RAG capabilities
- **Observability**: OpenTelemetry, Jaeger, Prometheus

### A2A Protocol Architecture
```
┌─────────────────┐    A2A Messages (JSON-RPC 2.0)    ┌─────────────────┐
│   Orchestrator  │◄────────────────────────────────►│   Agent Service │
│   (Port: 8003)  │                                   │   (Port: 8002)  │
└─────────────────┘                                   └─────────────────┘
         │                                                       │
         │ A2A Protocol                                         │ A2A Protocol
         ▼                                                       ▼
┌─────────────────┐                                   ┌─────────────────┐
│   RAG Service   │                                   │  Tools Service  │
│   (Port: 8004)  │                                   │   (Port: 8005)  │
└─────────────────┘                                   └─────────────────┘
                                    │
                                    ▼ MCP Protocol
                            ┌─────────────────┐
                            │   MCP Servers   │
                            │   (External)    │
                            └─────────────────┘
```

### Service Architecture
```
backend/services/
├── gateway/              # API Gateway & Authentication (Port: 8000)
├── orchestrator/         # Multi-agent orchestration with A2A (Port: 8003)
├── agents/              # Agent management service with A2A (Port: 8002)
├── tools/               # Tool integration service with MCP (Port: 8005)
├── rag/                 # RAG service with vector search (Port: 8004)
├── workflow-engine/     # Workflow execution engine (Port: 8007)
├── observability/       # Monitoring and tracing (Port: 8008)
└── sqltool/            # SQL tool service (Port: 8006)
```

## Modules
### Frontend (Next.js)
- **Chat Screen**: Interface for agent interactions.
- **RAG Tool Screen**: Manage RAG tools and document uploads.
- **Workflows Screen**: Create and manage workflows.
- **Observability Screen**: Monitor agent interactions and system performance.
- **Agents Management**: Create, update, and list agents.
- **Tools Management**: Create, update, and list tools.

### Backend Services
- **Orchestrator**: Manages multi-agent interactions and workflow execution.
- **Agents**: Handles agent creation, updates, and execution.
- **Tools**: Manages various tools including SQL and RAG tools.
- **RAG**: Responsible for document ingestion, indexing, and retrieval.
- **SQL Tool**: Executes SQL queries and manages database interactions.
- **Observability**: Collects and stores trace and log data for monitoring.
- **Workflow Engine**: Executes and manages workflows.

## API Endpoints
### Agents API
- `POST /api/agents`: Create a new agent.
- `PUT /api/agents/:id`: Update an existing agent.
- `GET /api/agents`: List all agents.
- `POST /api/agents/:id/run`: Run a specific agent.

### Tools API
- `POST /api/tools`: Create a new tool.
- `PUT /api/tools/:id`: Update an existing tool.
- `GET /api/tools`: List all tools.
- `POST /api/tools/:id/invoke`: Invoke a specific tool.

### RAG API
- `POST /api/rag/documents`: Upload a new document.
- `GET /api/rag/documents`: List all documents.
- `POST /api/rag/query`: Query the RAG index.

### SQL Tool API
- `POST /api/sql/run`: Run a SQL query.
- `GET /api/sql/schema`: Introspect the database schema.

### Observability API
- `GET /api/observability/traces`: Get trace data.
- `GET /api/observability/spans`: Get span data.
- `GET /api/observability/search`: Search observability data.

### Workflow API
- `POST /api/workflows`: Create a new workflow.
- `PUT /api/workflows/:id`: Update an existing workflow.
- `GET /api/workflows`: List all workflows.
- `POST /api/workflows/:id/run`: Run a specific workflow.

## Development

### Backend Development
Each FastAPI service follows the same structure:
```bash
backend/services/{service}/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/                 # API routes
│   ├── core/                # Core functionality
│   ├── models/              # Database models
│   └── services/            # Business logic
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── .env                    # Environment variables
```

### Frontend Development
```bash
frontend/
├── apps/web/               # Main Next.js application
├── packages/
│   ├── ui/                 # Shared UI components (shadcn/ui)
│   ├── shared/             # Shared utilities and types
│   └── sdk/                # API SDK for backend services
└── services/               # Frontend service workers
```

### A2A Protocol Development
```python
# Example A2A message implementation
from pydantic import BaseModel

class A2AMessage(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict
    id: Optional[str] = None

class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict
    output_schema: Dict

# Register agent capabilities
await a2a_protocol.register_agent(AgentCard(
    id="agent-service",
    capabilities=[
        AgentCapability(
            name="create_agent",
            description="Create new AI agent",
            input_schema={...},
            output_schema={...}
        )
    ]
))
```

### Environment Configuration
Key environment variables for development:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform

# Redis for A2A Communication
REDIS_URL=redis://redis:6379/0

# A2A Protocol
A2A_PROTOCOL_ENABLED=true
A2A_AGENT_ID=your-service-name

# AI Provider Keys
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Vector Database
CHROMA_URL=http://chromadb:8000
```

## Scripts & Utilities

The platform includes a comprehensive set of scripts for testing, debugging, and maintenance organized in the `scripts/` directory:

### Directory Structure
```
scripts/
├── testing/          # API and functionality testing scripts
├── debug/            # Database and system debugging scripts
├── utilities/        # System maintenance utilities
└── README.md         # Detailed scripts documentation
```

### Quick Testing Commands
```bash
# Basic platform health check
python scripts/testing/test_basic_endpoints.py

# Complete API endpoint testing
python scripts/testing/test_all_endpoints.py

# Database connectivity and schema verification
python scripts/debug/check_db.py

# Backend authentication testing
python scripts/testing/test_backend.py
```

### Available Script Categories

#### 🧪 Testing Scripts (`scripts/testing/`)
- **`test_all_endpoints.py`** - Comprehensive testing across all 8 microservices
- **`test_backend.py`** - Backend authentication and API testing
- **`test_basic_endpoints.py`** - Basic service health validation
- **`test_frontend_api.py`** - Frontend integration testing
- **`test_llm_api.py`** - LLM models API testing
- **`test_rag_pgvector.py`** - RAG service with vector database testing
- **`test_user_management.py`** - User management functionality testing
- **`verify_complete_apis.py`** - Complete API verification
- **`verify_signatures.py`** - Agent signature verification

#### 🔍 Debug Scripts (`scripts/debug/`)
- **`check_agents.py`** - Agents table inspection
- **`check_db.py`** - Database connectivity and structure
- **`check_schema.py`** - Schema analysis
- **`check_tools_workflows.py`** - Tools/workflows inspection
- **`debug_db.py`** - Advanced database debugging

#### 🛠️ Utility Scripts (`scripts/utilities/`)
- **`fix_docker.py`** - Docker configuration troubleshooting
- **`cleanup_migrations.py`** - Archive management

### Usage Examples
```bash
# Development workflow
python initial_setup.py                          # Setup platform
python scripts/debug/check_db.py                 # Verify database
python scripts/testing/test_basic_endpoints.py   # Test services
python scripts/testing/test_backend.py           # Test authentication

# Troubleshooting workflow
python scripts/debug/check_schema.py             # Check schema
python scripts/debug/debug_db.py                 # Debug queries
python scripts/utilities/fix_docker.py           # Fix Docker issues
```

For detailed script documentation and usage instructions, see [`scripts/README.md`](scripts/README.md).

## Testing

### Automated Testing Scripts
The platform includes comprehensive testing scripts in the `scripts/testing/` directory:

```bash
# Backend service testing
python scripts/testing/test_backend.py

# All microservices endpoint testing  
python scripts/testing/test_all_endpoints.py

# Basic health and connectivity
python scripts/testing/test_basic_endpoints.py

# RAG and vector database testing
python scripts/testing/test_rag_pgvector.py

# User management testing
python scripts/testing/test_user_management.py
```

### Manual Testing

### Manual Testing

#### Backend Testing
```bash
# Unit tests for A2A protocol
pytest backend/tests/test_a2a_protocol.py -v

# Integration tests for service communication
pytest backend/tests/test_integration.py -v

# Load testing
pytest backend/tests/test_load.py -v
```
```bash
#### Frontend Testing
```bash
# Unit tests
cd frontend && pnpm test

# E2E tests with Playwright
cd frontend && pnpm test:e2e

# Component testing
cd frontend && pnpm test:components
```

#### A2A Protocol Testing
```python
# Test A2A message flow
async def test_a2a_communication():
    # Send message from orchestrator to agent
    message = A2AMessage(
        method="execute_task",
        params={"task": "analyze document", "context": {...}}
    )
    response = await orchestrator.send_a2a_message("agent-service", message)
    assert response.result is not None
```

### Testing Checklist
For comprehensive platform testing, run scripts in this order:

1. **Setup Verification**: `python scripts/debug/check_db.py`
2. **Basic Health**: `python scripts/testing/test_basic_endpoints.py`  
3. **Backend APIs**: `python scripts/testing/test_backend.py`
4. **All Services**: `python scripts/testing/test_all_endpoints.py`
5. **Specialized**: `python scripts/testing/test_rag_pgvector.py`
```

### A2A Protocol Testing
```python
# Test A2A message flow
async def test_a2a_communication():
    # Send message from orchestrator to agent
    message = A2AMessage(
        method="execute_task",
        params={"task": "analyze document", "context": {...}}
    )
    response = await orchestrator.send_a2a_message("agent-service", message)
    assert response.result is not None
```

## Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up --build -d

# Scale specific services
docker-compose up --scale agents=3 --scale orchestrator=2

# View logs
docker-compose logs -f orchestrator
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f infra/k8s/deployments/
kubectl apply -f infra/k8s/services/
kubectl apply -f infra/k8s/ingress/

# Check deployment status
kubectl get pods -l app=agents-service
kubectl get services
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Redis cluster configured
- [ ] Monitoring and alerting setup
- [ ] SSL certificates installed
- [ ] A2A protocol security enabled
- [ ] Resource limits configured
- [ ] Health checks verified

## API Documentation
Interactive API documentation is available at:
- **Gateway API**: http://localhost:8000/docs
- **Agents API**: http://localhost:8002/docs
- **Orchestrator API**: http://localhost:8003/docs
- **RAG API**: http://localhost:8004/docs
- **Tools API**: http://localhost:8005/docs

## Monitoring & Observability
- **Jaeger Tracing**: http://localhost:16686
- **Prometheus Metrics**: http://localhost:9090
- **A2A Message Monitoring**: Built into observability service
- **System Health**: Available through /health endpoints

## Contributing
1. Follow the A2A protocol specifications
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure observability instrumentation
5. Test MCP integration compatibility

## License
[License details here]

## Support
For support and questions:
- Check the [documentation](docs/)
- Review [API specifications](docs/api/)
- Check [troubleshooting guide](docs/operations/)

---

**The Agentic AI Acceleration provides enterprise-grade multi-agent orchestration with A2A protocol support, MCP integration, and comprehensive observability for building intelligent applications at scale.**