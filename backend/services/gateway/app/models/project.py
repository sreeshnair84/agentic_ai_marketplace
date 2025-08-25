"""
Project models and schemas
"""

from typing import Optional, List, Union, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, field_serializer, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)
    
    id: Union[str, UUID]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    @field_validator('created_by', 'updated_by', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v: Any) -> Optional[str]:
        """Convert UUID objects to string for created_by and updated_by fields"""
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        if isinstance(v, str):
            return v
        return str(v) if v is not None else None
    
    @field_serializer('created_by', 'updated_by')
    def serialize_user_fields(self, v: Any) -> Optional[str]:
        """Ensure UUID objects are serialized as strings"""
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return str(v)
