"""
Project service layer for CRUD operations
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from ..models.db_models import Project
from ..models.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service class for project operations"""
    
    @staticmethod
    async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects"""
        query = select(Project).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_project(db: AsyncSession, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_default_project(db: AsyncSession) -> Optional[Project]:
        """Get the default project"""
        query = select(Project).where(Project.is_default == True)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_project(db: AsyncSession, project: ProjectCreate, created_by: Optional[str] = None) -> Project:
        """Create a new project"""
        db_project = Project(
            name=project.name,
            description=project.description,
            tags=project.tags,
            is_default=project.is_default,
            created_by=created_by
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project
    
    @staticmethod
    async def update_project(db: AsyncSession, project_id: str, project: ProjectUpdate, updated_by: Optional[str] = None) -> Optional[Project]:
        """Update an existing project"""
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        db_project = result.scalar_one_or_none()
        
        if not db_project:
            return None
        
        if project.name is not None:
            db_project.name = project.name
        if project.description is not None:
            db_project.description = project.description
        if project.tags is not None:
            db_project.tags = project.tags
        if project.is_default is not None:
            db_project.is_default = project.is_default
        
        db_project.updated_by = updated_by
        
        await db.commit()
        await db.refresh(db_project)
        return db_project
    
    @staticmethod
    async def delete_project(db: AsyncSession, project_id: str) -> bool:
        """Delete a project"""
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        db_project = result.scalar_one_or_none()
        
        if not db_project:
            return False
        
        await db.delete(db_project)
        await db.commit()
        return True
