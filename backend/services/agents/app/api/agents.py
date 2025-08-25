"""
Simplified Agents service API endpoints using direct database queries
"""

from fastapi import APIRouter, HTTPException, status as http_status, Query
from fastapi import Depends
from typing import Dict, Any, List, Optional
import logging
from uuid import UUID
import asyncpg
import os
from tenacity import retry, stop_after_attempt, wait_fixed
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])


# Database connection pool (singleton)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agenticai_user:agenticai_password@postgres:5432/agenticai_platform")
POOL_MIN_SIZE = int(os.getenv("AGENTS_DB_POOL_MIN_SIZE", 2))
POOL_MAX_SIZE = int(os.getenv("AGENTS_DB_POOL_MAX_SIZE", 10))
_db_pool = None

async def get_db_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=POOL_MIN_SIZE,
            max_size=POOL_MAX_SIZE,
            timeout=10
        )
    return _db_pool

# Retry logic for DB operations
def db_retry():
    return retry(stop=stop_after_attempt(3), wait=wait_fixed(1))

@db_retry()
async def acquire_db_conn():
    pool = await get_db_pool()
    return await pool.acquire()

async def release_db_conn(conn):
    pool = await get_db_pool()
    await pool.release(conn)



@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents(
    status_filter: Optional[str] = Query(None, alias="status"),
    agent_type_filter: Optional[str] = Query(None, alias="type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List all agents with optional filtering"""
    try:
        conn = await acquire_db_conn()
        try:
            base_query = """
                SELECT id, name, description, agent_type, status, ai_provider, 
                       model_name, created_at, updated_at, is_active, framework, version, llm_model_id
                FROM agents 
                WHERE 1=1
            """
            params = []
            param_count = 0
            if status_filter:
                param_count += 1
                base_query += f" AND status = ${param_count}"
                params.append(status_filter)
            if agent_type_filter:
                param_count += 1
                base_query += f" AND agent_type = ${param_count}"
                params.append(agent_type_filter)
            base_query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
            params.extend([limit, offset])
            rows = await conn.fetch(base_query, *params)
            agents = []
            for row in rows:
                agent = {
                    "id": str(row['id']),
                    "name": row['name'],
                    "description": row['description'],
                    "agent_type": row['agent_type'],
                    "status": row['status'],
                    "ai_provider": row['ai_provider'],
                    "model_name": row['model_name'],
                    "llm_model_id": str(row['llm_model_id']) if row['llm_model_id'] else None,
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
                    "is_active": row['is_active'],
                    "framework": row['framework'],
                    "version": row['version']
                }
                agents.append(agent)
            return agents
        finally:
            await release_db_conn(conn)
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )



@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: UUID):
    """Get agent by ID"""
    try:
        conn = await acquire_db_conn()
        try:
            row = await conn.fetchrow("""
                SELECT id, name, description, agent_type, status, ai_provider, 
                       model_name, created_at, updated_at, is_active, framework, 
                       version, capabilities, system_prompt, llm_model_id
                FROM agents 
                WHERE id = $1
            """, str(agent_id))
            if not row:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found"
                )
            return {
                "id": str(row['id']),
                "name": row['name'],
                "description": row['description'],
                "agent_type": row['agent_type'],
                "status": row['status'],
                "ai_provider": row['ai_provider'],
                "model_name": row['model_name'],
                "llm_model_id": str(row['llm_model_id']) if row['llm_model_id'] else None,
                "capabilities": row['capabilities'] or [],
                "system_prompt": row['system_prompt'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
                "is_active": row['is_active'],
                "framework": row['framework'],
                "version": row['version']
            }
        finally:
            await release_db_conn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )

# Pydantic models for CRUD operations
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import json

class AgentCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: str
    framework: str = "custom"
    capabilities: List[str] = []
    tags: List[str] = []
    project_tags: Optional[List[str]] = []
    llm_model_id: Optional[str] = None
    systemPrompt: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    max_tokens: Optional[int] = None
    category: Optional[str] = None
    agent_type: str = "generic"
    version: str = "1.0"
    a2a_enabled: bool = True
    a2a_address: Optional[str] = None
    # Deployment fields
    url: Optional[str] = None
    dns_name: Optional[str] = None
    health_url: Optional[str] = None
    environment: Optional[str] = "development"
    author: Optional[str] = None
    organization: Optional[str] = None
    # Signature fields (stored in model_config_data for now)
    # input_signature: Optional[Dict[str, Any]] = None
    # output_signature: Optional[Dict[str, Any]] = None
    default_input_modes: Optional[List[str]] = []
    default_output_modes: Optional[List[str]] = []
    # Model configuration
    model_config_data: Optional[Dict[str, Any]] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    llm_model_id: Optional[str] = None
    systemPrompt: Optional[str] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    category: Optional[str] = None
    agent_type: Optional[str] = None
    version: Optional[str] = None
    a2a_enabled: Optional[bool] = None


@router.post("/", status_code=201)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent"""
    try:
        conn = await acquire_db_conn()
        try:
            agent_id = str(uuid4())
            now = datetime.utcnow()
            
            # Insert new agent
            await conn.execute("""
                INSERT INTO agents (
                    id, name, display_name, description, agent_type, status, framework, version,
                    capabilities, system_prompt, llm_model_id, tags, project_tags,
                    temperature, max_tokens, category, a2a_enabled, a2a_address,
                    url, dns_name, health_url, environment, author, organization,
                    default_input_modes, default_output_modes, model_config_data,
                    created_at, updated_at, is_active
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                    $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24,
                    $25, $26, $27, $28, $29, $30
                )
            """, 
                agent_id, agent_data.name, agent_data.display_name, agent_data.description, 
                agent_data.agent_type, "active", agent_data.framework, agent_data.version,
                agent_data.capabilities, agent_data.systemPrompt or agent_data.system_prompt, 
                agent_data.llm_model_id, agent_data.tags, agent_data.project_tags,
                agent_data.temperature, agent_data.maxTokens or agent_data.max_tokens, 
                agent_data.category, agent_data.a2a_enabled, 
                agent_data.a2a_address or (f"http://agents:8002/agents/{agent_id}" if agent_data.a2a_enabled else None),
                agent_data.url or (f"http://agents:8002/agents/{agent_id}" if agent_data.a2a_enabled else None), 
                agent_data.dns_name, agent_data.health_url, 
                agent_data.environment, agent_data.author, agent_data.organization,
                agent_data.default_input_modes, agent_data.default_output_modes, 
                agent_data.model_config_data, now, now, True
            )
            
            # Return the created agent
            return {
                "id": agent_id,
                "name": agent_data.name,
                "description": agent_data.description,
                "agent_type": agent_data.agent_type,
                "status": "active",
                "framework": agent_data.framework,
                "version": agent_data.version,
                "capabilities": agent_data.capabilities,
                "system_prompt": agent_data.systemPrompt,
                "llm_model_id": agent_data.llm_model_id,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "is_active": True
            }
        finally:
            await release_db_conn(conn)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.put("/{agent_id}")
async def update_agent(agent_id: UUID, agent_data: AgentUpdate):
    """Update an existing agent"""
    try:
        conn = await acquire_db_conn()
        try:
            # Check if agent exists
            existing = await conn.fetchrow("SELECT id FROM agents WHERE id = $1", str(agent_id))
            if not existing:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found"
                )
            
            # Build update query dynamically based on provided fields
            update_fields = []
            update_values = []
            param_count = 1
            
            for field, value in agent_data.dict(exclude_unset=True).items():
                if value is not None:
                    # Map field names to database columns
                    db_field = field
                    if field == "systemPrompt":
                        db_field = "system_prompt"
                    
                    update_fields.append(f"{db_field} = ${param_count}")
                    update_values.append(value)
                    param_count += 1
            
            if not update_fields:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )
            
            # Add updated_at
            update_fields.append(f"updated_at = ${param_count}")
            update_values.append(datetime.utcnow())
            param_count += 1
            
            # Add agent_id for WHERE clause
            update_values.append(str(agent_id))
            
            query = f"""
                UPDATE agents 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count}
            """
            
            await conn.execute(query, *update_values)
            
            # Fetch and return the updated agent
            row = await conn.fetchrow("""
                SELECT id, name, description, agent_type, status, framework, 
                       version, capabilities, system_prompt, llm_model_id,
                       created_at, updated_at, is_active
                FROM agents 
                WHERE id = $1
            """, str(agent_id))
            
            return {
                "id": str(row['id']),
                "name": row['name'],
                "description": row['description'],
                "agent_type": row['agent_type'],
                "status": row['status'],
                "framework": row['framework'],
                "version": row['version'],
                "capabilities": row['capabilities'] or [],
                "system_prompt": row['system_prompt'],
                "llm_model_id": str(row['llm_model_id']) if row['llm_model_id'] else None,
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
                "is_active": row['is_active']
            }
            
        finally:
            await release_db_conn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: UUID):
    """Delete an agent"""
    try:
        conn = await acquire_db_conn()
        try:
            # Check if agent exists
            existing = await conn.fetchrow("SELECT id FROM agents WHERE id = $1", str(agent_id))
            if not existing:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found"
                )
            
            # Delete the agent
            await conn.execute("DELETE FROM agents WHERE id = $1", str(agent_id))
            
            # Return 204 No Content (handled by status_code parameter)
            return None
            
        finally:
            await release_db_conn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post("/{agent_id}/run")
async def run_agent(agent_id: UUID, task_data: dict = None):
    """Run an agent with given task data"""
    try:
        conn = await acquire_db_conn()
        try:
            # Check if agent exists and is active
            agent = await conn.fetchrow("""
                SELECT id, name, status, is_active FROM agents 
                WHERE id = $1
            """, str(agent_id))
            
            if not agent:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found"
                )
            
            if not agent['is_active'] or agent['status'] != 'active':
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Agent {agent_id} is not active"
                )
            
            # For now, return a mock execution response
            # In a real implementation, this would execute the agent
            task_id = str(uuid4())
            
            return {
                "taskId": task_id,
                "agentId": str(agent_id),
                "agentName": agent['name'],
                "status": "running",
                "message": "Agent execution started",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            await release_db_conn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run agent: {str(e)}"
        )


# Health check endpoint for DB connection
@router.get("/health", tags=["health"])
async def health_check():
    try:
        conn = await acquire_db_conn()
        try:
            await conn.execute("SELECT 1")
            return {"status": "healthy", "db": "connected"}
        finally:
            await release_db_conn(conn)
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        return {"status": "unhealthy", "db": "disconnected", "error": str(e)}
