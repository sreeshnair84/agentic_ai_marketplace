"""
Environment Variables API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

from ..models.environment import (
    EnvironmentVariable,
    EnvironmentVariableCreate,
    EnvironmentVariableUpdate,
    EnvironmentVariableResponse
)
from ..database import get_db
from ..auth import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/environment", tags=["environment"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.get("/variables", response_model=List[EnvironmentVariableResponse])
async def get_environment_variables(
    category: Optional[str] = None,
    scope: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all environment variables with optional filtering"""
    try:
        query = db.query(EnvironmentVariable)
        
        if category and category != "all":
            query = query.filter(EnvironmentVariable.category == category)
        
        if scope and scope != "all":
            query = query.filter(EnvironmentVariable.scope == scope)
        
        if search:
            query = query.filter(
                EnvironmentVariable.name.ilike(f"%{search}%") |
                EnvironmentVariable.description.ilike(f"%{search}%")
            )
        
        variables = query.order_by(EnvironmentVariable.name).all()
        
        # Mask secret values
        for var in variables:
            if var.is_secret:
                var.value = "•" * 20
        
        return variables
    
    except Exception as e:
        logger.error(f"Error fetching environment variables: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch environment variables"
        )

@router.get("/variables/{variable_id}", response_model=EnvironmentVariableResponse)
async def get_environment_variable(
    variable_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific environment variable"""
    try:
        variable = db.query(EnvironmentVariable).filter(
            EnvironmentVariable.id == variable_id
        ).first()
        
        if not variable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment variable not found"
            )
        
        # Only return actual value if user has admin privileges
        if variable.is_secret and current_user.get("role") != "admin":
            variable.value = "•" * 20
        
        return variable
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching environment variable {variable_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch environment variable"
        )

@router.post("/variables", response_model=EnvironmentVariableResponse)
async def create_environment_variable(
    variable: EnvironmentVariableCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new environment variable"""
    try:
        # Check if variable name already exists
        existing = db.query(EnvironmentVariable).filter(
            EnvironmentVariable.name == variable.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Environment variable with this name already exists"
            )
        
        db_variable = EnvironmentVariable(
            **variable.dict(),
            created_by=current_user.get("email"),
            updated_by=current_user.get("email")
        )
        
        db.add(db_variable)
        db.commit()
        db.refresh(db_variable)
        
        # Mask secret value in response
        if db_variable.is_secret:
            db_variable.value = "•" * 20
        
        logger.info(f"Created environment variable: {variable.name}")
        return db_variable
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating environment variable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create environment variable"
        )

@router.put("/variables/{variable_id}", response_model=EnvironmentVariableResponse)
async def update_environment_variable(
    variable_id: UUID,
    variable_update: EnvironmentVariableUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an environment variable"""
    try:
        db_variable = db.query(EnvironmentVariable).filter(
            EnvironmentVariable.id == variable_id
        ).first()
        
        if not db_variable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment variable not found"
            )
        
        # Update only provided fields
        update_data = variable_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_variable, field, value)
        
        db_variable.updated_by = current_user.get("email")
        db_variable.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_variable)
        
        # Mask secret value in response
        if db_variable.is_secret:
            db_variable.value = "•" * 20
        
        logger.info(f"Updated environment variable: {db_variable.name}")
        return db_variable
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating environment variable {variable_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update environment variable"
        )

@router.delete("/variables/{variable_id}")
async def delete_environment_variable(
    variable_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an environment variable"""
    try:
        db_variable = db.query(EnvironmentVariable).filter(
            EnvironmentVariable.id == variable_id
        ).first()
        
        if not db_variable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment variable not found"
            )
        
        # Check if variable is required
        if db_variable.is_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete required environment variable"
            )
        
        db.delete(db_variable)
        db.commit()
        
        logger.info(f"Deleted environment variable: {db_variable.name}")
        return {"message": "Environment variable deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting environment variable {variable_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete environment variable"
        )

@router.get("/variables/{variable_id}/value")
async def get_environment_variable_value(
    variable_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the actual value of an environment variable (admin only)"""
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view secret values"
            )
        
        variable = db.query(EnvironmentVariable).filter(
            EnvironmentVariable.id == variable_id
        ).first()
        
        if not variable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment variable not found"
            )
        
        return {"value": variable.value}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching variable value {variable_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch variable value"
        )

@router.get("/categories")
async def get_environment_categories():
    """Get all available environment variable categories"""
    return {
        "categories": [
            {"value": "llm", "label": "LLM", "description": "Language model configurations"},
            {"value": "database", "label": "Database", "description": "Database connection settings"},
            {"value": "api", "label": "API", "description": "External API configurations"},
            {"value": "auth", "label": "Authentication", "description": "Authentication and security settings"},
            {"value": "system", "label": "System", "description": "System-wide configurations"},
            {"value": "integration", "label": "Integration", "description": "Third-party integrations"}
        ]
    }

@router.get("/scopes")
async def get_environment_scopes():
    """Get all available environment variable scopes"""
    return {
        "scopes": [
            {"value": "global", "label": "Global", "description": "Available across all environments"},
            {"value": "development", "label": "Development", "description": "Development environment only"},
            {"value": "staging", "label": "Staging", "description": "Staging environment only"},
            {"value": "production", "label": "Production", "description": "Production environment only"}
        ]
    }
