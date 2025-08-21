import { useState, useCallback, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';

export interface EmbeddingModel {
  id: string;
  name: string;
  display_name: string;
  provider: string;
  model_type: string;
  api_endpoint?: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  capabilities?: {
    dimensions?: number;
    max_input_tokens?: number;
    supports_batching?: boolean;
    supported_languages?: string[];
  };
  pricing_info?: {
    cost_per_token?: number;
    currency?: string;
  };
  performance_metrics?: {
    avg_latency?: number;
    throughput?: number;
    availability?: number;
  };
  api_key?: string;
  health_url?: string;
  dns_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateEmbeddingModelData {
  name: string;
  display_name: string;
  provider: string;
  model_type: string;
  api_endpoint?: string;
  status?: 'active' | 'inactive' | 'error' | 'testing';
  capabilities?: EmbeddingModel['capabilities'];
  pricing_info?: EmbeddingModel['pricing_info'];
  performance_metrics?: EmbeddingModel['performance_metrics'];
  api_key?: string;
  health_url?: string;
  dns_name?: string;
}

export function useEmbeddingModels() {
  const [models, setModels] = useState<EmbeddingModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/tools/embedding-models`);
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

  const createModel = useCallback(async (modelData: CreateEmbeddingModelData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/embedding-models`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(modelData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        return { success: false, error: errorData.detail || 'Failed to create model' };
      }

      const result = await response.json();
      await fetchModels(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Failed to create model' };
    }
  }, [fetchModels]);

  const updateModel = useCallback(async (modelId: string, modelData: CreateEmbeddingModelData): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/embedding-models/${modelId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(modelData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        return { success: false, error: errorData.detail || 'Failed to update model' };
      }

      await fetchModels(); // Refresh the list
      return { success: true };
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Failed to update model' };
    }
  }, [fetchModels]);

  const deleteModel = useCallback(async (modelId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/embedding-models/${modelId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        return { success: false, error: errorData.detail || 'Failed to delete model' };
      }

      await fetchModels(); // Refresh the list
      return { success: true };
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : 'Failed to delete model' };
    }
  }, [fetchModels]);

  const testModel = useCallback(async (modelId: string): Promise<{ success: boolean; error?: string; status?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/embedding-models/${modelId}/test`, {
        method: 'POST',
      });

      const result = await response.json();
      
      return {
        success: response.ok && result.success,
        error: result.success ? undefined : result.message,
        status: result.status 
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to test model';
      return { success: false, error: errorMessage };
    }
  }, [fetchModels]);

  const getModel = useCallback(async (modelId: string): Promise<EmbeddingModel | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/embedding-models/${modelId}`);
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
