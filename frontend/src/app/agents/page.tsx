'use client';

import { useState, useMemo } from 'react';
import { useProject } from '@/store/projectContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AgentCard } from './components/agent-card';
import { AgentFilters } from './components/agent-filters';
import { CreateAgentDialog } from './components/create-agent-dialog';
// import { useAgents } from '@/hooks/use-agents';
import { PlusIcon, MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';

// Mock data for development
const mockAgents = [
  {
    id: '1',
    name: 'DataFetcher',
    description: 'An agent that fetches data from various sources and APIs.',
    framework: 'langchain' as const,
    skills: ['data-retrieval', 'api-integration', 'web-scraping'],
    status: 'active' as const,
    version: '1.0.0',
    createdAt: new Date('2023-10-01'),
    updatedAt: new Date('2023-10-01'),
    lastExecutedAt: new Date('2023-12-07'),
    executionCount: 125,
    systemPrompt: 'You are a data fetching specialist.',
    tags: ['analytics', 'data', 'general'],
    config: {
      model: 'gpt-4',
      temperature: 0.1,
      maxTokens: 2000,
      systemPrompt: 'You are a data fetching specialist.',
      tools: ['web-search', 'api-client'],
      memory: true,
      streaming: false,
      timeout: 30000,
      retryAttempts: 3,
    }
  },
  {
    id: '2',
    name: 'DataProcessor',
    description: 'An agent that processes and analyzes data with advanced algorithms.',
    framework: 'llamaindex' as const,
    skills: ['data-processing', 'analytics', 'machine-learning'],
    status: 'active' as const,
    version: '2.1.0',
    createdAt: new Date('2023-09-15'),
    updatedAt: new Date('2023-11-20'),
    lastExecutedAt: new Date('2023-12-06'),
    executionCount: 89,
    systemPrompt: 'You are a data processing expert.',
    tags: ['analytics', 'ml', 'data'],
    config: {
      model: 'gpt-4',
      temperature: 0.3,
      maxTokens: 4000,
      systemPrompt: 'You are a data processing expert.',
      tools: ['pandas', 'numpy', 'sklearn'],
      memory: true,
      streaming: true,
      timeout: 60000,
      retryAttempts: 2,
    }
  },
  {
    id: '3',
    name: 'ReportGenerator',
    description: 'An agent that generates comprehensive reports and visualizations.',
    framework: 'crewai' as const,
    skills: ['reporting', 'data-visualization', 'document-generation'],
    status: 'inactive' as const,
    version: '1.5.0',
    createdAt: new Date('2023-08-10'),
    updatedAt: new Date('2023-10-25'),
    lastExecutedAt: new Date('2023-11-28'),
    executionCount: 42,
    systemPrompt: 'You are a report generation specialist.',
    tags: ['reporting', 'analytics', 'general'],
    config: {
      model: 'gpt-3.5-turbo',
      temperature: 0.5,
      maxTokens: 3000,
      systemPrompt: 'You are a report generation specialist.',
      tools: ['matplotlib', 'plotly', 'pdf-generator'],
      memory: false,
      streaming: false,
      timeout: 45000,
      retryAttempts: 1,
    }
  },
  {
    id: '4',
    name: 'CustomerSupport',
    description: 'An intelligent customer support agent with natural language understanding.',
    framework: 'semantic-kernel' as const,
    skills: ['conversation', 'problem-solving', 'knowledge-base'],
    status: 'active' as const,
    version: '3.0.0',
    createdAt: new Date('2023-11-01'),
    updatedAt: new Date('2023-12-01'),
    lastExecutedAt: new Date('2023-12-08'),
    executionCount: 234,
    systemPrompt: 'You are a helpful customer support agent.',
    tags: ['support', 'customer', 'automation'],
    config: {
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 2500,
      systemPrompt: 'You are a helpful customer support agent.',
      tools: ['knowledge-base', 'ticket-system'],
      memory: true,
      streaming: true,
      timeout: 20000,
      retryAttempts: 3,
    }
  },
  {
    id: '5',
    name: 'ContentCreator',
    description: 'An agent specialized in creating marketing content and social media posts.',
    framework: 'langchain' as const,
    skills: ['content-generation', 'copywriting', 'social-media'],
    status: 'active' as const,
    version: '1.2.0',
    createdAt: new Date('2023-11-15'),
    updatedAt: new Date('2023-12-05'),
    lastExecutedAt: new Date('2023-12-08'),
    executionCount: 156,
    systemPrompt: 'You are a creative content specialist.',
    tags: ['content', 'marketing', 'generation'],
    config: {
      model: 'gpt-4',
      temperature: 0.8,
      maxTokens: 3000,
      systemPrompt: 'You are a creative content specialist.',
      tools: ['content-planner', 'seo-analyzer'],
      memory: true,
      streaming: true,
      timeout: 30000,
      retryAttempts: 2,
    }
  },
  {
    id: '6',
    name: 'SocialMediaManager',
    description: 'Manages social media campaigns and automates posting schedules.',
    framework: 'crewai' as const,
    skills: ['social-media', 'automation', 'scheduling'],
    status: 'active' as const,
    version: '2.0.0',
    createdAt: new Date('2023-12-01'),
    updatedAt: new Date('2023-12-07'),
    lastExecutedAt: new Date('2023-12-08'),
    executionCount: 78,
    systemPrompt: 'You are a social media management expert.',
    tags: ['social', 'marketing', 'automation'],
    config: {
      model: 'gpt-3.5-turbo',
      temperature: 0.6,
      maxTokens: 2000,
      systemPrompt: 'You are a social media management expert.',
      tools: ['social-api', 'scheduler', 'analytics'],
      memory: false,
      streaming: false,
      timeout: 25000,
      retryAttempts: 3,
    }
  }
];

export default function AgentsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFramework, setSelectedFramework] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  
  const { state: projectState } = useProject();
  
  // TODO: Replace with actual API call
  // const { data: agents, isLoading, error } = useAgents();
  const agents = mockAgents;
  const isLoading = false;
  const error = null;

  // Filter agents based on search, filters, and selected project
  const filteredAgents = useMemo(() => {
    return agents.filter(agent => {
      // Basic filters
      const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           agent.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesFramework = selectedFramework === 'all' || agent.framework === selectedFramework;
      const matchesStatus = selectedStatus === 'all' || agent.status === selectedStatus;
      
      // Project filtering: if a project is selected, only show agents that have tags matching the project tags
      const matchesProject = !projectState.selectedProject || 
                             projectState.selectedProject.tags.some(projectTag => 
                               agent.tags.includes(projectTag)
                             );
      
      return matchesSearch && matchesFramework && matchesStatus && matchesProject;
    });
  }, [agents, searchTerm, selectedFramework, selectedStatus, projectState.selectedProject]);

  const stats = {
    total: agents.length,
    active: agents.filter(a => a.status === 'active').length,
    inactive: agents.filter(a => a.status === 'inactive').length,
    totalExecutions: agents.reduce((sum, a) => sum + a.executionCount, 0),
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading agents...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Error loading agents: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Agent Registry
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <p className="text-gray-600 dark:text-gray-400">
              Manage and monitor your AI agents across different frameworks
            </p>
            {projectState.selectedProject && (
              <div className="flex items-center gap-2">
                <FunnelIcon className="w-4 h-4 text-blue-500" />
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50">
                  Filtered by: {projectState.selectedProject.name}
                </Badge>
              </div>
            )}
          </div>
        </div>
        <Button 
          onClick={() => setIsCreateDialogOpen(true)}
          className="flex items-center gap-2"
        >
          <PlusIcon className="w-4 h-4" />
          Create Agent
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl font-bold text-blue-600">
              {stats.total}
            </CardTitle>
            <CardDescription>Total Agents</CardDescription>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl font-bold text-green-600">
              {stats.active}
            </CardTitle>
            <CardDescription>Active Agents</CardDescription>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl font-bold text-orange-600">
              {stats.inactive}
            </CardTitle>
            <CardDescription>Inactive Agents</CardDescription>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl font-bold text-purple-600">
              {stats.totalExecutions.toLocaleString()}
            </CardTitle>
            <CardDescription>Total Executions</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search agents by name, description, or skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <AgentFilters
          selectedFramework={selectedFramework}
          selectedStatus={selectedStatus}
          onFrameworkChange={setSelectedFramework}
          onStatusChange={setSelectedStatus}
        />
      </div>

      {/* Agents Grid */}
      {filteredAgents.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <div className="text-gray-400 text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No agents found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {searchTerm || selectedFramework !== 'all' || selectedStatus !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first agent'}
            </p>
            {!searchTerm && selectedFramework === 'all' && selectedStatus === 'all' && (
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <PlusIcon className="w-4 h-4 mr-2" />
                Create Your First Agent
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}

      {/* Create Agent Dialog */}
      <CreateAgentDialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
      />
    </div>
  );
}
