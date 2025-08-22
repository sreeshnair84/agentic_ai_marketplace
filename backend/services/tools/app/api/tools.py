"""
API endpoints for Tools service
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
import logging
import time
from datetime import datetime

from ..services.tool_executor import ToolExecutor, ToolExecutionResult
from ..services.tool_registry import get_tool_registry
from ..services.database_service import get_database_service, DatabaseService
from ..services.enhanced_model_service import get_enhanced_model_service, EnhancedModelService
from ..services.enhanced_chat_service import get_enhanced_chat_service, EnhancedChatService
from ..core.config import get_settings
from ..models.execution_models import (
    ToolExecutionRequest, 
    BatchToolExecutionRequest, 
    MCPToolExecutionRequest,
    ToolExecutionResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/", response_model=List[Dict[str, Any]])
async def list_tools(
    category: Optional[str] = None,
    project_tags: Optional[List[str]] = Query(None, description="Filter tools by project tags"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """List all available tools with optional project-based filtering"""
    
    try:
        # Get tools from registry (for runtime tools)
        executor = ToolExecutor()
        runtime_tools = executor.get_available_tools(category)
        
        # Get tool templates from database with project filtering
        db_tools = await db_service.get_tool_templates(project_tags=project_tags, category=category)
        
        # Combine and return both runtime and database tools
        all_tools = runtime_tools + [tool.dict() for tool in db_tools]
        
        return all_tools
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_tool_templates(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    db_service: DatabaseService = Depends(get_database_service)
):
    """List tool templates with project-based filtering"""
    
    try:
        templates = await db_service.get_tool_templates(
            project_tags=project_tags,
            category=category,
            is_active=is_active
        )
        
        return [template.dict() for template in templates]
        
    except Exception as e:
        logger.error(f"Error listing tool templates: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tool templates: {str(e)}"
        )


@router.get("/instances", response_model=List[Dict[str, Any]])
async def list_tool_instances(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    template_id: Optional[str] = None,
    status: Optional[str] = None,
    db_service: DatabaseService = Depends(get_database_service)
):
    """List tool instances with project-based filtering"""
    
    try:
        instances = await db_service.get_tool_instances(
            project_tags=project_tags,
            template_id=template_id,
            status=status
        )
        
        return [instance.dict() for instance in instances]
        
    except Exception as e:
        logger.error(f"Error listing tool instances: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tool instances: {str(e)}"
        )


@router.get("/llm-models", response_model=List[Dict[str, Any]])
async def list_llm_models(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """List LLM models with enhanced LangGraph support"""
    
    try:
        models = await enhanced_service.list_llm_models(
            provider=provider,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return models
        
    except Exception as e:
        logger.error(f"Error listing LLM models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list LLM models: {str(e)}"
        )


@router.get("/embedding-models", response_model=List[Dict[str, Any]])
async def list_embedding_models(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """List embedding models with enhanced LangGraph support"""
    
    try:
        models = await enhanced_service.list_embedding_models(
            provider=provider,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return models
        
    except Exception as e:
        logger.error(f"Error listing embedding models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list embedding models: {str(e)}"
        )


@router.get("/categories", response_model=List[str])
async def list_categories():
    """List all tool categories"""
    
    try:
        registry = get_tool_registry()
        categories = registry.get_categories()
        
        return categories
        
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list categories: {str(e)}"
        )


@router.get("/{tool_name}/schema", response_model=Dict[str, Any])
async def get_tool_schema(tool_name: str):
    """Get schema for a specific tool"""
    
    try:
        registry = get_tool_registry()
        schema = registry.get_tool_schema(tool_name)
        
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )
        
        return schema
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool schema: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tool schema: {str(e)}"
        )


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool with given parameters"""
    
    try:
        executor = ToolExecutor()
        result = await executor.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            user_permissions=request.user_permissions or [],
            timeout=request.timeout
        )
        
        return ToolExecutionResponse(
            success=result.success,
            result=result.result,
            error=result.error,
            execution_time=result.execution_time,
            tool_name=request.tool_name
        )
        
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return ToolExecutionResponse(
            success=False,
            result=None,
            error=str(e),
            execution_time=None,
            tool_name=request.tool_name
        )


@router.post("/execute/batch", response_model=List[ToolExecutionResponse])
async def batch_execute_tools(request: BatchToolExecutionRequest):
    """Execute multiple tools concurrently"""
    
    try:
        executor = ToolExecutor()
        results = await executor.batch_execute(
            tool_requests=request.tool_requests,
            user_permissions=request.user_permissions,
            max_concurrent=request.max_concurrent
        )
        
        return [
            ToolExecutionResponse(
                success=result.success,
                result=result.result,
                error=result.error,
                execution_time=result.execution_time,
                tool_name=getattr(result, 'tool_name', None)
            )
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error in batch execution: {e}")
        # Return error response for batch execution
        return [
            ToolExecutionResponse(
                success=False,
                result=None,
                error=str(e),
                execution_time=None,
                tool_name=None
            )
        ]


@router.get("/mcp", response_model=List[Dict[str, Any]])
async def list_mcp_tools(server_url: Optional[str] = None):
    """List available MCP tools"""
    
    try:
        executor = ToolExecutor()
        tools = await executor.get_mcp_tools(server_url)
        
        return tools
        
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list MCP tools: {str(e)}"
        )


@router.post("/mcp/execute", response_model=ToolExecutionResponse)
async def execute_mcp_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    server_name: Optional[str] = None
):
    """Execute an MCP tool"""
    
    try:
        executor = ToolExecutor()
        result = await executor.execute_mcp_tool(
            tool_name=tool_name,
            parameters=parameters,
            server_name=server_name
        )
        
        return ToolExecutionResponse(
            success=result.success,
            result=result.result,
            error=result.error,
            execution_time=result.execution_time,
            tool_name=tool_name
        )
        
    except Exception as e:
        logger.error(f"Error executing MCP tool: {e}")
        return ToolExecutionResponse(
            success=False,
            result=None,
            error=str(e),
            execution_time=None,
            tool_name=tool_name
        )


@router.post("/create/llm-model", response_model=Dict[str, Any])
async def create_llm_model(
    model_data: Dict[str, Any],
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Create a new LLM model with enhanced LangGraph support"""
    
    try:
        result = await enhanced_service.create_llm_model(model_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create LLM model")
            )
        
        return {
            "success": True,
            "message": "LLM model created successfully",
            "model_id": result.get("id"),
            "model": result.get("model"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating LLM model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create LLM model: {str(e)}"
        )


@router.post("/create/tool-instance", response_model=Dict[str, Any])
async def create_tool_instance(
    instance_data: Dict[str, Any],
    db_service: DatabaseService = Depends(get_database_service)
):
    """Create a new tool instance (demo endpoint)"""
    
    try:
        # For now, just return success with the provided data
        # In a real implementation, this would validate and save to database
        instance_id = f"tool-{instance_data.get('name', 'unnamed')}-{int(time.time())}"
        
        return {
            "success": True,
            "message": "Tool instance created successfully",
            "instance_id": instance_id,
            "instance_data": instance_data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error creating tool instance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create tool instance: {str(e)}"
        )


@router.put("/edit/llm-model/{model_id}", response_model=Dict[str, Any])
async def edit_llm_model(
    model_id: str,
    model_data: Dict[str, Any],
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Edit an existing LLM model with enhanced LangGraph support"""
    
    try:
        result = await enhanced_service.update_model(model_id, "llm", model_data)
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to update LLM model")
            if "not found" in error_message.lower():
                raise HTTPException(status_code=404, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)
        
        return {
            "success": True,
            "message": f"LLM model {model_id} updated successfully",
            "model_id": model_id,
            "model": result.get("model"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing LLM model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit LLM model: {str(e)}"
        )


@router.put("/edit/tool-instance/{instance_id}", response_model=Dict[str, Any])
async def edit_tool_instance(
    instance_id: str,
    instance_data: Dict[str, Any],
    db_service: DatabaseService = Depends(get_database_service)
):
    """Edit an existing tool instance (demo endpoint)"""
    
    try:
        # For now, just return success with the provided data
        # In a real implementation, this would validate and update in database
        
        return {
            "success": True,
            "message": f"Tool instance {instance_id} updated successfully",
            "instance_id": instance_id,
            "updated_data": instance_data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error editing tool instance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit tool instance: {str(e)}"
        )


# ============================================================================
# ENHANCED LANGGRAPH MODEL ENDPOINTS
# ============================================================================

@router.get("/llm-models/{model_id}", response_model=Dict[str, Any])
async def get_llm_model(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Get a specific LLM model with enhanced details"""
    
    try:
        model = await enhanced_service.get_model(model_id, "llm")
        if not model:
            raise HTTPException(status_code=404, detail=f"LLM model {model_id} not found")
        
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LLM model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get LLM model: {str(e)}"
        )


@router.get("/embedding-models/{model_id}", response_model=Dict[str, Any])
async def get_embedding_model(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Get a specific embedding model with enhanced details"""
    
    try:
        model = await enhanced_service.get_model(model_id, "embedding")
        if not model:
            raise HTTPException(status_code=404, detail=f"Embedding model {model_id} not found")
        
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting embedding model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get embedding model: {str(e)}"
        )


@router.post("/create/embedding-model", response_model=Dict[str, Any])
async def create_embedding_model(
    model_data: Dict[str, Any],
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Create a new embedding model with enhanced LangGraph support"""
    
    try:
        result = await enhanced_service.create_embedding_model(model_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create embedding model")
            )
        
        return {
            "success": True,
            "message": "Embedding model created successfully",
            "model_id": result.get("id"),
            "model": result.get("model"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating embedding model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create embedding model: {str(e)}"
        )


@router.put("/edit/embedding-model/{model_id}", response_model=Dict[str, Any])
async def edit_embedding_model(
    model_id: str,
    model_data: Dict[str, Any],
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Edit an existing embedding model with enhanced LangGraph support"""
    
    try:
        result = await enhanced_service.update_model(model_id, "embedding", model_data)
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to update embedding model")
            if "not found" in error_message.lower():
                raise HTTPException(status_code=404, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)
        
        return {
            "success": True,
            "message": f"Embedding model {model_id} updated successfully",
            "model_id": model_id,
            "model": result.get("model"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing embedding model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit embedding model: {str(e)}"
        )


@router.post("/llm-models/{model_id}/test", response_model=Dict[str, Any])
async def test_llm_model(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Test an LLM model's connectivity and functionality"""
    
    try:
        result = await enhanced_service.test_model(model_id, "llm")
        
        return {
            "success": result.get("success", False),
            "response": result.get("response"),
            "status": result.get("status", "unknown"),
            "error": result.get("error"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing LLM model: {e}")
        return {
            "success": False,
            "response": None,
            "status": "error",
            "error": f"Failed to test model: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/embedding-models/{model_id}/test", response_model=Dict[str, Any])
async def test_embedding_model(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Test an embedding model's connectivity and functionality"""
    
    try:
        result = await enhanced_service.test_model(model_id, "embedding")
        
        return {
            "success": result.get("success", False),
            "dimensions": result.get("dimensions"),
            "status": result.get("status", "unknown"),
            "error": result.get("error"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error testing embedding model: {e}")
        return {
            "success": False,
            "dimensions": None,
            "status": "error",
            "error": f"Failed to test model: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/llm-models/{model_id}/set-default", response_model=Dict[str, Any])
async def set_default_llm(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Set an LLM model as the default"""
    
    try:
        result = await enhanced_service.set_default_model(model_id, "llm")
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to set default LLM")
            if "not found" in error_message.lower():
                raise HTTPException(status_code=404, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)
        
        return {
            "success": True,
            "message": f"Set model {model_id} as default LLM",
            "default_llm_id": result.get("default_llm_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting default LLM: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set default LLM: {str(e)}"
        )


@router.post("/embedding-models/{model_id}/set-default", response_model=Dict[str, Any])
async def set_default_embedding(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Set an embedding model as the default"""
    
    try:
        result = await enhanced_service.set_default_model(model_id, "embedding")
        
        if not result.get("success"):
            error_message = result.get("error", "Failed to set default embedding model")
            if "not found" in error_message.lower():
                raise HTTPException(status_code=404, detail=error_message)
            else:
                raise HTTPException(status_code=400, detail=error_message)
        
        return {
            "success": True,
            "message": f"Set model {model_id} as default embedding model",
            "default_embedding_id": result.get("default_embedding_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting default embedding model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set default embedding model: {str(e)}"
        )


@router.delete("/llm-models/{model_id}", response_model=Dict[str, Any])
async def delete_llm_model(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Delete an LLM model"""
    
    try:
        result = await enhanced_service.delete_model(model_id, "llm")
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to delete LLM model")
            )
        
        return {
            "success": True,
            "message": "LLM model deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting LLM model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete LLM model: {str(e)}"
        )


@router.delete("/embedding-models/{model_id}", response_model=Dict[str, Any])
async def delete_embedding_model(
    model_id: str,
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Delete an embedding model"""
    
    try:
        result = await enhanced_service.delete_model(model_id, "embedding")
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to delete embedding model")
            )
        
        return {
            "success": True,
            "message": "Embedding model deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting embedding model: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete embedding model: {str(e)}"
        )


@router.get("/models/providers", response_model=Dict[str, Any])
async def get_supported_providers():
    """Get list of supported model providers"""
    
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "type": "both",
                "description": "OpenAI language and embedding models"
            },
            {
                "id": "azure_openai",
                "name": "Azure OpenAI",
                "type": "both",
                "description": "Azure-hosted OpenAI models"
            },
            {
                "id": "google_gemini",
                "name": "Google Gemini",
                "type": "both",
                "description": "Google Gemini models"
            },
            {
                "id": "ollama",
                "name": "Ollama",
                "type": "both",
                "description": "Local Ollama models"
            }
        ]
    }


@router.get("/models/defaults", response_model=Dict[str, Any])
async def get_default_models(
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Get current default models"""
    
    try:
        default_llm = await enhanced_service.get_default_model("llm")
        default_embedding = await enhanced_service.get_default_model("embedding")
        
        return {
            "default_llm": default_llm,
            "default_embedding": default_embedding,
            "has_default_llm": default_llm is not None,
            "has_default_embedding": default_embedding is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting default models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get default models: {str(e)}"
        )


@router.get("/models/health", response_model=Dict[str, Any])
async def get_model_service_health(
    enhanced_service: EnhancedModelService = Depends(get_enhanced_model_service)
):
    """Get health status of the model service"""
    
    try:
        return enhanced_service.get_health_status()
        
    except Exception as e:
        logger.error(f"Error getting model service health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model service health: {str(e)}"
        )


# ============================================================================
# ENHANCED CHAT ENDPOINTS
# ============================================================================

@router.post("/chat", response_model=Dict[str, Any])
async def enhanced_chat(
    message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None,
    model_id: Optional[str] = None,
    stream: bool = False,
    chat_service: EnhancedChatService = Depends(get_enhanced_chat_service)
):
    """Enhanced chat with LangGraph model support"""
    
    try:
        if stream:
            raise HTTPException(
                status_code=400,
                detail="Use /chat/stream endpoint for streaming responses"
            )
        
        response = await chat_service.chat(
            message=message,
            conversation_history=conversation_history or [],
            session_id=session_id,
            model_id=model_id,
            stream=False
        )
        
        if not response.get("success"):
            raise HTTPException(
                status_code=400,
                detail=response.get("error", "Chat request failed")
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )


@router.post("/chat/stream")
async def enhanced_chat_stream(
    message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None,
    model_id: Optional[str] = None,
    chat_service: EnhancedChatService = Depends(get_enhanced_chat_service)
):
    """Enhanced streaming chat with LangGraph model support"""
    
    from fastapi.responses import StreamingResponse
    import json
    
    try:
        async def generate_stream():
            try:
                async for chunk in chat_service.chat(
                    message=message,
                    conversation_history=conversation_history or [],
                    session_id=session_id,
                    model_id=model_id,
                    stream=True
                ):
                    # Format as Server-Sent Events
                    data = json.dumps(chunk)
                    yield f"data: {data}\n\n"
                
                # Send final event to close stream
                yield f"data: {json.dumps({'final': True, 'success': True})}\n\n"
                
            except Exception as e:
                error_data = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "final": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        logger.error(f"Streaming chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Streaming chat error: {str(e)}"
        )


@router.post("/chat/summary", response_model=Dict[str, Any])
async def get_conversation_summary(
    conversation_history: List[Dict[str, Any]],
    max_length: int = 200,
    chat_service: EnhancedChatService = Depends(get_enhanced_chat_service)
):
    """Generate a summary of the conversation"""
    
    try:
        summary = await chat_service.get_conversation_summary(
            conversation_history=conversation_history,
            max_length=max_length
        )
        
        if summary is None:
            return {
                "success": False,
                "error": "Could not generate summary - no default model configured",
                "summary": None
            }
        
        return {
            "success": True,
            "summary": summary,
            "message_count": len(conversation_history),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/chat/health", response_model=Dict[str, Any])
async def get_chat_health(
    chat_service: EnhancedChatService = Depends(get_enhanced_chat_service)
):
    """Get health status of the enhanced chat service"""
    
    try:
        return chat_service.get_health_status()
        
    except Exception as e:
        logger.error(f"Error getting chat health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get chat health: {str(e)}"
        )
