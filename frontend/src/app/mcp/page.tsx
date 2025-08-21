'use client';

import { useState, useEffect } from 'react';
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
  CloudIcon,
  PlayIcon,
  PencilIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  CodeBracketIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';
import { useMCP } from '@/hooks/useMCP';
import MCPServerForm from './components/MCPServerForm';
import MCPEndpointForm from './components/MCPEndpointForm';
import MCPToolTester from './components/MCPToolTester';

export default function MCPManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState<'servers' | 'endpoints' | 'tools' | 'tester'>('servers');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [selectedServer, setSelectedServer] = useState<string>('');

  const {
    servers,
    endpoints,
    tools,
    executionLogs,
    loading,
    error,
    fetchServers,
    fetchEndpoints,
    fetchTools,
    fetchExecutionLogs,
    createServer,
    updateServer,
    deleteServer,
    createEndpoint,
    updateEndpoint,
    deleteEndpoint,
    discoverTools,
    testTool,
    executeEndpoint
  } = useMCP();

  useEffect(() => {
    fetchServers();
    fetchEndpoints();
    if (selectedServer) {
      fetchTools(selectedServer);
    }
    fetchExecutionLogs();
  }, [selectedServer]);

  const handleSaveServer = async (serverData: any) => {
    try {
      if (serverData.id) {
        await updateServer(serverData.id, serverData);
      } else {
        await createServer(serverData);
      }
      setShowCreateForm(false);
      setEditingItem(null);
      fetchServers();
    } catch (err) {
      console.error('Error saving server:', err);
    }
  };

  const handleSaveEndpoint = async (endpointData: any) => {
    try {
      if (endpointData.id) {
        await updateEndpoint(endpointData.id, endpointData);
      } else {
        await createEndpoint(endpointData);
      }
      setShowCreateForm(false);
      setEditingItem(null);
      fetchEndpoints();
    } catch (err) {
      console.error('Error saving endpoint:', err);
    }
  };

  const handleDeleteItem = async (item: any) => {
    if (selectedTab === 'servers') {
      await deleteServer(item.id);
      fetchServers();
    } else if (selectedTab === 'endpoints') {
      await deleteEndpoint(item.id);
      fetchEndpoints();
    }
  };

  const handleDiscoverTools = async (serverId: string) => {
    try {
      await discoverTools(serverId);
      if (selectedServer === serverId) {
        fetchTools(serverId);
      }
    } catch (err) {
      console.error('Error discovering tools:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'inactive':
      case 'unknown':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
      case 'error':
      case 'unhealthy':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'error':
      case 'unhealthy':
        return <XCircleIcon className="h-4 w-4" />;
      case 'inactive':
      case 'unknown':
        return <ClockIcon className="h-4 w-4" />;
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  const filteredData = () => {
    const searchLower = searchTerm.toLowerCase();
    
    switch (selectedTab) {
      case 'servers':
        return servers.filter(server => 
          server.display_name.toLowerCase().includes(searchLower) ||
          server.description?.toLowerCase().includes(searchLower) ||
          server.name.toLowerCase().includes(searchLower)
        );
      case 'endpoints':
        return endpoints.filter(endpoint => 
          endpoint.display_name.toLowerCase().includes(searchLower) ||
          endpoint.description?.toLowerCase().includes(searchLower) ||
          endpoint.endpoint_name.toLowerCase().includes(searchLower)
        );
      case 'tools':
        return tools.filter(tool => 
          tool.display_name?.toLowerCase().includes(searchLower) ||
          tool.description?.toLowerCase().includes(searchLower) ||
          tool.tool_name.toLowerCase().includes(searchLower)
        );
      default:
        return [];
    }
  };

  if (loading) {
    return (
      <AuthGuard>
        <StandardPageLayout title="MCP Management" description="Loading MCP data...">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-body text-gray-600 dark:text-gray-400">Loading MCP data...</p>
            </div>
          </div>
        </StandardPageLayout>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <StandardPageLayout
        title="MCP Management"
        description="Manage Model Context Protocol servers, endpoints, and tools"
        actions={
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
            <div className="flex space-x-3">
              <Button 
                variant="outline" 
                onClick={() => {
                  fetchServers();
                  fetchEndpoints();
                  if (selectedServer) fetchTools(selectedServer);
                  fetchExecutionLogs();
                }}
                className="flex items-center space-x-2"
              >
                <ArrowPathIcon className="h-4 w-4" />
                <span>Refresh</span>
              </Button>
              {selectedTab !== 'tester' && (
                <Button 
                  onClick={() => {
                    setEditingItem(null);
                    setShowCreateForm(true);
                  }}
                  className="flex items-center space-x-2"
                >
                  <PlusIcon className="h-4 w-4" />
                  <span>Create {selectedTab === 'servers' ? 'Server' : 'Endpoint'}</span>
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
                onClick={() => setSelectedTab('servers')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedTab === 'servers'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                MCP Servers ({servers.length})
              </button>
              <button
                onClick={() => setSelectedTab('endpoints')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedTab === 'endpoints'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Gateway Endpoints ({endpoints.length})
              </button>
              <button
                onClick={() => setSelectedTab('tools')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedTab === 'tools'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Discovered Tools ({tools.length})
              </button>
              <button
                onClick={() => setSelectedTab('tester')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedTab === 'tester'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Tool Tester
              </button>
            </div>

            <div className="flex space-x-3">
              {selectedTab !== 'tester' && (
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder={`Search ${selectedTab}...`}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              )}
              
              {selectedTab === 'tools' && (
                <select
                  value={selectedServer}
                  onChange={(e) => setSelectedServer(e.target.value)}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="">All Servers</option>
                  {servers.map((server) => (
                    <option key={server.id} value={server.id}>
                      {server.display_name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>
        </StandardSection>

        {/* Content */}
        <StandardSection>
          {selectedTab === 'tester' ? (
            <MCPToolTester 
              servers={servers}
              endpoints={endpoints}
              tools={tools}
              onTestTool={testTool}
              onExecuteEndpoint={executeEndpoint}
            />
          ) : (
            <div className="space-y-4">
              {/* MCP Servers */}
              {selectedTab === 'servers' && filteredData().map((server: any) => (
                <div
                  key={server.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="flex items-center space-x-2">
                          <CloudIcon className="h-5 w-5 text-blue-500" />
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {server.display_name}
                          </h3>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(server.status)}
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(server.status)}`}>
                            {server.status}
                          </span>
                        </div>
                        
                        {server.health_status && (
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(server.health_status)}`}>
                            {server.health_status}
                          </span>
                        )}

                        <Badge variant="outline" className="text-xs">
                          {server.transport_type}
                        </Badge>
                      </div>
                      
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        {server.description}
                      </p>
                      
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">URL:</span>
                            <span className="text-gray-900 dark:text-white font-mono text-xs">
                              {server.server_url}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Version:</span>
                            <span className="text-gray-900 dark:text-white">{server.version}</span>
                          </div>
                        </div>
                      </div>

                      {server.tags && server.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {server.tags.map((tag: string, index: number) => (
                            <span 
                              key={index}
                              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-md"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-6">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDiscoverTools(server.id)}
                        title="Discover tools"
                      >
                        <BeakerIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditingItem(server);
                          setShowCreateForm(true);
                        }}
                      >
                        <PencilIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteItem(server)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XCircleIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}

              {/* MCP Endpoints */}
              {selectedTab === 'endpoints' && filteredData().map((endpoint: any) => (
                <div
                  key={endpoint.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="flex items-center space-x-2">
                          <GlobeAltIcon className="h-5 w-5 text-green-500" />
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {endpoint.display_name}
                          </h3>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(endpoint.status)}
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(endpoint.status)}`}>
                            {endpoint.status}
                          </span>
                        </div>

                        {endpoint.is_public && (
                          <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700">
                            Public
                          </Badge>
                        )}

                        {endpoint.authentication_required && (
                          <Badge variant="outline" className="text-xs bg-orange-50 text-orange-700">
                            Auth Required
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        {endpoint.description}
                      </p>
                      
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
                        <div className="grid grid-cols-1 gap-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Path:</span>
                            <span className="text-gray-900 dark:text-white font-mono text-xs">
                              {endpoint.endpoint_path}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">URL:</span>
                            <span className="text-gray-900 dark:text-white font-mono text-xs">
                              {endpoint.endpoint_url}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-6">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => executeEndpoint(endpoint.endpoint_name, {})}
                      >
                        <PlayIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditingItem(endpoint);
                          setShowCreateForm(true);
                        }}
                      >
                        <PencilIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteItem(endpoint)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <XCircleIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}

              {/* MCP Tools */}
              {selectedTab === 'tools' && filteredData().map((tool: any) => (
                <div
                  key={tool.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="flex items-center space-x-2">
                          <CodeBracketIcon className="h-5 w-5 text-purple-500" />
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {tool.display_name || tool.tool_name}
                          </h3>
                        </div>
                        
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          tool.is_available 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                        }`}>
                          {tool.is_available ? 'Available' : 'Unavailable'}
                        </span>

                        <Badge variant="outline" className="text-xs">
                          v{tool.version}
                        </Badge>
                      </div>
                      
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        {tool.description}
                      </p>
                      
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Usage Count:</span>
                            <span className="text-gray-900 dark:text-white">{tool.usage_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Success Rate:</span>
                            <span className="text-gray-900 dark:text-white">{tool.success_rate.toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Avg Time:</span>
                            <span className="text-gray-900 dark:text-white">{tool.avg_execution_time}ms</span>
                          </div>
                        </div>
                      </div>

                      {tool.capabilities && tool.capabilities.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {tool.capabilities.map((capability: string, index: number) => (
                            <span 
                              key={index}
                              className="px-2 py-1 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-md"
                            >
                              {capability}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-6">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => testTool(tool.id, {})}
                      >
                        <PlayIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          // View tool schema
                        }}
                      >
                        <EyeIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              {filteredData().length === 0 && (
                <div className="text-center py-12">
                  <CloudIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No {selectedTab} found
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {searchTerm 
                      ? 'Try adjusting your search term.'
                      : `Get started by creating your first ${selectedTab.slice(0, -1)}.`
                    }
                  </p>
                </div>
              )}
            </div>
          )}
        </StandardSection>

        {/* Create/Edit Forms */}
        {showCreateForm && selectedTab === 'servers' && (
          <MCPServerForm
            server={editingItem}
            onSave={handleSaveServer}
            onCancel={() => {
              setShowCreateForm(false);
              setEditingItem(null);
            }}
          />
        )}

        {showCreateForm && selectedTab === 'endpoints' && (
          <MCPEndpointForm
            endpoint={editingItem}
            servers={servers}
            onSave={handleSaveEndpoint}
            onCancel={() => {
              setShowCreateForm(false);
              setEditingItem(null);
            }}
          />
        )}
      </StandardPageLayout>
    </AuthGuard>
  );
}
