"""
Workflow management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...core.database import get_db, Workflow, WorkflowExecution
from ...services.workflow_service import WorkflowService, workflow_service

router = APIRouter()


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any]


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    definition: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_active: bool


class WorkflowExecutionCreate(BaseModel):
    input_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    created_by: str


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = "system"  # TODO: Get from auth
):
    """Create a new workflow"""
    
    return await workflow_service.create_workflow(
        db=db,
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        created_by=current_user
    )


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List workflows"""
    
    query = select(Workflow).offset(skip).limit(limit)
    
    if is_active is not None:
        query = query.where(Workflow.is_active == is_active)
    
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return [
        WorkflowResponse(
            id=w.id,
            name=w.name,
            description=w.description,
            definition=w.definition,
            status=w.status,
            created_at=w.created_at,
            updated_at=w.updated_at,
            created_by=w.created_by,
            is_active=w.is_active
        )
        for w in workflows
    ]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow"""
    
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        status=workflow.status,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        created_by=workflow.created_by,
        is_active=workflow.is_active
    )


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a workflow"""
    
    # Check if workflow exists
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Update fields
    update_data = workflow_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        await db.execute(
            update(Workflow)
            .where(Workflow.id == workflow_id)
            .values(**update_data)
        )
        await db.commit()
        
        # Refresh workflow
        await db.refresh(workflow)
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        definition=workflow.definition,
        status=workflow.status,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        created_by=workflow.created_by,
        is_active=workflow.is_active
    )


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a workflow (soft delete)"""
    
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id)
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Soft delete
    await db.execute(
        update(Workflow)
        .where(Workflow.id == workflow_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    
    return {"message": "Workflow deleted successfully"}


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    execution_data: WorkflowExecutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = "system"  # TODO: Get from auth
):
    """Execute a workflow"""
    
    return await workflow_service.execute_workflow(
        db=db,
        workflow_id=workflow_id,
        input_data=execution_data.input_data,
        created_by=current_user
    )


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List executions for a workflow"""
    
    result = await db.execute(
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .offset(skip)
        .limit(limit)
        .order_by(WorkflowExecution.created_at.desc())
    )
    executions = result.scalars().all()
    
    return [
        WorkflowExecutionResponse(
            id=e.id,
            workflow_id=e.workflow_id,
            status=e.status,
            input_data=e.input_data,
            output_data=e.output_data,
            error_message=e.error_message,
            started_at=e.started_at,
            completed_at=e.completed_at,
            created_at=e.created_at,
            created_by=e.created_by
        )
        for e in executions
    ]


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow execution"""
    
    result = await db.execute(
        select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found"
        )
    
    return WorkflowExecutionResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        status=execution.status,
        input_data=execution.input_data,
        output_data=execution.output_data,
        error_message=execution.error_message,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        created_at=execution.created_at,
        created_by=execution.created_by
    )
