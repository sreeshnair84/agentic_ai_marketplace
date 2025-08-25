'use client';

import { useState, useEffect, useMemo } from 'react';
import { useProject } from '@/store/projectContext';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { StandardPageLayout, StandardSection } from '@/components/layout/StandardPageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowPathIcon,
  BoltIcon,
  CloudIcon,
  PlayIcon,
  PencilIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  CodeBracketIcon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';
import ToolTemplateForm from './components/ToolTemplateForm';
import ToolInstanceForm from './components/ToolInstanceForm';
import PhysicalToolTester from './components/PhysicalToolTester';
import RAGInstanceManager from './components/RAGInstanceManager';
import { useTools, useToolAnalytics, ToolTemplate, ToolInstance, ToolTemplateField } from '@/hooks/useTools';

export default function ToolsManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedScope, setSelectedScope] = useState<string>('all');
  const [selectedTab, setSelectedTab] = useState<'templates' | 'instances' | 'physical-tester'>('instances');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<any>(null);
  const [editingInstance, setEditingInstance] = useState<any>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [managingRAGInstance, setManagingRAGInstance] = useState<any>(null);

  const { state: projectState } = useProject();

  // Use real API data from hooks
  const {
    toolTemplates,
    toolInstances,
    loading,
    error,
    fetchToolTemplates,
    fetchToolInstances,
    createTemplate,
    updateTemplate,
    createInstance,
    updateInstance,
    testInstance,
  } = useTools();
  
  const analytics = useToolAnalytics();

  // Fetch data on component mount
  useEffect(() => {
    fetchToolTemplates();
    fetchToolInstances();
  }, [fetchToolTemplates, fetchToolInstances]);

  const handleSaveTemplate = async (template: any) => {
    try {
      if (template.id) {
        await updateTemplate(template.id, template);
      } else {
        await createTemplate(template);
      }
      setShowCreateForm(false);
      setEditingTemplate(null);
    } catch (err) {
      console.error('Error saving template:', err);
    }
  };

  const handleSaveInstance = async (instance: any) => {
    try {
      if (instance.id) {
        await updateInstance(instance.id, instance);
      } else {
        await createInstance(instance);
      }
      setShowCreateForm(false);
      setEditingInstance(null);
    } catch (err) {
      console.error('Error saving instance:', err);
    }
  };

  const handleEditItem = (item: any) => {
    if (selectedTab === 'templates') {
      setEditingTemplate(item);
      setShowCreateForm(true);
    } else {
      setEditingInstance(item);
      setShowCreateForm(true);
    }
  };

  const handleCloneItem = (item: any) => {
    if (selectedTab === 'templates') {
      const clonedTemplate = {
        ...item,
        id: undefined,
        name: `${item.name}_copy`,
        display_name: `${item.display_name} (Copy)`,
      };
      setEditingTemplate(clonedTemplate);
      setShowCreateForm(true);
    } else {
      const clonedInstance = {
        ...item,
        id: undefined,
        name: `${item.name}_copy`,
        display_name: `${item.display_name} (Copy)`,
      };
      setEditingInstance(clonedInstance);
      setShowCreateForm(true);
    }
  };

  const handleExecuteInstance = async (instance: any) => {
    try {
      const result = await testInstance(instance.id);
      console.log('Tool execution result:', result);
      // Handle execution result (could show in a modal or toast)
    } catch (err) {
      console.error('Error executing tool:', err);
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
        return <BoltIcon className="h-4 w-4" />;
      case 'database':
      case 'rag':
        return <CloudIcon className="h-4 w-4" />;
      case 'api':
        return <CloudIcon className="h-4 w-4" />;
      case 'llm':
        return <CodeBracketIcon className="h-4 w-4" />;
      default:
        return <BoltIcon className="h-4 w-4" />;
    }
  };

  const isRAGInstance = (instance: ToolInstance) => {
    // Check if the instance is a RAG type based on various indicators
    return (
      instance.category === 'rag' ||
      instance.name?.toLowerCase().includes('rag') ||
      instance.display_name?.toLowerCase().includes('rag') ||
      instance.configuration?.database_url ||
      instance.configuration?.embedding_model ||
      instance.configuration?.vector_database ||
      instance.configuration?.rag_service_enabled ||
      instance.tags?.some(tag => tag.toLowerCase().includes('rag'))
    );
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
      <AuthGuard>
        <StandardPageLayout title="Tools Management" description="Loading tools data...">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-body text-gray-600 dark:text-gray-400">Loading tools data...</p>
            </div>
          </div>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
    <StandardPageLayout
      title="Tools Management"
      description="Manage tool templates and instances with dynamic configuration"
      actions={
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          {projectState.selectedProject && (projectState.selectedProject.name === 'Default Project' || (projectState.selectedProject.tags && projectState.selectedProject.tags.length > 0)) && (
            <div className="flex items-center gap-2">
              <FunnelIcon className="w-4 h-4 text-blue-500" />
              <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                Filtered by: {projectState.selectedProject.name}
              </Badge>
            </div>
          )}
          <div className="flex space-x-3">
            <Button 
              variant="outline" 
              onClick={() => {
                fetchToolTemplates();
                fetchToolInstances();
              }}
              className="flex items-center space-x-2"
            >
              <ArrowPathIcon className="h-4 w-4" />
              <span>Refresh</span>
            </Button>
            {selectedTab !== 'physical-tester' && (
              <Button 
                onClick={() => {
                  setEditingTemplate(null);
                  setEditingInstance(null);
                  setShowCreateForm(true);
                }}
                className="flex items-center space-x-2"
              >
                <PlusIcon className="h-4 w-4" />
                <span>Create {selectedTab === 'templates' ? 'Template' : 'Instance'}</span>
              </Button>
            )}
          </div>
        </div>
      }
    >

      {error && (
        <StandardSection>
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400" />
              <span className="text-red-800 dark:text-red-200">{error}</span>
            </div>
          </div>
        </StandardSection>
      )}

      {/* Tabs and Filters */}
      <StandardSection>
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
          <button
            onClick={() => setSelectedTab('physical-tester')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedTab === 'physical-tester'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Physical Tool Tester
          </button>
        </div>

        <div className="flex space-x-3">
          {selectedTab !== 'physical-tester' && (
            <>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder={`Search ${selectedTab}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
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
            </>
          )}
        </div>
      </div>
      </StandardSection>

      {/* Content */}
      <StandardSection>
      {selectedTab === 'physical-tester' ? (
        <PhysicalToolTester />
      ) : (
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
                {selectedTab === 'instances' && isRAGInstance(item as ToolInstance) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setManagingRAGInstance(item as ToolInstance)}
                    title="Manage RAG Documents & Search"
                  >
                    <CloudIcon className="h-4 w-4" />
                  </Button>
                )}
                {selectedTab === 'instances' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleExecuteInstance(item as ToolInstance)}
                  >
                    <PlayIcon className="h-4 w-4" />
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
                  <EyeIcon className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditItem(item)}
                >
                  <PencilIcon className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCloneItem(item)}
                  title="Clone item"
                >
                  <DocumentDuplicateIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          );
        })}
        
        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <BoltIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
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
                  {selectedTemplate.fields?.map((field: ToolTemplateField) => (
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
      </StandardSection>

      {/* Create/Edit Forms */}
      {showCreateForm && selectedTab === 'templates' && (
        <ToolTemplateForm
          template={editingTemplate as any}
          onSave={(template: any) => handleSaveTemplate(template as any)}
          onCancel={() => {
            setShowCreateForm(false);
            setEditingTemplate(null);
          }}
        />
      )}

      {showCreateForm && selectedTab === 'instances' && (
        <ToolInstanceForm
          instance={editingInstance as any}
          templates={toolTemplates.filter(t => t.id) as any}
          onSave={(instance: any) => handleSaveInstance(instance as any)}
          onCancel={() => {
            setShowCreateForm(false);
            setEditingInstance(null);
          }}
        />
      )}

      {managingRAGInstance && (
        <RAGInstanceManager
          instance={managingRAGInstance}
          onClose={() => setManagingRAGInstance(null)}
          onSave={(updatedInstance) => {
            // Optionally handle saving updated instance
            setManagingRAGInstance(null);
          }}
        />
      )}
    </StandardPageLayout>
    </AuthGuard>
  );
}
