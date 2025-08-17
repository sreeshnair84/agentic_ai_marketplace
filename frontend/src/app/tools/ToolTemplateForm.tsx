'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  Plus, 
  Trash2, 
  Save, 
  ArrowLeft,
  Settings,
  Eye,
  EyeOff,
  Info
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FieldType {
  value: string;
  label: string;
  description: string;
  supportedOptions?: string[];
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

interface ToolTemplate {
  id?: string;
  name: string;
  display_name: string;
  description: string;
  category: string;
  type: string;
  version: string;
  is_active: boolean;
  icon?: string;
  tags?: string[];
  fields: ToolTemplateField[];
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

interface ToolTemplateFormProps {
  template?: ToolTemplate;
  onSave: (template: ToolTemplate) => void;
  onCancel: () => void;
  llmModels: LLMModel[];
  embeddingModels: EmbeddingModel[];
}

const fieldTypes: FieldType[] = [
  {
    value: 'text',
    label: 'Text Input',
    description: 'Single line text input'
  },
  {
    value: 'textarea',
    label: 'Text Area',
    description: 'Multi-line text input'
  },
  {
    value: 'number',
    label: 'Number',
    description: 'Numeric input'
  },
  {
    value: 'boolean',
    label: 'Boolean',
    description: 'True/false checkbox'
  },
  {
    value: 'select',
    label: 'Select Dropdown',
    description: 'Single selection from options',
    supportedOptions: ['custom', 'llm_models', 'embedding_models']
  },
  {
    value: 'multiselect',
    label: 'Multi-Select',
    description: 'Multiple selections from options',
    supportedOptions: ['custom', 'llm_models', 'embedding_models']
  },
  {
    value: 'url',
    label: 'URL',
    description: 'URL input with validation'
  },
  {
    value: 'email',
    label: 'Email',
    description: 'Email input with validation'
  },
  {
    value: 'password',
    label: 'Password',
    description: 'Masked password input'
  },
  {
    value: 'json',
    label: 'JSON',
    description: 'JSON object input'
  }
];

const categories = [
  { value: 'mcp', label: 'MCP Tools' },
  { value: 'custom', label: 'Custom Tools' },
  { value: 'api', label: 'API Tools' },
  { value: 'llm', label: 'LLM Tools' },
  { value: 'rag', label: 'RAG Tools' },
  { value: 'workflow', label: 'Workflow Tools' }
];

export default function ToolTemplateForm({ 
  template, 
  onSave, 
  onCancel, 
  llmModels, 
  embeddingModels 
}: ToolTemplateFormProps) {
  const [formData, setFormData] = useState<ToolTemplate>({
    name: '',
    display_name: '',
    description: '',
    category: 'custom',
    type: '',
    version: '1.0.0',
    is_active: true,
    tags: [],
    fields: []
  });

  const [newTag, setNewTag] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (template) {
      setFormData(template);
    }
  }, [template]);

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

  const addTag = () => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags?.filter(tag => tag !== tagToRemove) || []
    }));
  };

  const addField = () => {
    const newField: ToolTemplateField = {
      id: `field-${Date.now()}`,
      field_name: '',
      field_label: '',
      field_type: 'text',
      field_description: '',
      is_required: false,
      is_secret: false,
      field_order: formData.fields.length + 1
    };

    setFormData(prev => ({
      ...prev,
      fields: [...prev.fields, newField]
    }));
  };

  const updateField = (fieldId: string, updates: Partial<ToolTemplateField>) => {
    setFormData(prev => ({
      ...prev,
      fields: prev.fields.map(field => 
        field.id === fieldId ? { ...field, ...updates } : field
      )
    }));
  };

  const removeField = (fieldId: string) => {
    setFormData(prev => ({
      ...prev,
      fields: prev.fields.filter(field => field.id !== fieldId)
    }));
  };

  const moveField = (fieldId: string, direction: 'up' | 'down') => {
    const currentIndex = formData.fields.findIndex(f => f.id === fieldId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= formData.fields.length) return;

    const newFields = [...formData.fields];
    [newFields[currentIndex], newFields[newIndex]] = [newFields[newIndex], newFields[currentIndex]];
    
    // Update field orders
    newFields.forEach((field, index) => {
      field.field_order = index + 1;
    });

    setFormData(prev => ({
      ...prev,
      fields: newFields
    }));
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

    if (!formData.type.trim()) {
      newErrors.type = 'Type is required';
    }

    // Validate fields
    formData.fields.forEach((field, index) => {
      if (!field.field_name.trim()) {
        newErrors[`field_${index}_name`] = 'Field name is required';
      }
      if (!field.field_label.trim()) {
        newErrors[`field_${index}_label`] = 'Field label is required';
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

  const getFieldOptionTypes = (fieldType: string) => {
    const type = fieldTypes.find(t => t.value === fieldType);
    return type?.supportedOptions || [];
  };

  const renderFieldOptions = (field: ToolTemplateField, fieldIndex: number) => {
    const optionTypes = getFieldOptionTypes(field.field_type);
    
    if (optionTypes.length === 0) return null;

    return (
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Options Source
        </label>
        <select
          value={field.field_options?.source || 'custom'}
          onChange={(e) => updateField(field.id, {
            field_options: { ...field.field_options, source: e.target.value }
          })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="custom">Custom Options</option>
          {optionTypes.includes('llm_models') && (
            <option value="llm_models">LLM Models</option>
          )}
          {optionTypes.includes('embedding_models') && (
            <option value="embedding_models">Embedding Models</option>
          )}
        </select>

        {field.field_options?.source === 'custom' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Custom Options (one per line)
            </label>
            <textarea
              value={field.field_options?.custom_options?.join('\n') || ''}
              onChange={(e) => updateField(field.id, {
                field_options: {
                  ...field.field_options,
                  custom_options: e.target.value.split('\n').filter(opt => opt.trim())
                }
              })}
              placeholder="Option 1&#10;Option 2&#10;Option 3"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              rows={4}
            />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {template ? 'Edit Tool Template' : 'Create Tool Template'}
          </h2>
          <Button variant="ghost" onClick={onCancel}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 140px)' }}>
          <form onSubmit={handleSubmit} className="space-y-6">
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
                  placeholder="e.g., rag-document-processor"
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
                  placeholder="e.g., RAG Document Processor"
                />
                {errors.display_name && <p className="text-red-500 text-sm mt-1">{errors.display_name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Type <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="e.g., rag_processor, chat_completion"
                />
                {errors.type && <p className="text-red-500 text-sm mt-1">{errors.type}</p>}
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

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => handleInputChange('is_active', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="is_active" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Active Template
                </label>
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
                placeholder="Describe what this tool template does..."
              />
              {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tags
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.tags?.map((tag, index) => (
                  <span 
                    key={index}
                    className="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 rounded-md flex items-center space-x-1"
                  >
                    <span>{tag}</span>
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Add a tag..."
                />
                <Button type="button" onClick={addTag} variant="outline">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Fields */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Template Fields
                </h3>
                <Button type="button" onClick={addField} variant="outline">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Field
                </Button>
              </div>

              <div className="space-y-4">
                {formData.fields.map((field, fieldIndex) => (
                  <div 
                    key={field.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        Field {fieldIndex + 1}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => moveField(field.id, 'up')}
                          disabled={fieldIndex === 0}
                        >
                          ↑
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => moveField(field.id, 'down')}
                          disabled={fieldIndex === formData.fields.length - 1}
                        >
                          ↓
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeField(field.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Field Name <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={field.field_name}
                          onChange={(e) => updateField(field.id, { field_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                          placeholder="e.g., embedding_model"
                        />
                        {errors[`field_${fieldIndex}_name`] && (
                          <p className="text-red-500 text-sm mt-1">{errors[`field_${fieldIndex}_name`]}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Field Label <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={field.field_label}
                          onChange={(e) => updateField(field.id, { field_label: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                          placeholder="e.g., Embedding Model"
                        />
                        {errors[`field_${fieldIndex}_label`] && (
                          <p className="text-red-500 text-sm mt-1">{errors[`field_${fieldIndex}_label`]}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Field Type
                        </label>
                        <select
                          value={field.field_type}
                          onChange={(e) => updateField(field.id, { field_type: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                          {fieldTypes.map(type => (
                            <option key={type.value} value={type.value}>{type.label}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Description
                      </label>
                      <textarea
                        value={field.field_description || ''}
                        onChange={(e) => updateField(field.id, { field_description: e.target.value })}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="Describe this field..."
                      />
                    </div>

                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Default Value
                        </label>
                        <input
                          type="text"
                          value={field.default_value || ''}
                          onChange={(e) => updateField(field.id, { default_value: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                          placeholder="Default value..."
                        />
                      </div>

                      <div className="flex items-center space-x-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id={`required_${field.id}`}
                            checked={field.is_required}
                            onChange={(e) => updateField(field.id, { is_required: e.target.checked })}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor={`required_${field.id}`} className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                            Required
                          </label>
                        </div>

                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id={`secret_${field.id}`}
                            checked={field.is_secret}
                            onChange={(e) => updateField(field.id, { is_secret: e.target.checked })}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <label htmlFor={`secret_${field.id}`} className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                            Secret
                          </label>
                        </div>
                      </div>
                    </div>

                    {/* Field Options */}
                    {['select', 'multiselect'].includes(field.field_type) && (
                      <div className="mt-4">
                        {renderFieldOptions(field, fieldIndex)}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {formData.fields.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No fields defined yet. Add fields to configure your tool template.</p>
                </div>
              )}
            </div>
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
      </div>
    </div>
  );
}
