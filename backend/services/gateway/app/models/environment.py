"""
Pydantic models for Environment Variables
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class EnvironmentCategory(str, Enum):
    LLM = "llm"
    DATABASE = "database"
    API = "api"
    AUTH = "auth"
    SYSTEM = "system"
    INTEGRATION = "integration"

class EnvironmentScope(str, Enum):
    GLOBAL = "global"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class EnvironmentVariableBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: EnvironmentCategory
    is_secret: bool = False
    is_required: bool = False
    scope: EnvironmentScope

class EnvironmentVariableCreate(EnvironmentVariableBase):
    pass

class EnvironmentVariableUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[EnvironmentCategory] = None
    is_secret: Optional[bool] = None
    is_required: Optional[bool] = None
    scope: Optional[EnvironmentScope] = None

class EnvironmentVariableResponse(EnvironmentVariableBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
