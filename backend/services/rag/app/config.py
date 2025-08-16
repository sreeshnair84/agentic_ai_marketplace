"""
Configuration module for RAG service - reads from database tool instances
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)


class RAGConfig:
    """Configuration manager for RAG service based on database tool instances"""
    
    def __init__(self):
        self.embedding_config: Optional[Dict[str, Any]] = None
        self.llm_config: Optional[Dict[str, Any]] = None
        self.vector_store_config: Optional[Dict[str, Any]] = None
        self.last_refresh: Optional[datetime] = None
        self.refresh_interval_seconds = 300  # Refresh every 5 minutes
    
    async def load_config(self, async_session: AsyncSession) -> None:
        """Load configuration from database"""
        try:
            logger.info("Loading RAG configuration from database...")
            
            # Load embedding model configuration
            await self._load_embedding_config(async_session)
            
            # Load LLM configuration
            await self._load_llm_config(async_session)
            
            # Load vector store configuration
            await self._load_vector_store_config(async_session)
            
            self.last_refresh = datetime.utcnow()
            logger.info("RAG configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load RAG configuration: {e}")
            raise
    
    async def _load_embedding_config(self, async_session: AsyncSession) -> None:
        """Load embedding model configuration"""
        query = text("""
            SELECT em.name, em.display_name, em.provider, em.api_endpoint,
                   em.capabilities, em.pricing_info, em.performance_metrics,
                   em.input_signature, em.output_signature
            FROM embedding_models em 
            WHERE em.status = 'active'
            ORDER BY em.performance_metrics->>'availability' DESC
            LIMIT 1
        """)
        
        result = await async_session.execute(query)
        row = result.fetchone()
        
        if row:
            self.embedding_config = {
                'name': row[0],
                'display_name': row[1],
                'provider': row[2],
                'api_endpoint': row[3],
                'capabilities': row[4] or {},
                'pricing_info': row[5] or {},
                'performance_metrics': row[6] or {},
                'input_signature': row[7] or {},
                'output_signature': row[8] or {},
                'dimensions': row[4].get('dimensions', 1536) if row[4] else 1536
            }
            logger.info(f"Loaded embedding model: {self.embedding_config['name']}")
        else:
            logger.warning("No active embedding models found, using default configuration")
            self.embedding_config = self._get_default_embedding_config()
    
    async def _load_llm_config(self, async_session: AsyncSession) -> None:
        """Load LLM configuration"""
        query = text("""
            SELECT lm.name, lm.display_name, lm.provider, lm.api_endpoint,
                   lm.capabilities, lm.pricing_info, lm.performance_metrics,
                   lm.input_signature, lm.output_signature
            FROM llm_models lm 
            WHERE lm.status = 'active' AND lm.model_type = 'text-generation'
            ORDER BY lm.performance_metrics->>'availability' DESC
            LIMIT 1
        """)
        
        result = await async_session.execute(query)
        row = result.fetchone()
        
        if row:
            self.llm_config = {
                'name': row[0],
                'display_name': row[1],
                'provider': row[2],
                'api_endpoint': row[3],
                'capabilities': row[4] or {},
                'pricing_info': row[5] or {},
                'performance_metrics': row[6] or {},
                'input_signature': row[7] or {},
                'output_signature': row[8] or {}
            }
            logger.info(f"Loaded LLM model: {self.llm_config['name']}")
        else:
            logger.warning("No active LLM models found, using default configuration")
            self.llm_config = self._get_default_llm_config()
    
    async def _load_vector_store_config(self, async_session: AsyncSession) -> None:
        """Load vector store configuration from tool instances"""
        query = text("""
            SELECT ti.name, ti.display_name, ti.template_name, ti.configuration
            FROM tool_instances ti 
            WHERE ti.status = 'active' 
            AND (ti.template_name LIKE '%vector%' OR ti.template_name LIKE '%pgvector%' OR ti.template_name LIKE '%rag%')
            ORDER BY ti.created_at DESC
            LIMIT 1
        """)
        
        result = await async_session.execute(query)
        row = result.fetchone()
        
        if row:
            config = row[3] or {}
            self.vector_store_config = {
                'name': row[0],
                'display_name': row[1],
                'template_name': row[2],
                'type': 'pgvector',
                'configuration': config,
                'similarity_threshold': config.get('similarity_threshold', 0.7),
                'max_results': config.get('max_results', 10),
                'chunk_size': config.get('chunk_size', 1000),
                'chunk_overlap': config.get('chunk_overlap', 200)
            }
            logger.info(f"Loaded vector store config: {self.vector_store_config['name']}")
        else:
            logger.warning("No vector store tool instances found, using default configuration")
            self.vector_store_config = self._get_default_vector_store_config()
    
    def _get_default_embedding_config(self) -> Dict[str, Any]:
        """Default embedding configuration"""
        return {
            'name': 'text-embedding-3-small',
            'display_name': 'OpenAI Text Embedding 3 Small (Default)',
            'provider': 'OpenAI',
            'api_endpoint': 'https://api.openai.com/v1/embeddings',
            'capabilities': {'dimensions': 1536, 'max_input_tokens': 8191},
            'pricing_info': {'cost_per_1k': 0.00002, 'currency': 'USD'},
            'performance_metrics': {'latency_p95': 0.5, 'throughput_tps': 300, 'availability': 99.9},
            'input_signature': {},
            'output_signature': {},
            'dimensions': 1536
        }
    
    def _get_default_llm_config(self) -> Dict[str, Any]:
        """Default LLM configuration"""
        return {
            'name': 'gpt-3.5-turbo',
            'display_name': 'GPT-3.5 Turbo (Default)',
            'provider': 'OpenAI',
            'api_endpoint': 'https://api.openai.com/v1/chat/completions',
            'capabilities': {'max_tokens': 16385, 'supports_functions': True},
            'pricing_info': {'input_cost_per_1k': 0.0005, 'output_cost_per_1k': 0.0015, 'currency': 'USD'},
            'performance_metrics': {'latency_p95': 1.5, 'throughput_tps': 100, 'availability': 99.9},
            'input_signature': {},
            'output_signature': {}
        }
    
    def _get_default_vector_store_config(self) -> Dict[str, Any]:
        """Default vector store configuration"""
        return {
            'name': 'pgvector-default',
            'display_name': 'PGVector Default Configuration',
            'template_name': 'pgvector-rag',
            'type': 'pgvector',
            'configuration': {},
            'similarity_threshold': 0.7,
            'max_results': 10,
            'chunk_size': 1000,
            'chunk_overlap': 200
        }
    
    def needs_refresh(self) -> bool:
        """Check if configuration needs to be refreshed"""
        if not self.last_refresh:
            return True
        
        time_since_refresh = (datetime.utcnow() - self.last_refresh).total_seconds()
        return time_since_refresh > self.refresh_interval_seconds
    
    def get_embedding_model_name(self) -> str:
        """Get the current embedding model name"""
        return self.embedding_config['name'] if self.embedding_config else 'text-embedding-3-small'
    
    def get_embedding_dimensions(self) -> int:
        """Get the embedding dimensions"""
        return self.embedding_config['dimensions'] if self.embedding_config else 1536
    
    def get_llm_model_name(self) -> str:
        """Get the current LLM model name"""
        return self.llm_config['name'] if self.llm_config else 'gpt-3.5-turbo'
    
    def get_similarity_threshold(self) -> float:
        """Get the similarity threshold for searches"""
        return self.vector_store_config['similarity_threshold'] if self.vector_store_config else 0.7
    
    def get_max_results(self) -> int:
        """Get the maximum number of results for searches"""
        return self.vector_store_config['max_results'] if self.vector_store_config else 10
    
    def get_chunk_config(self) -> Dict[str, int]:
        """Get the chunk configuration"""
        if self.vector_store_config:
            return {
                'chunk_size': self.vector_store_config['chunk_size'],
                'chunk_overlap': self.vector_store_config['chunk_overlap']
            }
        return {'chunk_size': 1000, 'chunk_overlap': 200}
    
    async def refresh_if_needed(self, async_session: AsyncSession) -> None:
        """Refresh configuration if needed"""
        if self.needs_refresh():
            await self.load_config(async_session)


# Global configuration instance
rag_config = RAGConfig()
