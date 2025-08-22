"""
LangGraph Model Service
Manages LLM and embedding models with LangGraph integration
Supports Google Gemini, Azure OpenAI, OpenAI, and Ollama
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import os

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, insert, update
from sqlalchemy.orm import sessionmaker

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    from langchain_community.llms import Ollama
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.embeddings import Embeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseLanguageModel = None
    Embeddings = None

logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    GOOGLE_GEMINI = "google_gemini"
    OLLAMA = "ollama"

class ModelType(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"

class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ERROR = "error"

class LLMModelConfig(BaseModel):
    """Configuration for LLM models"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop_sequences: List[str] = Field(default_factory=list)

class EmbeddingModelConfig(BaseModel):
    """Configuration for embedding models"""
    dimensions: Optional[int] = Field(default=None, gt=0)
    batch_size: int = Field(default=512, gt=0)
    normalize: bool = Field(default=True)

class ModelCapabilities(BaseModel):
    """Model capabilities information"""
    max_tokens: Optional[int] = None
    supports_streaming: bool = False
    supports_function_calling: bool = False
    input_modalities: List[str] = Field(default_factory=lambda: ["text"])
    output_modalities: List[str] = Field(default_factory=lambda: ["text"])
    dimensions: Optional[int] = None  # For embeddings
    max_input_tokens: Optional[int] = None  # For embeddings
    supports_batching: bool = False  # For embeddings
    supported_languages: List[str] = Field(default_factory=lambda: ["en"])

class PricingInfo(BaseModel):
    """Pricing information for models"""
    input_cost_per_token: float = 0.0
    output_cost_per_token: float = 0.0
    cost_per_token: float = 0.0  # For embeddings
    currency: str = "USD"

class PerformanceMetrics(BaseModel):
    """Performance metrics for models"""
    avg_latency: float = 0.0
    tokens_per_second: float = 0.0
    throughput: float = 0.0  # For embeddings
    availability: float = 99.9

class LangGraphModelService:
    """Service for managing LLM and embedding models with LangGraph integration"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.model_instances: Dict[str, Union[BaseLanguageModel, Embeddings]] = {}
        self.default_llm_id: Optional[str] = None
        self.default_embedding_id: Optional[str] = None
        # Use unified_models table instead of separate llm_models and embedding_models
        self.models_table = "unified_models"
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, using mock implementations")
        
        # Model factory mappings
        self.llm_factories = {
            ModelProvider.OPENAI: self._create_openai_llm,
            ModelProvider.AZURE_OPENAI: self._create_azure_openai_llm,
            ModelProvider.GOOGLE_GEMINI: self._create_google_gemini_llm,
            ModelProvider.OLLAMA: self._create_ollama_llm,
        }
        
        self.embedding_factories = {
            ModelProvider.OPENAI: self._create_openai_embedding,
            ModelProvider.AZURE_OPENAI: self._create_azure_openai_embedding,
            ModelProvider.GOOGLE_GEMINI: self._create_google_gemini_embedding,
            ModelProvider.OLLAMA: self._create_ollama_embedding,
        }
        
        logger.info("LangGraph Model Service initialized")

    async def create_llm_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new LLM model configuration"""
        try:
            # Validate provider
            provider = ModelProvider(model_data.get("provider"))
            
            # Create model configuration
            model_config = LLMModelConfig(**model_data.get("model_config", {}))
            capabilities = ModelCapabilities(**model_data.get("capabilities", {}))
            pricing_info = PricingInfo(**model_data.get("pricing_info", {}))
            performance_metrics = PerformanceMetrics(**model_data.get("performance_metrics", {}))
            
            # Create database record
            model_record = {
                "id": model_data.get("id", self._generate_id()),
                "name": model_data["name"],
                "display_name": model_data["display_name"],
                "provider": provider.value,
                "model_type": ModelType.LLM.value,
                "api_endpoint": model_data.get("api_endpoint"),
                "api_key": model_data.get("api_key"),
                "status": ModelStatus(model_data.get("status", ModelStatus.INACTIVE)),
                "capabilities": capabilities.dict(),
                "pricing_info": pricing_info.dict(),
                "performance_metrics": performance_metrics.dict(),
                "model_config": model_config.dict(),
                "health_url": model_data.get("health_url"),
                "dns_name": model_data.get("dns_name"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Store in database (mock for now)
            await self._store_model_record(model_record)
            
            # Initialize model instance if active
            if model_record["status"] == ModelStatus.ACTIVE:
                await self._initialize_llm_model(model_record["id"])
            
            logger.info(f"Created LLM model: {model_record['id']}")
            return {"success": True, "id": model_record["id"], "model": model_record}
            
        except Exception as e:
            logger.error(f"Error creating LLM model: {str(e)}")
            return {"success": False, "error": str(e)}

    async def create_embedding_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new embedding model configuration"""
        try:
            # Validate provider
            provider = ModelProvider(model_data.get("provider"))
            
            # Create model configuration
            model_config = EmbeddingModelConfig(**model_data.get("model_config", {}))
            capabilities = ModelCapabilities(**model_data.get("capabilities", {}))
            pricing_info = PricingInfo(**model_data.get("pricing_info", {}))
            performance_metrics = PerformanceMetrics(**model_data.get("performance_metrics", {}))
            
            # Create database record
            model_record = {
                "id": model_data.get("id", self._generate_id()),
                "name": model_data["name"],
                "display_name": model_data["display_name"],
                "provider": provider.value,
                "model_type": ModelType.EMBEDDING.value,
                "api_endpoint": model_data.get("api_endpoint"),
                "api_key": model_data.get("api_key"),
                "status": ModelStatus(model_data.get("status", ModelStatus.INACTIVE)),
                "capabilities": capabilities.dict(),
                "pricing_info": pricing_info.dict(),
                "performance_metrics": performance_metrics.dict(),
                "model_config": model_config.dict(),
                "health_url": model_data.get("health_url"),
                "dns_name": model_data.get("dns_name"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Store in database (mock for now)
            await self._store_model_record(model_record)
            
            # Initialize model instance if active
            if model_record["status"] == ModelStatus.ACTIVE:
                await self._initialize_embedding_model(model_record["id"])
            
            logger.info(f"Created embedding model: {model_record['id']}")
            return {"success": True, "id": model_record["id"], "model": model_record}
            
        except Exception as e:
            logger.error(f"Error creating embedding model: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get a model by ID"""
        try:
            # Mock database lookup
            return await self._get_model_record(model_id)
        except Exception as e:
            logger.error(f"Error getting model {model_id}: {str(e)}")
            return None

    async def list_models(
        self, 
        model_type: Optional[ModelType] = None,
        provider: Optional[ModelProvider] = None,
        status: Optional[ModelStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List models with filtering"""
        try:
            # Mock database query
            return await self._list_model_records(model_type, provider, status, limit, offset)
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []

    async def update_model(self, model_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a model configuration"""
        try:
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            # Update fields
            for key, value in update_data.items():
                if key in ["name", "display_name", "status", "api_endpoint", "api_key"]:
                    model_record[key] = value
                elif key in ["capabilities", "pricing_info", "performance_metrics", "model_config"]:
                    model_record[key].update(value)
            
            model_record["updated_at"] = datetime.utcnow()
            
            # Update database record
            await self._store_model_record(model_record)
            
            # Reinitialize model instance if needed
            if model_record["status"] == ModelStatus.ACTIVE.value:
                if model_record["model_type"] == ModelType.LLM.value:
                    await self._initialize_llm_model(model_id)
                else:
                    await self._initialize_embedding_model(model_id)
            else:
                # Remove from active instances
                if model_id in self.model_instances:
                    del self.model_instances[model_id]
            
            return {"success": True, "model": model_record}
            
        except Exception as e:
            logger.error(f"Error updating model {model_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_model(self, model_id: str) -> Dict[str, Any]:
        """Delete a model"""
        try:
            # Remove from active instances
            if model_id in self.model_instances:
                del self.model_instances[model_id]
            
            # Remove default assignment if needed
            if self.default_llm_id == model_id:
                self.default_llm_id = None
            if self.default_embedding_id == model_id:
                self.default_embedding_id = None
            
            # Remove from database
            await self._delete_model_record(model_id)
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error deleting model {model_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def test_model(self, model_id: str) -> Dict[str, Any]:
        """Test a model's connectivity and functionality"""
        try:
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            # Initialize model instance for testing
            if model_record["model_type"] == ModelType.LLM.value:
                model_instance = await self._create_llm_instance(model_record)
                # Test with a simple prompt
                if LANGCHAIN_AVAILABLE and model_instance:
                    try:
                        result = await model_instance.ainvoke("Hello! Please respond with 'Test successful.'")
                        return {"success": True, "response": str(result), "status": "healthy"}
                    except Exception as e:
                        return {"success": False, "error": f"Model test failed: {str(e)}", "status": "error"}
                else:
                    return {"success": True, "response": "Mock test successful", "status": "healthy"}
            else:
                model_instance = await self._create_embedding_instance(model_record)
                # Test with a simple text embedding
                if LANGCHAIN_AVAILABLE and model_instance:
                    try:
                        result = await model_instance.aembed_query("Test embedding")
                        return {"success": True, "dimensions": len(result), "status": "healthy"}
                    except Exception as e:
                        return {"success": False, "error": f"Model test failed: {str(e)}", "status": "error"}
                else:
                    return {"success": True, "dimensions": 768, "status": "healthy"}
            
        except Exception as e:
            logger.error(f"Error testing model {model_id}: {str(e)}")
            return {"success": False, "error": str(e), "status": "error"}

    async def set_default_llm(self, model_id: str) -> Dict[str, Any]:
        """Set the default LLM model"""
        try:
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            if model_record["model_type"] != ModelType.LLM.value:
                return {"success": False, "error": "Model is not an LLM"}
            
            if model_record["status"] != ModelStatus.ACTIVE.value:
                return {"success": False, "error": "Model is not active"}
            
            self.default_llm_id = model_id
            logger.info(f"Set default LLM to: {model_id}")
            return {"success": True, "default_llm_id": model_id}
            
        except Exception as e:
            logger.error(f"Error setting default LLM: {str(e)}")
            return {"success": False, "error": str(e)}

    async def set_default_embedding(self, model_id: str) -> Dict[str, Any]:
        """Set the default embedding model"""
        try:
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            if model_record["model_type"] != ModelType.EMBEDDING.value:
                return {"success": False, "error": "Model is not an embedding model"}
            
            if model_record["status"] != ModelStatus.ACTIVE.value:
                return {"success": False, "error": "Model is not active"}
            
            self.default_embedding_id = model_id
            logger.info(f"Set default embedding model to: {model_id}")
            return {"success": True, "default_embedding_id": model_id}
            
        except Exception as e:
            logger.error(f"Error setting default embedding model: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_default_llm(self) -> Optional[Union[BaseLanguageModel, Dict[str, Any]]]:
        """Get the default LLM model instance or configuration"""
        if not self.default_llm_id:
            return None
        
        if self.default_llm_id in self.model_instances:
            return self.model_instances[self.default_llm_id]
        
        # Initialize if not in memory
        await self._initialize_llm_model(self.default_llm_id)
        return self.model_instances.get(self.default_llm_id)

    async def get_default_embedding(self) -> Optional[Union[Embeddings, Dict[str, Any]]]:
        """Get the default embedding model instance or configuration"""
        if not self.default_embedding_id:
            return None
        
        if self.default_embedding_id in self.model_instances:
            return self.model_instances[self.default_embedding_id]
        
        # Initialize if not in memory
        await self._initialize_embedding_model(self.default_embedding_id)
        return self.model_instances.get(self.default_embedding_id)

    async def get_model_instance(self, model_id: str) -> Optional[Union[BaseLanguageModel, Embeddings]]:
        """Get a model instance for use in tools and agents"""
        if model_id in self.model_instances:
            return self.model_instances[model_id]
        
        model_record = await self._get_model_record(model_id)
        if not model_record:
            return None
        
        if model_record["status"] != ModelStatus.ACTIVE.value:
            return None
        
        if model_record["model_type"] == ModelType.LLM.value:
            await self._initialize_llm_model(model_id)
        else:
            await self._initialize_embedding_model(model_id)
        
        return self.model_instances.get(model_id)

    # ============================================================================
    # PRIVATE METHODS - LLM FACTORIES
    # ============================================================================

    async def _create_openai_llm(self, model_record: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create OpenAI LLM instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            config = model_record.get("model_config", {})
            return ChatOpenAI(
                model=model_record["name"],
                api_key=model_record.get("api_key") or os.getenv("OPENAI_API_KEY"),
                base_url=model_record.get("api_endpoint"),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 4096),
                top_p=config.get("top_p", 1.0),
                frequency_penalty=config.get("frequency_penalty", 0.0),
                presence_penalty=config.get("presence_penalty", 0.0),
                stop=config.get("stop_sequences", []) or None
            )
        except Exception as e:
            logger.error(f"Error creating OpenAI LLM: {str(e)}")
            return None

    async def _create_azure_openai_llm(self, model_record: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create Azure OpenAI LLM instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            config = model_record.get("model_config", {})
            return AzureChatOpenAI(
                deployment_name=model_record["name"],
                api_key=model_record.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=model_record.get("api_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 4096),
                top_p=config.get("top_p", 1.0),
                frequency_penalty=config.get("frequency_penalty", 0.0),
                presence_penalty=config.get("presence_penalty", 0.0),
            )
        except Exception as e:
            logger.error(f"Error creating Azure OpenAI LLM: {str(e)}")
            return None

    async def _create_google_gemini_llm(self, model_record: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create Google Gemini LLM instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            config = model_record.get("model_config", {})
            return ChatGoogleGenerativeAI(
                model=model_record["name"],
                google_api_key=model_record.get("api_key") or os.getenv("GOOGLE_API_KEY"),
                temperature=config.get("temperature", 0.7),
                max_output_tokens=config.get("max_tokens", 4096),
                top_p=config.get("top_p", 1.0),
                top_k=config.get("top_k", 40),
            )
        except Exception as e:
            logger.error(f"Error creating Google Gemini LLM: {str(e)}")
            return None

    async def _create_ollama_llm(self, model_record: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create Ollama LLM instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            config = model_record.get("model_config", {})
            return Ollama(
                model=model_record["name"],
                base_url=model_record.get("api_endpoint", "http://localhost:11434"),
                temperature=config.get("temperature", 0.7),
                num_predict=config.get("max_tokens", 4096),
                top_p=config.get("top_p", 1.0),
                stop=config.get("stop_sequences", []) or None
            )
        except Exception as e:
            logger.error(f"Error creating Ollama LLM: {str(e)}")
            return None

    # ============================================================================
    # PRIVATE METHODS - EMBEDDING FACTORIES
    # ============================================================================

    async def _create_openai_embedding(self, model_record: Dict[str, Any]) -> Optional[Embeddings]:
        """Create OpenAI embedding instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            config = model_record.get("model_config", {})
            return OpenAIEmbeddings(
                model=model_record["name"],
                api_key=model_record.get("api_key") or os.getenv("OPENAI_API_KEY"),
                base_url=model_record.get("api_endpoint"),
                dimensions=config.get("dimensions"),
                chunk_size=config.get("batch_size", 1000),
            )
        except Exception as e:
            logger.error(f"Error creating OpenAI embedding: {str(e)}")
            return None

    async def _create_azure_openai_embedding(self, model_record: Dict[str, Any]) -> Optional[Embeddings]:
        """Create Azure OpenAI embedding instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            config = model_record.get("model_config", {})
            return AzureOpenAIEmbeddings(
                model=model_record["name"],
                api_key=model_record.get("api_key") or os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=model_record.get("api_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                dimensions=config.get("dimensions"),
                chunk_size=config.get("batch_size", 1000),
            )
        except Exception as e:
            logger.error(f"Error creating Azure OpenAI embedding: {str(e)}")
            return None

    async def _create_google_gemini_embedding(self, model_record: Dict[str, Any]) -> Optional[Embeddings]:
        """Create Google Gemini embedding instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            return GoogleGenerativeAIEmbeddings(
                model=model_record["name"],
                google_api_key=model_record.get("api_key") or os.getenv("GOOGLE_API_KEY"),
            )
        except Exception as e:
            logger.error(f"Error creating Google Gemini embedding: {str(e)}")
            return None

    async def _create_ollama_embedding(self, model_record: Dict[str, Any]) -> Optional[Embeddings]:
        """Create Ollama embedding instance"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            return OllamaEmbeddings(
                model=model_record["name"],
                base_url=model_record.get("api_endpoint", "http://localhost:11434"),
            )
        except Exception as e:
            logger.error(f"Error creating Ollama embedding: {str(e)}")
            return None

    # ============================================================================
    # PRIVATE METHODS - INITIALIZATION
    # ============================================================================

    async def _initialize_llm_model(self, model_id: str) -> bool:
        """Initialize an LLM model instance"""
        try:
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return False
            
            model_instance = await self._create_llm_instance(model_record)
            if model_instance:
                self.model_instances[model_id] = model_instance
                logger.info(f"Initialized LLM model: {model_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error initializing LLM model {model_id}: {str(e)}")
            return False

    async def _initialize_embedding_model(self, model_id: str) -> bool:
        """Initialize an embedding model instance"""
        try:
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return False
            
            model_instance = await self._create_embedding_instance(model_record)
            if model_instance:
                self.model_instances[model_id] = model_instance
                logger.info(f"Initialized embedding model: {model_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error initializing embedding model {model_id}: {str(e)}")
            return False

    async def _create_llm_instance(self, model_record: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create LLM instance based on provider"""
        provider = ModelProvider(model_record["provider"])
        if provider in self.llm_factories:
            return await self.llm_factories[provider](model_record)
        return None

    async def _create_embedding_instance(self, model_record: Dict[str, Any]) -> Optional[Embeddings]:
        """Create embedding instance based on provider"""
        provider = ModelProvider(model_record["provider"])
        if provider in self.embedding_factories:
            return await self.embedding_factories[provider](model_record)
        return None

    # ============================================================================
    # PRIVATE METHODS - DATABASE OPERATIONS (MOCK)
    # ============================================================================

    def _generate_id(self) -> str:
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())

    async def _store_model_record(self, model_record: Dict[str, Any]) -> None:
        """Store model record in unified_models table"""
        try:
            # Convert dict to match database schema
            insert_data = {
                "id": model_record.get("id"),
                "name": model_record["name"],
                "display_name": model_record["display_name"],
                "provider": model_record["provider"],
                "model_type": model_record["model_type"],
                "api_endpoint": model_record.get("api_endpoint"),
                "api_key_encrypted": model_record.get("api_key"),  # Note: Should encrypt in production
                "status": model_record["status"],
                "capabilities": model_record.get("capabilities", {}),
                "pricing_info": model_record.get("pricing_info", {}),
                "performance_metrics": model_record.get("performance_metrics", {}),
                "model_config": model_record.get("model_config", {}),
                "health_url": model_record.get("health_url"),
                "dns_name": model_record.get("dns_name"),
                "is_default": model_record.get("is_default", False),
                "priority": model_record.get("priority", 1000),
                "max_tokens": model_record.get("max_tokens"),
                "supports_streaming": model_record.get("supports_streaming", False),
                "dimensions": model_record.get("dimensions"),
                "max_input_tokens": model_record.get("max_input_tokens"),
                "cost_per_token": model_record.get("cost_per_token"),
                "tags": model_record.get("tags", []),
                "project_tags": model_record.get("project_tags", []),
                "is_active": model_record.get("is_active", True),
                "created_at": model_record.get("created_at"),
                "updated_at": model_record.get("updated_at"),
                "created_by": model_record.get("created_by"),
                "updated_by": model_record.get("updated_by")
            }
            
            # Insert or update
            stmt = text("""
                INSERT INTO unified_models (
                    id, name, display_name, provider, model_type, api_endpoint, api_key_encrypted,
                    status, capabilities, pricing_info, performance_metrics, model_config,
                    health_url, dns_name, is_default, priority, max_tokens, supports_streaming,
                    dimensions, max_input_tokens, cost_per_token, tags, project_tags, is_active,
                    created_at, updated_at, created_by, updated_by
                ) VALUES (
                    :id, :name, :display_name, :provider, :model_type, :api_endpoint, :api_key_encrypted,
                    :status, :capabilities, :pricing_info, :performance_metrics, :model_config,
                    :health_url, :dns_name, :is_default, :priority, :max_tokens, :supports_streaming,
                    :dimensions, :max_input_tokens, :cost_per_token, :tags, :project_tags, :is_active,
                    :created_at, :updated_at, :created_by, :updated_by
                )
                ON CONFLICT (name, provider) 
                DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    status = EXCLUDED.status,
                    capabilities = EXCLUDED.capabilities,
                    pricing_info = EXCLUDED.pricing_info,
                    performance_metrics = EXCLUDED.performance_metrics,
                    model_config = EXCLUDED.model_config,
                    updated_at = EXCLUDED.updated_at,
                    updated_by = EXCLUDED.updated_by
            """)
            
            await self.db_session.execute(stmt, insert_data)
            await self.db_session.commit()
            
            logger.info(f"Stored model record: {model_record['id']}")
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error storing model record: {str(e)}")
            raise

    async def _get_model_record(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model record from unified_models table"""
        try:
            stmt = text("""
                SELECT id, name, display_name, provider, model_type, api_endpoint, api_key_encrypted,
                       status, capabilities, pricing_info, performance_metrics, model_config,
                       health_url, dns_name, is_default, priority, max_tokens, supports_streaming,
                       dimensions, max_input_tokens, cost_per_token, tags, project_tags, is_active,
                       created_at, updated_at, created_by, updated_by
                FROM unified_models 
                WHERE id = :model_id
            """)
            
            result = await self.db_session.execute(stmt, {"model_id": model_id})
            row = result.fetchone()
            
            if row:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "display_name": row.display_name,
                    "provider": row.provider,
                    "model_type": row.model_type,
                    "api_endpoint": row.api_endpoint,
                    "api_key": row.api_key_encrypted,
                    "status": row.status,
                    "capabilities": row.capabilities or {},
                    "pricing_info": row.pricing_info or {},
                    "performance_metrics": row.performance_metrics or {},
                    "model_config": row.model_config or {},
                    "health_url": row.health_url,
                    "dns_name": row.dns_name,
                    "is_default": row.is_default,
                    "priority": row.priority,
                    "max_tokens": row.max_tokens,
                    "supports_streaming": row.supports_streaming,
                    "dimensions": row.dimensions,
                    "max_input_tokens": row.max_input_tokens,
                    "cost_per_token": row.cost_per_token,
                    "tags": row.tags or [],
                    "project_tags": row.project_tags or [],
                    "is_active": row.is_active,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                    "created_by": row.created_by,
                    "updated_by": row.updated_by
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting model record {model_id}: {str(e)}")
            return None

    async def _list_model_records(
        self, 
        model_type: Optional[ModelType] = None,
        provider: Optional[ModelProvider] = None,
        status: Optional[ModelStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List model records from unified_models table with filtering"""
        try:
            # Build WHERE conditions
            conditions = []
            params = {"limit": limit, "offset": offset}
            
            if model_type:
                conditions.append("model_type = :model_type")
                params["model_type"] = model_type.value
                
            if provider:
                conditions.append("provider = :provider")
                params["provider"] = provider.value
                
            if status:
                conditions.append("status = :status")
                params["status"] = status.value
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            stmt = text(f"""
                SELECT id, name, display_name, provider, model_type, api_endpoint,
                       status, capabilities, pricing_info, performance_metrics, model_config,
                       health_url, dns_name, is_default, priority, max_tokens, supports_streaming,
                       dimensions, max_input_tokens, cost_per_token, tags, project_tags, is_active,
                       created_at, updated_at
                FROM unified_models 
                WHERE {where_clause}
                ORDER BY model_type, priority ASC, display_name
                LIMIT :limit OFFSET :offset
            """)
            
            result = await self.db_session.execute(stmt, params)
            rows = result.fetchall()
            
            models = []
            for row in rows:
                models.append({
                    "id": str(row.id),
                    "name": row.name,
                    "display_name": row.display_name,
                    "provider": row.provider,
                    "model_type": row.model_type,
                    "api_endpoint": row.api_endpoint,
                    "status": row.status,
                    "capabilities": row.capabilities or {},
                    "pricing_info": row.pricing_info or {},
                    "performance_metrics": row.performance_metrics or {},
                    "model_config": row.model_config or {},
                    "health_url": row.health_url,
                    "dns_name": row.dns_name,
                    "is_default": row.is_default,
                    "priority": row.priority,
                    "max_tokens": row.max_tokens,
                    "supports_streaming": row.supports_streaming,
                    "dimensions": row.dimensions,
                    "max_input_tokens": row.max_input_tokens,
                    "cost_per_token": row.cost_per_token,
                    "tags": row.tags or [],
                    "project_tags": row.project_tags or [],
                    "is_active": row.is_active,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at
                })
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing model records: {str(e)}")
            return []

    async def _delete_model_record(self, model_id: str) -> None:
        """Delete model record from unified_models table"""
        try:
            stmt = text("DELETE FROM unified_models WHERE id = :model_id")
            await self.db_session.execute(stmt, {"model_id": model_id})
            await self.db_session.commit()
            
            logger.info(f"Deleted model record: {model_id}")
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error deleting model record {model_id}: {str(e)}")
            raise

    # ============================================================================
    # HEALTH AND MONITORING
    # ============================================================================

    async def get_default_llm(self) -> Optional[Dict[str, Any]]:
        """Get the default LLM model from database"""
        try:
            stmt = text("""
                SELECT id, name, display_name, provider, model_type, api_endpoint, api_key_encrypted,
                       status, capabilities, pricing_info, model_config, health_url, dns_name
                FROM unified_models 
                WHERE model_type = 'llm' AND is_default = TRUE AND status = 'active'
                LIMIT 1
            """)
            
            result = await self.db_session.execute(stmt)
            row = result.fetchone()
            
            if row:
                self.default_llm_id = str(row.id)
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "display_name": row.display_name,
                    "provider": row.provider,
                    "model_type": row.model_type,
                    "api_endpoint": row.api_endpoint,
                    "api_key": row.api_key_encrypted,
                    "status": row.status,
                    "capabilities": row.capabilities or {},
                    "pricing_info": row.pricing_info or {},
                    "model_config": row.model_config or {},
                    "health_url": row.health_url,
                    "dns_name": row.dns_name
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting default LLM: {str(e)}")
            return None

    async def get_default_embedding(self) -> Optional[Dict[str, Any]]:
        """Get the default embedding model from database"""
        try:
            stmt = text("""
                SELECT id, name, display_name, provider, model_type, api_endpoint, api_key_encrypted,
                       status, capabilities, pricing_info, model_config, health_url, dns_name, dimensions
                FROM unified_models 
                WHERE model_type = 'embedding' AND is_default = TRUE AND status = 'active'
                LIMIT 1
            """)
            
            result = await self.db_session.execute(stmt)
            row = result.fetchone()
            
            if row:
                self.default_embedding_id = str(row.id)
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "display_name": row.display_name,
                    "provider": row.provider,
                    "model_type": row.model_type,
                    "api_endpoint": row.api_endpoint,
                    "api_key": row.api_key_encrypted,
                    "status": row.status,
                    "capabilities": row.capabilities or {},
                    "pricing_info": row.pricing_info or {},
                    "model_config": row.model_config or {},
                    "health_url": row.health_url,
                    "dns_name": row.dns_name,
                    "dimensions": row.dimensions
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting default embedding model: {str(e)}")
            return None

    async def set_default_llm(self, model_id: str) -> Dict[str, Any]:
        """Set a model as the default LLM"""
        try:
            # First verify the model exists and is an LLM
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            if model_record["model_type"] != "llm":
                return {"success": False, "error": "Model is not an LLM"}
            
            if model_record["status"] != "active":
                return {"success": False, "error": "Model is not active"}
            
            # Update the model to be default (database trigger will handle unsetting others)
            stmt = text("""
                UPDATE unified_models 
                SET is_default = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = :model_id
            """)
            
            await self.db_session.execute(stmt, {"model_id": model_id})
            await self.db_session.commit()
            
            self.default_llm_id = model_id
            logger.info(f"Set default LLM to: {model_id}")
            
            return {"success": True, "message": f"Set {model_record['display_name']} as default LLM"}
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error setting default LLM {model_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def set_default_embedding(self, model_id: str) -> Dict[str, Any]:
        """Set a model as the default embedding model"""
        try:
            # First verify the model exists and is an embedding model
            model_record = await self._get_model_record(model_id)
            if not model_record:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            if model_record["model_type"] != "embedding":
                return {"success": False, "error": "Model is not an embedding model"}
            
            if model_record["status"] != "active":
                return {"success": False, "error": "Model is not active"}
            
            # Update the model to be default (database trigger will handle unsetting others)
            stmt = text("""
                UPDATE unified_models 
                SET is_default = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = :model_id
            """)
            
            await self.db_session.execute(stmt, {"model_id": model_id})
            await self.db_session.commit()
            
            self.default_embedding_id = model_id
            logger.info(f"Set default embedding model to: {model_id}")
            
            return {"success": True, "message": f"Set {model_record['display_name']} as default embedding model"}
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error setting default embedding model {model_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the model service"""
        return {
            "status": "healthy",
            "active_models": len(self.model_instances),
            "default_llm_id": self.default_llm_id,
            "default_embedding_id": self.default_embedding_id,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "supported_providers": [provider.value for provider in ModelProvider],
            "timestamp": datetime.utcnow().isoformat()
        }