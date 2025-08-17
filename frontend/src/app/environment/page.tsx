'use client';

import { useState, useEffect } from 'react';
import { 
  Key, 
  Plus, 
  Edit3, 
  Trash2, 
  Eye, 
  EyeOff, 
  Save, 
  Search, 
  Filter,
  Shield,
  Database,
  Cloud,
  Zap,
  RefreshCw,
  Copy,
  Check,
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EnvironmentVariable {
  id: string;
  name: string;
  value: string;
  description: string;
  category: 'llm' | 'database' | 'api' | 'auth' | 'system' | 'integration';
  isSecret: boolean;
  isRequired: boolean;
  lastUpdated: string;
  updatedBy: string;
  scope: 'global' | 'development' | 'staging' | 'production';
}

interface NewEnvVarForm {
  name: string;
  value: string;
  description: string;
  category: 'llm' | 'database' | 'api' | 'auth' | 'system' | 'integration';
  isSecret: boolean;
  isRequired: boolean;
  scope: 'global' | 'development' | 'staging' | 'production';
}

const mockEnvironmentVariables: EnvironmentVariable[] = [
  {
    id: 'env-1',
    name: 'OPENAI_API_KEY',
    value: 'sk-proj-***************************',
    description: 'OpenAI API key for GPT models',
    category: 'llm',
    isSecret: true,
    isRequired: true,
    lastUpdated: '2024-01-15T10:30:00Z',
    updatedBy: 'admin@platform.com',
    scope: 'production'
  },
  {
    id: 'env-2',
    name: 'ANTHROPIC_API_KEY',
    value: 'sk-ant-***************************',
    description: 'Anthropic Claude API key',
    category: 'llm',
    isSecret: true,
    isRequired: false,
    lastUpdated: '2024-01-15T09:15:00Z',
    updatedBy: 'admin@platform.com',
    scope: 'production'
  },
  {
    id: 'env-3',
    name: 'DATABASE_URL',
    value: 'postgresql://***:***@localhost:5432/platform',
    description: 'Primary database connection string',
    category: 'database',
    isSecret: true,
    isRequired: true,
    lastUpdated: '2024-01-14T16:20:00Z',
    updatedBy: 'admin@platform.com',
    scope: 'production'
  },
  {
    id: 'env-4',
    name: 'REDIS_URL',
    value: 'redis://localhost:6379',
    description: 'Redis cache connection string',
    category: 'database',
    isSecret: false,
    isRequired: true,
    lastUpdated: '2024-01-14T14:45:00Z',
    updatedBy: 'admin@platform.com',
    scope: 'production'
  },
  {
    id: 'env-5',
    name: 'EMBEDDING_MODEL_ENDPOINT',
    value: 'https://api.openai.com/v1/embeddings',
    description: 'Endpoint for text embeddings generation',
    category: 'llm',
    isSecret: false,
    isRequired: true,
    lastUpdated: '2024-01-15T08:30:00Z',
    updatedBy: 'admin@platform.com',
    scope: 'production'
  },
  {
    id: 'env-6',
    name: 'JWT_SECRET',
    value: '***************************',
    description: 'Secret key for JWT token signing',
    category: 'auth',
    isSecret: true,
    isRequired: true,
    lastUpdated: '2024-01-10T12:00:00Z',
    updatedBy: 'admin@platform.com',
    scope: 'production'
  }
];

const categoryConfig = {
  llm: { icon: Zap, color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300', label: 'LLM' },
  database: { icon: Database, color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300', label: 'Database' },
  api: { icon: Cloud, color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300', label: 'API' },
  auth: { icon: Shield, color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300', label: 'Auth' },
  system: { icon: RefreshCw, color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300', label: 'System' },
  integration: { icon: Zap, color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300', label: 'Integration' }
};

export default function EnvironmentManagement() {
  const [envVars, setEnvVars] = useState<EnvironmentVariable[]>(mockEnvironmentVariables);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedScope, setSelectedScope] = useState<string>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingVar, setEditingVar] = useState<string | null>(null);
  const [visibleSecrets, setVisibleSecrets] = useState<Set<string>>(new Set());
  const [copiedValue, setCopiedValue] = useState<string | null>(null);

  const [newEnvVar, setNewEnvVar] = useState<NewEnvVarForm>({
    name: '',
    value: '',
    description: '',
    category: 'system',
    isSecret: false,
    isRequired: false,
    scope: 'development'
  });

  const toggleSecretVisibility = (id: string) => {
    const newVisible = new Set(visibleSecrets);
    if (newVisible.has(id)) {
      newVisible.delete(id);
    } else {
      newVisible.add(id);
    }
    setVisibleSecrets(newVisible);
  };

  const copyToClipboard = async (value: string, id: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopiedValue(id);
      setTimeout(() => setCopiedValue(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleAddEnvVar = () => {
    const envVar: EnvironmentVariable = {
      id: `env-${Date.now()}`,
      ...newEnvVar,
      lastUpdated: new Date().toISOString(),
      updatedBy: 'admin@platform.com'
    };
    
    setEnvVars([...envVars, envVar]);
    setNewEnvVar({
      name: '',
      value: '',
      description: '',
      category: 'system',
      isSecret: false,
      isRequired: false,
      scope: 'development'
    });
    setShowAddForm(false);
  };

  const handleDeleteEnvVar = (id: string) => {
    setEnvVars(envVars.filter(env => env.id !== id));
  };

  const filteredEnvVars = envVars.filter(envVar => {
    const matchesSearch = envVar.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         envVar.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || envVar.category === selectedCategory;
    const matchesScope = selectedScope === 'all' || envVar.scope === selectedScope;
    
    return matchesSearch && matchesCategory && matchesScope;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const renderValue = (envVar: EnvironmentVariable) => {
    if (envVar.isSecret && !visibleSecrets.has(envVar.id)) {
      return '•'.repeat(20);
    }
    return envVar.value;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Environment Variables & Secrets
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage configuration variables, API keys, and sensitive data
          </p>
        </div>
        <Button 
          onClick={() => setShowAddForm(true)}
          className="flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Add Variable</span>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search variables..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>
        
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="all">All Categories</option>
          {Object.entries(categoryConfig).map(([key, config]) => (
            <option key={key} value={key}>{config.label}</option>
          ))}
        </select>

        <select
          value={selectedScope}
          onChange={(e) => setSelectedScope(e.target.value)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="all">All Scopes</option>
          <option value="development">Development</option>
          <option value="staging">Staging</option>
          <option value="production">Production</option>
          <option value="global">Global</option>
        </select>
      </div>

      {/* Environment Variables List */}
      <div className="space-y-4">
        {filteredEnvVars.map((envVar) => {
          const categoryInfo = categoryConfig[envVar.category];
          const CategoryIcon = categoryInfo.icon;
          
          return (
            <div
              key={envVar.id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="flex items-center space-x-2">
                      <CategoryIcon className="h-4 w-4" />
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {envVar.name}
                      </h3>
                    </div>
                    
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${categoryInfo.color}`}>
                      {categoryInfo.label}
                    </span>
                    
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      envVar.scope === 'production' 
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                        : envVar.scope === 'staging'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                        : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                    }`}>
                      {envVar.scope}
                    </span>
                    
                    {envVar.isRequired && (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300">
                        Required
                      </span>
                    )}
                    
                    {envVar.isSecret && (
                      <Key className="h-4 w-4 text-amber-500" />
                    )}
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 mb-3">
                    {envVar.description}
                  </p>
                  
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 font-mono text-sm text-gray-900 dark:text-white break-all">
                        {renderValue(envVar)}
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        {envVar.isSecret && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleSecretVisibility(envVar.id)}
                          >
                            {visibleSecrets.has(envVar.id) ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        )}
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(envVar.value, envVar.id)}
                        >
                          {copiedValue === envVar.id ? (
                            <Check className="h-4 w-4 text-green-500" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-3 text-sm text-gray-500 dark:text-gray-400">
                    <span>Last updated: {formatDate(envVar.lastUpdated)}</span>
                    <span>By: {envVar.updatedBy}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-6">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setEditingVar(envVar.id)}
                  >
                    <Edit3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteEnvVar(envVar.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add New Environment Variable Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Add Environment Variable
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={newEnvVar.name}
                  onChange={(e) => setNewEnvVar({...newEnvVar, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="VARIABLE_NAME"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Value
                </label>
                <input
                  type={newEnvVar.isSecret ? "password" : "text"}
                  value={newEnvVar.value}
                  onChange={(e) => setNewEnvVar({...newEnvVar, value: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Variable value"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={newEnvVar.description}
                  onChange={(e) => setNewEnvVar({...newEnvVar, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  placeholder="Description of this variable"
                  rows={3}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Category
                  </label>
                  <select
                    value={newEnvVar.category}
                    onChange={(e) => setNewEnvVar({...newEnvVar, category: e.target.value as 'llm' | 'database' | 'api' | 'auth' | 'system' | 'integration'})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    {Object.entries(categoryConfig).map(([key, config]) => (
                      <option key={key} value={key}>{config.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Scope
                  </label>
                  <select
                    value={newEnvVar.scope}
                    onChange={(e) => setNewEnvVar({...newEnvVar, scope: e.target.value as 'global' | 'development' | 'staging' | 'production'})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    <option value="development">Development</option>
                    <option value="staging">Staging</option>
                    <option value="production">Production</option>
                    <option value="global">Global</option>
                  </select>
                </div>
              </div>
              
              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newEnvVar.isSecret}
                    onChange={(e) => setNewEnvVar({...newEnvVar, isSecret: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Secret</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newEnvVar.isRequired}
                    onChange={(e) => setNewEnvVar({...newEnvVar, isRequired: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Required</span>
                </label>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button variant="outline" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddEnvVar}>
                Add Variable
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
