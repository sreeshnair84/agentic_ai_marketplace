'use client';

import { useLLMModels } from '@/hooks/useLLMModels';
import { useState, useMemo } from 'react';
import { useProject } from '@/store/projectContext';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { StandardPageLayout, StandardSection, StandardGrid, StandardCard } from '@/components/layout/StandardPageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PlayIcon,
  PencilIcon,
  DocumentDuplicateIcon,
  TrashIcon,
  UserGroupIcon,
  CodeBracketIcon,
  ChartBarIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import {
  CheckCircleIcon as CheckCircleIconSolid,
  PlayIcon as PlayIconSolid,
  PauseIcon as PauseIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid,
  PencilIcon as PencilIconSolid
} from '@heroicons/react/24/solid';
import { useWorkflows, useWorkflowAnalytics, type WorkflowData } from '@/hooks/useWorkflows';

const categories = [
  { value: 'all', label: 'All Categories' },
  { value: 'automation', label: 'Automation' },
  { value: 'data-processing', label: 'Data Processing' },
  { value: 'ai-pipeline', label: 'AI Pipeline' },
  { value: 'integration', label: 'Integration' },
  { value: 'monitoring', label: 'Monitoring' }
];

export default function WorkflowsPage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<WorkflowData | null>(null);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    category: 'automation',
    complexity: 'simple',
    llm_model_id: '',
    version: '1.0.0',
    timeout_seconds: 3600,
    is_public: false,
    triggers: [] as string[],
    url: '',
  });
  const { models: llmModels, loading: llmLoading } = useLLMModels();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedComplexity, setSelectedComplexity] = useState('all');

  const { state: projectState } = useProject();

  // Use real API data from hooks
  const {
    workflows,
    loading,
    error,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    executeWorkflow,
    pauseWorkflow,
    resumeWorkflow,
  } = useWorkflows();
  
  const analytics = useWorkflowAnalytics();


  const filteredWorkflows = useMemo(() => {
    return workflows.filter(workflow => {
      const matchesSearch = workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || workflow.category === selectedCategory;
      const matchesStatus = selectedStatus === 'all' || workflow.status === selectedStatus;
      const matchesComplexity = selectedComplexity === 'all' || workflow.complexity === selectedComplexity;
      
      // Project filtering: if a project is selected, only show workflows that have tags matching the project tags
      const matchesProject = !projectState.selectedProject || projectState.selectedProject.name === 'Default Project' ||
                             projectState.selectedProject.tags.some(projectTag => 
                               workflow.tags.includes(projectTag)
                             );
      
      return matchesSearch && matchesCategory && matchesStatus && matchesComplexity && matchesProject;
    });
  }, [workflows, searchTerm, selectedCategory, selectedStatus, selectedComplexity, projectState.selectedProject]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIconSolid className="h-4 w-4 text-green-500" />;
      case 'running':
        return <PlayIconSolid className="h-4 w-4 text-blue-500" />;
      case 'inactive':
        return <PauseIconSolid className="h-4 w-4 text-gray-500" />;
      case 'error':
        return <ExclamationTriangleIconSolid className="h-4 w-4 text-red-500" />;
      case 'draft':
        return <PencilIconSolid className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircleIconSolid className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-300 dark:border-gray-700';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-300 dark:border-gray-700';
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple':
        return 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800';
      case 'moderate':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-300 dark:border-yellow-800';
      case 'complex':
        return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-900/20 dark:text-gray-300 dark:border-gray-700';
    }
  };

  const handleWorkflowAction = async (workflowId: string, action: string) => {
    console.log(`Performing ${action} on workflow ${workflowId}`);
    
    try {
      switch (action) {
        case 'run':
          await executeWorkflow(workflowId);
          break;
        case 'pause':
          await pauseWorkflow(workflowId);
          break;
        case 'resume':
          await resumeWorkflow(workflowId);
          break;
        case 'delete':
          if (confirm('Are you sure you want to delete this workflow?')) {
            await deleteWorkflow(workflowId);
          }
          break;
        case 'copy':
          // Clone workflow logic
          const workflow = workflows.find(w => w.id === workflowId);
          if (workflow) {
            await createWorkflow({
              name: `${workflow.name} (Copy)`,
              description: workflow.description,
              category: workflow.category,
              complexity: workflow.complexity,
              agents: workflow.agents,
              tools: workflow.tools,
              tags: workflow.tags,
            });
          }
          break;
        case 'edit':
          const editWorkflow = workflows.find(w => w.id === workflowId);
          if (editWorkflow) {
            setEditingWorkflow(editWorkflow);
            setShowCreateDialog(true);
          }
          break;
        default:
          console.log(`Action ${action} not implemented`);
      }
    } catch (err) {
      console.error(`Error performing ${action}:`, err);
    }
  };

  const stats = {
    total: analytics.totalWorkflows,
    active: analytics.activeWorkflows,
    totalExecutions: analytics.totalRuns,
    avgSuccessRate: analytics.totalSuccessfulRuns > 0 
      ? (analytics.totalSuccessfulRuns / analytics.totalRuns) * 100 
      : 0
  };

  if (loading) {
    return (
      <AuthGuard>
        <StandardPageLayout title="Workflow Management" description="Loading workflows...">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <ArrowPathIcon className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
              <div className="text-lg">Loading workflows...</div>
            </div>
          </div>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  if (error) {
    return (
      <AuthGuard>
        <StandardPageLayout title="Workflow Management" description="Error loading workflows">
          <div className="flex items-center justify-center h-64">
            <div className="text-red-500">Error loading workflows: {error}</div>
          </div>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <StandardPageLayout
        title="Workflow Management"
        description="Design, deploy, and monitor your multi-agent workflows"
        actions={
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            {projectState.selectedProject && (
              <div className="flex items-center gap-2">
                <FunnelIcon className="w-4 h-4 text-blue-500" />
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                  Filtered by: {projectState.selectedProject.name}
                </Badge>
              </div>
            )}
            <div className="flex items-center space-x-3">
              <Button variant="outline">
                <CodeBracketIcon className="mr-2 h-4 w-4" />
                Templates
              </Button>
              <Button onClick={() => {
                setEditingWorkflow(null);
                setShowCreateDialog(true);
              }}>
                <PlusIcon className="mr-2 h-4 w-4" />
                Create Workflow
              </Button>
            </div>
          </div>
        }
      >
        {/* Main content would go here */}
        
        {/* Create Workflow Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-8 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">{editingWorkflow ? 'Edit Workflow' : 'Create Workflow'}</h2>
            <div className="space-y-4">
              <Input
                placeholder="Workflow Name"
                value={editingWorkflow ? editingWorkflow.name : newWorkflow.name}
                onChange={e => {
                  if (editingWorkflow) {
                    setEditingWorkflow({ ...editingWorkflow, name: e.target.value });
                  } else {
                    setNewWorkflow({ ...newWorkflow, name: e.target.value });
                  }
                }}
              />
              <Input
                placeholder="Description"
                value={editingWorkflow ? editingWorkflow.description : newWorkflow.description}
                onChange={e => {
                  if (editingWorkflow) {
                    setEditingWorkflow({ ...editingWorkflow, description: e.target.value });
                  } else {
                    setNewWorkflow({ ...newWorkflow, description: e.target.value });
                  }
                }}
              />
              <select
                value={newWorkflow.category}
                onChange={e => setNewWorkflow({ ...newWorkflow, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                {categories.filter(category => category.value !== 'all').map(category => (
                  <option key={category.value} value={category.value}>{category.label}</option>
                ))}
              </select>
              <select
                value={newWorkflow.complexity}
                onChange={e => setNewWorkflow({ ...newWorkflow, complexity: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="simple">Simple</option>
                <option value="moderate">Moderate</option>
                <option value="complex">Complex</option>
              </select>
              <select
                value={newWorkflow.llm_model_id}
                onChange={e => setNewWorkflow({ ...newWorkflow, llm_model_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="">Select LLM Model (optional)</option>
                {llmModels
                  .filter(model => model.model_type === 'chat' || model.model_type === 'completion' || model.model_type === 'multimodal')
                  .map(model => (
                    <option key={model.id} value={model.id}>{model.display_name || model.name} ({model.provider})</option>
                  ))}
              </select>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  placeholder="Version (e.g., 1.0.0)"
                  value={newWorkflow.version}
                  onChange={e => setNewWorkflow({ ...newWorkflow, version: e.target.value })}
                />
                <Input
                  placeholder="Timeout (seconds)"
                  type="number"
                  value={newWorkflow.timeout_seconds}
                  onChange={e => setNewWorkflow({ ...newWorkflow, timeout_seconds: parseInt(e.target.value) || 3600 })}
                />
              </div>
              <Input
                placeholder="Workflow URL (optional)"
                value={newWorkflow.url}
                onChange={e => setNewWorkflow({ ...newWorkflow, url: e.target.value })}
              />
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={newWorkflow.is_public}
                  onChange={e => setNewWorkflow({ ...newWorkflow, is_public: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                />
                <label htmlFor="is_public" className="text-sm font-medium text-gray-900 dark:text-white">
                  Make workflow public
                </label>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => {
                setShowCreateDialog(false);
                setEditingWorkflow(null);
              }}>Cancel</Button>
              <Button
                onClick={async () => {
                  const workflowData = editingWorkflow ? {
                    name: editingWorkflow.name,
                    description: editingWorkflow.description,
                    category: editingWorkflow.category,
                    complexity: editingWorkflow.complexity,
                    llm_model_id: editingWorkflow.llm_model_id || undefined,
                  } : {
                    name: newWorkflow.name,
                    description: newWorkflow.description,
                    category: newWorkflow.category as "monitoring" | "automation" | "data-processing" | "ai-pipeline" | "integration",
                    complexity: newWorkflow.complexity as "simple" | "moderate" | "complex",
                    llm_model_id: newWorkflow.llm_model_id || undefined,
                    version: newWorkflow.version,
                    timeout_seconds: newWorkflow.timeout_seconds,
                    is_public: newWorkflow.is_public,
                    url: newWorkflow.url || undefined,
                  };
                  
                  if (editingWorkflow) {
                    await updateWorkflow(editingWorkflow.id, workflowData);
                  } else {
                    await createWorkflow(workflowData);
                  }
                  
                  setShowCreateDialog(false);
                  setEditingWorkflow(null);
                  setNewWorkflow({ 
                    name: '', 
                    description: '', 
                    category: 'automation', 
                    complexity: 'simple', 
                    llm_model_id: '',
                    version: '1.0.0',
                    timeout_seconds: 3600,
                    is_public: false,
                    triggers: [],
                    url: '',
                  });
                }}
                disabled={editingWorkflow ? (!editingWorkflow.name || !editingWorkflow.description) : (!newWorkflow.name || !newWorkflow.description)}
              >
                {editingWorkflow ? 'Update' : 'Create'}
              </Button>
            </div>
          </div>
        </div>
      )}

        {/* Stats Cards */}
        <StandardSection>
          <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-blue-600">
                  {stats.total}
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Total Workflows</p>
              </div>
            </StandardCard>
            
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-green-600">
                  {stats.active}
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Active/Running</p>
              </div>
            </StandardCard>
            
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-purple-600">
                  {stats.totalExecutions.toLocaleString()}
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Total Executions</p>
              </div>
            </StandardCard>
            
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-orange-600">
                  {stats.avgSuccessRate.toFixed(1)}%
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Avg Success Rate</p>
              </div>
            </StandardCard>
          </StandardGrid>
        </StandardSection>

        {/* Search and Filters */}
        <StandardSection>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search workflows by name or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              {categories.map(category => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
            
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="running">Running</option>
              <option value="inactive">Inactive</option>
              <option value="error">Error</option>
              <option value="draft">Draft</option>
            </select>
            
            <select
              value={selectedComplexity}
              onChange={(e) => setSelectedComplexity(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">All Complexity</option>
              <option value="simple">Simple</option>
              <option value="moderate">Moderate</option>
              <option value="complex">Complex</option>
            </select>
          </div>
        </StandardSection>

        {/* Workflows Grid */}
        <StandardSection>
          {filteredWorkflows.length === 0 ? (
            <StandardCard className="p-12">
              <div className="text-center">
                <div className="text-gray-400 text-6xl mb-4">⚙️</div>
                <h3 className="text-heading-2 text-gray-900 dark:text-white mb-2">
                  No workflows found
                </h3>
                <p className="text-body text-gray-600 dark:text-gray-400 mb-4">
                  {searchTerm || selectedCategory !== 'all' || selectedStatus !== 'all' || selectedComplexity !== 'all'
                    ? 'Try adjusting your search or filters'
                    : 'Get started by creating your first workflow'}
                </p>
                {!searchTerm && selectedCategory === 'all' && selectedStatus === 'all' && selectedComplexity === 'all' && (
                  <Button>
                    <PlusIcon className="w-4 h-4 mr-2" />
                    Create Your First Workflow
                  </Button>
                )}
              </div>
            </StandardCard>
          ) : (
            <StandardGrid cols={{ default: 1, lg: 2 }} gap="md">
              {filteredWorkflows.map((workflow) => (
                <StandardCard key={workflow.id}>
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3 min-w-0 flex-1">
                        {getStatusIcon(workflow.status)}
                        <div className="min-w-0 flex-1">
                          <h3 className="text-heading-2 text-gray-900 dark:text-white truncate">
                            {workflow.name}
                          </h3>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge className={getStatusColor(workflow.status)}>
                              {workflow.status}
                            </Badge>
                            <Badge className={getComplexityColor(workflow.complexity)}>
                              {workflow.complexity}
                            </Badge>
                            {/* Removed isTemplate check since it doesn't exist in WorkflowData */}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-body-sm text-gray-600 dark:text-gray-300">
                      {workflow.description}
                    </p>
                    
                    {/* Agents */}
                    <div>
                      <div className="text-body-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Agents ({workflow.agents.length})
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {workflow.agents.slice(0, 3).map((agent) => (
                          <div key={agent.id} className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-800 rounded px-2 py-1">
                            <UserGroupIcon className="h-3 w-3 text-blue-500" />
                            <span className="text-caption">{agent.name}</span>
                          </div>
                        ))}
                        {workflow.agents.length > 3 && (
                          <div className="bg-gray-100 dark:bg-gray-800 rounded px-2 py-1">
                            <span className="text-caption">+{workflow.agents.length - 3} more</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Performance Metrics */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-caption text-gray-500">Executions</div>
                        <div className="text-body font-medium">{workflow.execution.totalRuns.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-caption text-gray-500">Success Rate</div>
                        <div className="text-body font-medium">
                          {workflow.execution.totalRuns > 0 
                            ? Math.round((workflow.execution.successfulRuns / workflow.execution.totalRuns) * 100)
                            : 0}%
                        </div>
                      </div>
                      <div>
                        <div className="text-caption text-gray-500">Avg Time</div>
                        <div className="text-body font-medium">{workflow.execution.avgDuration}s</div>
                      </div>
                      <div>
                        <div className="text-caption text-gray-500">Last Run</div>
                        <div className="text-body font-medium">
                          {workflow.execution.lastRun ? new Date(workflow.execution.lastRun).toLocaleDateString() : 'Never'}
                        </div>
                      </div>
                    </div>

                    {/* Triggers */}
                    <div>
                      <div className="text-body-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Triggers
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {workflow.schedule?.triggers?.map((trigger: string, index: number) => (
                          <Badge key={index} variant="outline" className="text-caption">
                            {trigger}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Metadata */}
                    <div className="text-caption text-gray-500 pt-2 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center justify-between">
                        <span>Created by {workflow.owner}</span>
                        {/* Version not available in WorkflowData interface */}
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span>Category: {workflow.category}</span>
                        <span>{new Date(workflow.updated_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkflowAction(workflow.id, 'run')}
                          disabled={workflow.status === 'error' || workflow.status === 'draft'}
                        >
                          <PlayIcon className="h-3 w-3" />
                          Run
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkflowAction(workflow.id, 'edit')}
                        >
                          <PencilIcon className="h-3 w-3" />
                          Edit
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkflowAction(workflow.id, 'copy')}
                        >
                          <DocumentDuplicateIcon className="h-3 w-3" />
                          Clone
                        </Button>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkflowAction(workflow.id, 'metrics')}
                        >
                          <ChartBarIcon className="h-3 w-3" />
                          Metrics
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleWorkflowAction(workflow.id, 'delete')}
                          className="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                        >
                          <TrashIcon className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </StandardCard>
              ))}
            </StandardGrid>
          )}
        </StandardSection>

      </StandardPageLayout>
    </AuthGuard>
  );
}
