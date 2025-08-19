'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  Save, 
  Trash2,
  Database,
  FileText,
  Globe,
  Settings,
  CheckCircle,
  AlertCircle,
  Search,
  Layers,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface DataSource {
  id?: string;
  name: string;
  type: 'file_upload' | 'web_scraping' | 'database' | 'api';
  configuration: Record<string, unknown>;
  status: 'pending' | 'processing' | 'ready' | 'error';
  metadata?: Record<string, unknown>;
}

interface VectorizationConfig {
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  text_splitter: 'recursive' | 'character' | 'semantic';
  metadata_extraction: boolean;
  custom_embeddings?: boolean;
}

interface RetrievalConfig {
  retrieval_strategy: 'similarity' | 'mmr' | 'hybrid';
  top_k: number;
  similarity_threshold: number;
  reranking: boolean;
  reranker_model?: string;
  query_expansion: boolean;
}

interface RAGPipeline {
  id?: string;
  name: string;
  description: string;
  data_sources: DataSource[];
  vectorization_config: VectorizationConfig;
  retrieval_config: RetrievalConfig;
  status: 'draft' | 'building' | 'ready' | 'error';
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

interface RAGPipelineBuilderProps {
  pipeline?: RAGPipeline;
  onSave: (pipeline: RAGPipeline) => void;
  onCancel: () => void;
}

interface FieldConfig {
  type: string;
  label: string;
  required?: boolean;
  secret?: boolean;
  default?: string | number | boolean;
  min?: number;
  max?: number;
  options?: string[];
}

interface DataSourceTypeConfig {
  icon: React.ReactElement;
  label: string;
  description: string;
  supportedFormats: string[];
  fields: Record<string, FieldConfig>;
}

const dataSourceTypeConfig: Record<string, DataSourceTypeConfig> = {
  file_upload: {
    icon: <FileText className="h-5 w-5 text-blue-600" />,
    label: 'File Upload',
    description: 'Upload documents, PDFs, text files',
    supportedFormats: ['PDF', 'DOCX', 'TXT', 'MD', 'CSV'],
    fields: {
      file_paths: { type: 'array', label: 'File Paths', required: true },
      file_types: { type: 'multiselect', label: 'Supported Types', options: ['pdf', 'docx', 'txt', 'md', 'csv'] },
      auto_extract_metadata: { type: 'boolean', label: 'Auto Extract Metadata', default: true }
    }
  },
  web_scraping: {
    icon: <Globe className="h-5 w-5 text-green-600" />,
    label: 'Web Scraping',
    description: 'Scrape content from websites',
    supportedFormats: ['HTML', 'XML', 'RSS'],
    fields: {
      urls: { type: 'array', label: 'URLs', required: true },
      depth: { type: 'number', label: 'Crawl Depth', default: 1, min: 1, max: 5 },
      selectors: { type: 'array', label: 'CSS Selectors (Optional)' },
      respect_robots: { type: 'boolean', label: 'Respect robots.txt', default: true }
    }
  },
  database: {
    icon: <Database className="h-5 w-5 text-purple-600" />,
    label: 'Database',
    description: 'Connect to SQL or NoSQL databases',
    supportedFormats: ['PostgreSQL', 'MySQL', 'MongoDB', 'Elasticsearch'],
    fields: {
      connection_string: { type: 'text', label: 'Connection String', required: true, secret: true },
      query: { type: 'textarea', label: 'Query', required: true },
      text_columns: { type: 'array', label: 'Text Columns', required: true },
      batch_size: { type: 'number', label: 'Batch Size', default: 1000 }
    }
  },
  api: {
    icon: <Zap className="h-5 w-5 text-orange-600" />,
    label: 'API',
    description: 'Fetch data from REST APIs',
    supportedFormats: ['JSON', 'XML', 'CSV'],
    fields: {
      endpoint: { type: 'text', label: 'API Endpoint', required: true },
      headers: { type: 'object', label: 'Headers' },
      auth_type: { type: 'select', label: 'Auth Type', options: ['none', 'bearer', 'basic', 'api_key'] },
      auth_config: { type: 'object', label: 'Auth Configuration' },
      response_path: { type: 'text', label: 'Response Data Path' }
    }
  }
};

const embeddingModels = [
  { value: 'text-embedding-3-small', label: 'OpenAI Text Embedding 3 Small', dimensions: 1536 },
  { value: 'text-embedding-3-large', label: 'OpenAI Text Embedding 3 Large', dimensions: 3072 },
  { value: 'text-embedding-ada-002', label: 'OpenAI Text Embedding Ada 002', dimensions: 1536 },
  { value: 'sentence-transformers/all-MiniLM-L6-v2', label: 'Sentence Transformers Mini', dimensions: 384 },
  { value: 'sentence-transformers/all-mpnet-base-v2', label: 'Sentence Transformers MPNet', dimensions: 768 }
];

export default function RAGPipelineBuilder({ 
  pipeline, 
  onSave, 
  onCancel 
}: RAGPipelineBuilderProps) {
  const [formData, setFormData] = useState<RAGPipeline>({
    name: '',
    description: '',
    data_sources: [],
    vectorization_config: {
      embedding_model: 'text-embedding-3-small',
      chunk_size: 1000,
      chunk_overlap: 200,
      text_splitter: 'recursive',
      metadata_extraction: true
    },
    retrieval_config: {
      retrieval_strategy: 'similarity',
      top_k: 5,
      similarity_threshold: 0.7,
      reranking: false,
      query_expansion: false
    },
    status: 'draft'
  });

  const [activeTab, setActiveTab] = useState('basic');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [buildProgress, setBuildProgress] = useState<number>(0);
  const [testResults, setTestResults] = useState<{
    status: string;
    message: string;
    test_query?: string;
    results?: Array<{ chunk: string; score: number }>;
    metrics?: Record<string, string | number>;
  } | null>(null);

  useEffect(() => {
    if (pipeline) {
      setFormData(pipeline);
    }
  }, [pipeline]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleVectorizationConfigChange = (field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      vectorization_config: {
        ...prev.vectorization_config,
        [field]: value
      }
    }));
  };

  const handleRetrievalConfigChange = (field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      retrieval_config: {
        ...prev.retrieval_config,
        [field]: value
      }
    }));
  };

  const addDataSource = (type: string) => {
    const newDataSource: DataSource = {
      id: `ds_${Date.now()}`,
      name: `New ${dataSourceTypeConfig[type as keyof typeof dataSourceTypeConfig].label}`,
      type: type as any,
      configuration: {},
      status: 'pending'
    };
    
    setFormData(prev => ({
      ...prev,
      data_sources: [...prev.data_sources, newDataSource]
    }));
  };

  const updateDataSource = (index: number, updates: Partial<DataSource>) => {
    setFormData(prev => ({
      ...prev,
      data_sources: prev.data_sources.map((ds, i) => 
        i === index ? { ...ds, ...updates } : ds
      )
    }));
  };

  const removeDataSource = (index: number) => {
    setFormData(prev => ({
      ...prev,
      data_sources: prev.data_sources.filter((_, i) => i !== index)
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Pipeline name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    if (formData.data_sources.length === 0) {
      newErrors.data_sources = 'At least one data source is required';
    }

    // Validate data sources
    formData.data_sources.forEach((ds, index) => {
      const config = dataSourceTypeConfig[ds.type];
      if (config) {
        Object.entries(config.fields).forEach(([field, fieldConfig]) => {
          if (fieldConfig.required && !ds.configuration[field]) {
            newErrors[`ds_${index}_${field}`] = `${fieldConfig.label} is required`;
          }
        });
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const buildPipeline = async () => {
    if (!validateForm()) return;

    setBuildProgress(0);
    setFormData(prev => ({ ...prev, status: 'building' }));

    // Simulate build process
    const steps = [
      'Validating data sources...',
      'Setting up vectorization...',
      'Configuring retrieval...',
      'Building pipeline...',
      'Testing configuration...'
    ];

    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setBuildProgress(((i + 1) / steps.length) * 100);
    }

    setFormData(prev => ({ ...prev, status: 'ready' }));
    setTestResults({
      status: 'success',
      message: 'Pipeline built successfully',
      metrics: {
        total_documents: 1250,
        total_chunks: 5678,
        average_chunk_size: 875,
        embedding_time: '2.3s',
        index_size: '45MB'
      }
    });
  };

  const testPipeline = async () => {
    setTestResults({ status: 'testing', message: 'Testing pipeline configuration...' });
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setTestResults({
      status: 'success',
      message: 'Pipeline test completed',
      test_query: 'What is machine learning?',
      results: [
        { chunk: 'Machine learning is a subset of artificial intelligence...', score: 0.92 },
        { chunk: 'ML algorithms learn patterns from data...', score: 0.87 },
        { chunk: 'Types of machine learning include supervised...', score: 0.84 }
      ]
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSave(formData);
    }
  };

  const renderDataSourceConfiguration = (dataSource: DataSource, index: number) => {
    const config = dataSourceTypeConfig[dataSource.type];
    if (!config) return null;

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Data Source Name
          </label>
          <input
            type="text"
            value={dataSource.name}
            onChange={(e) => updateDataSource(index, { name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
        </div>

        {Object.entries(config.fields).map(([field, fieldConfig]) => (
          <div key={field}>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {fieldConfig.label}
              {fieldConfig.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            {fieldConfig.type === 'text' && (
              <input
                type={fieldConfig.secret ? 'password' : 'text'}
                value={String(dataSource.configuration[field] || '')}
                onChange={(e) => updateDataSource(index, {
                  configuration: { ...dataSource.configuration, [field]: e.target.value }
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            )}
            
            {fieldConfig.type === 'textarea' && (
              <textarea
                value={String(dataSource.configuration[field] || '')}
                onChange={(e) => updateDataSource(index, {
                  configuration: { ...dataSource.configuration, [field]: e.target.value }
                })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            )}
            
            {fieldConfig.type === 'number' && (
              <input
                type="number"
                min={fieldConfig.min}
                max={fieldConfig.max}
                value={Number(dataSource.configuration[field] || fieldConfig.default || 0)}
                onChange={(e) => updateDataSource(index, {
                  configuration: { ...dataSource.configuration, [field]: parseInt(e.target.value) }
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            )}
            
            {fieldConfig.type === 'boolean' && (
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={Boolean(dataSource.configuration[field] || fieldConfig.default || false)}
                  onChange={(e) => updateDataSource(index, {
                    configuration: { ...dataSource.configuration, [field]: e.target.checked }
                  })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-600 dark:text-gray-400">Enable</span>
              </label>
            )}
            
            {fieldConfig.type === 'select' && (
              <select
                value={String(dataSource.configuration[field] || '')}
                onChange={(e) => updateDataSource(index, {
                  configuration: { ...dataSource.configuration, [field]: e.target.value }
                })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="">Select {fieldConfig.label}</option>
                {fieldConfig.options?.map((option: string) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            )}
            
            {errors[`ds_${index}_${field}`] && (
              <p className="text-red-500 text-sm mt-1">{errors[`ds_${index}_${field}`]}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          {pipeline ? 'Edit RAG Pipeline' : 'Create RAG Pipeline'}
        </h2>
        <Button variant="ghost" onClick={onCancel}>
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Content */}
      <div className="overflow-y-auto p-6" style={{ maxHeight: 'calc(90vh - 140px)' }}>
        <form onSubmit={handleSubmit} className="space-y-6">
          
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="data">Data Sources</TabsTrigger>
              <TabsTrigger value="vectorization">Vectorization</TabsTrigger>
              <TabsTrigger value="retrieval">Retrieval</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Pipeline Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    placeholder="e.g., Knowledge Base RAG Pipeline"
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
                    <option value="draft">Draft</option>
                    <option value="building">Building</option>
                    <option value="ready">Ready</option>
                    <option value="error">Error</option>
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
                  placeholder="Describe the purpose and scope of this RAG pipeline..."
                />
                {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
              </div>

              {/* Build Progress */}
              {formData.status === 'building' && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <Settings className="h-5 w-5 text-blue-600 animate-spin" />
                    <span className="font-medium text-blue-900 dark:text-blue-100">
                      Building Pipeline...
                    </span>
                  </div>
                  <Progress value={buildProgress} className="w-full" />
                  <p className="text-sm text-blue-700 dark:text-blue-300 mt-2">
                    {buildProgress.toFixed(0)}% complete
                  </p>
                </div>
              )}

              {/* Test Results */}
              {testResults && (
                <div className={`border rounded-lg p-4 ${
                  testResults.status === 'success' ? 'border-green-200 bg-green-50 dark:bg-green-900/20' :
                  testResults.status === 'error' ? 'border-red-200 bg-red-50 dark:bg-red-900/20' :
                  'border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20'
                }`}>
                  <div className="flex items-start space-x-3">
                    {testResults.status === 'testing' && (
                      <Settings className="h-5 w-5 text-yellow-600 animate-spin mt-0.5" />
                    )}
                    {testResults.status === 'success' && (
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    )}
                    {testResults.status === 'error' && (
                      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <h4 className="font-medium">
                        {testResults.status === 'testing' ? 'Testing Pipeline...' : 
                         testResults.status === 'success' ? 'Test Results' : 'Test Failed'}
                      </h4>
                      <p className="text-sm mt-1">{testResults.message}</p>
                      
                      {testResults.metrics && (
                        <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          {Object.entries(testResults.metrics).map(([key, value]) => (
                            <div key={key}>
                              <span className="font-medium">{key.replace(/_/g, ' ')}:</span>
                              <span className="ml-1">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {testResults.results && (
                        <div className="mt-3">
                          <p className="font-medium text-sm mb-2">Test Query: &quot;{testResults.test_query}&quot;</p>
                          <div className="space-y-2">
                            {testResults.results.map((result: any, index: number) => (
                              <div key={index} className="bg-white dark:bg-gray-800 rounded p-3 border">
                                <div className="flex justify-between items-start mb-1">
                                  <span className="text-sm font-medium">Result {index + 1}</span>
                                  <Badge variant="secondary">{result.score.toFixed(2)}</Badge>
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  {result.chunk}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="data" className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Data Sources
                </h3>
                <div className="flex items-center space-x-2">
                  {Object.entries(dataSourceTypeConfig).map(([type, config]) => (
                    <Button
                      key={type}
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => addDataSource(type)}
                      className="flex items-center space-x-2"
                    >
                      {config.icon}
                      <span>{config.label}</span>
                    </Button>
                  ))}
                </div>
              </div>

              {formData.data_sources.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                  <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    No data sources configured
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Add data sources to begin building your RAG pipeline
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {formData.data_sources.map((dataSource, index) => {
                    const config = dataSourceTypeConfig[dataSource.type];
                    return (
                      <Card key={dataSource.id || index}>
                        <CardHeader className="pb-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              {config.icon}
                              <div>
                                <CardTitle className="text-base">{dataSource.name}</CardTitle>
                                <CardDescription>{config.label}</CardDescription>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge variant={
                                dataSource.status === 'ready' ? 'default' :
                                dataSource.status === 'error' ? 'destructive' :
                                'secondary'
                              }>
                                {dataSource.status}
                              </Badge>
                              <Button
                                type="button"
                                size="sm"
                                variant="ghost"
                                onClick={() => removeDataSource(index)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          {renderDataSourceConfiguration(dataSource, index)}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
              
              {errors.data_sources && <p className="text-red-500 text-sm">{errors.data_sources}</p>}
            </TabsContent>

            <TabsContent value="vectorization" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Embedding Model
                  </label>
                  <select
                    value={formData.vectorization_config.embedding_model}
                    onChange={(e) => handleVectorizationConfigChange('embedding_model', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    {embeddingModels.map(model => (
                      <option key={model.value} value={model.value}>
                        {model.label} ({model.dimensions}d)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Text Splitter
                  </label>
                  <select
                    value={formData.vectorization_config.text_splitter}
                    onChange={(e) => handleVectorizationConfigChange('text_splitter', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    <option value="recursive">Recursive Character Text Splitter</option>
                    <option value="character">Character Text Splitter</option>
                    <option value="semantic">Semantic Text Splitter</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Chunk Size
                  </label>
                  <input
                    type="number"
                    min="100"
                    max="8000"
                    value={formData.vectorization_config.chunk_size}
                    onChange={(e) => handleVectorizationConfigChange('chunk_size', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Chunk Overlap
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1000"
                    value={formData.vectorization_config.chunk_overlap}
                    onChange={(e) => handleVectorizationConfigChange('chunk_overlap', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="metadata_extraction"
                  checked={formData.vectorization_config.metadata_extraction}
                  onChange={(e) => handleVectorizationConfigChange('metadata_extraction', e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="metadata_extraction" className="text-sm text-gray-700 dark:text-gray-300">
                  Enable metadata extraction during vectorization
                </label>
              </div>
            </TabsContent>

            <TabsContent value="retrieval" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Retrieval Strategy
                  </label>
                  <select
                    value={formData.retrieval_config.retrieval_strategy}
                    onChange={(e) => handleRetrievalConfigChange('retrieval_strategy', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    <option value="similarity">Similarity Search</option>
                    <option value="mmr">Maximal Marginal Relevance</option>
                    <option value="hybrid">Hybrid Search</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Top K Results
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={formData.retrieval_config.top_k}
                    onChange={(e) => handleRetrievalConfigChange('top_k', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Similarity Threshold
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={formData.retrieval_config.similarity_threshold}
                    onChange={(e) => handleRetrievalConfigChange('similarity_threshold', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>

                {formData.retrieval_config.reranking && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Reranker Model
                    </label>
                    <select
                      value={formData.retrieval_config.reranker_model || ''}
                      onChange={(e) => handleRetrievalConfigChange('reranker_model', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      <option value="">Select Reranker</option>
                      <option value="cross-encoder/ms-marco-MiniLM-L-6-v2">Cross-Encoder MiniLM</option>
                      <option value="cross-encoder/ms-marco-electra-base">Cross-Encoder Electra</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="reranking"
                    checked={formData.retrieval_config.reranking}
                    onChange={(e) => handleRetrievalConfigChange('reranking', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="reranking" className="text-sm text-gray-700 dark:text-gray-300">
                    Enable result reranking for improved relevance
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="query_expansion"
                    checked={formData.retrieval_config.query_expansion}
                    onChange={(e) => handleRetrievalConfigChange('query_expansion', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="query_expansion" className="text-sm text-gray-700 dark:text-gray-300">
                    Enable query expansion for better recall
                  </label>
                </div>
              </div>
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
      <div className="flex justify-between p-6 border-t border-gray-200 dark:border-gray-700">
        <div className="flex space-x-3">
          <Button
            type="button"
            variant="outline"
            onClick={buildPipeline}
            disabled={formData.status === 'building' || formData.data_sources.length === 0}
          >
            <Layers className="h-4 w-4 mr-2" />
            Build Pipeline
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={testPipeline}
            disabled={formData.status !== 'ready'}
          >
            <Search className="h-4 w-4 mr-2" />
            Test Pipeline
          </Button>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit}
            disabled={formData.data_sources.length === 0}
          >
            <Save className="h-4 w-4 mr-2" />
            Save Pipeline
          </Button>
        </div>
      </div>
    </>
  );
}
