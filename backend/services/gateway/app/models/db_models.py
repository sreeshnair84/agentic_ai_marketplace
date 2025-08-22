"""
SQLAlchemy database models for the project system
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


# Notification model
class Notification(Base):
    """Notification database model"""
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    message = Column(Text, nullable=False)
    type = Column(String(32), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, nullable=True)


class Project(Base):
    """Project database model"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    tags = Column(ARRAY(String), nullable=False, default=[])
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255))
    updated_by = Column(String(255))
