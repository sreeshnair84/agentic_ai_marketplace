"""
Tool Management API Router
Provides endpoints for managing tool templates, instances, and execution
Integrates with the LangGraph framework for workflow orchestration
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import logging

from ..models.database import get_db
from ..models.tool_management import (
    ToolTemplate, ToolInstance, ToolInstanceExecution, ExecutionMetrics
)
from ..schemas.tool_management import (
    ToolTemplateCreate, ToolTemplateUpdate, ToolTemplateResponse,
    ToolInstanceCreate, ToolInstanceUpdate, ToolInstanceResponse,
    ToolExecutionCreate, ToolExecutionResponse,
    ToolTemplateType, ToolInstanceStatus, ToolExecutionStatus,
    ExecutionMetricsResponse, ConfigurationValidationResponse
)
from ..services.langgraph_tool_manager import LangGraphToolManager

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Tool Management"])

# Initialize LangGraph tool manager
tool_manager = LangGraphToolManager()

# ============================================================================
# TOOL TEMPLATE ENDPOINTS
# ============================================================================

@router.post("/templates", response_model=ToolTemplateResponse)
async def create_tool_template(
    template: ToolTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tool template
    """
    try:
        # Validate configuration based on template type
        validation_result = await validate_tool_configuration(
            template.template_type, template.default_configuration
        )
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid configuration: {', '.join(validation_result.errors)}"
            )
        
        # Create template
        db_template = ToolTemplate(
            id=str(uuid.uuid4()),
            name=template.name,
            description=template.description,
            template_type=template.template_type,
            version=template.version,
            default_configuration=template.default_configuration,
            schema_definition=template.schema_definition,
            code_template=template.code_template,
            metadata=template.metadata or {},
            is_active=template.is_active,
            created_by="system",  # TODO: Get from auth context
            created_at=datetime.utcnow()
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        logger.info(f"Created tool template: {db_template.name} ({db_template.id})")
        return db_template
        
    except Exception as e:
        logger.error(f"Error creating tool template: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=List[ToolTemplateResponse])
async def list_tool_templates(
    template_type: Optional[ToolTemplateType] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List tool templates with optional filtering
    """
    try:
        query = db.query(ToolTemplate)
        
        if template_type:
            query = query.filter(ToolTemplate.template_type == template_type)
        if is_active is not None:
            query = query.filter(ToolTemplate.is_active == is_active)
            
        templates = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(templates)} tool templates")
        return templates
        
    except Exception as e:
        logger.error(f"Error listing tool templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", response_model=ToolTemplateResponse)
async def get_tool_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tool template by ID
    """
    try:
        template = db.query(ToolTemplate).filter(ToolTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
            
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tool template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_id}", response_model=ToolTemplateResponse)
async def update_tool_template(
    template_id: str,
    template_update: ToolTemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a tool template
    """
    try:
        db_template = db.query(ToolTemplate).filter(ToolTemplate.id == template_id).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        # Update fields
        update_data = template_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
        
        db_template.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_template)
        
        logger.info(f"Updated tool template: {template_id}")
        return db_template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool template {template_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_tool_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a tool template
    """
    try:
        template = db.query(ToolTemplate).filter(ToolTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        # Check if template has active instances
        active_instances = db.query(ToolInstance).filter(
            ToolInstance.template_id == template_id,
            ToolInstance.status.in_([ToolInstanceStatus.ACTIVE, ToolInstanceStatus.RUNNING])
        ).count()
        
        if active_instances > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete template with {active_instances} active instances"
            )
        
        db.delete(template)
        db.commit()
        
        logger.info(f"Deleted tool template: {template_id}")
        return {"message": "Tool template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tool template {template_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOOL INSTANCE ENDPOINTS
# ============================================================================

@router.post("/instances", response_model=ToolInstanceResponse)
async def create_tool_instance(
    instance: ToolInstanceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new tool instance from a template
    """
    try:
        # Validate template exists
        template = db.query(ToolTemplate).filter(ToolTemplate.id == instance.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        if not template.is_active:
            raise HTTPException(status_code=400, detail="Cannot create instance from inactive template")
        
        # Merge configurations
        merged_config = {**template.default_configuration}
        if instance.configuration:
            merged_config.update(instance.configuration)
        
        # Validate merged configuration
        validation_result = await validate_tool_configuration(
            template.template_type, merged_config
        )
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid configuration: {', '.join(validation_result.errors)}"
            )
        
        # Create instance
        db_instance = ToolInstance(
            id=str(uuid.uuid4()),
            template_id=instance.template_id,
            name=instance.name,
            description=instance.description,
            configuration=merged_config,
            runtime_config=instance.runtime_config or {},
            status=ToolInstanceStatus.INACTIVE,
            metadata=instance.metadata or {},
            created_by="system",  # TODO: Get from auth context
            created_at=datetime.utcnow()
        )
        
        db.add(db_instance)
        db.commit()
        db.refresh(db_instance)
        
        logger.info(f"Created tool instance: {db_instance.name} ({db_instance.id})")
        return db_instance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tool instance: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances", response_model=List[ToolInstanceResponse])
async def list_tool_instances(
    template_id: Optional[str] = None,
    status: Optional[ToolInstanceStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List tool instances with optional filtering
    """
    try:
        query = db.query(ToolInstance)
        
        if template_id:
            query = query.filter(ToolInstance.template_id == template_id)
        if status:
            query = query.filter(ToolInstance.status == status)
            
        instances = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(instances)} tool instances")
        return instances
        
    except Exception as e:
        logger.error(f"Error listing tool instances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}", response_model=ToolInstanceResponse)
async def get_tool_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tool instance by ID
    """
    try:
        instance = db.query(ToolInstance).filter(ToolInstance.id == instance_id).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
            
        return instance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tool instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/activate")
async def activate_tool_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """
    Activate a tool instance
    """
    try:
        instance = db.query(ToolInstance).filter(ToolInstance.id == instance_id).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        # Activate using LangGraph tool manager
        success = await tool_manager.activate_tool_instance(instance)
        
        if success:
            instance.status = ToolInstanceStatus.ACTIVE
            instance.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Activated tool instance: {instance_id}")
            return {"message": "Tool instance activated successfully", "status": "active"}
        else:
            raise HTTPException(status_code=500, detail="Failed to activate tool instance")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating tool instance {instance_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/deactivate")
async def deactivate_tool_instance(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """
    Deactivate a tool instance
    """
    try:
        instance = db.query(ToolInstance).filter(ToolInstance.id == instance_id).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        # Deactivate using LangGraph tool manager
        success = await tool_manager.deactivate_tool_instance(instance)
        
        if success:
            instance.status = ToolInstanceStatus.INACTIVE
            instance.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Deactivated tool instance: {instance_id}")
            return {"message": "Tool instance deactivated successfully", "status": "inactive"}
        else:
            raise HTTPException(status_code=500, detail="Failed to deactivate tool instance")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating tool instance {instance_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOOL EXECUTION ENDPOINTS
# ============================================================================

@router.post("/instances/{instance_id}/execute", response_model=ToolExecutionResponse)
async def execute_tool_instance(
    instance_id: str,
    execution_request: ToolExecutionCreate,
    db: Session = Depends(get_db)
):
    """
    Execute a tool instance with provided parameters
    """
    try:
        instance = db.query(ToolInstance).filter(ToolInstance.id == instance_id).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        if instance.status != ToolInstanceStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Tool instance is not active")
        
        # Create execution record
        execution = ToolExecution(
            id=str(uuid.uuid4()),
            instance_id=instance_id,
            execution_parameters=execution_request.execution_parameters,
            status=ToolExecutionStatus.RUNNING,
            created_at=datetime.utcnow()
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # Execute using LangGraph tool manager
        try:
            result = await tool_manager.execute_tool_instance(
                instance, execution_request.execution_parameters
            )
            
            # Update execution with results
            execution.status = ToolExecutionStatus.COMPLETED
            execution.result = result
            execution.completed_at = datetime.utcnow()
            
            # Update metrics
            execution_time = (execution.completed_at - execution.created_at).total_seconds()
            await update_execution_metrics(instance_id, True, execution_time, db)
            
        except Exception as exec_error:
            execution.status = ToolExecutionStatus.FAILED
            execution.error_message = str(exec_error)
            execution.completed_at = datetime.utcnow()
            
            # Update metrics
            execution_time = (execution.completed_at - execution.created_at).total_seconds()
            await update_execution_metrics(instance_id, False, execution_time, db)
            
            logger.error(f"Tool execution failed: {str(exec_error)}")
        
        db.commit()
        db.refresh(execution)
        
        return execution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing tool instance {instance_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}/executions", response_model=List[ToolExecutionResponse])
async def list_tool_executions(
    instance_id: str,
    status: Optional[ToolExecutionStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List executions for a tool instance
    """
    try:
        query = db.query(ToolExecution).filter(ToolExecution.instance_id == instance_id)
        
        if status:
            query = query.filter(ToolExecution.status == status)
            
        executions = query.order_by(ToolExecution.created_at.desc()).offset(skip).limit(limit).all()
        
        return executions
        
    except Exception as e:
        logger.error(f"Error listing executions for instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}", response_model=ToolExecutionResponse)
async def get_tool_execution(
    execution_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific tool execution by ID
    """
    try:
        execution = db.query(ToolExecution).filter(ToolExecution.id == execution_id).first()
        if not execution:
            raise HTTPException(status_code=404, detail="Tool execution not found")
            
        return execution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving execution {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# METRICS AND MONITORING ENDPOINTS
# ============================================================================

@router.get("/instances/{instance_id}/metrics", response_model=ExecutionMetricsResponse)
async def get_tool_instance_metrics(
    instance_id: str,
    db: Session = Depends(get_db)
):
    """
    Get execution metrics for a tool instance
    """
    try:
        metrics = db.query(ExecutionMetrics).filter(
            ExecutionMetrics.instance_id == instance_id
        ).first()
        
        if not metrics:
            # Return default metrics if none exist
            return ExecutionMetricsResponse(
                instance_id=instance_id,
                total_executions=0,
                successful_executions=0,
                failed_executions=0,
                average_execution_time=0.0,
                last_execution_at=None
            )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving metrics for instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

@router.post("/validate-configuration", response_model=ConfigurationValidationResponse)
async def validate_tool_configuration(
    template_type: ToolTemplateType,
    configuration: Dict[str, Any]
):
    """
    Validate a tool configuration against its template type
    """
    try:
        validation_result = await tool_manager.validate_configuration(template_type, configuration)
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def update_execution_metrics(
    instance_id: str, 
    success: bool, 
    execution_time: float, 
    db: Session
):
    """
    Update execution metrics for a tool instance
    """
    try:
        metrics = db.query(ExecutionMetrics).filter(
            ExecutionMetrics.instance_id == instance_id
        ).first()
        
        if not metrics:
            metrics = ExecutionMetrics(
                instance_id=instance_id,
                total_executions=0,
                successful_executions=0,
                failed_executions=0,
                average_execution_time=0.0
            )
            db.add(metrics)
        
        # Update counters
        metrics.total_executions += 1
        if success:
            metrics.successful_executions += 1
        else:
            metrics.failed_executions += 1
        
        # Update average execution time
        if metrics.total_executions == 1:
            metrics.average_execution_time = execution_time
        else:
            metrics.average_execution_time = (
                (metrics.average_execution_time * (metrics.total_executions - 1) + execution_time) / 
                metrics.total_executions
            )
        
        metrics.last_execution_at = datetime.utcnow()
        metrics.updated_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error updating execution metrics: {str(e)}")
        db.rollback()

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for tool management service
    """
    return {
        "status": "healthy",
        "service": "tool-management",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "tool_templates": True,
            "tool_instances": True,
            "tool_execution": True,
            "langgraph_integration": True,
            "metrics_tracking": True
        }
    }
