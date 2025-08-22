"""
Embedding Models API
REST endpoints for managing embedding model configurations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...services.langgraph_model_service import (
    LangGraphModelService, 
    ModelProvider, 
    ModelType, 
    ModelStatus,
    EmbeddingModelConfig,
    ModelCapabilities,
    PricingInfo,
    PerformanceMetrics
)
from ...core.dependencies import get_current_user
from ...core.database import get_db_session

router = APIRouter(prefix="/embedding-models", tags=["Embedding Models"])

class CreateEmbeddingModelRequest(BaseModel):
    """Request model for creating embedding models"""
    name: str = Field(..., description="Model name (e.g., 'text-embedding-ada-002')")
    display_name: str = Field(..., description="Human-readable display name")
    provider: ModelProvider = Field(..., description="Model provider")
    api_endpoint: Optional[str] = Field(None, description="Custom API endpoint")
    api_key: Optional[str] = Field(None, description="API key for the model")
    status: ModelStatus = Field(ModelStatus.INACTIVE, description="Model status")
    capabilities: Optional[ModelCapabilities] = Field(None, description="Model capabilities")
    pricing_info: Optional[PricingInfo] = Field(None, description="Pricing information")
    performance_metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    model_config: Optional[EmbeddingModelConfig] = Field(None, description="Model configuration")
    health_url: Optional[str] = Field(None, description="Health check URL")
    dns_name: Optional[str] = Field(None, description="DNS name for the model service")

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('display_name')
    def validate_display_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Display name cannot be empty')
        return v.strip()

class UpdateEmbeddingModelRequest(BaseModel):
    """Request model for updating embedding models"""
    name: Optional[str] = Field(None, description="Model name")
    display_name: Optional[str] = Field(None, description="Display name")
    api_endpoint: Optional[str] = Field(None, description="API endpoint")
    api_key: Optional[str] = Field(None, description="API key")
    status: Optional[ModelStatus] = Field(None, description="Model status")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="Model capabilities")
    pricing_info: Optional[Dict[str, Any]] = Field(None, description="Pricing information")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    model_config: Optional[Dict[str, Any]] = Field(None, description="Model configuration")
    health_url: Optional[str] = Field(None, description="Health check URL")
    dns_name: Optional[str] = Field(None, description="DNS name")

class EmbeddingModelResponse(BaseModel):
    """Response model for embedding models"""
    id: str
    name: str
    display_name: str
    provider: str
    model_type: str
    api_endpoint: Optional[str]
    status: str
    capabilities: Dict[str, Any]
    pricing_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    model_config: Dict[str, Any]
    health_url: Optional[str]
    dns_name: Optional[str]
    created_at: datetime
    updated_at: datetime

class TestEmbeddingModelResponse(BaseModel):
    """Response model for embedding model testing"""
    success: bool
    dimensions: Optional[int]
    status: str
    error: Optional[str]

async def get_model_service(db_session=Depends(get_db_session)) -> LangGraphModelService:
    """Dependency to get the model service"""
    return LangGraphModelService(db_session)

@router.get("/", response_model=List[EmbeddingModelResponse])
async def list_embedding_models(
    provider: Optional[ModelProvider] = Query(None, description="Filter by provider"),
    status: Optional[ModelStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of models to return"),
    offset: int = Query(0, ge=0, description="Number of models to skip"),
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """List all embedding models with filtering options"""
    try:
        models = await model_service.list_models(
            model_type=ModelType.EMBEDDING,
            provider=provider,
            status=status,
            limit=limit,
            offset=offset
        )
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list embedding models: {str(e)}"
        )

@router.get("/{model_id}", response_model=EmbeddingModelResponse)
async def get_embedding_model(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Get a specific embedding model by ID"""
    try:
        model = await model_service.get_model(model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Embedding model {model_id} not found"
            )
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get embedding model: {str(e)}"
        )

@router.post("/", response_model=Dict[str, Any])
async def create_embedding_model(
    model_data: CreateEmbeddingModelRequest,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Create a new embedding model configuration"""
    try:
        # Convert Pydantic model to dict
        model_dict = model_data.dict(exclude_unset=True)
        
        # Set model type
        model_dict["model_type"] = ModelType.EMBEDDING.value
        
        result = await model_service.create_embedding_model(model_dict)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create embedding model")
            )
        
        return {
            "success": True,
            "message": "Embedding model created successfully",
            "id": result.get("id"),
            "model": result.get("model")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding model: {str(e)}"
        )

@router.put("/{model_id}", response_model=Dict[str, Any])
async def update_embedding_model(
    model_id: str,
    model_data: UpdateEmbeddingModelRequest,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Update an existing embedding model configuration"""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = model_data.dict(exclude_unset=True, exclude_none=True)
        
        result = await model_service.update_model(model_id, update_dict)
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to update embedding model")
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
        
        return {
            "success": True,
            "message": "Embedding model updated successfully",
            "model": result.get("model")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embedding model: {str(e)}"
        )

@router.delete("/{model_id}")
async def delete_embedding_model(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Delete an embedding model configuration"""
    try:
        # Check if model exists first
        existing_model = await model_service.get_model(model_id)
        if not existing_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Embedding model {model_id} not found"
            )
        
        result = await model_service.delete_model(model_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to delete embedding model")
            )
        
        return {
            "success": True,
            "message": "Embedding model deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete embedding model: {str(e)}"
        )

@router.post("/{model_id}/test", response_model=TestEmbeddingModelResponse)
async def test_embedding_model(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Test an embedding model's connectivity and functionality"""
    try:
        result = await model_service.test_model(model_id)
        
        return TestEmbeddingModelResponse(
            success=result.get("success", False),
            dimensions=result.get("dimensions"),
            status=result.get("status", "unknown"),
            error=result.get("error")
        )
    except Exception as e:
        return TestEmbeddingModelResponse(
            success=False,
            dimensions=None,
            status="error",
            error=f"Failed to test model: {str(e)}"
        )

@router.post("/{model_id}/set-default")
async def set_default_embedding(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Set an embedding model as the default"""
    try:
        result = await model_service.set_default_embedding(model_id)
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to set default embedding model")
            if "not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
        
        return {
            "success": True,
            "message": f"Set model {model_id} as default embedding model",
            "default_embedding_id": result.get("default_embedding_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default embedding model: {str(e)}"
        )

@router.get("/providers/supported")
async def get_supported_embedding_providers(
    current_user = Depends(get_current_user)
):
    """Get list of supported embedding providers"""
    return {
        "providers": [
            {
                "id": provider.value,
                "name": provider.value.replace("_", " ").title(),
                "type": "embedding",
                "description": f"{provider.value.replace('_', ' ').title()} embedding provider"
            }
            for provider in ModelProvider
        ]
    }

@router.get("/templates/configuration")
async def get_embedding_configuration_templates(
    provider: Optional[ModelProvider] = Query(None, description="Filter templates by provider"),
    current_user = Depends(get_current_user)
):
    """Get configuration templates for different embedding providers"""
    templates = {
        "openai": {
            "name": "text-embedding-ada-002",
            "display_name": "OpenAI Ada v2",
            "provider": "openai",
            "capabilities": {
                "dimensions": 1536,
                "max_input_tokens": 8191,
                "supports_batching": True,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt"]
            },
            "model_config": {
                "dimensions": 1536,
                "batch_size": 512,
                "normalize": True
            },
            "pricing_info": {
                "cost_per_token": 0.0000001,
                "currency": "USD"
            }
        },
        "azure_openai": {
            "name": "text-embedding-ada-002",
            "display_name": "Azure OpenAI Ada v2",
            "provider": "azure_openai",
            "api_endpoint": "https://your-resource.openai.azure.com/",
            "capabilities": {
                "dimensions": 1536,
                "max_input_tokens": 8191,
                "supports_batching": True,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt"]
            },
            "model_config": {
                "dimensions": 1536,
                "batch_size": 512,
                "normalize": True
            }
        },
        "google_gemini": {
            "name": "models/embedding-001",
            "display_name": "Gemini Embedding",
            "provider": "google_gemini",
            "capabilities": {
                "dimensions": 768,
                "max_input_tokens": 2048,
                "supports_batching": True,
                "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"]
            },
            "model_config": {
                "dimensions": 768,
                "batch_size": 100,
                "normalize": True
            },
            "pricing_info": {
                "cost_per_token": 0.0000001,
                "currency": "USD"
            }
        },
        "ollama": {
            "name": "nomic-embed-text",
            "display_name": "Nomic Embed Text",
            "provider": "ollama",
            "api_endpoint": "http://localhost:11434",
            "capabilities": {
                "dimensions": 768,
                "max_input_tokens": 2048,
                "supports_batching": False,
                "supported_languages": ["en"]
            },
            "model_config": {
                "dimensions": 768,
                "batch_size": 1,
                "normalize": True
            },
            "pricing_info": {
                "cost_per_token": 0.0,
                "currency": "USD"
            }
        }
    }
    
    if provider:
        template = templates.get(provider.value)
        if template:
            return {"template": template}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No template found for provider {provider.value}"
            )
    
    return {"templates": templates}