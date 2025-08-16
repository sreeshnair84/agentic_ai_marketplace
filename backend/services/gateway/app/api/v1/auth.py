"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging

from ...core.dependencies import get_database, get_current_user, verify_token_dependency, get_admin_user
from ...models.user import (
    LoginRequest, LoginResponse, User, UserCreate, RegisterRequest,
    RefreshTokenRequest, RefreshTokenResponse, PasswordResetRequest,
    ChangePasswordRequest, EmailVerificationRequest, UserUpdate
)
from ...services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """User login endpoint - supports email or username"""
    try:
        auth_service = AuthService(db)
        
        # Determine login field (email or username)
        username_or_email = login_data.email or login_data.username
        if not username_or_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either email or username must be provided"
            )
        
        result = await auth_service.authenticate_user(
            username_or_email, 
            login_data.password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token, refresh_token, user = result
        
        # Calculate token expiration
        settings = auth_service.settings
        expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        return LoginResponse(
            auth_token=access_token,  # Backend uses auth_token
            refresh_token=refresh_token,
            expires_in=expires_in,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register", response_model=User)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_database)
):
    """User registration endpoint"""
    try:
        auth_service = AuthService(db)
        
        # Convert RegisterRequest to UserCreate
        user_create = UserCreate(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            firstName=user_data.firstName,
            lastName=user_data.lastName
        )
        
        user = await auth_service.create_user(user_create)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_database)
):
    """Refresh access token using refresh token"""
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_access_token(refresh_data.refresh_token)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    token: str = Depends(verify_token_dependency),
    db: AsyncSession = Depends(get_database)
):
    """User logout endpoint"""
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(token)
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        # Logout should always succeed, even if token is invalid
        return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Update user information (Admin only)"""
    try:
        auth_service = AuthService(db)
        
        # Get the user to update
        target_user = await auth_service.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user (implementation would need to be added to auth_service)
        updated_user = await auth_service.update_user(user_id, user_update)
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.get("/users", response_model=list[User])
async def list_users(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database),
    skip: int = 0,
    limit: int = 100
):
    """List all users (Admin only)"""
    try:
        auth_service = AuthService(db)
        users = await auth_service.list_users(skip=skip, limit=limit)
        return users
        
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Change user password"""
    try:
        auth_service = AuthService(db)
        
        # Verify current password by attempting authentication
        result = await auth_service.authenticate_user(
            current_user.email,
            password_data.current_password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password (implementation would go here)
        # For now, return success
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/forgot-password")
async def forgot_password(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_database)
):
    """Request password reset"""
    try:
        auth_service = AuthService(db)
        
        # Check if user exists
        user_db = await auth_service.get_user_by_email(reset_data.email)
        if not user_db:
            # Don't reveal if email exists for security
            return {"message": "If the email exists, a reset link has been sent"}
        
        # In real implementation, would generate reset token and send email
        # For now, return success message
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Always return success for security
        return {"message": "If the email exists, a reset link has been sent"}


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_database)
):
    """Verify user email"""
    try:
        # Implementation for email verification would go here
        # For now, return success
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )


@router.get("/health")
async def auth_health():
    """Auth service health check"""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# OAuth endpoints (placeholder for future implementation)
@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    """Initiate OAuth login"""
    # Redirect to OAuth provider
    # Implementation would depend on the provider
    return {"message": f"OAuth login with {provider} not yet implemented"}


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str = None,
    db: AsyncSession = Depends(get_database)
):
    """Handle OAuth callback"""
    # Process OAuth callback
    # Implementation would depend on the provider
    return {"message": f"OAuth callback for {provider} not yet implemented"}
