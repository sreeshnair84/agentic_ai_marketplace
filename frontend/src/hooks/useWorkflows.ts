import { useState, useEffect, useCallback } from 'react';

export interface WorkflowData {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'running' | 'inactive' | 'paused' | 'draft' | 'error' | 'completed';
  category: 'automation' | 'data-processing' | 'ai-pipeline' | 'integration' | 'monitoring';
  complexity: 'simple' | 'moderate' | 'complex';
  execution: {
    totalRuns: number;
    successfulRuns: number;
    failedRuns: number;
    lastRun?: Date;
    nextScheduled?: Date;
    avgDuration: number; // in seconds
  };
  agents: Array<{
    id: string;
    name: string;
    role: string;
  }>;
  tools: Array<{
    id: string;
    name: string;
    type: string;
  }>;
  owner: string;
  tags: string[];
  schedule?: {
    type: 'manual' | 'scheduled' | 'triggered';
    cron?: string;
    triggers?: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface CreateWorkflowData {
  name: string;
  description: string;
  category: WorkflowData['category'];
  complexity?: WorkflowData['complexity'];
  agents?: WorkflowData['agents'];
  tools?: WorkflowData['tools'];
  tags?: string[];
  schedule?: WorkflowData['schedule'];
}

export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  started_at: Date;
  completed_at?: Date;
  duration?: number; // in seconds
  logs: Array<{
    timestamp: Date;
    level: 'info' | 'warning' | 'error';
    message: string;
    component?: string;
  }>;
  results?: Record<string, unknown>;
  error_message?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useWorkflows() {
  const [workflows, setWorkflows] = useState<WorkflowData[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/workflows`);
      if (!response.ok) {
        throw new Error(`Failed to fetch workflows: ${response.statusText}`);
      }
      const data = await response.json();
      console.log('Raw workflow API response:', data);
      
      // Transform backend data to frontend format
      const workflows = data.workflows || [];
      const transformedWorkflows = workflows.map((w: any) => ({
        id: w.name || w.id,
        name: w.display_name || w.name,
        description: w.description,
        status: w.status,
        category: w.category,
        complexity: 'simple', // Default since backend doesn't have this
        execution: {
          totalRuns: w.execution_count || 0,
          successfulRuns: w.success_rate ? Math.round((w.execution_count || 0) * (w.success_rate / 100)) : 0,
          failedRuns: w.execution_count ? (w.execution_count - (w.success_rate ? Math.round((w.execution_count || 0) * (w.success_rate / 100)) : 0)) : 0,
          lastRun: null,
          nextScheduled: null,
          avgDuration: 120 // Default
        },
        agents: [], // Default empty array
        tools: [], // Default empty array
        owner: 'system',
        tags: w.tags || [],
        schedule: {
          type: 'manual' as const,
          triggers: []
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }));
      
      console.log('Transformed workflows:', transformedWorkflows);
      setWorkflows(transformedWorkflows);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch workflows');
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchExecutions = useCallback(async (workflowId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = workflowId 
        ? `${API_BASE}/api/workflows/${workflowId}/executions`
        : `${API_BASE}/api/workflows/executions`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch executions: ${response.statusText}`);
      }
      const data = await response.json();
      setExecutions(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch executions');
      setExecutions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createWorkflow = useCallback(async (workflowData: CreateWorkflowData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create workflow');
      }

      const result = await response.json();
      await fetchWorkflows(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create workflow';
      return { success: false, error: errorMessage };
    }
  }, [fetchWorkflows]);

  const updateWorkflow = useCallback(async (workflowId: string, workflowData: Partial<CreateWorkflowData>): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to update workflow');
      }

      await fetchWorkflows(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update workflow';
      return { success: false, error: errorMessage };
    }
  }, [fetchWorkflows]);

  const deleteWorkflow = useCallback(async (workflowId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete workflow');
      }

      await fetchWorkflows(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete workflow';
      return { success: false, error: errorMessage };
    }
  }, [fetchWorkflows]);

  const executeWorkflow = useCallback(async (workflowId: string, params?: Record<string, unknown>): Promise<{ success: boolean; error?: string; executionId?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params || {}),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to execute workflow');
      }

      const result = await response.json();
      await fetchWorkflows(); // Refresh to get updated execution stats
      await fetchExecutions(); // Refresh executions
      return { 
        success: true, 
        executionId: result.executionId
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute workflow';
      return { success: false, error: errorMessage };
    }
  }, [fetchWorkflows, fetchExecutions]);

  const pauseWorkflow = useCallback(async (workflowId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/${workflowId}/pause`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to pause workflow');
      }

      await fetchWorkflows(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to pause workflow';
      return { success: false, error: errorMessage };
    }
  }, [fetchWorkflows]);

  const resumeWorkflow = useCallback(async (workflowId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/${workflowId}/resume`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to resume workflow');
      }

      await fetchWorkflows(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to resume workflow';
      return { success: false, error: errorMessage };
    }
  }, [fetchWorkflows]);

  const getWorkflow = useCallback(async (workflowId: string): Promise<WorkflowData | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/workflows/${workflowId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch workflow: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching workflow:', err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchWorkflows();
    fetchExecutions();
  }, [fetchWorkflows, fetchExecutions]);

  return {
    workflows,
    executions,
    loading,
    error,
    fetchWorkflows,
    fetchExecutions,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    executeWorkflow,
    pauseWorkflow,
    resumeWorkflow,
    getWorkflow,
  };
}

// Hook for workflow analytics
export function useWorkflowAnalytics() {
  const { workflows, executions } = useWorkflows();
  
  const analytics = {
    totalWorkflows: workflows.length,
    activeWorkflows: workflows.filter(w => w.status === 'active').length,
    pausedWorkflows: workflows.filter(w => w.status === 'paused').length,
    draftWorkflows: workflows.filter(w => w.status === 'draft').length,
    errorWorkflows: workflows.filter(w => w.status === 'error').length,
    categoryBreakdown: {
      automation: workflows.filter(w => w.category === 'automation').length,
      'data-processing': workflows.filter(w => w.category === 'data-processing').length,
      'ai-pipeline': workflows.filter(w => w.category === 'ai-pipeline').length,
      integration: workflows.filter(w => w.category === 'integration').length,
      monitoring: workflows.filter(w => w.category === 'monitoring').length,
    },
    complexityBreakdown: {
      simple: workflows.filter(w => w.complexity === 'simple').length,
      moderate: workflows.filter(w => w.complexity === 'moderate').length,
      complex: workflows.filter(w => w.complexity === 'complex').length,
    },
    executionStats: {
      totalExecutions: executions.length,
      runningExecutions: executions.filter(e => e.status === 'running').length,
      completedExecutions: executions.filter(e => e.status === 'completed').length,
      failedExecutions: executions.filter(e => e.status === 'failed').length,
      successRate: executions.length > 0 
        ? (executions.filter(e => e.status === 'completed').length / executions.length) * 100 
        : 0,
    },
    totalRuns: workflows.reduce((sum, w) => sum + w.execution.totalRuns, 0),
    totalSuccessfulRuns: workflows.reduce((sum, w) => sum + w.execution.successfulRuns, 0),
    totalFailedRuns: workflows.reduce((sum, w) => sum + w.execution.failedRuns, 0),
  };

  return analytics;
}
