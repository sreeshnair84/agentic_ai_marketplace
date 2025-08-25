'use client';

import { useState, useEffect } from 'react';
import { useLLMModels } from '@/hooks/useLLMModels';
import { useTools } from '@/hooks/useTools';
import { useMCP } from '@/hooks/useMCP';
import type { Agent } from '@/hooks/useAgents';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  XMarkIcon, 
  InformationCircleIcon,
  CogIcon as SettingsIcon,
  ServerIcon,
  DocumentTextIcon,
  TagIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

type FrameworkType = 'langgraph' | 'crewai' | 'autogen' | 'semantic_kernel' | 'custom';

interface AgentData {
  name: string;
  display_name?: string;
  description: string;
  framework: FrameworkType;
  capabilities: string[];
  systemPrompt?: string;
  system_prompt?: string;
  tags?: string[];
  project_tags?: string[];
  llm_model_id?: string;
  temperature?: number;
  maxTokens?: number;
  max_tokens?: number;
  category?: string;
  agent_type?: string;
  version?: string;
  a2a_enabled?: boolean;
  a2a_address?: string;
  // Deployment fields
  url?: string;
  dns_name?: string;
  health_url?: string;
  environment?: string;
  author?: string;
  organization?: string;
  // Signature fields
  input_signature?: Record<string, any>;
  output_signature?: Record<string, any>;
  default_input_modes?: string[];
  default_output_modes?: string[];
  // Model configuration
  model_config_data?: Record<string, any>;
  // Additional properties for the form
  skills?: string[];
  ai_provider?: string;
  model_name?: string;
  [key: string]: unknown;
}

interface CreateAgentDialogProps {
  open: boolean;
  onClose: () => void;
  onSave?: (agentData: AgentData) => void;
  editingAgent?: Agent | null;
}


export function CreateAgentDialog({ open, onClose, onSave, editingAgent }: CreateAgentDialogProps) {
  const [formData, setFormData] = useState<AgentData>({
    name: '',
    display_name: '',
    description: '',
    framework: 'langgraph' as FrameworkType,
    capabilities: [],
    systemPrompt: '',
    system_prompt: '',
    llm_model_id: '',
    temperature: 0.7,
    maxTokens: 2000,
    max_tokens: 2000,
    category: 'general',
    agent_type: 'autonomous',
    version: '1.0.0',
    a2a_enabled: true,
    a2a_address: '',
    // Deployment fields
    url: '',
    dns_name: '',
    health_url: '',
    environment: 'development',
    author: '',
    organization: '',
    // Signature fields
    input_signature: {},
    output_signature: {},
    default_input_modes: ['text'],
    default_output_modes: ['text'],
    // Model configuration
    model_config_data: {},
    skills: [],
    tags: [],
    project_tags: [],
  });

  const { models, loading: modelsLoading, error: modelsError, fetchModels } = useLLMModels();
  const { toolTemplates, toolInstances, loading: toolsLoading, fetchData: fetchTools } = useTools();
  const { tools: mcpTools, endpoints: mcpEndpoints, loading: mcpLoading, fetchTools: fetchMCPTools, fetchEndpoints: fetchMCPEndpoints } = useMCP();

  useEffect(() => {
    fetchModels();
    fetchTools();
    fetchMCPTools();
    fetchMCPEndpoints();
  }, [fetchModels, fetchTools, fetchMCPTools, fetchMCPEndpoints]);

  // Pre-populate form when editing an agent
  useEffect(() => {
    if (editingAgent) {
      setFormData({
        name: editingAgent.name || '',
        display_name: editingAgent.display_name || '',
        description: editingAgent.description || '',
        framework: editingAgent.framework || 'langgraph',
        capabilities: Array.isArray(editingAgent.capabilities) ? editingAgent.capabilities : [],
        systemPrompt: editingAgent.systemPrompt || editingAgent.system_prompt || '',
        system_prompt: editingAgent.system_prompt || editingAgent.systemPrompt || '',
        llm_model_id: editingAgent.llm_model_id || '',
        temperature: editingAgent.temperature || 0.7,
        maxTokens: editingAgent.maxTokens || editingAgent.max_tokens || 2000,
        max_tokens: editingAgent.max_tokens || editingAgent.maxTokens || 2000,
        category: editingAgent.category || 'general',
        agent_type: editingAgent.agent_type || 'autonomous',
        version: editingAgent.version || '1.0.0',
        a2a_enabled: editingAgent.a2a_enabled ?? true,
        a2a_address: editingAgent.a2a_address || '',
        // Deployment fields
        url: editingAgent.url || '',
        dns_name: editingAgent.dns_name || '',
        health_url: editingAgent.health_url || '',
        environment: editingAgent.environment || 'development',
        author: editingAgent.author || '',
        organization: editingAgent.organization || '',
        // Signature fields
        input_signature: editingAgent.input_signature || {},
        output_signature: editingAgent.output_signature || {},
        default_input_modes: Array.isArray(editingAgent.default_input_modes) ? editingAgent.default_input_modes : ['text'],
        default_output_modes: Array.isArray(editingAgent.default_output_modes) ? editingAgent.default_output_modes : ['text'],
        // Model configuration
        model_config_data: editingAgent.model_config_data || {},
        skills: Array.isArray(editingAgent.capabilities) ? editingAgent.capabilities : [],
        tags: Array.isArray(editingAgent.tags) ? editingAgent.tags : [],
        project_tags: Array.isArray(editingAgent.project_tags) ? editingAgent.project_tags : [],
      });
    } else {
      // Reset form for create mode
      setFormData({
        name: '',
        display_name: '',
        description: '',
        framework: 'langgraph',
        capabilities: [],
        systemPrompt: '',
        system_prompt: '',
        llm_model_id: '',
        temperature: 0.7,
        maxTokens: 2000,
        max_tokens: 2000,
        category: 'general',
        agent_type: 'autonomous',
        version: '1.0.0',
        a2a_enabled: true,
        a2a_address: '',
        // Deployment fields
        url: '',
        dns_name: '',
        health_url: '',
        environment: 'development',
        author: '',
        organization: '',
        // Signature fields
        input_signature: {},
        output_signature: {},
        default_input_modes: ['text'],
        default_output_modes: ['text'],
        // Model configuration
        model_config_data: {},
        skills: [],
        tags: [],
        project_tags: [],
      });
    }
  }, [editingAgent, open]);

  const [newSkill, setNewSkill] = useState('');
  const [newTag, setNewTag] = useState('');
  const [newProjectTag, setNewProjectTag] = useState('');
  const [newInputField, setNewInputField] = useState({ name: '', type: 'string', required: false, description: '' });
  const [newOutputField, setNewOutputField] = useState({ name: '', type: 'string', required: false, description: '' });
  const [inputModeText, setInputModeText] = useState('');
  const [outputModeText, setOutputModeText] = useState('');

  if (!open) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave?.(formData);
    onClose();
  };

  const addSkill = () => {
    if (newSkill.trim() && !(formData.skills || []).includes(newSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...(prev.skills || []), newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: (prev.skills || []).filter(s => s !== skill)
    }));
  };

  const addTag = () => {
    if (newTag.trim() && !(formData.tags || []).includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: (prev.tags || []).filter(t => t !== tag)
    }));
  };

  const addProjectTag = () => {
    if (newProjectTag.trim() && !(formData.project_tags || []).includes(newProjectTag.trim())) {
      setFormData(prev => ({
        ...prev,
        project_tags: [...(prev.project_tags || []), newProjectTag.trim()]
      }));
      setNewProjectTag('');
    }
  };

  const removeProjectTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      project_tags: (prev.project_tags || []).filter(t => t !== tag)
    }));
  };

  const addInputField = () => {
    if (newInputField.name.trim()) {
      const currentSignature = formData.input_signature || {};
      const newSignature = {
        ...currentSignature,
        [newInputField.name]: {
          type: newInputField.type,
          required: newInputField.required,
          description: newInputField.description
        }
      };
      setFormData(prev => ({ ...prev, input_signature: newSignature }));
      setNewInputField({ name: '', type: 'string', required: false, description: '' });
    }
  };

  const removeInputField = (fieldName: string) => {
    const currentSignature = formData.input_signature || {};
    const { [fieldName]: removed, ...newSignature } = currentSignature;
    setFormData(prev => ({ ...prev, input_signature: newSignature }));
  };

  const addOutputField = () => {
    if (newOutputField.name.trim()) {
      const currentSignature = formData.output_signature || {};
      const newSignature = {
        ...currentSignature,
        [newOutputField.name]: {
          type: newOutputField.type,
          required: newOutputField.required,
          description: newOutputField.description
        }
      };
      setFormData(prev => ({ ...prev, output_signature: newSignature }));
      setNewOutputField({ name: '', type: 'string', required: false, description: '' });
    }
  };

  const removeOutputField = (fieldName: string) => {
    const currentSignature = formData.output_signature || {};
    const { [fieldName]: removed, ...newSignature } = currentSignature;
    setFormData(prev => ({ ...prev, output_signature: newSignature }));
  };

  const addInputMode = () => {
    if (inputModeText.trim() && !(formData.default_input_modes || []).includes(inputModeText.trim())) {
      setFormData(prev => ({
        ...prev,
        default_input_modes: [...(prev.default_input_modes || []), inputModeText.trim()]
      }));
      setInputModeText('');
    }
  };

  const removeInputMode = (mode: string) => {
    setFormData(prev => ({
      ...prev,
      default_input_modes: (prev.default_input_modes || []).filter(m => m !== mode)
    }));
  };

  const addOutputMode = () => {
    if (outputModeText.trim() && !(formData.default_output_modes || []).includes(outputModeText.trim())) {
      setFormData(prev => ({
        ...prev,
        default_output_modes: [...(prev.default_output_modes || []), outputModeText.trim()]
      }));
      setOutputModeText('');
    }
  };

  const removeOutputMode = (mode: string) => {
    setFormData(prev => ({
      ...prev,
      default_output_modes: (prev.default_output_modes || []).filter(m => m !== mode)
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {editingAgent ? 'Edit Agent' : 'Create New Agent'}
          </h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8"
          >
            <XMarkIcon className="h-4 w-4" />
          </Button>
        </div>

        <Tabs defaultValue="basic" className="p-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="basic" className="flex items-center gap-2">
              <InformationCircleIcon className="h-4 w-4" />
              Basic Info
            </TabsTrigger>
            <TabsTrigger value="configuration" className="flex items-center gap-2">
              <SettingsIcon className="h-4 w-4" />
              Configuration
            </TabsTrigger>
            <TabsTrigger value="deployment" className="flex items-center gap-2">
              <ServerIcon className="h-4 w-4" />
              Deployment
            </TabsTrigger>
            <TabsTrigger value="signatures" className="flex items-center gap-2">
              <DocumentTextIcon className="h-4 w-4" />
              Signatures
            </TabsTrigger>
            <TabsTrigger value="metadata" className="flex items-center gap-2">
              <TagIcon className="h-4 w-4" />
              Metadata
            </TabsTrigger>
          </TabsList>

          <form onSubmit={handleSubmit}>
            {/* Basic Information Tab */}
            <TabsContent value="basic" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Basic Information</CardTitle>
                  <CardDescription>Core agent identification and description</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Agent Name *
                      </label>
                      <Input
                        value={formData.name}
                        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter agent name (e.g., customer-service-agent)"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Display Name
                      </label>
                      <Input
                        value={formData.display_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, display_name: e.target.value }))}
                        placeholder="Enter display name (e.g., Customer Service Agent)"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Framework *
                      </label>
                      <select
                        value={formData.framework}
                        onChange={(e) => setFormData(prev => ({ ...prev, framework: e.target.value as FrameworkType }))}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="langgraph">LangGraph 🕸️</option>
                        <option value="crewai">CrewAI 👥</option>
                        <option value="autogen">AutoGen 🤖</option>
                        <option value="semantic_kernel">Semantic Kernel 🧠</option>
                        <option value="custom">Custom 🛠️</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Version
                      </label>
                      <Input
                        value={formData.version}
                        onChange={(e) => setFormData(prev => ({ ...prev, version: e.target.value }))}
                        placeholder="1.0.0"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description *
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Describe what this agent does"
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Category
                      </label>
                      <select
                        value={formData.category}
                        onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="general">General</option>
                        <option value="customer-service">Customer Service</option>
                        <option value="data-analytics">Data Analytics</option>
                        <option value="content-creation">Content Creation</option>
                        <option value="research">Research</option>
                        <option value="automation">Automation</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Agent Type
                      </label>
                      <select
                        value={formData.agent_type}
                        onChange={(e) => setFormData(prev => ({ ...prev, agent_type: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="autonomous">Autonomous</option>
                        <option value="collaborative">Collaborative</option>
                        <option value="specialized">Specialized</option>
                        <option value="supervisor">Supervisor</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Author
                      </label>
                      <Input
                        value={formData.author}
                        onChange={(e) => setFormData(prev => ({ ...prev, author: e.target.value }))}
                        placeholder="Author name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Organization
                      </label>
                      <Input
                        value={formData.organization}
                        onChange={(e) => setFormData(prev => ({ ...prev, organization: e.target.value }))}
                        placeholder="Organization name"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Configuration Tab */}
            <TabsContent value="configuration" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>LLM Configuration</CardTitle>
                  <CardDescription>Model selection and behavior settings</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      LLM Model *
                    </label>
                    <select
                      value={formData.llm_model_id}
                      onChange={(e) => setFormData(prev => ({ ...prev, llm_model_id: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Select a model</option>
                      {modelsLoading && <option>Loading...</option>}
                      {modelsError && <option disabled>Error loading models</option>}
                      {models && Array.isArray(models) && models
                        .filter(model => model.model_type === 'chat' || model.model_type === 'completion' || model.model_type === 'multimodal')
                        .map((model) => (
                          <option key={model.id} value={model.id}>
                            {model.display_name || model.name} ({model.provider})
                          </option>
                        ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Temperature
                      </label>
                      <Input
                        type="number"
                        min="0"
                        max="2"
                        step="0.1"
                        value={formData.temperature}
                        onChange={(e) => setFormData(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Max Tokens
                      </label>
                      <Input
                        type="number"
                        min="1"
                        max="8000"
                        value={formData.maxTokens}
                        onChange={(e) => {
                          const value = parseInt(e.target.value);
                          setFormData(prev => ({ ...prev, maxTokens: value, max_tokens: value }));
                        }}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      System Prompt
                    </label>
                    <textarea
                      value={formData.systemPrompt}
                      onChange={(e) => {
                        const value = e.target.value;
                        setFormData(prev => ({ ...prev, systemPrompt: value, system_prompt: value }));
                      }}
                      placeholder="Enter the system prompt for this agent"
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      id="a2a_enabled"
                      checked={formData.a2a_enabled}
                      onChange={(e) => setFormData(prev => ({ ...prev, a2a_enabled: e.target.checked }))}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                    />
                    <label htmlFor="a2a_enabled" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Enable Agent-to-Agent Communication
                    </label>
                  </div>

                  {formData.a2a_enabled && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        A2A Address
                      </label>
                      <Input
                        value={formData.a2a_address}
                        onChange={(e) => setFormData(prev => ({ ...prev, a2a_address: e.target.value }))}
                        placeholder="A2A communication address"
                      />
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Capabilities & Skills</CardTitle>
                  <CardDescription>Define what this agent can do</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Skills
                    </label>
                    <div className="flex gap-2 mb-2">
                      <Input
                        value={newSkill}
                        onChange={(e) => setNewSkill(e.target.value)}
                        placeholder="Add a skill"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                      />
                      <Button type="button" onClick={addSkill} variant="outline">
                        Add
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData.skills || []).map((skill) => (
                        <Badge key={skill} variant="secondary" className="flex items-center gap-1">
                          {skill}
                          <button
                            type="button"
                            onClick={() => removeSkill(skill)}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Available Tools & Integrations
                    </label>
                    <div className="max-h-64 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-md p-3">
                      {(toolsLoading || mcpLoading) ? (
                        <div className="text-center py-4 text-gray-500">Loading tools and MCP integrations...</div>
                      ) : (
                        <div className="space-y-3">
                          {/* Tool Templates */}
                          {toolTemplates.length > 0 && (
                            <div>
                              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">Tool Templates</h4>
                              <div className="space-y-2">
                                {toolTemplates.map((tool) => (
                                  <div key={`template-${tool.id}`} className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
                                    <input
                                      type="checkbox"
                                      id={`template-${tool.id}`}
                                      checked={(formData.capabilities || []).includes(`template:${tool.name}`)}
                                      onChange={(e) => {
                                        const toolId = `template:${tool.name}`;
                                        const isChecked = e.target.checked;
                                        const currentCapabilities = formData.capabilities || [];
                                        
                                        if (isChecked) {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: [...currentCapabilities, toolId]
                                          }));
                                        } else {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: currentCapabilities.filter(cap => cap !== toolId)
                                          }));
                                        }
                                      }}
                                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                                    />
                                    <label htmlFor={`template-${tool.id}`} className="flex-1 text-sm cursor-pointer">
                                      <div className="font-medium">{tool.display_name}</div>
                                      <div className="text-gray-500 dark:text-gray-400 text-xs">{tool.description}</div>
                                      <div className="flex gap-1 mt-1">
                                        <Badge variant="outline" className="text-xs">Template</Badge>
                                        <Badge variant="outline" className="text-xs">{tool.category}</Badge>
                                        {tool.tags?.slice(0, 2).map(tag => (
                                          <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                                        ))}
                                      </div>
                                    </label>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Tool Instances */}
                          {toolInstances.length > 0 && (
                            <div>
                              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">Tool Instances</h4>
                              <div className="space-y-2">
                                {toolInstances.map((tool) => (
                                  <div key={`instance-${tool.id}`} className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
                                    <input
                                      type="checkbox"
                                      id={`instance-${tool.id}`}
                                      checked={(formData.capabilities || []).includes(`instance:${tool.name}`)}
                                      onChange={(e) => {
                                        const toolId = `instance:${tool.name}`;
                                        const isChecked = e.target.checked;
                                        const currentCapabilities = formData.capabilities || [];
                                        
                                        if (isChecked) {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: [...currentCapabilities, toolId]
                                          }));
                                        } else {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: currentCapabilities.filter(cap => cap !== toolId)
                                          }));
                                        }
                                      }}
                                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                                    />
                                    <label htmlFor={`instance-${tool.id}`} className="flex-1 text-sm cursor-pointer">
                                      <div className="font-medium">{tool.display_name}</div>
                                      <div className="text-gray-500 dark:text-gray-400 text-xs">{tool.description}</div>
                                      <div className="flex gap-1 mt-1">
                                        <Badge variant="outline" className="text-xs">Instance</Badge>
                                        <Badge variant="outline" className="text-xs">{tool.category}</Badge>
                                        <Badge variant={tool.status === 'active' ? 'default' : 'secondary'} className="text-xs">{tool.status}</Badge>
                                        {tool.tags?.slice(0, 1).map(tag => (
                                          <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                                        ))}
                                      </div>
                                    </label>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* MCP Tools */}
                          {mcpTools.length > 0 && (
                            <div>
                              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">MCP Tools</h4>
                              <div className="space-y-2">
                                {mcpTools.map((tool) => (
                                  <div key={`mcp-tool-${tool.id}`} className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
                                    <input
                                      type="checkbox"
                                      id={`mcp-tool-${tool.id}`}
                                      checked={(formData.capabilities || []).includes(`mcp:${tool.tool_name}`)}
                                      onChange={(e) => {
                                        const toolId = `mcp:${tool.tool_name}`;
                                        const isChecked = e.target.checked;
                                        const currentCapabilities = formData.capabilities || [];
                                        
                                        if (isChecked) {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: [...currentCapabilities, toolId]
                                          }));
                                        } else {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: currentCapabilities.filter(cap => cap !== toolId)
                                          }));
                                        }
                                      }}
                                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                                    />
                                    <label htmlFor={`mcp-tool-${tool.id}`} className="flex-1 text-sm cursor-pointer">
                                      <div className="font-medium">{tool.display_name || tool.tool_name}</div>
                                      <div className="text-gray-500 dark:text-gray-400 text-xs">{tool.description}</div>
                                      <div className="flex gap-1 mt-1">
                                        <Badge variant="outline" className="text-xs">MCP</Badge>
                                        <Badge variant={tool.is_available ? 'default' : 'secondary'} className="text-xs">
                                          {tool.is_available ? 'Available' : 'Unavailable'}
                                        </Badge>
                                        {tool.success_rate > 0 && (
                                          <Badge variant="secondary" className="text-xs">
                                            {(tool.success_rate * 100).toFixed(0)}% success
                                          </Badge>
                                        )}
                                      </div>
                                    </label>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* MCP Endpoints */}
                          {mcpEndpoints.length > 0 && (
                            <div>
                              <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">MCP Endpoints</h4>
                              <div className="space-y-2">
                                {mcpEndpoints.map((endpoint) => (
                                  <div key={`mcp-endpoint-${endpoint.id}`} className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded">
                                    <input
                                      type="checkbox"
                                      id={`mcp-endpoint-${endpoint.id}`}
                                      checked={(formData.capabilities || []).includes(`mcp-endpoint:${endpoint.endpoint_name}`)}
                                      onChange={(e) => {
                                        const endpointId = `mcp-endpoint:${endpoint.endpoint_name}`;
                                        const isChecked = e.target.checked;
                                        const currentCapabilities = formData.capabilities || [];
                                        
                                        if (isChecked) {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: [...currentCapabilities, endpointId]
                                          }));
                                        } else {
                                          setFormData(prev => ({
                                            ...prev,
                                            capabilities: currentCapabilities.filter(cap => cap !== endpointId)
                                          }));
                                        }
                                      }}
                                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
                                    />
                                    <label htmlFor={`mcp-endpoint-${endpoint.id}`} className="flex-1 text-sm cursor-pointer">
                                      <div className="font-medium">{endpoint.display_name}</div>
                                      <div className="text-gray-500 dark:text-gray-400 text-xs">{endpoint.description}</div>
                                      <div className="flex gap-1 mt-1">
                                        <Badge variant="outline" className="text-xs">MCP Endpoint</Badge>
                                        <Badge variant={endpoint.status === 'active' ? 'default' : 'secondary'} className="text-xs">
                                          {endpoint.status}
                                        </Badge>
                                        {endpoint.is_public && (
                                          <Badge variant="secondary" className="text-xs">Public</Badge>
                                        )}
                                        {endpoint.authentication_required && (
                                          <Badge variant="outline" className="text-xs">Auth Required</Badge>
                                        )}
                                      </div>
                                    </label>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {toolTemplates.length === 0 && toolInstances.length === 0 && mcpTools.length === 0 && mcpEndpoints.length === 0 && (
                            <div className="text-center py-8 text-gray-500">
                              <div className="text-sm">No tools or MCP integrations available</div>
                              <div className="text-xs mt-1">Create tool templates or set up MCP servers to add capabilities</div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Deployment Tab */}
            <TabsContent value="deployment" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Network & Infrastructure</CardTitle>
                  <CardDescription>Deployment and network configuration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        URL
                      </label>
                      <Input
                        value={formData.url}
                        onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                        placeholder="https://api.example.com/agent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        DNS Name
                      </label>
                      <Input
                        value={formData.dns_name}
                        onChange={(e) => setFormData(prev => ({ ...prev, dns_name: e.target.value }))}
                        placeholder="agent.example.com"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Health Check URL
                      </label>
                      <Input
                        value={formData.health_url}
                        onChange={(e) => setFormData(prev => ({ ...prev, health_url: e.target.value }))}
                        placeholder="https://api.example.com/health"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Environment
                      </label>
                      <select
                        value={formData.environment}
                        onChange={(e) => setFormData(prev => ({ ...prev, environment: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="development">Development</option>
                        <option value="staging">Staging</option>
                        <option value="production">Production</option>
                      </select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Signatures Tab */}
            <TabsContent value="signatures" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Input Signature</CardTitle>
                  <CardDescription>Define the expected input structure for this agent</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                      <Input
                        placeholder="Field name"
                        value={newInputField.name}
                        onChange={(e) => setNewInputField(prev => ({ ...prev, name: e.target.value }))}
                      />
                      <select
                        value={newInputField.type}
                        onChange={(e) => setNewInputField(prev => ({ ...prev, type: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="string">String</option>
                        <option value="number">Number</option>
                        <option value="boolean">Boolean</option>
                        <option value="object">Object</option>
                        <option value="array">Array</option>
                      </select>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="input-required"
                          checked={newInputField.required}
                          onChange={(e) => setNewInputField(prev => ({ ...prev, required: e.target.checked }))}
                          className="mr-2"
                        />
                        <label htmlFor="input-required" className="text-sm">Required</label>
                      </div>
                      <Button type="button" onClick={addInputField} size="sm">
                        <PlusIcon className="h-4 w-4" />
                      </Button>
                    </div>
                    <Input
                      placeholder="Field description"
                      value={newInputField.description}
                      onChange={(e) => setNewInputField(prev => ({ ...prev, description: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    {Object.entries(formData.input_signature || {}).map(([fieldName, fieldConfig]: [string, any]) => (
                      <div key={fieldName} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 border rounded">
                        <div>
                          <div className="font-medium">{fieldName}</div>
                          <div className="text-sm text-gray-500">
                            {fieldConfig.type} {fieldConfig.required && '(required)'}
                          </div>
                          {fieldConfig.description && (
                            <div className="text-xs text-gray-400 mt-1">{fieldConfig.description}</div>
                          )}
                        </div>
                        <Button
                          type="button"
                          variant="destructive"
                          size="sm"
                          onClick={() => removeInputField(fieldName)}
                        >
                          <TrashIcon className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Output Signature</CardTitle>
                  <CardDescription>Define the expected output structure for this agent</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                      <Input
                        placeholder="Field name"
                        value={newOutputField.name}
                        onChange={(e) => setNewOutputField(prev => ({ ...prev, name: e.target.value }))}
                      />
                      <select
                        value={newOutputField.type}
                        onChange={(e) => setNewOutputField(prev => ({ ...prev, type: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="string">String</option>
                        <option value="number">Number</option>
                        <option value="boolean">Boolean</option>
                        <option value="object">Object</option>
                        <option value="array">Array</option>
                      </select>
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          id="output-required"
                          checked={newOutputField.required}
                          onChange={(e) => setNewOutputField(prev => ({ ...prev, required: e.target.checked }))}
                          className="mr-2"
                        />
                        <label htmlFor="output-required" className="text-sm">Required</label>
                      </div>
                      <Button type="button" onClick={addOutputField} size="sm">
                        <PlusIcon className="h-4 w-4" />
                      </Button>
                    </div>
                    <Input
                      placeholder="Field description"
                      value={newOutputField.description}
                      onChange={(e) => setNewOutputField(prev => ({ ...prev, description: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    {Object.entries(formData.output_signature || {}).map(([fieldName, fieldConfig]: [string, any]) => (
                      <div key={fieldName} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 border rounded">
                        <div>
                          <div className="font-medium">{fieldName}</div>
                          <div className="text-sm text-gray-500">
                            {fieldConfig.type} {fieldConfig.required && '(required)'}
                          </div>
                          {fieldConfig.description && (
                            <div className="text-xs text-gray-400 mt-1">{fieldConfig.description}</div>
                          )}
                        </div>
                        <Button
                          type="button"
                          variant="destructive"
                          size="sm"
                          onClick={() => removeOutputField(fieldName)}
                        >
                          <TrashIcon className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Input Modes</CardTitle>
                    <CardDescription>Supported input formats</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex gap-2">
                      <Input
                        value={inputModeText}
                        onChange={(e) => setInputModeText(e.target.value)}
                        placeholder="e.g., text, image, audio"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInputMode())}
                      />
                      <Button type="button" onClick={addInputMode} variant="outline" size="sm">
                        Add
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData.default_input_modes || []).map((mode) => (
                        <Badge key={mode} variant="secondary" className="flex items-center gap-1">
                          {mode}
                          <button
                            type="button"
                            onClick={() => removeInputMode(mode)}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Output Modes</CardTitle>
                    <CardDescription>Supported output formats</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex gap-2">
                      <Input
                        value={outputModeText}
                        onChange={(e) => setOutputModeText(e.target.value)}
                        placeholder="e.g., text, json, structured"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addOutputMode())}
                      />
                      <Button type="button" onClick={addOutputMode} variant="outline" size="sm">
                        Add
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData.default_output_modes || []).map((mode) => (
                        <Badge key={mode} variant="secondary" className="flex items-center gap-1">
                          {mode}
                          <button
                            type="button"
                            onClick={() => removeOutputMode(mode)}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Metadata Tab */}
            <TabsContent value="metadata" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Tags & Classification</CardTitle>
                  <CardDescription>Organize and categorize this agent</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tags
                    </label>
                    <div className="flex gap-2 mb-2">
                      <Input
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        placeholder="Add a tag"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      />
                      <Button type="button" onClick={addTag} variant="outline">
                        Add
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData.tags || []).map((tag) => (
                        <Badge key={tag} variant="outline" className="flex items-center gap-1">
                          #{tag}
                          <button
                            type="button"
                            onClick={() => removeTag(tag)}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Project Tags
                    </label>
                    <div className="flex gap-2 mb-2">
                      <Input
                        value={newProjectTag}
                        onChange={(e) => setNewProjectTag(e.target.value)}
                        placeholder="Add a project tag"
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addProjectTag())}
                      />
                      <Button type="button" onClick={addProjectTag} variant="outline">
                        Add
                      </Button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(formData.project_tags || []).map((tag) => (
                        <Badge key={tag} variant="default" className="flex items-center gap-1">
                          {tag}
                          <button
                            type="button"
                            onClick={() => removeProjectTag(tag)}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Form Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit">
                {editingAgent ? 'Update Agent' : 'Create Agent'}
              </Button>
            </div>

          </form>
        </Tabs>
      </div>
    </div>
  );
}
