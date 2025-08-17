import { useState, useEffect, useCallback } from 'react';

export interface LLMModel {
  id: string;
  name: string;
  display_name: string;
  provider: string;
  model_type: string;
  api_endpoint?: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  capabilities?: {
    max_tokens?: number;
    supports_streaming?: boolean;
    supports_function_calling?: boolean;
    input_modalities?: string[];
    output_modalities?: string[];
  };
  pricing_info?: {
    input_cost_per_token?: number;
    output_cost_per_token?: number;
    currency?: string;
  };
  performance_metrics?: {
    avg_latency?: number;
    tokens_per_second?: number;
    availability?: number;
  };
  model_config?: {
    temperature?: number;
    max_tokens?: number;
    top_p?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    stop_sequences?: string[];
  };
  api_key?: string;
  health_url?: string;
  dns_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateLLMModelData {
  name: string;
  display_name: string;
  provider: string;
  model_type: string;
  api_endpoint?: string;
  status?: 'active' | 'inactive' | 'error' | 'testing';
  capabilities?: LLMModel['capabilities'];
  pricing_info?: LLMModel['pricing_info'];
  performance_metrics?: LLMModel['performance_metrics'];
  model_config?: LLMModel['model_config'];
  api_key?: string;
  health_url?: string;
  dns_name?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useLLMModels() {
  const [models, setModels] = useState<LLMModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/tools/llm-models`);
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.statusText}`);
      }
      const data = await response.json();
      setModels(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch models');
      setModels([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createModel = useCallback(async (modelData: CreateLLMModelData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/llm-models`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(modelData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create model');
      }

      const result = await response.json();
      await fetchModels(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create model';
      return { success: false, error: errorMessage };
    }
  }, [fetchModels]);

  const updateModel = useCallback(async (modelId: string, modelData: CreateLLMModelData): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/llm-models/${modelId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(modelData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to update model');
      }

      await fetchModels(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update model';
      return { success: false, error: errorMessage };
    }
  }, [fetchModels]);

  const deleteModel = useCallback(async (modelId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/llm-models/${modelId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete model');
      }

      await fetchModels(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete model';
      return { success: false, error: errorMessage };
    }
  }, [fetchModels]);

  const testModel = useCallback(async (modelId: string): Promise<{ success: boolean; error?: string; status?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/llm-models/${modelId}/test`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to test model');
      }

      const result = await response.json();
      await fetchModels(); // Refresh to get updated status
      return { 
        success: result.success, 
        error: result.success ? undefined : result.message,
        status: result.status 
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to test model';
      return { success: false, error: errorMessage };
    }
  }, [fetchModels]);

  const getModel = useCallback(async (modelId: string): Promise<LLMModel | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/llm-models/${modelId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch model: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching model:', err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  return {
    models,
    loading,
    error,
    fetchModels,
    createModel,
    updateModel,
    deleteModel,
    testModel,
    getModel,
  };
}
