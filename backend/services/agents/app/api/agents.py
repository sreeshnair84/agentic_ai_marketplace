"""
Simplified Agents service API endpoints using direct database queries
"""

from fastapi import APIRouter, HTTPException, status as http_status, Query
from typing import Dict, Any, List, Optional
import logging
from uuid import UUID
import asyncpg
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lcnc_user:lcnc_password@postgres:5432/lcnc_platform")


async def get_db_connection():
    """Get database connection"""
    return await asyncpg.connect(DATABASE_URL)


@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents(
    status_filter: Optional[str] = Query(None, alias="status"),
    agent_type_filter: Optional[str] = Query(None, alias="type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List all agents with optional filtering"""
    
    try:
        conn = await get_db_connection()
        
        try:
            # Build query
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
            
            # Execute query
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
            await conn.close()
        
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
        conn = await get_db_connection()
        
        try:
            # Execute query
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
            await conn.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )
