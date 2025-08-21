import { useState, useCallback } from 'react';

export interface MCPServer {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  server_url: string;
  transport_type: 'stdio' | 'http' | 'websocket' | 'sse';
  status: 'active' | 'inactive' | 'error';
  health_status?: 'healthy' | 'unhealthy' | 'degraded' | 'unknown';
  version: string;
  capabilities?: string[];
  tags?: string[];
  connection_config: any;
  authentication_config?: any;
  metadata?: any;
  created_at: string;
  updated_at: string;
  last_health_check?: string;
}

export interface MCPEndpoint {
  id: string;
  endpoint_name: string;
  display_name: string;
  description?: string;
  endpoint_path: string;
  endpoint_url: string;
  status: 'active' | 'inactive' | 'error';
  is_public: boolean;
  authentication_required: boolean;
  allowed_methods: string[];
  rate_limit?: number;
  timeout_seconds?: number;
  tags?: string[];
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface MCPTool {
  id: string;
  server_id: string;
  tool_name: string;
  display_name?: string;
  description?: string;
  version: string;
  schema: any;
  capabilities?: string[];
  usage_count: number;
  last_used?: string;
  success_rate: number;
  avg_execution_time: number;
  is_available: boolean;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface MCPExecutionLog {
  id: string;
  endpoint_id?: string;
  tool_id?: string;
  execution_type: 'endpoint' | 'tool';
  input_parameters: any;
  output_result?: any;
  execution_status: 'success' | 'error' | 'timeout';
  execution_time_ms: number;
  error_message?: string;
  user_id?: string;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useMCP() {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [endpoints, setEndpoints] = useState<MCPEndpoint[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [executionLogs, setExecutionLogs] = useState<MCPExecutionLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any, context: string) => {
    console.error(`Error in ${context}:`, err);
    setError(err.message || `Error in ${context}`);
    setTimeout(() => setError(null), 5000);
  };

  const apiRequest = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `HTTP ${response.status}`);
    }

    return response.json();
  };

  // MCP Servers
  const fetchServers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/v1/mcp/servers');
      setServers(data);
    } catch (err) {
      handleError(err, 'fetching servers');
    } finally {
      setLoading(false);
    }
  }, []);

  const createServer = useCallback(async (serverData: Partial<MCPServer>) => {
    try {
      const data = await apiRequest('/api/v1/mcp/servers', {
        method: 'POST',
        body: JSON.stringify(serverData),
      });
      return data;
    } catch (err) {
      handleError(err, 'creating server');
      throw err;
    }
  }, []);

  const updateServer = useCallback(async (serverId: string, serverData: Partial<MCPServer>) => {
    try {
      const data = await apiRequest(`/api/v1/mcp/servers/${serverId}`, {
        method: 'PUT',
        body: JSON.stringify(serverData),
      });
      return data;
    } catch (err) {
      handleError(err, 'updating server');
      throw err;
    }
  }, []);

  const deleteServer = useCallback(async (serverId: string) => {
    try {
      await apiRequest(`/api/v1/mcp/servers/${serverId}`, {
        method: 'DELETE',
      });
    } catch (err) {
      handleError(err, 'deleting server');
      throw err;
    }
  }, []);

  const testServerConnection = useCallback(async (serverId: string) => {
    try {
      const data = await apiRequest(`/api/v1/mcp/servers/${serverId}/test`, {
        method: 'POST',
      });
      return data;
    } catch (err) {
      handleError(err, 'testing server connection');
      throw err;
    }
  }, []);

  const discoverTools = useCallback(async (serverId: string) => {
    try {
      const data = await apiRequest(`/api/v1/mcp/servers/${serverId}/discover-tools`, {
        method: 'POST',
      });
      return data;
    } catch (err) {
      handleError(err, 'discovering tools');
      throw err;
    }
  }, []);

  // MCP Endpoints
  const fetchEndpoints = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/v1/mcp-gateway/endpoints');
      setEndpoints(data);
    } catch (err) {
      handleError(err, 'fetching endpoints');
    } finally {
      setLoading(false);
    }
  }, []);

  const createEndpoint = useCallback(async (endpointData: Partial<MCPEndpoint>) => {
    try {
      const data = await apiRequest('/api/v1/mcp-gateway/endpoints', {
        method: 'POST',
        body: JSON.stringify(endpointData),
      });
      return data;
    } catch (err) {
      handleError(err, 'creating endpoint');
      throw err;
    }
  }, []);

  const updateEndpoint = useCallback(async (endpointId: string, endpointData: Partial<MCPEndpoint>) => {
    try {
      const data = await apiRequest(`/api/v1/mcp-gateway/endpoints/${endpointId}`, {
        method: 'PUT',
        body: JSON.stringify(endpointData),
      });
      return data;
    } catch (err) {
      handleError(err, 'updating endpoint');
      throw err;
    }
  }, []);

  const deleteEndpoint = useCallback(async (endpointId: string) => {
    try {
      await apiRequest(`/api/v1/mcp-gateway/endpoints/${endpointId}`, {
        method: 'DELETE',
      });
    } catch (err) {
      handleError(err, 'deleting endpoint');
      throw err;
    }
  }, []);

  const executeEndpoint = useCallback(async (endpointName: string, parameters: any) => {
    try {
      const data = await apiRequest(`/api/v1/mcp-gateway/endpoints/${endpointName}/execute`, {
        method: 'POST',
        body: JSON.stringify({ parameters }),
      });
      return data;
    } catch (err) {
      handleError(err, 'executing endpoint');
      throw err;
    }
  }, []);

  // MCP Tools
  const fetchTools = useCallback(async (serverId?: string) => {
    try {
      setLoading(true);
      const url = serverId ? `/api/v1/mcp/tools?server_id=${serverId}` : '/api/v1/mcp/tools';
      const data = await apiRequest(url);
      setTools(data);
    } catch (err) {
      handleError(err, 'fetching tools');
    } finally {
      setLoading(false);
    }
  }, []);

  const testTool = useCallback(async (toolId: string, parameters: any) => {
    try {
      const data = await apiRequest(`/api/v1/mcp/tools/${toolId}/test`, {
        method: 'POST',
        body: JSON.stringify({ parameters }),
      });
      return data;
    } catch (err) {
      handleError(err, 'testing tool');
      throw err;
    }
  }, []);

  // Execution Logs
  const fetchExecutionLogs = useCallback(async () => {
    try {
      const data = await apiRequest('/api/v1/mcp-gateway/execution-logs');
      setExecutionLogs(data);
    } catch (err) {
      handleError(err, 'fetching execution logs');
    }
  }, []);

  // Tool Bindings
  const bindToolToEndpoint = useCallback(async (endpointId: string, toolId: string, config: any) => {
    try {
      const data = await apiRequest(`/api/v1/mcp-gateway/endpoints/${endpointId}/bind-tool`, {
        method: 'POST',
        body: JSON.stringify({ tool_id: toolId, binding_config: config }),
      });
      return data;
    } catch (err) {
      handleError(err, 'binding tool to endpoint');
      throw err;
    }
  }, []);

  const unbindToolFromEndpoint = useCallback(async (endpointId: string, toolId: string) => {
    try {
      await apiRequest(`/api/v1/mcp-gateway/endpoints/${endpointId}/unbind-tool`, {
        method: 'POST',
        body: JSON.stringify({ tool_id: toolId }),
      });
    } catch (err) {
      handleError(err, 'unbinding tool from endpoint');
      throw err;
    }
  }, []);

  return {
    // State
    servers,
    endpoints,
    tools,
    executionLogs,
    loading,
    error,

    // MCP Servers
    fetchServers,
    createServer,
    updateServer,
    deleteServer,
    testServerConnection,
    discoverTools,

    // MCP Endpoints
    fetchEndpoints,
    createEndpoint,
    updateEndpoint,
    deleteEndpoint,
    executeEndpoint,

    // MCP Tools
    fetchTools,
    testTool,

    // Execution Logs
    fetchExecutionLogs,

    // Tool Bindings
    bindToolToEndpoint,
    unbindToolFromEndpoint,
  };
}
