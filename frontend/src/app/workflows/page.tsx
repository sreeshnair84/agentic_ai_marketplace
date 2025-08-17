'use client';

import { useState, useMemo } from 'react';
import { useProject } from '@/store/projectContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  Search, 
  Workflow, 
  Play, 
  Pause, 
  Square,
  Edit, 
  Copy,
  Trash2,
  Bot,
  Clock,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Users,
  GitBranch,
  Timer,
  BarChart3,
  Filter
} from 'lucide-react';

interface WorkflowData {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'running' | 'error' | 'draft';
  category: string;
  tags: string[];
  agents: Array<{
    id: string;
    name: string;
    role: string;
  }>;
  triggers: string[];
  executionCount: number;
  lastExecuted: string;
  avgExecutionTime: string;
  successRate: number;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  version: string;
  isTemplate: boolean;
  complexity: 'simple' | 'moderate' | 'complex';
}

const mockWorkflows: WorkflowData[] = [
  {
    id: '1',
    name: 'Customer Support Pipeline',
    description: 'Automated customer inquiry processing with intelligent routing and escalation',
    status: 'active',
    category: 'Customer Service',
    tags: ['support', 'customer', 'automation'],
    agents: [
      { id: '1', name: 'Classifier Agent', role: 'Classification' },
      { id: '2', name: 'Support Agent', role: 'Response' },
      { id: '3', name: 'Escalation Agent', role: 'Escalation' }
    ],
    triggers: ['email_received', 'chat_message', 'api_request'],
    executionCount: 1247,
    lastExecuted: '2 minutes ago',
    avgExecutionTime: '1.2s',
    successRate: 97.8,
    createdBy: 'Sarah Chen',
    createdAt: '2024-01-15',
    updatedAt: '2024-08-10',
    version: '2.1.0',
    isTemplate: false,
    complexity: 'moderate'
  },
  {
    id: '2',
    name: 'Document Analysis Workflow',
    description: 'Comprehensive document processing with extraction, analysis, and summarization',
    status: 'running',
    category: 'Document Processing',
    tags: ['analytics', 'data', 'general'],
    agents: [
      { id: '4', name: 'Document Reader', role: 'Extraction' },
      { id: '5', name: 'Text Analyzer', role: 'Analysis' },
      { id: '6', name: 'Summary Generator', role: 'Summarization' }
    ],
    triggers: ['file_upload', 'folder_watch'],
    executionCount: 567,
    lastExecuted: '5 minutes ago',
    avgExecutionTime: '4.7s',
    successRate: 94.2,
    createdBy: 'Mike Johnson',
    createdAt: '2024-02-20',
    updatedAt: '2024-08-11',
    version: '1.5.3',
    isTemplate: true,
    complexity: 'complex'
  },
  {
    id: '3',
    name: 'Research & Report Generation',
    description: 'Automated research pipeline with web search, analysis, and report creation',
    status: 'inactive',
    category: 'Research',
    tags: ['analytics', 'reporting', 'general'],
    agents: [
      { id: '7', name: 'Web Researcher', role: 'Research' },
      { id: '8', name: 'Data Analyzer', role: 'Analysis' },
      { id: '9', name: 'Report Writer', role: 'Writing' }
    ],
    triggers: ['manual_trigger', 'scheduled'],
    executionCount: 89,
    lastExecuted: '2 days ago',
    avgExecutionTime: '12.3s',
    successRate: 91.0,
    createdBy: 'Emily Davis',
    createdAt: '2024-03-10',
    updatedAt: '2024-07-25',
    version: '1.0.2',
    isTemplate: false,
    complexity: 'complex'
  },
  {
    id: '4',
    name: 'Code Review Assistant',
    description: 'Automated code review with quality analysis and improvement suggestions',
    status: 'draft',
    category: 'Development',
    tags: ['general', 'default'],
    agents: [
      { id: '10', name: 'Code Analyzer', role: 'Analysis' },
      { id: '11', name: 'Quality Checker', role: 'Quality Control' },
      { id: '12', name: 'Documentation Generator', role: 'Documentation' }
    ],
    triggers: ['git_push', 'pr_created'],
    executionCount: 23,
    lastExecuted: '1 week ago',
    avgExecutionTime: '8.9s',
    successRate: 88.5,
    createdBy: 'Alex Rodriguez',
    createdAt: '2024-07-30',
    updatedAt: '2024-08-05',
    version: '0.9.1',
    isTemplate: false,
    complexity: 'moderate'
  },
  {
    id: '5',
    name: 'Data Pipeline Processor',
    description: 'ETL workflow for data extraction, transformation, and loading with validation',
    status: 'error',
    category: 'Data Processing',
    tags: ['analytics', 'data', 'ml'],
    agents: [
      { id: '13', name: 'Data Extractor', role: 'Extraction' },
      { id: '14', name: 'Data Transformer', role: 'Transformation' },
      { id: '15', name: 'Data Validator', role: 'Validation' }
    ],
    triggers: ['database_change', 'scheduled'],
    executionCount: 342,
    lastExecuted: '3 hours ago',
    avgExecutionTime: '6.1s',
    successRate: 82.3,
    createdBy: 'David Kim',
    createdAt: '2024-04-12',
    updatedAt: '2024-08-12',
    version: '1.3.0',
    isTemplate: true,
    complexity: 'complex'
  },
  {
    id: '6',
    name: 'Simple Task Automation',
    description: 'Basic task automation for routine operations and notifications',
    status: 'active',
    category: 'Automation',
    tags: ['general', 'automation', 'default'],
    agents: [
      { id: '16', name: 'Task Processor', role: 'Processing' },
      { id: '17', name: 'Notifier', role: 'Notification' }
    ],
    triggers: ['api_call', 'webhook'],
    executionCount: 2156,
    lastExecuted: '10 minutes ago',
    avgExecutionTime: '0.8s',
    successRate: 99.2,
    createdBy: 'Lisa Wang',
    createdAt: '2024-01-05',
    updatedAt: '2024-08-01',
    version: '1.1.0',
    isTemplate: true,
    complexity: 'simple'
  }
];

const categories = [
  { value: 'all', label: 'All Categories' },
  { value: 'Customer Service', label: 'Customer Service' },
  { value: 'Document Processing', label: 'Document Processing' },
  { value: 'Research', label: 'Research' },
  { value: 'Development', label: 'Development' },
  { value: 'Data Processing', label: 'Data Processing' },
  { value: 'Automation', label: 'Automation' }
];

export default function WorkflowsPage() {
  const [workflows] = useState<WorkflowData[]>(mockWorkflows);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedComplexity, setSelectedComplexity] = useState('all');

  const { state: projectState } = useProject();

  const filteredWorkflows = useMemo(() => {
    return workflows.filter(workflow => {
      const matchesSearch = workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           workflow.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || workflow.category === selectedCategory;
      const matchesStatus = selectedStatus === 'all' || workflow.status === selectedStatus;
      const matchesComplexity = selectedComplexity === 'all' || workflow.complexity === selectedComplexity;
      
      // Project filtering: if a project is selected, only show workflows that have tags matching the project tags
      const matchesProject = !projectState.selectedProject || 
                             projectState.selectedProject.tags.some(projectTag => 
                               workflow.tags.includes(projectTag)
                             );
      
      return matchesSearch && matchesCategory && matchesStatus && matchesComplexity && matchesProject;
    });
  }, [workflows, searchTerm, selectedCategory, selectedStatus, selectedComplexity, projectState.selectedProject]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running':
        return <Play className="h-4 w-4 text-blue-500" />;
      case 'inactive':
        return <Pause className="h-4 w-4 text-gray-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'draft':
        return <Edit className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'moderate':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'complex':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const handleWorkflowAction = (workflowId: string, action: string) => {
    console.log(`Performing ${action} on workflow ${workflowId}`);
    // Implement workflow actions
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Workflow Management
              </h1>
              <div className="flex items-center gap-2 mt-2">
                <p className="text-gray-600 dark:text-gray-300">
                  Design, deploy, and monitor your multi-agent workflows
                </p>
                {projectState.selectedProject && (
                  <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-blue-500" />
                    <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                      Filtered by: {projectState.selectedProject.name}
                    </Badge>
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline">
                <GitBranch className="mr-2 h-4 w-4" />
                Templates
              </Button>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Workflow
              </Button>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Workflow className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold">{workflows.length}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Total Workflows</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Play className="h-5 w-5 text-green-500" />
                <div>
                  <div className="text-2xl font-bold">
                    {workflows.filter(w => w.status === 'active' || w.status === 'running').length}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Active/Running</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-purple-500" />
                <div>
                  <div className="text-2xl font-bold">
                    {workflows.reduce((acc, w) => acc + w.executionCount, 0).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Total Executions</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-orange-500" />
                <div>
                  <div className="text-2xl font-bold">
                    {(workflows.reduce((acc, w) => acc + w.successRate, 0) / workflows.length).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300">Avg Success Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <div className="mb-6">
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search workflows..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md"
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
                  className="px-3 py-2 border border-gray-300 rounded-md"
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
                  className="px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="all">All Complexity</option>
                  <option value="simple">Simple</option>
                  <option value="moderate">Moderate</option>
                  <option value="complex">Complex</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workflows Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredWorkflows.map((workflow) => (
            <Card key={workflow.id} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(workflow.status)}
                    <div>
                      <CardTitle className="text-lg">{workflow.name}</CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge className={getStatusColor(workflow.status)}>
                          {workflow.status}
                        </Badge>
                        <Badge className={getComplexityColor(workflow.complexity)}>
                          {workflow.complexity}
                        </Badge>
                        {workflow.isTemplate && (
                          <Badge variant="outline">Template</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                  {workflow.description}
                </p>
                
                <div className="space-y-4">
                  {/* Agents */}
                  <div>
                    <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Agents ({workflow.agents.length})
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {workflow.agents.slice(0, 3).map((agent) => (
                        <div key={agent.id} className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-800 rounded px-2 py-1">
                          <Bot className="h-3 w-3 text-blue-500" />
                          <span className="text-xs">{agent.name}</span>
                        </div>
                      ))}
                      {workflow.agents.length > 3 && (
                        <div className="bg-gray-100 dark:bg-gray-800 rounded px-2 py-1">
                          <span className="text-xs">+{workflow.agents.length - 3} more</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">Executions</div>
                      <div className="font-medium">{workflow.executionCount.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Success Rate</div>
                      <div className="font-medium">{workflow.successRate}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Avg Time</div>
                      <div className="font-medium">{workflow.avgExecutionTime}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Last Run</div>
                      <div className="font-medium">{workflow.lastExecuted}</div>
                    </div>
                  </div>

                  {/* Triggers */}
                  <div>
                    <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Triggers
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {workflow.triggers.map((trigger, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {trigger}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="text-xs text-gray-500 pt-2 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                      <span>Created by {workflow.createdBy}</span>
                      <span>v{workflow.version}</span>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span>Category: {workflow.category}</span>
                      <span>{workflow.updatedAt}</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleWorkflowAction(workflow.id, 'run')}
                      disabled={workflow.status === 'error' || workflow.status === 'draft'}
                    >
                      <Play className="h-3 w-3" />
                      Run
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleWorkflowAction(workflow.id, 'edit')}
                    >
                      <Edit className="h-3 w-3" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleWorkflowAction(workflow.id, 'copy')}
                    >
                      <Copy className="h-3 w-3" />
                      Clone
                    </Button>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleWorkflowAction(workflow.id, 'metrics')}
                    >
                      <BarChart3 className="h-3 w-3" />
                      Metrics
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleWorkflowAction(workflow.id, 'delete')}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
