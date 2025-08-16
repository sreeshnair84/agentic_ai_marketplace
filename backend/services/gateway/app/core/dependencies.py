"""
FastAPI dependencies for dependency injection
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Optional
import redis.asyncio as redis
import logging

from .database import get_database
from .config import get_settings
from ..models.user import User
from ..services.auth_service import AuthService

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Redis connection pool
_redis_pool: Optional[redis.ConnectionPool] = None


async def get_redis_pool() -> redis.ConnectionPool:
    """Get Redis connection pool"""
    global _redis_pool
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS
        )
    return _redis_pool


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Get Redis connection"""
    pool = await get_redis_pool()
    redis_client = redis.Redis(connection_pool=pool)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database),
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        
        # Verify and decode JWT token
        payload = auth_service.verify_token(token)
        
        # Check token type
        if payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await auth_service.get_user_by_id(payload.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.isActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.isActive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current admin user"""
    if current_user.role.value.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_user_or_viewer(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current user with at least viewer permissions"""
    allowed_roles = ["ADMIN", "USER", "VIEWER"]
    if current_user.role.value.upper() not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Optional dependency for when user might not be required
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_database),
) -> Optional[User]:
    """Get optional current user (for public endpoints that might have user context)"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database),
) -> str:
    """Verify token and return token string for logout operations"""
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        
        # Just verify the token is valid
        auth_service.verify_token(token)
        
        return token
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
