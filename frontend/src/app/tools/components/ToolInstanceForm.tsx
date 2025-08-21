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
  AlertCircle,
  Play,
  Eye,
  EyeOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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

interface ToolInstance {
  id?: string;
  template_id: string;
  name: string;
  description: string;
  configuration: Record<string, any>;
  runtime_config?: Record<string, any>;
  status: 'active' | 'inactive' | 'error' | 'running';
  metadata?: Record<string, any>;
  template?: ToolTemplate;
}

interface ToolInstanceFormProps {
  instance?: ToolInstance;
  templates: ToolTemplate[];
  onSave: (instance: ToolInstance) => void;
  onCancel: () => void;
}

const getTemplateTypeIcon = (templateType: string) => {
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

export default function ToolInstanceForm({ 
  instance, 
  templates,
  onSave, 
  onCancel 
}: ToolInstanceFormProps) {
  const [formData, setFormData] = useState<ToolInstance>({
    template_id: '',
    name: '',
    description: '',
    configuration: {},
    runtime_config: {},
    status: 'inactive',
    metadata: {}
  });

  const [selectedTemplate, setSelectedTemplate] = useState<ToolTemplate | null>(null);
  const [configurationJson, setConfigurationJson] = useState<string>('');
  const [runtimeConfigJson, setRuntimeConfigJson] = useState<string>('');
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [validationStatus, setValidationStatus] = useState<'idle' | 'validating' | 'valid' | 'invalid'>('idle');
  const [testResult, setTestResult] = useState<any>(null);

  useEffect(() => {
    if (instance) {
      setFormData(instance);
      setConfigurationJson(JSON.stringify(instance.configuration, null, 2));
      setRuntimeConfigJson(JSON.stringify(instance.runtime_config || {}, null, 2));
      
      if (instance.template_id) {
        const template = templates.find(t => t.id === instance.template_id);
        setSelectedTemplate(template || null);
      }
    }
  }, [instance, templates]);

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

  const handleTemplateSelection = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setSelectedTemplate(template);
      setFormData(prev => ({
        ...prev,
        template_id: templateId,
        configuration: { ...template.default_configuration }
      }));
      setConfigurationJson(JSON.stringify(template.default_configuration, null, 2));
    }
  };

  const validateConfiguration = async () => {
    setValidationStatus('validating');
    try {
      const config = JSON.parse(configurationJson);
      const runtimeConfig = runtimeConfigJson ? JSON.parse(runtimeConfigJson) : {};
      
      // Mock validation against schema
      if (selectedTemplate?.schema_definition) {
        // In real implementation, validate against JSON schema
        setTimeout(() => {
          setValidationStatus('valid');
          setFormData(prev => ({
            ...prev,
            configuration: config,
            runtime_config: runtimeConfig
          }));
        }, 1000);
      } else {
        setValidationStatus('valid');
        setFormData(prev => ({
          ...prev,
          configuration: config,
          runtime_config: runtimeConfig
        }));
      }
    } catch (err) {
      setValidationStatus('invalid');
      setErrors(prev => ({
        ...prev,
        configuration: 'Invalid JSON format'
      }));
    }
  };

  const testConfiguration = async () => {
    if (!selectedTemplate) return;
    
    try {
      const config = JSON.parse(configurationJson);
      // Mock test execution
      setTestResult({ status: 'testing' });
      
      setTimeout(() => {
        setTestResult({
          status: 'success',
          message: 'Configuration test passed successfully',
          details: {
            connection_test: 'passed',
            authentication: 'valid',
            performance: '< 100ms'
          }
        });
      }, 2000);
    } catch (err) {
      setTestResult({
        status: 'error',
        message: 'Configuration test failed',
        error: 'Invalid configuration format'
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.template_id) {
      newErrors.template_id = 'Template selection is required';
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Instance name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    try {
      JSON.parse(configurationJson);
    } catch (err) {
      newErrors.configuration = 'Invalid JSON format in configuration';
    }

    if (runtimeConfigJson) {
      try {
        JSON.parse(runtimeConfigJson);
      } catch (err) {
        newErrors.runtime_config = 'Invalid JSON format in runtime configuration';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        const finalInstance: ToolInstance = {
          ...formData,
          configuration: JSON.parse(configurationJson),
          runtime_config: runtimeConfigJson ? JSON.parse(runtimeConfigJson) : {}
        };
        onSave(finalInstance);
      } catch (err) {
        setErrors({ submit: 'Error preparing instance data' });
      }
    }
  };

  const renderConfigurationField = (key: string, value: any, path: string = '') => {
    const fieldPath = path ? `${path}.${key}` : key;
    const isSecret = key.toLowerCase().includes('password') || 
                    key.toLowerCase().includes('secret') || 
                    key.toLowerCase().includes('token') ||
                    key.toLowerCase().includes('key');

    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      return (
        <div key={fieldPath} className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </label>
          <div className="pl-4 border-l-2 border-gray-200 dark:border-gray-700 space-y-2">
            {Object.entries(value).map(([subKey, subValue]) => 
              renderConfigurationField(subKey, subValue, fieldPath)
            )}
          </div>
        </div>
      );
    }

    return (
      <div key={fieldPath} className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          {isSecret && (
            <Badge variant="secondary" className="ml-2 text-xs">
              Secret
            </Badge>
          )}
        </label>
        <div className="relative">
          <input
            type={isSecret && !showSecrets[fieldPath] ? 'password' : 'text'}
            value={String(value)}
            onChange={(e) => {
              const newConfig = { ...JSON.parse(configurationJson) };
              const keys = fieldPath.split('.');
              let current = newConfig;
              for (let i = 0; i < keys.length - 1; i++) {
                current = current[keys[i]];
              }
              current[keys[keys.length - 1]] = e.target.value;
              setConfigurationJson(JSON.stringify(newConfig, null, 2));
            }}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          {isSecret && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-2 top-1/2 transform -translate-y-1/2"
              onClick={() => setShowSecrets(prev => ({ ...prev, [fieldPath]: !prev[fieldPath] }))}
            >
              {showSecrets[fieldPath] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          )}
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          {instance ? 'Edit Tool Instance' : 'Create Tool Instance'}
        </h2>
        <Button variant="ghost" onClick={onCancel}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Content */}
      <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 140px)' }}>
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Template Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
              Select Template <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.filter(t => t.is_active).map((template) => (
                <Card 
                  key={template.id}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    formData.template_id === template.id 
                      ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                      : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}
                  onClick={() => handleTemplateSelection(template.id!)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
                        {getTemplateTypeIcon(template.template_type)}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{template.name}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {template.description}
                        </p>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline">{template.template_type}</Badge>
                          <Badge variant="secondary">v{template.version}</Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            {errors.template_id && <p className="text-red-500 text-sm mt-1">{errors.template_id}</p>}
          </div>

          {selectedTemplate && (
            <>
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Instance Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="e.g., production-rag-instance"
                  />
                  {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
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
                    <option value="inactive">Inactive</option>
                    <option value="active">Active</option>
                    <option value="error">Error</option>
                    <option value="running">Running</option>
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
                  placeholder="Describe this tool instance and its specific use case..."
                />
                {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
              </div>

              {/* Configuration Tabs */}
              <Tabs defaultValue="visual" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="visual">Visual Configuration</TabsTrigger>
                  <TabsTrigger value="json">JSON Configuration</TabsTrigger>
                  <TabsTrigger value="runtime">Runtime Config</TabsTrigger>
                </TabsList>

                <TabsContent value="visual" className="space-y-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-blue-900 dark:text-blue-100">
                          Template: {selectedTemplate.name}
                        </h4>
                        <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                          Configure the specific settings for this instance based on the template defaults.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Object.entries(JSON.parse(configurationJson)).map(([key, value]) => 
                      renderConfigurationField(key, value)
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="json" className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Instance Configuration <span className="text-red-500">*</span>
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
                      <Button
                        type="button"
                        size="sm"
                        onClick={testConfiguration}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Test
                      </Button>
                    </div>
                  </div>

                  <textarea
                    value={configurationJson}
                    onChange={(e) => setConfigurationJson(e.target.value)}
                    rows={15}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                    placeholder="Enter JSON configuration..."
                  />
                  {errors.configuration && <p className="text-red-500 text-sm mt-1">{errors.configuration}</p>}

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
                        <div>
                          <h4 className="font-medium">
                            {testResult.status === 'testing' ? 'Testing Configuration...' : 
                             testResult.status === 'success' ? 'Test Successful' : 'Test Failed'}
                          </h4>
                          <p className="text-sm mt-1">{testResult.message}</p>
                          {testResult.details && (
                            <div className="mt-2 text-sm">
                              {Object.entries(testResult.details).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span>{key.replace(/_/g, ' ')}:</span>
                                  <span className="font-mono">{String(value)}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="runtime" className="space-y-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Runtime Configuration (Optional)
                  </label>
                  <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Runtime configuration includes settings that can be changed during execution,
                      such as timeouts, retry policies, and environment-specific variables.
                    </p>
                  </div>
                  <textarea
                    value={runtimeConfigJson}
                    onChange={(e) => setRuntimeConfigJson(e.target.value)}
                    rows={10}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
                    placeholder='Enter runtime configuration...\n\nExample:\n{\n  "timeout": 30,\n  "retry_attempts": 3,\n  "debug_mode": false,\n  "environment": "production"\n}'
                  />
                  {errors.runtime_config && <p className="text-red-500 text-sm mt-1">{errors.runtime_config}</p>}
                </TabsContent>
              </Tabs>
            </>
          )}

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
        <Button onClick={handleSubmit} disabled={!selectedTemplate}>
          <Save className="h-4 w-4 mr-2" />
          Save Instance
        </Button>
      </div>
    </>
  );
}
