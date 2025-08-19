-- =====================================================
-- AgenticAI PLATFORM - COMPLETE DATABASE SCHEMA
-- Consolidated Migration: All core tables and functionality
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- CORE PLATFORM TABLES
-- =====================================================

-- Agents table - Core AI agents
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Tools table - Core tools and integrations
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Workflows table - Automation workflows
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
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- RAG Documents table - Document storage for retrieval
CREATE TABLE IF NOT EXISTS rag_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Observability traces table - System monitoring
CREATE TABLE IF NOT EXISTS observability_traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    duration INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Observability spans table - Detailed monitoring
CREATE TABLE IF NOT EXISTS observability_spans (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(255) NOT NULL,
    span_id VARCHAR(255) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PROJECTS AND ORGANIZATION
-- =====================================================

-- Projects table - Project organization
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

-- User Projects Association table
CREATE TABLE IF NOT EXISTS user_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ADVANCED TOOLS AND WORKFLOWS SYSTEM
-- =====================================================

-- Tool Templates table - Advanced tool definitions
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
    status VARCHAR(50) DEFAULT 'inactive',
    configuration JSONB DEFAULT '{}',
    environment_scope VARCHAR(50) DEFAULT 'development',
    project_tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- LLM Models table
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

-- Embedding Models table
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

-- Workflow Definitions table
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

-- Workflow Templates table
CREATE TABLE IF NOT EXISTS workflow_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    template_definition JSONB NOT NULL,
    parameters JSONB DEFAULT '[]',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

-- Workflow Schedules table
CREATE TABLE IF NOT EXISTS workflow_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definitions(id) ON DELETE CASCADE,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255)
);

-- =====================================================
-- USER AUTHENTICATION AND AUTHORIZATION
-- =====================================================

-- Users table
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

-- Sample queries table 
CREATE TABLE IF NOT EXISTS demo_sample_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    query_text TEXT NOT NULL,
    description TEXT,
    complexity_level VARCHAR(20) DEFAULT 'beginner',
    tags TEXT[],
    is_featured BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

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

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_tags ON projects USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_projects_is_default ON projects(is_default);

-- Tool templates indexes
CREATE INDEX IF NOT EXISTS idx_tool_templates_project_tags ON tool_templates USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_tool_templates_category ON tool_templates(category);
CREATE INDEX IF NOT EXISTS idx_tool_templates_is_active ON tool_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_tool_templates_status ON tool_templates(status);

-- Tool instances indexes
CREATE INDEX IF NOT EXISTS idx_tool_instances_project_tags ON tool_instances USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_tool_instances_template_id ON tool_instances(tool_template_id);
CREATE INDEX IF NOT EXISTS idx_tool_instances_status ON tool_instances(status);

-- LLM models indexes
CREATE INDEX IF NOT EXISTS idx_llm_models_project_tags ON llm_models USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_llm_models_provider ON llm_models(provider);
CREATE INDEX IF NOT EXISTS idx_llm_models_is_active ON llm_models(is_active);

-- Embedding models indexes
CREATE INDEX IF NOT EXISTS idx_embedding_models_project_tags ON embedding_models USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_embedding_models_provider ON embedding_models(provider);
CREATE INDEX IF NOT EXISTS idx_embedding_models_is_active ON embedding_models(is_active);

-- Workflow definitions indexes
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_project_tags ON workflow_definitions USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_category ON workflow_definitions(category);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_status ON workflow_definitions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_definitions_is_template ON workflow_definitions(is_template);

-- Workflow executions indexes
CREATE INDEX IF NOT EXISTS idx_workflow_executions_project_tags ON workflow_executions USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_created_at ON workflow_executions(created_at DESC);

-- Workflow templates indexes
CREATE INDEX IF NOT EXISTS idx_workflow_templates_project_tags ON workflow_templates USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_category ON workflow_templates(category);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_is_active ON workflow_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_usage_count ON workflow_templates(usage_count DESC);

-- Workflow schedules indexes
CREATE INDEX IF NOT EXISTS idx_workflow_schedules_project_tags ON workflow_schedules USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_workflow_schedules_workflow_id ON workflow_schedules(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_schedules_is_active ON workflow_schedules(is_active);
CREATE INDEX IF NOT EXISTS idx_workflow_schedules_next_run_at ON workflow_schedules(next_run_at);

-- Association tables indexes
CREATE INDEX IF NOT EXISTS idx_workflow_agents_workflow_id ON workflow_agents(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_agents_agent_id ON workflow_agents(agent_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON user_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_project_id ON user_projects(project_id);

-- Users and auth indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_demo_sample_queries_service_type ON demo_sample_queries(service_type);
CREATE INDEX IF NOT EXISTS idx_demo_sample_queries_featured ON demo_sample_queries(is_featured);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

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
