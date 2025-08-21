'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { StandardSection } from '@/components/layout/StandardPageLayout';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface MCPServerFormProps {
  server?: any;
  onSave: (serverData: any) => Promise<void>;
  onCancel: () => void;
}

export default function MCPServerForm({ server, onSave, onCancel }: MCPServerFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    server_url: '',
    transport_type: 'http' as 'stdio' | 'http' | 'websocket' | 'sse',
    version: '1.0.0',
    capabilities: [] as string[],
    tags: [] as string[],
    connection_config: {},
    authentication_config: {},
    metadata: {}
  });

  const [capabilityInput, setCapabilityInput] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [configJsonError, setConfigJsonError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (server) {
      setFormData({
        name: server.name || '',
        display_name: server.display_name || '',
        description: server.description || '',
        server_url: server.server_url || '',
        transport_type: server.transport_type || 'http',
        version: server.version || '1.0.0',
        capabilities: server.capabilities || [],
        tags: server.tags || [],
        connection_config: server.connection_config || {},
        authentication_config: server.authentication_config || {},
        metadata: server.metadata || {}
      });
    }
  }, [server]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleJsonConfigChange = (field: string, value: string) => {
    try {
      const parsed = value.trim() ? JSON.parse(value) : {};
      setFormData(prev => ({
        ...prev,
        [field]: parsed
      }));
      setConfigJsonError('');
    } catch (err) {
      setConfigJsonError('Invalid JSON format');
    }
  };

  const addCapability = () => {
    if (capabilityInput.trim() && !formData.capabilities.includes(capabilityInput.trim())) {
      setFormData(prev => ({
        ...prev,
        capabilities: [...prev.capabilities, capabilityInput.trim()]
      }));
      setCapabilityInput('');
    }
  };

  const removeCapability = (capability: string) => {
    setFormData(prev => ({
      ...prev,
      capabilities: prev.capabilities.filter(c => c !== capability)
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (configJsonError) {
      return;
    }

    setSaving(true);
    try {
      const submitData = {
        ...formData,
        ...(server?.id ? { id: server.id } : {})
      };
      await onSave(submitData);
    } catch (err) {
      console.error('Error saving server:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <StandardSection>
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {server ? 'Edit MCP Server' : 'Create MCP Server'}
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
                <Label htmlFor="name">Server Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="my-mcp-server"
                  required
                />
              </div>

              <div>
                <Label htmlFor="display_name">Display Name *</Label>
                <Input
                  id="display_name"
                  value={formData.display_name}
                  onChange={(e) => handleInputChange('display_name', e.target.value)}
                  placeholder="My MCP Server"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Description of what this MCP server does"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-vertical min-h-[80px]"
                />
              </div>

              <div>
                <Label htmlFor="server_url">Server URL *</Label>
                <Input
                  id="server_url"
                  value={formData.server_url}
                  onChange={(e) => handleInputChange('server_url', e.target.value)}
                  placeholder="http://localhost:3001"
                  required
                />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="transport_type">Transport Type *</Label>
                <select
                  id="transport_type"
                  value={formData.transport_type}
                  onChange={(e) => handleInputChange('transport_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  required
                >
                  <option value="http">HTTP</option>
                  <option value="websocket">WebSocket</option>
                  <option value="sse">Server-Sent Events</option>
                  <option value="stdio">Standard I/O</option>
                </select>
              </div>

              <div>
                <Label htmlFor="version">Version</Label>
                <Input
                  id="version"
                  value={formData.version}
                  onChange={(e) => handleInputChange('version', e.target.value)}
                  placeholder="1.0.0"
                />
              </div>

              {/* Capabilities */}
              <div>
                <Label>Capabilities</Label>
                <div className="flex space-x-2 mb-2">
                  <Input
                    value={capabilityInput}
                    onChange={(e) => setCapabilityInput(e.target.value)}
                    placeholder="Add capability"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCapability())}
                  />
                  <Button type="button" onClick={addCapability} size="sm">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.capabilities.map((capability) => (
                    <span
                      key={capability}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 rounded-full text-sm"
                    >
                      {capability}
                      <button
                        type="button"
                        onClick={() => removeCapability(capability)}
                        className="ml-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
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

          {/* Configuration JSON */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <Label htmlFor="connection_config">Connection Config (JSON)</Label>
              <textarea
                id="connection_config"
                value={JSON.stringify(formData.connection_config, null, 2)}
                onChange={(e) => handleJsonConfigChange('connection_config', e.target.value)}
                placeholder='{"timeout": 30000}'
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm resize-vertical min-h-[100px]"
              />
            </div>

            <div>
              <Label htmlFor="authentication_config">Authentication Config (JSON)</Label>
              <textarea
                id="authentication_config"
                value={JSON.stringify(formData.authentication_config, null, 2)}
                onChange={(e) => handleJsonConfigChange('authentication_config', e.target.value)}
                placeholder='{"api_key": "..."}'
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm resize-vertical min-h-[100px]"
              />
            </div>

            <div>
              <Label htmlFor="metadata">Metadata (JSON)</Label>
              <textarea
                id="metadata"
                value={JSON.stringify(formData.metadata, null, 2)}
                onChange={(e) => handleJsonConfigChange('metadata', e.target.value)}
                placeholder='{"environment": "development"}'
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-sm resize-vertical min-h-[100px]"
              />
            </div>
          </div>

          {configJsonError && (
            <div className="text-red-600 dark:text-red-400 text-sm">
              {configJsonError}
            </div>
          )}

          <div className="flex justify-end space-x-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving || !!configJsonError}>
              {saving ? 'Saving...' : (server ? 'Update Server' : 'Create Server')}
            </Button>
          </div>
        </form>
      </div>
    </StandardSection>
  );
}
