"""
Configuration settings for the Tools service
"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    SERVICE_NAME: str = "tools"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/lcnc_tools"
    
    # Redis configuration for tool caching
    REDIS_URL: str = "redis://localhost:6379/3"
    
    # MCP Configuration
    MCP_SERVERS: Dict[str, str] = {
        "filesystem": "mcp-server-filesystem",
        "git": "mcp-server-git",
        "postgresql": "mcp-server-postgresql",
        "sqlite": "mcp-server-sqlite",
        "web-search": "mcp-server-web-search",
    }
    
    # Tool execution configuration
    MAX_EXECUTION_TIME: int = 300  # 5 minutes
    MAX_CONCURRENT_EXECUTIONS: int = 100
    SANDBOX_ENABLED: bool = True
    ALLOWED_DOMAINS: List[str] = ["*"]  # For web tools
    
    # File handling
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    TEMP_DIR: str = "/tmp/lcnc-tools"
    
    # Standard tools configuration
    ENABLE_WEB_TOOLS: bool = True
    ENABLE_FILE_TOOLS: bool = True
    ENABLE_DATA_TOOLS: bool = True
    ENABLE_SYSTEM_TOOLS: bool = False  # Disabled by default for security
    
    # Service URLs
    ORCHESTRATOR_URL: str = "http://localhost:8001"
    AGENTS_URL: str = "http://localhost:8002"
    
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
