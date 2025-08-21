'use client';

import { useState, useEffect } from 'react';
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
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';

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
}

interface ToolTemplateFormProps {
  template?: ToolTemplate;
  onSave: (template: ToolTemplate) => void;
  onCancel: () => void;
}

const toolTemplateTypes = [
  {
    value: 'rag_pipeline',
    label: 'RAG Pipeline',
    description: 'Retrieval-Augmented Generation with configurable embeddings and vector stores',
    icon: <Database className="h-5 w-5" />,
    color: 'bg-blue-100 text-blue-800',
    defaultConfig: {
      vector_store: {
        type: 'pgvector',
        connection_string: '',
        collection_name: 'documents'
      },
      embedding_model: 'text-embedding-ada-002',
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
    defaultConfig: {
      connection_string: '',
      database_type: 'postgresql',
      schema_info: {},
      query_timeout: 30,
      max_rows: 1000
    }
  },
  {
    value: 'mcp_client',
    label: 'MCP Client',
    description: 'Model Context Protocol integration for external tool connectivity',
    icon: <Zap className="h-5 w-5" />,
    color: 'bg-yellow-100 text-yellow-800',
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
    defaultConfig: {
      base_url: '',
      auth_method: 'none',
      timeout: 30,
      retry_policy: 'exponential'
    }
  },
  {
    value: 'workflow_orchestrator',
    label: 'Workflow Orchestrator',
    description: 'Complex multi-step workflows with conditional logic',
    icon: <Workflow className="h-5 w-5" />,
    color: 'bg-red-100 text-red-800',
    defaultConfig: {
      workflow_definition: {},
      parallel_execution: true,
      error_handling: 'continue'
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
    description: '',
    template_type: 'rag_pipeline',
    version: '1.0.0',
    default_configuration: {},
    schema_definition: {},
    metadata: {},
    is_active: true
  });

  const [selectedTemplateType, setSelectedTemplateType] = useState<string>('rag_pipeline');
  const [configurationJson, setConfigurationJson] = useState<string>('');
  const [schemaJson, setSchemaJson] = useState<string>('');
  const [codeTemplate, setCodeTemplate] = useState<string>('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validationStatus, setValidationStatus] = useState<'idle' | 'validating' | 'valid' | 'invalid'>('idle');

  useEffect(() => {
    if (template) {
      setFormData(template);
      setSelectedTemplateType(template.template_type);
      setConfigurationJson(JSON.stringify(template.default_configuration, null, 2));
      setSchemaJson(JSON.stringify(template.schema_definition, null, 2));
      setCodeTemplate(template.code_template || '');
    } else {
      // Set default configuration when template type changes
      const templateType = toolTemplateTypes.find(t => t.value === selectedTemplateType);
      if (templateType) {
        const newFormData = {
          ...formData,
          template_type: selectedTemplateType as any,
          default_configuration: templateType.defaultConfig
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
        template_type: templateType as any,
        default_configuration: typeConfig.defaultConfig
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
          default_configuration: config,
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
          default_configuration: JSON.parse(configurationJson),
          schema_definition: schemaJson ? JSON.parse(schemaJson) : {},
          code_template: codeTemplate || undefined
        };
        onSave(finalTemplate);
      } catch (err) {
        setErrors({ submit: 'Error preparing template data' });
      }
    }
  };

  const currentTemplateType = toolTemplateTypes.find(t => t.value === selectedTemplateType);

  return (
    <>
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
      <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 140px)' }}>
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Template Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
              Template Type <span className="text-red-500">*</span>
            </label>
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
          </div>

          {/* Basic Information */}
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
                placeholder="e.g., advanced-rag-pipeline"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
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

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => handleInputChange('is_active', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              Active Template (available for creating instances)
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
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={validateConfiguration}
                    disabled={validationStatus === 'validating'}
                  >
                    {validationStatus === 'validating' ? (
                      <>
                        <Settings className="h-4 w-4 animate-spin mr-2" />
                        Validating...
                      </>
                    ) : validationStatus === 'valid' ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                        Valid
                      </>
                    ) : validationStatus === 'invalid' ? (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
                        Invalid
                      </>
                    ) : (
                      'Validate'
                    )}
                  </Button>
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
                Code Template (Optional)
              </label>
              <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Provide a code template that will be used when creating instances. This can include
                  placeholder variables that will be replaced with actual configuration values.
                </p>
              </div>
              <textarea
                value={codeTemplate}
                onChange={(e) => setCodeTemplate(e.target.value)}
                rows={15}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                placeholder={`Enter code template...\n\nExample for RAG Pipeline:\nfrom langchain.embeddings import OpenAIEmbeddings\nfrom langchain.vectorstores import PGVector\n\nembeddings = OpenAIEmbeddings(model="{{embedding_model}}")\nvector_store = PGVector(\n    connection_string="{{vector_store.connection_string}}",\n    collection_name="{{vector_store.collection_name}}",\n    embedding_function=embeddings\n)`}
              />
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
      <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button onClick={handleSubmit}>
          <Save className="h-4 w-4 mr-2" />
          Save Template
        </Button>
      </div>
    </>
  );
}
