"""
Configuration settings for the LCNC Gateway Service
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "LCNC Gateway Service"
    PROJECT_NAME: str = "LCNC Gateway Service"  # Alias for APP_NAME
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"  # Alias for API_V1_PREFIX
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-here-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_HOSTS: str = "*"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://lcnc_user:lcnc_password@localhost:5432/lcnc_platform"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    
    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:3001"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    CORS_ALLOW_HEADERS: str = "*"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: str = ".pdf,.txt,.docx,.xlsx,.csv"
    
    # External Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Session
    SESSION_EXPIRE_MINUTES: int = 60
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_ENABLED: bool = True
    
    # Development
    RELOAD: bool = False
    AUTO_RELOAD: bool = False
    
    # Security Headers
    SECURE_HEADERS: bool = True
    HSTS_MAX_AGE: int = 31536000
    
    # Agent Communication
    AGENT_REGISTRY_URL: str = "http://localhost:8001"
    ORCHESTRATOR_URL: str = "http://localhost:8002"
    AGENTS_URL: str = "http://localhost:8002"  # Same as orchestrator for now
    RAG_SERVICE_URL: str = "http://localhost:8003"
    RAG_URL: str = "http://localhost:8003"  # Alias for RAG_SERVICE_URL
    TOOLS_SERVICE_URL: str = "http://localhost:8004"
    TOOLS_URL: str = "http://localhost:8004"  # Alias for TOOLS_SERVICE_URL
    SQLTOOL_URL: str = "http://localhost:8005"
    WORKFLOW_ENGINE_URL: str = "http://localhost:8006"
    WORKFLOW_URL: str = "http://localhost:8006"  # Alias for WORKFLOW_ENGINE_URL
    OBSERVABILITY_URL: str = "http://localhost:8007"
    
    # Default Admin User
    DEFAULT_ADMIN_EMAIL: str = "admin@lcnc.com"
    DEFAULT_ADMIN_PASSWORD: str = "secret123"
    DEFAULT_ADMIN_FIRST_NAME: str = "Admin"
    DEFAULT_ADMIN_LAST_NAME: str = "User"

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.CORS_ORIGINS_STR, str):
            return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
        return self.CORS_ORIGINS_STR if isinstance(self.CORS_ORIGINS_STR, list) else []

    def get_cors_methods(self) -> List[str]:
        """Get CORS methods as a list"""
        if isinstance(self.CORS_ALLOW_METHODS, str):
            return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",") if method.strip()]
        return self.CORS_ALLOW_METHODS if isinstance(self.CORS_ALLOW_METHODS, list) else []

    def get_cors_headers(self) -> List[str]:
        """Get CORS headers as a list"""
        if isinstance(self.CORS_ALLOW_HEADERS, str):
            return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",") if header.strip()]
        return self.CORS_ALLOW_HEADERS if isinstance(self.CORS_ALLOW_HEADERS, list) else []

    def get_allowed_extensions(self) -> List[str]:
        """Get allowed extensions as a list"""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]
        return self.ALLOWED_EXTENSIONS if isinstance(self.ALLOWED_EXTENSIONS, list) else []


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
