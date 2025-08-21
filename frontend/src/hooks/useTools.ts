import { useState, useEffect, useCallback } from 'react';

export interface ToolTemplate {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: 'mcp' | 'custom' | 'api' | 'llm' | 'rag' | 'workflow';
  tags?: string[];
  fields?: ToolTemplateField[];
  created_at: string;
  updated_at: string;
}

export interface ToolTemplateField {
  id: string;
  field_name: string;
  field_label: string;
  field_type: string;
  field_description: string;
  is_required: boolean;
  default_value?: string;
}

export interface ToolInstance {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: 'mcp' | 'custom' | 'api' | 'llm' | 'rag' | 'workflow';
  status: 'active' | 'inactive' | 'error' | 'testing';
  environment_scope: 'development' | 'staging' | 'production' | 'global';
  configuration: Record<string, any>;
  tags?: string[];
  template_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateToolTemplateData {
  name: string;
  display_name: string;
  description: string;
  category: ToolTemplate['category'];
  tags?: string[];
  fields?: Omit<ToolTemplateField, 'id'>[];
}

export interface CreateToolInstanceData {
  name: string;
  display_name: string;
  description: string;
  category: ToolInstance['category'];
  status?: ToolInstance['status'];
  environment_scope: ToolInstance['environment_scope'];
  configuration: Record<string, any>;
  tags?: string[];
  template_id?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useTools() {
  const [toolTemplates, setToolTemplates] = useState<ToolTemplate[]>([]);
  const [toolInstances, setToolInstances] = useState<ToolInstance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchToolTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/tools/templates`);
      if (!response.ok) {
        throw new Error(`Failed to fetch tool templates: ${response.statusText}`);
      }
      const data = await response.json();
      setToolTemplates(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tool templates');
      setToolTemplates([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchToolInstances = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/tools/instances`);
      if (!response.ok) {
        throw new Error(`Failed to fetch tool instances: ${response.statusText}`);
      }
      const data = await response.json();
      setToolInstances(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tool instances');
      setToolInstances([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchData = useCallback(async () => {
    await Promise.all([fetchToolTemplates(), fetchToolInstances()]);
  }, [fetchToolTemplates, fetchToolInstances]);

  const createTemplate = useCallback(async (templateData: CreateToolTemplateData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create template');
      }

      const result = await response.json();
      await fetchToolTemplates(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create template';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolTemplates]);

  const updateTemplate = useCallback(async (templateId: string, templateData: Partial<CreateToolTemplateData>): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/templates/${templateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to update template');
      }

      await fetchToolTemplates(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update template';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolTemplates]);

  const deleteTemplate = useCallback(async (templateId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/templates/${templateId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete template');
      }

      await fetchToolTemplates(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete template';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolTemplates]);

  const createInstance = useCallback(async (instanceData: CreateToolInstanceData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/instances`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(instanceData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create instance');
      }

      const result = await response.json();
      await fetchToolInstances(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create instance';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolInstances]);

  const updateInstance = useCallback(async (instanceId: string, instanceData: Partial<CreateToolInstanceData>): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/instances/${instanceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(instanceData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to update instance');
      }

      await fetchToolInstances(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update instance';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolInstances]);

  const deleteInstance = useCallback(async (instanceId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/instances/${instanceId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete instance');
      }

      await fetchToolInstances(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete instance';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolInstances]);

  const testInstance = useCallback(async (instanceId: string): Promise<{ success: boolean; error?: string; result?: any }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/instances/${instanceId}/test`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to test instance');
      }

      const result = await response.json();
      await fetchToolInstances(); // Refresh to get updated status
      return { 
        success: result.success, 
        error: result.success ? undefined : result.message,
        result: result.data
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to test instance';
      return { success: false, error: errorMessage };
    }
  }, [fetchToolInstances]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    toolTemplates,
    toolInstances,
    loading,
    error,
    fetchData,
    fetchToolTemplates,
    fetchToolInstances,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    createInstance,
    updateInstance,
    deleteInstance,
    testInstance,
  };
}

// Hook for tool analytics
export function useToolAnalytics() {
  const { toolTemplates, toolInstances } = useTools();
  
  const analytics = {
    totalTemplates: toolTemplates.length,
    totalInstances: toolInstances.length,
    activeInstances: toolInstances.filter(i => i.status === 'active').length,
    errorInstances: toolInstances.filter(i => i.status === 'error').length,
    categoryBreakdown: {
      mcp: toolInstances.filter(i => i.category === 'mcp').length,
      custom: toolInstances.filter(i => i.category === 'custom').length,
      api: toolInstances.filter(i => i.category === 'api').length,
      llm: toolInstances.filter(i => i.category === 'llm').length,
      rag: toolInstances.filter(i => i.category === 'rag').length,
      workflow: toolInstances.filter(i => i.category === 'workflow').length,
    },
    environmentBreakdown: {
      development: toolInstances.filter(i => i.environment_scope === 'development').length,
      staging: toolInstances.filter(i => i.environment_scope === 'staging').length,
      production: toolInstances.filter(i => i.environment_scope === 'production').length,
      global: toolInstances.filter(i => i.environment_scope === 'global').length,
    }
  };

  return analytics;
}
