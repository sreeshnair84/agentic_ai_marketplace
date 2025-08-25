'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal,
  Edit3,
  Trash2,
  Eye,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Zap,
  Activity,
  DollarSign,
  Clock,
  X
} from 'lucide-react';
import LLMModelForm from '../components/LLMModelForm';
import { useLLMModels, LLMModel, CreateLLMModelData } from '@/hooks/useLLMModels';

export default function LLMModelsManagement() {
  const { 
    models, 
    loading, 
    error, 
    createModel, 
    updateModel, 
    deleteModel, 
    testModel 
  } = useLLMModels();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingModel, setEditingModel] = useState<LLMModel | null>(null);
  const [viewingModel, setViewingModel] = useState<LLMModel | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleSaveModel = async (modelData: CreateLLMModelData) => {
    setActionLoading('save');
    try {
      const result = editingModel 
        ? await updateModel(editingModel.id, modelData)
        : await createModel(modelData);
      
      if (result.success) {
        setShowCreateForm(false);
        setEditingModel(null);
      } else {
        alert(`Failed to save model: ${result.error || 'Unknown error'}`);
      }
    } finally {
      setActionLoading(null);
    }
    return { success: true }; // For form compatibility
  };

  // Wrapper function for form compatibility
  const handleFormSave = async (model: LLMModel): Promise<void> => {
    await handleSaveModel(model as CreateLLMModelData);
  };

  const handleTestModel = async (model: LLMModel): Promise<boolean> => {
    setActionLoading(`test-${model.id}`);
    try {
      const result = await testModel(model.id);
      if (result.success) {
        alert('Model test successful!');
        return true;
      } else {
        alert(`Model test failed: ${result.error || 'Unknown error'}`);
        return false;
      }
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteModel = async (modelId: string) => {
    if (!confirm('Are you sure you want to delete this model?')) return;

    setActionLoading(`delete-${modelId}`);
    try {
      const result = await deleteModel(modelId);
      if (!result.success && result.error) {
        alert(`Failed to delete model: ${result.error}`);
      }
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
      case 'testing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'anthropic':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      case 'google':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
      case 'microsoft':
        return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const filteredModels = (models || []).filter(model => {
    const matchesSearch = model.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesProvider = selectedProvider === 'all' || model.provider === selectedProvider;
    const matchesStatus = selectedStatus === 'all' || model.status === selectedStatus;
    const matchesType = selectedType === 'all' || model.model_type === selectedType;
    
    return matchesSearch && matchesProvider && matchesStatus && matchesType;
  });

  const uniqueProviders = [...new Set(models.map(m => m.provider))];
  const uniqueTypes = [...new Set(models.map(m => m.model_type))];

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading LLM models...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Models Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage and configure language models/Embedding Model for your applications
          </p>
        </div>
        <div className="flex space-x-3">
          <Button 
            variant="outline" 
            onClick={() => window.location.reload()}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
          <Button 
            onClick={() => {
              setEditingModel(null);
              setShowCreateForm(true);
            }}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Model</span>
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
            <span className="text-red-800 dark:text-red-200">{error}</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0 gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search models..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        
        <div className="flex space-x-3">
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Providers</option>
            {uniqueProviders.map(provider => (
              <option key={provider} value={provider}>
                {provider.charAt(0).toUpperCase() + provider.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Types</option>
            {uniqueTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="testing">Testing</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredModels.map((model) => (
          <div
            key={model.id}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
          >
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {model.display_name}
                  </h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(model.status)}`}>
                    {model.status}
                  </span>
                </div>
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getProviderColor(model.provider)}`}>
                    {model.provider}
                  </span>
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                    {model.model_type}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                  {model.name}
                </p>
              </div>
              
              <div className="flex space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setViewingModel(model)}
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setEditingModel(model);
                    setShowCreateForm(true);
                  }}
                  disabled={actionLoading?.startsWith('edit')}
                >
                  <Edit3 className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteModel(model.id)}
                  disabled={actionLoading === `delete-${model.id}`}
                >
                  {actionLoading === `delete-${model.id}` ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Capabilities */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Max Tokens:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {model.capabilities?.max_tokens?.toLocaleString() || 'N/A'}
                </span>
              </div>

              {model.pricing_info && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Input Cost:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    ${model.pricing_info.input_cost_per_token}/1K tokens
                  </span>
                </div>
              )}

              {model.performance_metrics && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Availability:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {model.performance_metrics.availability}%
                  </span>
                </div>
              )}

              {/* Features */}
              <div className="flex flex-wrap gap-1 mt-2">
                {model.capabilities?.supports_streaming && (
                  <Badge variant="outline" className="text-xs">Streaming</Badge>
                )}
                {model.capabilities?.supports_function_calling && (
                  <Badge variant="outline" className="text-xs">Functions</Badge>
                )}
                {model.capabilities?.input_modalities?.includes('image') && (
                  <Badge variant="outline" className="text-xs">Vision</Badge>
                )}
              </div>

              {/* Test Button */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleTestModel(model)}
                disabled={actionLoading === `test-${model.id}`}
                className="w-full mt-3"
              >
                {actionLoading === `test-${model.id}` ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4 mr-2" />
                    Test Connection
                  </>
                )}
              </Button>
            </div>
          </div>
        ))}
      </div>

      {filteredModels.length === 0 && (
        <div className="text-center py-12">
          <Zap className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No models found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {searchTerm || selectedProvider !== 'all' || selectedStatus !== 'all'
              ? 'Try adjusting your search or filters.'
              : 'Get started by adding your first LLM model.'
            }
          </p>
          {!searchTerm && selectedProvider === 'all' && selectedStatus === 'all' && (
            <Button 
              className="mt-4" 
              onClick={() => {
                setEditingModel(null);
                setShowCreateForm(true);
              }}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Model
            </Button>
          )}
        </div>
      )}

      {/* Model Details Modal */}
      {viewingModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {viewingModel.display_name}
              </h2>
              <Button 
                variant="ghost" 
                onClick={() => setViewingModel(null)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Basic Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Name:</span>
                    <p className="font-mono">{viewingModel.name}</p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Provider:</span>
                    <p className="capitalize">{viewingModel.provider}</p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Type:</span>
                    <p className="capitalize">{viewingModel.model_type}</p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Status:</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(viewingModel.status)}`}>
                      {viewingModel.status}
                    </span>
                  </div>
                  {viewingModel.api_endpoint && (
                    <div className="col-span-2">
                      <span className="text-gray-600 dark:text-gray-400">API Endpoint:</span>
                      <p className="font-mono text-xs">{viewingModel.api_endpoint}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Capabilities */}
              {viewingModel.capabilities && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Capabilities</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Max Tokens:</span>
                      <span>{viewingModel.capabilities.max_tokens?.toLocaleString() || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Streaming:</span>
                      <span>{viewingModel.capabilities.supports_streaming ? '✓' : '✗'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Functions:</span>
                      <span>{viewingModel.capabilities.supports_function_calling ? '✓' : '✗'}</span>
                    </div>
                    {viewingModel.capabilities.input_modalities && (
                      <div className="col-span-2">
                        <span className="text-gray-600 dark:text-gray-400">Input Modalities:</span>
                        <p>{viewingModel.capabilities.input_modalities.join(', ')}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Pricing */}
              {viewingModel.pricing_info && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Pricing</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Input Cost (1K tokens):</span>
                      <span>${viewingModel.pricing_info.input_cost_per_token || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Output Cost (1K tokens):</span>
                      <span>${viewingModel.pricing_info.output_cost_per_token || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Currency:</span>
                      <span>{viewingModel.pricing_info.currency || 'USD'}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Performance */}
              {viewingModel.performance_metrics && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Performance</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Avg Latency:</span>
                      <span>{viewingModel.performance_metrics.avg_latency || 'N/A'}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Tokens/Second:</span>
                      <span>{viewingModel.performance_metrics.tokens_per_second || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Availability:</span>
                      <span>{viewingModel.performance_metrics.availability || 'N/A'}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Timestamps */}
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Timestamps</h3>
                <div className="text-sm space-y-1">
                  {viewingModel.created_at && (
                    <div><strong>Created:</strong> {new Date(viewingModel.created_at).toLocaleString()}</div>
                  )}
                  {viewingModel.updated_at && (
                    <div><strong>Updated:</strong> {new Date(viewingModel.updated_at).toLocaleString()}</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Form */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {editingModel ? 'Edit LLM Model' : 'Create New LLM Model'}
              </h2>
              <Button 
                variant="ghost" 
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingModel(null);
                }}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div className="p-6">
              <LLMModelForm
                model={editingModel || undefined}
                onSave={handleFormSave}
                onCancel={() => {
                  setShowCreateForm(false);
                  setEditingModel(null);
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
