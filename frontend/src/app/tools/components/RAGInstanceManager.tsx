'use client';

import React, { useState, useEffect } from 'react';
import {
  Upload,
  Search,
  FileText,
  Database,
  Settings,
  Activity,
  BarChart3,
  Trash2,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Info,
  ExternalLink,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import EnhancedDocumentUpload from './EnhancedDocumentUpload';

interface RAGInstanceManagerProps {
  instance: {
    id: string;
    name: string;
    description: string;
    configuration: Record<string, any>;
    status: string;
    template?: {
      type: string;
      name: string;
    };
  };
  onClose: () => void;
  onSave?: (updatedInstance: any) => void;
}

interface SearchResult {
  chunk_id: string;
  content: string;
  similarity_score: number;
  metadata: Record<string, any>;
  source_info: {
    filename: string;
    document_created_at?: string;
  };
}

interface RAGStatistics {
  total_documents: number;
  total_chunks: number;
  content_breakdown: Record<string, number>;
  avg_chunk_length: number;
  system_info: Record<string, any>;
}

export default function RAGInstanceManager({
  instance,
  onClose,
  onSave
}: RAGInstanceManagerProps) {
  const [activeTab, setActiveTab] = useState('documents');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [statistics, setStatistics] = useState<RAGStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search configuration
  const [searchTopK, setSearchTopK] = useState(5);
  const [searchContentTypes, setSearchContentTypes] = useState<string[]>(['text']);
  const [searchFilters, setSearchFilters] = useState<string>('{}');

  const isRAGInstance = instance.template?.type === 'rag' || 
                       instance.template?.name?.includes('rag') ||
                       instance.configuration?.database_url;

  useEffect(() => {
    if (isRAGInstance && activeTab === 'statistics') {
      fetchStatistics();
    }
  }, [activeTab, isRAGInstance]);

  const fetchStatistics = async () => {
    if (!isRAGInstance) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/tools/instances/${instance.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation: 'get_statistics'
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === 'success') {
          setStatistics(result.result);
        }
      }
    } catch (err) {
      console.error('Error fetching statistics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !isRAGInstance) return;

    setIsSearching(true);
    setError(null);
    
    try {
      let filters = {};
      if (searchFilters.trim()) {
        filters = JSON.parse(searchFilters);
      }

      const response = await fetch(`/api/tools/instances/${instance.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation: 'search',
          query: searchQuery,
          top_k: searchTopK,
          content_types: searchContentTypes,
          filters
        })
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        setSearchResults(result.result.results || []);
      } else {
        setError(result.error || 'Search failed');
        setSearchResults([]);
      }
    } catch (err) {
      setError('Failed to perform search');
      setSearchResults([]);
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDocumentUploadComplete = (results: any[]) => {
    // Refresh statistics after successful upload
    if (activeTab === 'statistics') {
      fetchStatistics();
    }
  };

  const handleDocumentUploadError = (error: string) => {
    setError(error);
  };

  const handleHealthCheck = async () => {
    if (!isRAGInstance) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/tools/instances/${instance.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation: 'health_check'
        })
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Health check passed! System is operational.');
      } else {
        setError(result.error || 'Health check failed');
      }
    } catch (err) {
      setError('Failed to perform health check');
      console.error('Health check error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isRAGInstance) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Not a RAG Instance
            </h2>
            <Button variant="ghost" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            This tool instance is not configured as a RAG system. RAG management features are only available for RAG-type tool instances.
          </p>
          <div className="flex justify-end">
            <Button onClick={onClose}>Close</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              RAG Instance Manager
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {instance.name} • {instance.description}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={instance.status === 'active' ? 'default' : 'secondary'}>
              {instance.status}
            </Badge>
            <Button variant="outline" onClick={handleHealthCheck} disabled={isLoading}>
              <Activity className="h-4 w-4 mr-2" />
              Health Check
            </Button>
            <Button variant="ghost" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {error && (
          <Alert className="m-6 mb-0">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="documents" className="flex items-center space-x-2">
                <Upload className="h-4 w-4" />
                <span>Documents</span>
              </TabsTrigger>
              <TabsTrigger value="search" className="flex items-center space-x-2">
                <Search className="h-4 w-4" />
                <span>Search</span>
              </TabsTrigger>
              <TabsTrigger value="statistics" className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>Statistics</span>
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center space-x-2">
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="documents" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Document Management</span>
                  </CardTitle>
                  <CardDescription>
                    Upload and manage documents in your RAG knowledge base
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <EnhancedDocumentUpload
                    pipelineId={instance.id}
                    onUploadComplete={handleDocumentUploadComplete}
                    onUploadError={handleDocumentUploadError}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="search" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Search className="h-5 w-5" />
                    <span>Knowledge Base Search</span>
                  </CardTitle>
                  <CardDescription>
                    Search through your indexed documents using semantic search
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex space-x-4">
                    <div className="flex-1">
                      <Label htmlFor="search-query">Search Query</Label>
                      <div className="flex space-x-2">
                        <Input
                          id="search-query"
                          placeholder="Enter your search query..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                        <Button onClick={handleSearch} disabled={isSearching || !searchQuery.trim()}>
                          {isSearching ? (
                            <RefreshCw className="h-4 w-4 animate-spin" />
                          ) : (
                            <Search className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="top-k">Results Count</Label>
                      <Input
                        id="top-k"
                        type="number"
                        min="1"
                        max="50"
                        value={searchTopK}
                        onChange={(e) => setSearchTopK(parseInt(e.target.value) || 5)}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="content-types">Content Types</Label>
                      <Select
                        value={searchContentTypes[0] || 'text'}
                        onValueChange={(value) => setSearchContentTypes([value])}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="text">Text</SelectItem>
                          <SelectItem value="table">Tables</SelectItem>
                          <SelectItem value="image">Images</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="filters">Filters (JSON)</Label>
                      <Input
                        id="filters"
                        placeholder="{}"
                        value={searchFilters}
                        onChange={(e) => setSearchFilters(e.target.value)}
                      />
                    </div>
                  </div>

                  {searchResults.length > 0 && (
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold">Search Results ({searchResults.length})</h3>
                      {searchResults.map((result, index) => (
                        <Card key={result.chunk_id} className="border-l-4 border-l-blue-500">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center space-x-2">
                                <Badge variant="outline">
                                  Score: {(result.similarity_score * 100).toFixed(1)}%
                                </Badge>
                                <Badge variant="secondary">
                                  {result.source_info.filename}
                                </Badge>
                              </div>
                              <Badge>
                                {result.metadata.content_type || 'text'}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                              {result.content}
                            </p>
                            <div className="text-xs text-gray-500 flex justify-between">
                              <span>Chunk ID: {result.chunk_id}</span>
                              {result.source_info.document_created_at && (
                                <span>Created: {new Date(result.source_info.document_created_at).toLocaleDateString()}</span>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="statistics" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-2">
                      <FileText className="h-8 w-8 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Documents</p>
                        <p className="text-2xl font-bold">{statistics?.total_documents || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-2">
                      <Database className="h-8 w-8 text-green-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Chunks</p>
                        <p className="text-2xl font-bold">{statistics?.total_chunks || 0}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-2">
                      <BarChart3 className="h-8 w-8 text-orange-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Length</p>
                        <p className="text-2xl font-bold">{Math.round(statistics?.avg_chunk_length || 0)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-8 w-8 text-emerald-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Status</p>
                        <p className="text-xl font-bold text-emerald-600">{instance.status}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {statistics?.content_breakdown && (
                <Card>
                  <CardHeader>
                    <CardTitle>Content Breakdown</CardTitle>
                    <CardDescription>Distribution of content types in your knowledge base</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(statistics.content_breakdown).map(([type, count]) => (
                        <div key={type} className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">{type}</Badge>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{
                                  width: `${(count / (statistics.total_chunks || 1)) * 100}%`
                                }}
                              />
                            </div>
                            <span className="font-medium w-16 text-right">{count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {statistics?.system_info && (
                <Card>
                  <CardHeader>
                    <CardTitle>System Information</CardTitle>
                    <CardDescription>RAG system configuration and capabilities</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(statistics.system_info).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400 capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="font-mono text-sm">
                            {typeof value === 'boolean' ? (value ? '✓' : '✗') : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="settings" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Instance Configuration</CardTitle>
                  <CardDescription>Current RAG instance settings</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(instance.configuration).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                        <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="font-mono text-sm max-w-xs truncate">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Actions</CardTitle>
                  <CardDescription>Manage your RAG instance</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex space-x-4">
                    <Button variant="outline" onClick={handleHealthCheck} disabled={isLoading}>
                      <Activity className="h-4 w-4 mr-2" />
                      Run Health Check
                    </Button>
                    <Button variant="outline" onClick={fetchStatistics} disabled={isLoading}>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh Statistics
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}