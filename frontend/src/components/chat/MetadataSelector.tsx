'use client';

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Workflow, 
  Bot, 
  Wrench, 
  ChevronDown, 
  ChevronRight,
  Globe,
  Zap,
  Activity,
  Clock,
  CheckCircle2,
  AlertCircle,
  Filter,
  X
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';

// Types for metadata
export interface WorkflowMetadata {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  version: string;
  status: string;
  dns_name?: string;
  health_url?: string;
  url?: string;
  capabilities: any;
  tags: string[];
  project_tags: string[];
  execution_count: number;
  success_rate?: number;
  is_public: boolean;
  timeout_seconds: number;
  input_modes: string[];
  output_modes: string[];
  type: 'workflow';
}

export interface AgentMetadata {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  status: string;
  dns_name?: string;
  health_url?: string;
  url?: string;
  a2a_address?: string;
  ai_provider: string;
  model_name: string;
  capabilities: any;
  tags: string[];
  project_tags: string[];
  execution_count: number;
  success_rate?: number;
  input_modes: string[];
  output_modes: string[];
  type: 'agent';
}

export interface ToolMetadata {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  tool_type: string;
  version: string;
  status: string;
  dns_name?: string;
  health_url?: string;
  capabilities: any;
  tags: string[];
  execution_count: number;
  success_rate?: number;
  input_modes: string[];
  output_modes: string[];
  type: 'tool';
}

export interface LLMModelMetadata {
  id: string;
  name: string;
  display_name: string;
  description: string;
  provider: string;
  status: string;
  capabilities: any;
  model_config: any;
  pricing_info?: any;
  is_default: boolean;
  type: 'llm';
}

export interface MetadataOptions {
  workflows: WorkflowMetadata[];
  agents: AgentMetadata[];
  tools: ToolMetadata[];
  llm_models: LLMModelMetadata[];
  summary: {
    total_workflows: number;
    total_agents: number;
    total_tools: number;
    total_llm_models: number;
    categories: {
      workflows: string[];
      agents: string[];
      tools: string[];
      llm_models: string[];
    };
    default_llm_model: LLMModelMetadata | null;
  };
}

export interface SelectedContext {
  type: 'workflow' | 'agent' | 'tools' | 'llm' | null;
  workflow?: WorkflowMetadata;
  agent?: AgentMetadata;
  tools?: ToolMetadata[];
  llm_model?: LLMModelMetadata;
}

interface MetadataSelectorProps {
  onSelectionChange: (context: SelectedContext) => void;
  selectedContext: SelectedContext;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

interface MetadataItemProps {
  item: WorkflowMetadata | AgentMetadata | ToolMetadata | LLMModelMetadata;
  isSelected: boolean;
  onSelect: () => void;
  isMultiSelect?: boolean;
}

const MetadataItem: React.FC<MetadataItemProps> = ({ 
  item, 
  isSelected, 
  onSelect, 
  isMultiSelect = false 
}) => {
  const getIcon = () => {
    switch (item.type) {
      case 'workflow': return <Workflow className="h-4 w-4" />;
      case 'agent': return <Bot className="h-4 w-4" />;
      case 'tool': return <Wrench className="h-4 w-4" />;
      case 'llm': return <Zap className="h-4 w-4" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (item.status) {
      case 'active':
      case 'published': return 'text-green-500';
      case 'inactive': return 'text-gray-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div 
      className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-sm ${
        isSelected 
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          {isMultiSelect && (
            <Checkbox 
              checked={isSelected} 
              onChange={() => {}} 
              className="mt-1"
            />
          )}
          <div className={getStatusColor()}>
            {getIcon()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h4 className="font-medium text-sm truncate">{item.display_name}</h4>
              <Badge variant="outline" className="text-xs">
                {item.type}
              </Badge>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
              {item.description}
            </p>
            
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
              {(item.type !== 'llm' && (item as any).category) && (
                <span className="flex items-center space-x-1">
                  <Filter className="h-3 w-3" />
                  <span>{(item as any).category}</span>
                </span>
              )}
              
              {item.type === 'llm' && (item as LLMModelMetadata).provider && (
                <span className="flex items-center space-x-1">
                  <Filter className="h-3 w-3" />
                  <span>{(item as LLMModelMetadata).provider}</span>
                </span>
              )}
              
              {item.type !== 'llm' && (item as any).execution_count > 0 && (
                <span className="flex items-center space-x-1">
                  <Activity className="h-3 w-3" />
                  <span>{(item as any).execution_count}</span>
                </span>
              )}
              
              {item.type !== 'llm' && (item as any).success_rate !== undefined && (
                <span className="flex items-center space-x-1">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>{((item as any).success_rate * 100).toFixed(0)}%</span>
                </span>
              )}
              
              {item.type === 'llm' && (item as LLMModelMetadata).is_default && (
                <span className="flex items-center space-x-1">
                  <CheckCircle2 className="h-3 w-3" />
                  <span>Default</span>
                </span>
              )}
            </div>
            
            {item.type !== 'llm' && Array.isArray((item as any).tags) && (item as any).tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {(item as any).tags.slice(0, 3).map((tag: string, index: number) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {(item as any).tags.length > 3 && (
                  <span className="text-xs text-gray-500">+{(item as any).tags.length - 3}</span>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex flex-col items-end space-y-1">
          <div className={`h-2 w-2 rounded-full ${
            item.status === 'active' || item.status === 'published' 
              ? 'bg-green-500' 
              : 'bg-gray-400'
          }`} />
          {(item.type === 'workflow' || item.type === 'tool') && (item as any).version && (
            <span className="text-xs text-gray-400">
              v{(item as any).version}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export const MetadataSelector: React.FC<MetadataSelectorProps> = ({
  onSelectionChange,
  selectedContext,
  isCollapsed = false,
  onToggleCollapse
}) => {
  const [metadata, setMetadata] = useState<MetadataOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});

  // Load metadata options
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const response = await fetch('/api/v1/metadata/chat-options');
        if (!response.ok) throw new Error('Failed to load metadata');
        const data = await response.json();
        setMetadata(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load metadata');
      } finally {
        setLoading(false);
      }
    };

    loadMetadata();
  }, []);

  // Filter items based on search and category
  const filterItems = (items: (WorkflowMetadata | AgentMetadata | ToolMetadata | LLMModelMetadata)[]) => {
    return items.filter(item => {
      const matchesSearch = !searchTerm || 
        item.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.type !== 'llm' && (item as any).tags && (item as any).tags.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase())));
      
      const matchesCategory = selectedCategory === 'all' || 
        (item.type === 'llm' ? (item as LLMModelMetadata).provider === selectedCategory : (item as any).category === selectedCategory);
      
      return matchesSearch && matchesCategory;
    });
  };

  // Handle workflow selection
  const handleWorkflowSelect = (workflow: WorkflowMetadata) => {
    onSelectionChange({
      type: 'workflow',
      workflow,
      agent: undefined,
      tools: undefined,
      llm_model: undefined
    });
  };

  // Handle agent selection  
  const handleAgentSelect = (agent: AgentMetadata) => {
    onSelectionChange({
      type: 'agent',
      workflow: undefined,
      agent,
      tools: undefined,
      llm_model: undefined
    });
  };

  // Handle tool selection (multi-select)
  const handleToolSelect = (tool: ToolMetadata) => {
    const currentTools = selectedContext.tools || [];
    const isSelected = currentTools.some(t => t.id === tool.id);
    
    let newTools: ToolMetadata[];
    if (isSelected) {
      newTools = currentTools.filter(t => t.id !== tool.id);
    } else {
      newTools = [...currentTools, tool];
    }
    
    onSelectionChange({
      type: newTools.length > 0 ? 'tools' : null,
      workflow: undefined,
      agent: undefined,
      tools: newTools.length > 0 ? newTools : undefined,
      llm_model: undefined
    });
  };

  // Handle LLM model selection
  const handleLLMSelect = (llm_model: LLMModelMetadata) => {
    onSelectionChange({
      type: 'llm',
      workflow: undefined,
      agent: undefined,
      tools: undefined,
      llm_model
    });
  };

  // Clear selection
  const handleClearSelection = () => {
    onSelectionChange({
      type: null,
      workflow: undefined,
      agent: undefined,
      tools: undefined,
      llm_model: undefined
    });
  };

  // Toggle category expansion
  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-sm">Loading Options...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-sm text-red-600">Error Loading Options</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!metadata) return null;

  // Get all categories
  const allCategories = Array.from(new Set([
    ...(metadata.summary?.categories?.workflows || []),
    ...(metadata.summary?.categories?.agents || []),
    ...(metadata.summary?.categories?.tools || []),
    ...(metadata.summary?.categories?.llm_models || [])
  ]));

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center space-x-2">
            <span>Chat Context</span>
            {selectedContext.type && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearSelection}
                className="p-1"
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </CardTitle>
          {onToggleCollapse && (
            <Button variant="ghost" size="sm" onClick={onToggleCollapse}>
              {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          )}
        </div>
        
        {selectedContext.type && (
          <div className="text-xs text-gray-600 dark:text-gray-300">
            {selectedContext.type === 'workflow' && selectedContext.workflow && (
              <span>Workflow: {selectedContext.workflow.display_name}</span>
            )}
            {selectedContext.type === 'agent' && selectedContext.agent && (
              <span>Agent: {selectedContext.agent.display_name}</span>
            )}
            {selectedContext.type === 'tools' && selectedContext.tools && (
              <span>Tools: {selectedContext.tools.length} selected</span>
            )}
            {selectedContext.type === 'llm' && selectedContext.llm_model && (
              <span>LLM: {selectedContext.llm_model.display_name}</span>
            )}
          </div>
        )}
      </CardHeader>

      {!isCollapsed && (
        <CardContent className="pt-0">
          {/* Search and Filter */}
          <div className="space-y-3 mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search workflows, agents, tools..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger>
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {allCategories.map(category => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Selection Tabs */}
          <Tabs defaultValue="workflows" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="workflows" className="text-xs">
                <Workflow className="h-3 w-3 mr-1" />
                Workflows ({metadata.summary?.total_workflows || 0})
              </TabsTrigger>
              <TabsTrigger value="agents" className="text-xs">
                <Bot className="h-3 w-3 mr-1" />
                Agents ({metadata.summary?.total_agents || 0})
              </TabsTrigger>
              <TabsTrigger value="tools" className="text-xs">
                <Wrench className="h-3 w-3 mr-1" />
                Tools ({metadata.summary?.total_tools || 0})
              </TabsTrigger>
              <TabsTrigger value="llm" className="text-xs">
                <Zap className="h-3 w-3 mr-1" />
                LLMs ({metadata.summary?.total_llm_models || 0})
              </TabsTrigger>
            </TabsList>

            {/* Workflows Tab */}
            <TabsContent value="workflows" className="mt-4">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {filterItems(metadata.workflows || []).map(workflow => (
                    <MetadataItem
                      key={workflow.id}
                      item={workflow}
                      isSelected={selectedContext.workflow?.id === workflow.id}
                      onSelect={() => handleWorkflowSelect(workflow as WorkflowMetadata)}
                    />
                  ))}
                  {filterItems(metadata.workflows || []).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Workflow className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No workflows found</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Agents Tab */}
            <TabsContent value="agents" className="mt-4">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {filterItems(metadata.agents || []).map(agent => (
                    <MetadataItem
                      key={agent.id}
                      item={agent}
                      isSelected={selectedContext.agent?.id === agent.id}
                      onSelect={() => handleAgentSelect(agent as AgentMetadata)}
                    />
                  ))}
                  {filterItems(metadata.agents || []).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Bot className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No agents found</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Tools Tab */}
            <TabsContent value="tools" className="mt-4">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {filterItems(metadata.tools || []).map(tool => (
                    <MetadataItem
                      key={tool.id}
                      item={tool}
                      isSelected={selectedContext.tools?.some(t => t.id === tool.id) || false}
                      onSelect={() => handleToolSelect(tool as ToolMetadata)}
                      isMultiSelect={true}
                    />
                  ))}
                  {filterItems(metadata.tools || []).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Wrench className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No tools found</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* LLM Models Tab */}
            <TabsContent value="llm" className="mt-4">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {filterItems(metadata.llm_models || []).map(llm_model => (
                    <MetadataItem
                      key={llm_model.id}
                      item={llm_model}
                      isSelected={selectedContext.llm_model?.id === llm_model.id}
                      onSelect={() => handleLLMSelect(llm_model as LLMModelMetadata)}
                    />
                  ))}
                  {filterItems(metadata.llm_models || []).length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No LLM models found</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>

          {/* Quick Selection Info */}
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h4 className="text-sm font-medium mb-2">Selection Guide:</h4>
            <div className="space-y-1 text-xs text-gray-600 dark:text-gray-300">
              <p>• <strong>Workflow:</strong> Routes to workflow DNS endpoint</p>
              <p>• <strong>Agent:</strong> Direct A2A agent communication</p>
              <p>• <strong>Tools:</strong> Uses Generic A2A agent with selected tools</p>
              <p>• <strong>LLM:</strong> Direct LLM model chat (when no workflow/agent selected)</p>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
};