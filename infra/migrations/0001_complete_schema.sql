-- =====================================================
-- AgenticAI PLATFORM - UNIFIED DATABASE SCHEMA
-- Optimized consolidated schema with pgvector support
-- Version: Unified
-- Date: 2025-08-23
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- CORE PLATFORM TABLES
-- =====================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'VIEWER' CHECK (role IN ('ADMIN', 'EDITOR', 'VIEWER')),
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

-- MCP Endpoints table
CREATE TABLE IF NOT EXISTS mcp_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    endpoint_path VARCHAR(255) NOT NULL,
    endpoint_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'draft', 'archived')),
    authentication_required BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- User Projects Association table
CREATE TABLE IF NOT EXISTS user_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, project_id)
);

-- LLM Models table (unified from both llm_models and embedding_models)
CREATE TABLE IF NOT EXISTS llm_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL CHECK (model_type IN ('chat', 'completion', 'embedding', 'multimodal')),
    endpoint_url VARCHAR(500),
    api_key_env_var VARCHAR(255),
    model_config JSONB DEFAULT '{}',
    max_tokens INTEGER,
    dimensions INTEGER, -- For embedding models
    supports_streaming BOOLEAN DEFAULT false,
    supports_functions BOOLEAN DEFAULT false,
    pricing_info JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TOOL SYSTEM TABLES
-- =====================================================

-- Tool Templates table
CREATE TABLE IF NOT EXISTS tool_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL CHECK (type IN ('rag', 'sql_agent', 'mcp', 'code_interpreter', 'web_scraper', 'file_processor', 'api_integration', 'custom')),
    description TEXT,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    icon VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    health_url TEXT,
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'draft', 'archived')),
    dns_name TEXT,
    execution_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    schema_definition JSONB NOT NULL DEFAULT '{}',
    default_config JSONB DEFAULT '{}',
    documentation TEXT,
    capabilities JSONB DEFAULT '[]',
    input_signature JSONB,
    output_signature JSONB,
    default_input_modes TEXT[] DEFAULT ARRAY['text'],
    default_output_modes TEXT[] DEFAULT ARRAY['text'],
    -- MCP Integration
    mcp_server_id UUID,
    mcp_tool_name VARCHAR(255),
    mcp_binding_config JSONB DEFAULT '{}',
    is_mcp_tool BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Tool Template Fields table
CREATE TABLE IF NOT EXISTS tool_template_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_template_id UUID NOT NULL REFERENCES tool_templates(id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    field_label VARCHAR(255) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    field_description TEXT,
    is_required BOOLEAN DEFAULT false,
    is_secret BOOLEAN DEFAULT false,
    default_value TEXT,
    validation_rules JSONB,
    field_options JSONB,
    field_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tool Instances table
CREATE TABLE IF NOT EXISTS tool_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_template_id UUID NOT NULL REFERENCES tool_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'maintenance', 'deploying')),
    configuration JSONB DEFAULT '{}',
    credentials JSONB DEFAULT '{}',
    environment VARCHAR(50) DEFAULT 'development' CHECK (environment IN ('development', 'staging', 'production')),
    environment_scope VARCHAR(50) DEFAULT 'development',
    project_tags TEXT[] DEFAULT '{}',
    resource_limits JSONB DEFAULT '{}',
    health_check_config JSONB DEFAULT '{}',
    last_health_check TIMESTAMP WITH TIME ZONE,
    health_status VARCHAR(50) DEFAULT 'unknown' CHECK (health_status IN ('healthy', 'unhealthy', 'unknown', 'warning')),
    metrics JSONB DEFAULT '{}',
    error_log TEXT,
    llm_model_id UUID REFERENCES llm_models(id) ON DELETE SET NULL,
    -- MCP Integration
    mcp_endpoint_id UUID,
    mcp_binding_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    CONSTRAINT unique_instance_name_per_template UNIQUE (tool_template_id, name)
);

-- Legacy tools table (maintained for backward compatibility)
CREATE TABLE IF NOT EXISTS tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft', 'archived')),
    category VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    is_template BOOLEAN DEFAULT false,
    configuration JSONB,
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    template_id UUID REFERENCES tool_templates(id),
    instance_id UUID REFERENCES tool_instances(id),
    is_template_based BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- AGENT SYSTEM TABLES
-- =====================================================

-- Agent Templates table
CREATE TABLE IF NOT EXISTS agent_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    framework VARCHAR(100) DEFAULT 'langgraph' CHECK (framework IN ('langgraph', 'crewai', 'autogen', 'semantic_kernel', 'custom')),
    workflow_config JSONB NOT NULL DEFAULT '{}',
    persona_config JSONB DEFAULT '{}',
    capabilities TEXT[] DEFAULT '{}',
    constraints JSONB DEFAULT '{}',
    tool_template_requirements JSONB DEFAULT '[]',
    optional_tool_templates JSONB DEFAULT '[]',
    default_tool_bindings JSONB DEFAULT '{}',
    version VARCHAR(50) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    tags TEXT[] DEFAULT '{}',
    documentation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Agent Instances table
CREATE TABLE IF NOT EXISTS agent_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tool_instance_bindings JSONB NOT NULL DEFAULT '{}',
    runtime_config JSONB DEFAULT '{}',
    state_config JSONB DEFAULT '{}',
    conversation_history JSONB DEFAULT '[]',
    performance_metrics JSONB DEFAULT '{}',
    security_config JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'maintenance', 'deploying')),
    environment VARCHAR(50) DEFAULT 'development' CHECK (environment IN ('development', 'staging', 'production')),
    last_activity TIMESTAMP WITH TIME ZONE,
    error_log TEXT,
    deployment_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    CONSTRAINT unique_agent_instance_name UNIQUE (name, environment)
);

-- Legacy agents table (maintained for backward compatibility)
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
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft', 'archived')),
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
    default_input_modes JSONB DEFAULT '[]',
    default_output_modes JSONB DEFAULT '[]',
    llm_model_id UUID REFERENCES llm_models(id) ON DELETE SET NULL,
    template_id UUID REFERENCES agent_templates(id),
    instance_id UUID REFERENCES agent_instances(id),
    is_template_based BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- =====================================================
-- WORKFLOW SYSTEM TABLES
-- =====================================================

-- Workflow Definitions table
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    url TEXT,
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('active', 'inactive', 'running', 'error', 'draft')),
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
    last_executed TIMESTAMP WITH TIME ZONE,
    avg_execution_time VARCHAR(20),
    complexity VARCHAR(20) DEFAULT 'simple' CHECK (complexity IN ('simple', 'moderate', 'complex')),
    triggers TEXT[] DEFAULT '{}',
    capabilities JSONB DEFAULT '{}',
    default_input_modes JSONB DEFAULT '[]',
    default_output_modes JSONB DEFAULT '[]',
    llm_model_id UUID REFERENCES llm_models(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Legacy workflows table (maintained for backward compatibility)
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('active', 'inactive', 'running', 'error', 'draft')),
    category VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    is_template BOOLEAN DEFAULT false,
    complexity VARCHAR(20) DEFAULT 'simple' CHECK (complexity IN ('simple', 'moderate', 'complex')),
    triggers TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    execution_count INTEGER DEFAULT 0,
    last_executed TIMESTAMP WITH TIME ZONE,
    avg_execution_time VARCHAR(20),
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Workflow Agents Association table
CREATE TABLE IF NOT EXISTS workflow_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    role VARCHAR(100) NOT NULL,
    sequence_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Workflow Executions table
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
    execution_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
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
    executed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    execution_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- RAG AND VECTOR STORAGE TABLES
-- =====================================================

-- RAG Documents table
CREATE TABLE IF NOT EXISTS rag_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document embeddings table for RAG
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-small dimension
    metadata JSONB,
    namespace VARCHAR(255) DEFAULT 'default',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation embeddings for context retrieval
CREATE TABLE IF NOT EXISTS conversation_embeddings (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    message_content TEXT NOT NULL,
    embedding vector(1536),
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base embeddings
CREATE TABLE IF NOT EXISTS knowledge_base_embeddings (
    id SERIAL PRIMARY KEY,
    knowledge_item_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    content TEXT NOT NULL,
    embedding vector(1536),
    category VARCHAR(255),
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RAG Pipelines table
CREATE TABLE IF NOT EXISTS rag_pipelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    data_sources JSONB NOT NULL DEFAULT '[]',
    processing_config JSONB NOT NULL DEFAULT '{}',
    chunking_strategy JSONB NOT NULL DEFAULT '{}',
    vectorization_config JSONB NOT NULL DEFAULT '{}',
    storage_config JSONB NOT NULL DEFAULT '{}',
    retrieval_config JSONB NOT NULL DEFAULT '{}',
    quality_config JSONB DEFAULT '{}',
    schedule_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- RAG Pipeline Runs table
CREATE TABLE IF NOT EXISTS rag_pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_id UUID NOT NULL REFERENCES rag_pipelines(id) ON DELETE CASCADE,
    run_type VARCHAR(50) DEFAULT 'manual' CHECK (run_type IN ('manual', 'scheduled', 'triggered')),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    logs TEXT,
    error_details TEXT,
    input_data JSONB DEFAULT '{}',
    output_summary JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- MCP (Model Context Protocol) TABLES
-- =====================================================

-- MCP Servers table
CREATE TABLE IF NOT EXISTS mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    server_url VARCHAR(500) NOT NULL,
    transport_type VARCHAR(50) DEFAULT 'streamable' CHECK (transport_type IN ('streamable', 'sse', 'stdio')),
    authentication_config JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '{}',
    version VARCHAR(50) DEFAULT '1.0.0',
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'testing')),
    health_check_url VARCHAR(500),
    health_status VARCHAR(50) DEFAULT 'unknown' CHECK (health_status IN ('healthy', 'unhealthy', 'unknown', 'degraded')),
    last_health_check TIMESTAMP WITH TIME ZONE,
    connection_config JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- MCP Tools Registry table
CREATE TABLE IF NOT EXISTS mcp_tools_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    input_schema JSONB NOT NULL DEFAULT '{}',
    output_schema JSONB DEFAULT '{}',
    tool_config JSONB DEFAULT '{}',
    capabilities TEXT[] DEFAULT '{}',
    resource_requirements JSONB DEFAULT '{}',
    examples JSONB DEFAULT '[]',
    documentation_url VARCHAR(500),
    version VARCHAR(50) DEFAULT '1.0.0',
    is_available BOOLEAN DEFAULT true,
    last_discovered TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_execution_time INTEGER DEFAULT 0,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_tool_per_server UNIQUE (server_id, tool_name)
);

-- =====================================================
-- AUTHENTICATION AND SESSION MANAGEMENT
-- =====================================================

-- Refresh tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    device_id VARCHAR(255),
    user_agent VARCHAR(500),
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    device_id VARCHAR(255),
    user_agent TEXT,
    ip_address VARCHAR(45),
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- EXECUTION AND MONITORING TABLES
-- =====================================================

-- Tool Instance Execution Logs
CREATE TABLE IF NOT EXISTS tool_instance_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_instance_id UUID NOT NULL REFERENCES tool_instances(id) ON DELETE CASCADE,
    agent_instance_id UUID REFERENCES agent_instances(id) ON DELETE SET NULL,
    execution_type VARCHAR(100) NOT NULL,
    input_data JSONB DEFAULT '{}',
    output_data JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout')),
    error_details TEXT,
    execution_time_ms INTEGER,
    resource_usage JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Agent Instance Conversations
CREATE TABLE IF NOT EXISTS agent_instance_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_instance_id UUID NOT NULL REFERENCES agent_instances(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(255) NOT NULL,
    conversation_data JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    tools_used JSONB DEFAULT '[]',
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_session_per_agent UNIQUE (agent_instance_id, session_id)
);

-- Observability traces table
CREATE TABLE IF NOT EXISTS observability_traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    duration INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Observability spans table
CREATE TABLE IF NOT EXISTS observability_spans (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type VARCHAR(32) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

-- Demo sample queries table
CREATE TABLE IF NOT EXISTS demo_sample_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    query_text TEXT NOT NULL,
    description TEXT,
    complexity_level VARCHAR(20) DEFAULT 'beginner' CHECK (complexity_level IN ('beginner', 'intermediate', 'advanced')),
    tags TEXT[],
    is_featured BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ASSOCIATION TABLES
-- =====================================================

-- Tool Template - Agent Template Associations
CREATE TABLE IF NOT EXISTS tool_template_agent_template_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_template_id UUID NOT NULL REFERENCES tool_templates(id) ON DELETE CASCADE,
    agent_template_id UUID NOT NULL REFERENCES agent_templates(id) ON DELETE CASCADE,
    role_name VARCHAR(255) NOT NULL,
    configuration JSONB DEFAULT '{}',
    is_required BOOLEAN DEFAULT true,
    execution_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_tool_role_per_agent UNIQUE (agent_template_id, role_name)
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- Core tables indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_tags ON projects USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_projects_is_default ON projects(is_default);

CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON user_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_project_id ON user_projects(project_id);

-- LLM Models indexes
CREATE INDEX IF NOT EXISTS idx_llm_models_provider ON llm_models(provider);
CREATE INDEX IF NOT EXISTS idx_llm_models_model_type ON llm_models(model_type);
CREATE INDEX IF NOT EXISTS idx_llm_models_is_active ON llm_models(is_active);
CREATE INDEX IF NOT EXISTS idx_llm_models_project_tags ON llm_models USING GIN(project_tags);

-- Tool system indexes
CREATE INDEX IF NOT EXISTS idx_tool_templates_type ON tool_templates(type);
CREATE INDEX IF NOT EXISTS idx_tool_templates_active ON tool_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_tool_templates_status ON tool_templates(status);
CREATE INDEX IF NOT EXISTS idx_tool_templates_project_tags ON tool_templates USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_tool_templates_is_mcp ON tool_templates(is_mcp_tool);

CREATE INDEX IF NOT EXISTS idx_tool_instances_template ON tool_instances(tool_template_id);
CREATE INDEX IF NOT EXISTS idx_tool_instances_status ON tool_instances(status);
CREATE INDEX IF NOT EXISTS idx_tool_instances_environment ON tool_instances(environment);
CREATE INDEX IF NOT EXISTS idx_tool_instances_health ON tool_instances(health_status);
CREATE INDEX IF NOT EXISTS idx_tool_instances_project_tags ON tool_instances USING GIN(project_tags);

-- Agent system indexes
CREATE INDEX IF NOT EXISTS idx_agent_templates_framework ON agent_templates(framework);
CREATE INDEX IF NOT EXISTS idx_agent_templates_active ON agent_templates(is_active);

CREATE INDEX IF NOT EXISTS idx_agent_instances_template ON agent_instances(template_id);
CREATE INDEX IF NOT EXISTS idx_agent_instances_status ON agent_instances(status);
CREATE INDEX IF NOT EXISTS idx_agent_instances_environment ON agent_instances(environment);
CREATE INDEX IF NOT EXISTS idx_agent_instances_activity ON agent_instances(last_activity);

CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_agents_project_tags ON agents USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_agents_environment ON agents(environment);

-- Workflow system indexes
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_status ON workflow_definitions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_category ON workflow_definitions(category);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_is_template ON workflow_definitions(is_template);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_project_tags ON workflow_definitions USING GIN(project_tags);

CREATE INDEX IF NOT EXISTS idx_workflows_name ON workflows(name);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_tags ON workflows USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_workflows_project_tags ON workflows USING GIN(project_tags);

CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_created_at ON workflow_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_project_tags ON workflow_executions USING GIN(project_tags);

CREATE INDEX IF NOT EXISTS idx_workflow_agents_workflow_id ON workflow_agents(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_agents_agent_id ON workflow_agents(agent_id);

-- Vector storage indexes
CREATE INDEX IF NOT EXISTS idx_document_embeddings_embedding ON document_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings (document_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_namespace ON document_embeddings (namespace);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_metadata ON document_embeddings USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_embedding ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_conversation_id ON conversation_embeddings (conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_role ON conversation_embeddings (role);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_embedding ON knowledge_base_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_knowledge_item_id ON knowledge_base_embeddings (knowledge_item_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_category ON knowledge_base_embeddings (category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_embeddings_tags ON knowledge_base_embeddings USING GIN (tags);

-- RAG system indexes
CREATE INDEX IF NOT EXISTS idx_rag_pipelines_active ON rag_pipelines(is_active);
CREATE INDEX IF NOT EXISTS idx_rag_pipeline_runs_pipeline ON rag_pipeline_runs(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_rag_pipeline_runs_status ON rag_pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_rag_pipeline_runs_created ON rag_pipeline_runs(created_at);

-- MCP system indexes
CREATE INDEX IF NOT EXISTS idx_mcp_servers_status ON mcp_servers(status);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_health_status ON mcp_servers(health_status);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_project_tags ON mcp_servers USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_transport_type ON mcp_servers(transport_type);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_active ON mcp_servers(is_active);

CREATE INDEX IF NOT EXISTS idx_mcp_tools_server_id ON mcp_tools_registry(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_tool_name ON mcp_tools_registry(tool_name);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_available ON mcp_tools_registry(is_available);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_usage_count ON mcp_tools_registry(usage_count DESC);

-- Execution and monitoring indexes
CREATE INDEX IF NOT EXISTS idx_tool_executions_instance ON tool_instance_executions(tool_instance_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_agent ON tool_instance_executions(agent_instance_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_status ON tool_instance_executions(status);
CREATE INDEX IF NOT EXISTS idx_tool_executions_time ON tool_instance_executions(started_at);

CREATE INDEX IF NOT EXISTS idx_conversations_agent ON agent_instance_conversations(agent_instance_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON agent_instance_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON agent_instance_conversations(session_id);

-- Authentication indexes
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);

-- Demo queries indexes
CREATE INDEX IF NOT EXISTS idx_demo_sample_queries_service_type ON demo_sample_queries(service_type);
CREATE INDEX IF NOT EXISTS idx_demo_sample_queries_featured ON demo_sample_queries(is_featured);

-- Association table indexes
CREATE INDEX IF NOT EXISTS idx_tool_agent_associations_tool ON tool_template_agent_template_associations(tool_template_id);
CREATE INDEX IF NOT EXISTS idx_tool_agent_associations_agent ON tool_template_agent_template_associations(agent_template_id);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_llm_models_updated_at BEFORE UPDATE ON llm_models FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tool_templates_updated_at BEFORE UPDATE ON tool_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tool_instances_updated_at BEFORE UPDATE ON tool_instances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tools_updated_at BEFORE UPDATE ON tools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_templates_updated_at BEFORE UPDATE ON agent_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_instances_updated_at BEFORE UPDATE ON agent_instances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_definitions_updated_at BEFORE UPDATE ON workflow_definitions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_executions_updated_at BEFORE UPDATE ON workflow_executions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rag_pipelines_updated_at BEFORE UPDATE ON rag_pipelines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcp_servers_updated_at BEFORE UPDATE ON mcp_servers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcp_tools_registry_updated_at BEFORE UPDATE ON mcp_tools_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agent_conversations_updated_at BEFORE UPDATE ON agent_instance_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Cosine similarity function for vector operations
CREATE OR REPLACE FUNCTION cosine_similarity(vec1 vector, vec2 vector)
RETURNS float
LANGUAGE sql
IMMUTABLE STRICT
AS $$
    SELECT 1 - (vec1 <=> vec2);
$$;

-- Search similar documents function
CREATE OR REPLACE FUNCTION search_similar_documents(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10,
    target_namespace varchar DEFAULT 'default'
)
RETURNS TABLE (
    id integer,
    document_id varchar,
    content text,
    similarity float,
    metadata jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT 
        de.id,
        de.document_id,
        de.content,
        cosine_similarity(de.embedding, query_embedding) as similarity,
        de.metadata
    FROM document_embeddings de
    WHERE de.namespace = target_namespace
    AND cosine_similarity(de.embedding, query_embedding) > similarity_threshold
    ORDER BY similarity DESC
    LIMIT max_results;
$$;

-- Search knowledge base function
CREATE OR REPLACE FUNCTION search_knowledge_base(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 10,
    target_category varchar DEFAULT NULL
)
RETURNS TABLE (
    id integer,
    knowledge_item_id varchar,
    title varchar,
    content text,
    category varchar,
    similarity float,
    metadata jsonb
)
LANGUAGE sql
STABLE
AS $$
    SELECT 
        kbe.id,
        kbe.knowledge_item_id,
        kbe.title,
        kbe.content,
        kbe.category,
        cosine_similarity(kbe.embedding, query_embedding) as similarity,
        kbe.metadata
    FROM knowledge_base_embeddings kbe
    WHERE cosine_similarity(kbe.embedding, query_embedding) > similarity_threshold
    AND (target_category IS NULL OR kbe.category = target_category)
    ORDER BY similarity DESC
    LIMIT max_results;
$$;

-- Platform health check function
CREATE OR REPLACE FUNCTION check_platform_health()
RETURNS TABLE(component TEXT, status TEXT, count BIGINT, details JSONB) AS $
BEGIN
    RETURN QUERY
    SELECT 'agents'::TEXT, 'active'::TEXT, COUNT(*), 
           jsonb_build_object('with_templates', COUNT(*) FILTER (WHERE template_id IS NOT NULL))
    FROM agents WHERE status = 'active'
    UNION ALL
    SELECT 'tool_templates'::TEXT, 'active'::TEXT, COUNT(*),
           jsonb_build_object('mcp_tools', COUNT(*) FILTER (WHERE is_mcp_tool = true))
    FROM tool_templates WHERE is_active = true
    UNION ALL
    SELECT 'workflows'::TEXT, 'active'::TEXT, COUNT(*),
           jsonb_build_object('templates', COUNT(*) FILTER (WHERE is_template = true))
    FROM workflow_definitions WHERE status = 'active'
    UNION ALL
    SELECT 'users'::TEXT, 'total'::TEXT, COUNT(*),
           jsonb_build_object('verified', COUNT(*) FILTER (WHERE is_verified = true))
    FROM users WHERE is_active = true
    UNION ALL
    SELECT 'projects'::TEXT, 'total'::TEXT, COUNT(*),
           jsonb_build_object('default_project', COUNT(*) FILTER (WHERE is_default = true))
    FROM projects
    UNION ALL
    SELECT 'mcp_servers'::TEXT, 'active'::TEXT, COUNT(*),
           jsonb_build_object('healthy', COUNT(*) FILTER (WHERE health_status = 'healthy'))
    FROM mcp_servers WHERE status = 'active'
    UNION ALL
    SELECT 'vector_documents'::TEXT, 'total'::TEXT, COUNT(*),
           jsonb_build_object('with_embeddings', COUNT(*) FILTER (WHERE embedding IS NOT NULL))
    FROM document_embeddings;
END;
$ LANGUAGE plpgsql;

-- MCP system health check function
CREATE OR REPLACE FUNCTION check_mcp_system_health()
RETURNS TABLE(component TEXT, status TEXT, count BIGINT, details JSONB) AS $
BEGIN
    RETURN QUERY
    SELECT 'mcp_servers'::TEXT, 'active'::TEXT, COUNT(*), 
           jsonb_build_object('healthy', COUNT(*) FILTER (WHERE health_status = 'healthy'))
    FROM mcp_servers WHERE status = 'active'
    UNION ALL
    SELECT 'mcp_tools'::TEXT, 'available'::TEXT, COUNT(*),
           jsonb_build_object('total_executions', SUM(usage_count), 'avg_success_rate', AVG(success_rate))
    FROM mcp_tools_registry WHERE is_available = true;
END;
$ LANGUAGE plpgsql;

-- Update MCP tool usage statistics
CREATE OR REPLACE FUNCTION update_mcp_tool_usage_stats(
    p_tool_registry_id UUID,
    p_execution_time_ms INTEGER,
    p_success BOOLEAN
) RETURNS VOID AS $
BEGIN
    UPDATE mcp_tools_registry 
    SET 
        usage_count = usage_count + 1,
        avg_execution_time = CASE 
            WHEN usage_count = 0 THEN p_execution_time_ms
            ELSE (avg_execution_time * usage_count + p_execution_time_ms) / (usage_count + 1)
        END,
        success_rate = CASE
            WHEN usage_count = 0 THEN CASE WHEN p_success THEN 100.0 ELSE 0.0 END
            ELSE (success_rate * usage_count + CASE WHEN p_success THEN 100.0 ELSE 0.0 END) / (usage_count + 1)
        END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_tool_registry_id;
END;
$ LANGUAGE plpgsql;

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Insert default admin user
INSERT INTO users (
    email, username, first_name, last_name, hashed_password, role, is_active, is_verified
) VALUES (
    'admin@agenticai.local',
    'admin',
    'System',
    'Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LKO8F3ZH9VdGQ1oC6', -- password: admin123
    'ADMIN',
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- Insert default project
INSERT INTO projects (name, description, tags, is_default, created_by) 
SELECT 'Default Project', 'The default project for general use', ARRAY['general', 'default'], true, u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT (name) DO NOTHING;

-- Insert essential sample projects
INSERT INTO projects (name, description, tags, created_by) 
SELECT 'Customer Support', 'Customer service and support automation', ARRAY['support', 'customer', 'automation'], u.id
FROM users u WHERE u.username = 'admin'
UNION ALL
SELECT 'Data Analytics', 'Data analysis and reporting workflows', ARRAY['analytics', 'data', 'reporting'], u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT (name) DO NOTHING;

-- Insert essential LLM models
INSERT INTO llm_models (name, display_name, provider, model_type, supports_streaming, supports_functions, is_active, project_tags) VALUES
('gpt-4o', 'GPT-4o', 'openai', 'chat', true, true, true, ARRAY['general', 'default']),
('gpt-4o-mini', 'GPT-4o Mini', 'openai', 'chat', true, true, true, ARRAY['general', 'default']),
('gemini-1.5-pro', 'Gemini 1.5 Pro', 'google', 'chat', true, false, true, ARRAY['general', 'default']),
('text-embedding-3-small', 'OpenAI Text Embedding 3 Small', 'openai', 'embedding', false, false, true, ARRAY['general', 'default']),
('text-embedding-3-large', 'OpenAI Text Embedding 3 Large', 'openai', 'embedding', false, false, true, ARRAY['general', 'default'])
ON CONFLICT (name) DO NOTHING;

-- Update embedding model dimensions
UPDATE llm_models SET dimensions = 1536 WHERE name = 'text-embedding-3-small';
UPDATE llm_models SET dimensions = 3072 WHERE name = 'text-embedding-3-large';

-- Insert essential tool templates
INSERT INTO tool_templates (name, display_name, type, description, category, project_tags, tags, status, schema_definition, default_config, created_by) 
SELECT 
    'RAG Tool Template',
    'RAG Tool Template',
    'rag',
    'Retrieval-Augmented Generation tool for semantic search and knowledge retrieval',
    'AI/ML',
    ARRAY['general', 'default'],
    ARRAY['rag', 'retrieval', 'ai'],
    'active',
    '{
        "type": "object",
        "properties": {
            "vector_database": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["pgvector", "chroma", "pinecone"]},
                    "connection_string": {"type": "string"},
                    "collection_name": {"type": "string"}
                },
                "required": ["provider", "connection_string", "collection_name"]
            },
            "embedding_model": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["openai", "cohere", "huggingface"]},
                    "model_name": {"type": "string"},
                    "dimensions": {"type": "integer"}
                },
                "required": ["provider", "model_name"]
            }
        }
    }'::jsonb,
    '{
        "vector_database": {
            "provider": "pgvector",
            "collection_name": "documents"
        },
        "embedding_model": {
            "provider": "openai",
            "model_name": "text-embedding-3-small",
            "dimensions": 1536
        }
    }'::jsonb,
    u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT (name) DO NOTHING;

-- Insert essential agent templates
INSERT INTO agent_templates (name, description, framework, workflow_config, persona_config, tool_template_requirements, created_by) 
SELECT 
    'Research Assistant Agent',
    'An AI agent specialized in research tasks using RAG and web search capabilities',
    'langgraph',
    '{
        "nodes": [
            {"id": "question_analysis", "type": "llm", "prompt": "analyze_research_question"},
            {"id": "rag_search", "type": "tool", "tool_role": "primary_rag"},
            {"id": "synthesis", "type": "llm", "prompt": "synthesize_research"}
        ],
        "edges": [
            {"from": "question_analysis", "to": "rag_search"},
            {"from": "rag_search", "to": "synthesis"}
        ]
    }'::jsonb,
    '{
        "role": "Research Assistant",
        "personality": "Thorough, analytical, and precise researcher",
        "system_prompt": "You are a research assistant that helps users find and synthesize information from multiple sources.",
        "capabilities": ["research", "analysis", "synthesis", "fact_checking"],
        "communication_style": "Professional and detailed"
    }'::jsonb,
    '[{"template_name": "RAG Tool Template", "role": "primary_rag", "required": true}]'::jsonb,
    u.id
FROM users u WHERE u.username = 'admin'
ON CONFLICT (name) DO NOTHING;

-- Insert sample legacy agents for backward compatibility
INSERT INTO agents (name, display_name, description, url, health_url, category, ai_provider, model_name, tags, project_tags, author, organization, environment, llm_model_id, created_by) 
SELECT 
    'customer-service-agent',
    'Customer Service Agent',
    'AI agent for customer service interactions',
    'http://localhost:8002/a2a/agents/customer-service',
    'http://localhost:8002/health',
    'customer-service',
    'openai',
    'gpt-4o',
    ARRAY['customer', 'support', 'service'],
    ARRAY['support', 'customer'],
    'Platform Team',
    'Agentic AI Accelerator',
    'development',
    m.id,
    u.id
FROM users u, llm_models m 
WHERE u.username = 'admin' AND m.name = 'gpt-4o'
ON CONFLICT (name) DO NOTHING;

-- Insert sample workflow definitions
INSERT INTO workflow_definitions (name, display_name, description, category, tags, project_tags, steps, variables, llm_model_id, created_by) 
SELECT
    'customer-support-pipeline',
    'Customer Support Pipeline',
    'Automated customer inquiry processing',
    'customer-service',
    ARRAY['support', 'automation'],
    ARRAY['support', 'customer'],
    '[{"step": "classify", "agent": "customer-service-agent"}, {"step": "respond", "agent": "customer-service-agent"}]'::jsonb,
    '{"max_retries": 3}'::jsonb,
    m.id,
    u.id
FROM users u, llm_models m 
WHERE u.username = 'admin' AND m.name = 'gpt-4o'
ON CONFLICT (name) DO NOTHING;

-- Insert sample demo queries
INSERT INTO demo_sample_queries (service_type, category, query_text, description, complexity_level, is_featured, sort_order) VALUES
('agents', 'discovery', 'List all available agents', 'Get overview of available AI agents', 'beginner', true, 1),
('tools', 'discovery', 'Show available tool templates', 'Display tool templates for integration', 'beginner', true, 2),
('workflows', 'creation', 'Create basic workflow', 'Design a simple automation workflow', 'intermediate', true, 3),
('rag', 'search', 'Search knowledge base', 'Semantic search through documents', 'beginner', true, 4)
ON CONFLICT DO NOTHING;

-- Insert sample knowledge base content
INSERT INTO knowledge_base_embeddings (knowledge_item_id, title, content, category, tags, metadata) VALUES
('kb-001', 'Platform Overview', 'The Agentic AI Accelerator is a low-code/no-code multi-agent AI platform that enables users to create, deploy, and manage AI agents, tools, and workflows.', 'platform', ARRAY['overview', 'platform', 'introduction'], '{"type": "documentation", "version": "1.0"}'),
('kb-002', 'Agent Management', 'Agents are AI-powered entities that can perform specific tasks. They can be configured with different models, capabilities, and integration points.', 'agents', ARRAY['agents', 'management', 'configuration'], '{"type": "documentation", "section": "agents"}'),
('kb-003', 'Workflow Automation', 'Workflows enable the orchestration of multiple agents and tools to create complex automation pipelines with conditional logic and error handling.', 'workflows', ARRAY['workflows', 'automation', 'orchestration'], '{"type": "documentation", "section": "workflows"}')
ON CONFLICT (knowledge_item_id) DO NOTHING;

-- Update execution statistics with sample data
UPDATE agents SET 
    execution_count = FLOOR(RANDOM() * 500 + 50)::INTEGER,
    success_rate = ROUND((RANDOM() * 10 + 90)::numeric, 1),
    avg_response_time = FLOOR(RANDOM() * 2000 + 500)::INTEGER,
    last_executed = CURRENT_TIMESTAMP - (RANDOM() * INTERVAL '7 days')
WHERE name IN ('customer-service-agent');

UPDATE workflow_definitions SET 
    status = 'active'
WHERE name IN ('customer-support-pipeline');

-- Create foreign key constraint for tool_templates.mcp_server_id after mcp_servers table is ready
ALTER TABLE tool_templates ADD CONSTRAINT fk_tool_templates_mcp_server FOREIGN KEY (mcp_server_id) REFERENCES mcp_servers(id) ON DELETE SET NULL;

-- Update user's selected project to default project
UPDATE users SET selected_project_id = (SELECT id FROM projects WHERE is_default = true LIMIT 1) WHERE username = 'admin';

-- =====================================================
-- END OF UNIFIED SCHEMA
-- =====================================================

-- Final verification query to check system health
SELECT 'Schema installation completed successfully. Run check_platform_health() to verify system status.' as status;