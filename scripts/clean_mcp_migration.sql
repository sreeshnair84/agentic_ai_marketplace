-- Drop and recreate MCP tables if they exist
BEGIN;

-- Create or replace the update timestamp function (in case it doesn't exist)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing tables if they exist
DROP TABLE IF EXISTS mcp_execution_logs CASCADE;
DROP TABLE IF EXISTS mcp_endpoint_tool_bindings CASCADE;
DROP TABLE IF EXISTS mcp_endpoints CASCADE;
DROP TABLE IF EXISTS mcp_tools_registry CASCADE;
DROP TABLE IF EXISTS mcp_servers CASCADE;

-- MCP Servers table
CREATE TABLE mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    server_url TEXT NOT NULL,
    transport_type VARCHAR(50) NOT NULL DEFAULT 'http',
    status VARCHAR(50) DEFAULT 'inactive',
    health_status VARCHAR(50) DEFAULT 'unknown',
    version VARCHAR(50) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    capabilities JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    connection_config JSONB DEFAULT '{}',
    authentication_config JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MCP Tools Registry table
CREATE TABLE mcp_tools_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id UUID NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0.0',
    schema JSONB DEFAULT '{}',
    capabilities TEXT[] DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    avg_execution_time INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(server_id, tool_name)
);

-- MCP Endpoints table
CREATE TABLE mcp_endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    endpoint_path VARCHAR(500) NOT NULL,
    endpoint_url TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'inactive',
    is_public BOOLEAN DEFAULT false,
    authentication_required BOOLEAN DEFAULT true,
    allowed_methods TEXT[] DEFAULT ARRAY['POST'],
    rate_limit INTEGER,
    timeout_seconds INTEGER DEFAULT 30,
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- MCP Execution Logs table
CREATE TABLE mcp_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_id UUID REFERENCES mcp_endpoints(id) ON DELETE SET NULL,
    tool_id UUID REFERENCES mcp_tools_registry(id) ON DELETE SET NULL,
    execution_type VARCHAR(50) NOT NULL,
    input_parameters JSONB DEFAULT '{}',
    output_result JSONB,
    execution_status VARCHAR(50) NOT NULL,
    execution_time_ms INTEGER DEFAULT 0,
    error_message TEXT,
    user_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_execution_type CHECK (execution_type IN ('endpoint', 'tool')),
    CONSTRAINT chk_execution_status CHECK (execution_status IN ('success', 'error', 'timeout'))
);

-- Create indexes
CREATE INDEX idx_mcp_servers_status ON mcp_servers(status);
CREATE INDEX idx_mcp_servers_active ON mcp_servers(is_active);
CREATE INDEX idx_mcp_tools_server ON mcp_tools_registry(server_id);
CREATE INDEX idx_mcp_tools_available ON mcp_tools_registry(is_available);
CREATE INDEX idx_mcp_endpoints_status ON mcp_endpoints(status);
CREATE INDEX idx_mcp_logs_type ON mcp_execution_logs(execution_type);
CREATE INDEX idx_mcp_logs_status ON mcp_execution_logs(execution_status);

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_mcp_servers_updated_at 
    BEFORE UPDATE ON mcp_servers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_tools_registry_updated_at 
    BEFORE UPDATE ON mcp_tools_registry 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_endpoints_updated_at 
    BEFORE UPDATE ON mcp_endpoints 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert demo data
INSERT INTO mcp_servers (name, display_name, description, server_url, transport_type, status, health_status) VALUES
('demo-server', 'Demo MCP Server', 'A demonstration MCP server for testing', 'http://localhost:8001', 'http', 'active', 'healthy'),
('test-server', 'Test MCP Server', 'Test server for development', 'http://localhost:8002', 'http', 'inactive', 'unknown');

INSERT INTO mcp_endpoints (endpoint_name, display_name, description, endpoint_path, endpoint_url, status) VALUES
('demo-endpoint', 'Demo Endpoint', 'A demo endpoint for testing', '/demo', 'http://localhost:8000/api/mcp/gateway/demo', 'active'),
('test-endpoint', 'Test Endpoint', 'Test endpoint for development', '/test', 'http://localhost:8000/api/mcp/gateway/test', 'inactive');

-- Insert sample tools for the demo server
INSERT INTO mcp_tools_registry (server_id, tool_name, display_name, description, schema, capabilities, is_available) 
SELECT 
    s.id,
    'demo_tool',
    'Demo Tool',
    'A demonstration tool for testing MCP functionality',
    '{"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}'::jsonb,
    ARRAY['read', 'demo'],
    true
FROM mcp_servers s WHERE s.name = 'demo-server';

COMMIT;
