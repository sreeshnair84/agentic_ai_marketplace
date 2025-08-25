'use client';

import { useState, useEffect } from 'react';
import { useLLMModels } from '@/hooks/useLLMModels';
import { 
  X,  
  Save, 
  Settings,
  Code,
  Database,
  Globe,
  FileText,
  Cloud,
  Workflow,
  Zap,
  Info,
  CheckCircle,
  AlertCircle,
  Server,
  Tag,
  Plus,
  Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

interface ToolTemplate {
  id?: string;
  name: string;
  display_name: string;
  type: 'rag' | 'sql_agent' | 'mcp' | 'code_interpreter' | 'web_scraper' | 'file_processor' | 'api_integration' | 'custom';
  description: string;
  category: string;
  version: string;
  default_config: Record<string, any>;
  schema_definition: Record<string, any>;
  icon?: string;
  tags?: string[];
  project_tags?: string[];
  status: 'active' | 'inactive' | 'draft' | 'archived';
  capabilities?: string[];
  documentation?: string;
  // Deployment fields
  dns_name?: string;
  health_url?: string;
  execution_count?: number;
  success_rate?: number;
  // MCP Integration fields
  mcp_server_id?: string;
  mcp_tool_name?: string;
  mcp_binding_config?: Record<string, any>;
  is_mcp_tool?: boolean;
  // Signature fields
  input_signature?: Record<string, any>;
  output_signature?: Record<string, any>;
  default_input_modes?: string[];
  default_output_modes?: string[];
}

interface ToolTemplateFormProps {
  template?: ToolTemplate;
  onSave: (template: ToolTemplate) => void;
  onCancel: () => void;
}

const toolTemplateTypes = [
  {
    value: 'rag',
    label: 'RAG Tool',
    description: 'Retrieval-Augmented Generation with configurable embeddings and vector stores',
    icon: <Database className="h-5 w-5" />,
    color: 'bg-blue-100 text-blue-800',
    category: 'AI/ML',
    defaultConfig: {
      vector_database: {
        provider: 'pgvector',
        connection_string: '',
        collection_name: 'documents'
      },
      embedding_model_id: '',
      chunk_size: 1000,
      chunk_overlap: 200,
      retrieval_k: 5
    }
  },
  {
    value: 'sql_agent',
    label: 'SQL Agent',
    description: 'Intelligent database query generation and execution with schema awareness',
    icon: <Database className="h-5 w-5" />,
    color: 'bg-green-100 text-green-800',
    category: 'Data',
    defaultConfig: {
      connection_string: '',
      database_type: 'postgresql',
      schema_info: {},
      query_timeout: 30,
      max_rows: 1000
    }
  },
  {
    value: 'mcp',
    label: 'MCP Tool',
    description: 'Model Context Protocol integration for external tool connectivity',
    icon: <Zap className="h-5 w-5" />,
    color: 'bg-yellow-100 text-yellow-800',
    category: 'Integration',
    defaultConfig: {
      server_url: '',
      capabilities: [],
      timeout: 30,
      retry_attempts: 3
    }
  },
  {
    value: 'code_interpreter',
    label: 'Code Interpreter',
    description: 'Multi-language code execution with sandbox security',
    icon: <Code className="h-5 w-5" />,
    color: 'bg-purple-100 text-purple-800',
    category: 'Utilities',
    defaultConfig: {
      language: 'python',
      timeout: 30,
      sandbox_enabled: true,
      allowed_imports: []
    }
  },
  {
    value: 'web_scraper',
    label: 'Web Scraper',
    description: 'Configurable web content extraction with rate limiting',
    icon: <Globe className="h-5 w-5" />,
    color: 'bg-cyan-100 text-cyan-800',
    category: 'Data',
    defaultConfig: {
      user_agent: 'Enterprise AI Bot',
      timeout: 10,
      respect_robots: true,
      rate_limit: 1
    }
  },
  {
    value: 'file_processor',
    label: 'File Processor',
    description: 'Multi-format document processing and text extraction',
    icon: <FileText className="h-5 w-5" />,
    color: 'bg-orange-100 text-orange-800',
    category: 'Utilities',
    defaultConfig: {
      supported_formats: ['pdf', 'docx', 'txt', 'csv'],
      max_file_size: 10485760,
      extract_metadata: true
    }
  },
  {
    value: 'api_integration',
    label: 'API Integration',
    description: 'REST and GraphQL API connectivity with authentication',
    icon: <Cloud className="h-5 w-5" />,
    color: 'bg-indigo-100 text-indigo-800',
    category: 'Integration',
    defaultConfig: {
      base_url: '',
      auth_method: 'none',
      timeout: 30,
      retry_policy: 'exponential'
    }
  },
  {
    value: 'custom',
    label: 'Custom Tool',
    description: 'Custom tool implementation with flexible configuration',
    icon: <Workflow className="h-5 w-5" />,
    color: 'bg-red-100 text-red-800',
    category: 'Custom',
    defaultConfig: {
      custom_configuration: {},
      timeout: 30,
      retry_attempts: 3
    }
  }
];

export default function ToolTemplateForm({ 
  template, 
  onSave, 
  onCancel 
}: ToolTemplateFormProps) {
  const [formData, setFormData] = useState<ToolTemplate>({
    name: '',
    display_name: '',
    type: 'rag',
    description: '',
    category: 'AI/ML',
    version: '1.0.0',
    default_config: {},
    schema_definition: {},
    tags: [],
    project_tags: [],
    status: 'active',
    capabilities: [],
    documentation: '',
    // Deployment fields
    dns_name: '',
    health_url: '',
    execution_count: 0,
    success_rate: 0,
    // MCP Integration
    mcp_server_id: '',
    mcp_tool_name: '',
    mcp_binding_config: {},
    is_mcp_tool: false,
    // Signatures
    input_signature: {},
    output_signature: {},
    default_input_modes: ['text'],
    default_output_modes: ['text']
  });

  const [selectedTemplateType, setSelectedTemplateType] = useState<string>('rag');
  const { models: llmModels, loading: llmLoading } = useLLMModels();
  const [configurationJson, setConfigurationJson] = useState<string>('');
  const [schemaJson, setSchemaJson] = useState<string>('');
  const [codeTemplate, setCodeTemplate] = useState<string>('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validationStatus, setValidationStatus] = useState<'idle' | 'validating' | 'valid' | 'invalid'>('idle');
  // Additional state for new fields
  const [newCapability, setNewCapability] = useState('');
  const [newProjectTag, setNewProjectTag] = useState('');
  const [newInputField, setNewInputField] = useState({ name: '', type: 'string', required: false, description: '' });
  const [newOutputField, setNewOutputField] = useState({ name: '', type: 'string', required: false, description: '' });
  const [inputModeText, setInputModeText] = useState('');
  const [outputModeText, setOutputModeText] = useState('');

  useEffect(() => {
    if (template) {
      setFormData(template);
      setSelectedTemplateType(template.type);
      setConfigurationJson(JSON.stringify(template.default_config, null, 2));
      setSchemaJson(JSON.stringify(template.schema_definition, null, 2));
      setCodeTemplate(template.documentation || '');
    } else {
      // Set default configuration when template type changes
      const templateType = toolTemplateTypes.find(t => t.value === selectedTemplateType);
      if (templateType) {
        const newFormData = {
          ...formData,
          type: selectedTemplateType as any,
          category: templateType.category,
          default_config: templateType.defaultConfig
        };
        setFormData(newFormData);
        setConfigurationJson(JSON.stringify(templateType.defaultConfig, null, 2));
      }
    }
  }, [template, selectedTemplateType]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleTemplateTypeChange = (templateType: string) => {
    setSelectedTemplateType(templateType);
    const typeConfig = toolTemplateTypes.find(t => t.value === templateType);
    if (typeConfig) {
      setFormData(prev => ({
        ...prev,
        type: templateType as any,
        category: typeConfig.category,
        default_config: typeConfig.defaultConfig
      }));
      setConfigurationJson(JSON.stringify(typeConfig.defaultConfig, null, 2));
    }
  };

  const validateConfiguration = async () => {
    setValidationStatus('validating');
    try {
      const config = JSON.parse(configurationJson);
      const schema = schemaJson ? JSON.parse(schemaJson) : {};
      
      // Mock validation - in real implementation, call backend validation
      setTimeout(() => {
        setValidationStatus('valid');
        setFormData(prev => ({
          ...prev,
          default_config: config,
          schema_definition: schema
        }));
      }, 1000);
    } catch (err) {
      setValidationStatus('invalid');
      setErrors(prev => ({
        ...prev,
        configuration: 'Invalid JSON format'
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.display_name.trim()) {
      newErrors.display_name = 'Display name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    try {
      JSON.parse(configurationJson);
    } catch (err) {
      newErrors.configuration = 'Invalid JSON format in configuration';
    }

    if (schemaJson) {
      try {
        JSON.parse(schemaJson);
      } catch (err) {
        newErrors.schema = 'Invalid JSON format in schema';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        const finalTemplate: ToolTemplate = {
          ...formData,
          default_config: JSON.parse(configurationJson),
          schema_definition: schemaJson ? JSON.parse(schemaJson) : {},
          documentation: codeTemplate || undefined
        };
        onSave(finalTemplate);
      } catch (err) {
        setErrors({ submit: 'Error preparing template data' });
      }
    }
  };

  const currentTemplateType = toolTemplateTypes.find(t => t.value === selectedTemplateType);

  // Helper functions for managing arrays
  const addCapability = () => {
    if (newCapability.trim() && !(formData.capabilities || []).includes(newCapability.trim())) {
      setFormData(prev => ({
        ...prev,
        capabilities: [...(prev.capabilities || []), newCapability.trim()]
      }));
      setNewCapability('');
    }
  };

  const removeCapability = (capability: string) => {
    setFormData(prev => ({
      ...prev,
      capabilities: (prev.capabilities || []).filter(c => c !== capability)
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
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[95vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {template ? 'Edit Tool Template' : 'Create Enhanced Tool Template'}
          </h2>
          <Button variant="ghost" onClick={onCancel}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(95vh - 140px)' }}>
        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="basic" className="flex items-center gap-2">
              <Info className="h-4 w-4" />
              Basic Info
            </TabsTrigger>
            <TabsTrigger value="configuration" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Configuration
            </TabsTrigger>
            <TabsTrigger value="deployment" className="flex items-center gap-2">
              <Server className="h-4 w-4" />
              Deployment
            </TabsTrigger>
            <TabsTrigger value="signatures" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Signatures
            </TabsTrigger>
            <TabsTrigger value="metadata" className="flex items-center gap-2">
              <Tag className="h-4 w-4" />
              Metadata
            </TabsTrigger>
          </TabsList>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information Tab */}
          <TabsContent value="basic" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Template Type Selection</CardTitle>
                <CardDescription>Choose the type of tool template to create</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {toolTemplateTypes.map((type) => (
                    <Card 
                      key={type.value}
                      className={`cursor-pointer transition-all hover:shadow-md ${
                        selectedTemplateType === type.value 
                          ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => handleTemplateTypeChange(type.value)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className={`p-2 rounded-lg ${type.color}`}>
                            {type.icon}
                          </div>
                          <div>
                            <h4 className="font-medium text-sm">{type.label}</h4>
                          </div>
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {type.description}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
                <CardDescription>Core template identification and description</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Template Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="e.g., advanced-rag-tool"
                    />
                    {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Display Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.display_name}
                      onChange={(e) => handleInputChange('display_name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="Advanced RAG Tool"
                    />
                    {errors.display_name && <p className="text-red-500 text-sm mt-1">{errors.display_name}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Category
                    </label>
                    <select
                      value={formData.category}
                      onChange={(e) => handleInputChange('category', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      <option value="AI/ML">AI/ML</option>
                      <option value="Data">Data</option>
                      <option value="Integration">Integration</option>
                      <option value="Custom">Custom</option>
                      <option value="Utilities">Utilities</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Version
                    </label>
                    <input
                      type="text"
                      value={formData.version}
                      onChange={(e) => handleInputChange('version', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="1.0.0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => handleInputChange('status', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      <option value="active">Active</option>
                      <option value="draft">Draft</option>
                      <option value="inactive">Inactive</option>
                      <option value="archived">Archived</option>
                    </select>
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
                    placeholder="Describe what this tool template does and its capabilities..."
                  />
                  {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Configuration Tab */}
          <TabsContent value="configuration" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Tool Configuration</CardTitle>
                <CardDescription>Configure the tool-specific settings and behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* RAG Specific Configuration */}
                {selectedTemplateType === 'rag' && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-4">RAG Configuration</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Default Embedding Model
                        </label>
                        <select
                          value={formData.default_config?.embedding_model_id || ''}
                          onChange={(e) => {
                            const newConfig = {
                              ...formData.default_config,
                              embedding_model_id: e.target.value
                            };
                            handleInputChange('default_config', newConfig);
                            setConfigurationJson(JSON.stringify(newConfig, null, 2));
                          }}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                          <option value="">Select Embedding Model</option>
                          {!llmLoading && llmModels && Array.isArray(llmModels) && llmModels
                            .filter(model => model.model_type === 'embedding')
                            .map((model) => (
                              <option key={model.id} value={model.id}>
                                {model.display_name || model.name} ({model.provider})
                              </option>
                            ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Vector Database Provider
                        </label>
                        <select
                          value={formData.default_config?.vector_database?.provider || 'pgvector'}
                          onChange={(e) => {
                            const newConfig = {
                              ...formData.default_config,
                              vector_database: {
                                ...formData.default_config?.vector_database,
                                provider: e.target.value
                              }
                            };
                            handleInputChange('default_config', newConfig);
                            setConfigurationJson(JSON.stringify(newConfig, null, 2));
                          }}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                          <option value="pgvector">PgVector (PostgreSQL)</option>
                          <option value="chroma">Chroma</option>
                          <option value="pinecone">Pinecone</option>
                          <option value="weaviate">Weaviate</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_mcp_tool"
                    checked={formData.is_mcp_tool}
                    onChange={(e) => handleInputChange('is_mcp_tool', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="is_mcp_tool" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    MCP Tool (Model Context Protocol integration)
                  </label>
                </div>

                {/* Configuration Tabs */}
                <Tabs defaultValue="configuration" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="configuration">Configuration</TabsTrigger>
                    <TabsTrigger value="schema">Schema Definition</TabsTrigger>
                    <TabsTrigger value="code">Code Template</TabsTrigger>
                  </TabsList>

                  <TabsContent value="configuration" className="space-y-4">
                    <div className="flex items-center justify-between">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Default Configuration <span className="text-red-500">*</span>
                      </label>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={validateConfiguration}
                          disabled={validationStatus === 'validating'}
                          className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                        >
                          {validationStatus === 'validating' ? (
                            <>
                              <Settings className="h-4 w-4 animate-spin inline mr-2" />
                              Validating...
                            </>
                          ) : validationStatus === 'valid' ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-600 inline mr-2" />
                              Valid
                            </>
                          ) : validationStatus === 'invalid' ? (
                            <>
                              <AlertCircle className="h-4 w-4 text-red-600 inline mr-2" />
                              Invalid
                            </>
                          ) : (
                            'Validate'
                          )}
                        </button>
                      </div>
                    </div>
                    
                    {currentTemplateType && (
                      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
                        <div className="flex items-start space-x-3">
                          <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                          <div>
                            <h4 className="font-medium text-blue-900 dark:text-blue-100">
                              {currentTemplateType.label} Configuration
                            </h4>
                            <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                              {currentTemplateType.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    <textarea
                      value={configurationJson}
                      onChange={(e) => setConfigurationJson(e.target.value)}
                      rows={15}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                      placeholder="Enter JSON configuration..."
                    />
                    {errors.configuration && <p className="text-red-500 text-sm mt-1">{errors.configuration}</p>}
                  </TabsContent>

                  <TabsContent value="schema" className="space-y-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Schema Definition (Optional)
                    </label>
                    <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Define the JSON schema for validating instance configurations. This helps ensure
                        instances created from this template have valid configurations.
                      </p>
                    </div>
                    <textarea
                      value={schemaJson}
                      onChange={(e) => setSchemaJson(e.target.value)}
                      rows={15}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                      placeholder='Enter JSON schema definition...\n\nExample:\n{\n  "type": "object",\n  "properties": {\n    "embedding_model": {\n      "type": "string",\n      "enum": ["text-embedding-ada-002", "text-embedding-3-small"]\n    }\n  },\n  "required": ["embedding_model"]\n}'
                    />
                    {errors.schema && <p className="text-red-500 text-sm mt-1">{errors.schema}</p>}
                  </TabsContent>

                  <TabsContent value="code" className="space-y-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Documentation (Optional)
                    </label>
                    <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Provide documentation and usage instructions for this tool template.
                        This will help users understand how to configure and use instances.
                      </p>
                    </div>
                    <textarea
                      value={codeTemplate}
                      onChange={(e) => setCodeTemplate(e.target.value)}
                      rows={15}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                      placeholder="Enter documentation and usage instructions...\n\nExample:\n# RAG Tool Template\n\nThis template creates a RAG (Retrieval-Augmented Generation) tool that can:\n- Index documents into a vector database\n- Perform semantic search\n- Generate responses using retrieved context\n\n## Configuration\n- embedding_model_id: The LLM model to use for embeddings\n- vector_database: Database configuration for storing vectors\n- chunk_size: Size of document chunks\n- retrieval_k: Number of documents to retrieve"
                    />
                  </TabsContent>
                </Tabs>
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
                      DNS Name
                    </label>
                    <input
                      type="text"
                      value={formData.dns_name}
                      onChange={(e) => handleInputChange('dns_name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="tool.example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Health Check URL
                    </label>
                    <input
                      type="text"
                      value={formData.health_url}
                      onChange={(e) => handleInputChange('health_url', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="https://api.example.com/health"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>MCP Integration</CardTitle>
                <CardDescription>Model Context Protocol configuration</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      MCP Server ID
                    </label>
                    <input
                      type="text"
                      value={formData.mcp_server_id}
                      onChange={(e) => handleInputChange('mcp_server_id', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="MCP server identifier"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      MCP Tool Name
                    </label>
                    <input
                      type="text"
                      value={formData.mcp_tool_name}
                      onChange={(e) => handleInputChange('mcp_tool_name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="MCP tool name"
                    />
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
                <CardDescription>Define the expected input structure for this tool</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                    <input
                      placeholder="Field name"
                      value={newInputField.name}
                      onChange={(e) => setNewInputField(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
                    <button
                      type="button"
                      onClick={addInputField}
                      className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <input
                    placeholder="Field description"
                    value={newInputField.description}
                    onChange={(e) => setNewInputField(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
                      <button
                        type="button"
                        onClick={() => removeInputField(fieldName)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Output Signature</CardTitle>
                <CardDescription>Define the expected output structure for this tool</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
                    <input
                      placeholder="Field name"
                      value={newOutputField.name}
                      onChange={(e) => setNewOutputField(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
                    <button
                      type="button"
                      onClick={addOutputField}
                      className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <input
                    placeholder="Field description"
                    value={newOutputField.description}
                    onChange={(e) => setNewOutputField(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
                      <button
                        type="button"
                        onClick={() => removeOutputField(fieldName)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
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
                    <input
                      value={inputModeText}
                      onChange={(e) => setInputModeText(e.target.value)}
                      placeholder="e.g., text, image, audio"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInputMode())}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                    <button type="button" onClick={addInputMode} className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                      Add
                    </button>
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
                    <input
                      value={outputModeText}
                      onChange={(e) => setOutputModeText(e.target.value)}
                      placeholder="e.g., text, json, structured"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addOutputMode())}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                    <button type="button" onClick={addOutputMode} className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                      Add
                    </button>
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
                <CardTitle>Capabilities & Tags</CardTitle>
                <CardDescription>Define tool capabilities and organize with tags</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Capabilities
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      value={newCapability}
                      onChange={(e) => setNewCapability(e.target.value)}
                      placeholder="Add a capability"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCapability())}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                    <button type="button" onClick={addCapability} className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                      Add
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(formData.capabilities || []).map((capability) => (
                      <Badge key={capability} variant="secondary" className="flex items-center gap-1">
                        {capability}
                        <button
                          type="button"
                          onClick={() => removeCapability(capability)}
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
                    Tags
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      value={formData.tags?.join(', ') || ''}
                      onChange={(e) => handleInputChange('tags', e.target.value.split(',').map(t => t.trim()).filter(Boolean))}
                      placeholder="tag1, tag2, tag3"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(formData.tags || []).map((tag) => (
                      <Badge key={tag} variant="outline" className="flex items-center gap-1">
                        #{tag}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Project Tags
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      value={newProjectTag}
                      onChange={(e) => setNewProjectTag(e.target.value)}
                      placeholder="Add a project tag"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addProjectTag())}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                    <button type="button" onClick={addProjectTag} className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                      Add
                    </button>
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

          {errors.submit && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200">{errors.submit}</p>
            </div>
          )}
        </form>
        </Tabs>
        </div>
        
        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>
            <Save className="h-4 w-4 mr-2" />
            Save Template
          </Button>
        </div>
      </div>
    </div>
  );
}
