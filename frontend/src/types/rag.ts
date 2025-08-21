// Enhanced RAG types for the redesigned UI
export interface VectorDatabase {
  id: string;
  name: string;
  type: 'pgvector' | 'chromadb' | 'pinecone' | 'weaviate' | 'qdrant';
  provider: 'postgresql' | 'chroma' | 'pinecone' | 'weaviate' | 'qdrant';
  status: 'connected' | 'disconnected' | 'error' | 'configuring';
  configuration: VectorDatabaseConfig;
  collections: Collection[];
  dimensions: number;
  maxCollections: number;
  createdAt: Date;
  lastSync: Date;
}

export interface VectorDatabaseConfig {
  connectionString?: string;
  host?: string;
  port?: number;
  apiKey?: string;
  region?: string;
  index?: string;
  namespace?: string;
  ssl?: boolean;
  timeout?: number;
  [key: string]: unknown;
}

export interface Collection {
  id: string;
  name: string;
  description?: string;
  embeddingModel: string;
  vectorDatabaseId: string;
  dimensions: number;
  documentCount: number;
  status: 'active' | 'indexing' | 'error' | 'maintenance';
  metadata: CollectionMetadata;
  createdAt: Date;
  lastIndexed: Date;
}

export interface CollectionMetadata {
  totalDocuments: number;
  totalChunks: number;
  avgChunkSize: number;
  indexingProgress?: number;
  lastOptimized?: Date;
  tags: string[];
}

export interface EmbeddingModel {
  id: string;
  name: string;
  displayName: string;
  provider: 'openai' | 'azure-openai' | 'huggingface' | 'google' | 'cohere' | 'local';
  dimensions: number;
  maxTokens: number;
  costPerToken: number;
  isActive: boolean;
  configuration: EmbeddingModelConfig;
  supportedLanguages: string[];
  tags: string[];
}

export interface EmbeddingModelConfig {
  apiKey?: string;
  endpoint?: string;
  modelName?: string;
  deploymentName?: string;
  apiVersion?: string;
  timeout?: number;
  batchSize?: number;
  [key: string]: unknown;
}

export interface CloudBucket {
  id: string;
  name: string;
  provider: 'aws-s3' | 'azure-blob' | 'google-cloud-storage' | 'minio';
  region?: string;
  endpoint?: string;
  accessKey?: string;
  secretKey?: string;
  containerName?: string;
  bucketName?: string;
  prefix?: string;
  isActive: boolean;
  lastSync?: Date;
  documentsCount: number;
}

export interface DocumentProcessingJob {
  id: string;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  totalDocuments: number;
  processedDocuments: number;
  failedDocuments: number;
  source: DocumentSource;
  target: ProcessingTarget;
  configuration: ProcessingConfiguration;
  startedAt?: Date;
  completedAt?: Date;
  estimatedDuration?: number;
  logs: ProcessingLog[];
  error?: string;
}

export interface DocumentSource {
  type: 'upload' | 'cloud-bucket' | 'url' | 'api';
  cloudBucketId?: string;
  urls?: string[];
  files?: File[];
  apiEndpoint?: string;
  filters?: DocumentFilter[];
}

export interface ProcessingTarget {
  collectionId: string;
  embeddingModelId: string;
  vectorDatabaseId: string;
  namespace?: string;
  overwriteExisting: boolean;
}

export interface ProcessingConfiguration {
  useDocling: boolean;
  extractTables: boolean;
  extractImages: boolean;
  extractMetadata: boolean;
  llmPreprocessing: boolean;
  llmModelId?: string;
  chunkSize: number;
  chunkOverlap: number;
  chunkingStrategy: 'fixed' | 'semantic' | 'sentence' | 'paragraph';
  separateTables: boolean;
  separateImages: boolean;
  preprocessing: {
    removeHeaders: boolean;
    removeFooters: boolean;
    normalizeText: boolean;
    removeExtraSpaces: boolean;
    splitByParagraphs: boolean;
  };
  filters: {
    minChunkLength: number;
    maxChunkLength: number;
    excludePatterns: string[];
    includePatterns: string[];
  };
}

export interface DocumentFilter {
  field: 'filename' | 'extension' | 'size' | 'modified' | 'path';
  operator: 'equals' | 'contains' | 'starts_with' | 'ends_with' | 'greater_than' | 'less_than';
  value: string | number | Date;
}

export interface ProcessingLog {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  details?: Record<string, unknown>;
  documentName?: string;
  stepName?: string;
}

export interface RAGTool {
  id: string;
  name: string;
  description: string;
  type: 'search' | 'qa' | 'summarization' | 'extraction';
  configuration: RAGToolConfig;
  collections: string[];
  embeddingModel: string;
  isActive: boolean;
  usage: RAGToolUsage;
  createdAt: Date;
  updatedAt: Date;
}

export interface RAGToolConfig {
  searchMethod: 'semantic' | 'hybrid' | 'keyword';
  similarityThreshold: number;
  maxResults: number;
  useReranking: boolean;
  rerankingModel?: string;
  enableFiltering: boolean;
  filters?: Record<string, unknown>;
  llmModel?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface RAGToolUsage {
  totalQueries: number;
  successfulQueries: number;
  averageResponseTime: number;
  averageAccuracy: number;
  lastUsed?: Date;
  popularFilters: string[];
}

export interface SearchQuery {
  query: string;
  collections?: string[];
  filters?: Record<string, unknown>;
  limit?: number;
  similarityThreshold?: number;
  searchMethod?: 'semantic' | 'hybrid' | 'keyword';
  includeMetadata?: boolean;
  rerank?: boolean;
}

export interface SearchResult {
  id: string;
  content: string;
  similarity: number;
  metadata: Record<string, unknown>;
  source: {
    documentId: string;
    documentName: string;
    chunkIndex: number;
    collection: string;
  };
  highlights?: string[];
}

export interface DocumentUpload {
  file: File;
  metadata?: {
    title?: string;
    description?: string;
    tags?: string[];
    category?: string;
    [key: string]: unknown;
  };
}

export interface DoclingConfig {
  enabled: boolean;
  extractionSettings: {
    extractTables: boolean;
    extractImages: boolean;
    extractMetadata: boolean;
    preserveLayout: boolean;
    detectLanguage: boolean;
  };
  tableProcessing: {
    separateTable: boolean;
    preserveTableStructure: boolean;
    convertToMarkdown: boolean;
    minTableRows: number;
  };
  imageProcessing: {
    separateImages: boolean;
    extractImageText: boolean; // OCR
    generateImageDescriptions: boolean; // Using vision models
    imageDescriptionModel?: string;
  };
  preprocessingPipeline: {
    steps: ProcessingStep[];
    customRules: PreprocessingRule[];
  };
}

export interface ProcessingStep {
  id: string;
  name: string;
  type: 'extraction' | 'transformation' | 'validation' | 'enrichment';
  enabled: boolean;
  order: number;
  configuration: Record<string, unknown>;
}

export interface PreprocessingRule {
  id: string;
  name: string;
  condition: string; // JavaScript expression
  action: 'skip' | 'transform' | 'flag' | 'separate';
  parameters: Record<string, unknown>;
}

export interface RAGMetrics {
  totalDocuments: number;
  totalChunks: number;
  totalQueries: number;
  averageResponseTime: number;
  indexingProgress: number;
  storageUsed: number;
  recentActivity: ActivityMetric[];
}

export interface ActivityMetric {
  timestamp: Date;
  action: 'upload' | 'query' | 'index' | 'delete';
  count: number;
  details?: Record<string, unknown>;
}

// Form types for the UI
export interface VectorDatabaseFormData {
  name: string;
  type: VectorDatabase['type'];
  configuration: VectorDatabaseConfig;
}

export interface CollectionFormData {
  name: string;
  description?: string;
  embeddingModelId: string;
  vectorDatabaseId: string;
  tags: string[];
}

export interface EmbeddingModelFormData {
  name: string;
  displayName: string;
  provider: EmbeddingModel['provider'];
  configuration: EmbeddingModelConfig;
}

export interface CloudBucketFormData {
  name: string;
  provider: CloudBucket['provider'];
  configuration: {
    accessKey?: string;
    secretKey?: string;
    region?: string;
    bucketName?: string;
    endpoint?: string;
    [key: string]: unknown;
  };
}

export interface ProcessingJobFormData {
  name: string;
  description?: string;
  source: DocumentSource;
  target: ProcessingTarget;
  configuration: ProcessingConfiguration;
}
