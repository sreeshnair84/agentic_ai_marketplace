"""
Project models and schemas
"""

from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    is_default: bool = False


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_default: Optional[bool] = None


class Project(ProjectBase):
    """Project response schema"""
    id: Union[str, UUID]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True
