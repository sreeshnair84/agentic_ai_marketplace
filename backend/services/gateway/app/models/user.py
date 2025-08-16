"""
User models and schemas
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    VIEWER = "VIEWER"


class OAuthProvider(str, Enum):
    LOCAL = "local"
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    firstName: Optional[str] = None  # Changed from first_name to match frontend
    lastName: Optional[str] = None   # Changed from last_name to match frontend
    role: UserRole = UserRole.VIEWER
    isActive: bool = True           # Changed from is_active to match frontend


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    username: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[UserRole] = None
    isActive: Optional[bool] = None
    selectedProjectId: Optional[str] = None


class UserProjectPreference(BaseModel):
    """User project preference update schema"""
    selectedProjectId: str


class User(UserBase):
    """User response schema"""
    id: str
    createdAt: datetime        # Changed from created_at to match frontend
    updatedAt: datetime        # Changed from updated_at to match frontend
    lastLoginAt: Optional[datetime] = None  # Changed from last_login_at to match frontend
    provider: Optional[OAuthProvider] = OAuthProvider.LOCAL
    avatarUrl: Optional[str] = None
    isVerified: bool = False
    selectedProjectId: Optional[str] = None  # User's selected project
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserSession(BaseModel):
    """User session schema"""
    id: str
    userId: str
    expiresAt: datetime
    createdAt: datetime
    lastActivityAt: datetime
    deviceId: Optional[str] = None
    userAgent: Optional[str] = None
    ipAddress: Optional[str] = None
    location: Optional[str] = None
    isActive: bool = True


class LoginRequest(BaseModel):
    """Login request schema - supports both email and username"""
    email: Optional[str] = None      # Support email login
    username: Optional[str] = None   # Support username login  
    password: str


class LoginResponse(BaseModel):
    """Login response schema - match frontend expectations"""
    auth_token: str        # Backend uses auth_token, frontend maps to access_token
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr
    username: str
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # user ID
    exp: int  # expiration time
    iat: int  # issued at
    jti: str  # JWT ID
    type: str  # token type (access/refresh)
    email: Optional[str] = None
    role: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    auth_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    token: str


class OAuthLoginRequest(BaseModel):
    """OAuth login request"""
    provider: OAuthProvider
    code: str
    redirect_uri: Optional[str] = None
    state: Optional[str] = None


class OAuthUserInfo(BaseModel):
    """OAuth user information"""
    id: str
    email: str
    name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: OAuthProvider


class AuthErrorResponse(BaseModel):
    """Authentication error response"""
    error: str
    error_description: str
    error_code: Optional[str] = None
