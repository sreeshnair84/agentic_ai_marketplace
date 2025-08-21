'use client';

import { useState, useEffect } from 'react';
import { 
  Search, Plus, Upload, FileText, Database, MoreHorizontal, 
  Settings2, Cloud, Activity, Target, Brain, Layers,
  HardDrive, CheckCircle, AlertCircle, Pause, Server,
  Workflow, Eye, BarChart3, Link
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { StandardPageLayout, StandardSection, StandardGrid } from '@/components/layout/StandardPageLayout';
import { useRAG } from '@/hooks/useRAG';

// Simple Progress component for this page
const Progress = ({ value, className }: { value: number; className?: string }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2 ${className || ''}`}>
    <div 
      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
      style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
    />
  </div>
);

export default function EnhancedRAGManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState<'overview' | 'collections' | 'tools' | 'processing' | 'infrastructure'>('overview');
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [createDialogType, setCreateDialogType] = useState<'collection' | 'tool' | 'job' | 'vector-db' | 'embedding-model' | 'cloud-bucket'>('collection');

  // Use RAG hooks
  const {
    knowledgeBases,
    loading: ragLoading,
    error: ragError,
    fetchKnowledgeBases,
    fetchDocuments,
    fetchSearchHistory,
    createKnowledgeBase,
    deleteKnowledgeBase,
    getDocument
  } = useRAG();

  // Mock data for enhanced features (since the hook provides a simpler interface)
  // These would need to be implemented in the backend/API
  const vectorDatabases = [
    {
      id: 'vdb-1',
      name: 'Primary PGVector',
      type: 'pgvector',
      provider: 'postgresql',
      status: 'connected',
      collections: [],
      dimensions: 1536,
      maxCollections: 100,
      createdAt: new Date('2024-01-01'),
      lastSync: new Date()
    }
  ];

  const collections = knowledgeBases.map(kb => ({
    id: kb.id,
    name: kb.name,
    description: kb.description,
    embeddingModel: 'text-embedding-3-small',
    vectorDatabaseId: 'vdb-1',
    dimensions: 1536,
    documentCount: kb.stats.total_documents,
    status: kb.status === 'active' ? 'active' : 'inactive',
    metadata: {
      totalDocuments: kb.stats.total_documents,
      totalChunks: kb.stats.total_chunks,
      avgChunkSize: 512,
      tags: [] // KB doesn't have tags in this interface
    },
    createdAt: new Date(kb.created_at),
    lastIndexed: new Date(kb.updated_at)
  }));

  const embeddingModels = [
    {
      id: 'em-1',
      name: 'text-embedding-3-small',
      displayName: 'OpenAI Text Embedding 3 Small',
      provider: 'openai',
      dimensions: 1536,
      maxTokens: 8191,
      costPerToken: 0.00002,
      isActive: true,
      supportedLanguages: ['en', 'es', 'fr', 'de'],
      tags: ['general', 'fast', 'cost-effective']
    }
  ];

  const cloudBuckets: any[] = [];
  const processingJobs: any[] = [];
  const ragTools: any[] = [];

  // Fetch data on component mount
  useEffect(() => {
    fetchKnowledgeBases();
    fetchDocuments();
    fetchSearchHistory();
  }, [fetchKnowledgeBases, fetchDocuments, fetchSearchHistory]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'running':
      case 'connected':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'processing':
      case 'indexing':
      case 'configuring':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'inactive':
      case 'stopped':
      case 'disconnected':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'postgresql':
      case 'pgvector':
        return <Database className="h-4 w-4" />;
      case 'chroma':
      case 'chromadb':
        return <Layers className="h-4 w-4" />;
      case 'pinecone':
        return <Target className="h-4 w-4" />;
      case 'openai':
        return <Brain className="h-4 w-4" />;
      case 'aws-s3':
        return <Cloud className="h-4 w-4" />;
      case 'azure-blob':
        return <Server className="h-4 w-4" />;
      default:
        return <HardDrive className="h-4 w-4" />;
    }
  };

  const filteredCollections = collections.filter(collection =>
    collection.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    collection.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Show loading state
  if (ragLoading) {
    return (
      <StandardPageLayout
        title="Enhanced RAG Management"
        description="Advanced document processing with vector databases, embedding models, and cloud integration"
      >
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-muted-foreground">Loading RAG data...</span>
          </div>
        </div>
      </StandardPageLayout>
    );
  }

  // Show error state
  if (ragError) {
    return (
      <StandardPageLayout
        title="Enhanced RAG Management"
        description="Advanced document processing with vector databases, embedding models, and cloud integration"
      >
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading RAG Data</h3>
            <p className="text-gray-600 mb-4">
              {ragError || 'An unexpected error occurred'}
            </p>
            <Button onClick={() => window.location.reload()}>
              Try Again
            </Button>
          </div>
        </div>
      </StandardPageLayout>
    );
  }

  // Action handlers
  const handleCreateDatabase = async (data: any) => {
    try {
      console.log('Create vector database:', data);
      // This would need to be implemented in the backend
    } catch (error) {
      console.error('Failed to create vector database:', error);
    }
  };

  const handleCreateCollection = async (data: any) => {
    try {
      await createKnowledgeBase(data);
      setShowCreateDialog(false);
    } catch (error) {
      console.error('Failed to create collection:', error);
    }
  };

  const handleStartProcessing = async (jobId: string) => {
    try {
      console.log('Start processing:', jobId);
      // This would need to be implemented in the backend
    } catch (error) {
      console.error('Failed to start processing:', error);
    }
  };

  const handleStopProcessing = async (jobId: string) => {
    try {
      console.log('Stop processing:', jobId);
      // This would need to be implemented in the backend
    } catch (error) {
      console.error('Failed to stop processing:', error);
    }
  };

  const handleDeleteCollection = async (collectionId: string) => {
    try {
      await deleteKnowledgeBase(collectionId);
    } catch (error) {
      console.error('Failed to delete collection:', error);
    }
  };

  const handleDeleteDatabase = async (databaseId: string) => {
    try {
      console.log('Delete database:', databaseId);
      // This would need to be implemented in the backend
    } catch (error) {
      console.error('Failed to delete database:', error);
    }
  };

  const handleTestRAGTool = async (toolId: string) => {
    try {
      console.log('Test RAG tool:', toolId);
      // This would need to be implemented in the backend
    } catch (error) {
      console.error('Failed to test RAG tool:', error);
    }
  };

  return (
    <StandardPageLayout
      title="Enhanced RAG Management"
      description="Advanced document processing with vector databases, embedding models, and cloud integration"
      actions={
        <div className="flex space-x-3">
          <Button 
            variant="outline" 
            onClick={() => {
              setCreateDialogType('job');
              setShowCreateDialog(true);
            }}
            className="flex items-center space-x-2"
          >
            <Workflow className="h-4 w-4" />
            <span>New Processing Job</span>
          </Button>
          <Button 
            onClick={() => {
              setCreateDialogType('collection');
              setShowCreateDialog(true);
            }}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Create Collection</span>
          </Button>
        </div>
      }
    >

      {/* Main Tabs */}
      <StandardSection>
        <Tabs value={selectedTab} onValueChange={(value) => setSelectedTab(value as 'overview' | 'collections' | 'tools' | 'processing' | 'infrastructure')}>
          <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="collections" className="flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Collections
          </TabsTrigger>
          <TabsTrigger value="tools" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            RAG Tools
          </TabsTrigger>
          <TabsTrigger value="processing" className="flex items-center gap-2">
            <Workflow className="h-4 w-4" />
            Processing
          </TabsTrigger>
          <TabsTrigger value="infrastructure" className="flex items-center gap-2">
            <Server className="h-4 w-4" />
            Infrastructure
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Collections</CardTitle>
                <Layers className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{collections.length}</div>
                <p className="text-xs text-muted-foreground">
                  {collections.filter(c => c.status === 'active').length} active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Documents</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {collections.reduce((sum, c) => sum + c.documentCount, 0).toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  Across all collections
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Vector DBs</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{vectorDatabases.length}</div>
                <p className="text-xs text-muted-foreground">
                  {vectorDatabases.filter(db => db.status === 'connected').length} connected
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Processing Jobs</CardTitle>
                <Workflow className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{processingJobs.length}</div>
                <p className="text-xs text-muted-foreground">
                  {processingJobs.filter(j => j.status === 'running').length} running
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Active Processing Jobs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 h-5" />
                Active Processing Jobs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {processingJobs.filter(job => job.status === 'running').map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{job.name}</h4>
                      <p className="text-sm text-muted-foreground">{job.description}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <Progress value={job.progress} className="w-32" />
                        <span className="text-sm">{job.progress}%</span>
                        <span className="text-sm text-muted-foreground">
                          {job.processedDocuments}/{job.totalDocuments} documents
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleStopProcessing(job.id)}
                      >
                        <Pause className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Collections Tab */}
        <TabsContent value="collections" className="space-y-6">
          <div className="flex justify-between items-center">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search collections..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-96"
              />
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Upload Documents
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Collection
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredCollections.map((collection) => (
              <Card 
                key={collection.id} 
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedCollection === collection.id ? 'ring-2 ring-blue-500 border-blue-500' : ''
                }`}
                onClick={() => setSelectedCollection(collection.id)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="flex items-center justify-center w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg">
                        {getProviderIcon(collection.vectorDatabaseId)}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-lg">{collection.name}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                          {collection.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Settings2 className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(collection.status)}`}>
                        {collection.status}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {collection.documentCount.toLocaleString()} docs
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Chunks</p>
                        <p className="font-medium">{collection.metadata.totalChunks?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Dimensions</p>
                        <p className="font-medium">{collection.dimensions}</p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {collection.metadata.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Tools Tab */}
        <TabsContent value="tools" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">RAG Tools</h2>
              <p className="text-muted-foreground">Configure and manage your RAG tools and search interfaces</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Link className="h-4 w-4 mr-2" />
                Link Collections
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Tool
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {ragTools.map((tool) => (
              <Card key={tool.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="flex items-center justify-center w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg">
                        <Brain className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-lg">{tool.name}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                          {tool.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={tool.isActive ? 'default' : 'secondary'}>
                        {tool.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Settings2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Total Queries</p>
                        <p className="font-medium">{tool.usage?.totalQueries.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Success Rate</p>
                        <p className="font-medium">
                          {tool.usage ? Math.round((tool.usage.successfulQueries / tool.usage.totalQueries) * 100) : 0}%
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Avg Response</p>
                        <p className="font-medium">{tool.usage?.averageResponseTime}ms</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Collections</p>
                        <p className="font-medium">{tool.collections.length}</p>
                      </div>
                    </div>

                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Linked Collections</p>
                      <div className="flex flex-wrap gap-1">
                        {tool.collections?.map((collectionId: string) => {
                          const collection = collections.find(c => c.id === collectionId);
                          return collection ? (
                            <Badge key={collectionId} variant="outline" className="text-xs">
                              {collection.name}
                            </Badge>
                          ) : null;
                        })}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Processing Tab */}
        <TabsContent value="processing" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Document Processing</h2>
              <p className="text-muted-foreground">Manage document processing jobs with Docling integration</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <Cloud className="h-4 w-4 mr-2" />
                Configure Buckets
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Job
              </Button>
            </div>
          </div>

          <div className="space-y-6">
            {processingJobs.map((job: any) => (
              <Card key={job.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        {job.name}
                        <Badge className={getStatusColor(job.status)}>
                          {job.status}
                        </Badge>
                      </CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        {job.description}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {job.status === 'running' && (
                        <Button variant="outline" size="sm">
                          <Pause className="h-4 w-4" />
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Settings2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Progress Bar */}
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Progress</span>
                        <span>{job.progress}%</span>
                      </div>
                      <Progress value={job.progress} />
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>{job.processedDocuments} processed</span>
                        <span>{job.totalDocuments} total</span>
                        <span>{job.failedDocuments} failed</span>
                      </div>
                    </div>

                    {/* Configuration Details */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Docling</p>
                        <p className="font-medium flex items-center gap-1">
                          {job.configuration.useDocling ? (
                            <>
                              <CheckCircle className="h-3 w-3 text-green-500" />
                              Enabled
                            </>
                          ) : (
                            <>
                              <AlertCircle className="h-3 w-3 text-gray-500" />
                              Disabled
                            </>
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Extract Tables</p>
                        <p className="font-medium flex items-center gap-1">
                          {job.configuration.extractTables ? (
                            <>
                              <CheckCircle className="h-3 w-3 text-green-500" />
                              Yes
                            </>
                          ) : (
                            <>
                              <AlertCircle className="h-3 w-3 text-gray-500" />
                              No
                            </>
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Chunk Size</p>
                        <p className="font-medium">{job.configuration.chunkSize}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Strategy</p>
                        <p className="font-medium">{job.configuration.chunkingStrategy}</p>
                      </div>
                    </div>

                    {/* Source and Target */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Source</h4>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">
                            <span className="text-muted-foreground">Type:</span> {job.source.type}
                          </p>
                          {job.source.cloudBucketId && (
                            <p className="text-sm">
                              <span className="text-muted-foreground">Bucket:</span>{' '}
                              {cloudBuckets.find(b => b.id === job.source.cloudBucketId)?.name}
                            </p>
                          )}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Target</h4>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-sm">
                            <span className="text-muted-foreground">Collection:</span>{' '}
                            {collections.find(c => c.id === job.target.collectionId)?.name}
                          </p>
                          <p className="text-sm">
                            <span className="text-muted-foreground">Vector DB:</span>{' '}
                            {vectorDatabases.find(db => db.id === job.target.vectorDatabaseId)?.name}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Infrastructure Tab */}
        <TabsContent value="infrastructure" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Vector Databases */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Vector Databases
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {vectorDatabases.map((db) => (
                    <div key={db.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded">
                          {getProviderIcon(db.provider)}
                        </div>
                        <div>
                          <p className="font-medium">{db.name}</p>
                          <p className="text-sm text-muted-foreground">{db.type}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(db.status)}>
                          {db.status}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          <Settings2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Vector Database
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Embedding Models */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  Embedding Models
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {embeddingModels.map((model) => (
                    <div key={model.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded">
                          {getProviderIcon(model.provider)}
                        </div>
                        <div>
                          <p className="font-medium">{model.displayName}</p>
                          <p className="text-sm text-muted-foreground">{model.dimensions}D</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={model.isActive ? 'default' : 'secondary'}>
                          {model.isActive ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          <Settings2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Embedding Model
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Cloud Buckets */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cloud className="h-5 w-5" />
                  Cloud Storage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {cloudBuckets.map((bucket) => (
                    <div key={bucket.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-8 h-8 bg-green-100 dark:bg-green-900 rounded">
                          {getProviderIcon(bucket.provider)}
                        </div>
                        <div>
                          <p className="font-medium">{bucket.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {bucket.documentsCount} documents
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={bucket.isActive ? 'default' : 'secondary'}>
                          {bucket.isActive ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          <Settings2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Cloud Bucket
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Create Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              Create New {createDialogType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </DialogTitle>
            <DialogDescription>
              Configure your new {createDialogType.replace('-', ' ')} with the settings below.
            </DialogDescription>
          </DialogHeader>
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              Creation form for {createDialogType} would be implemented here
            </p>
          </div>
        </DialogContent>
      </Dialog>
      </StandardSection>
    </StandardPageLayout>
  );
}
