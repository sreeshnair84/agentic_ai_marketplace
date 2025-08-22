"""
Main application entrypoint for the API Gateway
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
import traceback
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import init_db
from .api.v1.auth import router as auth_router
from .api.v1.proxy import router as proxy_router
from .api.v1.health import router as health_router
from .api.v1.projects import router as projects_router
from .api.v1.notification import router as notification_router
from .api.v1.stats import router as stats_router
from .api.v1.metadata import router as metadata_router
from .api.v1.memory import router as memory_router
from .api.v1.monitoring import router as monitoring_router
from .api.v1.llm_models import router as llm_models_router
from .api.v1.embedding_models import router as embedding_models_router
from .api.v1.default_chat import router as default_chat_router
from .api.v1.a2a_chat import router as a2a_chat_router
from .api.sample_queries import router as sample_queries_router
from .api.agents import router as agents_router
from .api.tools import router as tools_router
from .api.workflows import router as workflows_router
from .api.rag import router as rag_router
from .api.mcp_registry import router as mcp_registry_router
from .api.mcp_gateway import router as mcp_gateway_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting API Gateway...")
    settings = get_settings()
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    settings = get_settings()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API Gateway for Agentic AI Acceleration",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )
    
    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS.split(",") if isinstance(settings.ALLOWED_HOSTS, str) else settings.ALLOWED_HOSTS
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # V1 API routers (preferred)
    app.include_router(
        auth_router, 
        prefix=f"{settings.API_V1_STR}/auth", 
        tags=["authentication"]
    )
    app.include_router(
        proxy_router, 
        prefix=f"{settings.API_V1_STR}/services", 
        tags=["services"]
    )
    app.include_router(
        health_router, 
        prefix="", 
        tags=["health"]
    )
    app.include_router(
        projects_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["projects"]
    )
    app.include_router(
        notification_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["notifications"]
    )
    app.include_router(
        stats_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["statistics"]
    )
    app.include_router(
        metadata_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["metadata"]
    )
    app.include_router(
        memory_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["memory"]
    )
    app.include_router(
        monitoring_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["monitoring"]
    )
    app.include_router(
        llm_models_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["llm-models"]
    )
    app.include_router(
        embedding_models_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["embedding-models"]
    )
    app.include_router(
        default_chat_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["default-chat"]
    )
    app.include_router(
        a2a_chat_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["a2a-chat"]
    )
    app.include_router(
        agents_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["agents"]
    )
    app.include_router(
        tools_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["tools"]
    )
    app.include_router(
        workflows_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["workflows"]
    )
    app.include_router(
        rag_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["rag"]
    )
    app.include_router(
        mcp_registry_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["mcp-registry"]
    )
    app.include_router(
        mcp_gateway_router, 
        prefix=f"{settings.API_V1_STR}", 
        tags=["mcp-gateway"]
    )
    
    # Legacy API compatibility routers
    app.include_router(
        sample_queries_router, 
        prefix="/api", 
        tags=["sample-queries-legacy"]
    )
    app.include_router(
        agents_router, 
        prefix="/api", 
        tags=["agents-legacy"]
    )
    app.include_router(
        tools_router, 
        prefix="/api", 
        tags=["tools-legacy"]
    )
    app.include_router(
        workflows_router, 
        prefix="/api", 
        tags=["workflows-legacy"]
    )
    app.include_router(
        rag_router, 
        prefix="/api", 
        tags=["rag-legacy"]
    )
    app.include_router(
        mcp_registry_router, 
        prefix="/api", 
        tags=["mcp-registry-legacy"]
    )
    app.include_router(
        mcp_gateway_router, 
        prefix="/api", 
        tags=["mcp-gateway-legacy"]
    )
    
    # Global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": exc.errors(),
                "body": exc.body
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error for {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error for {request.url}: {exc}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Agentic AI Acceleration API Gateway",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs"
        }
    
    return app


# Create application instance
app = create_application()