import { useState, useEffect, useCallback } from 'react';

export interface Agent {
  id: string;
  name: string;
  display_name?: string;
  description: string;
  status: 'active' | 'inactive' | 'draft' | 'error';
  framework: 'langgraph' | 'crewai' | 'autogen' | 'semantic_kernel' | 'custom';
  capabilities: string[];
  performance: {
    tasksCompleted: number;
    successRate: number;
    avgResponseTime: number;
  };
  lastActivity: Date;
  owner: string;
  tags: string[];
  project_tags?: string[];
  created_at: string;
  updated_at: string;
  llm_model_id?: string;
  // Enhanced schema fields
  systemPrompt?: string;
  system_prompt?: string;
  temperature?: number;
  maxTokens?: number;
  max_tokens?: number;
  category?: string;
  agent_type?: string;
  version?: string;
  ai_provider?: string;
  model_name?: string;
  a2a_enabled?: boolean;
  a2a_address?: string;
  // Deployment fields
  url?: string;
  dns_name?: string;
  health_url?: string;
  environment?: string;
  author?: string;
  organization?: string;
  // Signature fields
  input_signature?: Record<string, any>;
  output_signature?: Record<string, any>;
  default_input_modes?: string[];
  default_output_modes?: string[];
  // Model configuration
  model_config_data?: Record<string, any>;
}

export interface CreateAgentData {
  name: string;
  display_name?: string;
  description: string;
  framework: 'langgraph' | 'crewai' | 'autogen' | 'semantic_kernel' | 'custom';
  capabilities: string[];
  tags?: string[];
  project_tags?: string[];
  llm_model_id?: string;
  systemPrompt?: string;
  system_prompt?: string;
  temperature?: number;
  maxTokens?: number;
  max_tokens?: number;
  category?: string;
  agent_type?: string;
  version?: string;
  a2a_enabled?: boolean;
  a2a_address?: string;
  // Deployment fields
  url?: string;
  dns_name?: string;
  health_url?: string;
  environment?: string;
  author?: string;
  organization?: string;
  // Signature fields
  input_signature?: Record<string, any>;
  output_signature?: Record<string, any>;
  default_input_modes?: string[];
  default_output_modes?: string[];
  // Model configuration
  model_config_data?: Record<string, any>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/agents`);
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.statusText}`);
      }
      const data = await response.json();
      console.log('Raw agent data received:', data);
      
      // Transform backend response to frontend format
      const transformedAgents = (data.agents || []).map((agent: any) => {
        console.log('Transforming agent:', agent);
        return {
        id: agent.id || agent.name,
        name: agent.name || agent.display_name,
        description: agent.description || 'No description available',
        status: agent.status || 'inactive',
        framework: agent.framework || (agent.ai_provider === 'gemini' ? 'custom' : (agent.ai_provider === 'openai' ? 'langchain' : 'crewai')),
        capabilities: agent.skills || [...(agent.tags || []), ...(agent.project_tags || [])], // Use skills if available, otherwise combine tags
        performance: {
          tasksCompleted: agent.executionCount || agent.execution_count || 0,
          successRate: agent.success_rate || 0,
          avgResponseTime: agent.responseTime || 0,
        },
        lastActivity: new Date(agent.lastExecutedAt || agent.updated_at || Date.now()),
        owner: agent.author || 'system',
        tags: agent.tags || [...(agent.tags || []), ...(agent.project_tags || [])],
        created_at: agent.createdAt || agent.created_at || new Date().toISOString(),
        updated_at: agent.updatedAt || agent.updated_at || new Date().toISOString(),
        };
      });
      
      console.log('Transformed agents:', transformedAgents);
      
      setAgents(transformedAgents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agents');
      setAgents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createAgent = useCallback(async (agentData: CreateAgentData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      // Use the agents service directly for CRUD operations
      const AGENTS_SERVICE_URL = process.env.NEXT_PUBLIC_AGENTS_URL || `${API_BASE.replace(':8000', ':8002')}`;
      const response = await fetch(`${AGENTS_SERVICE_URL}/agents/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create agent');
      }

      const result = await response.json();
      await fetchAgents(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create agent';
      return { success: false, error: errorMessage };
    }
  }, [fetchAgents]);

  const updateAgent = useCallback(async (agentId: string, agentData: Partial<CreateAgentData>): Promise<{ success: boolean; error?: string }> => {
    try {
      const AGENTS_SERVICE_URL = process.env.NEXT_PUBLIC_AGENTS_URL || `${API_BASE.replace(':8000', ':8002')}`;
      const response = await fetch(`${AGENTS_SERVICE_URL}/agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to update agent');
      }

      await fetchAgents(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update agent';
      return { success: false, error: errorMessage };
    }
  }, [fetchAgents]);

  const deleteAgent = useCallback(async (agentId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const AGENTS_SERVICE_URL = process.env.NEXT_PUBLIC_AGENTS_URL || `${API_BASE.replace(':8000', ':8002')}`;
      const response = await fetch(`${AGENTS_SERVICE_URL}/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete agent');
      }

      await fetchAgents(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete agent';
      return { success: false, error: errorMessage };
    }
  }, [fetchAgents]);

  const runAgent = useCallback(async (agentId: string, taskData?: any): Promise<{ success: boolean; error?: string; taskId?: string }> => {
    try {
      const AGENTS_SERVICE_URL = process.env.NEXT_PUBLIC_AGENTS_URL || `${API_BASE.replace(':8000', ':8002')}`;
      const response = await fetch(`${AGENTS_SERVICE_URL}/agents/${agentId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData || {}),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to run agent');
      }

      const result = await response.json();
      await fetchAgents(); // Refresh to get updated performance metrics
      return { 
        success: true, 
        taskId: result.taskId
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to run agent';
      return { success: false, error: errorMessage };
    }
  }, [fetchAgents]);

  const getAgent = useCallback(async (agentId: string): Promise<Agent | null> => {
    try {
      const AGENTS_SERVICE_URL = process.env.NEXT_PUBLIC_AGENTS_URL || `${API_BASE.replace(':8000', ':8002')}`;
      const response = await fetch(`${AGENTS_SERVICE_URL}/agents/${agentId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch agent: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching agent:', err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return {
    agents,
    loading,
    error,
    fetchAgents,
    createAgent,
    updateAgent,
    deleteAgent,
    runAgent,
    getAgent,
  };
}

// Hook for agent analytics
export function useAgentAnalytics() {
  const { agents } = useAgents();
  
  const analytics = {
    totalAgents: agents.length,
    activeAgents: agents.filter(a => a.status === 'active').length,
    inactiveAgents: agents.filter(a => a.status === 'inactive').length,
    draftAgents: agents.filter(a => a.status === 'draft').length,
    errorAgents: agents.filter(a => a.status === 'error').length,
    frameworkBreakdown: {
      crewai: agents.filter(a => a.framework === 'crewai').length,
      autogen: agents.filter(a => a.framework === 'autogen').length,
      langgraph: agents.filter(a => a.framework === 'langgraph').length,
      semantic_kernel: agents.filter(a => a.framework === 'semantic_kernel').length,
      custom: agents.filter(a => a.framework === 'custom').length,
    },
    avgSuccessRate: agents.length > 0 
      ? agents.reduce((sum, agent) => sum + agent.performance.successRate, 0) / agents.length 
      : 0,
    totalTasksCompleted: agents.reduce((sum, agent) => sum + agent.performance.tasksCompleted, 0),
  };

  return analytics;
}
