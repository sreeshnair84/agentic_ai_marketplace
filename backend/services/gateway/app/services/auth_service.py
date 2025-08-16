"""
Authentication service implementation
"""

import jwt
from jwt.exceptions import InvalidTokenError
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, status
import uuid

from ..core.config import get_settings
from ..models.user import (
    User, UserCreate, LoginRequest, LoginResponse, 
    TokenPayload, RefreshTokenRequest, RefreshTokenResponse,
    OAuthProvider, UserRole, UserUpdate
)
from ..models.database.user import UserDB, RefreshTokenDB, UserSessionDB


class AuthService:
    """Service for handling authentication and JWT tokens"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self, 
        user_id: str,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            payload, 
            self.settings.JWT_SECRET_KEY, 
            algorithm=self.settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            payload, 
            self.settings.JWT_SECRET_KEY, 
            algorithm=self.settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenPayload:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.settings.JWT_SECRET_KEY, 
                algorithms=[self.settings.JWT_ALGORITHM]
            )
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(
        self, 
        username_or_email: str, 
        password: str
    ) -> Optional[Tuple[str, str, User]]:
        """Authenticate a user with username/email and password"""
        
        # Try to find user by email first, then username - use tuple query for immediate evaluation
        user_query = select(
            UserDB.id, UserDB.email, UserDB.username, UserDB.first_name, UserDB.last_name,
            UserDB.hashed_password, UserDB.role, UserDB.is_active, UserDB.is_verified,
            UserDB.created_at, UserDB.updated_at, UserDB.last_login_at,
            UserDB.provider, UserDB.avatar_url, UserDB.selected_project_id
        ).where(
            (UserDB.email == username_or_email) | 
            (UserDB.username == username_or_email)
        )
        result = await self.db.execute(user_query)
        user_row = result.first()
        
        if not user_row:
            return None
        
        # Extract values from row
        (user_id, email, username, first_name, last_name, hashed_password, 
         role, is_active, is_verified, created_at, updated_at, last_login_at,
         provider, avatar_url, selected_project_id) = user_row
        
        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated"
            )
        
        if not self.verify_password(password, hashed_password):
            return None
        
        # Update last login
        await self.update_last_login(user_id)
        
        # Create tokens
        access_token = self.create_access_token(
            user_id=str(user_id),
            email=email,
            role=role
        )
        
        refresh_token = self.create_refresh_token(str(user_id))
        
        # Store refresh token in database
        await self.store_refresh_token(user_id, refresh_token)
        
        # Convert to Pydantic model with manual field mapping
        user = User(
            id=str(user_id),
            email=email,
            username=username,
            firstName=first_name,
            lastName=last_name,
            role=UserRole(role),
            isActive=is_active,
            isVerified=is_verified,
            createdAt=created_at,
            updatedAt=updated_at,
            lastLoginAt=last_login_at,
            provider=OAuthProvider(provider) if provider else OAuthProvider.LOCAL,
            avatarUrl=avatar_url,
            selectedProjectId=str(selected_project_id) if selected_project_id else None
        )
        
        return access_token, refresh_token, user
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        
        # Check if user already exists by email
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username is taken
        existing_username = await self.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        hashed_password = self.get_password_hash(user_data.password)
        
        user_db = UserDB(
            id=uuid.uuid4(),
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.firstName,
            last_name=user_data.lastName,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
            is_verified=False,
            provider="local"
        )
        
        self.db.add(user_db)
        await self.db.commit()
        await self.db.refresh(user_db)
        
        # Convert to Pydantic model - access fields immediately after refresh
        user = User(
            id=str(user_db.id),
            email=str(user_db.email),
            username=str(user_db.username),
            firstName=str(user_db.first_name) if user_db.first_name is not None else None,
            lastName=str(user_db.last_name) if user_db.last_name is not None else None,
            role=UserRole(str(user_db.role)),
            isActive=bool(user_db.is_active),
            isVerified=bool(user_db.is_verified),
            createdAt=datetime.now(),  # Use current time for new user
            updatedAt=datetime.now(),  # Use current time for new user
            lastLoginAt=None,  # New user, no login yet
            provider=OAuthProvider.LOCAL,
            avatarUrl=str(user_db.avatar_url) if user_db.avatar_url is not None else None,
            selectedProjectId=str(user_db.selected_project_id) if user_db.selected_project_id is not None else None
        )
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        
        query = select(UserDB).where(UserDB.id == uuid.UUID(user_id))
        result = await self.db.execute(query)
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            return None
        
        user = User(
            id=str(user_db.id),
            email=str(user_db.email),
            username=str(user_db.username),
            firstName=str(user_db.first_name) if user_db.first_name is not None else None,
            lastName=str(user_db.last_name) if user_db.last_name is not None else None,
            role=UserRole(str(user_db.role)),
            isActive=bool(user_db.is_active),
            isVerified=bool(user_db.is_verified),
            createdAt=datetime.now(),  # Use current time as fallback
            updatedAt=datetime.now(),  # Use current time as fallback  
            lastLoginAt=None,  # Default to None
            provider=OAuthProvider(str(user_db.provider)) if user_db.provider is not None else OAuthProvider.LOCAL,
            avatarUrl=str(user_db.avatar_url) if user_db.avatar_url is not None else None,
            selectedProjectId=str(user_db.selected_project_id) if user_db.selected_project_id is not None else None
        )
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email"""
        
        query = select(UserDB).where(UserDB.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[UserDB]:
        """Get user by username"""
        
        query = select(UserDB).where(UserDB.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update user information"""
        
        # Get existing user
        query = select(UserDB).where(UserDB.id == uuid.UUID(user_id))
        result = await self.db.execute(query)
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields that are provided
        update_data = {}
        if user_update.email is not None:
            update_data["email"] = user_update.email
        if user_update.username is not None:
            update_data["username"] = user_update.username
        if user_update.firstName is not None:
            update_data["first_name"] = user_update.firstName
        if user_update.lastName is not None:
            update_data["last_name"] = user_update.lastName
        if user_update.role is not None:
            update_data["role"] = user_update.role.value
        if user_update.isActive is not None:
            update_data["is_active"] = user_update.isActive
        if user_update.selectedProjectId is not None:
            # Convert to UUID if string provided
            if isinstance(user_update.selectedProjectId, str):
                update_data["selected_project_id"] = uuid.UUID(user_update.selectedProjectId)
            else:
                update_data["selected_project_id"] = user_update.selectedProjectId
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            query = update(UserDB).where(
                UserDB.id == uuid.UUID(user_id)
            ).values(**update_data)
            
            await self.db.execute(query)
            await self.db.commit()
        
        # Return updated user
        updated_user = await self.get_user_by_id(user_id)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found after update"
            )
        return updated_user
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List users with pagination"""
        
        query = select(
            UserDB.id, UserDB.email, UserDB.username, UserDB.first_name, UserDB.last_name,
            UserDB.role, UserDB.is_active, UserDB.is_verified,
            UserDB.created_at, UserDB.updated_at, UserDB.last_login_at,
            UserDB.provider, UserDB.avatar_url, UserDB.selected_project_id
        ).offset(skip).limit(limit).order_by(UserDB.created_at.desc())
        
        result = await self.db.execute(query)
        user_rows = result.fetchall()
        
        users = []
        for row in user_rows:
            (user_id, email, username, first_name, last_name,
             role, is_active, is_verified, created_at, updated_at, last_login_at,
             provider, avatar_url, selected_project_id) = row
            
            user = User(
                id=str(user_id),
                email=email,
                username=username,
                firstName=first_name,
                lastName=last_name,
                role=UserRole(role),
                isActive=is_active,
                isVerified=is_verified,
                createdAt=created_at,
                updatedAt=updated_at,
                lastLoginAt=last_login_at,
                provider=OAuthProvider(provider) if provider else OAuthProvider.LOCAL,
                avatarUrl=avatar_url,
                selectedProjectId=str(selected_project_id) if selected_project_id else None
            )
            users.append(user)
        
        return users
    
    async def refresh_access_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refresh access token using refresh token"""
        
        # Verify refresh token
        try:
            payload = self.verify_token(refresh_token)
            if payload.type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        query = select(RefreshTokenDB).where(
            RefreshTokenDB.token_hash == token_hash,
            RefreshTokenDB.is_revoked == False,
            RefreshTokenDB.expires_at > datetime.utcnow()
        )
        result = await self.db.execute(query)
        stored_token = result.scalar_one_or_none()
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or expired"
            )
        
        # Get user
        user = await self.get_user_by_id(payload.sub)
        if not user or not user.isActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        new_access_token = self.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value
        )
        
        new_refresh_token = self.create_refresh_token(user.id)
        
        # Revoke old refresh token and store new one
        await self.revoke_refresh_token(token_hash)
        await self.store_refresh_token(uuid.UUID(user.id), new_refresh_token)
        
        return RefreshTokenResponse(
            auth_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def store_refresh_token(self, user_id: uuid.UUID, refresh_token: str):
        """Store refresh token in database"""
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token_db = RefreshTokenDB(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        self.db.add(refresh_token_db)
        await self.db.commit()
    
    async def revoke_refresh_token(self, token_hash: str):
        """Revoke a refresh token"""
        
        query = update(RefreshTokenDB).where(
            RefreshTokenDB.token_hash == token_hash
        ).values(is_revoked=True)
        
        await self.db.execute(query)
        await self.db.commit()
    
    async def logout_user(self, access_token: str):
        """Logout user by revoking their tokens"""
        
        try:
            payload = self.verify_token(access_token)
            user_id = uuid.UUID(payload.sub)
            
            # Revoke all refresh tokens for the user
            query = update(RefreshTokenDB).where(
                RefreshTokenDB.user_id == user_id
            ).values(is_revoked=True)
            
            await self.db.execute(query)
            await self.db.commit()
            
        except HTTPException:
            # Token is invalid, but logout should still succeed
            pass
    
    async def update_last_login(self, user_id: uuid.UUID):
        """Update user's last login timestamp"""
        
        query = update(UserDB).where(
            UserDB.id == user_id
        ).values(last_login_at=datetime.utcnow())
        
        await self.db.execute(query)
        await self.db.commit()
    
    async def cleanup_expired_tokens(self):
        """Clean up expired refresh tokens"""
        
        query = delete(RefreshTokenDB).where(
            RefreshTokenDB.expires_at < datetime.utcnow()
        )
        
        await self.db.execute(query)
        await self.db.commit()
