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
import { useAgents, useAgentAnalytics, type Agent } from '@/hooks/useAgents';
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
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showAnalytics, setShowAnalytics] = useState(true);
  const [sortBy, setSortBy] = useState<'name' | 'created' | 'updated' | 'status'>('updated');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  const { state: projectState } = useProject();
  
  // Use real API data from hooks
  const {
    agents,
    loading,
    error,
    createAgent,
    deleteAgent,
    runAgent,
  } = useAgents();
  
  const analytics = useAgentAnalytics();

  // Handler functions
  const handleEditAgent = async (agent: Agent) => {
    // TODO: Open edit modal
    console.log('Edit agent:', agent);
  };

  const handleCloneAgent = async (agent: Agent) => {
    const clonedData = {
      name: `${agent.name} (Copy)`,
      description: agent.description,
      framework: agent.framework,
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

  // Filter and sort agents based on search, filters, and selected project
  const filteredAndSortedAgents = useMemo(() => {
    let filtered = agents.filter(agent => {
      // Basic filters
      const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           agent.capabilities.some((capability: string) => capability.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesFramework = selectedFramework === 'all' || agent.framework === selectedFramework;
      const matchesStatus = selectedStatus === 'all' || agent.status === selectedStatus;
      
      // Project filtering: if a project is selected, only show agents that have tags matching the project tags
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

    // Sort agents
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'created':
          aValue = new Date(a.created_at || 0).getTime();
          bValue = new Date(b.created_at || 0).getTime();
          break;
        case 'updated':
          aValue = new Date(a.updated_at || 0).getTime();
          bValue = new Date(b.updated_at || 0).getTime();
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          return 0;
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [agents, searchTerm, selectedFramework, selectedStatus, projectState.selectedProject, sortBy, sortOrder]);

  const stats = {
    total: analytics.totalAgents,
    active: analytics.activeAgents,
    inactive: analytics.inactiveAgents,
    totalExecutions: analytics.totalTasksCompleted,
    averageResponseTime: 245, // Mock data - replace with real analytics when available
    successRate: analytics.avgSuccessRate || 0,
  };

  // Loading state with enhanced skeleton
  if (loading) {
    return (
      <AuthGuard>
        <StandardPageLayout 
          title="Agent Registry" 
          description="Manage and monitor your AI agents across different frameworks"
          variant="wide"
        >
          <StandardSection>
            <StandardGrid cols={{ default: 1, sm: 2, lg: 4 }} gap="md">
              {[...Array(6)].map((_, i) => (
                <StandardCard key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                </StandardCard>
              ))}
            </StandardGrid>
          </StandardSection>
          
          <StandardSection>
            <div className="space-y-4">
              <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <StandardGrid cols={{ default: 1, md: 2, lg: 3 }} gap="md">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
                ))}
              </StandardGrid>
            </div>
          </StandardSection>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  if (error) {
    return (
      <AuthGuard>
        <StandardPageLayout title="Agent Registry" description="Error loading agents">
          <StandardSection>
            <StandardCard className="p-12 text-center bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
              <ExclamationTriangleIcon className="w-16 h-16 mx-auto text-red-500 mb-4" />
              <h3 className="text-heading-2 text-red-900 dark:text-red-100 mb-2">
                Failed to Load Agents
              </h3>
              <p className="text-body text-red-700 dark:text-red-300 mb-4">
                {error}
              </p>
              <Button onClick={() => window.location.reload()} variant="outline">
                Try Again
              </Button>
            </StandardCard>
          </StandardSection>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <StandardPageLayout
        title="Agent Registry"
        description="Manage and monitor your AI agents across different frameworks"
        variant="wide"
        actions={
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            {projectState.selectedProject && (
              <div className="flex items-center gap-2 animate-fade-in">
                <FunnelIcon className="w-4 h-4 text-blue-500" />
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 dark:border-blue-800 dark:text-blue-300 dark:bg-blue-900/20">
                  Filtered by: {projectState.selectedProject.name}
                </Badge>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowAnalytics(!showAnalytics)}
                className="hidden lg:flex items-center gap-2"
              >
                <ChartBarIcon className="w-4 h-4" />
                {showAnalytics ? 'Hide' : 'Show'} Analytics
              </Button>
              <Button 
                onClick={() => setIsCreateDialogOpen(true)}
                className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="w-4 h-4" />
                Create Agent
              </Button>
            </div>
          </div>
        }
      >

        {/* Enhanced Analytics Dashboard */}
        {showAnalytics && (
          <StandardSection className="animate-fade-in">
            <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                    <ChartBarIconSolid className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-heading-3 text-gray-900 dark:text-white">Agent Analytics</h3>
                    <p className="text-body-sm text-gray-600 dark:text-gray-400">Real-time performance metrics</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="status-dot status-online"></div>
                  <span className="text-body-sm text-gray-600 dark:text-gray-400">Live Data</span>
                </div>
              </div>
              
              <StandardGrid cols={{ default: 2, sm: 3, lg: 6 }} gap="md">
                <StandardCard className="card-hover-subtle bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
                      <CpuChipIconSolid className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {stats.total}
                      </div>
                      <p className="text-body-sm text-gray-600 dark:text-gray-400">Total Agents</p>
                    </div>
                  </div>
                </StandardCard>
                
                <StandardCard className="card-hover-subtle bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                      <CheckCircleIconSolid className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {stats.active}
                      </div>
                      <p className="text-body-sm text-gray-600 dark:text-gray-400">Active Agents</p>
                    </div>
                  </div>
                </StandardCard>
                
                <StandardCard className="card-hover-subtle bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 rounded-xl flex items-center justify-center">
                      <PauseIcon className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {stats.inactive}
                      </div>
                      <p className="text-body-sm text-gray-600 dark:text-gray-400">Inactive Agents</p>
                    </div>
                  </div>
                </StandardCard>
                
                <StandardCard className="card-hover-subtle bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                      <PlayIcon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {stats.totalExecutions.toLocaleString()}
                      </div>
                      <p className="text-body-sm text-gray-600 dark:text-gray-400">Total Executions</p>
                    </div>
                  </div>
                </StandardCard>
                
                <StandardCard className="card-hover-subtle bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center">
                      <ClockIconSolid className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {stats.averageResponseTime.toFixed(0)}ms
                      </div>
                      <p className="text-body-sm text-gray-600 dark:text-gray-400">Avg Response</p>
                    </div>
                  </div>
                </StandardCard>
                
                <StandardCard className="card-hover-subtle bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border-0 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center">
                      <CheckCircleIcon className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {(stats.successRate * 100).toFixed(1)}%
                      </div>
                      <p className="text-body-sm text-gray-600 dark:text-gray-400">Success Rate</p>
                    </div>
                  </div>
                </StandardCard>
              </StandardGrid>
            </div>
          </StandardSection>
        )}

        {/* Enhanced Search, Filters, and Controls */}
        <StandardSection>
          <StandardCard className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-0 shadow-lg">
            <div className="space-y-4">
              {/* Search Bar */}
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  placeholder="Search agents by name, description, capabilities, or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-12 pr-12 h-12 text-body bg-gray-50/50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
                />
                {searchTerm && (
                  <button
                    onClick={() => setSearchTerm('')}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              {/* Filters and Controls */}
              <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                <div className="flex flex-wrap items-center gap-3">
                  <AgentFilters
                    selectedFramework={selectedFramework}
                    selectedStatus={selectedStatus}
                    onFrameworkChange={setSelectedFramework}
                    onStatusChange={setSelectedStatus}
                  />
                  
                  {/* Sort Controls */}
                  <div className="flex items-center gap-2">
                    <label className="text-body-sm text-gray-600 dark:text-gray-400">Sort by:</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                      className="px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    >
                      <option value="updated">Last Updated</option>
                      <option value="created">Created Date</option>
                      <option value="name">Name</option>
                      <option value="status">Status</option>
                    </select>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                      className="p-2"
                    >
                      <ArrowPathIcon className={cn(
                        "w-4 h-4 transition-transform",
                        sortOrder === 'desc' && "rotate-180"
                      )} />
                    </Button>
                  </div>
                </div>
                
                {/* View Mode Toggle */}
                <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                  <Button
                    variant={viewMode === 'grid' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                    className={cn(
                      "px-3 py-2",
                      viewMode === 'grid' && "bg-white dark:bg-gray-700 shadow-sm"
                    )}
                  >
                    <Squares2X2Icon className="w-4 h-4" />
                    <span className="hidden sm:inline ml-2">Grid</span>
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                    className={cn(
                      "px-3 py-2",
                      viewMode === 'list' && "bg-white dark:bg-gray-700 shadow-sm"
                    )}
                  >
                    <ListBulletIcon className="w-4 h-4" />
                    <span className="hidden sm:inline ml-2">List</span>
                  </Button>
                </div>
              </div>
              
              {/* Results Summary */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-body-sm text-gray-600 dark:text-gray-400">
                  Showing {filteredAndSortedAgents.length} of {agents.length} agents
                  {searchTerm && (
                    <span> for "<span className="font-medium text-gray-900 dark:text-white">{searchTerm}</span>"
                    </span>
                  )}
                </p>
                {filteredAndSortedAgents.length > 0 && (
                  <div className="flex items-center gap-2 text-body-sm text-gray-500 dark:text-gray-400">
                    <div className="status-dot status-online"></div>
                    <span>{filteredAndSortedAgents.filter(a => a.status === 'active').length} active</span>
                  </div>
                )}
              </div>
            </div>
          </StandardCard>
        </StandardSection>

        {/* Enhanced Agents Display */}
        <StandardSection>
          {filteredAndSortedAgents.length === 0 ? (
            <StandardCard className="p-16 text-center bg-gradient-to-br from-gray-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 border-0 shadow-lg">
              <div className="animate-fade-in">
                <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <CpuChipIcon className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-heading-2 text-gray-900 dark:text-white mb-4">
                  {searchTerm || selectedFramework !== 'all' || selectedStatus !== 'all'
                    ? 'No agents match your criteria'
                    : 'No agents found'}
                </h3>
                <p className="text-body text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
                  {searchTerm || selectedFramework !== 'all' || selectedStatus !== 'all'
                    ? 'Try adjusting your search terms or filters to find the agents you\'re looking for.'
                    : 'Get started by creating your first AI agent to begin automating tasks and workflows.'}
                </p>
                
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  {(searchTerm || selectedFramework !== 'all' || selectedStatus !== 'all') && (
                    <Button 
                      variant="outline" 
                      onClick={() => {
                        setSearchTerm('');
                        setSelectedFramework('all');
                        setSelectedStatus('all');
                      }}
                      className="flex items-center gap-2"
                    >
                      <ArrowPathIcon className="w-4 h-4" />
                      Clear Filters
                    </Button>
                  )}
                  <Button 
                    onClick={() => setIsCreateDialogOpen(true)}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white flex items-center gap-2 shadow-lg"
                  >
                    <PlusIcon className="w-4 h-4" />
                    {agents.length === 0 ? 'Create Your First Agent' : 'Create New Agent'}
                  </Button>
                </div>
              </div>
            </StandardCard>
          ) : (
            <div className="animate-fade-in">
              {viewMode === 'grid' ? (
                <StandardGrid cols={{ default: 1, md: 2, lg: 3, xl: 4 }} gap="lg">
                  {filteredAndSortedAgents.map((agent, index) => (
                    <div key={agent.id} className="animate-fade-in-up" style={{ animationDelay: `${index * 50}ms` }}>
                      <AgentCard 
                        agent={agent}
                        onEdit={handleEditAgent}
                        onClone={handleCloneAgent}
                        onDelete={handleDeleteAgent}
                        onExecute={handleExecuteAgent}
                      />
                    </div>
                  ))}
                </StandardGrid>
              ) : (
                <div className="space-y-4">
                  {filteredAndSortedAgents.map((agent, index) => (
                    <div key={agent.id} className="animate-fade-in-up" style={{ animationDelay: `${index * 30}ms` }}>
                      <AgentCard 
                        agent={agent}
                        onEdit={handleEditAgent}
                        onClone={handleCloneAgent}
                        onDelete={handleDeleteAgent}
                        onExecute={handleExecuteAgent}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </StandardSection>

        {/* Create Agent Dialog */}
        <CreateAgentDialog
          open={isCreateDialogOpen}
          onClose={() => setIsCreateDialogOpen(false)}
        />
        
        {/* Quick Actions Floating Button (Mobile) */}
        <div className="fixed bottom-6 right-6 lg:hidden z-50">
          <Button 
            onClick={() => setIsCreateDialogOpen(true)}
            className="w-14 h-14 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-2xl hover:scale-110 transition-all duration-200"
          >
            <PlusIcon className="w-6 h-6" />
          </Button>
        </div>
      </StandardPageLayout>
    </AuthGuard>
  );
}