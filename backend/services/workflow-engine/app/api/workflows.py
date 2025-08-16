"""
API endpoints for Workflow Engine with project-based filtering
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi import status as http_status
from typing import Dict, Any, List, Optional
import logging

from ..services.database_service import get_database_service, DatabaseService
from ..models.workflows import (
    WorkflowDefinitionResponse, WorkflowExecutionResponse, 
    WorkflowTemplateResponse, WorkflowScheduleResponse,
    WorkflowSummary, ExecutionSummary
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=List[Dict[str, Any]])
async def list_workflows(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    category: Optional[str] = None,
    status: Optional[str] = None,
    is_template: Optional[bool] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db_service: DatabaseService = Depends(get_database_service)
):
    """List workflow definitions with project-based filtering"""
    
    try:
        workflows = await db_service.get_workflows(
            project_tags=project_tags,
            category=category,
            status=status,
            is_template=is_template,
            limit=limit,
            offset=offset
        )
        
        return [workflow.dict() for workflow in workflows]
        
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(
    workflow_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Get workflow definition by ID"""
    
    try:
        workflow = await db_service.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{workflow_id}' not found"
            )
        
        return workflow.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}"
        )


@router.get("/executions/", response_model=List[Dict[str, Any]])
async def list_executions(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db_service: DatabaseService = Depends(get_database_service)
):
    """List workflow executions with project-based filtering"""
    
    try:
        executions = await db_service.get_executions(
            project_tags=project_tags,
            workflow_id=workflow_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return [execution.dict() for execution in executions]
        
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}"
        )


@router.get("/executions/{execution_id}", response_model=Dict[str, Any])
async def get_execution(
    execution_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Get workflow execution by ID"""
    
    try:
        execution = await db_service.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution '{execution_id}' not found"
            )
        
        return execution.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}"
        )


@router.get("/templates/", response_model=List[Dict[str, Any]])
async def list_templates(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    category: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db_service: DatabaseService = Depends(get_database_service)
):
    """List workflow templates with project-based filtering"""
    
    try:
        templates = await db_service.get_templates(
            project_tags=project_tags,
            category=category,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        return [template.dict() for template in templates]
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_template(
    template_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Get workflow template by ID"""
    
    try:
        template = await db_service.get_template(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_id}' not found"
            )
        
        return template.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.get("/schedules/", response_model=List[Dict[str, Any]])
async def list_schedules(
    project_tags: Optional[List[str]] = Query(None, description="Filter by project tags"),
    workflow_id: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db_service: DatabaseService = Depends(get_database_service)
):
    """List workflow schedules with project-based filtering"""
    
    try:
        schedules = await db_service.get_schedules(
            project_tags=project_tags,
            workflow_id=workflow_id,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        return [schedule.dict() for schedule in schedules]
        
    except Exception as e:
        logger.error(f"Error listing schedules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schedules: {str(e)}"
        )


@router.get("/schedules/{schedule_id}", response_model=Dict[str, Any])
async def get_schedule(
    schedule_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Get workflow schedule by ID"""
    
    try:
        schedule = await db_service.get_schedule(schedule_id)
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule '{schedule_id}' not found"
            )
        
        return schedule.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schedule: {str(e)}"
        )


# Enhanced Registry Endpoints
@router.get("/registry/cards/{workflow_id}")
async def get_workflow_card(
    workflow_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Get enhanced workflow card with complete registry information"""
    
    try:
        workflow = await db_service.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{workflow_id}' not found"
            )
        
        # Convert to enhanced registry format
        workflow_card = {
            "id": str(workflow.id),
            "name": workflow.name,
            "display_name": workflow.display_name,
            "description": workflow.description,
            "category": workflow.category,
            "version": workflow.version,
            
            # Service Discovery
            "execution_url": getattr(workflow, 'execution_url', f"http://localhost:8007/workflows/{workflow.id}/execute"),
            "dns_name": getattr(workflow, 'dns_name', "workflow-engine.lcnc.local"),
            "status_url": getattr(workflow, 'status_url', f"http://localhost:8007/workflows/{workflow.id}/status"),
            
            # Enhanced metadata
            "input_signature": getattr(workflow, 'input_signature', None),
            "output_signature": getattr(workflow, 'output_signature', None),
            "triggers": getattr(workflow, 'triggers', []),
            "dependencies": getattr(workflow, 'dependencies', None),
            
            # Standard fields
            "steps": [step.dict() if hasattr(step, 'dict') else step for step in workflow.steps],
            "tags": workflow.tags,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "author": getattr(workflow, 'author', None),
            "organization": getattr(workflow, 'organization', "LCNC Platform"),
            "environment": getattr(workflow, 'environment', "development")
        }
        
        return workflow_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow card: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow card: {str(e)}"
        )


@router.get("/registry/search")
async def search_workflows(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    capabilities: Optional[List[str]] = Query(None, description="Filter by capabilities"),
    max_results: int = Query(10, le=50, description="Maximum results to return"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Search workflows using natural language and filters"""
    
    try:
        # Basic search implementation - can be enhanced with vector search
        workflows = await db_service.get_workflows(
            category=category,
            limit=max_results * 2  # Get more to filter
        )
        
        # Filter by query (simple text matching for now)
        matching_workflows = []
        for workflow in workflows:
            workflow_text = f"{workflow.name} {workflow.description} {' '.join(workflow.tags or [])}"
            if query.lower() in workflow_text.lower():
                matching_workflows.append({
                    "id": str(workflow.id),
                    "name": workflow.name,
                    "display_name": workflow.display_name,
                    "description": workflow.description,
                    "category": workflow.category,
                    "tags": workflow.tags,
                    "relevance_score": 0.8  # Placeholder scoring
                })
        
        return {
            "query": query,
            "total_results": len(matching_workflows),
            "workflows": matching_workflows[:max_results]
        }
        
    except Exception as e:
        logger.error(f"Error searching workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search workflows: {str(e)}"
        )
