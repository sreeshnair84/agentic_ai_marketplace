"""
LLM Models API
REST endpoints for managing LLM model configurations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from pydantic import Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from ...services.langgraph_model_service import (
    LangGraphModelService, 
    ModelProvider, 
    ModelType, 
    ModelStatus,
    LLMModelConfig,
    ModelCapabilities,
    PricingInfo,
    PerformanceMetrics
)
from ...core.dependencies import get_current_user
from ...core.database import get_database

router = APIRouter(prefix="/llm-models", tags=["LLM Models"])

class CreateLLMModelRequest(BaseModel):
    """Request model for creating LLM models"""
    name: str = Field(..., description="Model name (e.g., 'gpt-4', 'gemini-pro')")
    display_name: str = Field(..., description="Human-readable display name")
    provider: ModelProvider = Field(..., description="Model provider")
    api_endpoint: Optional[str] = Field(None, description="Custom API endpoint")
    api_key: Optional[str] = Field(None, description="API key for the model")
    status: ModelStatus = Field(ModelStatus.INACTIVE, description="Model status")
    capabilities: Optional[ModelCapabilities] = Field(None, description="Model capabilities")
    pricing_info: Optional[PricingInfo] = Field(None, description="Pricing information")
    performance_metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    config: Optional[LLMModelConfig] = Field(None, description="Model configuration")
    health_url: Optional[str] = Field(None, description="Health check URL")
    dns_name: Optional[str] = Field(None, description="DNS name for the model service")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('display_name')
    @classmethod
    def validate_display_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Display name cannot be empty')
        return v.strip()

class UpdateLLMModelRequest(BaseModel):
    """Request model for updating LLM models"""
    name: Optional[str] = Field(None, description="Model name")
    display_name: Optional[str] = Field(None, description="Display name")
    api_endpoint: Optional[str] = Field(None, description="API endpoint")
    api_key: Optional[str] = Field(None, description="API key")
    status: Optional[ModelStatus] = Field(None, description="Model status")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="Model capabilities")
    pricing_info: Optional[Dict[str, Any]] = Field(None, description="Pricing information")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    config: Optional[Dict[str, Any]] = Field(None, description="Model configuration")
    health_url: Optional[str] = Field(None, description="Health check URL")
    dns_name: Optional[str] = Field(None, description="DNS name")

class LLMModelResponse(BaseModel):
    """Response model for LLM models"""
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
    config: Dict[str, Any]
    health_url: Optional[str]
    dns_name: Optional[str]
    created_at: datetime
    updated_at: datetime

class TestModelResponse(BaseModel):
    """Response model for model testing"""
    success: bool
    response: Optional[str]
    status: str
    error: Optional[str]

async def get_model_service(db_session=Depends(get_database)) -> LangGraphModelService:
    """Dependency to get the model service"""
    return LangGraphModelService(db_session)

@router.get("/", response_model=List[LLMModelResponse])
async def list_llm_models(
    provider: Optional[ModelProvider] = Query(None, description="Filter by provider"),
    status: Optional[ModelStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of models to return"),
    offset: int = Query(0, ge=0, description="Number of models to skip"),
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """List all LLM models with filtering options"""
    try:
        models = await model_service.list_models(
            model_type=ModelType.LLM,
            provider=provider,
            status=status,
            limit=limit,
            offset=offset
        )
        return models
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list LLM models: {str(e)}"
        )

@router.get("/{model_id}", response_model=LLMModelResponse)
async def get_llm_model(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Get a specific LLM model by ID"""
    try:
        model = await model_service.get_model(model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LLM model {model_id} not found"
            )
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get LLM model: {str(e)}"
        )

@router.post("/", response_model=Dict[str, Any])
async def create_llm_model(
    model_data: CreateLLMModelRequest,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Create a new LLM model configuration"""
    try:
        # Convert Pydantic model to dict
        model_dict = model_data.model_dump(exclude_unset=True)
        
        # Map config field to model_config for backend compatibility
        if "config" in model_dict:
            model_dict["model_config"] = model_dict.pop("config")
        
        # Set model type
        model_dict["model_type"] = ModelType.LLM.value
        
        result = await model_service.create_llm_model(model_dict)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create LLM model")
            )
        
        return {
            "success": True,
            "message": "LLM model created successfully",
            "id": result.get("id"),
            "model": result.get("model")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create LLM model: {str(e)}"
        )

@router.put("/{model_id}", response_model=Dict[str, Any])
async def update_llm_model(
    model_id: str,
    model_data: UpdateLLMModelRequest,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Update an existing LLM model configuration"""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = model_data.model_dump(exclude_unset=True, exclude_none=True)
        
        # Map config field to model_config for backend compatibility
        if "config" in update_dict:
            update_dict["model_config"] = update_dict.pop("config")
        
        result = await model_service.update_model(model_id, update_dict)
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to update LLM model")
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
            "message": "LLM model updated successfully",
            "model": result.get("model")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update LLM model: {str(e)}"
        )

@router.delete("/{model_id}")
async def delete_llm_model(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Delete an LLM model configuration"""
    try:
        # Check if model exists first
        existing_model = await model_service.get_model(model_id)
        if not existing_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LLM model {model_id} not found"
            )
        
        result = await model_service.delete_model(model_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to delete LLM model")
            )
        
        return {
            "success": True,
            "message": "LLM model deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete LLM model: {str(e)}"
        )

@router.post("/{model_id}/test", response_model=TestModelResponse)
async def test_llm_model(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Test an LLM model's connectivity and functionality"""
    try:
        result = await model_service.test_model(model_id)
        
        return TestModelResponse(
            success=result.get("success", False),
            response=result.get("response"),
            status=result.get("status", "unknown"),
            error=result.get("error")
        )
    except Exception as e:
        return TestModelResponse(
            success=False,
            response=None,
            status="error",
            error=f"Failed to test model: {str(e)}"
        )

@router.post("/{model_id}/set-default")
async def set_default_llm(
    model_id: str,
    model_service: LangGraphModelService = Depends(get_model_service),
    current_user = Depends(get_current_user)
):
    """Set an LLM model as the default"""
    try:
        result = await model_service.set_default_llm(model_id)
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to set default LLM")
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
            "message": f"Set model {model_id} as default LLM",
            "default_llm_id": result.get("default_llm_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set default LLM: {str(e)}"
        )

@router.get("/providers/supported")
async def get_supported_providers(
    current_user = Depends(get_current_user)
):
    """Get list of supported LLM providers"""
    return {
        "providers": [
            {
                "id": provider.value,
                "name": provider.value.replace("_", " ").title(),
                "type": "llm",
                "description": f"{provider.value.replace('_', ' ').title()} language model provider"
            }
            for provider in ModelProvider
        ]
    }

@router.get("/templates/configuration")
async def get_configuration_templates(
    provider: Optional[ModelProvider] = Query(None, description="Filter templates by provider"),
    current_user = Depends(get_current_user)
):
    """Get configuration templates for different providers"""
    templates = {
        "openai": {
            "name": "gpt-4",
            "display_name": "GPT-4",
            "provider": "openai",
            "capabilities": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "supports_function_calling": True,
                "input_modalities": ["text"],
                "output_modalities": ["text"]
            },
            "model_config": {
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop_sequences": []
            },
            "pricing_info": {
                "input_cost_per_token": 0.00003,
                "output_cost_per_token": 0.00006,
                "currency": "USD"
            }
        },
        "azure_openai": {
            "name": "gpt-4",
            "display_name": "Azure GPT-4",
            "provider": "azure_openai",
            "api_endpoint": "https://your-resource.openai.azure.com/",
            "capabilities": {
                "max_tokens": 8192,
                "supports_streaming": True,
                "supports_function_calling": True,
                "input_modalities": ["text"],
                "output_modalities": ["text"]
            },
            "model_config": {
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        },
        "google_gemini": {
            "name": "gemini-pro",
            "display_name": "Gemini Pro",
            "provider": "google_gemini",
            "capabilities": {
                "max_tokens": 30720,
                "supports_streaming": True,
                "supports_function_calling": False,
                "input_modalities": ["text", "image"],
                "output_modalities": ["text"]
            },
            "model_config": {
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0
            },
            "pricing_info": {
                "input_cost_per_token": 0.000125,
                "output_cost_per_token": 0.000375,
                "currency": "USD"
            }
        },
        "ollama": {
            "name": "llama2",
            "display_name": "Llama 2",
            "provider": "ollama",
            "api_endpoint": "http://localhost:11434",
            "capabilities": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_function_calling": False,
                "input_modalities": ["text"],
                "output_modalities": ["text"]
            },
            "model_config": {
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1.0
            },
            "pricing_info": {
                "input_cost_per_token": 0.0,
                "output_cost_per_token": 0.0,
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