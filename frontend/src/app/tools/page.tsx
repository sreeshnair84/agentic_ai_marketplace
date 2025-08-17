'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useProject } from '@/store/projectContext';
import { 
  Search, 
  Plus, 
  Filter, 
  Zap, 
  Database, 
  Cloud, 
  Play, 
  MoreHorizontal,
  Edit3,
  Eye,
  AlertTriangle,
  RefreshCw,
  Code
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import ToolTemplateForm from './ToolTemplateForm';
import ToolInstanceForm from './ToolInstanceForm';

interface ToolTemplate {
  id?: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  type: string;
  version: string;
  is_active: boolean;
  icon?: string;
  tags?: string[];
  created_at?: string;
  fields: ToolTemplateField[];
}

interface ToolTemplateField {
  id: string;
  field_name: string;
  field_label: string;
  field_type: string;
  field_description?: string;
  is_required: boolean;
  is_secret: boolean;
  default_value?: string;
  validation_rules?: Record<string, unknown>;
  field_options?: Record<string, unknown>;
  field_order: number;
}

interface ToolInstance {
  id?: string;
  tool_template_id: string;
  name: string;
  display_name: string;
  description: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  configuration: Record<string, unknown>;
  environment_scope: 'global' | 'development' | 'staging' | 'production';
  project_tags?: string[];
  created_at?: string;
  updated_at?: string;
  template?: ToolTemplate;
}

interface LLMModel {
  id: string;
  name: string;
  display_name: string;
  provider: string;
  model_type?: string;
  max_tokens?: number;
  supports_streaming?: boolean;
  supports_functions?: boolean;
}

interface EmbeddingModel {
  id: string;
  name: string;
  display_name: string;
  provider: string;
  dimensions?: number;
  max_input_tokens?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ToolsManagement() {
  const [toolTemplates, setToolTemplates] = useState<ToolTemplate[]>([]);
  const [toolInstances, setToolInstances] = useState<ToolInstance[]>([]);
  const [llmModels, setLLMModels] = useState<LLMModel[]>([]);
  const [embeddingModels, setEmbeddingModels] = useState<EmbeddingModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedScope, setSelectedScope] = useState<string>('all');
  const [selectedTab, setSelectedTab] = useState<'templates' | 'instances'>('instances');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<ToolTemplate | null>(null);
  const [editingInstance, setEditingInstance] = useState<ToolInstance | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<ToolTemplate | null>(null);

  const { state: projectState } = useProject();

  // Fetch data from backend APIs
  useEffect(() => {
    fetchData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch templates and instances - these are the main data we need
      const [templatesRes, instancesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/tools/templates`, {
          headers: {
            'Content-Type': 'application/json'
          }
        }),
        fetch(`${API_BASE_URL}/api/tools/instances`, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
      ]);

      if (!templatesRes.ok || !instancesRes.ok) {
        throw new Error('Failed to fetch tools data from server');
      }

      const [templates, instances] = await Promise.all([
        templatesRes.json(),
        instancesRes.json()
      ]);

      console.log('Fetched templates:', templates);
      console.log('Fetched instances:', instances);

      setToolTemplates(templates);
      // Ensure instances is always an array
      setToolInstances(Array.isArray(instances) ? instances : [instances]);

      // Try to fetch LLM and embedding models, but don't fail if they're not available
      try {
        const llmRes = await fetch(`${API_BASE_URL}/api/tools/llm-models`, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (llmRes.ok) {
          const llmData = await llmRes.json();
          setLLMModels(llmData);
        }
      } catch (err) {
        console.warn('LLM models endpoint not available:', err);
        setLLMModels([]);
      }

      try {
        const embeddingRes = await fetch(`${API_BASE_URL}/api/tools/embedding-models`, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (embeddingRes.ok) {
          const embeddingData = await embeddingRes.json();
          setEmbeddingModels(embeddingData);
        }
      } catch (err) {
        console.warn('Embedding models endpoint not available:', err);
        setEmbeddingModels([]);
      }

    } catch (err) {
      console.error('Error fetching tools data:', err);
      setError('Failed to load tools data. Please check your connection and try again.');
      
      // Set empty arrays for main data
      setToolTemplates([]);
      setToolInstances([]);
      setLLMModels([]);
      setEmbeddingModels([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  

  const handleSaveTemplate = async (template: ToolTemplate) => {
    try {
      const url = template.id 
        ? `${API_BASE_URL}/api/tools/templates/${template.id}`
        : `${API_BASE_URL}/api/tools/templates`;
      
      const response = await fetch(url, {
        method: template.id ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(template)
      });

      if (response.ok) {
        await fetchData();
        setShowCreateForm(false);
        setEditingTemplate(null);
      } else {
        throw new Error('Failed to save template');
      }
    } catch (err) {
      console.error('Error saving template:', err);
      setError('Failed to save template. Please try again.');
    }
  };

  const handleSaveInstance = async (instance: ToolInstance) => {
    try {
      const url = instance.id 
        ? `${API_BASE_URL}/api/tools/instances/${instance.id}`
        : `${API_BASE_URL}/api/tools/instances`;
      
      const response = await fetch(url, {
        method: instance.id ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(instance)
      });

      if (response.ok) {
        await fetchData();
        setShowCreateForm(false);
        setEditingInstance(null);
      } else {
        throw new Error('Failed to save instance');
      }
    } catch (err) {
      console.error('Error saving instance:', err);
      setError('Failed to save instance. Please try again.');
    }
  };

  const handleEditItem = (item: ToolTemplate | ToolInstance) => {
    if (selectedTab === 'templates') {
      setEditingTemplate(item as ToolTemplate);
      setShowCreateForm(true);
    } else {
      setEditingInstance(item as ToolInstance);
      setShowCreateForm(true);
    }
  };

  const handleExecuteInstance = async (instance: ToolInstance) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tools/instances/${instance.id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Tool execution result:', result);
        // Handle execution result (could show in a modal or toast)
      } else {
        throw new Error('Failed to execute tool');
      }
    } catch (err) {
      console.error('Error executing tool:', err);
      setError('Failed to execute tool. Please try again.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'testing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'mcp':
        return <Zap className="h-4 w-4" />;
      case 'database':
      case 'rag':
        return <Database className="h-4 w-4" />;
      case 'api':
        return <Cloud className="h-4 w-4" />;
      case 'llm':
        return <Code className="h-4 w-4" />;
      default:
        return <Zap className="h-4 w-4" />;
    }
  };

  const filteredItems = useMemo(() => {
    console.log('=== DEBUGGING FILTER ===');
    console.log('selectedTab:', selectedTab);
    console.log('toolTemplates:', toolTemplates);
    console.log('toolInstances:', toolInstances);
    
    if (selectedTab === 'templates') {
      console.log('Filtering templates...');
      const filtered = toolTemplates.filter(template => {
        // Very simple filtering - just search and category
        const matchesSearch = !searchTerm || 
          template.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          template.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
        
        console.log('Template:', template.display_name, 'matchesSearch:', matchesSearch, 'matchesCategory:', matchesCategory);
        return matchesSearch && matchesCategory;
      });
      console.log('Filtered templates:', filtered);
      return filtered;
    } else {
      console.log('Filtering instances...');
      const filtered = toolInstances.filter(instance => {
        // Very simple filtering - just search and scope
        const matchesSearch = !searchTerm || 
          instance.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          instance.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesScope = selectedScope === 'all' || instance.environment_scope === selectedScope;
        
        console.log('Instance:', instance.display_name, 'matchesSearch:', matchesSearch, 'matchesScope:', matchesScope);
        return matchesSearch && matchesScope;
      });
      console.log('Filtered instances:', filtered);
      return filtered;
    }
  }, [selectedTab, toolTemplates, toolInstances, searchTerm, selectedCategory, selectedScope]);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading tools data...</p>
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
            Tools Management
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-gray-600 dark:text-gray-400">
              Manage tool templates and instances with dynamic configuration
            </p>
            {projectState.selectedProject && projectState.selectedProject.tags && projectState.selectedProject.tags.length > 0 && (
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-blue-500" />
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                  Filtered by: {projectState.selectedProject.name}
                </Badge>
              </div>
            )}
          </div>
        </div>
        <div className="flex space-x-3">
          <Button 
            variant="outline" 
            onClick={fetchData}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
          <Button 
            onClick={() => {
              setEditingTemplate(null);
              setEditingInstance(null);
              setShowCreateForm(true);
            }}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Create {selectedTab === 'templates' ? 'Template' : 'Instance'}</span>
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

      {/* Tabs and Filters */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setSelectedTab('instances')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedTab === 'instances'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Tool Instances ({toolInstances.length})
          </button>
          <button
            onClick={() => setSelectedTab('templates')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedTab === 'templates'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Templates ({toolTemplates.length})
          </button>
        </div>

        <div className="flex space-x-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder={`Search ${selectedTab}...`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>
          
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Categories</option>
            <option value="mcp">MCP Tools</option>
            <option value="custom">Custom Tools</option>
            <option value="api">API Tools</option>
            <option value="llm">LLM Tools</option>
            <option value="rag">RAG Tools</option>
            <option value="workflow">Workflow Tools</option>
          </select>

          {selectedTab === 'instances' && (
            <select
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">All Scopes</option>
              <option value="development">Development</option>
              <option value="staging">Staging</option>
              <option value="production">Production</option>
              <option value="global">Global</option>
            </select>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-4">
        {(() => {
          console.log('Rendering filteredItems:', filteredItems);
          return null;
        })()}
        {filteredItems.map((item) => {
          console.log('Rendering item:', item);
          return (
          <div
            key={item.id}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="flex items-center space-x-2">
                    {getCategoryIcon(selectedTab === 'templates' ? (item as ToolTemplate).category : 'custom')}
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedTab === 'templates' ? (item as ToolTemplate).display_name : (item as ToolInstance).display_name}
                    </h3>
                  </div>
                  
                  {selectedTab === 'instances' && (
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor((item as ToolInstance).status)}`}>
                      {(item as ToolInstance).status}
                    </span>
                  )}
                  
                  {selectedTab === 'instances' && (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                      {(item as ToolInstance).environment_scope}
                    </span>
                  )}
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  {selectedTab === 'templates' ? (item as ToolTemplate).description : (item as ToolInstance).description}
                </p>
                
                {selectedTab === 'templates' && (item as ToolTemplate).tags && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {(item as ToolTemplate).tags!.map((tag, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 text-xs bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-md"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {selectedTab === 'instances' && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Configuration</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries((item as ToolInstance).configuration).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-gray-900 dark:text-white font-mono">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-2 ml-6">
                {selectedTab === 'instances' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleExecuteInstance(item as ToolInstance)}
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    if (selectedTab === 'templates') {
                      setSelectedTemplate(item as ToolTemplate);
                    }
                  }}
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditItem(item)}
                >
                  <Edit3 className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {/* More options */}}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          );
        })}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <Zap className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No {selectedTab} found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {searchTerm || selectedCategory !== 'all' 
              ? 'Try adjusting your search or filters.'
              : `Get started by creating your first ${selectedTab.slice(0, -1)}.`
            }
          </p>
        </div>
      )}

      {/* Template Details Modal */}
      {selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Template: {selectedTemplate.display_name}
              </h2>
              <Button 
                variant="ghost" 
                onClick={() => setSelectedTemplate(null)}
              >
                ×
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Description</h3>
                <p className="text-gray-600 dark:text-gray-400">{selectedTemplate.description}</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Template Fields</h3>
                <div className="space-y-3">
                  {selectedTemplate.fields?.map((field) => (
                    <div key={field.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-white">{field.field_label}</h4>
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            field.is_required 
                              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                          }`}>
                            {field.is_required ? 'Required' : 'Optional'}
                          </span>
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 rounded-full">
                            {field.field_type}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{field.field_description}</p>
                      <div className="text-xs text-gray-500 dark:text-gray-500">
                        Field Name: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">{field.field_name}</code>
                        {field.default_value && (
                          <span className="ml-3">Default: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">{field.default_value}</code></span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create/Edit Forms */}
      {showCreateForm && selectedTab === 'templates' && (
        <ToolTemplateForm
          template={editingTemplate || undefined}
          onSave={(template) => handleSaveTemplate(template as any)}
          onCancel={() => {
            setShowCreateForm(false);
            setEditingTemplate(null);
          }}
          llmModels={llmModels}
          embeddingModels={embeddingModels}
        />
      )}

      {showCreateForm && selectedTab === 'instances' && (
        <ToolInstanceForm
          instance={editingInstance || undefined}
          templates={toolTemplates.filter(t => t.id) as any}
          llmModels={llmModels}
          embeddingModels={embeddingModels}
          onSave={(instance) => handleSaveInstance(instance as any)}
          onCancel={() => {
            setShowCreateForm(false);
            setEditingInstance(null);
          }}
        />
      )}
    </div>
  );
}
