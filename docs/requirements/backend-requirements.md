# Backend Requirements - Agentic AI Acceleration

## Overview
This document outlines the comprehensive backend requirements for the Agentic AI Acceleration with A2A Protocol implementation.

## Architecture Summary
- **Protocol**: Agent-to-Agent (A2A) Protocol with JSON-RPC 2.0
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with async SQLAlchemy
- **Message Queue**: Redis for A2A communication
- **Vector Store**: ChromaDB for RAG capabilities
- **Monitoring**: OpenTelemetry, Prometheus, Jaeger

## Service Ports Configuration
```
Gateway Service:      8000
Agents Service:       8002  (A2A Protocol)
Orchestrator Service: 8003  (A2A Core)
RAG Service:          8004  (Vector Search)
Tools Service:        8005  (MCP Integration)
SQL Tool Service:     8006
Workflow Engine:      8007
Observability:        8008
PostgreSQL:           5432
Redis:                6379
PGVectorDB:             8010
```

## Core Dependencies by Service

### 1. Gateway Service (Port: 8000)
```txt
# FastAPI Core
fastapi
uvicorn[standard]
pydantic
pydantic-settings

# Database
sqlalchemy[asyncio]
asyncpg
alembic

# Authentication
python-jose[cryptography]
passlib[bcrypt]
python-multipart

# HTTP Client
httpx
aiohttp

# Validation & Serialization
email-validator
python-dateutil

# Environment
python-dotenv
```

### 2. Agents Service (Port: 8002) - A2A Enhanced
```txt
# A2A Protocol Dependencies
fastapi
uvicorn[standard]
pydantic
websockets

# AI Frameworks
langchain
langchain-openai
langchain-google-genai
langchain-anthropic
llamaindex
crewai

# LLM Providers
openai
google-generativeai
anthropic

# Database & Cache
sqlalchemy[asyncio]
asyncpg
redis[hiredis]

# A2A Communication
aioredis
jsonrpc-base
jsonrpc-async

# HTTP & WebSocket
httpx
aiohttp
websockets

# Utilities
python-dotenv
pyyaml
jinja2
```

### 3. Orchestrator Service (Port: 8003) - A2A Core
```txt
# FastAPI & A2A Protocol
fastapi
uvicorn[standard]
pydantic
websockets

# A2A Protocol Implementation
aioredis
jsonrpc-base
jsonrpc-async
redis[hiredis]

# AI Orchestration
langchain
langchain-openai
google-generativeai

# Database
sqlalchemy[asyncio]
asyncpg

# HTTP Communication
httpx
aiohttp

# Workflow Management
celery[redis]
kombu

# Utilities
python-dotenv
pyyaml
asyncio-mqtt
```

### 4. RAG Service (Port: 8004) - Vector Enhanced
```txt
# FastAPI Core
fastapi
uvicorn[standard]
pydantic

# Vector Database
chromadb
sentence-transformers
faiss-cpu

# Document Processing
pypdf
python-docx
python-pptx
openpyxl
markdown

# Embeddings
openai
tiktoken
google-generativeai

# Text Processing
nltk
spacy
transformers

# Database
sqlalchemy[asyncio]
asyncpg
redis[hiredis]

# HTTP
httpx
aiofiles

# A2A Protocol
aioredis
jsonrpc-async

# Utilities
python-dotenv
pyyaml
```

### 5. Tools Service (Port: 8005) - MCP Integration
```txt
# FastAPI Core
fastapi
uvicorn[standard]
pydantic

# MCP Protocol
mcp # Model Context Protocol client
jsonrpc-base
jsonrpc-async

# A2A Protocol
aioredis
redis[hiredis]

# Database
sqlalchemy[asyncio]
asyncpg

# HTTP & WebSocket
httpx
aiohttp
websockets

# Tool Execution
subprocess32 # For secure subprocess execution
docker # For containerized tool execution

# Security
cryptography
jwt

# Utilities
python-dotenv
pyyaml
```

### 6. SQL Tool Service (Port: 8006)
```txt
# FastAPI Core
fastapi
uvicorn[standard]
pydantic

# Database Drivers
asyncpg # PostgreSQL
aiomysql # MySQL
aiosqlite # SQLite
pyodbc # SQL Server

# SQLAlchemy
sqlalchemy[asyncio]
alembic

# Security
sqlparse # SQL parsing and validation
cryptography

# A2A Protocol
aioredis
redis[hiredis]

# Utilities
python-dotenv
pyyaml
```

### 7. Workflow Engine Service (Port: 8007)
```txt
# FastAPI Core
fastapi
uvicorn[standard]
pydantic

# Workflow Management
celery[redis]
kombu
flower # Celery monitoring

# A2A Protocol
aioredis
redis[hiredis]
jsonrpc-async

# Database
sqlalchemy[asyncio]
asyncpg

# HTTP
httpx
aiohttp

# Workflow Definition
pyyaml
jsonschema

# Utilities
python-dotenv
crontab
```

### 8. Observability Service (Port: 8008)
```txt
# FastAPI Core
fastapi
uvicorn[standard]
pydantic

# OpenTelemetry
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-jaeger
opentelemetry-exporter-prometheusc1
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-sqlalchemy
opentelemetry-instrumentation-redis

# Metrics & Monitoring
prometheus-client
jaeger-client

# Database
sqlalchemy[asyncio]
asyncpg
redis[hiredis]

# A2A Protocol Monitoring
aioredis
jsonrpc-async

# HTTP
httpx
aiohttp

# Utilities
python-dotenv
pyyaml
```

## Development Dependencies
```txt
# Testing
pytest
pytest-asyncio
pytest-mock
httpx # For testing FastAPI
pytest-cov

# Code Quality
black
isort
flake8
mypy
pre-commit

# Development Tools
ipython
jupyter
python-dotenv
```

## Environment Variables by Service

### Gateway Service (.env)
```bash
# Server Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Redis
REDIS_URL=redis://redis:6379/0

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://web:3000"]

# Service URLs
ORCHESTRATOR_URL=http://orchestrator:8003
AGENTS_URL=http://agents:8002
TOOLS_URL=http://tools:8005
RAG_URL=http://rag:8004
SQLTOOL_URL=http://sqltool:8006
WORKFLOW_URL=http://workflow:8007
OBSERVABILITY_URL=http://observability:8008
```

### Agents Service (.env)
```bash
# Server Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8002

# Database
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform

# Redis for A2A
REDIS_URL=redis://redis:6379/2

# A2A Protocol
A2A_PROTOCOL_ENABLED=true
A2A_AGENT_ID=agents-service
A2A_DISCOVERY_CHANNEL=a2a:discovery

# AI Provider Keys
GOOGLE_API_KEY=${GOOGLE_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Service URLs
TOOLS_URL=http://tools:8005
ORCHESTRATOR_URL=http://orchestrator:8003

# MCP
MCP_SERVER_ENABLED=true
MCP_REGISTRY_URL=http://mcp-registry:9000
```

### Orchestrator Service (.env)
```bash
# Server Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8003

# Database
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform

# Redis for A2A
REDIS_URL=redis://redis:6379/1

# A2A Protocol
A2A_PROTOCOL_ENABLED=true
A2A_AGENT_ID=orchestrator-service
REMOTE_AGENTS=http://agents:8002,http://rag:8004,http://tools:8005

# AI Configuration
GOOGLE_API_KEY=${GOOGLE_API_KEY}
DEFAULT_LLM_MODEL=gpt-4-turbo-preview

# Service URLs
AGENTS_URL=http://agents:8002
TOOLS_URL=http://tools:8005
RAG_URL=http://rag:8004
WORKFLOW_URL=http://workflow:8007
```

### RAG Service (.env)
```bash
# Server Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8004

# Database
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform

# Redis
REDIS_URL=redis://redis:6379/4

# Vector Store
VECTOR_STORE_TYPE=chroma
CHROMA_URL=http://chromadb:8000
CHROMA_COLLECTION_PREFIX=lcnc_

# Embeddings
GOOGLE_API_KEY=${GOOGLE_API_KEY}
OPENAI_API_KEY=${OPENAI_API_KEY}
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# A2A Protocol
A2A_PROTOCOL_ENABLED=true
A2A_AGENT_ID=rag-service

# Document Processing
MAX_FILE_SIZE_MB=100
SUPPORTED_FORMATS=pdf,docx,pptx,xlsx,txt,md
```

### Tools Service (.env)
```bash
# Server Configuration
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8005

# Database
DATABASE_URL=postgresql+asyncpg://lcnc_user:lcnc_password@postgres:5432/lcnc_platform

# Redis
REDIS_URL=redis://redis:6379/3

# A2A Protocol
A2A_PROTOCOL_ENABLED=true
A2A_AGENT_ID=tools-service

# MCP Configuration
MCP_SERVER_REGISTRY_URL=http://mcp-registry:9000
MCP_TIMEOUT_SECONDS=30
MCP_MAX_RETRIES=3

# Tool Execution Security
TOOL_EXECUTION_TIMEOUT=300
ALLOW_CONTAINERIZED_EXECUTION=true
DOCKER_NETWORK=lcnc-tools
```

## Database Migrations
```sql
-- Create A2A tables
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agent Cards for A2A Protocol
CREATE TABLE agent_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    capabilities JSONB NOT NULL DEFAULT '[]',
    endpoints JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',
    last_heartbeat TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- A2A Messages Log
CREATE TABLE a2a_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent VARCHAR(255) NOT NULL,
    to_agent VARCHAR(255),
    method VARCHAR(100) NOT NULL,
    params JSONB,
    response JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    trace_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_agent_cards_agent_id ON agent_cards(agent_id);
CREATE INDEX idx_agent_cards_status ON agent_cards(status);
CREATE INDEX idx_a2a_messages_from_agent ON a2a_messages(from_agent);
CREATE INDEX idx_a2a_messages_to_agent ON a2a_messages(to_agent);
CREATE INDEX idx_a2a_messages_trace_id ON a2a_messages(trace_id);
```

## Docker Configuration
Each service requires a Dockerfile:

```dockerfile
# Example Dockerfile for FastAPI services
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application
ENV PYTHONPATH=/app
EXPOSE ${PORT:-8000}
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
```

## Testing Requirements
Each service should include:
- Unit tests for A2A protocol implementation
- Integration tests for service communication
- Performance tests for high-load scenarios
- Security tests for authentication and authorization

## Monitoring & Logging
- All services emit OpenTelemetry traces
- Prometheus metrics for performance monitoring
- Structured logging with correlation IDs
- A2A message flow tracing
- Health checks for container orchestration

## Security Considerations
- JWT-based authentication across services
- A2A message encryption in transit
- Database connection security
- Tool execution sandboxing
- Rate limiting and request validation
- Environment variable security

This comprehensive backend requirements document ensures all services are properly configured with A2A protocol support, MCP integration, and production-ready infrastructure.
