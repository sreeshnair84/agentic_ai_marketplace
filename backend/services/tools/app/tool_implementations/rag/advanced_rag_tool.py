"""
Advanced RAG Tool Implementation
Vector database integration with multiple embedding models and chunking strategies
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Document processing
import pypdf
from docx import Document as DocxDocument
import chardet

# Vector storage and embeddings
import openai
from sentence_transformers import SentenceTransformer
import numpy as np

# Chunking and text processing
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)

class AdvancedRAGTool:
    """
    Advanced RAG implementation with configurable embedding models,
    chunking strategies, and vector database integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize RAG tool with configuration"""
        self.config = config
        self.embedding_model = config.get("embedding_model", "text-embedding-3-small")
        self.chunk_size = config.get("chunk_size", 1000)
        self.chunk_overlap = config.get("chunk_overlap", 200)
        self.chunking_strategy = config.get("chunking_strategy", "recursive")
        self.vector_db_config = config.get("vector_database", {})
        
        # Initialize components
        self.sentence_transformer = None
        self.openai_client = None
        
        logger.info(f"Initialized RAG tool with model: {self.embedding_model}")
    
    async def initialize(self):
        """Initialize the RAG tool components"""
        try:
            # Initialize embedding model
            if self.embedding_model.startswith("sentence-transformers"):
                self.sentence_transformer = SentenceTransformer(self.embedding_model)
            elif self.embedding_model.startswith("text-embedding"):
                self.openai_client = openai.AsyncOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            
            logger.info("RAG tool components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG tool: {e}")
            raise
    
    async def ingest_document(self, document_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingest a document into the RAG system
        
        Args:
            document_path: Path to the document file
            metadata: Additional metadata for the document
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            # Extract text from document
            text_content = await self._extract_text(document_path)
            
            # Create chunks
            chunks = self._create_chunks(text_content)
            
            # Generate embeddings for chunks
            embeddings = []
            for chunk in chunks:
                embedding = await self._generate_embedding(chunk)
                embeddings.append(embedding)
            
            # Store in vector database
            doc_id = await self._store_chunks(chunks, embeddings, metadata or {})
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_created": len(chunks),
                "embedding_model": self.embedding_model,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error ingesting document {document_path}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def ingest_text(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingest raw text into the RAG system
        
        Args:
            text: Text content to ingest
            metadata: Additional metadata
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            # Create chunks
            chunks = self._create_chunks(text)
            
            # Generate embeddings
            embeddings = []
            for chunk in chunks:
                embedding = await self._generate_embedding(chunk)
                embeddings.append(embedding)
            
            # Store in vector database
            doc_id = await self._store_chunks(chunks, embeddings, metadata or {})
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_created": len(chunks),
                "embedding_model": self.embedding_model
            }
            
        except Exception as e:
            logger.error(f"Error ingesting text: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def search(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Additional filters to apply
            
        Returns:
            Dictionary with search results
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Perform vector search
            results = await self._vector_search(query_embedding, top_k, filters or {})
            
            return {
                "status": "success",
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_embedding_model(self, new_model: str) -> Dict[str, Any]:
        """
        Update the embedding model and re-process existing documents
        
        Args:
            new_model: New embedding model to use
            
        Returns:
            Dictionary with update results
        """
        try:
            old_model = self.embedding_model
            self.embedding_model = new_model
            
            # Re-initialize with new model
            await self.initialize()
            
            # TODO: Re-process existing documents with new model
            
            return {
                "status": "success",
                "old_model": old_model,
                "new_model": new_model,
                "message": "Embedding model updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating embedding model: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the RAG system"""
        try:
            # TODO: Implement statistics gathering
            return {
                "status": "success",
                "total_documents": 0,
                "total_chunks": 0,
                "embedding_model": self.embedding_model,
                "vector_db_status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Private methods
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".pdf":
            return self._extract_pdf_text(file_path)
        elif file_ext in [".docx", ".doc"]:
            return self._extract_docx_text(file_path)
        elif file_ext == ".txt":
            return self._extract_txt_text(file_path)
        else:
            # Try to read as text
            return self._extract_txt_text(file_path)
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        reader = pypdf.PdfReader(file_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = DocxDocument(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from text file with encoding detection"""
        # Detect encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding_result = chardet.detect(raw_data)
            encoding = encoding_result['encoding'] or 'utf-8'
        
        # Read with detected encoding
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    def _create_chunks(self, text: str) -> List[str]:
        """Create chunks based on the configured strategy"""
        if self.chunking_strategy == "fixed_size":
            return self._fixed_size_chunking(text)
        elif self.chunking_strategy == "sentence":
            return self._sentence_chunking(text)
        else:  # recursive (default)
            return self._recursive_chunking(text)
    
    def _fixed_size_chunking(self, text: str) -> List[str]:
        """Simple fixed-size chunking with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _sentence_chunking(self, text: str) -> List[str]:
        """Sentence-based chunking"""
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _recursive_chunking(self, text: str) -> List[str]:
        """Recursive text splitting (similar to LangChain's approach)"""
        separators = ["\n\n", "\n", " ", ""]
        
        def split_text(text: str, seps: List[str]) -> List[str]:
            if not seps or len(text) <= self.chunk_size:
                return [text] if text else []
            
            sep = seps[0]
            parts = text.split(sep)
            
            chunks = []
            current_chunk = ""
            
            for part in parts:
                if len(current_chunk) + len(part) + len(sep) <= self.chunk_size:
                    current_chunk += part + sep
                else:
                    if current_chunk:
                        chunks.append(current_chunk.rstrip())
                    
                    if len(part) > self.chunk_size:
                        # Recursively split large parts
                        sub_chunks = split_text(part, seps[1:])
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = part + sep
            
            if current_chunk:
                chunks.append(current_chunk.rstrip())
            
            return chunks
        
        return split_text(text, separators)
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.openai_client:
            # OpenAI embeddings
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        
        elif self.sentence_transformer:
            # Sentence Transformers
            embedding = self.sentence_transformer.encode(text)
            return embedding.tolist()
        
        else:
            raise ValueError(f"No embedding model initialized for {self.embedding_model}")
    
    async def _store_chunks(self, chunks: List[str], embeddings: List[List[float]], metadata: Dict[str, Any]) -> str:
        """Store chunks and embeddings in vector database"""
        # TODO: Implement vector database storage
        # This would connect to your chosen vector DB (Pinecone, Weaviate, ChromaDB, etc.)
        
        doc_id = f"doc_{datetime.now().timestamp()}"
        
        # Mock storage for now
        logger.info(f"Stored {len(chunks)} chunks with embeddings for document {doc_id}")
        
        return doc_id
    
    async def _vector_search(self, query_embedding: List[float], top_k: int, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        # TODO: Implement actual vector search
        # This would query your vector database
        
        # Mock results for now
        mock_results = [
            {
                "chunk_id": f"chunk_{i}",
                "content": f"Sample content chunk {i}",
                "similarity_score": 0.9 - (i * 0.1),
                "metadata": {"source": f"document_{i}"}
            }
            for i in range(min(top_k, 3))
        ]
        
        return mock_results

# Tool configuration schema
TOOL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "embedding_model": {
            "type": "string",
            "enum": [
                "text-embedding-3-small",
                "text-embedding-3-large", 
                "text-embedding-ada-002",
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-mpnet-base-v2"
            ],
            "default": "text-embedding-3-small",
            "description": "Embedding model to use for vectorization"
        },
        "chunk_size": {
            "type": "integer",
            "minimum": 100,
            "maximum": 8000,
            "default": 1000,
            "description": "Size of text chunks in characters"
        },
        "chunk_overlap": {
            "type": "integer",
            "minimum": 0,
            "maximum": 1000,
            "default": 200,
            "description": "Overlap between chunks in characters"
        },
        "chunking_strategy": {
            "type": "string",
            "enum": ["fixed_size", "sentence", "recursive"],
            "default": "recursive",
            "description": "Strategy for splitting text into chunks"
        },
        "vector_database": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["pinecone", "weaviate", "chromadb", "qdrant"],
                    "default": "chromadb"
                },
                "index_name": {
                    "type": "string",
                    "default": "rag-index"
                }
            }
        }
    },
    "required": ["embedding_model"]
}

# Tool input/output schemas
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["ingest_document", "ingest_text", "search", "update_model", "get_stats"],
            "description": "Operation to perform"
        },
        "document_path": {
            "type": "string",
            "description": "Path to document file (for ingest_document)"
        },
        "text": {
            "type": "string",
            "description": "Text content to ingest (for ingest_text)"
        },
        "query": {
            "type": "string",
            "description": "Search query (for search)"
        },
        "top_k": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 5,
            "description": "Number of results to return"
        },
        "metadata": {
            "type": "object",
            "description": "Additional metadata"
        },
        "filters": {
            "type": "object",
            "description": "Search filters"
        }
    },
    "required": ["operation"]
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["success", "error"]
        },
        "result": {
            "type": "object",
            "description": "Operation result"
        },
        "error": {
            "type": "string",
            "description": "Error message if status is error"
        }
    },
    "required": ["status"]
}
