"""
Tools service main application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .api.tools import router as tools_router
# from .api.tools_enhanced import enhanced_router  # Temporarily disabled due to dependency issues
from .api.sample_queries import router as sample_queries_router
from .core.config import get_settings
from .services.database_service import get_database_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Tools service...")
    
    try:
        # Initialize database
        db_service = get_database_service()
        await db_service.init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue without database for basic functionality
    
    yield
    
    # Shutdown
    logger.info("Shutting down Tools service...")

app = FastAPI(
    title="Tools Service",
    description="Tool execution and MCP integration service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tools_router)
# app.include_router(enhanced_router)  # Temporarily disabled 
app.include_router(sample_queries_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    settings = get_settings()
    
    return {
        "status": "healthy", 
        "service": "tools",
        "version": "1.0.0",
        "features": {
            "mcp_client": True,
            "standard_tools": True,
            "system_tools": settings.ENABLE_SYSTEM_TOOLS
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Tools Service",
        "version": "1.0.0",
        "description": "Tool execution and MCP integration service",
        "endpoints": {
            "tools": "/tools",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
