"""
API for agent registry with full signature support
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..core.database import get_database
from ..core.config import get_settings
import json
import httpx
import logging

# Logger for gateway agents
logger = logging.getLogger("gateway.agents")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

router = APIRouter(prefix="/agents", tags=["agents"])

# Pydantic models for agent CRUD operations
class AgentCreate(BaseModel):
    name: str
    description: str
    framework: str = "custom"
    capabilities: List[str] = []
    tags: List[str] = []
    llm_model_id: Optional[str] = None
    systemPrompt: Optional[str] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    category: Optional[str] = None
    agent_type: Optional[str] = None
    version: Optional[str] = "1.0"
    a2a_enabled: bool = False

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    framework: Optional[str] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    llm_model_id: Optional[str] = None
    systemPrompt: Optional[str] = None
    temperature: Optional[float] = None
    maxTokens: Optional[int] = None
    category: Optional[str] = None
    agent_type: Optional[str] = None
    version: Optional[str] = None
    a2a_enabled: Optional[bool] = None


@router.get("/")
async def get_all_agents(db: AsyncSession = Depends(get_database)):
    """Get all agents with basic information"""
    # Entry log to help debugging request flow
    logger.debug("Entered get_all_agents handler")
    
    result_query = await db.execute(
        select(text("""
            name, display_name, description, category, status,
            ai_provider, model_name, dns_name, health_url,
            tags, project_tags, execution_count, success_rate
        """)).select_from(text("agents"))
    )
    agents = result_query.fetchall()
    try:
        logger.debug("Agents DB query executed, rows fetched: %d", len(agents))
        if agents:
            # Log a sample of the first row keys to help debug shape
            sample = agents[0]
            try:
                logger.debug("Sample agent row keys: %s", list(sample._mapping.keys()))
            except Exception:
                logger.debug("Sample agent row (repr): %s", repr(sample))

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

        logger.debug("Returning %d agents in response", len(result))
        return {"agents": result}
    except Exception as e:
        logger.exception("Failed while transforming agent rows: %s", e)
        raise


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


@router.post("/test")
async def test_agent_post():
    """Simple test POST endpoint"""
    return {"message": "POST endpoint is working"}


@router.post("/")
async def create_agent(agent_data: AgentCreate, db: AsyncSession = Depends(get_database)):
    """Create a new agent"""
    try:
        import uuid
        from datetime import datetime
        
        agent_id = str(uuid.uuid4())
        
        # Insert directly into database
        await db.execute(
            text("""
                INSERT INTO agents (
                    id, name, display_name, description, agent_type, status, framework, version,
                    capabilities, system_prompt, llm_model_id, created_at, updated_at, is_active
                ) VALUES (
                    :id, :name, :display_name, :description, :agent_type, :status, :framework, :version,
                    :capabilities, :system_prompt, :llm_model_id, :created_at, :updated_at, :is_active
                )
            """),
            {
                "id": agent_id,
                "name": agent_data.name,
                "display_name": agent_data.name,
                "description": agent_data.description,
                "agent_type": agent_data.agent_type or "generic",
                "status": "active",
                "framework": agent_data.framework,
                "version": agent_data.version,
                "capabilities": json.dumps(agent_data.capabilities),
                "system_prompt": agent_data.systemPrompt,
                "llm_model_id": agent_data.llm_model_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
        )
        await db.commit()
        
        return {
            "id": agent_id,
            "name": agent_data.name,
            "display_name": agent_data.name,
            "description": agent_data.description,
            "agent_type": agent_data.agent_type or "generic",
            "status": "active",
            "framework": agent_data.framework,
            "version": agent_data.version,
            "capabilities": agent_data.capabilities,
            "system_prompt": agent_data.systemPrompt,
            "llm_model_id": agent_data.llm_model_id,
            "is_active": True
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.put("/{agent_id}")
async def update_agent(agent_id: str, agent_data: AgentUpdate, db: AsyncSession = Depends(get_database)):
    """Update an existing agent"""
    try:
        from datetime import datetime
        
        # Check if agent exists
        existing = await db.execute(
            text("SELECT id FROM agents WHERE id = :agent_id"),
            {"agent_id": agent_id}
        )
        
        if not existing.fetchone():
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Build update query dynamically
        update_fields = []
        update_params = {"agent_id": agent_id, "updated_at": datetime.utcnow()}
        
        update_data = agent_data.dict(exclude_unset=True)
        
        if "name" in update_data and update_data["name"] is not None:
            update_fields.append("name = :name")
            update_params["name"] = update_data["name"]
            
        if "description" in update_data and update_data["description"] is not None:
            update_fields.append("description = :description")
            update_params["description"] = update_data["description"]
            
        if "framework" in update_data and update_data["framework"] is not None:
            update_fields.append("framework = :framework")
            update_params["framework"] = update_data["framework"]
            
        if "capabilities" in update_data and update_data["capabilities"] is not None:
            update_fields.append("capabilities = :capabilities")
            update_params["capabilities"] = json.dumps(update_data["capabilities"])
            
        if "systemPrompt" in update_data and update_data["systemPrompt"] is not None:
            update_fields.append("system_prompt = :system_prompt")
            update_params["system_prompt"] = update_data["systemPrompt"]
            
        if "agent_type" in update_data and update_data["agent_type"] is not None:
            update_fields.append("agent_type = :agent_type")
            update_params["agent_type"] = update_data["agent_type"]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Add updated_at to update fields
        update_fields.append("updated_at = :updated_at")
        
        query = f"""
            UPDATE agents 
            SET {', '.join(update_fields)}
            WHERE id = :agent_id
        """
        
        await db.execute(text(query), update_params)
        await db.commit()
        
        # Fetch and return updated agent
        result = await db.execute(
            text("""
                SELECT id, name, display_name, description, agent_type, status, framework, 
                       version, capabilities, system_prompt, llm_model_id, is_active
                FROM agents WHERE id = :agent_id
            """),
            {"agent_id": agent_id}
        )
        
        agent = result.fetchone()
        
        return {
            "id": str(agent.id),
            "name": agent.name,
            "display_name": agent.display_name,
            "description": agent.description,
            "agent_type": agent.agent_type,
            "status": agent.status,
            "framework": agent.framework,
            "version": agent.version,
            "capabilities": json.loads(agent.capabilities) if agent.capabilities else [],
            "system_prompt": agent.system_prompt,
            "llm_model_id": str(agent.llm_model_id) if agent.llm_model_id else None,
            "is_active": agent.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_database)):
    """Delete an agent"""
    try:
        # Check if agent exists
        existing = await db.execute(
            text("SELECT id FROM agents WHERE id = :agent_id"),
            {"agent_id": agent_id}
        )
        
        if not existing.fetchone():
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Delete the agent
        await db.execute(
            text("DELETE FROM agents WHERE id = :agent_id"),
            {"agent_id": agent_id}
        )
        await db.commit()
        
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post("/{agent_id}/run")
async def run_agent(agent_id: str, task_data: Dict[str, Any] = None, db: AsyncSession = Depends(get_database)):
    """Run an agent task"""
    try:
        import uuid
        from datetime import datetime
        
        # Check if agent exists and is active
        result = await db.execute(
            text("""
                SELECT id, name, status, is_active FROM agents 
                WHERE id = :agent_id
            """),
            {"agent_id": agent_id}
        )
        
        agent = result.fetchone()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if not agent.is_active or agent.status != 'active':
            raise HTTPException(status_code=400, detail="Agent is not active")
        
        # For now, return a mock execution response
        # In a real implementation, this would execute the agent
        task_id = str(uuid.uuid4())
        
        return {
            "taskId": task_id,
            "agentId": str(agent_id),
            "agentName": agent.name,
            "status": "running",
            "message": "Agent execution started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run agent: {str(e)}"
        )
