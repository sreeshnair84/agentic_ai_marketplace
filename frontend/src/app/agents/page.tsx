'use client';

import { useState, useMemo, useEffect } from 'react';
import { useProject } from '@/store/projectContext';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { StandardPageLayout, StandardSection, StandardGrid, StandardCard } from '@/components/layout/StandardPageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AgentCard } from './components/AgentCard';
import { AgentFilters } from './components/AgentFilters';
import { CreateAgentDialog } from './components/CreateAgentDialog';
import { useAgents, useAgentAnalytics, type Agent, type CreateAgentData } from '@/hooks/useAgents';
import { cn } from '@/lib/utils';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  FunnelIcon,
  ArrowPathIcon,
  ChartBarIcon,
  CpuChipIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlayIcon,
  PauseIcon,
  Cog6ToothIcon,
  ViewColumnsIcon,
  ListBulletIcon,
  Squares2X2Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { 
  ChartBarIcon as ChartBarIconSolid,
  CpuChipIcon as CpuChipIconSolid,
  ClockIcon as ClockIconSolid,
  CheckCircleIcon as CheckCircleIconSolid
} from '@heroicons/react/24/solid';

export default function AgentsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFramework, setSelectedFramework] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  
  const { state: projectState } = useProject();
  
  // Use real API data from hooks
  const {
    agents,
    loading,
    error,
    createAgent,
    updateAgent,
    deleteAgent,
    runAgent,
  } = useAgents();
  
  const analytics = useAgentAnalytics();

  // Handler functions
  const handleEditAgent = async (agent: Agent) => {
    setEditingAgent(agent);
    setIsCreateDialogOpen(true);
  };

  const handleCloneAgent = async (agent: Agent) => {
    // Map old framework names to new ones if needed
    const mapFramework = (framework: string): 'langgraph' | 'crewai' | 'autogen' | 'semantic_kernel' | 'custom' => {
      switch (framework) {
        case 'langchain':
          return 'langgraph';
        case 'crewai':
        case 'autogen':
        case 'semantic_kernel':
        case 'custom':
          return framework;
        default:
          return 'custom'; // fallback for unknown frameworks
      }
    };

    const clonedData: CreateAgentData = {
      name: `${agent.name} (Copy)`,
      description: agent.description,
      framework: mapFramework(agent.framework),
      capabilities: agent.capabilities,
      tags: agent.tags,
    };
    
    await createAgent(clonedData);
  };

  const handleDeleteAgent = async (agent: Agent) => {
    if (confirm(`Are you sure you want to delete ${agent.name}?`)) {
      await deleteAgent(agent.id);
    }
  };

  const handleExecuteAgent = async (agent: Agent) => {
    console.log('Execute agent:', agent);
    await runAgent(agent.id, {});
  };

  // Filter agents based on search, filters, and selected project
  const filteredAgents = useMemo(() => {
    return agents.filter(agent => {
      // Basic filters
      const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           agent.capabilities.some((capability: string) => capability.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesFramework = selectedFramework === 'all' || agent.framework === selectedFramework;
      const matchesStatus = selectedStatus === 'all' || agent.status === selectedStatus;
      
      // Project filtering: if a project is selected, only show agents that have tags matching the project tags
      console.log('Project State:', projectState.selectedProject);
      console.log('Agent Tags:', agent.tags);
      let matchesProject = true;
      if (
        projectState.selectedProject !== null &&
        projectState.selectedProject.name !== 'Default Project'
      ) {
        matchesProject =
          projectState.selectedProject.tags.some((projectTag) =>
            agent.tags.includes(projectTag)
          );
      }

      return matchesSearch && matchesFramework && matchesStatus && matchesProject;
    });
  }, [agents, searchTerm, selectedFramework, selectedStatus, projectState.selectedProject]);

  const stats = {
    total: analytics.totalAgents,
    active: analytics.activeAgents,
    inactive: analytics.inactiveAgents,
    totalExecutions: analytics.totalTasksCompleted, // Use totalTasksCompleted instead
  };

  if (loading) {
    return (
      <AuthGuard>
        <StandardPageLayout title="Agent Registry" description="Loading agents...">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <ArrowPathIcon className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
              <div className="text-lg">Loading agents...</div>
            </div>
          </div>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  if (error) {
    return (
      <AuthGuard>
        <StandardPageLayout title="Agent Registry" description="Error loading agents">
          <div className="flex items-center justify-center h-64">
            <div className="text-red-500">Error loading agents: {error}</div>
          </div>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <StandardPageLayout
        title="Agent Registry"
        description="Manage and monitor your AI agents across different frameworks"
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
            <Button 
              onClick={() => setIsCreateDialogOpen(true)}
              className="flex items-center gap-2 w-full sm:w-auto"
            >
              <PlusIcon className="w-4 h-4" />
              Create Agent
            </Button>
          </div>
        }
      >

        {/* Stats Cards */}
        <StandardSection>
          <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-blue-600">
                  {stats.total}
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Total Agents</p>
              </div>
            </StandardCard>
            
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-green-600">
                  {stats.active}
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Active Agents</p>
              </div>
            </StandardCard>
            
            <StandardCard>
              <div className="pb-2">
                <div className="text-3xl font-bold text-orange-600">
                  {stats.inactive}
                </div>
                <p className="text-body-sm text-gray-600 dark:text-gray-400">Inactive Agents</p>
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
          </StandardGrid>
        </StandardSection>

        {/* Search and Filters */}
        <StandardSection>
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
        </StandardSection>

        {/* Agents Grid */}
        <StandardSection>
          {filteredAgents.length === 0 ? (
            <StandardCard className="p-12">
              <div className="text-center">
                <div className="text-gray-400 text-6xl mb-4">🤖</div>
                <h3 className="text-heading-2 text-gray-900 dark:text-white mb-2">
                  No agents found
                </h3>
                <p className="text-body text-gray-600 dark:text-gray-400 mb-4">
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
            </StandardCard>
          ) : (
            <StandardGrid cols={{ default: 1, md: 2, lg: 3 }} gap="md">
              
              {filteredAgents.map((agent) => (
                <AgentCard 
                  key={agent.id} 
                  agent={agent}
                  onEdit={handleEditAgent}
                  onClone={handleCloneAgent}
                  onDelete={handleDeleteAgent}
                  onExecute={handleExecuteAgent}
                />
              ))}
            </StandardGrid>
          )}
        </StandardSection>

        {/* Create/Edit Agent Dialog */}
        <CreateAgentDialog
          open={isCreateDialogOpen}
          onClose={() => {
            setIsCreateDialogOpen(false);
            setEditingAgent(null);
          }}
          editingAgent={editingAgent}
          onSave={async (agentData) => {
            // Transform agentData to match CreateAgentData interface
            const createAgentData: CreateAgentData = {
              name: agentData.name,
              display_name: agentData.display_name,
              description: agentData.description,
              framework: agentData.framework,
              capabilities: agentData.capabilities || [],
              tags: agentData.tags,
              project_tags: agentData.project_tags,
              llm_model_id: agentData.llm_model_id,
              systemPrompt: agentData.systemPrompt,
              system_prompt: agentData.system_prompt,
              temperature: agentData.temperature,
              maxTokens: agentData.maxTokens,
              max_tokens: agentData.max_tokens,
              category: agentData.category,
              agent_type: agentData.agent_type,
              version: agentData.version,
              a2a_enabled: agentData.a2a_enabled,
              a2a_address: agentData.a2a_address,
              // Deployment fields
              url: agentData.url,
              dns_name: agentData.dns_name,
              health_url: agentData.health_url,
              environment: agentData.environment,
              author: agentData.author,
              organization: agentData.organization,
              // Signature fields (temporarily stored in model_config_data)
              // input_signature: agentData.input_signature,
              // output_signature: agentData.output_signature,
              default_input_modes: agentData.default_input_modes,
              default_output_modes: agentData.default_output_modes,
              // Model configuration (including signatures for now)
              model_config_data: {
                ...agentData.model_config_data,
                input_signature: agentData.input_signature,
                output_signature: agentData.output_signature,
              },
            };

            if (editingAgent) {
              await updateAgent(editingAgent.id, createAgentData);
            } else {
              await createAgent(createAgentData);
            }
            setEditingAgent(null);
          }}
        />
      </StandardPageLayout>
    </AuthGuard>
  );
}
