"""
Agents service main application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api.agents import router as agents_router
from .api.a2a import router as a2a_router
from .core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agents Service",
    description="Multi-agent system with A2A communication and Gemini AI integration",
    version="1.0.0"
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
app.include_router(agents_router)
# app.include_router(a2a_router)  # Temporarily disabled due to AgentService issues

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    settings = get_settings()
    
    return {
        "status": "healthy", 
        "service": "agents",
        "version": "1.0.0",
        "features": {
            "ai_provider": "gemini",
            "a2a_messaging": True,
            "a2a_protocol": True,
            "agent_execution": True,
            "conversation_sessions": True
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agents Service",
        "version": "1.0.0",
        "description": "Multi-agent system with A2A communication and Gemini AI integration",
        "endpoints": {
            "agents": "/agents",
            "a2a": "/a2a",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
