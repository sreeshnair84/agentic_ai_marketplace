"""
Optimized Tool Management API Router
Consolidated from simple_tool_management, tool_management, and enhanced_tool_management
Provides comprehensive async endpoints for managing tool templates and instances
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text, and_, or_
from typing import List, Dict, Any, Optional
import json
import uuid
import logging
from datetime import datetime, timezone

from ..models.database import get_db
from ..models.tool_management import ToolTemplate, ToolInstance, ToolInstanceExecution
from ..schemas.tool_schemas import (
    ToolTemplateCreate, ToolTemplateUpdate, ToolTemplateResponse,
    ToolInstanceCreate, ToolInstanceUpdate, ToolInstanceResponse,
    ToolExecutionRequest, ToolExecutionResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tool-management", tags=["Tool Management"])

# Enhanced execution service
class OptimizedToolExecutionService:
    """Enhanced tool execution service with comprehensive features"""
    
    async def execute(self, instance_id: str, payload: dict, db: AsyncSession):
        """Execute a tool instance with full logging and error handling"""
        try:
            # Get instance
            result = await db.execute(
                select(ToolInstance).where(ToolInstance.id == instance_id)
            )
            instance = result.scalar_one_or_none()
            if not instance:
                raise HTTPException(status_code=404, detail="Instance not found")
            
            # Create execution record
            execution = ToolInstanceExecution(
                id=str(uuid.uuid4()),
                tool_instance_id=instance_id,
                input_data=payload,
                status="running",
                started_at=datetime.now(timezone.utc)
            )
            
            db.add(execution)
            await db.commit()
            
            # Mock execution logic - replace with actual implementation
            result_data = {
                "status": "completed",
                "result": f"Executed {instance.name} with payload: {payload}",
                "execution_time_ms": 150,
                "metadata": {
                    "instance_id": instance_id,
                    "template_type": instance.template.template_type if instance.template else "unknown"
                }
            }
            
            # Update execution record
            await db.execute(
                update(ToolInstanceExecution)
                .where(ToolInstanceExecution.id == execution.id)
                .values(
                    status="completed",
                    output_data=result_data,
                    completed_at=datetime.now(timezone.utc)
                )
            )
            
            await db.commit()
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error executing tool instance {instance_id}: {e}")
            if 'execution' in locals():
                await db.execute(
                    update(ToolInstanceExecution)
                    .where(ToolInstanceExecution.id == execution.id)
                    .values(
                        status="failed",
                        error_message=str(e),
                        completed_at=datetime.now(timezone.utc)
                    )
                )
                await db.commit()
            raise HTTPException(status_code=500, detail=str(e))

execution_service = OptimizedToolExecutionService()

# ============================================================================
# TOOL TEMPLATE ENDPOINTS
# ============================================================================

@router.get("/templates", response_model=List[ToolTemplateResponse])
async def list_tool_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all tool templates with comprehensive filtering"""
    try:
        query = select(ToolTemplate)
        
        # Apply filters
        filters = []
        if template_type:
            filters.append(ToolTemplate.template_type == template_type)
        if category:
            filters.append(ToolTemplate.category == category)
        if is_active is not None:
            filters.append(ToolTemplate.is_active == is_active)
        if search:
            search_filter = or_(
                ToolTemplate.name.ilike(f"%{search}%"),
                ToolTemplate.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(ToolTemplate.created_at.desc())
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        logger.info(f"Retrieved {len(templates)} tool templates")
        return [ToolTemplateResponse.model_validate(t) for t in templates]
        
    except Exception as e:
        logger.error(f"Error listing tool templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", response_model=ToolTemplateResponse)
async def get_tool_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tool template by ID"""
    try:
        result = await db.execute(
            select(ToolTemplate).where(ToolTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        return ToolTemplateResponse.model_validate(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tool template {template_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates", response_model=ToolTemplateResponse)
async def create_tool_template(
    template: ToolTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tool template"""
    try:
        # Check for existing template with same name
        existing = await db.execute(
            select(ToolTemplate).where(ToolTemplate.name == template.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template with this name already exists"
            )
        
        # Create new template
        db_template = ToolTemplate(
            id=str(uuid.uuid4()),
            name=template.name,
            display_name=getattr(template, 'display_name', template.name),
            description=getattr(template, 'description', ''),
            template_type=getattr(template, 'template_type', 'custom'),
            category=getattr(template, 'category', 'general'),
            version=getattr(template, 'version', '1.0.0'),
            default_configuration=getattr(template, 'default_configuration', {}),
            schema_definition=getattr(template, 'schema_definition', {}),
            code_template=getattr(template, 'code_template', None),
            metadata=getattr(template, 'metadata', {}),
            is_active=getattr(template, 'is_active', True),
            tags=getattr(template, 'tags', []),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)
        
        logger.info(f"Created tool template: {db_template.name}")
        return ToolTemplateResponse.model_validate(db_template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tool template: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_id}", response_model=ToolTemplateResponse)
async def update_tool_template(
    template_id: str,
    template_update: ToolTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing tool template"""
    try:
        # Get existing template
        result = await db.execute(
            select(ToolTemplate).where(ToolTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        # Update fields
        update_data = template_update.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.now(timezone.utc)
        
        await db.execute(
            update(ToolTemplate)
            .where(ToolTemplate.id == template_id)
            .values(**update_data)
        )
        
        await db.commit()
        await db.refresh(template)
        
        logger.info(f"Updated tool template: {template.name}")
        return ToolTemplateResponse.model_validate(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool template {template_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_tool_template(
    template_id: str,
    force: bool = Query(False, description="Force delete even if instances exist"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a tool template"""
    try:
        # Check if template exists
        template_result = await db.execute(
            select(ToolTemplate).where(ToolTemplate.id == template_id)
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        # Check for existing instances
        instances_result = await db.execute(
            select(ToolInstance).where(ToolInstance.template_id == template_id)
        )
        instances = instances_result.scalars().all()
        
        if instances and not force:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete template with {len(instances)} active instances. Use force=true to override."
            )
        
        # Delete template (cascade will handle instances if force=true)
        await db.execute(delete(ToolTemplate).where(ToolTemplate.id == template_id))
        await db.commit()
        
        logger.info(f"Deleted tool template: {template.name}")
        return {"message": "Template deleted successfully", "deleted_instances": len(instances) if force else 0}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tool template {template_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOOL INSTANCE ENDPOINTS
# ============================================================================

@router.get("/instances", response_model=List[ToolInstanceResponse])
async def list_tool_instances(
    template_id: Optional[str] = Query(None, description="Filter by template ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """List all tool instances with comprehensive filtering"""
    try:
        query = select(ToolInstance)
        
        # Apply filters
        filters = []
        if template_id:
            filters.append(ToolInstance.template_id == template_id)
        if status:
            filters.append(ToolInstance.status == status)
        if environment:
            filters.append(ToolInstance.environment == environment)
        if search:
            search_filter = or_(
                ToolInstance.name.ilike(f"%{search}%"),
                ToolInstance.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(ToolInstance.created_at.desc())
        
        result = await db.execute(query)
        instances = result.scalars().all()
        
        logger.info(f"Retrieved {len(instances)} tool instances")
        return [ToolInstanceResponse.model_validate(i) for i in instances]
        
    except Exception as e:
        logger.error(f"Error listing tool instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}", response_model=ToolInstanceResponse)
async def get_tool_instance(
    instance_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific tool instance by ID"""
    try:
        result = await db.execute(
            select(ToolInstance).where(ToolInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        return ToolInstanceResponse.model_validate(instance)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tool instance {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances", response_model=ToolInstanceResponse)
async def create_tool_instance(
    instance: ToolInstanceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new tool instance from a template"""
    try:
        # Validate template exists
        template_result = await db.execute(
            select(ToolTemplate).where(ToolTemplate.id == instance.template_id)
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Tool template not found")
        
        if template is not None:
            # Check if template is active using a query
            active_check = await db.execute(
                select(ToolTemplate.is_active).where(ToolTemplate.id == instance.template_id)
            )
            is_active = active_check.scalar_one_or_none()
            if not is_active:
                raise HTTPException(status_code=400, detail="Cannot create instance from inactive template")
        
        # Create new instance
        db_instance = ToolInstance(
            id=str(uuid.uuid4()),
            template_id=instance.template_id,
            name=instance.name,
            description=getattr(instance, 'description', ''),
            configuration=getattr(instance, 'configuration', {}),
            credentials=getattr(instance, 'credentials', {}),
            environment=getattr(instance, 'environment', 'development'),
            status=getattr(instance, 'status', 'inactive'),
            resource_limits=getattr(instance, 'resource_limits', {}),
            health_check_config=getattr(instance, 'health_check_config', {}),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(db_instance)
        await db.commit()
        await db.refresh(db_instance)
        
        logger.info(f"Created tool instance: {db_instance.name}")
        return ToolInstanceResponse.model_validate(db_instance)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tool instance: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/instances/{instance_id}", response_model=ToolInstanceResponse)
async def update_tool_instance(
    instance_id: str,
    instance_update: ToolInstanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing tool instance"""
    try:
        # Get existing instance
        result = await db.execute(
            select(ToolInstance).where(ToolInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        # Update fields
        update_data = instance_update.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.now(timezone.utc)
        
        await db.execute(
            update(ToolInstance)
            .where(ToolInstance.id == instance_id)
            .values(**update_data)
        )
        
        await db.commit()
        await db.refresh(instance)
        
        logger.info(f"Updated tool instance: {instance.name}")
        return ToolInstanceResponse.model_validate(instance)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool instance {instance_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/instances/{instance_id}")
async def delete_tool_instance(
    instance_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a tool instance"""
    try:
        # Check if instance exists
        result = await db.execute(
            select(ToolInstance).where(ToolInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        # Delete instance
        await db.execute(delete(ToolInstance).where(ToolInstance.id == instance_id))
        await db.commit()
        
        logger.info(f"Deleted tool instance: {instance.name}")
        return {"message": "Instance deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tool instance {instance_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# INSTANCE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/instances/{instance_id}/activate")
async def activate_instance(
    instance_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Activate a tool instance"""
    try:
        await db.execute(
            update(ToolInstance)
            .where(ToolInstance.id == instance_id)
            .values(status="active", updated_at=datetime.now(timezone.utc))
        )
        await db.commit()
        
        logger.info(f"Activated tool instance: {instance_id}")
        return {"message": "Instance activated successfully", "status": "active"}
        
    except Exception as e:
        logger.error(f"Error activating instance {instance_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/deactivate")
async def deactivate_instance(
    instance_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a tool instance"""
    try:
        await db.execute(
            update(ToolInstance)
            .where(ToolInstance.id == instance_id)
            .values(status="inactive", updated_at=datetime.now(timezone.utc))
        )
        await db.commit()
        
        logger.info(f"Deactivated tool instance: {instance_id}")
        return {"message": "Instance deactivated successfully", "status": "inactive"}
        
    except Exception as e:
        logger.error(f"Error deactivating instance {instance_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/execute", response_model=ToolExecutionResponse)
async def execute_tool_instance(
    instance_id: str,
    request: ToolExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Execute a tool instance with the provided payload"""
    try:
        # Validate instance exists and is active
        result = await db.execute(
            select(ToolInstance).where(ToolInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        # Check if instance is active
        status_check = await db.execute(
            select(ToolInstance.status).where(ToolInstance.id == instance_id)
        )
        status = status_check.scalar_one_or_none()
        if status != "active":
            raise HTTPException(status_code=400, detail="Instance is not active")
        
        # Execute the instance
        execution_result = await execution_service.execute(
            instance_id, request.execution_parameters, db
        )
        
        return ToolExecutionResponse(**execution_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing tool instance {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}/health")
async def check_instance_health(
    instance_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Check the health status of a tool instance"""
    try:
        result = await db.execute(
            select(ToolInstance).where(ToolInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Tool instance not found")
        
        # Mock health check - replace with actual implementation
        health_status = {
            "instance_id": instance_id,
            "status": instance.status,
            "health_status": instance.health_status or "unknown",
            "last_health_check": instance.last_health_check,
            "uptime": "calculating...",
            "response_time_ms": 42,
            "error_rate": 0.0
        }
        
        # Update health check timestamp
        await db.execute(
            update(ToolInstance)
            .where(ToolInstance.id == instance_id)
            .values(
                last_health_check=datetime.now(timezone.utc),
                health_status="healthy"
            )
        )
        await db.commit()
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking health for instance {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STATISTICS AND MONITORING ENDPOINTS
# ============================================================================

@router.get("/statistics")
async def get_tool_statistics(
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive tool management statistics"""
    try:
        # Get template statistics
        template_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_templates,
                    COUNT(*) FILTER (WHERE is_active = true) as active_templates,
                    COUNT(DISTINCT template_type) as unique_types
                FROM tool_templates
            """)
        )
        template_stats = template_result.fetchone()
        
        # Get instance statistics
        instance_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_instances,
                    COUNT(*) FILTER (WHERE status = 'active') as active_instances,
                    COUNT(*) FILTER (WHERE status = 'inactive') as inactive_instances,
                    COUNT(*) FILTER (WHERE status = 'error') as error_instances,
                    COUNT(DISTINCT environment) as unique_environments
                FROM tool_instances
            """)
        )
        instance_stats = instance_result.fetchone()
        
        # Get execution statistics
        execution_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_executions,
                    COUNT(*) FILTER (WHERE status = 'completed') as successful_executions,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_executions,
                    AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000) as avg_execution_time_ms
                FROM tool_instance_executions
                WHERE started_at > NOW() - INTERVAL '7 days'
            """)
        )
        execution_stats = execution_result.fetchone()
        
        statistics = {
            "templates": {
                "total": template_stats[0] if template_stats else 0,
                "active": template_stats[1] if template_stats else 0,
                "unique_types": template_stats[2] if template_stats else 0
            },
            "instances": {
                "total": instance_stats[0] if instance_stats else 0,
                "active": instance_stats[1] if instance_stats else 0,
                "inactive": instance_stats[2] if instance_stats else 0,
                "error": instance_stats[3] if instance_stats else 0,
                "unique_environments": instance_stats[4] if instance_stats else 0
            },
            "executions_last_7_days": {
                "total": execution_stats[0] if execution_stats else 0,
                "successful": execution_stats[1] if execution_stats else 0,
                "failed": execution_stats[2] if execution_stats else 0,
                "avg_execution_time_ms": float(execution_stats[3]) if execution_stats and execution_stats[3] else 0.0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error getting tool statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for the tool management service"""
    return {
        "status": "healthy",
        "service": "tool_management",
        "version": "1.0.0",
        "features": {
            "templates": True,
            "instances": True,
            "execution": True,
            "monitoring": True,
            "statistics": True,
            "health_checks": True
        },
        "endpoints": {
            "templates": "/tool-management/templates",
            "instances": "/tool-management/instances",
            "statistics": "/tool-management/statistics",
            "health": "/tool-management/health"
        }
    }
