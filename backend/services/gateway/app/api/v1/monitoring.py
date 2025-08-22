"""
Monitoring and Observability API for workflow execution
Provides metrics, traces, and health monitoring for the default workflow system
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import json
import redis
import logging
import httpx

from ...core.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Redis client for metrics
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

# Pydantic models
class WorkflowMetrics(BaseModel):
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time: float
    avg_steps_per_execution: float
    success_rate: float
    most_common_memory_types: List[Dict[str, Any]]
    executions_by_hour: List[Dict[str, Any]]

class SystemHealth(BaseModel):
    status: str
    services: Dict[str, Dict[str, Any]]
    database_health: Dict[str, Any]
    redis_health: Dict[str, Any]
    memory_usage: Dict[str, Any]
    timestamp: datetime

class ExecutionTrace(BaseModel):
    execution_id: str
    session_id: str
    user_query: str
    context: Optional[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    total_duration: float
    status: str
    error_message: Optional[str]
    memory_items_created: int

@router.get("/metrics/workflow")
async def get_workflow_metrics(
    time_range_hours: int = 24,
    db: AsyncSession = Depends(get_database)
):
    """Get workflow execution metrics"""
    try:
        # Calculate time range
        start_time = datetime.now() - timedelta(hours=time_range_hours)
        
        # Get execution metrics
        metrics_query = await db.execute(text("""
            WITH execution_stats AS (
                SELECT 
                    execution_id,
                    session_id,
                    MIN(created_at) as started_at,
                    MAX(created_at) as completed_at,
                    COUNT(*) as step_count,
                    CASE 
                        WHEN bool_or(memory_type LIKE '%error%') THEN 'failed'
                        WHEN bool_or(memory_type = 'workflow_completion') THEN 'completed'
                        ELSE 'in_progress'
                    END as status
                FROM workflow_short_memory 
                WHERE created_at >= :start_time 
                AND execution_id IS NOT NULL
                GROUP BY execution_id, session_id
            )
            SELECT 
                COUNT(*) as total_executions,
                COUNT(*) FILTER (WHERE status = 'completed') as successful_executions,
                COUNT(*) FILTER (WHERE status = 'failed') as failed_executions,
                COALESCE(AVG(EXTRACT(epoch FROM (completed_at - started_at))), 0) as avg_execution_time,
                COALESCE(AVG(step_count), 0) as avg_steps_per_execution,
                CASE 
                    WHEN COUNT(*) > 0 THEN 
                        CAST(COUNT(*) FILTER (WHERE status = 'completed') AS FLOAT) / COUNT(*) * 100
                    ELSE 0 
                END as success_rate
            FROM execution_stats
        """), {"start_time": start_time})
        
        metrics_row = metrics_query.fetchone()
        
        # Get memory type distribution
        memory_types_query = await db.execute(text("""
            SELECT 
                memory_type,
                COUNT(*) as count,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
            FROM workflow_short_memory 
            WHERE created_at >= :start_time
            GROUP BY memory_type
            ORDER BY count DESC
            LIMIT 10
        """), {"start_time": start_time})
        
        memory_types = memory_types_query.fetchall()
        
        # Get executions by hour
        hourly_query = await db.execute(text("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(DISTINCT execution_id) as executions,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM workflow_short_memory 
            WHERE created_at >= :start_time 
            AND execution_id IS NOT NULL
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
        """), {"start_time": start_time})
        
        hourly_data = hourly_query.fetchall()
        
        return {
            "time_range_hours": time_range_hours,
            "total_executions": metrics_row.total_executions or 0,
            "successful_executions": metrics_row.successful_executions or 0,
            "failed_executions": metrics_row.failed_executions or 0,
            "avg_execution_time": round(metrics_row.avg_execution_time or 0, 2),
            "avg_steps_per_execution": round(metrics_row.avg_steps_per_execution or 0, 1),
            "success_rate": round(metrics_row.success_rate or 0, 2),
            "most_common_memory_types": [
                {
                    "type": row.memory_type,
                    "count": row.count,
                    "percentage": round(row.percentage, 1)
                } for row in memory_types
            ],
            "executions_by_hour": [
                {
                    "hour": row.hour.isoformat(),
                    "executions": row.executions,
                    "unique_sessions": row.unique_sessions
                } for row in hourly_data
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/health/system")
async def get_system_health(db: AsyncSession = Depends(get_database)):
    """Get comprehensive system health status"""
    try:
        health_status = {
            "status": "healthy",
            "services": {},
            "database_health": {},
            "redis_health": {},
            "memory_usage": {},
            "timestamp": datetime.now()
        }
        
        # Check database health
        try:
            db_result = await db.execute(text("SELECT 1"))
            db_connected = db_result.fetchone() is not None
            
            # Get database stats
            stats_result = await db.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM workflow_short_memory WHERE expires_at IS NULL OR expires_at > NOW()) as active_short_memory,
                    (SELECT COUNT(*) FROM workflow_long_memory) as long_memory,
                    (SELECT COUNT(DISTINCT session_id) FROM workflow_short_memory WHERE created_at >= NOW() - INTERVAL '24 hours') as active_sessions_24h
            """))
            stats = stats_result.fetchone()
            
            health_status["database_health"] = {
                "connected": db_connected,
                "active_short_memory": stats.active_short_memory if stats else 0,
                "long_memory": stats.long_memory if stats else 0,
                "active_sessions_24h": stats.active_sessions_24h if stats else 0
            }
        except Exception as e:
            health_status["database_health"] = {"connected": False, "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check Redis health
        try:
            redis_client.ping()
            redis_info = redis_client.info()
            health_status["redis_health"] = {
                "connected": True,
                "memory_used": redis_info.get("used_memory_human", "unknown"),
                "connected_clients": redis_info.get("connected_clients", 0),
                "keyspace_hits": redis_info.get("keyspace_hits", 0)
            }
        except Exception as e:
            health_status["redis_health"] = {"connected": False, "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check workflow service health
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8005/health", timeout=5.0)
                if response.status_code == 200:
                    workflow_health = response.json()
                    health_status["services"]["workflow_service"] = {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "details": workflow_health
                    }
                else:
                    health_status["services"]["workflow_service"] = {
                        "status": "unhealthy",
                        "http_status": response.status_code
                    }
                    health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["workflow_service"] = {
                "status": "unreachable",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Get memory usage stats
        try:
            memory_stats = await db.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as database_size,
                    (SELECT COUNT(*) FROM workflow_short_memory WHERE expires_at > NOW()) as expiring_memories,
                    (SELECT COUNT(*) FROM workflow_short_memory WHERE created_at < NOW() - INTERVAL '1 hour' AND expires_at IS NULL) as old_memories
            """))
            memory = memory_stats.fetchone()
            
            health_status["memory_usage"] = {
                "database_size": memory.database_size if memory else "unknown",
                "expiring_memories": memory.expiring_memories if memory else 0,
                "old_memories": memory.old_memories if memory else 0
            }
        except Exception as e:
            health_status["memory_usage"] = {"error": str(e)}
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")

@router.get("/trace/execution/{execution_id}")
async def get_execution_trace(execution_id: str, db: AsyncSession = Depends(get_database)):
    """Get detailed execution trace for debugging"""
    try:
        # Get execution details
        execution_query = await db.execute(text("""
            SELECT 
                execution_id,
                session_id,
                MIN(created_at) as started_at,
                MAX(created_at) as completed_at,
                COUNT(*) as total_steps,
                array_agg(
                    json_build_object(
                        'memory_type', memory_type,
                        'content', content,
                        'metadata', metadata::json,
                        'timestamp', created_at
                    ) ORDER BY created_at
                ) as steps
            FROM workflow_short_memory 
            WHERE execution_id = :execution_id
            GROUP BY execution_id, session_id
        """), {"execution_id": execution_id})
        
        execution = execution_query.fetchone()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Calculate duration
        duration = 0
        if execution.started_at and execution.completed_at:
            duration = (execution.completed_at - execution.started_at).total_seconds()
        
        # Determine status
        status = "in_progress"
        error_message = None
        
        for step in execution.steps:
            if step.get("memory_type") == "workflow_completion":
                status = "completed"
                break
            elif "error" in step.get("memory_type", "").lower():
                status = "failed"
                error_message = step.get("content", "Unknown error")
                break
        
        return {
            "execution_id": execution.execution_id,
            "session_id": execution.session_id,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "total_duration": duration,
            "status": status,
            "error_message": error_message,
            "total_steps": execution.total_steps,
            "steps": [
                {
                    "memory_type": step["memory_type"],
                    "content": step["content"],
                    "metadata": step["metadata"],
                    "timestamp": step["timestamp"].isoformat() if step["timestamp"] else None
                } for step in execution.steps
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution trace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get execution trace: {str(e)}")

@router.get("/analytics/sessions")
async def get_session_analytics(
    limit: int = 20,
    db: AsyncSession = Depends(get_database)
):
    """Get session analytics and patterns"""
    try:
        # Get session statistics
        session_query = await db.execute(text("""
            WITH session_stats AS (
                SELECT 
                    session_id,
                    COUNT(DISTINCT execution_id) as executions,
                    COUNT(*) as total_memory_items,
                    MIN(created_at) as first_activity,
                    MAX(created_at) as last_activity,
                    array_agg(DISTINCT memory_type) as memory_types,
                    COUNT(*) FILTER (WHERE memory_type = 'workflow_completion') as completions,
                    COUNT(*) FILTER (WHERE memory_type LIKE '%error%') as errors
                FROM workflow_short_memory 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY session_id
            )
            SELECT 
                session_id,
                executions,
                total_memory_items,
                first_activity,
                last_activity,
                EXTRACT(epoch FROM (last_activity - first_activity)) as session_duration,
                memory_types,
                completions,
                errors,
                CASE 
                    WHEN errors = 0 AND completions > 0 THEN 'successful'
                    WHEN errors > 0 THEN 'has_errors'
                    ELSE 'active'
                END as status
            FROM session_stats
            ORDER BY last_activity DESC
            LIMIT :limit
        """), {"limit": limit})
        
        sessions = session_query.fetchall()
        
        # Get overall statistics
        overall_query = await db.execute(text("""
            SELECT 
                COUNT(DISTINCT session_id) as total_sessions,
                AVG(session_duration) as avg_session_duration,
                AVG(executions) as avg_executions_per_session,
                COUNT(*) FILTER (WHERE status = 'successful') as successful_sessions,
                COUNT(*) FILTER (WHERE status = 'has_errors') as error_sessions
            FROM (
                SELECT 
                    session_id,
                    EXTRACT(epoch FROM (MAX(created_at) - MIN(created_at))) as session_duration,
                    COUNT(DISTINCT execution_id) as executions,
                    CASE 
                        WHEN COUNT(*) FILTER (WHERE memory_type LIKE '%error%') = 0 
                             AND COUNT(*) FILTER (WHERE memory_type = 'workflow_completion') > 0 
                        THEN 'successful'
                        WHEN COUNT(*) FILTER (WHERE memory_type LIKE '%error%') > 0 THEN 'has_errors'
                        ELSE 'active'
                    END as status
                FROM workflow_short_memory 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY session_id
            ) stats
        """))
        
        overall_stats = overall_query.fetchone()
        
        return {
            "time_range": "7 days",
            "overall_statistics": {
                "total_sessions": overall_stats.total_sessions or 0,
                "avg_session_duration": round(overall_stats.avg_session_duration or 0, 2),
                "avg_executions_per_session": round(overall_stats.avg_executions_per_session or 0, 1),
                "successful_sessions": overall_stats.successful_sessions or 0,
                "error_sessions": overall_stats.error_sessions or 0
            },
            "recent_sessions": [
                {
                    "session_id": session.session_id,
                    "executions": session.executions,
                    "total_memory_items": session.total_memory_items,
                    "first_activity": session.first_activity.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "session_duration": round(session.session_duration, 2),
                    "memory_types": session.memory_types or [],
                    "completions": session.completions,
                    "errors": session.errors,
                    "status": session.status
                } for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session analytics: {str(e)}")

@router.post("/cleanup/expired-memory")
async def cleanup_expired_memory(db: AsyncSession = Depends(get_database)):
    """Clean up expired memory items"""
    try:
        # Clean up expired short-term memory
        cleanup_result = await db.execute(text("""
            DELETE FROM workflow_short_memory 
            WHERE expires_at IS NOT NULL AND expires_at < NOW()
        """))
        
        await db.commit()
        
        return {
            "message": "Memory cleanup completed",
            "deleted_items": cleanup_result.rowcount,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during memory cleanup: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Memory cleanup failed: {str(e)}")

@router.get("/health")
async def monitoring_health():
    """Health check for monitoring service"""
    return {
        "status": "healthy",
        "service": "monitoring",
        "timestamp": datetime.now().isoformat()
    }