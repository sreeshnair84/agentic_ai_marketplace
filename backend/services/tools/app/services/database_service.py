"""
Database service for Tools service
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
import logging
import os

from ..models.database import Base, ToolTemplate, ToolTemplateField, ToolInstance, Model
from ..models.tools import (
    ToolTemplateResponse, ToolInstanceResponse, LLMModelResponse, EmbeddingModelResponse
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for tool management"""
    
    def __init__(self):
        # Database URL from environment - use the main platform database
        database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://agenticai_user:agenticai_password@postgres:5432/agenticai_platform")
        
        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            pool_size=10,
            max_overflow=20
        )
        
        # Create session factory
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self):
        """Get database session - async generator for dependency injection"""
        async with self.SessionLocal() as session:
            yield session
    
    async def init_database(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # Tool Template methods
    async def get_tool_templates(
        self, 
        project_tags: Optional[List[str]] = None, 
        category: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[ToolTemplateResponse]:
        """Get tool templates with optional filtering"""
        
        async with self.SessionLocal() as session:
            query = select(ToolTemplate).options(selectinload(ToolTemplate.fields))
            
            # Apply filters
            filters = []
            if is_active is not None:
                filters.append(ToolTemplate.is_active == is_active)
            if category:
                filters.append(ToolTemplate.category == category)
            if project_tags:
                # Filter by project tags - tool must have at least one matching tag
                filters.append(ToolTemplate.project_tags.op('&&')(project_tags))
            
            if filters:
                query = query.where(and_(*filters))
            
            result = await session.execute(query)
            templates = result.scalars().all()
            
            return [ToolTemplateResponse.model_validate(template) for template in templates]
    
    async def get_tool_template(self, template_id: str) -> Optional[ToolTemplateResponse]:
        """Get tool template by ID"""
        
        async with self.SessionLocal() as session:
            query = select(ToolTemplate).options(selectinload(ToolTemplate.fields)).where(
                ToolTemplate.id == template_id
            )
            result = await session.execute(query)
            template = result.scalar_one_or_none()
            
            return ToolTemplateResponse.model_validate(template) if template else None
    
    # Tool Instance methods
    async def get_tool_instances(
        self,
        project_tags: Optional[List[str]] = None,
        template_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ToolInstanceResponse]:
        """Get tool instances with optional filtering"""
        
        async with self.SessionLocal() as session:
            query = select(ToolInstance).options(selectinload(ToolInstance.template))
            
            # Apply filters
            filters = []
            if template_id:
                filters.append(ToolInstance.tool_template_id == template_id)
            if status:
                filters.append(ToolInstance.status == status)
            if project_tags:
                # Filter by project tags - instance must have at least one matching tag
                filters.append(ToolInstance.project_tags.op('&&')(project_tags))
            
            if filters:
                query = query.where(and_(*filters))
            
            result = await session.execute(query)
            instances = result.scalars().all()
            
            return [ToolInstanceResponse.model_validate(instance) for instance in instances]
    
    async def get_tool_instance(self, instance_id: str) -> Optional[ToolInstanceResponse]:
        """Get tool instance by ID"""
        
        async with self.SessionLocal() as session:
            query = select(ToolInstance).options(selectinload(ToolInstance.template)).where(
                ToolInstance.id == instance_id
            )
            result = await session.execute(query)
            instance = result.scalar_one_or_none()
            
            return ToolInstanceResponse.model_validate(instance) if instance else None
    
    # LLM Model methods
    async def get_llm_models(
        self,
        project_tags: Optional[List[str]] = None,
        provider: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> list:
        """Get LLM models with optional filtering (using unified Model)"""
        async with self.SessionLocal() as session:
            query = select(Model)
            filters = [Model.model_type == "llm"]
            if is_active is not None:
                filters.append(Model.is_active == is_active)
            if provider:
                filters.append(Model.provider == provider)
            if filters:
                query = query.where(and_(*filters))
            result = await session.execute(query)
            models = result.scalars().all()
            return [model for model in models]
    
    # Embedding Model methods
    async def get_embedding_models(
        self,
        project_tags: Optional[List[str]] = None,
        provider: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> list:
        """Get embedding models with optional filtering (using unified Model)"""
        async with self.SessionLocal() as session:
            query = select(Model)
            filters = [Model.model_type == "embedding"]
            if is_active is not None:
                filters.append(Model.is_active == is_active)
            if provider:
                filters.append(Model.provider == provider)
            if filters:
                query = query.where(and_(*filters))
            result = await session.execute(query)
            models = result.scalars().all()
            return [model for model in models]

# Global database service instance
_database_service: Optional[DatabaseService] = None

def get_database_service() -> DatabaseService:
    """Get database service instance"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
