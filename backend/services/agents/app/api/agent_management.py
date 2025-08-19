"""
Agent Template and Instance management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.models.database import get_db
from ..models.agent_management import (
    AgentTemplate, AgentInstance, ToolTemplateAgentTemplateAssociation,
    AgentInstanceConversation
)
from ..schemas.agent_management import (
    AgentTemplateCreate, AgentTemplateUpdate, AgentTemplateResponse,
    AgentInstanceCreate, AgentInstanceUpdate, AgentInstanceResponse,
    ToolAssociationCreate, ToolAssociationResponse,
    ConversationCreate, ConversationResponse
)
from app.core.auth import get_current_user
from ..services.langgraph_agent_manager import LangGraphAgentManager

router = APIRouter(prefix="/templates", tags=["agent-templates"])

# Initialize agent manager
agent_manager = LangGraphAgentManager()

# Agent Templates Endpoints

@router.get("/", response_model=List[AgentTemplateResponse])
async def list_agent_templates(
    skip: int = 0,
    limit: int = 100,
    framework: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all agent templates with optional filtering"""
    query = select(AgentTemplate)
    
    # Apply filters
    filters = []
    if framework:
        filters.append(AgentTemplate.framework == framework)
    if is_active is not None:
        filters.append(AgentTemplate.is_active == is_active)
    if search:
        filters.append(
            or_(
                AgentTemplate.name.ilike(f"%{search}%"),
                AgentTemplate.description.ilike(f"%{search}%")
            )
        )
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit).order_by(AgentTemplate.created_at.desc())
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return templates

@router.post("/", response_model=AgentTemplateResponse)
async def create_agent_template(
    template_data: AgentTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new agent template"""
    # Check for unique name
    existing = await db.execute(
        select(AgentTemplate).where(AgentTemplate.name == template_data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Template name already exists")
    
    # Create template
    template = AgentTemplate(
        **template_data.dict(),
        created_by=current_user.id if hasattr(current_user, 'id') else None
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template

@router.get("/{template_id}", response_model=AgentTemplateResponse)
async def get_agent_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific agent template"""
    template = await db.execute(
        select(AgentTemplate)
        .options(selectinload(AgentTemplate.tool_associations))
        .where(AgentTemplate.id == template_id)
    )
    template = template.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

@router.put("/{template_id}", response_model=AgentTemplateResponse)
async def update_agent_template(
    template_id: uuid.UUID,
    template_data: AgentTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an agent template"""
    template = await db.execute(
        select(AgentTemplate).where(AgentTemplate.id == template_id)
    )
    template = template.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template

@router.delete("/{template_id}")
async def delete_agent_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an agent template"""
    template = await db.execute(
        select(AgentTemplate).where(AgentTemplate.id == template_id)
    )
    template = template.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if template has active instances
    instances = await db.execute(
        select(AgentInstance).where(
            and_(
                AgentInstance.template_id == template_id,
                AgentInstance.status == "active"
            )
        )
    )
    if instances.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete template with active instances"
        )
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted successfully"}

# Tool Associations for Agent Templates

@router.get("/{template_id}/tools", response_model=List[ToolAssociationResponse])
async def list_template_tools(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List tool associations for an agent template"""
    associations = await db.execute(
        select(ToolTemplateAgentTemplateAssociation)
        .where(ToolTemplateAgentTemplateAssociation.agent_template_id == template_id)
        .order_by(ToolTemplateAgentTemplateAssociation.execution_order)
    )
    
    return associations.scalars().all()

@router.post("/{template_id}/tools", response_model=ToolAssociationResponse)
async def associate_tool_with_template(
    template_id: uuid.UUID,
    association_data: ToolAssociationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Associate a tool template with an agent template"""
    # Verify template exists
    template = await db.execute(
        select(AgentTemplate).where(AgentTemplate.id == template_id)
    )
    if not template.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent template not found")
    
    # Check for unique role name per agent
    existing = await db.execute(
        select(ToolTemplateAgentTemplateAssociation).where(
            and_(
                ToolTemplateAgentTemplateAssociation.agent_template_id == template_id,
                ToolTemplateAgentTemplateAssociation.role_name == association_data.role_name
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Role name already exists for this template")
    
    # Create association
    association = ToolTemplateAgentTemplateAssociation(
        **association_data.dict(),
        agent_template_id=template_id
    )
    
    db.add(association)
    await db.commit()
    await db.refresh(association)
    
    return association

@router.delete("/{template_id}/tools/{association_id}")
async def remove_tool_association(
    template_id: uuid.UUID,
    association_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a tool association from an agent template"""
    association = await db.execute(
        select(ToolTemplateAgentTemplateAssociation).where(
            and_(
                ToolTemplateAgentTemplateAssociation.id == association_id,
                ToolTemplateAgentTemplateAssociation.agent_template_id == template_id
            )
        )
    )
    association = association.scalar_one_or_none()
    
    if not association:
        raise HTTPException(status_code=404, detail="Tool association not found")
    
    await db.delete(association)
    await db.commit()
    
    return {"message": "Tool association removed successfully"}

# Agent Instances Router
instances_router = APIRouter(prefix="/instances", tags=["agent-instances"])

@instances_router.get("/", response_model=List[AgentInstanceResponse])
async def list_agent_instances(
    skip: int = 0,
    limit: int = 100,
    template_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    environment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all agent instances with optional filtering"""
    query = select(AgentInstance).options(selectinload(AgentInstance.template))
    
    # Apply filters
    filters = []
    if template_id:
        filters.append(AgentInstance.template_id == template_id)
    if status:
        filters.append(AgentInstance.status == status)
    if environment:
        filters.append(AgentInstance.environment == environment)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit).order_by(AgentInstance.created_at.desc())
    
    result = await db.execute(query)
    instances = result.scalars().all()
    
    return instances

@instances_router.post("/", response_model=AgentInstanceResponse)
async def create_agent_instance(
    instance_data: AgentInstanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new agent instance"""
    # Validate template exists
    template = await db.execute(
        select(AgentTemplate).where(AgentTemplate.id == instance_data.template_id)
    )
    template = template.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create instance
    instance = AgentInstance(
        **instance_data.dict(),
        created_by=current_user.id if hasattr(current_user, 'id') else None
    )
    
    db.add(instance)
    await db.commit()
    await db.refresh(instance)
    
    # Initialize LangGraph agent if needed
    try:
        await agent_manager.create_agent_workflow(instance)
    except Exception as e:
        # Log error but don't fail instance creation
        print(f"Failed to create LangGraph agent workflow: {e}")
    
    return instance

@instances_router.get("/{instance_id}", response_model=AgentInstanceResponse)
async def get_agent_instance(
    instance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific agent instance"""
    instance = await db.execute(
        select(AgentInstance)
        .options(selectinload(AgentInstance.template))
        .where(AgentInstance.id == instance_id)
    )
    instance = instance.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return instance

@instances_router.put("/{instance_id}", response_model=AgentInstanceResponse)
async def update_agent_instance(
    instance_id: uuid.UUID,
    instance_data: AgentInstanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an agent instance"""
    instance = await db.execute(
        select(AgentInstance)
        .options(selectinload(AgentInstance.template))
        .where(AgentInstance.id == instance_id)
    )
    instance = instance.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Update fields
    update_data = instance_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instance, field, value)
    
    await db.commit()
    await db.refresh(instance)
    
    # Update LangGraph agent if needed
    try:
        await agent_manager.update_agent_workflow(instance)
    except Exception as e:
        print(f"Failed to update LangGraph agent workflow: {e}")
    
    return instance

@instances_router.delete("/{instance_id}")
async def delete_agent_instance(
    instance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an agent instance"""
    instance = await db.execute(
        select(AgentInstance).where(AgentInstance.id == instance_id)
    )
    instance = instance.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Remove from LangGraph if needed
    try:
        await agent_manager.remove_agent_workflow(instance_id)
    except Exception as e:
        print(f"Failed to remove LangGraph agent workflow: {e}")
    
    await db.delete(instance)
    await db.commit()
    
    return {"message": "Instance deleted successfully"}

@instances_router.post("/{instance_id}/start")
async def start_agent_instance(
    instance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start an agent instance"""
    instance = await db.execute(
        select(AgentInstance)
        .options(selectinload(AgentInstance.template))
        .where(AgentInstance.id == instance_id)
    )
    instance = instance.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    try:
        # Start the agent workflow
        await agent_manager.start_agent(instance)
        
        # Update status
        instance.status = "active"
        instance.last_activity = datetime.utcnow()
        await db.commit()
        
        return {"message": "Agent started successfully", "status": "active"}
        
    except Exception as e:
        instance.status = "error"
        instance.error_log = str(e)
        await db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start agent: {str(e)}"
        )

@instances_router.post("/{instance_id}/stop")
async def stop_agent_instance(
    instance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Stop an agent instance"""
    instance = await db.execute(
        select(AgentInstance).where(AgentInstance.id == instance_id)
    )
    instance = instance.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    try:
        # Stop the agent workflow
        await agent_manager.stop_agent(instance_id)
        
        # Update status
        instance.status = "inactive"
        await db.commit()
        
        return {"message": "Agent stopped successfully", "status": "inactive"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop agent: {str(e)}"
        )

@instances_router.get("/{instance_id}/metrics")
async def get_instance_metrics(
    instance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance metrics for an agent instance"""
    instance = await db.execute(
        select(AgentInstance).where(AgentInstance.id == instance_id)
    )
    instance = instance.scalar_one_or_none()
    
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Get conversation history and metrics
    conversations = await db.execute(
        select(AgentInstanceConversation)
        .where(AgentInstanceConversation.agent_instance_id == instance_id)
        .order_by(AgentInstanceConversation.created_at.desc())
        .limit(100)
    )
    conversations = conversations.scalars().all()
    
    return {
        "instance_id": instance_id,
        "metrics": instance.performance_metrics or {},
        "total_conversations": len(conversations),
        "last_activity": instance.last_activity,
        "status": instance.status,
        "recent_conversations": [
            {
                "id": str(c.id),
                "session_id": c.session_id,
                "created_at": c.created_at,
                "tools_used": c.tools_used or [],
                "performance_metrics": c.performance_metrics or {}
            }
            for c in conversations[:10]
        ]
    }

# Include both routers
router.include_router(instances_router)
