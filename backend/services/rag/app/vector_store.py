"""
Vector operations module for PGVector integration
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import openai
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import numpy as np
from .config import rag_config

logger = logging.getLogger(__name__)


class VectorStore:
    """PGVector-based vector store operations"""
    
    def __init__(self):
        self.openai_client = None
    
    async def initialize_openai_client(self, db: AsyncSession):
        """Initialize OpenAI client with API key from configuration"""
        await rag_config.refresh_if_needed(db)
        
        # For now, we'll use environment variables for API keys
        # In a full implementation, these could also be stored in the database
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            self.openai_client = openai
            logger.info("OpenAI client initialized")
        else:
            logger.warning("No OpenAI API key available")
    
    async def get_embedding(self, text: str, db: AsyncSession) -> List[float]:
        """Get embedding for text using configured embedding model"""
        await rag_config.refresh_if_needed(db)
        
        if not self.openai_client:
            await self.initialize_openai_client(db)
        
        if not self.openai_client:
            raise Exception("No embedding service available")
        
        try:
            model_name = rag_config.get_embedding_model_name()
            response = await self.openai_client.Embedding.acreate(
                model=model_name,
                input=text
            )
            
            embedding = response['data'][0]['embedding']
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    async def create_namespace(self, namespace: str, db: AsyncSession) -> Dict[str, Any]:
        """Create a new namespace (equivalent to collection in ChromaDB)"""
        try:
            # Check if namespace already exists
            query = text("""
                SELECT COUNT(*) FROM document_embeddings 
                WHERE namespace = :namespace
            """)
            result = await db.execute(query, {"namespace": namespace})
            count = result.scalar()
            
            return {
                "name": namespace,
                "document_count": count,
                "created_at": datetime.utcnow(),
                "status": "exists" if count > 0 else "created"
            }
            
        except Exception as e:
            logger.error(f"Error creating namespace: {e}")
            raise
    
    async def list_namespaces(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """List all namespaces with document counts"""
        try:
            query = text("""
                SELECT namespace, COUNT(*) as document_count,
                       MIN(created_at) as first_created,
                       MAX(updated_at) as last_updated
                FROM document_embeddings 
                GROUP BY namespace
                ORDER BY namespace
            """)
            result = await db.execute(query)
            rows = result.fetchall()
            
            namespaces = []
            for row in rows:
                namespaces.append({
                    "name": row[0],
                    "document_count": row[1],
                    "first_created": row[2],
                    "last_updated": row[3]
                })
            
            return namespaces
            
        except Exception as e:
            logger.error(f"Error listing namespaces: {e}")
            raise
    
    async def delete_namespace(self, namespace: str, db: AsyncSession) -> Dict[str, Any]:
        """Delete a namespace and all its documents"""
        try:
            query = text("""
                DELETE FROM document_embeddings 
                WHERE namespace = :namespace
            """)
            result = await db.execute(query, {"namespace": namespace})
            await db.commit()
            
            deleted_count = result.rowcount
            
            return {
                "namespace": namespace,
                "deleted_documents": deleted_count,
                "status": "deleted"
            }
            
        except Exception as e:
            logger.error(f"Error deleting namespace: {e}")
            await db.rollback()
            raise
    
    async def add_documents(
        self, 
        documents: List[str], 
        metadata_list: List[Dict[str, Any]], 
        namespace: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Add documents to the vector store"""
        try:
            embeddings = []
            for doc in documents:
                embedding = await self.get_embedding(doc, db)
                embeddings.append(embedding)
            
            # Insert documents with embeddings
            for i, (doc, metadata, embedding) in enumerate(zip(documents, metadata_list, embeddings)):
                doc_id = metadata.get('document_id', f"doc_{datetime.utcnow().timestamp()}_{i}")
                
                query = text("""
                    INSERT INTO document_embeddings 
                    (document_id, content, embedding, metadata, namespace)
                    VALUES (:document_id, :content, :embedding, :metadata, :namespace)
                """)
                
                await db.execute(query, {
                    "document_id": doc_id,
                    "content": doc,
                    "embedding": json.dumps(embedding),  # Store as JSON for now
                    "metadata": json.dumps(metadata),
                    "namespace": namespace
                })
            
            await db.commit()
            
            return {
                "added_documents": len(documents),
                "namespace": namespace,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            await db.rollback()
            raise
    
    async def search_similar(
        self, 
        query: str, 
        namespace: str, 
        n_results: int, 
        similarity_threshold: Optional[float] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Get query embedding
            query_embedding = await self.get_embedding(query, db)
            
            # Use configured similarity threshold if not provided
            if similarity_threshold is None:
                similarity_threshold = rag_config.get_similarity_threshold()
            
            # Build the search query
            base_query = """
                SELECT 
                    id, document_id, content, metadata,
                    cosine_similarity(embedding::vector, :query_embedding::vector) as similarity
                FROM document_embeddings 
                WHERE namespace = :namespace
                AND cosine_similarity(embedding::vector, :query_embedding::vector) > :similarity_threshold
            """
            
            # Add metadata filter if provided
            if metadata_filter:
                # Simple implementation - could be enhanced for complex filters
                filter_conditions = []
                for key, value in metadata_filter.items():
                    filter_conditions.append(f"metadata->>'{key}' = '{value}'")
                if filter_conditions:
                    base_query += " AND " + " AND ".join(filter_conditions)
            
            base_query += """
                ORDER BY similarity DESC
                LIMIT :n_results
            """
            
            query_stmt = text(base_query)
            result = await db.execute(query_stmt, {
                "query_embedding": json.dumps(query_embedding),
                "namespace": namespace,
                "similarity_threshold": similarity_threshold,
                "n_results": n_results
            })
            
            rows = result.fetchall()
            
            search_results = []
            for row in rows:
                search_results.append({
                    "id": str(row[0]),
                    "document_id": row[1],
                    "content": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {},
                    "similarity": float(row[4])
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise


# Global vector store instance
vector_store = VectorStore()
