"""
Configuration settings for the Agents service
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "agents"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8002
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/agenticai_agents"
    
    # Redis configuration for agent state
    REDIS_URL: str = "redis://localhost:6379/2"
    
    # AI Provider configurations
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Agent configuration
    MAX_AGENTS: int = 1000
    AGENT_TIMEOUT_SECONDS: int = 300
    MAX_CONCURRENT_TASKS: int = 50
    
    # A2A Protocol configuration
    A2A_PROTOCOL_VERSION: str = "1.0"
    A2A_WEBSOCKET_PORT: int = 9001
    A2A_MESSAGE_TTL_SECONDS: int = 300
    A2A_MAX_MESSAGE_SIZE: int = 1048576  # 1MB
    
    # Service URLs
    ORCHESTRATOR_URL: str = "http://localhost:8001"
    TOOLS_URL: str = "http://localhost:8003"
    RAG_URL: str = "http://localhost:8004"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # Observability
    ENABLE_TRACING: bool = True
    JAEGER_ENDPOINT: str = "http://localhost:14268/api/traces"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings instance (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
