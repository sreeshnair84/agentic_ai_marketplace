"""
Enhanced Tools API with Template and Configuration Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from ..models.tools import (
    ToolTemplateResponse as ToolTemplate,
    ToolTemplateCreate,
    ToolTemplateUpdate,
    ToolTemplateResponse,
    ToolTemplateFieldCreate,
    ToolInstanceResponse as ToolInstance,
    ToolInstanceCreate,
    ToolInstanceUpdate,
    ToolInstanceResponse,
    LLMModelResponse as LLMModel,
    EmbeddingModelResponse as EmbeddingModel
)
from ..database import get_db
from ..auth import get_current_user
from sqlalchemy.orm import Session
from .tools import router as existing_router

# Create new router for enhanced functionality
enhanced_router = APIRouter(prefix="/api/tools", tags=["enhanced-tools"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Tool Templates Endpoints

@enhanced_router.get("/templates", response_model=List[ToolTemplateResponse])
async def get_tool_templates(
    category: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all tool templates with optional filtering"""
    try:
        query = db.query(ToolTemplate).filter(ToolTemplate.is_active == True)
        
        if category and category != "all":
            query = query.filter(ToolTemplate.category == category)
        
        if type and type != "all":
            query = query.filter(ToolTemplate.type == type)
        
        if search:
            query = query.filter(
                ToolTemplate.name.ilike(f"%{search}%") |
                ToolTemplate.display_name.ilike(f"%{search}%") |
                ToolTemplate.description.ilike(f"%{search}%")
            )
        
        templates = query.order_by(ToolTemplate.display_name).all()
        
        # Load fields for each template
        for template in templates:
            fields = db.query(ToolTemplateField).filter(
                ToolTemplateField.tool_template_id == template.id
            ).order_by(ToolTemplateField.field_order).all()
            template.fields = fields
            
        return templates
    
    except Exception as e:
        logger.error(f"Error fetching tool templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tool templates"
        )

@enhanced_router.get("/templates/{template_id}", response_model=ToolTemplateResponse)
async def get_tool_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific tool template with its fields"""
    try:
        template = db.query(ToolTemplate).filter(
            ToolTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool template not found"
            )
        
        # Load template fields
        fields = db.query(ToolTemplateField).filter(
            ToolTemplateField.tool_template_id == template_id
        ).order_by(ToolTemplateField.field_order).all()
        
        template.fields = fields
        return template
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tool template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tool template"
        )

@enhanced_router.post("/templates", response_model=ToolTemplateResponse)
async def create_tool_template(
    template: ToolTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new tool template"""
    try:
        # Check if template name already exists
        existing = db.query(ToolTemplate).filter(
            ToolTemplate.name == template.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool template with this name already exists"
            )
        
        template_data = template.dict(exclude={"fields"})
        db_template = ToolTemplate(
            **template_data,
            created_by=current_user.get("email")
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        # Add template fields if provided
        if hasattr(template, 'fields') and template.fields:
            for field_data in template.fields:
                field = ToolTemplateField(
                    tool_template_id=db_template.id,
                    **field_data.dict()
                )
                db.add(field)
            
            db.commit()
        
        logger.info(f"Created tool template: {template.name}")
        return db_template
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tool template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tool template"
        )

# Tool Instances Endpoints

@enhanced_router.get("/instances", response_model=List[ToolInstanceResponse])
async def get_tool_instances(
    template_id: Optional[UUID] = None,
    status: Optional[str] = None,
    environment_scope: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all tool instances with optional filtering"""
    try:
        query = db.query(ToolInstance)
        
        if template_id:
            query = query.filter(ToolInstance.tool_template_id == template_id)
        
        if status and status != "all":
            query = query.filter(ToolInstance.status == status)
        
        if environment_scope and environment_scope != "all":
            query = query.filter(ToolInstance.environment_scope == environment_scope)
        
        if search:
            query = query.filter(
                ToolInstance.name.ilike(f"%{search}%") |
                ToolInstance.display_name.ilike(f"%{search}%") |
                ToolInstance.description.ilike(f"%{search}%")
            )
        
        instances = query.order_by(ToolInstance.display_name).all()
        
        # Add template information to each instance
        for instance in instances:
            template = db.query(ToolTemplate).filter(
                ToolTemplate.id == instance.tool_template_id
            ).first()
            if template:
                instance.template = template
                
        return instances
    
    except Exception as e:
        logger.error(f"Error fetching tool instances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tool instances"
        )

@enhanced_router.post("/instances", response_model=ToolInstanceResponse)
async def create_tool_instance(
    instance: ToolInstanceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new tool instance"""
    try:
        # Verify template exists
        template = db.query(ToolTemplate).filter(
            ToolTemplate.id == instance.tool_template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool template not found"
            )
        
        # Check if instance name already exists
        existing = db.query(ToolInstance).filter(
            ToolInstance.name == instance.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool instance with this name already exists"
            )
        
        db_instance = ToolInstance(
            **instance.dict(),
            created_by=current_user.get("email"),
            updated_by=current_user.get("email")
        )
        
        db.add(db_instance)
        db.commit()
        db.refresh(db_instance)
        
        logger.info(f"Created tool instance: {instance.name}")
        return db_instance
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tool instance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tool instance"
        )

# LLM and Embedding Models Endpoints

@enhanced_router.get("/llm-models", response_model=List[Dict[str, Any]])
async def get_llm_models(
    provider: Optional[str] = None,
    model_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all available LLM models"""
    try:
        query = db.query(LLMModel).filter(LLMModel.is_active == True)
        
        if provider and provider != "all":
            query = query.filter(LLMModel.provider == provider)
        
        if model_type and model_type != "all":
            query = query.filter(LLMModel.model_type == model_type)
        
        models = query.order_by(LLMModel.display_name).all()
        return [
            {
                "id": str(model.id),
                "name": model.name,
                "display_name": model.display_name,
                "provider": model.provider,
                "model_type": model.model_type,
                "max_tokens": model.max_tokens,
                "supports_streaming": model.supports_streaming,
                "supports_functions": model.supports_functions
            }
            for model in models
        ]
    
    except Exception as e:
        logger.error(f"Error fetching LLM models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch LLM models"
        )

@enhanced_router.get("/embedding-models", response_model=List[Dict[str, Any]])
async def get_embedding_models(
    provider: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all available embedding models"""
    try:
        query = db.query(EmbeddingModel).filter(EmbeddingModel.is_active == True)
        
        if provider and provider != "all":
            query = query.filter(EmbeddingModel.provider == provider)
        
        models = query.order_by(EmbeddingModel.display_name).all()
        return [
            {
                "id": str(model.id),
                "name": model.name,
                "display_name": model.display_name,
                "provider": model.provider,
                "dimensions": model.dimensions,
                "max_input_tokens": model.max_input_tokens
            }
            for model in models
        ]
    
    except Exception as e:
        logger.error(f"Error fetching embedding models: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch embedding models"
        )

@enhanced_router.get("/template-categories")
async def get_tool_template_categories():
    """Get all available tool template categories"""
    return {
        "categories": [
            {"value": "mcp", "label": "MCP Tools", "description": "Model Context Protocol tools"},
            {"value": "custom", "label": "Custom Tools", "description": "Custom developed tools"},
            {"value": "api", "label": "API Tools", "description": "External API integrations"},
            {"value": "llm", "label": "LLM Tools", "description": "Language model tools"},
            {"value": "rag", "label": "RAG Tools", "description": "Retrieval Augmented Generation tools"},
            {"value": "workflow", "label": "Workflow Tools", "description": "Workflow automation tools"}
        ]
    }

@enhanced_router.get("/field-types")
async def get_field_types():
    """Get all available field types for tool templates"""
    return {
        "field_types": [
            {"value": "text", "label": "Text", "description": "Single line text input"},
            {"value": "textarea", "label": "Text Area", "description": "Multi-line text input"},
            {"value": "number", "label": "Number", "description": "Numeric input"},
            {"value": "boolean", "label": "Boolean", "description": "True/false checkbox"},
            {"value": "select", "label": "Select", "description": "Single choice dropdown"},
            {"value": "multiselect", "label": "Multi-Select", "description": "Multiple choice selection"},
            {"value": "url", "label": "URL", "description": "URL input with validation"},
            {"value": "email", "label": "Email", "description": "Email input with validation"},
            {"value": "password", "label": "Password", "description": "Password input (hidden)"},
            {"value": "json", "label": "JSON", "description": "JSON object input"}
        ]
    }

@enhanced_router.post("/instances/{instance_id}/execute")
async def execute_tool_instance(
    instance_id: UUID,
    input_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Execute a tool instance with given input data"""
    try:
        instance = db.query(ToolInstance).filter(
            ToolInstance.id == instance_id
        ).first()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool instance not found"
            )
        
        if instance.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tool instance is not active"
            )
        
        # Get the template to understand the tool type
        template = db.query(ToolTemplate).filter(
            ToolTemplate.id == instance.tool_template_id
        ).first()
        
        # Here you would implement the actual tool execution logic based on template type
        # For now, this is a placeholder that returns configuration and input
        
        execution_result = {
            "instance_id": str(instance_id),
            "tool_name": instance.name,
            "template_type": template.type if template else "unknown",
            "configuration": instance.configuration,
            "input_data": input_data,
            "status": "executed",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Tool execution completed successfully"
        }
        
        # If it's a RAG tool, demonstrate using embedding model from configuration
        if template and template.type == "rag_processor":
            embedding_model_id = instance.configuration.get("embedding_model")
            if embedding_model_id:
                embedding_model = db.query(EmbeddingModel).filter(
                    EmbeddingModel.id == embedding_model_id
                ).first()
                if embedding_model:
                    execution_result["embedding_model_used"] = {
                        "name": embedding_model.name,
                        "display_name": embedding_model.display_name,
                        "provider": embedding_model.provider,
                        "dimensions": embedding_model.dimensions
                    }
        
        return execution_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing tool instance {instance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute tool instance"
        )

# Combine existing and enhanced routers
def get_combined_router():
    """Combine existing tools router with enhanced functionality"""
    combined = APIRouter()
    combined.include_router(existing_router)
    combined.include_router(enhanced_router)
    return combined
