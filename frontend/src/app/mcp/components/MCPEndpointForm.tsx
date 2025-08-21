'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { StandardSection } from '@/components/layout/StandardPageLayout';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface MCPEndpointFormProps {
  endpoint?: any;
  servers: any[];
  onSave: (endpointData: any) => Promise<void>;
  onCancel: () => void;
}

export default function MCPEndpointForm({ endpoint, servers, onSave, onCancel }: MCPEndpointFormProps) {
  const [formData, setFormData] = useState({
    endpoint_name: '',
    display_name: '',
    description: '',
    endpoint_path: '',
    endpoint_url: '',
    is_public: false,
    authentication_required: true,
    allowed_methods: ['POST'] as string[],
    rate_limit: null as number | null,
    timeout_seconds: 30,
    tags: [] as string[],
    metadata: {}
  });

  const [tagInput, setTagInput] = useState('');
  const [metadataJsonError, setMetadataJsonError] = useState('');
  const [saving, setSaving] = useState(false);

  const availableMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

  useEffect(() => {
    if (endpoint) {
      setFormData({
        endpoint_name: endpoint.endpoint_name || '',
        display_name: endpoint.display_name || '',
        description: endpoint.description || '',
        endpoint_path: endpoint.endpoint_path || '',
        endpoint_url: endpoint.endpoint_url || '',
        is_public: endpoint.is_public || false,
        authentication_required: endpoint.authentication_required !== false,
        allowed_methods: endpoint.allowed_methods || ['POST'],
        rate_limit: endpoint.rate_limit || null,
        timeout_seconds: endpoint.timeout_seconds || 30,
        tags: endpoint.tags || [],
        metadata: endpoint.metadata || {}
      });
    }
  }, [endpoint]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMetadataChange = (value: string) => {
    try {
      const parsed = value.trim() ? JSON.parse(value) : {};
      setFormData(prev => ({
        ...prev,
        metadata: parsed
      }));
      setMetadataJsonError('');
    } catch (err) {
      setMetadataJsonError('Invalid JSON format');
    }
  };

  const toggleMethod = (method: string) => {
    setFormData(prev => ({
      ...prev,
      allowed_methods: prev.allowed_methods.includes(method)
        ? prev.allowed_methods.filter(m => m !== method)
        : [...prev.allowed_methods, method]
    }));
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const removeTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const generateEndpointUrl = () => {
    if (formData.endpoint_path) {
      const path = formData.endpoint_path.startsWith('/') ? formData.endpoint_path : `/${formData.endpoint_path}`;
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      setFormData(prev => ({
        ...prev,
        endpoint_url: `${baseUrl}/api/v1/mcp-gateway${path}`
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (metadataJsonError || formData.allowed_methods.length === 0) {
      return;
    }

    setSaving(true);
    try {
      const submitData = {
        ...formData,
        rate_limit: formData.rate_limit || undefined,
        ...(endpoint?.id ? { id: endpoint.id } : {})
      };
      await onSave(submitData);
    } catch (err) {
      console.error('Error saving endpoint:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <StandardSection>
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {endpoint ? 'Edit MCP Endpoint' : 'Create MCP Endpoint'}
          </h3>
          <Button variant="ghost" size="sm" onClick={onCancel}>
            <XMarkIcon className="h-4 w-4" />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="endpoint_name">Endpoint Name *</Label>
                <Input
                  id="endpoint_name"
                  value={formData.endpoint_name}
                  onChange={(e) => handleInputChange('endpoint_name', e.target.value)}
                  placeholder="my-mcp-endpoint"
                  required
                />
              </div>

              <div>
                <Label htmlFor="display_name">Display Name *</Label>
                <Input
                  id="display_name"
                  value={formData.display_name}
                  onChange={(e) => handleInputChange('display_name', e.target.value)}
                  placeholder="My MCP Endpoint"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Description of what this endpoint does"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-vertical min-h-[80px]"
                />
              </div>

              <div>
                <Label htmlFor="endpoint_path">Endpoint Path *</Label>
                <div className="flex space-x-2">
                  <Input
                    id="endpoint_path"
                    value={formData.endpoint_path}
                    onChange={(e) => handleInputChange('endpoint_path', e.target.value)}
                    placeholder="/my-endpoint"
                    required
                  />
                  <Button type="button" onClick={generateEndpointUrl} size="sm">
                    Generate URL
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="endpoint_url">Endpoint URL</Label>
                <Input
                  id="endpoint_url"
                  value={formData.endpoint_url}
                  onChange={(e) => handleInputChange('endpoint_url', e.target.value)}
                  placeholder="http://localhost:8000/api/v1/mcp-gateway/my-endpoint"
                  readOnly
                  className="bg-gray-50 dark:bg-gray-700"
                />
              </div>
            </div>

            <div className="space-y-4">
              {/* Settings */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={formData.is_public}
                    onChange={(e) => handleInputChange('is_public', e.target.checked)}
                    className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                  />
                  <Label htmlFor="is_public">Public Endpoint</Label>
                </div>

                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="authentication_required"
                    checked={formData.authentication_required}
                    onChange={(e) => handleInputChange('authentication_required', e.target.checked)}
                    className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                  />
                  <Label htmlFor="authentication_required">Authentication Required</Label>
                </div>
              </div>

              {/* HTTP Methods */}
              <div>
                <Label>Allowed HTTP Methods *</Label>
                <div className="grid grid-cols-3 gap-2 mt-2">
                  {availableMethods.map((method) => (
                    <div key={method} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`method-${method}`}
                        checked={formData.allowed_methods.includes(method)}
                        onChange={() => toggleMethod(method)}
                        className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                      />
                      <Label htmlFor={`method-${method}`} className="text-sm">
                        {method}
                      </Label>
                    </div>
                  ))}
                </div>
                {formData.allowed_methods.length === 0 && (
                  <p className="text-red-600 dark:text-red-400 text-sm mt-1">
                    At least one HTTP method must be selected
                  </p>
                )}
              </div>

              {/* Rate Limit */}
              <div>
                <Label htmlFor="rate_limit">Rate Limit (requests per minute)</Label>
                <Input
                  id="rate_limit"
                  type="number"
                  value={formData.rate_limit || ''}
                  onChange={(e) => handleInputChange('rate_limit', e.target.value ? parseInt(e.target.value) : null)}
                  placeholder="100"
                  min="1"
                />
              </div>

              {/* Timeout */}
              <div>
                <Label htmlFor="timeout_seconds">Timeout (seconds)</Label>
                <Input
                  id="timeout_seconds"
                  type="number"
                  value={formData.timeout_seconds}
                  onChange={(e) => handleInputChange('timeout_seconds', parseInt(e.target.value))}
                  min="1"
                  max="300"
                />
              </div>

              {/* Tags */}
              <div>
                <Label>Tags</Label>
                <div className="flex space-x-2 mb-2">
                  <Input
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    placeholder="Add tag"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  />
                  <Button type="button" onClick={addTag} size="sm">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300 rounded-full text-sm"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Metadata JSON */}
          <div>
            <Label htmlFor="metadata">Metadata (JSON)</Label>
            <textarea
              id="metadata"
              value={JSON.stringify(formData.metadata, null, 2)}
              onChange={(e) => handleMetadataChange(e.target.value)}
              placeholder='{"custom_field": "value"}'
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm resize-vertical min-h-[100px]"
            />
            {metadataJsonError && (
              <p className="text-red-600 dark:text-red-400 text-sm mt-1">
                {metadataJsonError}
              </p>
            )}
          </div>

          <div className="flex justify-end space-x-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={saving || !!metadataJsonError || formData.allowed_methods.length === 0}
            >
              {saving ? 'Saving...' : (endpoint ? 'Update Endpoint' : 'Create Endpoint')}
            </Button>
          </div>
        </form>
      </div>
    </StandardSection>
  );
}
