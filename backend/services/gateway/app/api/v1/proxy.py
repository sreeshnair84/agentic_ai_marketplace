"""
Proxy service for routing requests to backend services
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response
import httpx
import logging
from typing import Dict, Any

from ...core.config import get_settings
from ...core.dependencies import get_current_user, get_optional_user
from ...models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class ProxyService:
    """Service for proxying requests to backend microservices"""
    
    def __init__(self):
        self.settings = get_settings()
        self.service_urls = {
            "orchestrator": self.settings.ORCHESTRATOR_URL,
            "agents": self.settings.AGENTS_URL,
            "tools": self.settings.TOOLS_URL,
            "rag": self.settings.RAG_URL,
            "sqltool": self.settings.SQLTOOL_URL,
            "workflow": self.settings.WORKFLOW_URL,
            "observability": self.settings.OBSERVABILITY_URL,
        }
    
    async def proxy_request(
        self,
        service: str,
        path: str,
        method: str,
        headers: Dict[str, str],
        params: Dict[str, Any] = None,
        body: bytes = None,
        user: User = None
    ) -> Response:
        """Proxy request to backend service"""
        
        if service not in self.service_urls:
            raise HTTPException(status_code=404, detail="Service not found")
        
        target_url = f"{self.service_urls[service]}/api{path}"
        
        # Add user context to headers
        if user:
            headers["X-User-ID"] = user.id
            headers["X-User-Role"] = user.role
            headers["X-User-Email"] = user.email
        
        # Remove authorization header to avoid conflicts
        headers.pop("authorization", None)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=target_url,
                    headers=headers,
                    params=params,
                    content=body
                )
                
                # Return response with original headers and status
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout proxying request to {service}: {target_url}")
            raise HTTPException(status_code=504, detail="Service timeout")
        except httpx.RequestError as e:
            logger.error(f"Error proxying request to {service}: {e}")
            raise HTTPException(status_code=502, detail="Service unavailable")


proxy_service = ProxyService()


@router.api_route(
    "/orchestrator/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_orchestrator(
    path: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    """Proxy requests to orchestrator service"""
    return await proxy_service.proxy_request(
        service="orchestrator",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )


@router.api_route(
    "/agents/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_agents(
    path: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    """Proxy requests to agents service"""
    return await proxy_service.proxy_request(
        service="agents",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )


@router.api_route(
    "/tools/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_tools(
    path: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    """Proxy requests to tools service"""
    return await proxy_service.proxy_request(
        service="tools",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )


@router.api_route(
    "/rag/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_rag(
    path: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    """Proxy requests to RAG service"""
    return await proxy_service.proxy_request(
        service="rag",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )


@router.api_route(
    "/sqltool/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_sqltool(
    path: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    """Proxy requests to SQL tool service"""
    return await proxy_service.proxy_request(
        service="sqltool",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )


@router.api_route(
    "/workflow/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_workflow(
    path: str,
    request: Request,
    user: User = Depends(get_current_user)
):
    """Proxy requests to workflow service"""
    return await proxy_service.proxy_request(
        service="workflow",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )


@router.api_route(
    "/observability/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_observability(
    path: str,
    request: Request,
    user: User = Depends(get_optional_user)  # Optional for monitoring endpoints
):
    """Proxy requests to observability service"""
    return await proxy_service.proxy_request(
        service="observability",
        path=f"/{path}",
        method=request.method,
        headers=dict(request.headers),
        params=dict(request.query_params),
        body=await request.body(),
        user=user
    )
