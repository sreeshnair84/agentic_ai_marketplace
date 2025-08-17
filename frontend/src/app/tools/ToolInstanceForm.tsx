'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  Save, 
  Eye,
  EyeOff,
  Settings,
  AlertTriangle,
  Info
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ToolTemplate {
  id: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  type: string;
  version: string;
  fields: ToolTemplateField[];
}

interface ToolTemplateField {
  id: string;
  field_name: string;
  field_label: string;
  field_type: string;
  field_description?: string;
  is_required: boolean;
  is_secret: boolean;
  default_value?: string;
  validation_rules?: any;
  field_options?: any;
  field_order: number;
}

interface ToolInstance {
  id?: string;
  tool_template_id: string;
  name: string;
  display_name: string;
  description: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  configuration: Record<string, any>;
  environment_scope: 'global' | 'development' | 'staging' | 'production';
}

interface LLMModel {
  id: string;
  name: string;
  display_name: string;
  provider: string;
}

interface EmbeddingModel {
  id: string;
  name: string;
  display_name: string;
  provider: string;
}

interface ToolInstanceFormProps {
  instance?: ToolInstance;
  templates: ToolTemplate[];
  llmModels: LLMModel[];
  embeddingModels: EmbeddingModel[];
  onSave: (instance: ToolInstance) => void;
  onCancel: () => void;
}

export default function ToolInstanceForm({ 
  instance, 
  templates, 
  llmModels, 
  embeddingModels, 
  onSave, 
  onCancel 
}: ToolInstanceFormProps) {
  const [formData, setFormData] = useState<ToolInstance>({
    tool_template_id: '',
    name: '',
    display_name: '',
    description: '',
    status: 'active',
    configuration: {},
    environment_scope: 'development'
  });

  const [selectedTemplate, setSelectedTemplate] = useState<ToolTemplate | null>(null);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (instance) {
      setFormData(instance);
      const template = templates.find(t => t.id === instance.tool_template_id);
      setSelectedTemplate(template || null);
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

  const handleTemplateChange = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    setSelectedTemplate(template || null);
    
    // Initialize configuration with default values
    const defaultConfig: Record<string, any> = {};
    template?.fields.forEach(field => {
      if (field.default_value) {
        defaultConfig[field.field_name] = field.default_value;
      }
    });

    setFormData(prev => ({
      ...prev,
      tool_template_id: templateId,
      configuration: defaultConfig
    }));
  };

  const handleConfigurationChange = (fieldName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      configuration: {
        ...prev.configuration,
        [fieldName]: value
      }
    }));

    // Clear field error
    if (errors[`config_${fieldName}`]) {
      setErrors(prev => ({
        ...prev,
        [`config_${fieldName}`]: ''
      }));
    }
  };

  const toggleSecretVisibility = (fieldName: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const getFieldOptions = (field: ToolTemplateField): Array<{value: string, label: string}> => {
    if (!field.field_options) return [];

    switch (field.field_options.source) {
      case 'llm_models':
        return llmModels.map(model => ({
          value: model.name,
          label: model.display_name
        }));
      case 'embedding_models':
        return embeddingModels.map(model => ({
          value: model.name,
          label: model.display_name
        }));
      case 'custom':
        return (field.field_options.custom_options || []).map((option: string) => ({
          value: option,
          label: option
        }));
      default:
        return [];
    }
  };

  const renderConfigurationField = (field: ToolTemplateField) => {
    const value = formData.configuration[field.field_name] || '';
    const fieldError = errors[`config_${field.field_name}`];

    switch (field.field_type) {
      case 'text':
      case 'url':
      case 'email':
        return (
          <input
            type={field.field_type === 'email' ? 'email' : field.field_type === 'url' ? 'url' : 'text'}
            value={value}
            onChange={(e) => handleConfigurationChange(field.field_name, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder={field.default_value || `Enter ${field.field_label.toLowerCase()}...`}
          />
        );

      case 'password':
        return (
          <div className="relative">
            <input
              type={showSecrets[field.field_name] ? 'text' : 'password'}
              value={value}
              onChange={(e) => handleConfigurationChange(field.field_name, e.target.value)}
              className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              placeholder={field.default_value || `Enter ${field.field_label.toLowerCase()}...`}
            />
            <button
              type="button"
              onClick={() => toggleSecretVisibility(field.field_name)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showSecrets[field.field_name] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        );

      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleConfigurationChange(field.field_name, e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder={field.default_value || `Enter ${field.field_label.toLowerCase()}...`}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleConfigurationChange(field.field_name, parseFloat(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder={field.default_value || `Enter ${field.field_label.toLowerCase()}...`}
          />
        );

      case 'boolean':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={Boolean(value)}
              onChange={(e) => handleConfigurationChange(field.field_name, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              {field.field_description || field.field_label}
            </span>
          </div>
        );

      case 'select':
        const options = getFieldOptions(field);
        return (
          <select
            value={value}
            onChange={(e) => handleConfigurationChange(field.field_name, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">Select {field.field_label.toLowerCase()}...</option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'multiselect':
        const multiselectOptions = getFieldOptions(field);
        const selectedValues = Array.isArray(value) ? value : [];
        
        return (
          <div className="space-y-2">
            {multiselectOptions.map((option) => (
              <div key={option.value} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedValues.includes(option.value)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...selectedValues, option.value]
                      : selectedValues.filter(v => v !== option.value);
                    handleConfigurationChange(field.field_name, newValues);
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  {option.label}
                </span>
              </div>
            ))}
          </div>
        );

      case 'json':
        return (
          <textarea
            value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
            onChange={(e) => {
              try {
                const jsonValue = JSON.parse(e.target.value);
                handleConfigurationChange(field.field_name, jsonValue);
              } catch {
                handleConfigurationChange(field.field_name, e.target.value);
              }
            }}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm"
            placeholder='{"key": "value"}'
          />
        );

      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleConfigurationChange(field.field_name, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder={field.default_value || `Enter ${field.field_label.toLowerCase()}...`}
          />
        );
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.tool_template_id) {
      newErrors.tool_template_id = 'Template is required';
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.display_name.trim()) {
      newErrors.display_name = 'Display name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    // Validate required configuration fields
    selectedTemplate?.fields.forEach(field => {
      if (field.is_required && !formData.configuration[field.field_name]) {
        newErrors[`config_${field.field_name}`] = `${field.field_label} is required`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSave(formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-hidden">
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
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tool Template <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.tool_template_id}
                onChange={(e) => handleTemplateChange(e.target.value)}
                disabled={Boolean(instance)} // Can't change template for existing instances
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="">Select a template...</option>
                {templates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.display_name} ({template.category})
                  </option>
                ))}
              </select>
              {errors.tool_template_id && <p className="text-red-500 text-sm mt-1">{errors.tool_template_id}</p>}
            </div>

            {selectedTemplate && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Info className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">{selectedTemplate.display_name}</h4>
                    <p className="text-blue-700 dark:text-blue-300 text-sm mt-1">{selectedTemplate.description}</p>
                    <div className="flex items-center space-x-4 mt-2 text-xs">
                      <span className="text-blue-600 dark:text-blue-400">Version: {selectedTemplate.version}</span>
                      <span className="text-blue-600 dark:text-blue-400">Category: {selectedTemplate.category}</span>
                      <span className="text-blue-600 dark:text-blue-400">Fields: {selectedTemplate.fields.length}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="e.g., rag-processor-prod"
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
                  placeholder="e.g., Production RAG Processor"
                />
                {errors.display_name && <p className="text-red-500 text-sm mt-1">{errors.display_name}</p>}
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
                  <option value="inactive">Inactive</option>
                  <option value="testing">Testing</option>
                  <option value="error">Error</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Environment Scope
                </label>
                <select
                  value={formData.environment_scope}
                  onChange={(e) => handleInputChange('environment_scope', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                  <option value="global">Global</option>
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
                placeholder="Describe this tool instance..."
              />
              {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
            </div>

            {/* Configuration Fields */}
            {selectedTemplate && selectedTemplate.fields.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Configuration
                </h3>
                <div className="space-y-4">
                  {selectedTemplate.fields
                    .sort((a, b) => a.field_order - b.field_order)
                    .map((field) => (
                      <div key={field.id}>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {field.field_label}
                          {field.is_required && <span className="text-red-500 ml-1">*</span>}
                          {field.is_secret && (
                            <span className="ml-2 px-1 py-0.5 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300 rounded">
                              Secret
                            </span>
                          )}
                        </label>
                        
                        {field.field_description && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {field.field_description}
                          </p>
                        )}
                        
                        {renderConfigurationField(field)}
                        
                        {errors[`config_${field.field_name}`] && (
                          <p className="text-red-500 text-sm mt-1">{errors[`config_${field.field_name}`]}</p>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            )}

            {selectedTemplate && selectedTemplate.fields.length === 0 && (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>This template has no configuration fields.</p>
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
            Save Instance
          </Button>
        </div>
      </div>
    </div>
  );
}
