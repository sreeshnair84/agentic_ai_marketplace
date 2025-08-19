"""
FastAPI application for the Orchestrator service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import init_db
from .api.v1 import workflows, agents, tasks
from .api import health, a2a

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
    logger.info("Starting Orchestrator service...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Orchestrator service...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    settings = get_settings()
    
    app = FastAPI(
        title="AgenticAI Orchestrator Service",
        description="Multi-Agent Workflow Orchestration Service with A2A Protocol Support",
        version="1.0.0",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
    
    # A2A Protocol routes
    app.include_router(a2a.router, prefix="/a2a", tags=["a2a"])
    
    @app.get("/")
    async def root():
        return {
            "service": "orchestrator",
            "version": "1.0.0",
            "status": "running",
            "protocols": ["HTTP", "A2A", "JSON-RPC 2.0"],
            "description": "AgenticAI Multi-Agent Orchestrator with A2A Protocol Support"
        }
    
    return app


app = create_application()
