# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an enterprise-grade multi-agent AI platform implementing Agent-to-Agent (A2A) Protocol with JSON-RPC 2.0 for inter-service communication. The platform supports Model Context Protocol (MCP) integration, LangGraph framework, and provides comprehensive observability for multi-agent orchestration.

## Architecture

### Microservices Architecture
The platform consists of 8 backend microservices and a Next.js frontend:

```
backend/services/
├── gateway/              # API Gateway & Authentication (Port: 8000)
├── agents/              # Agent management with A2A Protocol (Port: 8002)  
├── orchestrator/        # Multi-agent orchestration core (Port: 8003)
├── rag/                # RAG service with PGVector (Port: 8004)
├── tools/              # Tool integration with MCP support (Port: 8005)
├── sqltool/            # SQL tool service (Port: 8006)
├── workflow-engine/    # Workflow execution (Port: 8007)
└── observability/      # Monitoring and tracing (Port: 8008)

frontend/               # Next.js 14 with TypeScript
├── src/app/           # App router pages
├── src/components/    # Shared components 
├── src/hooks/         # Custom React hooks
└── src/services/      # API services
```

### A2A Protocol Communication
Services communicate via JSON-RPC 2.0 messages through Redis channels:
- Orchestrator (8003) coordinates agent communications
- Agents (8002) handle A2A message processing  
- Gateway (8000) provides metadata API for routing discovery

### Technology Stack
**Backend:** FastAPI, SQLAlchemy (async), PostgreSQL with PGVector, Redis, OpenTelemetry
**Frontend:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, React Query, Zustand
**AI Frameworks:** LangGraph, LangChain, support for OpenAI, Google Gemini, Azure OpenAI

## Development Commands

### Docker Environment
```bash
# Start all services with Docker Compose
docker-compose up -d

# Start with observability (Jaeger, Prometheus)  
docker-compose --profile observability up -d

# View logs for specific service
docker-compose logs -f orchestrator
```

### Backend Services
Each service uses uvicorn and has the same structure:
```bash
# Run individual service (from backend/services/{service}/)
uvicorn app.main:app --host 0.0.0.0 --port {PORT} --reload

# Examples:
cd backend/services/gateway && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd backend/services/agents && uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload  
cd backend/services/orchestrator && uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Frontend Development
```bash
# From frontend/ directory
pnpm install       # Install dependencies
pnpm dev          # Start development server with Turbopack
pnpm build        # Production build
pnpm start        # Start production server
pnpm lint         # Run ESLint
pnpm type-check   # Run TypeScript checks
```

### Testing
```bash
# Basic service health testing
python scripts/testing/test_basic_endpoints.py

# Complete API endpoint testing  
python scripts/testing/test_all_endpoints.py

# Backend authentication testing
python scripts/testing/test_backend.py

# Database connectivity verification
python scripts/debug/check_db.py

# RAG and vector database testing
python scripts/testing/test_rag_pgvector.py
```

### Database Setup
```bash
# Complete setup (recommended)
python initial_setup.py

# Manual database setup
python recreate_database.py
python insert_minimal_data.py
```

## Key Implementation Patterns

### A2A Protocol Implementation
Services implement A2A message handling with JSON-RPC 2.0:
```python
class A2AMessage(BaseModel):
    jsonrpc: str = "2.0" 
    method: str
    params: Dict
    id: Optional[str] = None

# Register agent capabilities
await a2a_protocol.register_agent(AgentCard(
    id="service-name",
    capabilities=[AgentCapability(...)]
))
```

### Frontend Service Integration  
API calls use consistent patterns with React Query:
```typescript
// Custom hooks pattern (useAgents.ts, useWorkflows.ts, etc.)
const { data, isLoading, error } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.get('/api/v1/agents')
});
```

### Database Models
All services use async SQLAlchemy with consistent patterns:
```python
# Each service has models/database.py with tables
class AgentModel(Base):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(primary_key=True)
    # ... other fields
```

### Error Handling
Consistent error handling across services:
```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error for {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

## Important Files and Locations

### Configuration
- `docker-compose.yml` - Complete service orchestration
- `backend/services/{service}/requirements.txt` - Python dependencies  
- `frontend/package.json` - Node.js dependencies
- Environment variables configured in docker-compose services

### Key Backend Files
- `backend/services/gateway/app/main.py` - Main API gateway with all router imports
- `backend/services/gateway/app/api/v1/metadata.py` - Metadata API for A2A routing
- `backend/services/orchestrator/app/services/a2a_orchestrator.py` - A2A coordination
- `backend/services/agents/app/services/a2a_handler.py` - A2A message processing

### Key Frontend Files
- `frontend/src/app/layout.tsx` - Root layout with ClientWrapper
- `frontend/src/components/chat/A2AChatInterface.tsx` - Main chat interface with A2A
- `frontend/src/hooks/useA2AChat.ts` - A2A chat logic with context routing
- `frontend/src/components/layout/StandardPageLayout.tsx` - Standard page wrapper

### Documentation
- `README.md` - Complete project documentation
- `DEVELOPER_CHECKLIST.md` - Development priorities and completed features
- `docs/LANGGRAPH_INTEGRATION_MERGED.md` - LangGraph integration details
- `scripts/testing/` - Comprehensive testing scripts

## Development Workflows

### Adding New Features
1. Create database models in `backend/services/{service}/app/models/`
2. Add API routes in `backend/services/{service}/app/api/`
3. Implement business logic in `backend/services/{service}/app/services/`
4. Add frontend components in `frontend/src/components/`
5. Create custom hooks in `frontend/src/hooks/`
6. Update routing in gateway `app/main.py`

### A2A Protocol Integration
When adding A2A capabilities to services:
1. Define agent capabilities in service models
2. Implement A2A message handlers  
3. Register with orchestrator via Redis
4. Add routing metadata to gateway
5. Update frontend metadata selector

### Database Changes
1. Modify models in service `models/database.py`
2. Create migration script if needed
3. Update database initialization
4. Test with `python scripts/debug/check_db.py`

### Testing New Services
1. Add health endpoints (`/` and `/health`)
2. Update `scripts/testing/test_basic_endpoints.py`
3. Add comprehensive tests to `scripts/testing/test_all_endpoints.py`
4. Test A2A communication if applicable

## Service Communication Patterns

### Gateway → Services
Gateway proxies requests to backend services and provides metadata APIs for service discovery.

### A2A Communication Flow
1. Frontend selects workflow/agent/tools via MetadataSelector
2. Chat hook determines routing (DNS, direct A2A, or Generic Agent)
3. Messages routed through orchestrator coordination
4. Responses streamed back with context preservation

### Database Access
Each service manages its own database access with shared connection pooling patterns and async SQLAlchemy.

## Common Issues and Solutions

### Service Startup
- Ensure PostgreSQL and Redis are running before starting services
- Check environment variables in docker-compose.yml
- Verify port conflicts (services run on 8000-8008)

### Database Connectivity
- Run `python scripts/debug/check_db.py` for database health
- Use `python initial_setup.py` for fresh setup
- Check PostgreSQL PGVector extension is loaded

### A2A Communication Issues  
- Verify Redis connectivity between services
- Check agent registration in orchestrator logs
- Test message routing with metadata APIs

### Frontend Build Issues
- Use `pnpm` instead of npm for dependency management
- Check TypeScript errors with `pnpm type-check`
- Ensure API endpoints are accessible

The platform implements enterprise-grade patterns for multi-agent AI orchestration with comprehensive observability and scalable microservices architecture.