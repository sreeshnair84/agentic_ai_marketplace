import { useState, useEffect, useCallback } from 'react';

export interface RAGDocument {
  id: string;
  name: string;
  type: 'pdf' | 'txt' | 'docx' | 'md' | 'html' | 'csv' | 'json';
  status: 'processing' | 'completed' | 'failed' | 'archived';
  size: number; // in bytes
  created_at: string;
  updated_at: string;
  metadata: {
    source?: string;
    author?: string;
    title?: string;
    description?: string;
    tags: string[];
    language?: string;
    pages?: number;
    words?: number;
  };
  processing: {
    chunks: number;
    embeddings: number;
    vectorized: boolean;
    indexing_status: 'pending' | 'in_progress' | 'completed' | 'failed';
    last_updated: string;
  };
  stats: {
    searches: number;
    relevance_score: number;
    last_accessed?: string;
  };
}

export interface RAGKnowledgeBase {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'archived' | 'building';
  visibility: 'public' | 'private' | 'shared';
  embedding_model: string;
  chunk_strategy: 'sentence' | 'paragraph' | 'semantic' | 'custom';
  chunk_size: number;
  overlap_size: number;
  documents: RAGDocument[];
  created_at: string;
  updated_at: string;
  stats: {
    total_documents: number;
    total_chunks: number;
    total_size: number; // in bytes
    search_count: number;
    avg_relevance: number;
  };
  owner: string;
  collaborators: string[];
}

export interface RAGSearch {
  id: string;
  query: string;
  knowledge_base_id: string;
  results: Array<{
    document_id: string;
    document_name: string;
    chunk_id: string;
    content: string;
    relevance_score: number;
    metadata: any;
  }>;
  search_params: {
    similarity_threshold: number;
    max_results: number;
    use_reranking: boolean;
    filters?: any;
  };
  created_at: string;
  duration: number; // in milliseconds
  user_id: string;
}

export interface CreateKnowledgeBaseData {
  name: string;
  description: string;
  visibility?: RAGKnowledgeBase['visibility'];
  embedding_model?: string;
  chunk_strategy?: RAGKnowledgeBase['chunk_strategy'];
  chunk_size?: number;
  overlap_size?: number;
}

export interface UploadDocumentData {
  file: File;
  metadata?: {
    source?: string;
    author?: string;
    title?: string;
    description?: string;
    tags?: string[];
    language?: string;
  };
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useRAG() {
  const [knowledgeBases, setKnowledgeBases] = useState<RAGKnowledgeBase[]>([]);
  const [documents, setDocuments] = useState<RAGDocument[]>([]);
  const [searchHistory, setSearchHistory] = useState<RAGSearch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchKnowledgeBases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases`);
      if (!response.ok) {
        throw new Error(`Failed to fetch knowledge bases: ${response.statusText}`);
      }
      const data = await response.json();
      setKnowledgeBases(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch knowledge bases');
      setKnowledgeBases([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchDocuments = useCallback(async (knowledgeBaseId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = knowledgeBaseId 
        ? `${API_BASE}/api/rag/knowledge-bases/${knowledgeBaseId}/documents`
        : `${API_BASE}/api/rag/documents`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch documents: ${response.statusText}`);
      }
      const data = await response.json();
      setDocuments(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSearchHistory = useCallback(async (knowledgeBaseId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = knowledgeBaseId 
        ? `${API_BASE}/api/rag/knowledge-bases/${knowledgeBaseId}/searches`
        : `${API_BASE}/api/rag/searches`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch search history: ${response.statusText}`);
      }
      const data = await response.json();
      setSearchHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch search history');
      setSearchHistory([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const createKnowledgeBase = useCallback(async (kbData: CreateKnowledgeBaseData): Promise<{ success: boolean; error?: string; id?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(kbData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create knowledge base');
      }

      const result = await response.json();
      await fetchKnowledgeBases(); // Refresh the list
      return { success: true, id: result.id };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create knowledge base';
      return { success: false, error: errorMessage };
    }
  }, [fetchKnowledgeBases]);

  const updateKnowledgeBase = useCallback(async (kbId: string, kbData: Partial<CreateKnowledgeBaseData>): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(kbData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to update knowledge base');
      }

      await fetchKnowledgeBases(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update knowledge base';
      return { success: false, error: errorMessage };
    }
  }, [fetchKnowledgeBases]);

  const deleteKnowledgeBase = useCallback(async (kbId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete knowledge base');
      }

      await fetchKnowledgeBases(); // Refresh the list
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete knowledge base';
      return { success: false, error: errorMessage };
    }
  }, [fetchKnowledgeBases]);

  const uploadDocument = useCallback(async (kbId: string, documentData: UploadDocumentData): Promise<{ success: boolean; error?: string; documentId?: string }> => {
    try {
      const formData = new FormData();
      formData.append('file', documentData.file);
      
      if (documentData.metadata) {
        formData.append('metadata', JSON.stringify(documentData.metadata));
      }

      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}/documents`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to upload document');
      }

      const result = await response.json();
      await fetchDocuments(kbId); // Refresh documents for this KB
      await fetchKnowledgeBases(); // Refresh KB stats
      return { 
        success: true, 
        documentId: result.id
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      return { success: false, error: errorMessage };
    }
  }, [fetchDocuments, fetchKnowledgeBases]);

  const deleteDocument = useCallback(async (kbId: string, documentId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}/documents/${documentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to delete document');
      }

      await fetchDocuments(kbId); // Refresh documents for this KB
      await fetchKnowledgeBases(); // Refresh KB stats
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete document';
      return { success: false, error: errorMessage };
    }
  }, [fetchDocuments, fetchKnowledgeBases]);

  const searchKnowledgeBase = useCallback(async (
    kbId: string, 
    query: string, 
    params?: {
      similarity_threshold?: number;
      max_results?: number;
      use_reranking?: boolean;
      filters?: any;
    }
  ): Promise<{ success: boolean; error?: string; results?: RAGSearch['results'] }> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          search_params: params,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to search knowledge base');
      }

      const result = await response.json();
      await fetchSearchHistory(kbId); // Refresh search history
      return { 
        success: true, 
        results: result.results
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search knowledge base';
      return { success: false, error: errorMessage };
    }
  }, [fetchSearchHistory]);

  const reprocessDocument = useCallback(async (kbId: string, documentId: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}/documents/${documentId}/reprocess`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to reprocess document');
      }

      await fetchDocuments(kbId); // Refresh documents for this KB
      return { success: true };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reprocess document';
      return { success: false, error: errorMessage };
    }
  }, [fetchDocuments]);

  const getKnowledgeBase = useCallback(async (kbId: string): Promise<RAGKnowledgeBase | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch knowledge base: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching knowledge base:', err);
      return null;
    }
  }, []);

  const getDocument = useCallback(async (kbId: string, documentId: string): Promise<RAGDocument | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/rag/knowledge-bases/${kbId}/documents/${documentId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch document: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching document:', err);
      return null;
    }
  }, []);

  useEffect(() => {
    fetchKnowledgeBases();
    fetchDocuments();
    fetchSearchHistory();
  }, [fetchKnowledgeBases, fetchDocuments, fetchSearchHistory]);

  return {
    knowledgeBases,
    documents,
    searchHistory,
    loading,
    error,
    fetchKnowledgeBases,
    fetchDocuments,
    fetchSearchHistory,
    createKnowledgeBase,
    updateKnowledgeBase,
    deleteKnowledgeBase,
    uploadDocument,
    deleteDocument,
    searchKnowledgeBase,
    reprocessDocument,
    getKnowledgeBase,
    getDocument,
  };
}

// Hook for RAG analytics
export function useRAGAnalytics() {
  const { knowledgeBases, documents, searchHistory } = useRAG();
  
  const analytics = {
    totalKnowledgeBases: knowledgeBases.length,
    activeKnowledgeBases: knowledgeBases.filter(kb => kb.status === 'active').length,
    buildingKnowledgeBases: knowledgeBases.filter(kb => kb.status === 'building').length,
    archivedKnowledgeBases: knowledgeBases.filter(kb => kb.status === 'archived').length,
    visibilityBreakdown: {
      public: knowledgeBases.filter(kb => kb.visibility === 'public').length,
      private: knowledgeBases.filter(kb => kb.visibility === 'private').length,
      shared: knowledgeBases.filter(kb => kb.visibility === 'shared').length,
    },
    totalDocuments: documents.length,
    documentsByStatus: {
      processing: documents.filter(d => d.status === 'processing').length,
      completed: documents.filter(d => d.status === 'completed').length,
      failed: documents.filter(d => d.status === 'failed').length,
      archived: documents.filter(d => d.status === 'archived').length,
    },
    documentsByType: {
      pdf: documents.filter(d => d.type === 'pdf').length,
      txt: documents.filter(d => d.type === 'txt').length,
      docx: documents.filter(d => d.type === 'docx').length,
      md: documents.filter(d => d.type === 'md').length,
      html: documents.filter(d => d.type === 'html').length,
      csv: documents.filter(d => d.type === 'csv').length,
      json: documents.filter(d => d.type === 'json').length,
    },
    totalSize: documents.reduce((sum, d) => sum + d.size, 0),
    totalChunks: documents.reduce((sum, d) => sum + d.processing.chunks, 0),
    totalEmbeddings: documents.reduce((sum, d) => sum + d.processing.embeddings, 0),
    totalSearches: searchHistory.length,
    avgSearchDuration: searchHistory.length > 0 
      ? searchHistory.reduce((sum, s) => sum + s.duration, 0) / searchHistory.length 
      : 0,
    searchSuccessRate: searchHistory.length > 0 
      ? (searchHistory.filter(s => s.results.length > 0).length / searchHistory.length) * 100 
      : 0,
  };

  return analytics;
}
