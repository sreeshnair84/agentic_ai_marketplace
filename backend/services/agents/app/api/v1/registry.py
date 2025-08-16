"""
Agent registry API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...core.database import get_db, Agent, AgentCapability, AgentType, AgentStatus, AIProvider
from ...services.agent_service import agent_service
from ...examples.sample_queries import (
    ALL_SAMPLE_QUERIES, QUICK_START_QUERIES, 
    get_sample_queries_by_category, get_contextual_suggestions,
    QueryCategory
)

router = APIRouter()


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: AgentType
    ai_provider: AIProvider = AIProvider.GEMINI
    model_name: str = "gemini-1.5-pro"
    system_prompt: Optional[str] = None
    capabilities: Optional[List[str]] = None
    model_config: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 2048


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_config: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    agent_type: AgentType
    status: AgentStatus
    ai_provider: AIProvider
    model_name: str
    capabilities: List[str]
    system_prompt: Optional[str]
    temperature: float
    max_tokens: int
    version: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_active: bool
    a2a_enabled: bool
    a2a_address: Optional[str]


class CapabilityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    parameters_schema: Optional[Dict[str, Any]] = None


class CapabilityResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    parameters_schema: Optional[Dict[str, Any]]
    created_at: datetime


@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = "system"  # TODO: Get from auth
):
    """Create a new agent"""
    
    # Prepare model config
    model_config = agent.model_config or {}
    model_config.update({
        "temperature": agent.temperature,
        "max_output_tokens": agent.max_tokens
    })
    
    created_agent = await agent_service.create_agent(
        db=db,
        name=agent.name,
        agent_type=agent.agent_type,
        created_by=current_user,
        description=agent.description,
        ai_provider=agent.ai_provider,
        model_name=agent.model_name,
        system_prompt=agent.system_prompt,
        capabilities=agent.capabilities,
        model_config=model_config
    )
    
    return AgentResponse(
        id=created_agent.id,
        name=created_agent.name,
        description=created_agent.description,
        agent_type=created_agent.agent_type,
        status=created_agent.status,
        ai_provider=created_agent.ai_provider,
        model_name=created_agent.model_name,
        capabilities=created_agent.capabilities,
        system_prompt=created_agent.system_prompt,
        temperature=(created_agent.model_config or {}).get("temperature", 0.7),
        max_tokens=(created_agent.model_config or {}).get("max_output_tokens", 2048),
        version=created_agent.version,
        created_at=created_agent.created_at,
        updated_at=created_agent.updated_at,
        created_by=created_agent.created_by,
        is_active=created_agent.is_active,
        a2a_enabled=created_agent.a2a_enabled,
        a2a_address=created_agent.a2a_address
    )


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    agent_type: Optional[AgentType] = Query(None),
    status: Optional[AgentStatus] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List agents"""
    
    query = select(Agent).offset(skip).limit(limit)
    
    if agent_type:
        query = query.where(Agent.agent_type == agent_type)
    if status:
        query = query.where(Agent.status == status)
    if is_active is not None:
        query = query.where(Agent.is_active == is_active)
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return [
        AgentResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            agent_type=a.agent_type,
            status=a.status,
            ai_provider=a.ai_provider,
            model_name=a.model_name,
            capabilities=a.capabilities,
            system_prompt=a.system_prompt,
            temperature=(a.model_config or {}).get("temperature", 0.7),
            max_tokens=(a.model_config or {}).get("max_output_tokens", 2048),
            version=a.version,
            created_at=a.created_at,
            updated_at=a.updated_at,
            created_by=a.created_by,
            is_active=a.is_active,
            a2a_enabled=a.a2a_enabled,
            a2a_address=a.a2a_address
        )
        for a in agents
    ]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific agent"""
    
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        status=agent.status,
        ai_provider=agent.ai_provider,
        model_name=agent.model_name,
        capabilities=agent.capabilities,
        system_prompt=agent.system_prompt,
        temperature=(agent.model_config or {}).get("temperature", 0.7),
        max_tokens=(agent.model_config or {}).get("max_output_tokens", 2048),
        version=agent.version,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        created_by=agent.created_by,
        is_active=agent.is_active,
        a2a_enabled=agent.a2a_enabled,
        a2a_address=agent.a2a_address
    )


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an agent"""
    
    # Check if agent exists
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Update fields
    update_data = agent_update.model_dump(exclude_unset=True)
    
    # Handle model config updates
    if any(k in update_data for k in ["temperature", "max_tokens"]):
        model_config = agent.model_config.copy() if agent.model_config else {}
        if "temperature" in update_data:
            model_config["temperature"] = update_data.pop("temperature")
        if "max_tokens" in update_data:
            model_config["max_output_tokens"] = update_data.pop("max_tokens")
        update_data["model_config"] = model_config
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        await db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(**update_data)
        )
        await db.commit()
        
        # Refresh agent
        await db.refresh(agent)
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        status=agent.status,
        ai_provider=agent.ai_provider,
        model_name=agent.model_name,
        capabilities=agent.capabilities,
        system_prompt=agent.system_prompt,
        temperature=(agent.model_config or {}).get("temperature", 0.7),
        max_tokens=(agent.model_config or {}).get("max_output_tokens", 2048),
        version=agent.version,
        created_at=agent.created_at,
        updated_at=agent.updated_at,
        created_by=agent.created_by,
        is_active=agent.is_active,
        a2a_enabled=agent.a2a_enabled,
        a2a_address=agent.a2a_address
    )


@router.delete("/agents/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an agent (soft delete)"""
    
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Soft delete
    await db.execute(
        update(Agent)
        .where(Agent.id == agent_id)
        .values(is_active=False, status=AgentStatus.INACTIVE, updated_at=datetime.utcnow())
    )
    await db.commit()
    
    return {"message": "Agent deleted successfully"}


@router.post("/agents/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Activate an agent"""
    
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Activate agent
    await db.execute(
        update(Agent)
        .where(Agent.id == agent_id)
        .values(status=AgentStatus.ACTIVE, updated_at=datetime.utcnow())
    )
    await db.commit()
    
    return {"message": "Agent activated successfully"}


@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate an agent"""
    
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Deactivate agent
    await db.execute(
        update(Agent)
        .where(Agent.id == agent_id)
        .values(status=AgentStatus.INACTIVE, updated_at=datetime.utcnow())
    )
    await db.commit()
    
    return {"message": "Agent deactivated successfully"}


# Capability endpoints
@router.post("/capabilities", response_model=CapabilityResponse)
async def create_capability(
    capability: CapabilityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent capability"""
    
    db_capability = AgentCapability(
        name=capability.name,
        description=capability.description,
        category=capability.category,
        parameters_schema=capability.parameters_schema
    )
    
    db.add(db_capability)
    await db.commit()
    await db.refresh(db_capability)
    
    return CapabilityResponse(
        id=db_capability.id,
        name=db_capability.name,
        description=db_capability.description,
        category=db_capability.category,
        parameters_schema=db_capability.parameters_schema,
        created_at=db_capability.created_at
    )


@router.get("/capabilities", response_model=List[CapabilityResponse])
async def list_capabilities(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List agent capabilities"""
    
    query = select(AgentCapability)
    
    if category:
        query = query.where(AgentCapability.category == category)
    
    result = await db.execute(query)
    capabilities = result.scalars().all()
    
    return [
        CapabilityResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            category=c.category,
            parameters_schema=c.parameters_schema,
            created_at=c.created_at
        )
        for c in capabilities
    ]


# Sample Queries Endpoints
@router.get("/sample-queries")
async def get_all_sample_queries():
    """Get all sample queries organized by component type"""
    
    # Convert to JSON-serializable format
    result = {}
    for component_type, queries_dict in ALL_SAMPLE_QUERIES.items():
        result[component_type] = {}
        for component_name, queries in queries_dict.items():
            result[component_type][component_name] = [
                {
                    "query": q.query,
                    "description": q.description,
                    "category": q.category.value,
                    "expected_response_type": q.expected_response_type,
                    "tags": q.tags
                }
                for q in queries
            ]
    
    return result


@router.get("/sample-queries/quick-start")
async def get_quick_start_queries():
    """Get quick start sample queries for new users"""
    
    return [
        {
            "query": q.query,
            "description": q.description,
            "category": q.category.value,
            "expected_response_type": q.expected_response_type,
            "tags": q.tags
        }
        for q in QUICK_START_QUERIES
    ]


@router.get("/sample-queries/by-category/{category}")
async def get_queries_by_category(category: str):
    """Get sample queries filtered by category"""
    
    try:
        category_enum = QueryCategory(category)
        queries = get_sample_queries_by_category(category_enum)
        
        return [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags
            }
            for q in queries
        ]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category: {category}. Valid categories: {[c.value for c in QueryCategory]}"
        )


@router.get("/sample-queries/contextual")
async def get_contextual_queries(
    user_role: Optional[str] = Query(None, description="User role for contextual suggestions"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags")
):
    """Get contextual sample queries based on user role or tags"""
    
    suggestions = get_contextual_suggestions(user_role)
    
    return {
        "user_role": user_role,
        "suggestions": suggestions,
        "quick_start": [q.query for q in QUICK_START_QUERIES[:3]]
    }


@router.get("/sample-queries/agents/{agent_id}")
async def get_agent_sample_queries(agent_id: str):
    """Get sample queries specific to an agent"""
    
    # Map agent IDs to sample query keys
    agent_query_mapping = {
        "general-ai-agent": "general_ai_agent",
        "conversation-agent": "conversation_agent", 
        "rag-agent": "rag_agent",
        "task-executor-agent": "task_executor_agent"
    }
    
    query_key = agent_query_mapping.get(agent_id)
    if not query_key or query_key not in ALL_SAMPLE_QUERIES["agents"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sample queries found for agent: {agent_id}"
        )
    
    queries = ALL_SAMPLE_QUERIES["agents"][query_key]
    
    return {
        "agent_id": agent_id,
        "agent_name": query_key.replace("_", " ").title(),
        "sample_queries": [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags
            }
            for q in queries
        ]
    }
