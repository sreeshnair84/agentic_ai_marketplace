"""
API for workflows registry with full signature support
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from ..core.database import get_database
import json

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/")
async def get_all_workflows(db: AsyncSession = Depends(get_database)):
    """Get all workflows with basic information"""
    
    result_query = await db.execute(
        select(text("""
            name, display_name, description, category, version, status,
            dns_name, health_url, tags, project_tags, execution_count, success_rate,
            is_template, is_public, timeout_seconds
        """)).select_from(text("workflow_definitions"))
    )
    workflows = result_query.fetchall()
    
    result = []
    for workflow in workflows:
        result.append({
            "name": workflow.name,
            "display_name": workflow.display_name,
            "description": workflow.description,
            "category": workflow.category,
            "version": workflow.version,
            "status": workflow.status,
            "dns_name": workflow.dns_name,
            "health_url": workflow.health_url,
            "tags": workflow.tags or [],
            "project_tags": workflow.project_tags or [],
            "execution_count": workflow.execution_count,
            "success_rate": float(workflow.success_rate) if workflow.success_rate else None,
            "is_template": workflow.is_template,
            "is_public": workflow.is_public,
            "timeout_seconds": workflow.timeout_seconds
        })
    
    return {"workflows": result}


@router.get("/{workflow_name}")
async def get_workflow_details(workflow_name: str, db: AsyncSession = Depends(get_database)):
    """Get detailed workflow information including signatures"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, description, category, version, status, url, health_url, 
                   dns_name, card_url, default_input_modes, default_output_modes, capabilities,
                   input_signature, output_signature, ai_provider, model_name, model_config,
                   health_check_config, usage_metrics, external_services,
                   author, organization, environment, search_keywords,
                   tags, project_tags, execution_count, success_rate, avg_response_time,
                   is_template, is_public, timeout_seconds, steps, variables,
                   retry_config, notification_config, triggers, dependencies,
                   created_at, updated_at, created_by, updated_by
            FROM workflow_definitions 
            WHERE name = :workflow_name
        """), {"workflow_name": workflow_name}
    )
    workflow = result_query.fetchone()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Parse JSON fields safely
    def safe_json_parse(value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            return value
    
    return {
        "name": workflow.name,
        "display_name": workflow.display_name,
        "description": workflow.description,
        "category": workflow.category,
        "version": workflow.version,
        "status": workflow.status,
        "url": workflow.url,
        "health_url": workflow.health_url,
        "dns_name": workflow.dns_name,
        "card_url": workflow.card_url,
        "default_input_modes": workflow.default_input_modes or [],
        "default_output_modes": workflow.default_output_modes or [],
        "capabilities": safe_json_parse(workflow.capabilities),
        "input_signature": safe_json_parse(workflow.input_signature),
        "output_signature": safe_json_parse(workflow.output_signature),
        "ai_provider": workflow.ai_provider,
        "model_name": workflow.model_name,
        "model_config": safe_json_parse(workflow.model_config),
        "health_check_config": safe_json_parse(workflow.health_check_config),
        "usage_metrics": safe_json_parse(workflow.usage_metrics),
        "external_services": safe_json_parse(workflow.external_services),
        "author": workflow.author,
        "organization": workflow.organization,
        "environment": workflow.environment,
        "search_keywords": workflow.search_keywords or [],
        "tags": workflow.tags or [],
        "project_tags": workflow.project_tags or [],
        "execution_count": workflow.execution_count,
        "success_rate": float(workflow.success_rate) if workflow.success_rate else None,
        "avg_response_time": workflow.avg_response_time,
        "is_template": workflow.is_template,
        "is_public": workflow.is_public,
        "timeout_seconds": workflow.timeout_seconds,
        "steps": safe_json_parse(workflow.steps),
        "variables": safe_json_parse(workflow.variables),
        "retry_config": safe_json_parse(workflow.retry_config),
        "notification_config": safe_json_parse(workflow.notification_config),
        "triggers": safe_json_parse(workflow.triggers),
        "dependencies": safe_json_parse(workflow.dependencies),
        "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
        "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
        "created_by": workflow.created_by,
        "updated_by": workflow.updated_by
    }


@router.get("/{workflow_name}/signature")
async def get_workflow_signature(workflow_name: str, db: AsyncSession = Depends(get_database)):
    """Get workflow input/output signature for integration"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, input_signature, output_signature, 
                   default_input_modes, default_output_modes, capabilities
            FROM workflow_definitions 
            WHERE name = :workflow_name
        """), {"workflow_name": workflow_name}
    )
    workflow = result_query.fetchone()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    def safe_json_parse(value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            return value
    
    return {
        "name": workflow.name,
        "display_name": workflow.display_name,
        "input_signature": safe_json_parse(workflow.input_signature),
        "output_signature": safe_json_parse(workflow.output_signature),
        "default_input_modes": workflow.default_input_modes or [],
        "default_output_modes": workflow.default_output_modes or [],
        "capabilities": safe_json_parse(workflow.capabilities)
    }


@router.get("/{workflow_name}/health")
async def get_workflow_health_config(workflow_name: str, db: AsyncSession = Depends(get_database)):
    """Get workflow health check configuration"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, health_url, dns_name, health_check_config
            FROM workflow_definitions 
            WHERE name = :workflow_name
        """), {"workflow_name": workflow_name}
    )
    workflow = result_query.fetchone()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    def safe_json_parse(value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            return value
    
    return {
        "name": workflow.name,
        "display_name": workflow.display_name,
        "health_url": workflow.health_url,
        "dns_name": workflow.dns_name,
        "health_check_config": safe_json_parse(workflow.health_check_config)
    }


@router.get("/{workflow_name}/steps")
async def get_workflow_steps(workflow_name: str, db: AsyncSession = Depends(get_database)):
    """Get workflow steps and execution plan"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, steps, variables, dependencies, triggers
            FROM workflow_definitions 
            WHERE name = :workflow_name
        """), {"workflow_name": workflow_name}
    )
    workflow = result_query.fetchone()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    def safe_json_parse(value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            return value
    
    return {
        "name": workflow.name,
        "display_name": workflow.display_name,
        "steps": safe_json_parse(workflow.steps),
        "variables": safe_json_parse(workflow.variables),
        "dependencies": safe_json_parse(workflow.dependencies),
        "triggers": safe_json_parse(workflow.triggers)
    }


@router.get("/category/{category}")
async def get_workflows_by_category(category: str, db: AsyncSession = Depends(get_database)):
    """Get workflows filtered by category"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, description, version, status,
                   dns_name, health_url, tags, project_tags, execution_count, success_rate,
                   is_template, is_public
            FROM workflow_definitions 
            WHERE category = :category
            ORDER BY name
        """), {"category": category}
    )
    workflows = result_query.fetchall()
    
    result = []
    for workflow in workflows:
        result.append({
            "name": workflow.name,
            "display_name": workflow.display_name,
            "description": workflow.description,
            "version": workflow.version,
            "status": workflow.status,
            "dns_name": workflow.dns_name,
            "health_url": workflow.health_url,
            "tags": workflow.tags or [],
            "project_tags": workflow.project_tags or [],
            "execution_count": workflow.execution_count,
            "success_rate": float(workflow.success_rate) if workflow.success_rate else None,
            "is_template": workflow.is_template,
            "is_public": workflow.is_public
        })
    
    return {
        "category": category,
        "workflows": result
    }
