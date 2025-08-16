"""
API endpoints for Tools service
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
import logging
import time

from ..services.tool_executor import ToolExecutor, ToolExecutionResult
from ..services.tool_registry import get_tool_registry
from ..services.database_service import get_database_service, DatabaseService
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
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    provider: Optional[str] = None,
    is_active: Optional[bool] = True,
    db_service: DatabaseService = Depends(get_database_service)
):
    """List LLM models with project-based filtering"""
    
    try:
        models = await db_service.get_llm_models(
            project_tags=project_tags,
            provider=provider,
            is_active=is_active
        )
        
        return [model.dict() for model in models]
        
    except Exception as e:
        logger.error(f"Error listing LLM models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list LLM models: {str(e)}"
        )


@router.get("/embedding-models", response_model=List[Dict[str, Any]])
async def list_embedding_models(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    provider: Optional[str] = None,
    is_active: Optional[bool] = True,
    db_service: DatabaseService = Depends(get_database_service)
):
    """List embedding models with project-based filtering"""
    
    try:
        models = await db_service.get_embedding_models(
            project_tags=project_tags,
            provider=provider,
            is_active=is_active
        )
        
        return [model.dict() for model in models]
        
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
    db_service: DatabaseService = Depends(get_database_service)
):
    """Create a new LLM model (demo endpoint)"""
    
    try:
        # For now, just return success with the provided data
        # In a real implementation, this would validate and save to database
        model_id = f"llm-{model_data.get('name', 'unnamed')}-{int(time.time())}"
        
        return {
            "success": True,
            "message": "LLM model created successfully",
            "model_id": model_id,
            "model_data": model_data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
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
    db_service: DatabaseService = Depends(get_database_service)
):
    """Edit an existing LLM model (demo endpoint)"""
    
    try:
        # For now, just return success with the provided data
        # In a real implementation, this would validate and update in database
        
        return {
            "success": True,
            "message": f"LLM model {model_id} updated successfully",
            "model_id": model_id,
            "updated_data": model_data,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
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
