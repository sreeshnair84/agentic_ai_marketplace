"""
Database service for Workflow Engine
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Dict, Any
import logging
import os

from .models.database import Base, WorkflowDefinition, WorkflowExecution, WorkflowTemplate, WorkflowSchedule
from .models.workflows import (
    WorkflowDefinitionResponse, WorkflowExecutionResponse, 
    WorkflowTemplateResponse, WorkflowScheduleResponse,
    WorkflowSummary, ExecutionSummary
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for workflow management"""
    
    def __init__(self):
        # Database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/workflow_db")
        
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
    
    async def get_session(self) -> AsyncSession:
        """Get database session"""
        async with self.SessionLocal() as session:
            yield session
    
    async def init_database(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    # Workflow Definition methods
    async def get_workflows(
        self, 
        project_tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        is_template: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowSummary]:
        """Get workflow definitions with filtering"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowDefinition)
            
            # Apply filters
            filters = []
            if category:
                filters.append(WorkflowDefinition.category == category)
            if status:
                filters.append(WorkflowDefinition.status == status)
            if is_template is not None:
                filters.append(WorkflowDefinition.is_template == is_template)
            if project_tags:
                # Filter by project tags - workflow must have at least one matching tag
                filters.append(WorkflowDefinition.project_tags.op('&&')(project_tags))
            
            if filters:
                query = query.where(and_(*filters))
            
            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            result = await session.execute(query)
            workflows = result.scalars().all()
            
            return [WorkflowSummary.from_orm(workflow) for workflow in workflows]
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinitionResponse]:
        """Get workflow definition by ID"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
            result = await session.execute(query)
            workflow = result.scalar_one_or_none()
            
            return WorkflowDefinitionResponse.from_orm(workflow) if workflow else None
    
    async def get_workflow_by_name(self, name: str) -> Optional[WorkflowDefinitionResponse]:
        """Get workflow definition by name"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowDefinition).where(WorkflowDefinition.name == name)
            result = await session.execute(query)
            workflow = result.scalar_one_or_none()
            
            return WorkflowDefinitionResponse.from_orm(workflow) if workflow else None
    
    # Workflow Execution methods
    async def get_executions(
        self,
        project_tags: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExecutionSummary]:
        """Get workflow executions with filtering"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowExecution)
            
            # Apply filters
            filters = []
            if workflow_id:
                filters.append(WorkflowExecution.workflow_id == workflow_id)
            if status:
                filters.append(WorkflowExecution.status == status)
            if project_tags:
                # Filter by project tags - execution must have at least one matching tag
                filters.append(WorkflowExecution.project_tags.op('&&')(project_tags))
            
            if filters:
                query = query.where(and_(*filters))
            
            # Order by creation time (newest first) and apply pagination
            query = query.order_by(WorkflowExecution.created_at.desc()).offset(offset).limit(limit)
            
            result = await session.execute(query)
            executions = result.scalars().all()
            
            return [ExecutionSummary.from_orm(execution) for execution in executions]
    
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecutionResponse]:
        """Get workflow execution by ID"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            result = await session.execute(query)
            execution = result.scalar_one_or_none()
            
            return WorkflowExecutionResponse.from_orm(execution) if execution else None
    
    # Workflow Template methods
    async def get_templates(
        self,
        project_tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowTemplateResponse]:
        """Get workflow templates with filtering"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowTemplate)
            
            # Apply filters
            filters = []
            if category:
                filters.append(WorkflowTemplate.category == category)
            if is_active is not None:
                filters.append(WorkflowTemplate.is_active == is_active)
            if project_tags:
                # Filter by project tags - template must have at least one matching tag
                filters.append(WorkflowTemplate.project_tags.op('&&')(project_tags))
            
            if filters:
                query = query.where(and_(*filters))
            
            # Order by usage count (most used first) and apply pagination
            query = query.order_by(WorkflowTemplate.usage_count.desc()).offset(offset).limit(limit)
            
            result = await session.execute(query)
            templates = result.scalars().all()
            
            return [WorkflowTemplateResponse.from_orm(template) for template in templates]
    
    async def get_template(self, template_id: str) -> Optional[WorkflowTemplateResponse]:
        """Get workflow template by ID"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowTemplate).where(WorkflowTemplate.id == template_id)
            result = await session.execute(query)
            template = result.scalar_one_or_none()
            
            return WorkflowTemplateResponse.from_orm(template) if template else None
    
    # Workflow Schedule methods
    async def get_schedules(
        self,
        project_tags: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowScheduleResponse]:
        """Get workflow schedules with filtering"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowSchedule)
            
            # Apply filters
            filters = []
            if workflow_id:
                filters.append(WorkflowSchedule.workflow_id == workflow_id)
            if is_active is not None:
                filters.append(WorkflowSchedule.is_active == is_active)
            if project_tags:
                # Filter by project tags - schedule must have at least one matching tag
                filters.append(WorkflowSchedule.project_tags.op('&&')(project_tags))
            
            if filters:
                query = query.where(and_(*filters))
            
            # Order by next run time and apply pagination
            query = query.order_by(WorkflowSchedule.next_run_at.asc()).offset(offset).limit(limit)
            
            result = await session.execute(query)
            schedules = result.scalars().all()
            
            return [WorkflowScheduleResponse.from_orm(schedule) for schedule in schedules]
    
    async def get_schedule(self, schedule_id: str) -> Optional[WorkflowScheduleResponse]:
        """Get workflow schedule by ID"""
        
        async with self.SessionLocal() as session:
            query = select(WorkflowSchedule).where(WorkflowSchedule.id == schedule_id)
            result = await session.execute(query)
            schedule = result.scalar_one_or_none()
            
            return WorkflowScheduleResponse.from_orm(schedule) if schedule else None

# Global database service instance
_database_service: Optional[DatabaseService] = None

def get_database_service() -> DatabaseService:
    """Get database service instance"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
