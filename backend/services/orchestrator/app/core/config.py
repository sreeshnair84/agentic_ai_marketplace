"""
Configuration settings for the Orchestrator service
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "orchestrator"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/agenticai_orchestrator"
    
    # Redis configuration for task queue
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Model Configuration (Default: Gemini)
    DEFAULT_AI_PROVIDER: str = "gemini"
    DEFAULT_MODEL: str = "gemini-1.5-pro"
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Agent Registry
    AGENTS_SERVICE_URL: str = "http://localhost:8002"
    TOOLS_SERVICE_URL: str = "http://localhost:8003"
    RAG_SERVICE_URL: str = "http://localhost:8004"
    SQLTOOL_SERVICE_URL: str = "http://localhost:8005"
    WORKFLOW_ENGINE_URL: str = "http://localhost:8007"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # Workflow configuration
    MAX_CONCURRENT_WORKFLOWS: int = 100
    WORKFLOW_TIMEOUT_SECONDS: int = 3600  # 1 hour
    TASK_RETRY_ATTEMPTS: int = 3
    TASK_TIMEOUT_SECONDS: int = 300  # 5 minutes
    
    # A2A Protocol configuration
    A2A_PROTOCOL_VERSION: str = "1.0"
    A2A_MESSAGE_TTL_SECONDS: int = 300
    A2A_MAX_RETRIES: int = 3
    
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
