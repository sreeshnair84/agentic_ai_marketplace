"""
Memory Management API endpoints for workflow execution memory
Provides access to short-term and long-term memory stored in Redis and PGVector
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import redis
import logging

from ...core.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/memory", tags=["memory"])

# Redis client (would be initialized from config)
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

# Pydantic models
class MemoryItem(BaseModel):
    id: Optional[str] = None
    session_id: str
    execution_id: Optional[str] = None
    memory_type: str
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime
    expires_at: Optional[datetime] = None

class MemoryQuery(BaseModel):
    session_id: str
    execution_id: Optional[str] = None
    memory_types: Optional[List[str]] = None
    limit: int = 50
    search_query: Optional[str] = None

class MemoryStats(BaseModel):
    session_id: str
    short_term_count: int
    long_term_count: int
    total_executions: int
    memory_types: List[str]
    oldest_memory: Optional[datetime]
    newest_memory: Optional[datetime]

@router.get("/sessions/{session_id}/short-term")
async def get_short_term_memory(
    session_id: str,
    execution_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_database)
):
    """Get short-term memory for a session"""
    try:
        # Build query conditions
        conditions = ["session_id = $1"]
        params = [session_id]
        param_count = 1
        
        if execution_id:
            param_count += 1
            conditions.append(f"execution_id = ${param_count}")
            params.append(execution_id)
        
        if memory_type:
            param_count += 1
            conditions.append(f"memory_type = ${param_count}")
            params.append(memory_type)
        
        # Add expiration check
        conditions.append("(expires_at IS NULL OR expires_at > NOW())")
        
        query = f"""
            SELECT id, session_id, execution_id, memory_type, content, metadata, 
                   created_at, expires_at
            FROM workflow_short_memory 
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC 
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        memory_items = []
        for row in rows:
            memory_items.append({
                "id": str(row.id),
                "session_id": row.session_id,
                "execution_id": row.execution_id,
                "memory_type": row.memory_type,
                "content": row.content,
                "metadata": json.loads(row.metadata) if row.metadata else {},
                "timestamp": row.created_at.isoformat(),
                "expires_at": row.expires_at.isoformat() if row.expires_at else None
            })
        
        return {
            "session_id": session_id,
            "execution_id": execution_id,
            "memory_type": memory_type,
            "count": len(memory_items),
            "items": memory_items
        }
        
    except Exception as e:
        logger.error(f"Error fetching short-term memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch memory: {str(e)}")

@router.get("/sessions/{session_id}/long-term")
async def get_long_term_memory(
    session_id: str,
    memory_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    db: AsyncSession = Depends(get_database)
):
    """Get long-term memory for a session"""
    try:
        conditions = ["session_id = $1"]
        params = [session_id]
        param_count = 1
        
        if memory_type:
            param_count += 1
            conditions.append(f"memory_type = ${param_count}")
            params.append(memory_type)
        
        query = f"""
            SELECT id, session_id, user_id, memory_type, content, metadata,
                   access_count, last_accessed, created_at
            FROM workflow_long_memory 
            WHERE {' AND '.join(conditions)}
            ORDER BY last_accessed DESC 
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        memory_items = []
        for row in rows:
            memory_items.append({
                "id": str(row.id),
                "session_id": row.session_id,
                "user_id": row.user_id,
                "memory_type": row.memory_type,
                "content": row.content,
                "metadata": json.loads(row.metadata) if row.metadata else {},
                "access_count": row.access_count,
                "last_accessed": row.last_accessed.isoformat(),
                "created_at": row.created_at.isoformat()
            })
        
        return {
            "session_id": session_id,
            "memory_type": memory_type,
            "count": len(memory_items),
            "items": memory_items
        }
        
    except Exception as e:
        logger.error(f"Error fetching long-term memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch memory: {str(e)}")

@router.get("/sessions/{session_id}/stats")
async def get_memory_stats(
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get memory statistics for a session"""
    try:
        # Get short-term memory stats
        short_term_result = await db.execute(text("""
            SELECT COUNT(*) as count, 
                   array_agg(DISTINCT memory_type) as types,
                   MIN(created_at) as oldest,
                   MAX(created_at) as newest
            FROM workflow_short_memory 
            WHERE session_id = $1 
            AND (expires_at IS NULL OR expires_at > NOW())
        """), [session_id])
        short_term_row = short_term_result.fetchone()
        
        # Get long-term memory stats
        long_term_result = await db.execute(text("""
            SELECT COUNT(*) as count,
                   array_agg(DISTINCT memory_type) as types,
                   MIN(created_at) as oldest,
                   MAX(created_at) as newest
            FROM workflow_long_memory 
            WHERE session_id = $1
        """), [session_id])
        long_term_row = long_term_result.fetchone()
        
        # Get execution count
        exec_result = await db.execute(text("""
            SELECT COUNT(DISTINCT execution_id) as exec_count
            FROM workflow_short_memory 
            WHERE session_id = $1 
            AND execution_id IS NOT NULL
        """), [session_id])
        exec_row = exec_result.fetchone()
        
        # Combine memory types
        short_types = short_term_row.types or []
        long_types = long_term_row.types or []
        all_types = list(set(short_types + long_types))
        
        # Get oldest/newest across both
        timestamps = [
            short_term_row.oldest, short_term_row.newest,
            long_term_row.oldest, long_term_row.newest
        ]
        valid_timestamps = [t for t in timestamps if t is not None]
        
        return {
            "session_id": session_id,
            "short_term_count": short_term_row.count or 0,
            "long_term_count": long_term_row.count or 0,
            "total_executions": exec_row.exec_count or 0,
            "memory_types": all_types,
            "oldest_memory": min(valid_timestamps).isoformat() if valid_timestamps else None,
            "newest_memory": max(valid_timestamps).isoformat() if valid_timestamps else None
        }
        
    except Exception as e:
        logger.error(f"Error fetching memory stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

@router.get("/sessions/{session_id}/executions")
async def get_execution_history(
    session_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database)
):
    """Get execution history for a session"""
    try:
        result = await db.execute(text("""
            SELECT execution_id,
                   MIN(created_at) as started_at,
                   MAX(created_at) as completed_at,
                   COUNT(*) as memory_count,
                   array_agg(DISTINCT memory_type) as memory_types,
                   bool_or(memory_type = 'execution_plan') as has_plan,
                   bool_or(memory_type LIKE '%_result') as has_results
            FROM workflow_short_memory
            WHERE session_id = $1 AND execution_id IS NOT NULL
            GROUP BY execution_id
            ORDER BY MIN(created_at) DESC
            LIMIT $2
        """), [session_id, limit])
        
        rows = result.fetchall()
        
        executions = []
        for row in rows:
            duration = None
            if row.started_at and row.completed_at:
                duration = (row.completed_at - row.started_at).total_seconds()
            
            executions.append({
                "execution_id": row.execution_id,
                "started_at": row.started_at.isoformat() if row.started_at else None,
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "duration_seconds": duration,
                "memory_count": row.memory_count,
                "memory_types": row.memory_types or [],
                "has_plan": row.has_plan,
                "has_results": row.has_results
            })
        
        return {
            "session_id": session_id,
            "count": len(executions),
            "executions": executions
        }
        
    except Exception as e:
        logger.error(f"Error fetching execution history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch executions: {str(e)}")

@router.get("/sessions/{session_id}/executions/{execution_id}")
async def get_execution_details(
    session_id: str,
    execution_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get detailed information about a specific execution"""
    try:
        result = await db.execute(text("""
            SELECT memory_type, content, metadata, created_at
            FROM workflow_short_memory 
            WHERE session_id = $1 AND execution_id = $2
            AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY created_at ASC
        """), [session_id, execution_id])
        
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Organize by memory type
        execution_data = {
            "session_id": session_id,
            "execution_id": execution_id,
            "started_at": rows[0].created_at.isoformat(),
            "completed_at": rows[-1].created_at.isoformat(),
            "memory_items": []
        }
        
        for row in rows:
            execution_data["memory_items"].append({
                "memory_type": row.memory_type,
                "content": row.content,
                "metadata": json.loads(row.metadata) if row.metadata else {},
                "timestamp": row.created_at.isoformat()
            })
        
        # Calculate duration
        start_time = datetime.fromisoformat(execution_data["started_at"])
        end_time = datetime.fromisoformat(execution_data["completed_at"])
        execution_data["duration_seconds"] = (end_time - start_time).total_seconds()
        
        return execution_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching execution details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch execution: {str(e)}")

@router.delete("/sessions/{session_id}/memory")
async def clear_session_memory(
    session_id: str,
    memory_type: Optional[str] = None,
    older_than_hours: Optional[int] = None,
    db: AsyncSession = Depends(get_database)
):
    """Clear memory for a session"""
    try:
        conditions = ["session_id = $1"]
        params = [session_id]
        param_count = 1
        
        if memory_type:
            param_count += 1
            conditions.append(f"memory_type = ${param_count}")
            params.append(memory_type)
        
        if older_than_hours:
            param_count += 1
            conditions.append(f"created_at < NOW() - INTERVAL '{older_than_hours} hours'")
        
        # Clear short-term memory
        short_query = f"""
            DELETE FROM workflow_short_memory 
            WHERE {' AND '.join(conditions)}
        """
        short_result = await db.execute(text(short_query), params)
        
        # Clear long-term memory (with same conditions)
        long_query = f"""
            DELETE FROM workflow_long_memory 
            WHERE {' AND '.join(conditions)}
        """
        long_result = await db.execute(text(long_query), params)
        
        await db.commit()
        
        return {
            "session_id": session_id,
            "memory_type": memory_type,
            "older_than_hours": older_than_hours,
            "short_term_deleted": short_result.rowcount,
            "long_term_deleted": long_result.rowcount,
            "total_deleted": short_result.rowcount + long_result.rowcount
        }
        
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")

@router.post("/sessions/{session_id}/memory/search")
async def search_memory(
    session_id: str,
    query: str,
    memory_types: Optional[List[str]] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_database)
):
    """Search memory content using text search"""
    try:
        conditions = ["session_id = $1", "content ILIKE $2"]
        params = [session_id, f"%{query}%"]
        param_count = 2
        
        if memory_types:
            param_count += 1
            placeholders = ','.join(f'${i}' for i in range(param_count, param_count + len(memory_types)))
            conditions.append(f"memory_type = ANY(ARRAY[{placeholders}])")
            params.extend(memory_types)
            param_count += len(memory_types)
        
        # Search short-term memory
        short_query = f"""
            SELECT 'short' as memory_category, id, execution_id, memory_type, 
                   content, metadata, created_at, expires_at
            FROM workflow_short_memory 
            WHERE {' AND '.join(conditions)} 
            AND (expires_at IS NULL OR expires_at > NOW())
        """
        
        # Search long-term memory
        long_query = f"""
            SELECT 'long' as memory_category, id, NULL as execution_id, memory_type,
                   content, metadata, created_at, NULL as expires_at
            FROM workflow_long_memory 
            WHERE {' AND '.join(conditions)}
        """
        
        # Combine queries
        combined_query = f"""
            ({short_query}) UNION ALL ({long_query})
            ORDER BY created_at DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)
        
        result = await db.execute(text(combined_query), params)
        rows = result.fetchall()
        
        search_results = []
        for row in rows:
            search_results.append({
                "memory_category": row.memory_category,
                "id": str(row.id),
                "execution_id": row.execution_id,
                "memory_type": row.memory_type,
                "content": row.content,
                "metadata": json.loads(row.metadata) if row.metadata else {},
                "created_at": row.created_at.isoformat(),
                "expires_at": row.expires_at.isoformat() if row.expires_at else None
            })
        
        return {
            "session_id": session_id,
            "query": query,
            "memory_types": memory_types,
            "count": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search memory: {str(e)}")

@router.get("/health")
async def get_memory_health(db: AsyncSession = Depends(get_database)):
    """Get memory system health status"""
    try:
        # Check database connection
        db_health = await db.execute(text("SELECT 1"))
        db_connected = db_health.fetchone() is not None
        
        # Check Redis connection
        try:
            redis_client.ping()
            redis_connected = True
        except:
            redis_connected = False
        
        # Get memory counts
        memory_stats = await db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM workflow_short_memory WHERE expires_at IS NULL OR expires_at > NOW()) as short_count,
                (SELECT COUNT(*) FROM workflow_long_memory) as long_count
        """))
        stats = memory_stats.fetchone()
        
        return {
            "status": "healthy" if db_connected and redis_connected else "degraded",
            "database_connected": db_connected,
            "redis_connected": redis_connected,
            "short_term_memory_count": stats.short_count if stats else 0,
            "long_term_memory_count": stats.long_count if stats else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking memory health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }