"""
Health check endpoints for the API Gateway
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
import psutil
import asyncio

from ...core.database import get_database
from ...core.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str
    version: str
    database: str
    memory_usage: float
    cpu_usage: float


class ServiceStatus(BaseModel):
    service: str
    status: str
    response_time_ms: float


class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: datetime
    service: str
    version: str
    database: str
    memory_usage: float
    cpu_usage: float
    services: Dict[str, ServiceStatus]


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_database)
):
    """Basic health check endpoint"""
    
    settings = get_settings()
    
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Get system metrics
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "unhealthy",
        timestamp=datetime.utcnow(),
        service="api-gateway",
        version=settings.VERSION,
        database=db_status,
        memory_usage=memory_usage,
        cpu_usage=cpu_usage
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    db: AsyncSession = Depends(get_database)
):
    """Detailed health check including downstream services"""
    
    settings = get_settings()
    
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Get system metrics
    memory_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Check downstream services
    services = {}
    service_urls = {
        "orchestrator": settings.ORCHESTRATOR_URL,
        "agents": settings.AGENTS_URL,
        "tools": settings.TOOLS_URL,
        "rag": settings.RAG_URL,
        "sqltool": settings.SQLTOOL_URL,
        "workflow": settings.WORKFLOW_URL,
        "observability": settings.OBSERVABILITY_URL,
    }
    
    # Check each service health
    for service_name, service_url in service_urls.items():
        if service_url:
            try:
                import httpx
                start_time = asyncio.get_event_loop().time()
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{service_url}/health")
                    
                end_time = asyncio.get_event_loop().time()
                response_time = (end_time - start_time) * 1000
                
                services[service_name] = ServiceStatus(
                    service=service_name,
                    status="healthy" if response.status_code == 200 else "unhealthy",
                    response_time_ms=response_time
                )
                
            except Exception:
                services[service_name] = ServiceStatus(
                    service=service_name,
                    status="unhealthy",
                    response_time_ms=0.0
                )
        else:
            services[service_name] = ServiceStatus(
                service=service_name,
                status="not_configured",
                response_time_ms=0.0
            )
    
    # Determine overall status
    overall_status = "healthy"
    if db_status != "healthy":
        overall_status = "unhealthy"
    elif any(service.status == "unhealthy" for service in services.values()):
        overall_status = "degraded"
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        service="api-gateway",
        version=settings.VERSION,
        database=db_status,
        memory_usage=memory_usage,
        cpu_usage=cpu_usage,
        services=services
    )


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_database)
):
    """Kubernetes readiness probe endpoint"""
    
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}, 503


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive"}
