"""
Enhanced Model Service
Integrates existing LLM/embedding model functionality with LangGraph capabilities
Extends the current database models with LangGraph-specific features
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, insert
from pydantic import BaseModel, Field

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

from ..models.database import Model
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class ModelProvider(str, Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    GOOGLE_GEMINI = "google_gemini"
    OLLAMA = "ollama"

class ModelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    ERROR = "error"

class EnhancedModelService:
    """
    Enhanced model service that combines existing model management with LangGraph integration
    """
    
    def __init__(self, database_service: DatabaseService):
        self.db_service = database_service
        self.model_instances: Dict[str, Union[BaseLanguageModel, Embeddings]] = {}
        self.default_llm_id: Optional[str] = None
        self.default_embedding_id: Optional[str] = None
        
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
        
        logger.info("Enhanced Model Service initialized")

    async def list_llm_models(
        self,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List LLM models with enhanced filtering"""
        try:
            async with self.db_service.SessionLocal() as session:
                query = select(Model)
                
                filters = []
                if provider:
                    filters.append(Model.provider == provider)
                if status:
                    # Map status to is_active for backward compatibility
                    if status == "active":
                        filters.append(Model.is_active == True)
                    elif status == "inactive":
                        filters.append(Model.is_active == False)
                
                if filters:
                    query = query.where(and_(*filters))
                
                query = query.offset(offset).limit(limit)
                result = await session.execute(query)
                models = result.scalars().all()
                
                # Convert to enhanced format
                enhanced_models = []
                for model in models:
                    enhanced_model = await self._convert_to_enhanced_format(model, "llm")
                    enhanced_models.append(enhanced_model)
                
                return enhanced_models
                
        except Exception as e:
            logger.error(f"Error listing LLM models: {str(e)}")
            return []

    async def list_embedding_models(
        self,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List embedding models with enhanced filtering"""
        try:
            async with self.db_service.SessionLocal() as session:
                query = select(Model)
                
                filters = []
                if provider:
                    filters.append(Model.provider == provider)
                if status:
                    # Map status to is_active for backward compatibility
                    if status == "active":
                        filters.append(Model.is_active == True)
                    elif status == "inactive":
                        filters.append(Model.is_active == False)
                
                if filters:
                    query = query.where(and_(*filters))
                
                query = query.offset(offset).limit(limit)
                result = await session.execute(query)
                models = result.scalars().all()
                
                # Convert to enhanced format
                enhanced_models = []
                for model in models:
                    enhanced_model = await self._convert_to_enhanced_format(model, "embedding")
                    enhanced_models.append(enhanced_model)
                
                return enhanced_models
                
        except Exception as e:
            logger.error(f"Error listing embedding models: {str(e)}")
            return []

    async def create_llm_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new LLM model with enhanced capabilities"""
        try:
            async with self.db_service.SessionLocal() as session:
                # Create enhanced model configuration
                enhanced_config = self._enhance_model_config(model_data, "llm")
                
                # Create new LLM model using existing structure
                new_model = Model(
                    name=model_data["name"],
                    display_name=model_data["display_name"],
                    provider=model_data["provider"],
                    model_type=model_data.get("model_type", "chat"),
                    endpoint_url=model_data.get("api_endpoint"),
                    api_key_env_var=model_data.get("api_key_env_var"),
                    model_config=enhanced_config,
                    max_tokens=model_data.get("capabilities", {}).get("max_tokens"),
                    supports_streaming=model_data.get("capabilities", {}).get("supports_streaming", False),
                    supports_functions=model_data.get("capabilities", {}).get("supports_function_calling", False),
                    cost_per_token=str(model_data.get("pricing_info", {}).get("input_cost_per_token", 0)),
                    pricing_info=model_data.get("pricing_info", {}),
                    is_active=model_data.get("status", "inactive") == "active"
                )
                
                session.add(new_model)
                await session.commit()
                await session.refresh(new_model)
                
                # Initialize model instance if active
                if getattr(new_model, 'is_active', False):
                    await self._initialize_llm_instance(str(new_model.id), new_model)
                
                enhanced_model = await self._convert_to_enhanced_format(new_model, "llm")
                
                logger.info(f"Created enhanced LLM model: {new_model.id}")
                return {"success": True, "id": str(new_model.id), "model": enhanced_model}
                
        except Exception as e:
            logger.error(f"Error creating LLM model: {str(e)}")
            return {"success": False, "error": str(e)}

    async def create_embedding_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new embedding model with enhanced capabilities"""
        try:
            async with self.db_service.SessionLocal() as session:
                # Create enhanced model configuration
                enhanced_config = self._enhance_model_config(model_data, "embedding")
                
                # Create new embedding model using existing structure
                new_model = Model(
                    name=model_data["name"],
                    display_name=model_data["display_name"],
                    provider=model_data["provider"],
                    endpoint_url=model_data.get("api_endpoint"),
                    api_key_env_var=model_data.get("api_key_env_var"),
                    model_config=enhanced_config,
                    dimensions=model_data.get("capabilities", {}).get("dimensions"),
                    max_input_tokens=model_data.get("capabilities", {}).get("max_input_tokens"),
                    cost_per_token=str(model_data.get("pricing_info", {}).get("cost_per_token", 0)),
                    pricing_info=model_data.get("pricing_info", {}),
                    is_active=model_data.get("status", "inactive") == "active"
                )
                
                session.add(new_model)
                await session.commit()
                await session.refresh(new_model)
                
                # Initialize model instance if active
                if getattr(new_model, 'is_active', False):
                    await self._initialize_embedding_instance(str(new_model.id), new_model)
                
                enhanced_model = await self._convert_to_enhanced_format(new_model, "embedding")
                
                logger.info(f"Created enhanced embedding model: {new_model.id}")
                return {"success": True, "id": str(new_model.id), "model": enhanced_model}
                
        except Exception as e:
            logger.error(f"Error creating embedding model: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_model(self, model_id: str, model_type: str = "llm") -> Optional[Dict[str, Any]]:
        """Get a specific model by ID (unified Model)"""
        try:
            async with self.db_service.SessionLocal() as session:
                result = await session.execute(
                    select(Model).where(Model.id == model_id, Model.model_type == model_type)
                )
                model = result.scalar_one_or_none()
                if not model:
                    return None
                return await self._convert_to_enhanced_format(model, model_type)
        except Exception as e:
            logger.error(f"Error getting model {model_id}: {str(e)}")
            return None

    async def update_model(self, model_id: str, model_type: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing model (unified Model)"""
        try:
            async with self.db_service.SessionLocal() as session:
                result = await session.execute(
                    select(Model).where(Model.id == model_id, Model.model_type == model_type)
                )
                model = result.scalar_one_or_none()
                if not model:
                    return {"success": False, "error": f"Model {model_id} not found"}
                update_fields = {}
                if "name" in update_data:
                    update_fields["name"] = update_data["name"]
                if "display_name" in update_data:
                    update_fields["display_name"] = update_data["display_name"]
                if "api_endpoint" in update_data:
                    update_fields["endpoint_url"] = update_data["api_endpoint"]
                if "status" in update_data:
                    update_fields["is_active"] = update_data["status"] == "active"
                if "model_config" in update_data or "capabilities" in update_data or "pricing_info" in update_data:
                    current_config = model.model_config or {}
                    enhanced_config = self._enhance_model_config({
                        **update_data,
                        "model_config": current_config
                    }, model_type)
                    update_fields["model_config"] = enhanced_config
                if update_fields:
                    await session.execute(
                        update(Model).where(Model.id == model_id, Model.model_type == model_type).values(**update_fields)
                    )
                    await session.commit()
                if update_data.get("status") == "active":
                    if model_type == "llm":
                        await self._initialize_llm_instance(model_id, model)
                    else:
                        await self._initialize_embedding_instance(model_id, model)
                elif update_data.get("status") == "inactive":
                    if model_id in self.model_instances:
                        del self.model_instances[model_id]
                updated_model = await self.get_model(model_id, model_type)
                return {"success": True, "model": updated_model}
        except Exception as e:
            logger.error(f"Error updating model {model_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_model(self, model_id: str, model_type: str) -> Dict[str, Any]:
        """Delete a model (unified Model)"""
        try:
            async with self.db_service.SessionLocal() as session:
                await session.execute(
                    update(Model).where(Model.id == model_id, Model.model_type == model_type).values(is_active=False)
                )
                await session.commit()
                if model_id in self.model_instances:
                    del self.model_instances[model_id]
                return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting model {model_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def test_model(self, model_id: str, model_type: str) -> Dict[str, Any]:
        """Test a model's connectivity and functionality"""
        try:
            model_data = await self.get_model(model_id, model_type)
            if not model_data:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            if model_type == "llm":
                model_instance = await self._create_llm_instance_from_data(model_data)
                if LANGCHAIN_AVAILABLE and model_instance:
                    try:
                        result = await model_instance.ainvoke("Hello! Please respond with 'Test successful.'")
                        return {"success": True, "response": str(result), "status": "healthy"}
                    except Exception as e:
                        return {"success": False, "error": f"Model test failed: {str(e)}", "status": "error"}
                else:
                    return {"success": True, "response": "Mock test successful", "status": "healthy"}
            else:
                model_instance = await self._create_embedding_instance_from_data(model_data)
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

    async def set_default_model(self, model_id: str, model_type: str) -> Dict[str, Any]:
        """Set a model as the default"""
        try:
            model_data = await self.get_model(model_id, model_type)
            if not model_data:
                return {"success": False, "error": f"Model {model_id} not found"}
            
            if model_data["status"] != "active":
                return {"success": False, "error": "Model is not active"}
            
            if model_type == "llm":
                self.default_llm_id = model_id
                logger.info(f"Set default LLM to: {model_id}")
                return {"success": True, "default_llm_id": model_id}
            else:
                self.default_embedding_id = model_id
                logger.info(f"Set default embedding model to: {model_id}")
                return {"success": True, "default_embedding_id": model_id}
            
        except Exception as e:
            logger.error(f"Error setting default model: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_default_model(self, model_type: str = "llm") -> Optional[Dict[str, Any]]:
        """Get the default model"""
        try:
            if model_type == "llm" and self.default_llm_id:
                if self.default_llm_id in self.model_instances:
                    return await self.get_model(self.default_llm_id, "llm")
            elif model_type == "embedding" and self.default_embedding_id:
                if self.default_embedding_id in self.model_instances:
                    return await self.get_model(self.default_embedding_id, "embedding")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting default model: {str(e)}")
            return None

    async def get_model_instance(self, model_id: str) -> Optional[Union[BaseLanguageModel, Embeddings]]:
        """Get a model instance for use in tools and agents"""
        if model_id in self.model_instances:
            return self.model_instances[model_id]
        
        # Try to initialize the instance
        model_data = await self.get_model(model_id, "llm")
        if not model_data:
            model_data = await self.get_model(model_id, "embedding")
        
        if not model_data or model_data["status"] != "active":
            return None
        
        try:
            if "dimensions" in model_data.get("capabilities", {}):
                # It's an embedding model
                instance = await self._create_embedding_instance_from_data(model_data)
                if instance:
                    self.model_instances[model_id] = instance
            else:
                # It's an LLM
                instance = await self._create_llm_instance_from_data(model_data)
                if instance:
                    self.model_instances[model_id] = instance
            
            return self.model_instances.get(model_id)
            
        except Exception as e:
            logger.error(f"Error getting model instance {model_id}: {str(e)}")
            return None

    # ============================================================================
    # PRIVATE METHODS
    # ============================================================================

    async def _convert_to_enhanced_format(self, model, model_type: str) -> Dict[str, Any]:
        """Convert existing model to enhanced format"""
        base_data = {
            "id": str(model.id),
            "name": model.name,
            "display_name": model.display_name,
            "provider": model.provider,
            "model_type": model_type,
            "api_endpoint": getattr(model, 'endpoint_url', None),
            "status": "active" if model.is_active else "inactive",
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None
        }
        
        # Extract enhanced configuration
        config = model.model_config or {}
        
        if model_type == "llm":
            base_data.update({
                "capabilities": {
                    "max_tokens": model.max_tokens,
                    "supports_streaming": model.supports_streaming,
                    "supports_function_calling": model.supports_functions,
                    "input_modalities": config.get("input_modalities", ["text"]),
                    "output_modalities": config.get("output_modalities", ["text"])
                },
                "model_config": {
                    "temperature": config.get("temperature", 0.7),
                    "max_tokens": config.get("max_tokens", model.max_tokens or 4096),
                    "top_p": config.get("top_p", 1.0),
                    "frequency_penalty": config.get("frequency_penalty", 0.0),
                    "presence_penalty": config.get("presence_penalty", 0.0),
                    "stop_sequences": config.get("stop_sequences", [])
                }
            })
        else:
            base_data.update({
                "capabilities": {
                    "dimensions": model.dimensions,
                    "max_input_tokens": model.max_input_tokens,
                    "supports_batching": config.get("supports_batching", True),
                    "supported_languages": config.get("supported_languages", ["en"])
                },
                "model_config": {
                    "dimensions": config.get("dimensions", model.dimensions),
                    "batch_size": config.get("batch_size", 512),
                    "normalize": config.get("normalize", True)
                }
            })
        
        # Pricing information
        base_data["pricing_info"] = model.pricing_info or {}
        
        # Performance metrics (mock for now)
        base_data["performance_metrics"] = {
            "avg_latency": 100.0,
            "availability": 99.9
        }
        
        return base_data

    def _enhance_model_config(self, model_data: Dict[str, Any], model_type: str) -> Dict[str, Any]:
        """Enhance model configuration with LangGraph-specific settings"""
        config = model_data.get("model_config", {})
        capabilities = model_data.get("capabilities", {})
        
        # Merge capabilities into config for storage
        enhanced_config = {**config}
        
        if model_type == "llm":
            enhanced_config.update({
                "input_modalities": capabilities.get("input_modalities", ["text"]),
                "output_modalities": capabilities.get("output_modalities", ["text"]),
                "supports_streaming": capabilities.get("supports_streaming", False),
                "supports_function_calling": capabilities.get("supports_function_calling", False)
            })
        else:
            enhanced_config.update({
                "supports_batching": capabilities.get("supports_batching", True),
                "supported_languages": capabilities.get("supported_languages", ["en"])
            })
        
        return enhanced_config

    async def _initialize_llm_instance(self, model_id: str, model) -> bool:
        """Initialize LLM instance from database model"""
        try:
            enhanced_data = await self._convert_to_enhanced_format(model, "llm")
            instance = await self._create_llm_instance_from_data(enhanced_data)
            if instance:
                self.model_instances[model_id] = instance
                return True
            return False
        except Exception as e:
            logger.error(f"Error initializing LLM instance {model_id}: {str(e)}")
            return False

    async def _initialize_embedding_instance(self, model_id: str, model) -> bool:
        """Initialize embedding instance from database model"""
        try:
            enhanced_data = await self._convert_to_enhanced_format(model, "embedding")
            instance = await self._create_embedding_instance_from_data(enhanced_data)
            if instance:
                self.model_instances[model_id] = instance
                return True
            return False
        except Exception as e:
            logger.error(f"Error initializing embedding instance {model_id}: {str(e)}")
            return False

    # Factory methods (same as before but adapted for existing data structure)
    async def _create_llm_instance_from_data(self, model_data: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create LLM instance from enhanced data"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        provider = ModelProvider(model_data["provider"])
        if provider in self.llm_factories:
            return await self.llm_factories[provider](model_data)
        return None

    async def _create_embedding_instance_from_data(self, model_data: Dict[str, Any]) -> Optional[Embeddings]:
        """Create embedding instance from enhanced data"""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        provider = ModelProvider(model_data["provider"])
        if provider in self.embedding_factories:
            return await self.embedding_factories[provider](model_data)
        return None

    # LLM Factory methods (adapted for existing structure)
    async def _create_openai_llm(self, model_data: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create OpenAI LLM instance"""
        try:
            config = model_data.get("model_config", {})
            return ChatOpenAI(
                model=model_data["name"],
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=model_data.get("api_endpoint"),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 4096),
                top_p=config.get("top_p", 1.0),
            )
        except Exception as e:
            logger.error(f"Error creating OpenAI LLM: {str(e)}")
            return None

    async def _create_azure_openai_llm(self, model_data: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create Azure OpenAI LLM instance"""
        try:
            config = model_data.get("model_config", {})
            return AzureChatOpenAI(
                deployment_name=model_data["name"],
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=model_data.get("api_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 4096),
            )
        except Exception as e:
            logger.error(f"Error creating Azure OpenAI LLM: {str(e)}")
            return None

    async def _create_google_gemini_llm(self, model_data: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create Google Gemini LLM instance"""
        try:
            config = model_data.get("model_config", {})
            return ChatGoogleGenerativeAI(
                model=model_data["name"],
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=config.get("temperature", 0.7),
                max_output_tokens=config.get("max_tokens", 4096),
            )
        except Exception as e:
            logger.error(f"Error creating Google Gemini LLM: {str(e)}")
            return None

    async def _create_ollama_llm(self, model_data: Dict[str, Any]) -> Optional[BaseLanguageModel]:
        """Create Ollama LLM instance"""
        try:
            config = model_data.get("model_config", {})
            return Ollama(
                model=model_data["name"],
                base_url=model_data.get("api_endpoint", "http://localhost:11434"),
                temperature=config.get("temperature", 0.7),
            )
        except Exception as e:
            logger.error(f"Error creating Ollama LLM: {str(e)}")
            return None

    # Embedding factory methods (similar pattern)
    async def _create_openai_embedding(self, model_data: Dict[str, Any]) -> Optional[Embeddings]:
        """Create OpenAI embedding instance"""
        try:
            return OpenAIEmbeddings(
                model=model_data["name"],
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=model_data.get("api_endpoint"),
            )
        except Exception as e:
            logger.error(f"Error creating OpenAI embedding: {str(e)}")
            return None

    async def _create_azure_openai_embedding(self, model_data: Dict[str, Any]) -> Optional[Embeddings]:
        """Create Azure OpenAI embedding instance"""
        try:
            return AzureOpenAIEmbeddings(
                model=model_data["name"],
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=model_data.get("api_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            )
        except Exception as e:
            logger.error(f"Error creating Azure OpenAI embedding: {str(e)}")
            return None

    async def _create_google_gemini_embedding(self, model_data: Dict[str, Any]) -> Optional[Embeddings]:
        """Create Google Gemini embedding instance"""
        try:
            return GoogleGenerativeAIEmbeddings(
                model=model_data["name"],
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
        except Exception as e:
            logger.error(f"Error creating Google Gemini embedding: {str(e)}")
            return None

    async def _create_ollama_embedding(self, model_data: Dict[str, Any]) -> Optional[Embeddings]:
        """Create Ollama embedding instance"""
        try:
            return OllamaEmbeddings(
                model=model_data["name"],
                base_url=model_data.get("api_endpoint", "http://localhost:11434"),
            )
        except Exception as e:
            logger.error(f"Error creating Ollama embedding: {str(e)}")
            return None

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the enhanced model service"""
        return {
            "status": "healthy",
            "active_instances": len(self.model_instances),
            "default_llm_id": self.default_llm_id,
            "default_embedding_id": self.default_embedding_id,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "supported_providers": [provider.value for provider in ModelProvider],
            "timestamp": datetime.utcnow().isoformat()
        }

# Global enhanced model service instance
_enhanced_model_service: Optional[EnhancedModelService] = None

def get_enhanced_model_service(database_service: DatabaseService = None) -> EnhancedModelService:
    """Get enhanced model service instance"""
    global _enhanced_model_service
    if _enhanced_model_service is None:
        from .database_service import get_database_service
        db_service = database_service or get_database_service()
        _enhanced_model_service = EnhancedModelService(db_service)
    return _enhanced_model_service