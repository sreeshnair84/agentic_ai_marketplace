import { useState, useEffect, useCallback } from 'react';

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'draft' | 'error';
  framework: 'crewai' | 'autogen' | 'langchain' | 'custom';
  capabilities: string[];
  performance: {
    tasksCompleted: number;
    successRate: number;
    avgResponseTime: number;
  };
  lastActivity: Date;
  owner: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateAgentData {
  name: string;
  description: string;
  framework: 'crewai' | 'autogen' | 'langchain' | 'custom';
  capabilities: string[];
  tags?: string[];
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
      const response = await fetch(`${API_BASE}/api/v1/agents/`);
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.statusText}`);
      }
      const data = await response.json();
      
      // Transform backend response to frontend format
      const transformedAgents = (data.agents || []).map((agent: any) => ({
        id: agent.name,
        name: agent.display_name || agent.name,
        description: agent.description,
        status: agent.status || 'inactive',
        framework: agent.ai_provider === 'gemini' ? 'custom' : (agent.ai_provider === 'openai' ? 'langchain' : 'crewai'),
        capabilities: [...(agent.tags || []), ...(agent.project_tags || [])], // Combine tags as capabilities
        performance: {
          tasksCompleted: agent.execution_count || 0,
          successRate: agent.success_rate || 0,
          avgResponseTime: 0, // Backend doesn't provide this in the list endpoint
        },
        lastActivity: new Date(agent.updated_at || Date.now()),
        owner: agent.author || 'system',
        tags: [...(agent.tags || []), ...(agent.project_tags || [])],
        created_at: agent.created_at || new Date().toISOString(),
        updated_at: agent.updated_at || new Date().toISOString(),
      }));
      
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
      const response = await fetch(`${API_BASE}/api/v1/agents/`, {
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
      const response = await fetch(`${API_BASE}/api/v1/agents/${agentId}`, {
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
      const response = await fetch(`${API_BASE}/api/v1/agents/${agentId}`, {
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
      const response = await fetch(`${API_BASE}/api/v1/agents/${agentId}/run`, {
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
      const response = await fetch(`${API_BASE}/api/v1/agents/${agentId}`);
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
      langchain: agents.filter(a => a.framework === 'langchain').length,
      custom: agents.filter(a => a.framework === 'custom').length,
    },
    avgSuccessRate: agents.length > 0 
      ? agents.reduce((sum, agent) => sum + agent.performance.successRate, 0) / agents.length 
      : 0,
    totalTasksCompleted: agents.reduce((sum, agent) => sum + agent.performance.tasksCompleted, 0),
  };

  return analytics;
}
