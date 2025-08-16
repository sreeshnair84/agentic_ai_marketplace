# Database Architecture - Agentic AI Acceleration

## Overview
This document outlines the comprehensive database architecture for the Agentic AI Acceleration. The platform uses a multi-database strategy with PostgreSQL as the primary relational database, Redis for caching and A2A message queuing, ChromaDB for vector storage, and specialized databases for different data types and access patterns.

## Database Strategy Overview

### Multi-Database Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│               Data Access Layer                             │
│  SQLAlchemy ORM │ Redis Client │ ChromaDB Client │ Others  │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│PostgreSQL│ │ Redis │    │ChromaDB│   │Vector │    │ File  │
│Primary  │  │Cache/ │    │Vector │    │ DB    │    │Storage│
│Database │  │Queue  │    │Search │    │Alt.   │    │S3/MinIO│
│Port:5432│  │Port:  │    │Port:  │    │Port:  │    │       │
│         │  │6379   │    │8000   │    │8010   │    │       │
└─────────┘  └───────┘    └───────┘    └───────┘    └───────┘
```

### Database Selection Rationale
- **PostgreSQL**: ACID compliance, advanced indexing, JSON support, scalability
- **Redis**: High-performance caching, pub/sub messaging, A2A message queuing
- **ChromaDB**: Optimized vector storage, similarity search, embedding management
- **File Storage**: S3-compatible storage for documents, models, and large objects

## PostgreSQL Primary Database

### Schema Organization
The PostgreSQL database is organized into logical schemas for different domains:

```sql
-- Core platform schemas
CREATE SCHEMA IF NOT EXISTS platform;      -- Core platform tables
CREATE SCHEMA IF NOT EXISTS a2a;          -- A2A protocol related tables
CREATE SCHEMA IF NOT EXISTS services;     -- Service-specific tables
CREATE SCHEMA IF NOT EXISTS observability; -- Monitoring and tracing
CREATE SCHEMA IF NOT EXISTS security;     -- Authentication and authorization
```

### Core Platform Tables

#### Users and Authentication
```sql
-- Users table with comprehensive profile information
CREATE TABLE platform.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- User sessions for authentication tracking
CREATE TABLE platform.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES platform.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true
);

-- API keys for programmatic access
CREATE TABLE platform.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES platform.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    permissions JSONB DEFAULT '[]',
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

#### Projects and Organization
```sql
-- Projects for organizing resources
CREATE TABLE platform.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    tags TEXT[] NOT NULL DEFAULT '{}',
    is_default BOOLEAN DEFAULT false,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id),
    updated_by UUID REFERENCES platform.users(id)
);

-- User-project relationships with roles
CREATE TABLE platform.user_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES platform.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES platform.projects(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, project_id)
);
```

#### Environment and Configuration
```sql
-- Environment variables with encryption support
CREATE TABLE platform.environment_variables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL CHECK (category IN ('llm', 'database', 'api', 'auth', 'system', 'integration')),
    is_secret BOOLEAN DEFAULT false,
    is_required BOOLEAN DEFAULT false,
    scope VARCHAR(50) NOT NULL CHECK (scope IN ('global', 'development', 'staging', 'production')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id),
    updated_by UUID REFERENCES platform.users(id)
);

-- System configuration settings
CREATE TABLE platform.system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(100),
    is_public BOOLEAN DEFAULT false,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### A2A Protocol Tables

#### Agent Cards and Capabilities
```sql
-- A2A agent cards with comprehensive metadata
CREATE TABLE a2a.agent_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    framework VARCHAR(100),
    model VARCHAR(255),
    capabilities JSONB NOT NULL DEFAULT '[]',
    endpoints JSONB NOT NULL DEFAULT '{}',
    input_schema JSONB,
    output_schema JSONB,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'error')),
    health_url TEXT,
    a2a_card_url TEXT,
    dns_name TEXT,
    project_tags TEXT[] DEFAULT '{}',
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);

-- A2A message routing and logs
CREATE TABLE a2a.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    from_agent VARCHAR(255) NOT NULL,
    to_agent VARCHAR(255),
    method VARCHAR(100) NOT NULL,
    params JSONB,
    response JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'timeout')),
    error_code VARCHAR(50),
    error_message TEXT,
    trace_id VARCHAR(255),
    span_id VARCHAR(255),
    routing_info JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Agent collaboration patterns and analytics
CREATE TABLE a2a.collaboration_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(255) NOT NULL,
    participating_agents TEXT[] NOT NULL,
    message_flow JSONB NOT NULL,
    success_rate DECIMAL(5,2),
    avg_execution_time INTEGER,
    complexity_score DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    project_tags TEXT[] DEFAULT '{}'
);
```

### Service-Specific Tables

#### Agents Service
```sql
-- Agent definitions and configurations
CREATE TABLE services.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[] NOT NULL DEFAULT '{}',
    project_tags TEXT[] NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft', 'archived')),
    category VARCHAR(100),
    framework VARCHAR(50),
    model VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    configuration JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '[]',
    input_schema JSONB,
    output_schema JSONB,
    performance_config JSONB DEFAULT '{}',
    resource_limits JSONB DEFAULT '{}',
    last_executed TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_response_time INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id),
    updated_by UUID REFERENCES platform.users(id)
);

-- Agent execution logs and performance tracking
CREATE TABLE services.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES services.agents(id) ON DELETE CASCADE,
    execution_id VARCHAR(255) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled', 'timeout')),
    error_message TEXT,
    error_details JSONB,
    performance_metrics JSONB,
    resource_usage JSONB,
    execution_time_ms INTEGER,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    trace_id VARCHAR(255),
    span_id VARCHAR(255)
);
```

#### Tools Service
```sql
-- Tool templates for tool creation
CREATE TABLE services.tool_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    icon VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    input_schema JSONB,
    output_schema JSONB,
    configuration_schema JSONB,
    health_check_config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);

-- Tool instances (configured tools)
CREATE TABLE services.tool_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_template_id UUID REFERENCES services.tool_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'testing')),
    configuration JSONB NOT NULL DEFAULT '{}',
    environment_scope VARCHAR(50) NOT NULL DEFAULT 'development',
    project_tags TEXT[] DEFAULT '{}',
    health_url TEXT,
    dns_name TEXT,
    performance_metrics JSONB DEFAULT '{}',
    last_health_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);

-- MCP server registrations
CREATE TABLE services.mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    server_url TEXT NOT NULL,
    protocol_version VARCHAR(20) DEFAULT '1.0',
    authentication_type VARCHAR(50) CHECK (authentication_type IN ('none', 'api_key', 'oauth', 'basic')),
    authentication_config JSONB DEFAULT '{}',
    health_check_url TEXT,
    status VARCHAR(20) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'maintenance')),
    capabilities JSONB DEFAULT '[]',
    discovered_tools JSONB DEFAULT '[]',
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_interval_minutes INTEGER DEFAULT 60,
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tool execution logs
CREATE TABLE services.tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_instance_id UUID REFERENCES services.tool_instances(id) ON DELETE CASCADE,
    execution_id VARCHAR(255) NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    input_parameters JSONB,
    output_result JSONB,
    status VARCHAR(50) NOT NULL CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    error_details JSONB,
    execution_time_ms INTEGER,
    resource_usage JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    trace_id VARCHAR(255),
    executed_by UUID REFERENCES platform.users(id)
);
```

#### Workflows Service
```sql
-- Workflow definitions with comprehensive metadata
CREATE TABLE services.workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive', 'archived')),
    category VARCHAR(100),
    complexity VARCHAR(20) DEFAULT 'simple' CHECK (complexity IN ('simple', 'moderate', 'complex')),
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    steps JSONB NOT NULL DEFAULT '[]',
    variables JSONB NOT NULL DEFAULT '{}',
    triggers JSONB DEFAULT '[]',
    timeout_seconds INTEGER DEFAULT 3600,
    retry_config JSONB DEFAULT '{}',
    notification_config JSONB DEFAULT '{}',
    is_template BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_execution_time INTEGER DEFAULT 0,
    last_executed TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id),
    updated_by UUID REFERENCES platform.users(id)
);

-- Workflow executions with detailed tracking
CREATE TABLE services.workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES services.workflow_definitions(id) ON DELETE CASCADE,
    execution_name VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
    current_step VARCHAR(255),
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB NOT NULL DEFAULT '{}',
    variables JSONB NOT NULL DEFAULT '{}',
    step_results JSONB NOT NULL DEFAULT '{}',
    step_statuses JSONB NOT NULL DEFAULT '{}',
    step_timings JSONB NOT NULL DEFAULT '{}',
    a2a_messages JSONB DEFAULT '[]',
    error_message TEXT,
    error_details JSONB,
    performance_metrics JSONB,
    resource_usage JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    priority INTEGER DEFAULT 0,
    timeout_seconds INTEGER,
    project_tags TEXT[] DEFAULT '{}',
    executed_by UUID REFERENCES platform.users(id),
    execution_context JSONB DEFAULT '{}',
    trace_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Workflow templates for reusability
CREATE TABLE services.workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    template_definition JSONB NOT NULL,
    parameters JSONB NOT NULL DEFAULT '[]',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(2,1) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);

-- Workflow scheduling
CREATE TABLE services.workflow_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES services.workflow_definitions(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    cron_expression VARCHAR(255),
    interval_seconds INTEGER,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT true,
    max_concurrent_executions INTEGER DEFAULT 1,
    retry_failed BOOLEAN DEFAULT false,
    default_input JSONB DEFAULT '{}',
    default_variables JSONB DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    run_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);
```

#### RAG Service
```sql
-- Document storage and metadata
CREATE TABLE services.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash VARCHAR(255) UNIQUE NOT NULL,
    storage_path TEXT NOT NULL,
    content_text TEXT,
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    processing_status VARCHAR(50) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    indexed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES platform.users(id)
);

-- Vector collections management
CREATE TABLE services.vector_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    embedding_model VARCHAR(255) NOT NULL,
    dimensions INTEGER NOT NULL,
    collection_config JSONB DEFAULT '{}',
    document_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);

-- Document-collection relationships
CREATE TABLE services.document_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES services.documents(id) ON DELETE CASCADE,
    collection_id UUID REFERENCES services.vector_collections(id) ON DELETE CASCADE,
    chunk_count INTEGER DEFAULT 0,
    indexed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, collection_id)
);

-- Search sessions and analytics
CREATE TABLE services.search_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) CHECK (query_type IN ('semantic', 'keyword', 'hybrid')),
    collection_id UUID REFERENCES services.vector_collections(id),
    filters JSONB DEFAULT '{}',
    results_count INTEGER,
    execution_time_ms INTEGER,
    similarity_threshold DECIMAL(3,2),
    results JSONB,
    user_feedback JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);
```

### Observability Tables

#### Distributed Tracing
```sql
-- Traces for distributed tracing
CREATE TABLE observability.traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(255) UNIQUE NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    status VARCHAR(20) CHECK (status IN ('ok', 'error', 'timeout')),
    tags JSONB DEFAULT '{}',
    logs JSONB DEFAULT '[]',
    process JSONB DEFAULT '{}',
    warnings TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spans for detailed operation tracking
CREATE TABLE observability.spans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(255) NOT NULL REFERENCES observability.traces(trace_id),
    span_id VARCHAR(255) UNIQUE NOT NULL,
    parent_span_id VARCHAR(255),
    operation_name VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    status VARCHAR(20) CHECK (status IN ('ok', 'error', 'timeout')),
    tags JSONB DEFAULT '{}',
    logs JSONB DEFAULT '[]',
    references JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System metrics storage
CREATE TABLE observability.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50) CHECK (metric_type IN ('counter', 'gauge', 'histogram', 'summary')),
    service_name VARCHAR(255) NOT NULL,
    value DECIMAL(15,6) NOT NULL,
    labels JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Health checks tracking
CREATE TABLE observability.health_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(255) NOT NULL,
    endpoint_url TEXT NOT NULL,
    status VARCHAR(20) CHECK (status IN ('healthy', 'unhealthy', 'unknown')),
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    additional_info JSONB DEFAULT '{}',
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Alerts and notifications
CREATE TABLE observability.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) CHECK (alert_type IN ('metric', 'health', 'error', 'performance')),
    severity VARCHAR(20) CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    service_name VARCHAR(255),
    condition_config JSONB NOT NULL,
    notification_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_triggered TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES platform.users(id)
);
```

## Redis Cache and Message Queue

### Redis Database Organization
Redis is organized into multiple databases for different purposes:

```
Redis Instance (Port: 6379)
├── Database 0: Session cache and general caching
├── Database 1: A2A message queues and routing
├── Database 2: Workflow execution state
├── Database 3: Tool execution cache
├── Database 4: RAG search cache
└── Database 5: Observability metrics cache
```

### A2A Message Queues
```redis
# A2A message routing queues
a2a:messages:pending         # Pending messages to be routed
a2a:messages:processing      # Currently processing messages
a2a:agents:registry          # Active agent registry
a2a:agents:capabilities      # Agent capabilities cache
a2a:routing:rules           # Message routing rules

# Agent status tracking
a2a:agents:{agent_id}:status    # Agent health status
a2a:agents:{agent_id}:load      # Agent current load
a2a:agents:{agent_id}:heartbeat # Last heartbeat timestamp
```

### Caching Strategies
```redis
# User session cache
session:{session_id}         # User session data
user:{user_id}:profile      # User profile cache
user:{user_id}:permissions  # User permissions cache

# API response cache
api:cache:{endpoint}:{hash}  # API response cache
api:ratelimit:{user_id}     # Rate limiting counters

# Workflow execution cache
workflow:{execution_id}:state   # Workflow execution state
workflow:{execution_id}:context # Execution context
workflow:templates:cache        # Workflow templates cache
```

## ChromaDB Vector Database

### Collection Organization
ChromaDB stores vector embeddings organized by collections:

```
ChromaDB Instance (Port: 8000)
├── Collections by Project
│   ├── project_{project_id}_documents
│   ├── project_{project_id}_knowledge
│   └── project_{project_id}_agents
├── Global Collections
│   ├── agent_capabilities
│   ├── tool_descriptions
│   └── workflow_patterns
└── System Collections
    ├── a2a_message_patterns
    └── collaboration_patterns
```

### Vector Storage Schema
```python
# Document embeddings
{
    "id": "doc_uuid",
    "embeddings": [0.1, 0.2, ...],  # Vector embeddings
    "metadata": {
        "document_id": "uuid",
        "title": "Document Title",
        "chunk_index": 0,
        "project_tags": ["project1"],
        "content_type": "text",
        "timestamp": "2025-08-14T10:00:00Z"
    }
}

# Agent capability embeddings
{
    "id": "agent_capability_uuid",
    "embeddings": [0.3, 0.4, ...],
    "metadata": {
        "agent_id": "agent_uuid",
        "capability_name": "text_analysis",
        "input_schema": {...},
        "output_schema": {...},
        "a2a_compatible": true
    }
}
```

## Database Performance Optimization

### Indexing Strategy
```sql
-- Performance indexes for frequently queried tables

-- A2A message routing indexes
CREATE INDEX CONCURRENTLY idx_a2a_messages_status_created 
ON a2a.messages(status, created_at DESC) WHERE status IN ('pending', 'processing');
CREATE INDEX CONCURRENTLY idx_a2a_messages_trace_id 
ON a2a.messages(trace_id) WHERE trace_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_a2a_messages_from_to_agents 
ON a2a.messages(from_agent, to_agent);

-- Agent registry indexes
CREATE INDEX CONCURRENTLY idx_agent_cards_status_project 
ON a2a.agent_cards(status, project_tags) USING GIN;
CREATE INDEX CONCURRENTLY idx_agent_cards_capabilities 
ON a2a.agent_cards(capabilities) USING GIN;

-- Workflow execution indexes
CREATE INDEX CONCURRENTLY idx_workflow_executions_status_created 
ON services.workflow_executions(status, created_at DESC);
CREATE INDEX CONCURRENTLY idx_workflow_executions_project_tags 
ON services.workflow_executions(project_tags) USING GIN;

-- Tool execution indexes
CREATE INDEX CONCURRENTLY idx_tool_executions_status_started 
ON services.tool_executions(status, started_at DESC);

-- Observability indexes
CREATE INDEX CONCURRENTLY idx_traces_service_start_time 
ON observability.traces(service_name, start_time DESC);
CREATE INDEX CONCURRENTLY idx_spans_trace_id_start_time 
ON observability.spans(trace_id, start_time);
CREATE INDEX CONCURRENTLY idx_metrics_name_timestamp 
ON observability.metrics(metric_name, timestamp DESC);
```

### Partitioning Strategy
```sql
-- Partition large tables by time for better performance
-- Traces table partitioned by month
CREATE TABLE observability.traces_y2025m08 PARTITION OF observability.traces
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

-- Metrics table partitioned by week
CREATE TABLE observability.metrics_y2025w32 PARTITION OF observability.metrics
FOR VALUES FROM ('2025-08-01') TO ('2025-08-08');

-- A2A messages partitioned by month
CREATE TABLE a2a.messages_y2025m08 PARTITION OF a2a.messages
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
```

## Data Backup and Recovery

### Backup Strategy
```yaml
# Automated backup configuration
backup_schedule:
  postgresql:
    full_backup: "0 2 * * 0"      # Weekly full backup
    incremental: "0 2 * * 1-6"    # Daily incremental
    retention: "30 days"
    compression: "gzip"
    
  redis:
    snapshot: "0 */6 * * *"       # Every 6 hours
    aof_rewrite: "0 3 * * *"      # Daily AOF rewrite
    retention: "7 days"
    
  chromadb:
    collection_backup: "0 4 * * *" # Daily collection backup
    metadata_backup: "0 4 * * *"   # Daily metadata backup
    retention: "14 days"
```

### Disaster Recovery
- **RTO (Recovery Time Objective)**: 4 hours maximum
- **RPO (Recovery Point Objective)**: 15 minutes maximum
- **Multi-region replication**: Primary and secondary regions
- **Automated failover**: Database cluster failover capabilities

## Database Security

### Access Control
```sql
-- Role-based database access
CREATE ROLE lcnc_admin WITH LOGIN CREATEDB CREATEROLE;
CREATE ROLE lcnc_app WITH LOGIN;
CREATE ROLE lcnc_readonly WITH LOGIN;

-- Grant appropriate permissions
GRANT ALL PRIVILEGES ON DATABASE lcnc_platform TO lcnc_admin;
GRANT CONNECT ON DATABASE lcnc_platform TO lcnc_app;
GRANT USAGE ON ALL SCHEMAS IN DATABASE lcnc_platform TO lcnc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN DATABASE lcnc_platform TO lcnc_app;

-- Readonly access for analytics
GRANT CONNECT ON DATABASE lcnc_platform TO lcnc_readonly;
GRANT USAGE ON SCHEMA observability TO lcnc_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA observability TO lcnc_readonly;
```

### Data Encryption
- **At Rest**: PostgreSQL TDE (Transparent Data Encryption)
- **In Transit**: SSL/TLS for all database connections
- **Application Level**: Sensitive fields encrypted using AES-256
- **Key Management**: HashiCorp Vault for key rotation

### Audit Logging
```sql
-- Enable audit logging for sensitive operations
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Configure audit settings
ALTER SYSTEM SET pgaudit.log = 'ddl, write, role';
ALTER SYSTEM SET pgaudit.log_catalog = on;
ALTER SYSTEM SET pgaudit.log_parameter = on;
```

## Monitoring and Observability

### Database Metrics
```yaml
# Key metrics to monitor
database_metrics:
  postgresql:
    - connection_count
    - query_performance
    - index_usage
    - table_sizes
    - replication_lag
    - cache_hit_ratio
    
  redis:
    - memory_usage
    - operation_rate
    - key_expiration
    - persistence_status
    - cluster_health
    
  chromadb:
    - collection_sizes
    - query_latency
    - index_performance
    - storage_usage
```

### Alerting Rules
```yaml
# Database alerting configuration
alerts:
  - name: "High Database Connections"
    condition: "postgresql_connections > 80% of max"
    severity: "warning"
    
  - name: "Slow Query Detected"
    condition: "query_duration > 10s"
    severity: "error"
    
  - name: "Redis Memory High"
    condition: "redis_memory_usage > 85%"
    severity: "warning"
    
  - name: "Vector Search Latency"
    condition: "chromadb_query_latency > 2s"
    severity: "warning"
```

## Migration and Schema Evolution

### Migration Strategy
```python
# Database migration framework
class DatabaseMigration:
    def __init__(self):
        self.version_table = "schema_migrations"
        self.migration_path = "migrations/"
    
    def run_migrations(self):
        # Check current schema version
        # Apply pending migrations
        # Update version tracking
        pass
    
    def rollback_migration(self, target_version):
        # Rollback to specific version
        # Maintain data integrity
        pass
```

### Schema Versioning
```sql
-- Schema version tracking
CREATE TABLE platform.schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rollback_sql TEXT,
    checksum VARCHAR(64)
);

-- Track current schema version
INSERT INTO platform.schema_migrations (version, description) 
VALUES ('1.0.0', 'Initial schema with A2A protocol support');
```

## Conclusion

The Agentic AI Acceleration's database architecture provides a robust, scalable foundation for enterprise-grade multi-agent systems. The multi-database approach optimizes performance for different data types while maintaining ACID compliance where needed. The comprehensive schema supports A2A protocol requirements, MCP integration, and sophisticated observability, enabling the platform to scale from development to production environments efficiently.

Key architectural decisions include:
- **PostgreSQL**: ACID compliance for critical business data
- **Redis**: High-performance caching and message queuing
- **ChromaDB**: Optimized vector storage for AI/ML workloads
- **Comprehensive indexing**: Optimized for A2A message routing and analytics
- **Security-first design**: Encryption, access control, and audit logging
- **Observability**: Built-in monitoring and tracing capabilities
- **Scalability**: Partitioning and replication strategies for growth
