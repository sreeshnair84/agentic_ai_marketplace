"""
Project API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_database
from ...models.project import Project, ProjectCreate, ProjectUpdate
from ...services.project_service import ProjectService

router = APIRouter()


# Project endpoints
@router.get("/projects", response_model=List[Project])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_database)
):
    """Get all projects"""
    projects = await ProjectService.get_projects(db, skip=skip, limit=limit)
    return projects


@router.get("/projects/default", response_model=Project)
async def get_default_project(db: AsyncSession = Depends(get_database)):
    """Get the default project"""
    project = await ProjectService.get_default_project(db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Default project not found"
        )
    return project


@router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, db: AsyncSession = Depends(get_database)):
    """Get a specific project"""
    project = await ProjectService.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new project"""
    try:
        return await ProjectService.create_project(db, project, created_by="system")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create project: {str(e)}"
        )


@router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update a project"""
    updated_project = await ProjectService.update_project(db, project_id, project, updated_by="system")
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return updated_project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_database)):
    """Delete a project"""
    success = await ProjectService.delete_project(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
