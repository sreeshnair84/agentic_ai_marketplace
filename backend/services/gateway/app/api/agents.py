"""
API for agent registry with full signature support
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from ..core.database import get_database
import json

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/")
async def get_all_agents(db: AsyncSession = Depends(get_database)):
    """Get all agents with basic information"""
    
    result_query = await db.execute(
        select(text("""
            name, display_name, description, category, status,
            ai_provider, model_name, dns_name, health_url,
            tags, project_tags, execution_count, success_rate
        """)).select_from(text("agents"))
    )
    agents = result_query.fetchall()
    
    result = []
    for agent in agents:
        result.append({
            "name": agent.name,
            "display_name": agent.display_name,
            "description": agent.description,
            "category": agent.category,
            "status": agent.status,
            "ai_provider": agent.ai_provider,
            "model_name": agent.model_name,
            "dns_name": agent.dns_name,
            "health_url": agent.health_url,
            "tags": agent.tags or [],
            "project_tags": agent.project_tags or [],
            "execution_count": agent.execution_count,
            "success_rate": float(agent.success_rate) if agent.success_rate else None
        })
    
    return {"agents": result}


@router.get("/{agent_name}")
async def get_agent_details(agent_name: str, db: AsyncSession = Depends(get_database)):
    """Get detailed agent information including signatures"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, description, category, status, url, health_url, dns_name,
                   card_url, default_input_modes, default_output_modes, capabilities,
                   input_signature, output_signature, ai_provider, model_name, model_config,
                   health_check_config, usage_metrics, external_services,
                   author, organization, environment, search_keywords,
                   tags, project_tags, execution_count, success_rate, avg_response_time,
                   created_at, updated_at
            FROM agents 
            WHERE name = :agent_name
        """), {"agent_name": agent_name}
    )
    agent = result_query.fetchone()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
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
        "name": agent.name,
        "display_name": agent.display_name,
        "description": agent.description,
        "category": agent.category,
        "status": agent.status,
        "url": agent.url,
        "health_url": agent.health_url,
        "dns_name": agent.dns_name,
        "card_url": agent.card_url,
        "default_input_modes": agent.default_input_modes or [],
        "default_output_modes": agent.default_output_modes or [],
        "capabilities": safe_json_parse(agent.capabilities),
        "input_signature": safe_json_parse(agent.input_signature),
        "output_signature": safe_json_parse(agent.output_signature),
        "ai_provider": agent.ai_provider,
        "model_name": agent.model_name,
        "model_config": safe_json_parse(agent.model_config),
        "health_check_config": safe_json_parse(agent.health_check_config),
        "usage_metrics": safe_json_parse(agent.usage_metrics),
        "external_services": safe_json_parse(agent.external_services),
        "author": agent.author,
        "organization": agent.organization,
        "environment": agent.environment,
        "search_keywords": agent.search_keywords or [],
        "tags": agent.tags or [],
        "project_tags": agent.project_tags or [],
        "execution_count": agent.execution_count,
        "success_rate": float(agent.success_rate) if agent.success_rate else None,
        "avg_response_time": agent.avg_response_time,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
        "updated_at": agent.updated_at.isoformat() if agent.updated_at else None
    }


@router.get("/{agent_name}/signature")
async def get_agent_signature(agent_name: str, db: AsyncSession = Depends(get_database)):
    """Get agent input/output signature for integration"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, input_signature, output_signature, 
                   default_input_modes, default_output_modes, capabilities
            FROM agents 
            WHERE name = :agent_name
        """), {"agent_name": agent_name}
    )
    agent = result_query.fetchone()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
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
        "name": agent.name,
        "display_name": agent.display_name,
        "input_signature": safe_json_parse(agent.input_signature),
        "output_signature": safe_json_parse(agent.output_signature),
        "default_input_modes": agent.default_input_modes or [],
        "default_output_modes": agent.default_output_modes or [],
        "capabilities": safe_json_parse(agent.capabilities)
    }


@router.get("/{agent_name}/health")
async def get_agent_health_config(agent_name: str, db: AsyncSession = Depends(get_database)):
    """Get agent health check configuration"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, health_url, dns_name, health_check_config
            FROM agents 
            WHERE name = :agent_name
        """), {"agent_name": agent_name}
    )
    agent = result_query.fetchone()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
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
        "name": agent.name,
        "display_name": agent.display_name,
        "health_url": agent.health_url,
        "dns_name": agent.dns_name,
        "health_check_config": safe_json_parse(agent.health_check_config)
    }
