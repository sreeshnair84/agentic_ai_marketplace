# Infrastructure & Deployment Documentation

## Overview

This document provides comprehensive information about the infrastructure requirements, database schema, and deployment configurations for the Enterprise AI Multi-Agent Platform.

## Database Schema & Migrations

### PostgreSQL Database Structure

The platform uses PostgreSQL 16 with PGVector extension for vector storage. The complete schema is defined in `infra/migrations/0001_complete_schema.sql`.

#### Core Platform Tables

##### 1. Agents Table
```sql
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    description TEXT,
    url TEXT,
    health_url TEXT,
    dns_name TEXT,
    category VARCHAR(100),
    agent_type VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    ai_provider VARCHAR(100),
    model_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    framework VARCHAR(50),
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_response_time INTEGER DEFAULT 0,
    last_executed TIMESTAMP WITH TIME ZONE,
    author VARCHAR(255),
    organization VARCHAR(255),
    environment VARCHAR(100) DEFAULT 'development',
    is_active BOOLEAN DEFAULT true,
    capabilities JSONB DEFAULT '[]',
    system_prompt TEXT,
    max_tokens INTEGER DEFAULT 2048,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    a2a_enabled BOOLEAN DEFAULT true,
    a2a_address VARCHAR(255),
    model_config_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);
```

##### 2. Tools Table
```sql
CREATE TABLE IF NOT EXISTS tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    category VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    is_template BOOLEAN DEFAULT false,
    configuration JSONB,
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);
```

##### 3. Workflows Table
```sql
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    category VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    is_template BOOLEAN DEFAULT false,
    complexity VARCHAR(20) DEFAULT 'simple',
    triggers TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    execution_count INTEGER DEFAULT 0,
    last_executed TIMESTAMP WITH TIME ZONE,
    avg_execution_time VARCHAR(20),
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);
```

#### Advanced Workflow System

##### Workflow Definitions
```sql
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) DEFAULT 'draft',
    steps JSONB DEFAULT '[]',
    variables JSONB DEFAULT '{}',
    timeout_seconds INTEGER DEFAULT 3600,
    category VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    is_template BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    retry_config JSONB,
    notification_config JSONB,
    health_url TEXT,
    dns_name TEXT,
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);
```

##### Workflow Executions
```sql
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    execution_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    current_step VARCHAR(255),
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    step_results JSONB DEFAULT '{}',
    step_statuses JSONB DEFAULT '{}',
    step_timings JSONB DEFAULT '{}',
    error_message TEXT,
    error_details JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    priority INTEGER DEFAULT 0,
    timeout_seconds INTEGER,
    project_tags TEXT[] DEFAULT '{}',
    executed_by VARCHAR(255),
    execution_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### User Authentication & Authorization

##### Users Table
```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'VIEWER',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    provider VARCHAR(50) DEFAULT 'local',
    provider_id VARCHAR(255),
    avatar_url VARCHAR(500),
    selected_project_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);
```

##### Projects & Organization
```sql
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS user_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Advanced Tool System

##### Tool Templates
```sql
CREATE TABLE IF NOT EXISTS tool_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    icon VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    health_url TEXT,
    status VARCHAR(50) DEFAULT 'inactive',
    dns_name TEXT,
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);
```

##### LLM & Embedding Models
```sql
CREATE TABLE IF NOT EXISTS llm_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    endpoint_url VARCHAR(500),
    api_key_env_var VARCHAR(255),
    model_config JSONB,
    max_tokens INTEGER,
    supports_streaming BOOLEAN DEFAULT false,
    supports_functions BOOLEAN DEFAULT false,
    cost_per_token VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embedding_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    endpoint_url VARCHAR(500),
    api_key_env_var VARCHAR(255),
    model_config JSONB,
    dimensions INTEGER,
    max_input_tokens INTEGER,
    cost_per_token VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### RAG & Observability

##### RAG Documents
```sql
CREATE TABLE IF NOT EXISTS rag_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

##### Observability Tables
```sql
CREATE TABLE IF NOT EXISTS observability_traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    duration INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS observability_spans (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Database Performance Indexes

```sql
-- Core tables indexes
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_agents_project_tags ON agents USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_agents_environment ON agents(environment);

CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(name);
CREATE INDEX IF NOT EXISTS idx_tools_status ON tools(status);
CREATE INDEX IF NOT EXISTS idx_tools_tags ON tools USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_tools_project_tags ON tools USING GIN(project_tags);

CREATE INDEX IF NOT EXISTS idx_workflows_name ON workflows(name);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_tags ON workflows USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_workflows_project_tags ON workflows USING GIN(project_tags);

-- Workflow execution indexes
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_created_at ON workflow_executions(created_at DESC);

-- User and auth indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
```

### Utility Functions

```sql
-- Platform health check function
CREATE OR REPLACE FUNCTION check_platform_health()
RETURNS TABLE(component TEXT, status TEXT, count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 'agents'::TEXT, 'active'::TEXT, COUNT(*) FROM agents WHERE status = 'active'
    UNION ALL
    SELECT 'tools'::TEXT, 'active'::TEXT, COUNT(*) FROM tool_templates WHERE is_active = true
    UNION ALL
    SELECT 'workflows'::TEXT, 'active'::TEXT, COUNT(*) FROM workflow_definitions WHERE status = 'active'
    UNION ALL
    SELECT 'users'::TEXT, 'total'::TEXT, COUNT(*) FROM users WHERE is_active = true
    UNION ALL
    SELECT 'projects'::TEXT, 'total'::TEXT, COUNT(*) FROM projects;
END;
$$ LANGUAGE plpgsql;
```

## Docker Infrastructure

### Docker Compose Configuration

The platform uses Docker Compose for local development and testing. Key services include:

#### Core Application Services
```yaml
services:
  # Frontend - Next.js Web Application
  web:
    build:
      context: ./frontend/
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
      - NEXT_PUBLIC_GATEWAY_URL=http://localhost:8000
    depends_on:
      - gateway
    networks:
      - agenticai-network

  # API Gateway - FastAPI
  gateway:
    build:
      context: ./backend/services/gateway
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=your-secret-key-here
    depends_on:
      - postgres
      - redis
    networks:
      - agenticai-network
```

#### Backend Microservices
```yaml
  # Agents Service - A2A Protocol
  agents:
    build:
      context: ./backend/services/agents
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform
      - REDIS_URL=redis://redis:6379/2
      - A2A_PROTOCOL_ENABLED=true
      - MCP_SERVER_ENABLED=true
    depends_on:
      - postgres
      - redis

  # Orchestrator - A2A Core
  orchestrator:
    build:
      context: ./backend/services/orchestrator
      dockerfile: Dockerfile
    ports:
      - "8003:8003"
    environment:
      - ENVIRONMENT=development
      - A2A_PROTOCOL_ENABLED=true
      - REMOTE_AGENTS=http://agents:8002,http://rag:8004,http://tools:8005
```

#### Data Services
```yaml
  # PostgreSQL Database with PGVector Extension
  postgres:
    image: pgvector/pgvector:pg16
    restart: always
    environment:
      POSTGRES_USER: agenticai_user
      POSTGRES_PASSWORD: agenticai_password
      POSTGRES_DB: agenticai_platform
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/migrations:/docker-entrypoint-initdb.d/
    ports:
      - "5432:5432"

  # Redis Cache and Message Broker
  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
```

#### Monitoring Services
```yaml
  # Jaeger Tracing
  jaeger:
    image: jaegertracing/all-in-one:1.57
    restart: always
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - JAEGER_DISABLED=false
    ports:
      - "16686:16686"
      - "14268:14268"

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    restart: always
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    volumes:
      - ./infra/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
```

## Kubernetes Deployment

### Namespace Configuration
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: agenticai-platform
---
```

### ConfigMaps and Secrets
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agenticai-config
  namespace: agenticai-platform
data:
  DATABASE_URL: "postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform"
  REDIS_URL: "redis://redis:6379/0"
  ENVIRONMENT: "production"
---
apiVersion: v1
kind: Secret
metadata:
  name: agenticai-secrets
  namespace: agenticai-platform
type: Opaque
data:
  JWT_SECRET_KEY: <base64-encoded-secret>
  OPENAI_API_KEY: <base64-encoded-key>
  GOOGLE_API_KEY: <base64-encoded-key>
```

### Service Deployments
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway-deployment
  namespace: agenticai-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      containers:
      - name: gateway
        image: agenticai-platform/gateway:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: agenticai-config
        - secretRef:
            name: agenticai-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Terraform Infrastructure (AWS Example)

### Main Configuration
```hcl
# infra/terraform/main.tf
resource "aws_s3_bucket" "agenticai_bucket" {
  bucket = "agenticai-multiagent-platform-bucket"
  
  tags = {
    Name        = "Agentic AI Acceleration Bucket"
    Environment = "production"
  }
}

resource "aws_dynamodb_table" "agents_table" {
  name         = "Agents"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "agent_id"

  attribute {
    name = "agent_id"
    type = "S"
  }

  tags = {
    Name        = "Agents Table"
    Environment = "production"
  }
}

resource "aws_ecs_cluster" "agenticai_cluster" {
  name = "agenticai-platform"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_service" "gateway_service" {
  name            = "gateway"
  cluster         = aws_ecs_cluster.agenticai_cluster.id
  task_definition = aws_ecs_task_definition.gateway.arn
  desired_count   = 3

  load_balancer {
    target_group_arn = aws_lb_target_group.gateway.arn
    container_name   = "gateway"
    container_port   = 8000
  }
}
```

### Variables and Outputs
```hcl
# infra/terraform/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

# infra/terraform/outputs.tf
output "bucket_name" {
  value = aws_s3_bucket.agenticai_bucket.bucket
}

output "cluster_name" {
  value = aws_ecs_cluster.agenticai_cluster.name
}

output "gateway_endpoint" {
  value = aws_lb.main.dns_name
}
```

## Monitoring Configuration

### Prometheus Configuration
```yaml
# infra/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'agenticai-platform'
    static_configs:
      - targets: ['gateway:8000', 'agents:8002', 'orchestrator:8003']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "Agentic AI Accelerator Overview",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"agenticai-platform\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "A2A Message Throughput",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(a2a_messages_total[5m])",
            "legendFormat": "Messages/sec"
          }
        ]
      }
    ]
  }
}
```

## Security Configuration

### Network Security
```yaml
# Security groups for AWS
resource "aws_security_group" "agenticai_platform" {
  name_prefix = "agenticai-platform"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### SSL/TLS Configuration
```nginx
# Nginx configuration for SSL termination
server {
    listen 443 ssl http2;
    server_name api.agenticai-platform.com;
    
    ssl_certificate /etc/ssl/certs/agenticai-platform.crt;
    ssl_certificate_key /etc/ssl/private/agenticai-platform.key;
    
    location / {
        proxy_pass http://gateway:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup and Recovery

### Database Backup Strategy
```bash
#!/bin/bash
# backup-database.sh
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="agenticai_platform_backup_${DATE}.sql"

# Create backup
pg_dump -h postgres -U agenticai_user -d agenticai_platform > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3 (optional)
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://agenticai-backups/database/
```

### Disaster Recovery Plan
1. **Database Recovery**: Restore from latest backup
2. **Service Recovery**: Redeploy from container registry
3. **Data Recovery**: Restore user data from S3 backups
4. **Configuration Recovery**: Restore from Git repository

## Performance Tuning

### Database Optimization
```sql
-- PostgreSQL configuration for performance
shared_buffers = 256MB
work_mem = 64MB
maintenance_work_mem = 128MB
effective_cache_size = 1GB
max_connections = 200
```

### Redis Configuration
```redis
# Redis performance tuning
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Application-Level Caching
```python
# FastAPI response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://redis:6379")
    FastAPICache.init(RedisBackend(redis), prefix="agenticai-cache")
```

This infrastructure documentation provides a comprehensive guide for deploying and managing the Enterprise AI Platform across different environments and cloud providers.
