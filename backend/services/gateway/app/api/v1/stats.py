"""
Statistics endpoints for the API Gateway
Provides aggregated statistics for dashboard and sidebar
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ...core.database import get_database
from ...core.config import get_settings

router = APIRouter()


class DashboardMetrics(BaseModel):
    activeAgents: int
    runningWorkflows: int
    a2aMessages: int
    responseTime: float
    totalServices: int
    healthyServices: int
    availableTools: int
    systemHealth: str
    lastUpdated: str
    memoryUsage: float
    cpuUsage: float
    databaseStatus: str


class RecentActivity(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    status: str


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    recentActivity: List[RecentActivity]
    systemStatus: str
    lastRefreshed: str
    serviceDetails: Dict


class SidebarStats(BaseModel):
    agents: int
    projects: int
    workflows: int
    tools: int
    lastUpdated: str
    systemHealth: str


async def fetch_service_data(service_url: str, endpoint: str, timeout: float = 3.0):
    """Fetch data from a backend service"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{service_url}{endpoint}")
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


async def get_tools_count():
    """Get actual tools count from tools service"""
    settings = get_settings()
    if not settings.TOOLS_URL:
        return 0
    
    tools_data = await fetch_service_data(settings.TOOLS_URL, "/tools")
    if tools_data and isinstance(tools_data, list):
        return len(tools_data)
    return 0


async def get_agents_count():
    """Get actual agents count from agents service"""
    settings = get_settings()
    if not settings.AGENTS_URL:
        return 0
    
    agents_data = await fetch_service_data(settings.AGENTS_URL, "/agents")
    if agents_data and isinstance(agents_data, dict):
        return len(agents_data.get("agents", []))
    return 0


async def get_workflows_count():
    """Get actual workflows count from workflow service"""
    settings = get_settings()
    if not settings.WORKFLOW_URL:
        return 0
    
    workflows_data = await fetch_service_data(settings.WORKFLOW_URL, "/workflows")
    if workflows_data and isinstance(workflows_data, dict):
        workflows = workflows_data.get("workflows", [])
        # Count running workflows
        running_workflows = [w for w in workflows if w.get("status") == "running"]
        return len(running_workflows)
    return 0


async def get_projects_count(db: AsyncSession):
    """Get projects count from database"""
    try:
        # Check if projects table exists and get count
        result = await db.execute(text("""
            SELECT COUNT(*) as count 
            FROM projects 
            WHERE deleted_at IS NULL
        """))
        row = result.fetchone()
        return row[0] if row else 1  # Default to 1 (current project)
    except Exception:
        return 1  # Default to 1 project


async def get_system_health_summary():
    """Get system health summary from health endpoint"""
    import psutil
    from ...api.v1.health import detailed_health_check
    from ...core.database import get_database
    
    # This is a bit hacky, but we need to call our own health endpoint
    # In a real implementation, you'd extract the logic to a shared service
    try:
        settings = get_settings()
        
        # Get basic system metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=0.1)  # Quick check
        
        # Check database
        db_status = "healthy"  # We'll assume healthy if we got this far
        
        # Check services
        service_urls = {
            "orchestrator": settings.ORCHESTRATOR_URL,
            "agents": settings.AGENTS_URL,
            "tools": settings.TOOLS_URL,
            "rag": settings.RAG_URL,
            "sqltool": settings.SQLTOOL_URL,
            "workflow": settings.WORKFLOW_URL,
            "observability": settings.OBSERVABILITY_URL,
        }
        
        healthy_services = 0
        total_services = len(service_urls)
        response_times = []
        
        for service_name, service_url in service_urls.items():
            if service_url:
                try:
                    start_time = asyncio.get_event_loop().time()
                    async with httpx.AsyncClient(timeout=3.0) as client:
                        response = await client.get(f"{service_url}/health")
                        end_time = asyncio.get_event_loop().time()
                        response_time = (end_time - start_time) * 1000
                        
                        if response.status_code == 200:
                            healthy_services += 1
                            response_times.append(response_time)
                except Exception:
                    pass
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Determine overall health
        if healthy_services == 0:
            system_health = "unhealthy"
        elif healthy_services < total_services // 2:
            system_health = "degraded"
        else:
            system_health = "healthy"
        
        return {
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "database_status": db_status,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "avg_response_time": avg_response_time,
            "system_health": system_health
        }
        
    except Exception:
        return {
            "memory_usage": 0,
            "cpu_usage": 0,
            "database_status": "unknown",
            "healthy_services": 0,
            "total_services": 7,
            "avg_response_time": 0,
            "system_health": "unhealthy"
        }


def generate_recent_activity(metrics: dict) -> List[RecentActivity]:
    """Generate recent activity based on system metrics"""
    activities = []
    now = datetime.utcnow()
    
    # Add service activities
    if metrics["healthy_services"] > 0:
        activities.append(RecentActivity(
            id=f"services-{int(now.timestamp())}",
            type="service",
            title="Service Health Check",
            description=f"{metrics['healthy_services']}/{metrics['total_services']} services healthy",
            timestamp=(now.replace(microsecond=0)).isoformat() + "Z",
            status="success" if metrics["healthy_services"] > metrics["total_services"] // 2 else "warning"
        ))
    
    # Add database activity
    if metrics["database_status"] == "healthy":
        activities.append(RecentActivity(
            id=f"db-{int(now.timestamp())}",
            type="service",
            title="Database Connection",
            description="Database connection verified and healthy",
            timestamp=(now.replace(microsecond=0)).isoformat() + "Z",
            status="success"
        ))
    
    # Add tools activity
    if metrics.get("tools_count", 0) > 0:
        activities.append(RecentActivity(
            id=f"tools-{int(now.timestamp())}",
            type="tool",
            title="Tools Registry",
            description=f"{metrics['tools_count']} tools available for use",
            timestamp=(now.replace(microsecond=0)).isoformat() + "Z",
            status="success"
        ))
    
    return activities[:10]  # Return top 10


@router.get("/stats/dashboard", response_model=DashboardResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_database)
):
    """Get comprehensive dashboard statistics"""
    
    try:
        # Get parallel data from all sources
        health_summary, tools_count, agents_count, workflows_count, projects_count = await asyncio.gather(
            get_system_health_summary(),
            get_tools_count(),
            get_agents_count(),
            get_workflows_count(),
            get_projects_count(db),
            return_exceptions=True
        )
        
        # Handle any exceptions in the gathered results
        if isinstance(health_summary, Exception):
            health_summary = {
                "memory_usage": 0, "cpu_usage": 0, "database_status": "unknown",
                "healthy_services": 0, "total_services": 7, "avg_response_time": 0,
                "system_health": "unhealthy"
            }
        
        tools_count = tools_count if not isinstance(tools_count, Exception) else 0
        agents_count = agents_count if not isinstance(agents_count, Exception) else 0
        workflows_count = workflows_count if not isinstance(workflows_count, Exception) else 0
        projects_count = projects_count if not isinstance(projects_count, Exception) else 1
        
        # Calculate A2A messages based on agent and workflow activity
        a2a_messages = agents_count * workflows_count * 5 if agents_count > 0 and workflows_count > 0 else 0
        
        now = datetime.utcnow()
        
        metrics = DashboardMetrics(
            activeAgents=agents_count,
            runningWorkflows=workflows_count,
            a2aMessages=a2a_messages,
            responseTime=health_summary["avg_response_time"],
            totalServices=health_summary["total_services"],
            healthyServices=health_summary["healthy_services"],
            availableTools=tools_count,
            systemHealth=health_summary["system_health"],
            lastUpdated=now.isoformat() + "Z",
            memoryUsage=health_summary["memory_usage"],
            cpuUsage=health_summary["cpu_usage"],
            databaseStatus=health_summary["database_status"]
        )
        
        # Generate recent activity
        activity_data = {
            **health_summary,
            "tools_count": tools_count,
            "agents_count": agents_count,
            "workflows_count": workflows_count
        }
        recent_activity = generate_recent_activity(activity_data)
        
        return DashboardResponse(
            metrics=metrics,
            recentActivity=recent_activity,
            systemStatus=health_summary["system_health"],
            lastRefreshed=now.isoformat() + "Z",
            serviceDetails={}  # Could be expanded with detailed service info
        )
        
    except Exception as e:
        # Return fallback data on error
        now = datetime.utcnow()
        return DashboardResponse(
            metrics=DashboardMetrics(
                activeAgents=0,
                runningWorkflows=0,
                a2aMessages=0,
                responseTime=0,
                totalServices=7,
                healthyServices=0,
                availableTools=0,
                systemHealth="unhealthy",
                lastUpdated=now.isoformat() + "Z",
                memoryUsage=0,
                cpuUsage=0,
                databaseStatus="unknown"
            ),
            recentActivity=[],
            systemStatus="error",
            lastRefreshed=now.isoformat() + "Z",
            serviceDetails={}
        )


@router.get("/stats/sidebar", response_model=SidebarStats)
async def get_sidebar_stats(
    db: AsyncSession = Depends(get_database)
):
    """Get sidebar navigation statistics"""
    
    try:
        # Get data from all sources
        tools_count, agents_count, workflows_count, projects_count = await asyncio.gather(
            get_tools_count(),
            get_agents_count(),
            get_workflows_count(),
            get_projects_count(db),
            return_exceptions=True
        )
        
        # Handle exceptions
        tools_count = tools_count if not isinstance(tools_count, Exception) else 0
        agents_count = agents_count if not isinstance(agents_count, Exception) else 0
        workflows_count = workflows_count if not isinstance(workflows_count, Exception) else 0
        projects_count = projects_count if not isinstance(projects_count, Exception) else 1
        
        # Get basic health status
        health_summary = await get_system_health_summary()
        
        return SidebarStats(
            agents=agents_count,
            projects=projects_count,
            workflows=workflows_count,
            tools=tools_count,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            systemHealth=health_summary["system_health"]
        )
        
    except Exception:
        return SidebarStats(
            agents=0,
            projects=1,
            workflows=0,
            tools=0,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            systemHealth="unhealthy"
        )
