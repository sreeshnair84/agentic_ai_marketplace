"""
Enhanced RAG Service
Handles all RAG operations including document ingestion, search, and collection management
"""

import asyncio
import asyncpg
import json
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import aiofiles
import numpy as np
from datetime import datetime

# Document processing imports
import pypdf
from docx import Document as DocxDocument
import chardet

# Embedding and vector storage
import openai
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EnhancedRAGService:
    """Enhanced RAG service with comprehensive document and collection management"""
    
    def __init__(self):
        self.embedding_models = {}
        self.connection_pool = None
        self.logger = logger
    
    async def initialize(self, database_url: str):
        """Initialize the RAG service with database connection"""
        self.connection_pool = await asyncpg.create_pool(database_url)
    
    async def ingest_document(
        self,
        pipeline_id: str,
        file_path: str,
        filename: str,
        metadata: Dict[str, Any] = None,
        processing_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Ingest a document into the RAG pipeline"""
        
        try:
            # Extract text from document
            text_content = await self._extract_text_from_file(file_path, filename)
            
            if not text_content.strip():
                return {
                    "status": "error",
                    "message": "No text content extracted from document"
                }
            
            # Process the text content
            result = await self.ingest_text(
                pipeline_id=pipeline_id,
                content=text_content,
                metadata={
                    **(metadata or {}),
                    "filename": filename,
                    "file_path": file_path,
                    "ingestion_date": datetime.utcnow().isoformat()
                },
                processing_options=processing_options
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error ingesting document {filename}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def ingest_text(
        self,
        pipeline_id: str,
        content: str,
        metadata: Dict[str, Any] = None,
        processing_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Ingest text content into the RAG pipeline"""
        
        try:
            # Get pipeline configuration
            pipeline_config = await self._get_pipeline_config(pipeline_id)
            
            # Clean and preprocess text
            processed_content = self._preprocess_text(content, processing_options or {})
            
            # Split into chunks
            chunks = self._create_chunks(
                processed_content, 
                pipeline_config.get("chunking_strategy", {})
            )
            
            # Generate embeddings
            embedding_config = pipeline_config.get("vectorization_config", {})
            embedding_model = embedding_config.get("embedding_model", "text-embedding-3-small")
            
            # Store chunks with embeddings
            stored_chunks = 0
            for i, chunk in enumerate(chunks):
                try:
                    # Generate embedding
                    embedding = await self._generate_embedding(chunk, embedding_model)
                    
                    # Store in database
                    await self._store_chunk(
                        pipeline_id=pipeline_id,
                        chunk_content=chunk,
                        embedding=embedding,
                        metadata={
                            **(metadata or {}),
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "embedding_model": embedding_model
                        }
                    )
                    
                    stored_chunks += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing chunk {i}: {e}")
                    continue
            
            return {
                "status": "success",
                "content_length": len(content),
                "chunks_created": stored_chunks,
                "embedding_model": embedding_model,
                "pipeline_id": pipeline_id
            }
            
        except Exception as e:
            self.logger.error(f"Error ingesting text for pipeline {pipeline_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def search(
        self,
        pipeline_id: str,
        query: str,
        k: int = 5,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search for relevant documents in the pipeline"""
        
        try:
            # Get pipeline configuration
            pipeline_config = await self._get_pipeline_config(pipeline_id)
            
            # Generate query embedding
            embedding_config = pipeline_config.get("vectorization_config", {})
            embedding_model = embedding_config.get("embedding_model", "text-embedding-3-small")
            query_embedding = await self._generate_embedding(query, embedding_model)
            
            # Perform vector search
            results = await self._vector_search(
                pipeline_id=pipeline_id,
                query_embedding=query_embedding,
                k=k,
                filters=filters or {}
            )
            
            return {
                "status": "success",
                "query": query,
                "results": results,
                "total_results": len(results),
                "embedding_model": embedding_model
            }
            
        except Exception as e:
            self.logger.error(f"Error searching pipeline {pipeline_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def rebuild_collection(
        self,
        pipeline_id: str,
        collection_name: str,
        new_embedding_model: str = None
    ) -> Dict[str, Any]:
        """Rebuild a collection with new embedding model"""
        
        try:
            # Get existing documents
            async with self.connection_pool.acquire() as conn:
                documents = await conn.fetch("""
                    SELECT content, metadata 
                    FROM document_embeddings 
                    WHERE namespace = $1
                """, f"{pipeline_id}_{collection_name}")
            
            if not documents:
                return {
                    "status": "error",
                    "message": "No documents found in collection"
                }
            
            # Get pipeline config and update embedding model if provided
            pipeline_config = await self._get_pipeline_config(pipeline_id)
            if new_embedding_model:
                embedding_config = pipeline_config.get("vectorization_config", {})
                embedding_config["embedding_model"] = new_embedding_model
                await self._update_pipeline_config(pipeline_id, {
                    "vectorization_config": embedding_config
                })
            
            # Delete existing embeddings
            await self._delete_collection_embeddings(pipeline_id, collection_name)
            
            # Re-generate embeddings for all documents
            embedding_model = new_embedding_model or pipeline_config.get(
                "vectorization_config", {}
            ).get("embedding_model", "text-embedding-3-small")
            
            rebuilt_count = 0
            for doc in documents:
                try:
                    # Generate new embedding
                    embedding = await self._generate_embedding(doc["content"], embedding_model)
                    
                    # Store with new embedding
                    await self._store_chunk(
                        pipeline_id=pipeline_id,
                        chunk_content=doc["content"],
                        embedding=embedding,
                        metadata={
                            **json.loads(doc["metadata"]),
                            "rebuilt_at": datetime.utcnow().isoformat(),
                            "embedding_model": embedding_model
                        },
                        collection_name=collection_name
                    )
                    
                    rebuilt_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error rebuilding document: {e}")
                    continue
            
            return {
                "status": "success",
                "collection_name": collection_name,
                "documents_rebuilt": rebuilt_count,
                "new_embedding_model": embedding_model
            }
            
        except Exception as e:
            self.logger.error(f"Error rebuilding collection {collection_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def delete_collection(
        self,
        pipeline_id: str,
        collection_name: str
    ) -> Dict[str, Any]:
        """Delete a collection and all its documents"""
        
        try:
            deleted_count = await self._delete_collection_embeddings(pipeline_id, collection_name)
            
            return {
                "status": "success",
                "collection_name": collection_name,
                "documents_deleted": deleted_count
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting collection {collection_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def list_collections(self, pipeline_id: str) -> Dict[str, Any]:
        """List all collections for a pipeline"""
        
        try:
            async with self.connection_pool.acquire() as conn:
                result = await conn.fetch("""
                    SELECT 
                        namespace,
                        COUNT(*) as document_count,
                        AVG(LENGTH(content)) as avg_content_length,
                        MIN(created_at) as earliest_document,
                        MAX(created_at) as latest_document
                    FROM document_embeddings 
                    WHERE namespace LIKE $1
                    GROUP BY namespace
                """, f"{pipeline_id}_%")
            
            collections = []
            for row in result:
                namespace_parts = row["namespace"].split("_", 1)
                collection_name = namespace_parts[1] if len(namespace_parts) > 1 else "default"
                
                collections.append({
                    "name": collection_name,
                    "document_count": row["document_count"],
                    "avg_content_length": float(row["avg_content_length"] or 0),
                    "earliest_document": row["earliest_document"],
                    "latest_document": row["latest_document"]
                })
            
            return {
                "status": "success",
                "pipeline_id": pipeline_id,
                "collections": collections
            }
            
        except Exception as e:
            self.logger.error(f"Error listing collections for pipeline {pipeline_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_collection_stats(
        self,
        pipeline_id: str,
        collection_name: str
    ) -> Dict[str, Any]:
        """Get detailed statistics for a collection"""
        
        try:
            namespace = f"{pipeline_id}_{collection_name}"
            
            async with self.connection_pool.acquire() as conn:
                # Get basic stats
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_documents,
                        AVG(LENGTH(content)) as avg_content_length,
                        SUM(LENGTH(content)) as total_content_length,
                        MIN(created_at) as earliest_document,
                        MAX(created_at) as latest_document
                    FROM document_embeddings 
                    WHERE namespace = $1
                """, namespace)
                
                # Get embedding model distribution
                models = await conn.fetch("""
                    SELECT 
                        metadata->>'embedding_model' as model,
                        COUNT(*) as count
                    FROM document_embeddings 
                    WHERE namespace = $1
                    GROUP BY metadata->>'embedding_model'
                """, namespace)
                
                # Get content type distribution
                content_types = await conn.fetch("""
                    SELECT 
                        metadata->>'document_type' as type,
                        COUNT(*) as count
                    FROM document_embeddings 
                    WHERE namespace = $1
                    GROUP BY metadata->>'document_type'
                """, namespace)
            
            return {
                "status": "success",
                "collection_name": collection_name,
                "total_documents": stats["total_documents"],
                "avg_content_length": float(stats["avg_content_length"] or 0),
                "total_content_length": stats["total_content_length"],
                "earliest_document": stats["earliest_document"],
                "latest_document": stats["latest_document"],
                "embedding_models": [
                    {"model": row["model"], "count": row["count"]} 
                    for row in models
                ],
                "content_types": [
                    {"type": row["type"], "count": row["count"]} 
                    for row in content_types
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stats for collection {collection_name}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def change_embedding_model(
        self,
        pipeline_id: str,
        new_model: str,
        migrate_existing: bool = False
    ) -> Dict[str, Any]:
        """Change the embedding model for a pipeline"""
        
        try:
            # Update pipeline configuration
            await self._update_pipeline_config(pipeline_id, {
                "vectorization_config": {
                    "embedding_model": new_model
                }
            })
            
            result = {
                "status": "success",
                "new_embedding_model": new_model,
                "pipeline_id": pipeline_id
            }
            
            if migrate_existing:
                # Get all collections for this pipeline
                collections_info = await self.list_collections(pipeline_id)
                
                if collections_info["status"] == "success":
                    collections = collections_info["collections"]
                    
                    for collection in collections:
                        rebuild_result = await self.rebuild_collection(
                            pipeline_id=pipeline_id,
                            collection_name=collection["name"],
                            new_embedding_model=new_model
                        )
                        
                        result[f"collection_{collection['name']}_migration"] = rebuild_result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error changing embedding model for pipeline {pipeline_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a complete pipeline run"""
        
        try:
            operation = parameters.get("operation", "index_documents")
            
            if operation == "index_documents":
                # Index new documents
                documents = parameters.get("documents", [])
                results = []
                
                for doc in documents:
                    if "content" in doc:
                        result = await self.ingest_text(
                            pipeline_id=pipeline_id,
                            content=doc["content"],
                            metadata=doc.get("metadata", {})
                        )
                        results.append(result)
                
                return {
                    "operation": operation,
                    "documents_processed": len(results),
                    "results": results
                }
            
            elif operation == "rebuild_all_collections":
                # Rebuild all collections
                collections_info = await self.list_collections(pipeline_id)
                
                if collections_info["status"] != "success":
                    return collections_info
                
                results = {}
                for collection in collections_info["collections"]:
                    result = await self.rebuild_collection(
                        pipeline_id=pipeline_id,
                        collection_name=collection["name"],
                        new_embedding_model=parameters.get("embedding_model")
                    )
                    results[collection["name"]] = result
                
                return {
                    "operation": operation,
                    "collections_rebuilt": len(results),
                    "results": results
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            self.logger.error(f"Error executing pipeline {pipeline_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    # Private helper methods
    
    async def _extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text content from various file formats"""
        
        file_ext = Path(filename).suffix.lower()
        
        try:
            if file_ext == ".pdf":
                return await self._extract_pdf_text(file_path)
            elif file_ext in [".docx", ".doc"]:
                return await self._extract_docx_text(file_path)
            elif file_ext == ".txt":
                return await self._extract_txt_text(file_path)
            else:
                # Try to read as text
                return await self._extract_txt_text(file_path)
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {filename}: {e}")
            raise
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        
        reader = pypdf.PdfReader(file_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        
        doc = DocxDocument(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from text file with encoding detection"""
        
        # Detect encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding_result = chardet.detect(raw_data)
            encoding = encoding_result['encoding'] or 'utf-8'
        
        # Read with detected encoding
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            return await f.read()
    
    def _preprocess_text(self, content: str, options: Dict[str, Any]) -> str:
        """Preprocess text content"""
        
        if options.get("clean_text", True):
            # Remove extra whitespace
            import re
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
        
        if options.get("normalize_unicode", True):
            import unicodedata
            content = unicodedata.normalize('NFKC', content)
        
        return content
    
    def _create_chunks(self, content: str, chunking_config: Dict[str, Any]) -> List[str]:
        """Create text chunks based on configuration"""
        
        chunk_size = chunking_config.get("chunk_size", 1000)
        chunk_overlap = chunking_config.get("chunk_overlap", 200)
        method = chunking_config.get("method", "recursive")
        
        if method == "fixed_size":
            return self._fixed_size_chunking(content, chunk_size, chunk_overlap)
        elif method == "sentence":
            return self._sentence_chunking(content, chunk_size, chunk_overlap)
        else:  # recursive (default)
            return self._recursive_chunking(content, chunk_size, chunk_overlap)
    
    def _fixed_size_chunking(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Simple fixed-size chunking with overlap"""
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk = content[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
            if start >= len(content):
                break
        
        return chunks
    
    def _sentence_chunking(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Sentence-based chunking"""
        
        import re
        
        # Split by sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _recursive_chunking(self, content: str, chunk_size: int, overlap: int) -> List[str]:
        """Recursive text splitting (similar to LangChain's approach)"""
        
        separators = ["\n\n", "\n", " ", ""]
        
        def split_text(text: str, seps: List[str]) -> List[str]:
            if not seps or len(text) <= chunk_size:
                return [text] if text else []
            
            sep = seps[0]
            parts = text.split(sep)
            
            chunks = []
            current_chunk = ""
            
            for part in parts:
                if len(current_chunk) + len(part) + len(sep) <= chunk_size:
                    current_chunk += part + sep
                else:
                    if current_chunk:
                        chunks.append(current_chunk.rstrip())
                    
                    if len(part) > chunk_size:
                        # Recursively split large parts
                        sub_chunks = split_text(part, seps[1:])
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = part + sep
            
            if current_chunk:
                chunks.append(current_chunk.rstrip())
            
            return chunks
        
        return split_text(content, separators)
    
    async def _generate_embedding(self, text: str, model_name: str) -> List[float]:
        """Generate embedding for text using specified model"""
        
        if model_name.startswith("text-embedding"):
            # OpenAI models
            client = openai.AsyncOpenAI()
            response = await client.embeddings.create(
                model=model_name,
                input=text
            )
            return response.data[0].embedding
        
        elif model_name.startswith("sentence-transformers"):
            # Sentence Transformers models
            if model_name not in self.embedding_models:
                self.embedding_models[model_name] = SentenceTransformer(model_name)
            
            model = self.embedding_models[model_name]
            embedding = model.encode(text)
            return embedding.tolist()
        
        else:
            raise ValueError(f"Unsupported embedding model: {model_name}")
    
    async def _store_chunk(
        self,
        pipeline_id: str,
        chunk_content: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        collection_name: str = "default"
    ):
        """Store a chunk with its embedding in the database"""
        
        namespace = f"{pipeline_id}_{collection_name}"
        
        async with self.connection_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO document_embeddings 
                (document_id, content, embedding, metadata, namespace, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                f"{pipeline_id}_{int(time.time() * 1000)}",  # Unique document ID
                chunk_content,
                embedding,
                json.dumps(metadata),
                namespace,
                datetime.utcnow(),
                datetime.utcnow()
            )
    
    async def _vector_search(
        self,
        pipeline_id: str,
        query_embedding: List[float],
        k: int,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        
        namespace_pattern = f"{pipeline_id}_%"
        
        async with self.connection_pool.acquire() as conn:
            # Use cosine similarity for search
            results = await conn.fetch("""
                SELECT 
                    document_id,
                    content,
                    metadata,
                    1 - (embedding <=> $1) as similarity
                FROM document_embeddings
                WHERE namespace LIKE $2
                ORDER BY embedding <=> $1
                LIMIT $3
            """, query_embedding, namespace_pattern, k)
        
        search_results = []
        for row in results:
            result = {
                "document_id": row["document_id"],
                "content": row["content"],
                "similarity": float(row["similarity"]),
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            }
            search_results.append(result)
        
        return search_results
    
    async def _get_pipeline_config(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline configuration from database"""
        
        # This would typically query the rag_pipelines table
        # For now, return default configuration
        return {
            "chunking_strategy": {
                "method": "recursive",
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "vectorization_config": {
                "embedding_model": "text-embedding-3-small"
            }
        }
    
    async def _update_pipeline_config(self, pipeline_id: str, config_update: Dict[str, Any]):
        """Update pipeline configuration in database"""
        
        # This would update the rag_pipelines table
        pass
    
    async def _delete_collection_embeddings(self, pipeline_id: str, collection_name: str) -> int:
        """Delete all embeddings for a collection"""
        
        namespace = f"{pipeline_id}_{collection_name}"
        
        async with self.connection_pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM document_embeddings 
                WHERE namespace = $1
            """, namespace)
            
            return result.split()[-1]  # Get the number of deleted rows
