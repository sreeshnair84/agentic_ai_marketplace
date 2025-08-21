'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  X, 
  Save, 
  AlertTriangle, 
  CheckCircle,
  Info,
  Plus,
  Trash2,
  TestTube
} from 'lucide-react';
import { EmbeddingModel } from '@/hooks/useEmbeddingModels';

interface EmbeddingModelFormProps {
  model?: EmbeddingModel;
  onSave: (model: EmbeddingModel) => Promise<void>;
  onCancel: () => void;
  onTest?: (model: EmbeddingModel) => Promise<boolean>;
}

const PROVIDERS = [
  'openai',
  'anthropic',
  'google',
  'microsoft',
  'cohere',
  'huggingface',
  'local',
  'azure',
  'aws_bedrock',
  'sentence_transformers',
  'custom'
];

const EMBEDDING_MODEL_TYPES = [
  'text_embedding',
  'multimodal_embedding',
  'code_embedding',
  'document_embedding'
];

export default function EmbeddingModelForm({ model, onSave, onCancel, onTest }: EmbeddingModelFormProps) {
  const [formData, setFormData] = useState<EmbeddingModel>({
    id: '',
    name: '',
    display_name: '',
    provider: 'openai',
    model_type: 'text_embedding',
    api_endpoint: '',
    status: 'inactive',
    capabilities: {
      dimensions: 1536,
      max_input_tokens: 8191,
      supports_batching: false,
      supported_languages: ['en']
    },
    pricing_info: {
      cost_per_token: 0,
      currency: 'USD'
    },
    performance_metrics: {},
    api_key: '',
    health_url: '',
    dns_name: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<'basic' | 'capabilities' | 'pricing' | 'performance' | 'config'>('basic');
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    if (model) {
      setFormData({
        ...model,
        capabilities: model.capabilities || {
          dimensions: 1536,
          max_input_tokens: 8191,
          supports_batching: false,
          supported_languages: ['en']
        },
        pricing_info: model.pricing_info || {
          cost_per_token: 0,
          currency: 'USD'
        },
        performance_metrics: model.performance_metrics || {}
      });
    }
  }, [model]);

  const updateFormData = (path: string, value: any) => {
    setFormData(prev => {
      const keys = path.split('.');
      const newData = { ...prev };
      let current: any = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) {
          current[keys[i]] = {};
        }
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Model name is required';
    }

    if (!formData.display_name?.trim()) {
      newErrors.display_name = 'Display name is required';
    }

    if (!formData.provider?.trim()) {
      newErrors.provider = 'Provider is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSaving(true);
    try {
      await onSave(formData);
    } catch (err) {
      console.error('Error saving model:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    if (!onTest) return;

    setIsTesting(true);
    setTestResult(null);
    try {
      const success = await onTest(formData);
      setTestResult({
        success,
        message: success ? 'Model connection test successful!' : 'Model connection test failed'
      });
    } catch (err) {
      setTestResult({
        success: false,
        message: 'Test failed: ' + (err instanceof Error ? err.message : 'Unknown error')
      });
    } finally {
      setIsTesting(false);
    }
  };

  const renderBasicTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Model Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => updateFormData('name', e.target.value)}
            placeholder="text-embedding-3-small"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Display Name *
          </label>
          <input
            type="text"
            value={formData.display_name}
            onChange={(e) => updateFormData('display_name', e.target.value)}
            placeholder="OpenAI Text Embedding 3 Small"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          {errors.display_name && <p className="text-red-500 text-sm mt-1">{errors.display_name}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Provider *
          </label>
          <select
            value={formData.provider}
            onChange={(e) => updateFormData('provider', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            {PROVIDERS.map(provider => (
              <option key={provider} value={provider}>
                {provider.charAt(0).toUpperCase() + provider.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Model Type
          </label>
          <select
            value={formData.model_type}
            onChange={(e) => updateFormData('model_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            {EMBEDDING_MODEL_TYPES.map(type => (
              <option key={type} value={type}>
                {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            API Endpoint
          </label>
          <input
            type="url"
            value={formData.api_endpoint || ''}
            onChange={(e) => updateFormData('api_endpoint', e.target.value)}
            placeholder="https://api.openai.com/v1"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Status
          </label>
          <select
            value={formData.status}
            onChange={(e) => updateFormData('status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="testing">Testing</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          API Key
        </label>
        <input
          type="password"
          value={formData.api_key || ''}
          onChange={(e) => updateFormData('api_key', e.target.value)}
          placeholder="sk-..."
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
      </div>
    </div>
  );

  const renderCapabilitiesTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Dimensions
          </label>
          <input
            type="number"
            value={formData.capabilities?.dimensions || ''}
            onChange={(e) => updateFormData('capabilities.dimensions', parseInt(e.target.value) || 0)}
            placeholder="1536"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Max Input Tokens
          </label>
          <input
            type="number"
            value={formData.capabilities?.max_input_tokens || ''}
            onChange={(e) => updateFormData('capabilities.max_input_tokens', parseInt(e.target.value) || 0)}
            placeholder="8191"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="supports_batching"
            checked={formData.capabilities?.supports_batching || false}
            onChange={(e) => updateFormData('capabilities.supports_batching', e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="supports_batching" className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
            Supports Batching
          </label>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Supported Languages
        </label>
        <input
          type="text"
          value={formData.capabilities?.supported_languages?.join(', ') || ''}
          onChange={(e) => updateFormData('capabilities.supported_languages', e.target.value.split(',').map(s => s.trim()))}
          placeholder="en, es, fr, de"
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        />
        <p className="text-xs text-gray-500 mt-1">Comma-separated language codes</p>
      </div>
    </div>
  );

  const renderPricingTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Cost per Token
          </label>
          <input
            type="number"
            step="0.000001"
            value={formData.pricing_info?.cost_per_token || ''}
            onChange={(e) => updateFormData('pricing_info.cost_per_token', parseFloat(e.target.value) || 0)}
            placeholder="0.00002"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Currency
          </label>
          <select
            value={formData.pricing_info?.currency || 'USD'}
            onChange={(e) => updateFormData('pricing_info.currency', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
            <option value="GBP">GBP</option>
            <option value="JPY">JPY</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Average Latency (ms)
          </label>
          <input
            type="number"
            value={formData.performance_metrics?.avg_latency || ''}
            onChange={(e) => updateFormData('performance_metrics.avg_latency', parseInt(e.target.value) || 0)}
            placeholder="150"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Throughput (requests/min)
          </label>
          <input
            type="number"
            value={formData.performance_metrics?.throughput || ''}
            onChange={(e) => updateFormData('performance_metrics.throughput', parseInt(e.target.value) || 0)}
            placeholder="1000"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Availability (%)
          </label>
          <input
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={formData.performance_metrics?.availability || ''}
            onChange={(e) => updateFormData('performance_metrics.availability', parseFloat(e.target.value) || 0)}
            placeholder="99.9"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      </div>
    </div>
  );

  const renderConfigTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Health Check URL
          </label>
          <input
            type="url"
            value={formData.health_url || ''}
            onChange={(e) => updateFormData('health_url', e.target.value)}
            placeholder="https://api.example.com/health"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            DNS Name
          </label>
          <input
            type="text"
            value={formData.dns_name || ''}
            onChange={(e) => updateFormData('dns_name', e.target.value)}
            placeholder="embedding-model.example.com"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {model ? 'Edit Embedding Model' : 'Create Embedding Model'}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Test Result */}
        {testResult && (
          <div className={`mx-6 mt-4 p-4 rounded-lg border ${
            testResult.success 
              ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' 
              : 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
          }`}>
            <div className="flex items-center space-x-2">
              {testResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
              )}
              <span className={`${
                testResult.success ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'
              }`}>
                {testResult.message}
              </span>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'basic', label: 'Basic Info' },
              { id: 'capabilities', label: 'Capabilities' },
              { id: 'pricing', label: 'Pricing' },
              { id: 'performance', label: 'Performance' },
              { id: 'config', label: 'Configuration' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Form Content */}
        <form onSubmit={handleSubmit} className="overflow-y-auto max-h-[60vh]">
          <div className="p-6">
            {activeTab === 'basic' && renderBasicTab()}
            {activeTab === 'capabilities' && renderCapabilitiesTab()}
            {activeTab === 'pricing' && renderPricingTab()}
            {activeTab === 'performance' && renderPerformanceTab()}
            {activeTab === 'config' && renderConfigTab()}
          </div>
        </form>

        {/* Footer */}
        <div className="flex justify-between items-center p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-3">
            {onTest && (
              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={isTesting}
                className="flex items-center space-x-2"
              >
                <TestTube className="h-4 w-4" />
                <span>{isTesting ? 'Testing...' : 'Test Connection'}</span>
              </Button>
            )}
          </div>
          
          <div className="flex space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              onClick={handleSubmit}
              disabled={isSaving}
              className="flex items-center space-x-2"
            >
              <Save className="h-4 w-4" />
              <span>{isSaving ? 'Saving...' : 'Save Model'}</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
