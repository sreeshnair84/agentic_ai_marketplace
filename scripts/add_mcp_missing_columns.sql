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
