# Agentic AI Acceleration - Python FastAPI Backend

## Overview

This document provides setup and deployment instructions for the Agentic AI Acceleration backend, which has been optimized with Python FastAPI for high performance and async capabilities.

## Architecture

The backend consists of 8 FastAPI microservices:

- **Gateway Service** (Port 8000): API Gateway and request routing
- **Orchestrator Service** (Port 8001): Multi-agent orchestration and supervision
- **Agents Service** (Port 8002): Agent lifecycle management and framework adapters
- **Tools Service** (Port 8003): Tool integration and MCP protocol support
- **RAG Service** (Port 8004): Document processing and vector search
- **SQL Tool Service** (Port 8005): Database connectivity and query execution
- **Workflow Engine** (Port 8006): Workflow definition and execution
- **Observability Service** (Port 8007): Monitoring, tracing, and metrics

## Prerequisites

### System Requirements
- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)

### Optional Dependencies
- UV package manager (recommended for faster Python installs)
- ChromaDB or other vector database
- Jaeger (for tracing)
- Prometheus (for metrics)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd lcnc-multiagent-platform

# Copy environment configuration
cp .env.example .env
# Edit .env with your configuration
```

### 2. Install Dependencies

#### Option A: Using UV (Recommended)
```bash
# Install UV
pip install uv

# Install dependencies for each service
services=("gateway" "orchestrator" "agents" "tools" "rag" "sqltool" "workflow_engine" "observability")
for service in "${services[@]}"; do
  cd services/$service
  uv pip install -r requirements.txt
  cd ../..
done
```

#### Option B: Using pip
```bash
# Install dependencies for each service
for service in services/*/; do
  cd "$service"
  pip install -r requirements.txt
  cd ../..
done
```

### 3. Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Run database migrations (after services are created)
cd services/gateway
alembic upgrade head
cd ../..

# Repeat for other services with database dependencies
```

### 4. Start Services

#### Option A: Docker Compose (Recommended)
```bash
# Start all services
docker-compose up --build

# Or start specific services
docker-compose up postgres redis chromadb gateway orchestrator
```

#### Option B: Manual Service Start
```bash
# Terminal 1 - Gateway Service
cd services/gateway
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Orchestrator Service
cd services/orchestrator
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3 - Agents Service
cd services/agents
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Continue for other services...

# Terminal N - Frontend
cd apps/web
npm install
npm run dev
```

### 5. Verify Installation

```bash
# Check service health
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Orchestrator
curl http://localhost:8002/health  # Agents
curl http://localhost:8003/health  # Tools
curl http://localhost:8004/health  # RAG
curl http://localhost:8005/health  # SQL Tool
curl http://localhost:8006/health  # Workflow Engine
curl http://localhost:8007/health  # Observability

# Access the application
open http://localhost:3000  # Frontend
open http://localhost:8000/docs  # API Documentation
```

## Development Workflow

### Code Structure

Each FastAPI service follows this structure:
```
services/{service_name}/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   ├── dependencies.py  # Dependency injection
│   │   └── database.py      # Database setup
│   ├── api/
│   │   └── v1/             # API version 1 routes
│   ├── services/           # Business logic
│   ├── models/             # Pydantic models and SQLAlchemy tables
│   ├── repository/         # Data access layer
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── pyproject.toml         # Python project configuration
```

### Adding New Features

1. **Create Models**: Define Pydantic models for request/response
2. **Add Database Models**: Create SQLAlchemy models if needed
3. **Implement Services**: Add business logic in services layer
4. **Create API Routes**: Add FastAPI routes in api/v1/
5. **Write Tests**: Add unit and integration tests
6. **Update Documentation**: Update API docs and README

### Testing

```bash
# Run tests for specific service
cd services/gateway
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run integration tests
pytest tests/integration/

# Run all tests
python -m pytest services/*/tests/
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Run all quality checks
make format  # If Makefile exists
make lint
make test
```

## Performance Optimization

### FastAPI Configuration

Key performance settings in each service:
```python
# uvicorn configuration
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    workers=4,
    worker_class="uvicorn.workers.UvicornWorker",
    max_requests=1000,
    max_requests_jitter=100
)
```

### Database Optimization

```python
# Async database configuration
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db"
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Caching Strategy

```python
# Redis configuration for caching
REDIS_URL = "redis://localhost:6379/0"
redis_pool = aioredis.ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,
    retry_on_timeout=True
)
```

## Monitoring and Observability

### Health Checks

All services provide health check endpoints:
```bash
GET /health
{
  "status": "healthy",
  "service": "lcnc-gateway",
  "version": "1.0.0",
  "timestamp": 1234567890
}
```

### Metrics Collection

Prometheus metrics are available at:
```bash
GET /metrics
```

### Distributed Tracing

Jaeger tracing is configured for all services:
- Trace collection endpoint: `http://localhost:14268/api/traces`
- Jaeger UI: `http://localhost:16686`

### Logging

Structured logging is configured with:
- JSON format for production
- Configurable log levels
- Request/response logging
- Error tracking

## Deployment

### Production Configuration

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **Vector Database**: Configure Pinecone or managed Chroma
5. **Secrets Management**: Use environment-specific secret management
6. **SSL/TLS**: Configure HTTPS for all services
7. **Load Balancing**: Use reverse proxy (nginx, Traefik)

### Kubernetes Deployment

```bash
# Build and push images
docker build -t registry/lcnc-gateway:latest services/gateway/
docker push registry/lcnc-gateway:latest

# Deploy to Kubernetes
kubectl apply -f infra/k8s/
```

### Scaling Guidelines

- **Gateway**: Scale based on request volume
- **Orchestrator**: Scale based on active workflows
- **RAG**: Scale based on document processing load
- **Tools**: Scale based on tool execution requests
- **Database**: Use read replicas for read-heavy workloads

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Check PostgreSQL connection and credentials
3. **Redis Connection**: Verify Redis server is running
4. **Service Communication**: Check service URLs and network connectivity
5. **Performance Issues**: Monitor CPU, memory, and database performance

### Debug Commands

```bash
# Check service logs
docker-compose logs gateway
docker-compose logs orchestrator

# Test database connection
python -c "import asyncpg; print('AsyncPG available')"

# Test Redis connection
python -c "import aioredis; print('Redis available')"

# Check service endpoints
curl -v http://localhost:8000/health
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Check database queries
# Enable query logging in PostgreSQL
# Monitor slow queries

# Redis monitoring
redis-cli info stats
```

## Migration from Node.js

If migrating from the original Node.js backend:

1. **Data Migration**: Export data from existing system
2. **API Compatibility**: Ensure frontend APIs remain compatible
3. **Configuration**: Update environment variables
4. **Testing**: Run comprehensive tests
5. **Gradual Migration**: Consider service-by-service migration

## Contributing

1. **Fork Repository**: Create your feature branch
2. **Follow Standards**: Use Black, isort, and type hints
3. **Write Tests**: Ensure good test coverage
4. **Documentation**: Update relevant documentation
5. **Pull Request**: Submit PR with clear description

## Support

For support and questions:
- Check the API documentation: `http://localhost:8000/docs`
- Review logs: `docker-compose logs <service>`
- Check health endpoints: `curl http://localhost:8000/health`
- Review the troubleshooting section above

## License

[Your License Here]
