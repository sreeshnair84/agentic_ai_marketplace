"""
API endpoints for chat interface metadata (workflows, agents, tools)
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from ..core.database import get_database
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metadata", tags=["metadata"])


def safe_json_parse(value):
    """Safely parse JSON values"""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return value


@router.get("/default-workflow")
async def get_default_workflow():
    """Get default workflow configuration"""
    try:
        # Default workflow configuration
        default_workflow = {
            "id": "default-plan-execute",
            "name": "default-plan-execute",
            "display_name": "Smart Plan & Execute",
            "description": "Intelligent workflow that analyzes your query and selects the best approach using LangGraph Plan and Execute pattern",
            "category": "intelligent-routing",
            "version": "1.0.0",
            "status": "active",
            "dns_name": "localhost:8005",  # Default workflow service
            "health_url": "http://localhost:8005/health",
            "url": "http://localhost:8005",
            "capabilities": {
                "planning": True,
                "execution": True,
                "memory": True,
                "context_aware": True,
                "multi_step": True,
                "agent_selection": True,
                "tool_integration": True
            },
            "tags": ["default", "intelligent", "plan-execute", "langraph"],
            "project_tags": ["core"],
            "execution_count": 0,
            "success_rate": 1.0,
            "is_public": True,
            "timeout_seconds": 300,
            "input_modes": ["text", "json"],
            "output_modes": ["text", "json"],
            "type": "workflow",
            "is_default": True
        }
        
        return default_workflow
        
    except Exception as e:
        logger.error(f"Error getting default workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get default workflow: {str(e)}")

@router.get("/chat-options")
async def get_chat_metadata_options(db: AsyncSession = Depends(get_database)):
    """Get all metadata options for chat interface (workflows, agents, tools)"""
    try:
        # Get workflows with A2A capabilities
        workflows_query = await db.execute(
            text("""
                SELECT name, display_name, description, category, version, status,
                       dns_name, health_url, url, capabilities, tags, project_tags,
                       execution_count, success_rate, is_public, timeout_seconds,
                       default_input_modes, default_output_modes
                FROM workflow_definitions 
                WHERE status = 'active' OR status = 'published'
                ORDER BY display_name
            """)
        )
        workflows = workflows_query.fetchall()
        
        # Get active agents with A2A capabilities
        agents_query = await db.execute(
            text("""
                SELECT name, display_name, description, category, status,
                       dns_name, health_url, url, a2a_enabled, a2a_address,
                       ai_provider, model_name, capabilities, tags, project_tags,
                       execution_count, success_rate, default_input_modes, default_output_modes
                FROM agents 
                WHERE status = 'active' AND a2a_enabled = true
                ORDER BY display_name
            """)
        )
        agents = agents_query.fetchall()
        
        # Get active tools
        tools_query = await db.execute(
            text("""
                SELECT name, display_name, description, category, type, version, status,
                       dns_name, health_url, tags, execution_count, success_rate,
                       capabilities, default_input_modes, default_output_modes
                FROM tool_templates 
                WHERE is_active = true
                ORDER BY display_name
            """)
        )
        tools = tools_query.fetchall()
        
        # Get default workflow
        default_workflow = await get_default_workflow()
        
        # Format workflows
        workflows_result = [default_workflow]  # Add default workflow first
        for workflow in workflows:
            workflows_result.append({
                "id": workflow.name,
                "name": workflow.name,
                "display_name": workflow.display_name,
                "description": workflow.description,
                "category": workflow.category,
                "version": workflow.version,
                "status": workflow.status,
                "dns_name": workflow.dns_name,
                "health_url": workflow.health_url,
                "url": workflow.url,
                "capabilities": safe_json_parse(workflow.capabilities),
                "tags": workflow.tags or [],
                "project_tags": workflow.project_tags or [],
                "execution_count": workflow.execution_count or 0,
                "success_rate": float(workflow.success_rate) if workflow.success_rate else None,
                "is_public": workflow.is_public,
                "timeout_seconds": workflow.timeout_seconds,
                "input_modes": workflow.default_input_modes or ["text"],
                "output_modes": workflow.default_output_modes or ["text"],
                "type": "workflow"
            })
        
        # Format agents
        agents_result = []
        for agent in agents:
            agents_result.append({
                "id": agent.name,
                "name": agent.name,
                "display_name": agent.display_name,
                "description": agent.description,
                "category": agent.category,
                "status": agent.status,
                "dns_name": agent.dns_name,
                "health_url": agent.health_url,
                "url": agent.url,
                "a2a_address": agent.a2a_address,
                "ai_provider": agent.ai_provider,
                "model_name": agent.model_name,
                "capabilities": safe_json_parse(agent.capabilities),
                "tags": agent.tags or [],
                "project_tags": agent.project_tags or [],
                "execution_count": agent.execution_count or 0,
                "success_rate": float(agent.success_rate) if agent.success_rate else None,
                "input_modes": agent.default_input_modes or ["text"],
                "output_modes": agent.default_output_modes or ["text"],
                "type": "agent"
            })
        
        # Format tools
        tools_result = []
        for tool in tools:
            tools_result.append({
                "id": tool.name,
                "name": tool.name,
                "display_name": tool.display_name,
                "description": tool.description,
                "category": tool.category,
                "tool_type": tool.type,
                "version": tool.version,
                "status": tool.status,
                "dns_name": tool.dns_name,
                "health_url": tool.health_url,
                "capabilities": safe_json_parse(tool.capabilities),
                "tags": tool.tags or [],
                "execution_count": tool.execution_count or 0,
                "success_rate": float(tool.success_rate) if tool.success_rate else None,
                "input_modes": tool.default_input_modes or ["text"],
                "output_modes": tool.default_output_modes or ["text"],
                "type": "tool"
            })
        
        return {
            "workflows": workflows_result,
            "agents": agents_result,
            "tools": tools_result,
            "summary": {
                "total_workflows": len(workflows_result),
                "total_agents": len(agents_result),
                "total_tools": len(tools_result),
                "categories": {
                    "workflows": list(set([w.get("category") for w in workflows_result if w.get("category")])),
                    "agents": list(set([a.get("category") for a in agents_result if a.get("category")])),
                    "tools": list(set([t.get("category") for t in tools_result if t.get("category")]))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting chat metadata options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metadata options: {str(e)}")


@router.get("/workflow/{workflow_name}/routing")
async def get_workflow_routing_info(workflow_name: str, db: AsyncSession = Depends(get_database)):
    """Get workflow routing information for A2A chat redirection"""
    try:
        result_query = await db.execute(
            text("""
                SELECT name, display_name, url, dns_name, health_url, capabilities,
                       default_input_modes, default_output_modes, status
                FROM workflow_definitions 
                WHERE name = :workflow_name
            """), {"workflow_name": workflow_name}
        )
        workflow = result_query.fetchone()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Determine routing URL - prefer DNS name, fall back to URL
        routing_url = None
        if workflow.dns_name:
            routing_url = f"https://{workflow.dns_name}/a2a/message/stream"
        elif workflow.url:
            routing_url = f"{workflow.url}/a2a/message/stream"
        
        return {
            "name": workflow.name,
            "display_name": workflow.display_name,
            "routing_url": routing_url,
            "dns_name": workflow.dns_name,
            "base_url": workflow.url,
            "health_url": workflow.health_url,
            "capabilities": safe_json_parse(workflow.capabilities),
            "input_modes": workflow.default_input_modes or ["text"],
            "output_modes": workflow.default_output_modes or ["text"],
            "status": workflow.status,
            "available": workflow.status in ["active", "published"] and routing_url is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow routing info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow routing info: {str(e)}")


@router.get("/agent/{agent_name}/routing")
async def get_agent_routing_info(agent_name: str, db: AsyncSession = Depends(get_database)):
    """Get agent routing information for A2A chat redirection"""
    try:
        result_query = await db.execute(
            text("""
                SELECT name, display_name, url, dns_name, health_url, a2a_address,
                       capabilities, default_input_modes, default_output_modes, 
                       status, a2a_enabled
                FROM agents 
                WHERE name = :agent_name
            """), {"agent_name": agent_name}
        )
        agent = result_query.fetchone()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Determine routing URL - prefer a2a_address, then DNS name, fall back to URL
        routing_url = None
        if agent.a2a_address:
            routing_url = f"{agent.a2a_address}/a2a/message/stream"
        elif agent.dns_name:
            routing_url = f"https://{agent.dns_name}/a2a/message/stream"
        elif agent.url:
            routing_url = f"{agent.url}/a2a/message/stream"
        
        return {
            "name": agent.name,
            "display_name": agent.display_name,
            "routing_url": routing_url,
            "a2a_address": agent.a2a_address,
            "dns_name": agent.dns_name,
            "base_url": agent.url,
            "health_url": agent.health_url,
            "capabilities": safe_json_parse(agent.capabilities),
            "input_modes": agent.default_input_modes or ["text"],
            "output_modes": agent.default_output_modes or ["text"],
            "status": agent.status,
            "a2a_enabled": agent.a2a_enabled,
            "available": agent.status == "active" and agent.a2a_enabled and routing_url is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent routing info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent routing info: {str(e)}")


@router.get("/tools/for-generic-agent")
async def get_tools_for_generic_agent(db: AsyncSession = Depends(get_database)):
    """Get tools that can be associated with generic A2A agent"""
    try:
        # Get active tools that can be used by generic agents
        tools_query = await db.execute(
            text("""
                SELECT name, display_name, description, category, type, version,
                       dns_name, health_url, capabilities, tags,
                       input_signature, output_signature, 
                       default_input_modes, default_output_modes
                FROM tool_templates 
                WHERE is_active = true
                ORDER BY category, display_name
            """)
        )
        tools = tools_query.fetchall()
        
        tools_result = []
        for tool in tools:
            tools_result.append({
                "id": tool.name,
                "name": tool.name,
                "display_name": tool.display_name,
                "description": tool.description,
                "category": tool.category,
                "tool_type": tool.type,
                "version": tool.version,
                "dns_name": tool.dns_name,
                "health_url": tool.health_url,
                "capabilities": safe_json_parse(tool.capabilities),
                "tags": tool.tags or [],
                "input_signature": safe_json_parse(tool.input_signature),
                "output_signature": safe_json_parse(tool.output_signature),
                "input_modes": tool.default_input_modes or ["text"],
                "output_modes": tool.default_output_modes or ["text"]
            })
        
        # Group by category
        categories = {}
        for tool in tools_result:
            category = tool["category"] or "Other"
            if category not in categories:
                categories[category] = []
            categories[category].append(tool)
        
        return {
            "tools": tools_result,
            "categories": categories,
            "total_tools": len(tools_result)
        }
        
    except Exception as e:
        logger.error(f"Error getting tools for generic agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


@router.get("/categories")
async def get_all_categories(db: AsyncSession = Depends(get_database)):
    """Get all available categories for workflows, agents, and tools"""
    try:
        # Get workflow categories
        workflow_categories_query = await db.execute(
            text("SELECT DISTINCT category FROM workflow_definitions WHERE category IS NOT NULL")
        )
        workflow_categories = [row[0] for row in workflow_categories_query.fetchall()]
        
        # Get agent categories
        agent_categories_query = await db.execute(
            text("SELECT DISTINCT category FROM agents WHERE category IS NOT NULL")
        )
        agent_categories = [row[0] for row in agent_categories_query.fetchall()]
        
        # Get tool categories
        tool_categories_query = await db.execute(
            text("SELECT DISTINCT category FROM tool_templates WHERE category IS NOT NULL")
        )
        tool_categories = [row[0] for row in tool_categories_query.fetchall()]
        
        return {
            "workflows": sorted(workflow_categories),
            "agents": sorted(agent_categories),
            "tools": sorted(tool_categories),
            "all": sorted(list(set(workflow_categories + agent_categories + tool_categories)))
        }
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


@router.get("/health")
async def get_metadata_health(db: AsyncSession = Depends(get_database)):
    """Get health status of all metadata sources"""
    try:
        # Count active workflows
        workflow_count_query = await db.execute(
            text("SELECT COUNT(*) FROM workflow_definitions WHERE status IN ('active', 'published')")
        )
        workflow_count = workflow_count_query.scalar()
        
        # Count active agents
        agent_count_query = await db.execute(
            text("SELECT COUNT(*) FROM agents WHERE status = 'active' AND a2a_enabled = true")
        )
        agent_count = agent_count_query.scalar()
        
        # Count active tools
        tool_count_query = await db.execute(
            text("SELECT COUNT(*) FROM tool_templates WHERE is_active = true")
        )
        tool_count = tool_count_query.scalar()
        
        return {
            "status": "healthy",
            "counts": {
                "workflows": workflow_count,
                "agents": agent_count,
                "tools": tool_count
            },
            "timestamp": "2025-01-22T00:00:00Z"  # Use current timestamp in real implementation
        }
        
    except Exception as e:
        logger.error(f"Error getting metadata health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-01-22T00:00:00Z"
        }