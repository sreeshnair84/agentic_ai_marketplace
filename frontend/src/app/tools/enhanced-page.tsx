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
  Code,
  Settings,
  Activity,
  FileText,
  Globe,
  Workflow,
  Brain,
  Bot,
  Target,
  Upload,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  Users,
  Layers,
  GitBranch
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import EnhancedToolTemplateForm from './EnhancedToolTemplateForm';
import EnhancedToolInstanceForm from './EnhancedToolInstanceForm';
import RAGPipelineBuilder from './RAGPipelineBuilder';
import AgentTemplateBuilder from './AgentTemplateBuilder';

// Enhanced interfaces for the new tool management system
interface ToolTemplate {
  id?: string;
  name: string;
  description: string;
  template_type: 'rag_pipeline' | 'sql_agent' | 'mcp_client' | 'code_interpreter' | 'web_scraper' | 'file_processor' | 'api_integration' | 'workflow_orchestrator';
  version: string;
  default_configuration: Record<string, any>;
  schema_definition: Record<string, any>;
  code_template?: string;
  metadata?: Record<string, any>;
  is_active: boolean;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
}

interface ToolInstance {
  id?: string;
  template_id: string;
  name: string;
  description: string;
  configuration: Record<string, any>;
  runtime_config?: Record<string, any>;
  status: 'active' | 'inactive' | 'error' | 'running';
  metadata?: Record<string, any>;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  template?: ToolTemplate;
}

interface RAGPipeline {
  id?: string;
  tool_instance_id: string;
  name: string;
  description: string;
  data_sources: Array<{
    type: 'text' | 'file' | 'url';
    source: string;
    metadata?: Record<string, any>;
  }>;
  ingestion_config: Record<string, any>;
  vectorization_config: Record<string, any>;
  status: 'active' | 'inactive' | 'processing' | 'error';
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

interface AgentTemplate {
  id?: string;
  name: string;
  description: string;
  framework: 'langgraph' | 'crewai' | 'autogen' | 'semantic_kernel';
  workflow_definition: Record<string, any>;
  default_configuration: Record<string, any>;
  tool_associations: string[];
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

interface ExecutionMetrics {
  instance_id: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_execution_time: number;
  last_execution_at?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005';

export default function EnhancedToolsManagement() {
  // State management
  const [toolTemplates, setToolTemplates] = useState<ToolTemplate[]>([]);
  const [toolInstances, setToolInstances] = useState<ToolInstance[]>([]);
  const [ragPipelines, setRAGPipelines] = useState<RAGPipeline[]>([]);
  const [agentTemplates, setAgentTemplates] = useState<AgentTemplate[]>([]);
  const [executionMetrics, setExecutionMetrics] = useState<Record<string, ExecutionMetrics>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTemplateType, setSelectedTemplateType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedTab, setSelectedTab] = useState<'overview' | 'templates' | 'instances' | 'rag-pipelines' | 'agents'>('overview');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<ToolTemplate | null>(null);
  const [editingInstance, setEditingInstance] = useState<ToolInstance | null>(null);
  const [selectedInstance, setSelectedInstance] = useState<ToolInstance | null>(null);

  const { state: projectState } = useProject();

  // Fetch data from enhanced backend APIs
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [
        templatesRes,
        instancesRes,
        ragPipelinesRes,
        agentTemplatesRes
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/tool-management/templates`),
        fetch(`${API_BASE_URL}/tool-management/instances`),
        fetch(`${API_BASE_URL}/rag-pipelines/`),
        fetch(`${API_BASE_URL}/api/agents/templates`)
      ]);

      if (!templatesRes.ok || !instancesRes.ok) {
        throw new Error('Failed to fetch tools data from enhanced backend');
      }

      const [templates, instances] = await Promise.all([
        templatesRes.json(),
        instancesRes.json()
      ]);

      setToolTemplates(templates);
      setToolInstances(instances);

      // Fetch RAG pipelines if available
      if (ragPipelinesRes.ok) {
        const ragPipelines = await ragPipelinesRes.json();
        setRAGPipelines(ragPipelines);
      }

      // Fetch agent templates if available
      if (agentTemplatesRes.ok) {
        const agentTemplates = await agentTemplatesRes.json();
        setAgentTemplates(agentTemplates);
      }

      // Fetch metrics for instances
      const metricsPromises = instances.map(async (instance: ToolInstance) => {
        try {
          const metricsRes = await fetch(`${API_BASE_URL}/tool-management/instances/${instance.id}/metrics`);
          if (metricsRes.ok) {
            const metrics = await metricsRes.json();
            return { [instance.id!]: metrics };
          }
        } catch (err) {
          console.warn(`Failed to fetch metrics for instance ${instance.id}`);
        }
        return null;
      });

      const metricsResults = await Promise.all(metricsPromises);
      const combinedMetrics = metricsResults.reduce((acc, metrics) => {
        if (metrics) {
          return { ...acc, ...metrics };
        }
        return acc;
      }, {});
      
      setExecutionMetrics(combinedMetrics);

    } catch (err) {
      console.error('Error fetching enhanced tools data:', err);
      setError('Failed to load tools data. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Tool type icons and colors
  const getToolTypeIcon = (templateType: string) => {
    switch (templateType) {
      case 'rag_pipeline':
        return <Database className="h-5 w-5 text-blue-600" />;
      case 'sql_agent':
        return <Database className="h-5 w-5 text-green-600" />;
      case 'mcp_client':
        return <Zap className="h-5 w-5 text-yellow-600" />;
      case 'code_interpreter':
        return <Code className="h-5 w-5 text-purple-600" />;
      case 'web_scraper':
        return <Globe className="h-5 w-5 text-cyan-600" />;
      case 'file_processor':
        return <FileText className="h-5 w-5 text-orange-600" />;
      case 'api_integration':
        return <Cloud className="h-5 w-5 text-indigo-600" />;
      case 'workflow_orchestrator':
        return <Workflow className="h-5 w-5 text-red-600" />;
      default:
        return <Settings className="h-5 w-5 text-gray-600" />;
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
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  // Handle tool instance actions
  const handleActivateInstance = async (instance: ToolInstance) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tool-management/instances/${instance.id}/activate`, {
        method: 'POST'
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      console.error('Error activating instance:', err);
      setError('Failed to activate instance');
    }
  };

  const handleDeactivateInstance = async (instance: ToolInstance) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tool-management/instances/${instance.id}/deactivate`, {
        method: 'POST'
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      console.error('Error deactivating instance:', err);
      setError('Failed to deactivate instance');
    }
  };

  const handleExecuteInstance = async (instance: ToolInstance) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tool-management/instances/${instance.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          execution_parameters: {
            test_mode: true,
            timeout: 30
          }
        })
      });
      if (response.ok) {
        const result = await response.json();
        console.log('Execution result:', result);
        await fetchData(); // Refresh metrics
      }
    } catch (err) {
      console.error('Error executing instance:', err);
      setError('Failed to execute instance');
    }
  };

  // Filtered data based on search and filters
  const filteredTemplates = useMemo(() => {
    return toolTemplates.filter(template => {
      const matchesSearch = !searchTerm || 
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        template.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = selectedTemplateType === 'all' || template.template_type === selectedTemplateType;
      return matchesSearch && matchesType;
    });
  }, [toolTemplates, searchTerm, selectedTemplateType]);

  const filteredInstances = useMemo(() => {
    return toolInstances.filter(instance => {
      const matchesSearch = !searchTerm || 
        instance.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        instance.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = selectedStatus === 'all' || instance.status === selectedStatus;
      return matchesSearch && matchesStatus;
    });
  }, [toolInstances, searchTerm, selectedStatus]);

  // Statistics for overview
  const stats = useMemo(() => {
    const totalTemplates = toolTemplates.length;
    const activeTemplates = toolTemplates.filter(t => t.is_active).length;
    const totalInstances = toolInstances.length;
    const activeInstances = toolInstances.filter(i => i.status === 'active').length;
    const totalPipelines = ragPipelines.length;
    const activePipelines = ragPipelines.filter(p => p.status === 'active').length;
    const totalAgents = agentTemplates.length;
    const activeAgents = agentTemplates.filter(a => a.is_active).length;

    return {
      totalTemplates,
      activeTemplates,
      totalInstances,
      activeInstances,
      totalPipelines,
      activePipelines,
      totalAgents,
      activeAgents
    };
  }, [toolTemplates, toolInstances, ragPipelines, agentTemplates]);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600 dark:text-gray-400">Loading enhanced tools data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Enhanced Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Enhanced Tools Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Comprehensive tool templates, instances, RAG pipelines, and agent management with LangGraph integration
          </p>
          {projectState.selectedProject && (
            <div className="flex items-center gap-2 mt-2">
              <Filter className="w-4 h-4 text-blue-500" />
              <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                Project: {projectState.selectedProject.name}
              </Badge>
            </div>
          )}
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={fetchData} className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </Button>
          <Button 
            onClick={() => setShowCreateForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Create New</span>
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

      {/* Enhanced Tabs */}
      <Tabs value={selectedTab} onValueChange={(value) => setSelectedTab(value as any)}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex items-center space-x-2">
            <Layers className="h-4 w-4" />
            <span>Templates ({toolTemplates.length})</span>
          </TabsTrigger>
          <TabsTrigger value="instances" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>Instances ({toolInstances.length})</span>
          </TabsTrigger>
          <TabsTrigger value="rag-pipelines" className="flex items-center space-x-2">
            <Database className="h-4 w-4" />
            <span>RAG Pipelines ({ragPipelines.length})</span>
          </TabsTrigger>
          <TabsTrigger value="agents" className="flex items-center space-x-2">
            <Bot className="h-4 w-4" />
            <span>Agents ({agentTemplates.length})</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tool Templates</CardTitle>
                <Layers className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalTemplates}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.activeTemplates} active
                </p>
                <Progress 
                  value={stats.totalTemplates ? (stats.activeTemplates / stats.totalTemplates) * 100 : 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Tool Instances</CardTitle>
                <Settings className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalInstances}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.activeInstances} active
                </p>
                <Progress 
                  value={stats.totalInstances ? (stats.activeInstances / stats.totalInstances) * 100 : 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">RAG Pipelines</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalPipelines}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.activePipelines} active
                </p>
                <Progress 
                  value={stats.totalPipelines ? (stats.activePipelines / stats.totalPipelines) * 100 : 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Agent Templates</CardTitle>
                <Bot className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalAgents}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.activeAgents} active
                </p>
                <Progress 
                  value={stats.totalAgents ? (stats.activeAgents / stats.totalAgents) * 100 : 0} 
                  className="mt-2"
                />
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Recent Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {toolInstances.slice(0, 5).map((instance) => (
                  <div key={instance.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getToolTypeIcon(instance.template?.template_type || '')}
                      <div>
                        <p className="font-medium">{instance.name}</p>
                        <p className="text-sm text-gray-500">
                          {instance.template?.template_type} • {instance.status}
                        </p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(instance.status)}>
                      {instance.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          {/* Search and Filters */}
          <div className="flex space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            <select
              value={selectedTemplateType}
              onChange={(e) => setSelectedTemplateType(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">All Types</option>
              <option value="rag_pipeline">RAG Pipeline</option>
              <option value="sql_agent">SQL Agent</option>
              <option value="mcp_client">MCP Client</option>
              <option value="code_interpreter">Code Interpreter</option>
              <option value="web_scraper">Web Scraper</option>
              <option value="file_processor">File Processor</option>
              <option value="api_integration">API Integration</option>
              <option value="workflow_orchestrator">Workflow Orchestrator</option>
            </select>
          </div>

          {/* Templates Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      {getToolTypeIcon(template.template_type)}
                      <div>
                        <CardTitle className="text-lg">{template.name}</CardTitle>
                        <CardDescription>{template.template_type}</CardDescription>
                      </div>
                    </div>
                    <Badge variant={template.is_active ? "default" : "secondary"}>
                      {template.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {template.description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">v{template.version}</span>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Edit3 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Instances Tab */}
        <TabsContent value="instances" className="space-y-6">
          {/* Search and Filters */}
          <div className="flex space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search instances..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="running">Running</option>
              <option value="error">Error</option>
            </select>
          </div>

          {/* Instances List */}
          <div className="space-y-4">
            {filteredInstances.map((instance) => {
              const metrics = executionMetrics[instance.id!];
              return (
                <Card key={instance.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          {getToolTypeIcon(instance.template?.template_type || '')}
                          <h3 className="text-lg font-semibold">{instance.name}</h3>
                          <Badge className={getStatusColor(instance.status)}>
                            {instance.status}
                          </Badge>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 mb-4">
                          {instance.description}
                        </p>
                        
                        {/* Metrics */}
                        {metrics && (
                          <div className="grid grid-cols-4 gap-4 mb-4">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">
                                {metrics.total_executions}
                              </div>
                              <div className="text-xs text-gray-500">Total Runs</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-green-600">
                                {metrics.successful_executions}
                              </div>
                              <div className="text-xs text-gray-500">Successful</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-red-600">
                                {metrics.failed_executions}
                              </div>
                              <div className="text-xs text-gray-500">Failed</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-purple-600">
                                {metrics.average_execution_time.toFixed(2)}s
                              </div>
                              <div className="text-xs text-gray-500">Avg Time</div>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Actions */}
                      <div className="flex items-center space-x-2 ml-6">
                        {instance.status === 'active' && (
                          <Button
                            size="sm"
                            onClick={() => handleExecuteInstance(instance)}
                            className="flex items-center space-x-1"
                          >
                            <Play className="h-4 w-4" />
                            <span>Execute</span>
                          </Button>
                        )}
                        {instance.status === 'inactive' ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleActivateInstance(instance)}
                            className="flex items-center space-x-1"
                          >
                            <CheckCircle className="h-4 w-4" />
                            <span>Activate</span>
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeactivateInstance(instance)}
                            className="flex items-center space-x-1"
                          >
                            <XCircle className="h-4 w-4" />
                            <span>Deactivate</span>
                          </Button>
                        )}
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit3 className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* RAG Pipelines Tab */}
        <TabsContent value="rag-pipelines" className="space-y-6">
          <div className="text-center py-12">
            <Database className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              RAG Pipeline Builder
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Create and manage RAG pipelines for data ingestion and vectorization
            </p>
            <Button onClick={() => setShowCreateForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create RAG Pipeline
            </Button>
          </div>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-6">
          <div className="text-center py-12">
            <Bot className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Agent Template Builder
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Create agent templates with tool associations and LangGraph workflows
            </p>
            <Button onClick={() => setShowCreateForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Agent Template
            </Button>
          </div>
        </TabsContent>
      </Tabs>

      {/* Enhanced Create Forms */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden">
            {selectedTab === 'templates' && (
              <EnhancedToolTemplateForm
                template={editingTemplate || undefined}
                onSave={(template) => {
                  console.log('Saving template:', template);
                  setShowCreateForm(false);
                  fetchData();
                }}
                onCancel={() => setShowCreateForm(false)}
              />
            )}
            {selectedTab === 'instances' && (
              <EnhancedToolInstanceForm
                instance={editingInstance || undefined}
                templates={toolTemplates}
                onSave={(instance) => {
                  console.log('Saving instance:', instance);
                  setShowCreateForm(false);
                  fetchData();
                }}
                onCancel={() => setShowCreateForm(false)}
              />
            )}
            {selectedTab === 'rag-pipelines' && (
              <RAGPipelineBuilder
                onSave={(pipeline) => {
                  console.log('Saving RAG pipeline:', pipeline);
                  setShowCreateForm(false);
                  fetchData();
                }}
                onCancel={() => setShowCreateForm(false)}
              />
            )}
            {selectedTab === 'agents' && (
              <AgentTemplateBuilder
                toolTemplates={toolTemplates}
                onSave={(agentTemplate) => {
                  console.log('Saving agent template:', agentTemplate);
                  setShowCreateForm(false);
                  fetchData();
                }}
                onCancel={() => setShowCreateForm(false)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
