-- Migration: MCP Registry and Gateway System
-- Description: Adds MCP (Model Context Protocol) registry and gateway functionality
-- Version: 0006
-- Date: 2025-08-21

BEGIN;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create or replace the update timestamp function (in case it doesn't exist)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- MCP REGISTRY TABLES
-- =====================================================

-- MCP Servers table - Registry of MCP servers
CREATE TABLE IF NOT EXISTS mcp_servers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    server_url VARCHAR(500) NOT NULL,
    transport_type VARCHAR(50) DEFAULT 'streamable' CHECK (transport_type IN ('streamable', 'sse', 'stdio')),
    authentication_config JSONB DEFAULT '{}', -- Auth configuration (API keys, OAuth, etc.)
    capabilities JSONB DEFAULT '{}', -- Server capabilities and features
    version VARCHAR(50) DEFAULT '1.0.0',
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'testing')),
    health_check_url VARCHAR(500),
    health_status VARCHAR(50) DEFAULT 'unknown' CHECK (health_status IN ('healthy', 'unhealthy', 'unknown', 'degraded')),
    last_health_check TIMESTAMP WITH TIME ZONE,
    connection_config JSONB DEFAULT '{}', -- Connection settings, timeouts, retries
    metadata JSONB DEFAULT '{}', -- Additional server metadata
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- MCP Tools Registry table - Catalog of discovered MCP tools
CREATE TABLE IF NOT EXISTS mcp_tools_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    server_id UUID NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    input_schema JSONB NOT NULL DEFAULT '{}', -- JSON Schema for tool inputs
    output_schema JSONB DEFAULT '{}', -- JSON Schema for tool outputs
    tool_config JSONB DEFAULT '{}', -- Tool-specific configuration
    capabilities TEXT[] DEFAULT '{}', -- Tool capabilities (read, write, etc.)
    resource_requirements JSONB DEFAULT '{}', -- Memory, CPU, timeout requirements
    examples JSONB DEFAULT '[]', -- Example usage and responses
    documentation_url VARCHAR(500),
    version VARCHAR(50) DEFAULT '1.0.0',
    is_available BOOLEAN DEFAULT true,
    last_discovered TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_execution_time INTEGER DEFAULT 0, -- milliseconds
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_tool_per_server UNIQUE (server_id, tool_name)
);

-- =====================================================
-- MCP GATEWAY TABLES
-- =====================================================

-- MCP Endpoints table - Dynamic MCP endpoints
CREATE TABLE IF NOT EXISTS mcp_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint_name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    endpoint_path VARCHAR(255) NOT NULL UNIQUE, -- e.g., /mcp/custom-endpoint
    endpoint_url VARCHAR(500) NOT NULL, -- Full URL for the endpoint
    transport_config JSONB NOT NULL DEFAULT '{}', -- Transport-specific configuration
    authentication_required BOOLEAN DEFAULT false,
    authentication_config JSONB DEFAULT '{}', -- Auth requirements for this endpoint
    rate_limiting JSONB DEFAULT '{}', -- Rate limiting configuration
    timeout_config JSONB DEFAULT '{}', -- Timeout settings
    middleware_config JSONB DEFAULT '[]', -- Middleware pipeline configuration
    status VARCHAR(50) DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'draft', 'error')),
    health_status VARCHAR(50) DEFAULT 'unknown' CHECK (health_status IN ('healthy', 'unhealthy', 'unknown', 'degraded')),
    last_health_check TIMESTAMP WITH TIME ZONE,
    usage_analytics JSONB DEFAULT '{}', -- Usage statistics and analytics
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    project_tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- MCP Endpoint Tool Bindings table - Link tools to endpoints
CREATE TABLE IF NOT EXISTS mcp_endpoint_tool_bindings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint_id UUID NOT NULL REFERENCES mcp_endpoints(id) ON DELETE CASCADE,
    tool_registry_id UUID REFERENCES mcp_tools_registry(id) ON DELETE CASCADE,
    server_id UUID REFERENCES mcp_servers(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    binding_name VARCHAR(255), -- Alias for the tool in this endpoint
    binding_config JSONB DEFAULT '{}', -- Tool-specific binding configuration
    parameter_mapping JSONB DEFAULT '{}', -- Input/output parameter mapping
    middleware_config JSONB DEFAULT '[]', -- Tool-specific middleware
    execution_order INTEGER DEFAULT 0,
    is_enabled BOOLEAN DEFAULT true,
    conditional_execution JSONB DEFAULT '{}', -- Conditions for tool execution
    error_handling JSONB DEFAULT '{}', -- Error handling configuration
    retry_config JSONB DEFAULT '{}', -- Retry configuration
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_binding_per_endpoint UNIQUE (endpoint_id, binding_name)
);

-- MCP Execution Logs table - Track tool executions
CREATE TABLE IF NOT EXISTS mcp_execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint_id UUID REFERENCES mcp_endpoints(id) ON DELETE SET NULL,
    binding_id UUID REFERENCES mcp_endpoint_tool_bindings(id) ON DELETE SET NULL,
    server_id UUID REFERENCES mcp_servers(id) ON DELETE SET NULL,
    tool_name VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255) NOT NULL, -- Unique execution identifier
    request_data JSONB DEFAULT '{}', -- Input parameters
    response_data JSONB DEFAULT '{}', -- Tool output
    execution_status VARCHAR(50) DEFAULT 'pending' CHECK (execution_status IN ('pending', 'running', 'completed', 'failed', 'timeout', 'cancelled')),
    error_details JSONB DEFAULT '{}', -- Error information if failed
    execution_time_ms INTEGER, -- Execution time in milliseconds
    resource_usage JSONB DEFAULT '{}', -- CPU, memory usage
    user_context JSONB DEFAULT '{}', -- User context and permissions
    trace_id VARCHAR(255), -- Distributed tracing ID
    span_id VARCHAR(255), -- Span ID for tracing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MCP Tool Test Results table - Store test execution results
CREATE TABLE IF NOT EXISTS mcp_tool_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_registry_id UUID REFERENCES mcp_tools_registry(id) ON DELETE CASCADE,
    server_id UUID NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    test_description TEXT,
    test_input JSONB NOT NULL DEFAULT '{}',
    expected_output JSONB DEFAULT '{}',
    actual_output JSONB DEFAULT '{}',
    test_status VARCHAR(50) DEFAULT 'pending' CHECK (test_status IN ('pending', 'running', 'passed', 'failed', 'error')),
    error_details TEXT,
    execution_time_ms INTEGER,
    assertions JSONB DEFAULT '[]', -- Test assertions and their results
    test_config JSONB DEFAULT '{}', -- Test configuration
    run_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- EXTEND EXISTING TABLES FOR MCP SUPPORT
-- =====================================================

-- Add MCP-specific columns to tool_templates
ALTER TABLE tool_templates ADD COLUMN IF NOT EXISTS mcp_server_id UUID REFERENCES mcp_servers(id) ON DELETE SET NULL;
ALTER TABLE tool_templates ADD COLUMN IF NOT EXISTS mcp_tool_name VARCHAR(255);
ALTER TABLE tool_templates ADD COLUMN IF NOT EXISTS mcp_binding_config JSONB DEFAULT '{}';
ALTER TABLE tool_templates ADD COLUMN IF NOT EXISTS is_mcp_tool BOOLEAN DEFAULT false;

-- Add MCP-specific columns to tool_instances
ALTER TABLE tool_instances ADD COLUMN IF NOT EXISTS mcp_endpoint_id UUID REFERENCES mcp_endpoints(id) ON DELETE SET NULL;
ALTER TABLE tool_instances ADD COLUMN IF NOT EXISTS mcp_binding_id UUID REFERENCES mcp_endpoint_tool_bindings(id) ON DELETE SET NULL;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- MCP Servers indexes
CREATE INDEX IF NOT EXISTS idx_mcp_servers_status ON mcp_servers(status);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_health_status ON mcp_servers(health_status);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_project_tags ON mcp_servers USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_transport_type ON mcp_servers(transport_type);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_active ON mcp_servers(is_active);

-- MCP Tools Registry indexes
CREATE INDEX IF NOT EXISTS idx_mcp_tools_server_id ON mcp_tools_registry(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_tool_name ON mcp_tools_registry(tool_name);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_available ON mcp_tools_registry(is_available);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_last_discovered ON mcp_tools_registry(last_discovered);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_usage_count ON mcp_tools_registry(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_tools_success_rate ON mcp_tools_registry(success_rate DESC);

-- MCP Endpoints indexes
CREATE INDEX IF NOT EXISTS idx_mcp_endpoints_status ON mcp_endpoints(status);
CREATE INDEX IF NOT EXISTS idx_mcp_endpoints_health_status ON mcp_endpoints(health_status);
CREATE INDEX IF NOT EXISTS idx_mcp_endpoints_project_tags ON mcp_endpoints USING GIN(project_tags);
CREATE INDEX IF NOT EXISTS idx_mcp_endpoints_public ON mcp_endpoints(is_public);
CREATE INDEX IF NOT EXISTS idx_mcp_endpoints_path ON mcp_endpoints(endpoint_path);

-- MCP Bindings indexes
CREATE INDEX IF NOT EXISTS idx_mcp_bindings_endpoint_id ON mcp_endpoint_tool_bindings(endpoint_id);
CREATE INDEX IF NOT EXISTS idx_mcp_bindings_tool_registry_id ON mcp_endpoint_tool_bindings(tool_registry_id);
CREATE INDEX IF NOT EXISTS idx_mcp_bindings_server_id ON mcp_endpoint_tool_bindings(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_bindings_enabled ON mcp_endpoint_tool_bindings(is_enabled);
CREATE INDEX IF NOT EXISTS idx_mcp_bindings_execution_order ON mcp_endpoint_tool_bindings(execution_order);

-- MCP Execution Logs indexes
CREATE INDEX IF NOT EXISTS idx_mcp_execution_endpoint_id ON mcp_execution_logs(endpoint_id);
CREATE INDEX IF NOT EXISTS idx_mcp_execution_server_id ON mcp_execution_logs(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_execution_status ON mcp_execution_logs(execution_status);
CREATE INDEX IF NOT EXISTS idx_mcp_execution_started_at ON mcp_execution_logs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_execution_execution_id ON mcp_execution_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_mcp_execution_trace_id ON mcp_execution_logs(trace_id);

-- MCP Test Results indexes
CREATE INDEX IF NOT EXISTS idx_mcp_test_tool_registry_id ON mcp_tool_test_results(tool_registry_id);
CREATE INDEX IF NOT EXISTS idx_mcp_test_server_id ON mcp_tool_test_results(server_id);
CREATE INDEX IF NOT EXISTS idx_mcp_test_status ON mcp_tool_test_results(test_status);
CREATE INDEX IF NOT EXISTS idx_mcp_test_created_at ON mcp_tool_test_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_mcp_test_run_by ON mcp_tool_test_results(run_by);

-- Extended table indexes
CREATE INDEX IF NOT EXISTS idx_tool_templates_mcp_server ON tool_templates(mcp_server_id);
CREATE INDEX IF NOT EXISTS idx_tool_templates_is_mcp ON tool_templates(is_mcp_tool);
CREATE INDEX IF NOT EXISTS idx_tool_instances_mcp_endpoint ON tool_instances(mcp_endpoint_id);
CREATE INDEX IF NOT EXISTS idx_tool_instances_mcp_binding ON tool_instances(mcp_binding_id);

-- =====================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =====================================================

CREATE TRIGGER update_mcp_servers_updated_at BEFORE UPDATE ON mcp_servers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcp_tools_registry_updated_at BEFORE UPDATE ON mcp_tools_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcp_endpoints_updated_at BEFORE UPDATE ON mcp_endpoints FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mcp_endpoint_tool_bindings_updated_at BEFORE UPDATE ON mcp_endpoint_tool_bindings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to check MCP system health
CREATE OR REPLACE FUNCTION check_mcp_system_health()
RETURNS TABLE(component TEXT, status TEXT, count BIGINT, details JSONB) AS $$
BEGIN
    RETURN QUERY
    SELECT 'mcp_servers'::TEXT, 'active'::TEXT, COUNT(*), 
           jsonb_build_object('healthy', COUNT(*) FILTER (WHERE health_status = 'healthy'))
    FROM mcp_servers WHERE status = 'active'
    UNION ALL
    SELECT 'mcp_tools'::TEXT, 'available'::TEXT, COUNT(*),
           jsonb_build_object('total_executions', SUM(usage_count), 'avg_success_rate', AVG(success_rate))
    FROM mcp_tools_registry WHERE is_available = true
    UNION ALL
    SELECT 'mcp_endpoints'::TEXT, 'active'::TEXT, COUNT(*),
           jsonb_build_object('public_endpoints', COUNT(*) FILTER (WHERE is_public = true))
    FROM mcp_endpoints WHERE status = 'active'
    UNION ALL
    SELECT 'mcp_executions_today'::TEXT, 'completed'::TEXT, COUNT(*),
           jsonb_build_object('success_rate', 
               ROUND((COUNT(*) FILTER (WHERE execution_status = 'completed')::DECIMAL / COUNT(*)) * 100, 2)
           )
    FROM mcp_execution_logs 
    WHERE started_at >= CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Function to update tool usage statistics
CREATE OR REPLACE FUNCTION update_mcp_tool_usage_stats(
    p_tool_registry_id UUID,
    p_execution_time_ms INTEGER,
    p_success BOOLEAN
) RETURNS VOID AS $$
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
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA FOR DEVELOPMENT
-- =====================================================

-- Insert sample MCP servers
INSERT INTO mcp_servers (name, display_name, description, server_url, transport_type, status, is_active) VALUES
(
    'azure-mcp-server',
    'Azure MCP Server',
    'Official Azure MCP server for interacting with Azure resources',
    'https://azure-mcp.example.com',
    'streamable',
    'active',
    true
),
(
    'local-file-server',
    'Local File MCP Server',
    'MCP server for local file operations and management',
    'http://localhost:8001/mcp',
    'streamable',
    'inactive',
    true
),
(
    'database-mcp-server',
    'Database MCP Server',
    'MCP server for database query and management operations',
    'https://db-mcp.example.com',
    'sse',
    'active',
    true
) ON CONFLICT (name) DO NOTHING;

-- Insert sample MCP tools (assuming the servers above exist)
INSERT INTO mcp_tools_registry (server_id, tool_name, display_name, description, input_schema, capabilities)
SELECT 
    s.id,
    'azure_vm_list',
    'List Azure VMs',
    'List virtual machines in Azure subscription',
    '{"type": "object", "properties": {"subscription_id": {"type": "string"}, "resource_group": {"type": "string"}}, "required": ["subscription_id"]}'::jsonb,
    ARRAY['read', 'azure']
FROM mcp_servers s WHERE s.name = 'azure-mcp-server'
UNION ALL
SELECT 
    s.id,
    'file_read',
    'Read File',
    'Read contents of a local file',
    '{"type": "object", "properties": {"file_path": {"type": "string"}, "encoding": {"type": "string", "default": "utf-8"}}, "required": ["file_path"]}'::jsonb,
    ARRAY['read', 'file']
FROM mcp_servers s WHERE s.name = 'local-file-server'
UNION ALL
SELECT 
    s.id,
    'sql_query',
    'Execute SQL Query',
    'Execute SQL query against database',
    '{"type": "object", "properties": {"query": {"type": "string"}, "database": {"type": "string"}}, "required": ["query"]}'::jsonb,
    ARRAY['read', 'write', 'database']
FROM mcp_servers s WHERE s.name = 'database-mcp-server'
ON CONFLICT (server_id, tool_name) DO NOTHING;

COMMIT;

-- Migration to add missing MCP columns
-- This adds project_tags and last_health_check columns to match the API expectations

-- Add project_tags column to mcp_servers
ALTER TABLE mcp_servers 
ADD COLUMN IF NOT EXISTS project_tags TEXT[] DEFAULT '{}';

-- Add last_health_check column to mcp_servers  
ALTER TABLE mcp_servers 
ADD COLUMN IF NOT EXISTS last_health_check TIMESTAMP WITH TIME ZONE;

-- Update existing servers to have some sample project_tags
UPDATE mcp_servers 
SET project_tags = ARRAY['demo', 'development'] 
WHERE name = 'demo-server';

UPDATE mcp_servers 
SET project_tags = ARRAY['test', 'development'] 
WHERE name = 'test-server';

-- Update last_health_check to current time for active servers
UPDATE mcp_servers 
SET last_health_check = CURRENT_TIMESTAMP 
WHERE status = 'active';

COMMIT;
