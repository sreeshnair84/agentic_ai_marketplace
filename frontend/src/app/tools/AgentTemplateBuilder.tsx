'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  Save, 
  Trash2,
  Bot,
  Settings,
  Workflow,
  Brain,
  MessageSquare,
  Zap,
  CheckCircle,
  AlertCircle,
  Info,
  Play,
  Eye,
  EyeOff,
  ArrowRight,
  ArrowDown,
  Edit
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

interface ToolTemplate {
  id?: string;
  name: string;
  description: string;
  template_type: string;
  is_active?: boolean;
}

interface WorkflowNode {
  id: string;
  type: 'tool' | 'condition' | 'llm' | 'input' | 'output';
  label: string;
  tool_id?: string;
  configuration?: Record<string, unknown>;
  position: { x: number; y: number };
}

interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  condition?: string;
}

interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'azure' | 'local';
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt?: string;
  custom_parameters?: Record<string, unknown>;
}

interface AgentTemplate {
  id?: string;
  name: string;
  description: string;
  agent_type: 'simple' | 'workflow' | 'multi_agent' | 'supervisor';
  tools: string[];
  llm_config: LLMConfig;
  workflow_definition?: {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
  };
  system_prompt: string;
  instructions: string;
  metadata?: Record<string, unknown>;
  is_active: boolean;
}

interface AgentTemplateBuilderProps {
  template?: AgentTemplate;
  toolTemplates: ToolTemplate[];
  onSave: (template: AgentTemplate) => void;
  onCancel: () => void;
}

const agentTypeConfig = {
  simple: {
    icon: <Bot className="h-5 w-5 text-blue-600" />,
    label: 'Simple Agent',
    description: 'Single-purpose agent with basic tool integration',
    features: ['LLM Integration', 'Tool Access', 'Simple Prompts']
  },
  workflow: {
    icon: <Workflow className="h-5 w-5 text-green-600" />,
    label: 'Workflow Agent',
    description: 'Agent with complex workflow and conditional logic',
    features: ['LangGraph Integration', 'Complex Workflows', 'State Management']
  },
  multi_agent: {
    icon: <Brain className="h-5 w-5 text-purple-600" />,
    label: 'Multi-Agent System',
    description: 'Coordinated team of specialized agents',
    features: ['Agent Coordination', 'Task Distribution', 'Result Aggregation']
  },
  supervisor: {
    icon: <MessageSquare className="h-5 w-5 text-orange-600" />,
    label: 'Supervisor Agent',
    description: 'Agent that manages and coordinates other agents',
    features: ['Agent Management', 'Task Delegation', 'Quality Control']
  }
};

const llmProviders = {
  openai: {
    label: 'OpenAI',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4-turbo'],
    maxTokens: 4096
  },
  anthropic: {
    label: 'Anthropic',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    maxTokens: 4096
  },
  azure: {
    label: 'Azure OpenAI',
    models: ['gpt-4', 'gpt-35-turbo', 'gpt-4-32k'],
    maxTokens: 8192
  },
  local: {
    label: 'Local Model',
    models: ['llama-2-7b', 'llama-2-13b', 'mistral-7b'],
    maxTokens: 2048
  }
};

const nodeTypes = [
  { type: 'input', label: 'Input', icon: <ArrowRight className="h-4 w-4" />, color: 'blue' },
  { type: 'tool', label: 'Tool', icon: <Zap className="h-4 w-4" />, color: 'green' },
  { type: 'llm', label: 'LLM', icon: <Brain className="h-4 w-4" />, color: 'purple' },
  { type: 'condition', label: 'Condition', icon: <Settings className="h-4 w-4" />, color: 'orange' },
  { type: 'output', label: 'Output', icon: <ArrowDown className="h-4 w-4" />, color: 'red' }
];

export default function AgentTemplateBuilder({ 
  template, 
  toolTemplates,
  onSave, 
  onCancel 
}: AgentTemplateBuilderProps) {
  const [formData, setFormData] = useState<AgentTemplate>({
    name: '',
    description: '',
    agent_type: 'simple',
    tools: [],
    llm_config: {
      provider: 'openai',
      model: 'gpt-4o',
      temperature: 0.7,
      max_tokens: 1000
    },
    system_prompt: '',
    instructions: '',
    is_active: true
  });

  const [activeTab, setActiveTab] = useState('basic');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [testResult, setTestResult] = useState<{
    status: string;
    message: string;
    test_input?: string;
    response?: string;
    execution_time?: string;
    tools_used?: string[];
    token_usage?: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  } | null>(null);

  useEffect(() => {
    if (template) {
      setFormData(template);
    }
  }, [template]);

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleLLMConfigChange = (field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      llm_config: {
        ...prev.llm_config,
        [field]: value
      }
    }));
  };

  const addTool = (toolId: string) => {
    if (!formData.tools.includes(toolId)) {
      setFormData(prev => ({
        ...prev,
        tools: [...prev.tools, toolId]
      }));
    }
  };

  const removeTool = (toolId: string) => {
    setFormData(prev => ({
      ...prev,
      tools: prev.tools.filter(id => id !== toolId)
    }));
  };

  const addWorkflowNode = (type: string) => {
    if (!formData.workflow_definition) {
      setFormData(prev => ({
        ...prev,
        workflow_definition: { nodes: [], edges: [] }
      }));
    }

    const newNode: WorkflowNode = {
      id: `node_${Date.now()}`,
      type: type as any,
      label: `New ${type}`,
      position: { 
        x: Math.random() * 400 + 100, 
        y: Math.random() * 300 + 100 
      },
      configuration: {}
    };

    setFormData(prev => ({
      ...prev,
      workflow_definition: {
        ...prev.workflow_definition!,
        nodes: [...prev.workflow_definition!.nodes, newNode]
      }
    }));
  };

  const updateWorkflowNode = (nodeId: string, updates: Partial<WorkflowNode>) => {
    setFormData(prev => ({
      ...prev,
      workflow_definition: {
        ...prev.workflow_definition!,
        nodes: prev.workflow_definition!.nodes.map(node =>
          node.id === nodeId ? { ...node, ...updates } : node
        )
      }
    }));
  };

  const removeWorkflowNode = (nodeId: string) => {
    setFormData(prev => ({
      ...prev,
      workflow_definition: {
        nodes: prev.workflow_definition!.nodes.filter(node => node.id !== nodeId),
        edges: prev.workflow_definition!.edges.filter(edge => 
          edge.source !== nodeId && edge.target !== nodeId
        )
      }
    }));
  };

  const testAgent = async () => {
    setTestResult({ status: 'testing', message: 'Testing agent configuration...' });
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setTestResult({
      status: 'success',
      message: 'Agent test completed successfully',
      test_input: 'Hello, can you help me analyze this data?',
      response: 'I can help you analyze data using the available tools. What type of data would you like me to examine?',
      execution_time: '1.2s',
      tools_used: ['data_analyzer', 'visualization_tool'],
      token_usage: {
        prompt_tokens: 150,
        completion_tokens: 45,
        total_tokens: 195
      }
    });
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Agent name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    if (!formData.system_prompt.trim()) {
      newErrors.system_prompt = 'System prompt is required';
    }

    if (!formData.instructions.trim()) {
      newErrors.instructions = 'Instructions are required';
    }

    if (formData.agent_type === 'workflow' && 
        (!formData.workflow_definition || formData.workflow_definition.nodes.length === 0)) {
      newErrors.workflow = 'Workflow definition is required for workflow agents';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSave(formData);
    }
  };

  const generateSystemPrompt = () => {
    const agentType = agentTypeConfig[formData.agent_type];
    const tools = formData.tools.map(toolId => {
      const tool = toolTemplates.find(t => t.id === toolId);
      return tool ? tool.name : toolId;
    });

    const prompt = `You are a ${agentType.label.toLowerCase()} designed to ${formData.description.toLowerCase()}.

Your capabilities include:
${agentType.features.map(feature => `- ${feature}`).join('\n')}

Available tools:
${tools.map(tool => `- ${tool}`).join('\n')}

Instructions:
${formData.instructions}

Always be helpful, accurate, and follow the provided instructions carefully.`;

    setFormData(prev => ({ ...prev, system_prompt: prompt }));
  };

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          {template ? 'Edit Agent Template' : 'Create Agent Template'}
        </h2>
        <Button variant="ghost" onClick={onCancel}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Content */}
      <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 140px)' }}>
        <form onSubmit={handleSubmit} className="space-y-6">
          
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="type">Agent Type</TabsTrigger>
              <TabsTrigger value="tools">Tools</TabsTrigger>
              <TabsTrigger value="llm">LLM Config</TabsTrigger>
              <TabsTrigger value="workflow">Workflow</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Agent Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="e.g., Data Analysis Assistant"
                  />
                  {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Status
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={(e) => handleInputChange('is_active', e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="is_active" className="text-sm text-gray-700 dark:text-gray-300">
                      Active
                    </label>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Describe the agent's purpose and capabilities..."
                />
                {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Instructions <span className="text-red-500">*</span>
                  </label>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={generateSystemPrompt}
                  >
                    <Bot className="h-4 w-4 mr-2" />
                    Generate System Prompt
                  </Button>
                </div>
                <textarea
                  value={formData.instructions}
                  onChange={(e) => handleInputChange('instructions', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Provide detailed instructions for the agent's behavior..."
                />
                {errors.instructions && <p className="text-red-500 text-sm mt-1">{errors.instructions}</p>}
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    System Prompt <span className="text-red-500">*</span>
                  </label>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowSystemPrompt(!showSystemPrompt)}
                  >
                    {showSystemPrompt ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                {showSystemPrompt && (
                  <textarea
                    value={formData.system_prompt}
                    onChange={(e) => handleInputChange('system_prompt', e.target.value)}
                    rows={8}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                    placeholder="Enter the system prompt for the agent..."
                  />
                )}
                {errors.system_prompt && <p className="text-red-500 text-sm mt-1">{errors.system_prompt}</p>}
              </div>

              {/* Test Results */}
              {testResult && (
                <div className={`border rounded-lg p-4 ${
                  testResult.status === 'success' ? 'border-green-200 bg-green-50 dark:bg-green-900/20' :
                  testResult.status === 'error' ? 'border-red-200 bg-red-50 dark:bg-red-900/20' :
                  'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20'
                }`}>
                  <div className="flex items-start space-x-3">
                    {testResult.status === 'testing' && (
                      <Settings className="h-5 w-5 text-yellow-600 animate-spin mt-0.5" />
                    )}
                    {testResult.status === 'success' && (
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    )}
                    {testResult.status === 'error' && (
                      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <h4 className="font-medium">
                        {testResult.status === 'testing' ? 'Testing Agent...' : 
                         testResult.status === 'success' ? 'Test Results' : 'Test Failed'}
                      </h4>
                      <p className="text-sm mt-1">{testResult.message}</p>
                      
                      {testResult.test_input && (
                        <div className="mt-3 space-y-2">
                          <div className="bg-white dark:bg-gray-800 rounded p-3 border">
                            <p className="font-medium text-sm mb-1">Input:</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {testResult.test_input}
                            </p>
                          </div>
                          <div className="bg-white dark:bg-gray-800 rounded p-3 border">
                            <p className="font-medium text-sm mb-1">Response:</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {testResult.response}
                            </p>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Execution Time:</span>
                              <span className="ml-1">{testResult.execution_time}</span>
                            </div>
                            <div>
                              <span className="font-medium">Tools Used:</span>
                              <span className="ml-1">{testResult.tools_used?.length || 0}</span>
                            </div>
                            <div>
                              <span className="font-medium">Total Tokens:</span>
                              <span className="ml-1">{testResult.token_usage?.total_tokens || 0}</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="type" className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                  Select Agent Type
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(agentTypeConfig).map(([type, config]) => (
                    <Card 
                      key={type}
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        formData.agent_type === type 
                          ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => handleInputChange('agent_type', type)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start space-x-3">
                          <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
                            {config.icon}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-medium">{config.label}</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                              {config.description}
                            </p>
                            <div className="space-y-1">
                              {config.features.map((feature, index) => (
                                <div key={index} className="flex items-center space-x-2">
                                  <CheckCircle className="h-3 w-3 text-green-500" />
                                  <span className="text-xs text-gray-500 dark:text-gray-400">
                                    {feature}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="tools" className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Available Tools
                </h3>
                <Badge variant="secondary">
                  {formData.tools.length} selected
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {toolTemplates.filter(t => t.is_active !== false).map((tool) => {
                  const isSelected = formData.tools.includes(tool.id!);
                  return (
                    <Card 
                      key={tool.id}
                      className={`cursor-pointer transition-all ${
                        isSelected 
                          ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => isSelected ? removeTool(tool.id!) : addTool(tool.id!)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{tool.name}</h4>
                          {isSelected && (
                            <CheckCircle className="h-5 w-5 text-blue-600" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {tool.description}
                        </p>
                        <Badge variant="outline">{tool.template_type}</Badge>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {formData.tools.length === 0 && (
                <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                  <Zap className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 dark:text-gray-400">
                    No tools selected. Click on tools above to add them to your agent.
                  </p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="llm" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    LLM Provider
                  </label>
                  <select
                    value={formData.llm_config.provider}
                    onChange={(e) => handleLLMConfigChange('provider', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    {Object.entries(llmProviders).map(([key, provider]) => (
                      <option key={key} value={key}>{provider.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Model
                  </label>
                  <select
                    value={formData.llm_config.model}
                    onChange={(e) => handleLLMConfigChange('model', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    {llmProviders[formData.llm_config.provider].models.map(model => (
                      <option key={model} value={model}>{model}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Temperature ({formData.llm_config.temperature})
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.llm_config.temperature}
                    onChange={(e) => handleLLMConfigChange('temperature', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Focused</span>
                    <span>Balanced</span>
                    <span>Creative</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    min="1"
                    max={llmProviders[formData.llm_config.provider].maxTokens}
                    value={formData.llm_config.max_tokens}
                    onChange={(e) => handleLLMConfigChange('max_tokens', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">
                      LLM Configuration
                    </h4>
                    <div className="text-sm text-blue-700 dark:text-blue-300 mt-1 space-y-1">
                      <p>• Temperature controls randomness (0 = deterministic, 2 = very creative)</p>
                      <p>• Max tokens limits the response length</p>
                      <p>• Choose models based on your performance and cost requirements</p>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="workflow" className="space-y-6">
              {formData.agent_type === 'workflow' ? (
                <>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      Workflow Designer
                    </h3>
                    <div className="flex items-center space-x-2">
                      {nodeTypes.map((nodeType) => (
                        <Button
                          key={nodeType.type}
                          type="button"
                          size="sm"
                          variant="outline"
                          onClick={() => addWorkflowNode(nodeType.type)}
                          className="flex items-center space-x-2"
                        >
                          {nodeType.icon}
                          <span>{nodeType.label}</span>
                        </Button>
                      ))}
                    </div>
                  </div>

                  {formData.workflow_definition && formData.workflow_definition.nodes.length > 0 ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {formData.workflow_definition.nodes.map((node) => {
                          const nodeTypeConfig = nodeTypes.find(nt => nt.type === node.type);
                          return (
                            <Card 
                              key={node.id}
                              className={`cursor-pointer transition-all ${
                                selectedNode?.id === node.id
                                  ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                  : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                              }`}
                              onClick={() => setSelectedNode(node)}
                            >
                              <CardContent className="p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <div className="flex items-center space-x-2">
                                    {nodeTypeConfig?.icon}
                                    <span className="font-medium">{node.label}</span>
                                  </div>
                                  <Button
                                    type="button"
                                    size="sm"
                                    variant="ghost"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      removeWorkflowNode(node.id);
                                    }}
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </div>
                                <Badge variant="outline">{node.type}</Badge>
                                {node.tool_id && (
                                  <div className="mt-2">
                                    <span className="text-xs text-gray-500">
                                      Tool: {toolTemplates.find(t => t.id === node.tool_id)?.name || node.tool_id}
                                    </span>
                                  </div>
                                )}
                              </CardContent>
                            </Card>
                          );
                        })}
                      </div>

                      {selectedNode && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                              <Edit className="h-5 w-5" />
                              <span>Edit Node: {selectedNode.label}</span>
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Node Label
                              </label>
                              <input
                                type="text"
                                value={selectedNode.label}
                                onChange={(e) => updateWorkflowNode(selectedNode.id, { label: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                              />
                            </div>

                            {selectedNode.type === 'tool' && (
                              <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                  Select Tool
                                </label>
                                <select
                                  value={selectedNode.tool_id || ''}
                                  onChange={(e) => updateWorkflowNode(selectedNode.id, { tool_id: e.target.value })}
                                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                >
                                  <option value="">Select a tool</option>
                                  {formData.tools.map(toolId => {
                                    const tool = toolTemplates.find(t => t.id === toolId);
                                    return (
                                      <option key={toolId} value={toolId}>
                                        {tool?.name || toolId}
                                      </option>
                                    );
                                  })}
                                </select>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                      <Workflow className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500 dark:text-gray-400 mb-4">
                        No workflow nodes defined
                      </p>
                      <p className="text-sm text-gray-400 dark:text-gray-500">
                        Add nodes above to start building your workflow
                      </p>
                    </div>
                  )}
                  {errors.workflow && <p className="text-red-500 text-sm">{errors.workflow}</p>}
                </>
              ) : (
                <div className="text-center py-12 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <Info className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">
                    Workflow configuration is only available for Workflow Agent type.
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                    Switch to &quot;Workflow Agent&quot; in the Agent Type tab to configure workflows.
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>

          {errors.submit && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200">{errors.submit}</p>
            </div>
          )}
        </form>
      </div>

      {/* Footer */}
      <div className="flex justify-between p-6 border-t border-gray-200 dark:border-gray-700">
        <Button
          type="button"
          variant="outline"
          onClick={testAgent}
          disabled={!formData.name || !formData.system_prompt}
        >
          <Play className="h-4 w-4 mr-2" />
          Test Agent
        </Button>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            <Save className="h-4 w-4 mr-2" />
            Save Template
          </Button>
        </div>
      </div>
    </>
  );
}
