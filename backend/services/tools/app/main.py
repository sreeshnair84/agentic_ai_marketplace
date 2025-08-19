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
from .models.database import init_db

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
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue without database for basic functionality
    
    try:
        # Initialize database service (legacy)
        db_service = get_database_service()
        await db_service.init_database()
        logger.info("Database service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database service: {e}")
        # Continue without database for basic functionality
    
    yield
    
    # Shutdown
    logger.info("Shutting down Tools service...")

app = FastAPI(
    title="Tools Service",
    description="""
    Enterprise AI Tools Service with comprehensive tool management and RAG pipeline capabilities.
    
    Features:
    - Dynamic Tools: Enhanced tools for database operations with automated analysis
    - Sample Queries: AI-generated SQL examples for different database patterns
    - Tool Management: Template-based tool creation and instance management
    - RAG Pipelines: Configurable data ingestion and vectorization workflows
    - LangGraph Integration: Workflow orchestration for complex tool chains
    - Multi-format Support: Text, file, and URL data ingestion
    - Vector Search: Semantic search capabilities across ingested data
    
    Tool Types Supported:
    - RAG Pipeline: Retrieval-Augmented Generation with configurable embeddings
    - SQL Agent: Database query generation and execution
    - MCP Client: Model Context Protocol integration
    - Code Interpreter: Multi-language code execution
    - Web Scraper: Configurable web content extraction
    - File Processor: Multi-format document processing
    - API Integration: REST/GraphQL API connectivity
    - Workflow Orchestrator: Complex multi-step workflows
    """,
    version="2.0.0",
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

# Include simple tool management router
try:
    from .api.simple_tool_management import router as simple_tool_management_router
    app.include_router(simple_tool_management_router)
    logger.info("Simple tool management router included successfully")
except ImportError as e:
    logger.warning(f"Could not import simple tool management router: {e}")
except Exception as e:
    logger.error(f"Error including simple tool management router: {e}")

# Include RAG pipeline router
try:
    from .api.rag_pipeline import router as rag_pipeline_router
    app.include_router(rag_pipeline_router, prefix="/rag-pipelines")
    logger.info("RAG pipeline router included successfully")
except ImportError as e:
    logger.warning(f"Could not import RAG pipeline router: {e}")
except Exception as e:
    logger.error(f"Error including RAG pipeline router: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    settings = get_settings()
    
    return {
        "status": "healthy", 
        "service": "tools",
        "version": "2.0.0",
        "features": {
            "mcp_client": True,
            "standard_tools": True,
            "tool_management": True,
            "rag_pipelines": True,
            "langgraph_integration": True,
            "vector_search": True,
            "multi_format_ingestion": True,
            "workflow_orchestration": True,
            "system_tools": settings.ENABLE_SYSTEM_TOOLS
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Tools Service",
        "version": "2.0.0",
        "description": "Enterprise AI Tools Service with comprehensive tool management and RAG pipeline capabilities",
        "endpoints": {
            "tools": "/tools",
            "tool_management": "/tool-management",
            "rag_pipelines": "/rag-pipelines",
            "health": "/health",
            "docs": "/docs"
        },
        "capabilities": {
            "tool_templates": 8,
            "supported_formats": ["text", "pdf", "docx", "csv", "json", "xml"],
            "ingestion_methods": ["text", "file_upload", "web_scraping", "api_extraction", "rss_feed"],
            "embedding_models": ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"],
            "workflow_orchestration": "LangGraph"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
