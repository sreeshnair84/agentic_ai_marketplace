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
                       model_name, created_at, updated_at, is_active, framework, version
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
                       version, capabilities, system_prompt
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
