"""
Authentication dependencies for the agents service
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Mock User class for agents service
class MockUser:
    """Mock user class for agents service when auth is not fully implemented"""
    def __init__(self, user_id: str = "system", role: str = "admin"):
        self.id = user_id
        self.role = role
        self.isActive = True


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> MockUser:
    """
    Get current authenticated user - Mock implementation for agents service
    In a production environment, this should validate the token and return real user data
    """
    try:
        # For now, return a mock user since this is an internal service
        # In production, you would validate the JWT token here
        token = credentials.credentials
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Mock validation - accept any non-empty token
        # In production, validate JWT token, check expiration, get user from DB, etc.
        return MockUser()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[MockUser]:
    """Get optional current user"""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None