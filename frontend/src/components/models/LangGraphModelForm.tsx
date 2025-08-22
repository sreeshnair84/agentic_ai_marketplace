'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
  Zap, 
  Settings, 
  DollarSign, 
  Activity, 
  Eye, 
  EyeOff, 
  AlertTriangle,
  CheckCircle,
  Loader2,
  Star
} from 'lucide-react';

interface ModelCapabilities {
  max_tokens?: number;
  supports_streaming?: boolean;
  supports_function_calling?: boolean;
  input_modalities?: string[];
  output_modalities?: string[];
  dimensions?: number;
  max_input_tokens?: number;
  supports_batching?: boolean;
  supported_languages?: string[];
}

interface PricingInfo {
  input_cost_per_token?: number;
  output_cost_per_token?: number;
  cost_per_token?: number;
  currency?: string;
}

interface PerformanceMetrics {
  avg_latency?: number;
  tokens_per_second?: number;
  throughput?: number;
  availability?: number;
}

interface ModelConfig {
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop_sequences?: string[];
  dimensions?: number;
  batch_size?: number;
  normalize?: boolean;
}

interface LangGraphModelFormProps {
  model?: any;
  modelType: 'llm' | 'embedding';
  onSave: (modelData: any) => Promise<void>;
  onCancel: () => void;
  onTest?: (modelData: any) => Promise<boolean>;
  onSetDefault?: (modelId: string) => Promise<boolean>;
}

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'azure_openai', label: 'Azure OpenAI' },
  { value: 'google_gemini', label: 'Google Gemini' },
  { value: 'ollama', label: 'Ollama' }
];

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active', color: 'bg-green-100 text-green-800' },
  { value: 'inactive', label: 'Inactive', color: 'bg-gray-100 text-gray-800' },
  { value: 'testing', label: 'Testing', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'error', label: 'Error', color: 'bg-red-100 text-red-800' }
];

const LangGraphModelForm: React.FC<LangGraphModelFormProps> = ({
  model,
  modelType,
  onSave,
  onCancel,
  onTest,
  onSetDefault
}) => {
  const [formData, setFormData] = useState({
    name: model?.name || '',
    display_name: model?.display_name || '',
    provider: model?.provider || 'openai',
    api_endpoint: model?.api_endpoint || '',
    api_key: model?.api_key || '',
    status: model?.status || 'inactive',
    health_url: model?.health_url || '',
    dns_name: model?.dns_name || '',
    capabilities: model?.capabilities || {},
    pricing_info: model?.pricing_info || {},
    performance_metrics: model?.performance_metrics || {},
    model_config: model?.model_config || {}
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isTestLoading, setIsTestLoading] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [activeTab, setActiveTab] = useState('basic');
  const [templates, setTemplates] = useState<any>({});

  useEffect(() => {
    // Load configuration templates
    loadConfigurationTemplates();
  }, [formData.provider]);

  const loadConfigurationTemplates = async () => {
    try {
      const endpoint = `/api/v1/models/templates/configuration?provider=${formData.provider}&model_type=${modelType}`;
      const response = await fetch(endpoint);
      if (response.ok) {
        const data = await response.json();
        if (data.template) {
          setTemplates({ [formData.provider]: data.template });
        }
      }
    } catch (error) {
      console.error('Failed to load configuration templates:', error);
    }
  };

  const applyTemplate = () => {
    const template = templates[formData.provider];
    if (template) {
      setFormData(prev => ({
        ...prev,
        name: template.name || prev.name,
        display_name: template.display_name || prev.display_name,
        api_endpoint: template.api_endpoint || prev.api_endpoint,
        capabilities: { ...template.capabilities, ...prev.capabilities },
        pricing_info: { ...template.pricing_info, ...prev.pricing_info },
        model_config: { ...template.model_config, ...prev.model_config }
      }));
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setTestResult(null); // Clear test result when form changes
  };

  const handleNestedChange = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev] as object,
        [field]: value
      }
    }));
    setTestResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await onSave({
        ...formData,
        model_type: modelType
      });
    } catch (error) {
      console.error('Failed to save model:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTest = async () => {
    if (!onTest) return;
    
    setIsTestLoading(true);
    setTestResult(null);
    
    try {
      const success = await onTest(formData);
      setTestResult({
        success,
        message: success ? 'Model test successful!' : 'Model test failed'
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: `Test failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      setIsTestLoading(false);
    }
  };

  const handleSetDefault = async () => {
    if (!onSetDefault || !model?.id) return;
    
    try {
      await onSetDefault(model.id);
    } catch (error) {
      console.error('Failed to set default model:', error);
    }
  };

  const renderCapabilitiesForm = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {modelType === 'llm' ? (
        <>
          <div>
            <Label htmlFor="max_tokens">Max Tokens</Label>
            <Input
              id="max_tokens"
              type="number"
              value={formData.capabilities.max_tokens || ''}
              onChange={(e) => handleNestedChange('capabilities', 'max_tokens', parseInt(e.target.value) || 0)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="supports_streaming"
              checked={formData.capabilities.supports_streaming || false}
              onCheckedChange={(checked) => handleNestedChange('capabilities', 'supports_streaming', checked)}
            />
            <Label htmlFor="supports_streaming">Supports Streaming</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="supports_function_calling"
              checked={formData.capabilities.supports_function_calling || false}
              onCheckedChange={(checked) => handleNestedChange('capabilities', 'supports_function_calling', checked)}
            />
            <Label htmlFor="supports_function_calling">Supports Function Calling</Label>
          </div>
          <div>
            <Label htmlFor="input_modalities">Input Modalities (comma-separated)</Label>
            <Input
              id="input_modalities"
              value={formData.capabilities.input_modalities?.join(', ') || 'text'}
              onChange={(e) => handleNestedChange('capabilities', 'input_modalities', 
                e.target.value.split(',').map(s => s.trim()).filter(s => s))}
            />
          </div>
        </>
      ) : (
        <>
          <div>
            <Label htmlFor="dimensions">Dimensions</Label>
            <Input
              id="dimensions"
              type="number"
              value={formData.capabilities.dimensions || ''}
              onChange={(e) => handleNestedChange('capabilities', 'dimensions', parseInt(e.target.value) || 0)}
            />
          </div>
          <div>
            <Label htmlFor="max_input_tokens">Max Input Tokens</Label>
            <Input
              id="max_input_tokens"
              type="number"
              value={formData.capabilities.max_input_tokens || ''}
              onChange={(e) => handleNestedChange('capabilities', 'max_input_tokens', parseInt(e.target.value) || 0)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="supports_batching"
              checked={formData.capabilities.supports_batching || false}
              onCheckedChange={(checked) => handleNestedChange('capabilities', 'supports_batching', checked)}
            />
            <Label htmlFor="supports_batching">Supports Batching</Label>
          </div>
          <div>
            <Label htmlFor="supported_languages">Supported Languages (comma-separated)</Label>
            <Input
              id="supported_languages"
              value={formData.capabilities.supported_languages?.join(', ') || 'en'}
              onChange={(e) => handleNestedChange('capabilities', 'supported_languages', 
                e.target.value.split(',').map(s => s.trim()).filter(s => s))}
            />
          </div>
        </>
      )}
    </div>
  );

  const renderModelConfigForm = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {modelType === 'llm' ? (
        <>
          <div>
            <Label htmlFor="temperature">Temperature</Label>
            <Input
              id="temperature"
              type="number"
              step="0.1"
              min="0"
              max="2"
              value={formData.model_config.temperature || 0.7}
              onChange={(e) => handleNestedChange('model_config', 'temperature', parseFloat(e.target.value) || 0.7)}
            />
          </div>
          <div>
            <Label htmlFor="config_max_tokens">Max Tokens</Label>
            <Input
              id="config_max_tokens"
              type="number"
              value={formData.model_config.max_tokens || 4096}
              onChange={(e) => handleNestedChange('model_config', 'max_tokens', parseInt(e.target.value) || 4096)}
            />
          </div>
          <div>
            <Label htmlFor="top_p">Top P</Label>
            <Input
              id="top_p"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={formData.model_config.top_p || 1.0}
              onChange={(e) => handleNestedChange('model_config', 'top_p', parseFloat(e.target.value) || 1.0)}
            />
          </div>
          <div>
            <Label htmlFor="frequency_penalty">Frequency Penalty</Label>
            <Input
              id="frequency_penalty"
              type="number"
              step="0.1"
              min="-2"
              max="2"
              value={formData.model_config.frequency_penalty || 0.0}
              onChange={(e) => handleNestedChange('model_config', 'frequency_penalty', parseFloat(e.target.value) || 0.0)}
            />
          </div>
        </>
      ) : (
        <>
          <div>
            <Label htmlFor="config_dimensions">Dimensions</Label>
            <Input
              id="config_dimensions"
              type="number"
              value={formData.model_config.dimensions || ''}
              onChange={(e) => handleNestedChange('model_config', 'dimensions', parseInt(e.target.value) || 0)}
            />
          </div>
          <div>
            <Label htmlFor="batch_size">Batch Size</Label>
            <Input
              id="batch_size"
              type="number"
              value={formData.model_config.batch_size || 512}
              onChange={(e) => handleNestedChange('model_config', 'batch_size', parseInt(e.target.value) || 512)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="normalize"
              checked={formData.model_config.normalize || true}
              onCheckedChange={(checked) => handleNestedChange('model_config', 'normalize', checked)}
            />
            <Label htmlFor="normalize">Normalize Embeddings</Label>
          </div>
        </>
      )}
    </div>
  );

  const renderPricingForm = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {modelType === 'llm' ? (
        <>
          <div>
            <Label htmlFor="input_cost_per_token">Input Cost per Token</Label>
            <Input
              id="input_cost_per_token"
              type="number"
              step="0.000001"
              min="0"
              value={formData.pricing_info.input_cost_per_token || ''}
              onChange={(e) => handleNestedChange('pricing_info', 'input_cost_per_token', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div>
            <Label htmlFor="output_cost_per_token">Output Cost per Token</Label>
            <Input
              id="output_cost_per_token"
              type="number"
              step="0.000001"
              min="0"
              value={formData.pricing_info.output_cost_per_token || ''}
              onChange={(e) => handleNestedChange('pricing_info', 'output_cost_per_token', parseFloat(e.target.value) || 0)}
            />
          </div>
        </>
      ) : (
        <div>
          <Label htmlFor="cost_per_token">Cost per Token</Label>
          <Input
            id="cost_per_token"
            type="number"
            step="0.000001"
            min="0"
            value={formData.pricing_info.cost_per_token || ''}
            onChange={(e) => handleNestedChange('pricing_info', 'cost_per_token', parseFloat(e.target.value) || 0)}
          />
        </div>
      )}
      <div>
        <Label htmlFor="currency">Currency</Label>
        <Select
          value={formData.pricing_info.currency || 'USD'}
          onValueChange={(value) => handleNestedChange('pricing_info', 'currency', value)}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="USD">USD</SelectItem>
            <SelectItem value="EUR">EUR</SelectItem>
            <SelectItem value="GBP">GBP</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-900 rounded-lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {modelType === 'llm' ? (
            <Zap className="h-8 w-8 text-blue-600" />
          ) : (
            <Brain className="h-8 w-8 text-purple-600" />
          )}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {model ? 'Edit' : 'Create'} Model
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Configure your model for the LangGraph framework
            </p>
          </div>
        </div>
        {model && (
          <div className="flex items-center space-x-2">
            {onSetDefault && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleSetDefault}
                className="flex items-center space-x-1"
              >
                <Star className="h-4 w-4" />
                <span>Set Default</span>
              </Button>
            )}
            <Badge className={STATUS_OPTIONS.find(s => s.value === model.status)?.color}>
              {model.status}
            </Badge>
          </div>
        )}
      </div>

      {testResult && (
        <Alert className={`mb-6 ${testResult.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
          <div className="flex items-center space-x-2">
            {testResult.success ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-600" />
            )}
            <AlertDescription className={testResult.success ? 'text-green-800' : 'text-red-800'}>
              {testResult.message}
            </AlertDescription>
          </div>
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="basic">Basic</TabsTrigger>
            <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
            <TabsTrigger value="pricing">Pricing</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Model Name</Label>
                    <Input
                      id="name"
                      required
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="e.g., gpt-4, text-embedding-ada-002"
                    />
                  </div>
                  <div>
                    <Label htmlFor="display_name">Display Name</Label>
                    <Input
                      id="display_name"
                      required
                      value={formData.display_name}
                      onChange={(e) => handleInputChange('display_name', e.target.value)}
                      placeholder="e.g., GPT-4, OpenAI Ada v2"
                    />
                  </div>
                  <div>
                    <Label htmlFor="provider">Provider</Label>
                    <Select
                      value={formData.provider}
                      onValueChange={(value) => handleInputChange('provider', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {PROVIDERS.map(provider => (
                          <SelectItem key={provider.value} value={provider.value}>
                            {provider.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="status">Status</Label>
                    <Select
                      value={formData.status}
                      onValueChange={(value) => handleInputChange('status', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {STATUS_OPTIONS.map(status => (
                          <SelectItem key={status.value} value={status.value}>
                            {status.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="api_endpoint">API Endpoint (Optional)</Label>
                    <Input
                      id="api_endpoint"
                      value={formData.api_endpoint}
                      onChange={(e) => handleInputChange('api_endpoint', e.target.value)}
                      placeholder="Custom API endpoint URL"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="api_key">API Key (Optional)</Label>
                    <div className="relative">
                      <Input
                        id="api_key"
                        type={showApiKey ? "text" : "password"}
                        value={formData.api_key}
                        onChange={(e) => handleInputChange('api_key', e.target.value)}
                        placeholder="Enter API key"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2"
                        onClick={() => setShowApiKey(!showApiKey)}
                      >
                        {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                </div>
                
                {templates[formData.provider] && (
                  <div className="mt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={applyTemplate}
                      className="flex items-center space-x-2"
                    >
                      <Settings className="h-4 w-4" />
                      <span>Apply {PROVIDERS.find(p => p.value === formData.provider)?.label} Template</span>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="capabilities" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Model Capabilities</CardTitle>
              </CardHeader>
              <CardContent>
                {renderCapabilitiesForm()}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="config" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Model Configuration</CardTitle>
              </CardHeader>
              <CardContent>
                {renderModelConfigForm()}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="pricing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Pricing Information</CardTitle>
              </CardHeader>
              <CardContent>
                {renderPricingForm()}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Advanced Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="health_url">Health Check URL</Label>
                    <Input
                      id="health_url"
                      value={formData.health_url}
                      onChange={(e) => handleInputChange('health_url', e.target.value)}
                      placeholder="Health check endpoint"
                    />
                  </div>
                  <div>
                    <Label htmlFor="dns_name">DNS Name</Label>
                    <Input
                      id="dns_name"
                      value={formData.dns_name}
                      onChange={(e) => handleInputChange('dns_name', e.target.value)}
                      placeholder="DNS name for service"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="flex items-center justify-between mt-8">
          <div className="flex space-x-2">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            {onTest && (
              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={isTestLoading}
                className="flex items-center space-x-2"
              >
                {isTestLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Activity className="h-4 w-4" />
                )}
                <span>Test</span>
              </Button>
            )}
          </div>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Saving...
              </>
            ) : (
              model ? 'Update Model' : 'Create Model'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default LangGraphModelForm;