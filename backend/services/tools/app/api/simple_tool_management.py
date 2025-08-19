"""
Simple Tool Management API Router
Provides basic endpoints for tool management that work with the UI
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/tool-management", tags=["Simple Tool Management"])

# Mock data for testing
MOCK_TOOL_TEMPLATES = [
    {
        "id": "rag-template",
        "name": "RAG Pipeline",
        "type": "rag",
        "description": "Retrieval-Augmented Generation pipeline for document processing",
        "category": "AI/ML",
        "icon": "📚",
        "version": "1.0.0",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "field_count": 5
    },
    {
        "id": "sql-agent-template", 
        "name": "SQL Agent",
        "type": "sql_agent",
        "description": "Intelligent SQL query generation and execution",
        "category": "Database",
        "icon": "🗃️",
        "version": "1.0.0",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "field_count": 4
    },
    {
        "id": "mcp-template",
        "name": "MCP Client",
        "type": "mcp",
        "description": "Model Context Protocol client integration",
        "category": "Integration",
        "icon": "🔌",
        "version": "1.0.0", 
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "field_count": 3
    },
    {
        "id": "web-scraper-template",
        "name": "Web Scraper",
        "type": "web_scraper",
        "description": "Configurable web content extraction and processing",
        "category": "Web",
        "icon": "🕷️",
        "version": "1.0.0",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "field_count": 6
    }
]

MOCK_TOOL_INSTANCES = [
    {
        "id": "instance-1",
        "name": "Production RAG",
        "template_id": "rag-template",
        "template_name": "RAG Pipeline",
        "status": "active",
        "environment": "production",
        "description": "Production RAG pipeline for customer support",
        "created_at": "2024-01-15T00:00:00Z",
        "last_execution": "2024-01-20T10:30:00Z"
    },
    {
        "id": "instance-2", 
        "name": "Dev SQL Agent",
        "template_id": "sql-agent-template",
        "template_name": "SQL Agent",
        "status": "inactive",
        "environment": "development",
        "description": "Development SQL agent for testing",
        "created_at": "2024-01-10T00:00:00Z",
        "last_execution": None
    }
]

@router.get("/templates")
async def get_tool_templates(
    category: Optional[str] = None,
    type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all tool templates"""
    logger.info(f"=== TOOL TEMPLATES API CALLED ===")
    logger.info(f"Getting tool templates - category: {category}, type: {type}")
    
    templates = MOCK_TOOL_TEMPLATES.copy()
    
    # Apply filters
    if category:
        templates = [t for t in templates if t.get("category", "").lower() == category.lower()]
    if type:
        templates = [t for t in templates if t.get("type", "").lower() == type.lower()]
    
    logger.info(f"Returning {len(templates)} tool templates")
    logger.info(f"Templates data: {templates}")
    return templates

@router.get("/instances")
async def get_tool_instances(
    template_id: Optional[str] = None,
    status: Optional[str] = None,
    environment: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all tool instances"""
    logger.info(f"Getting tool instances - template_id: {template_id}, status: {status}, environment: {environment}")
    
    instances = MOCK_TOOL_INSTANCES.copy()
    
    # Apply filters
    if template_id:
        instances = [i for i in instances if i.get("template_id") == template_id]
    if status:
        instances = [i for i in instances if i.get("status", "").lower() == status.lower()]
    if environment:
        instances = [i for i in instances if i.get("environment", "").lower() == environment.lower()]
    
    logger.info(f"Returning {len(instances)} tool instances")
    return instances

@router.get("/statistics")
async def get_tool_statistics() -> Dict[str, Any]:
    """Get tool management statistics"""
    logger.info("Getting tool statistics")
    
    return {
        "total_templates": len(MOCK_TOOL_TEMPLATES),
        "active_templates": len([t for t in MOCK_TOOL_TEMPLATES if t.get("is_active", False)]),
        "total_instances": len(MOCK_TOOL_INSTANCES),
        "active_instances": len([i for i in MOCK_TOOL_INSTANCES if i.get("status") == "active"]),
        "template_types": list(set(t.get("type") for t in MOCK_TOOL_TEMPLATES)),
        "environments": list(set(i.get("environment") for i in MOCK_TOOL_INSTANCES))
    }

@router.post("/instances/{instance_id}/activate")
async def activate_instance(instance_id: str) -> Dict[str, Any]:
    """Activate a tool instance"""
    logger.info(f"Activating instance {instance_id}")
    
    # Find instance
    instance = next((i for i in MOCK_TOOL_INSTANCES if i["id"] == instance_id), None)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Update status
    instance["status"] = "active"
    
    return {"message": f"Instance {instance_id} activated successfully", "status": "active"}

@router.post("/instances/{instance_id}/deactivate")
async def deactivate_instance(instance_id: str) -> Dict[str, Any]:
    """Deactivate a tool instance"""
    logger.info(f"Deactivating instance {instance_id}")
    
    # Find instance
    instance = next((i for i in MOCK_TOOL_INSTANCES if i["id"] == instance_id), None)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Update status
    instance["status"] = "inactive"
    
    return {"message": f"Instance {instance_id} deactivated successfully", "status": "inactive"}

@router.post("/instances/{instance_id}/execute")
async def execute_instance(instance_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a tool instance"""
    logger.info(f"Executing instance {instance_id} with parameters {parameters}")
    
    # Find instance
    instance = next((i for i in MOCK_TOOL_INSTANCES if i["id"] == instance_id), None)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    if instance["status"] != "active":
        raise HTTPException(status_code=400, detail="Instance is not active")
    
    # Mock execution
    execution_id = f"exec-{instance_id}-{int(time.time())}"
    
    return {
        "execution_id": execution_id,
        "instance_id": instance_id,
        "status": "running", 
        "message": f"Execution {execution_id} started successfully",
        "parameters": parameters or {}
    }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for tool management"""
    return {
        "status": "healthy",
        "service": "tool-management",
        "templates_available": len(MOCK_TOOL_TEMPLATES),
        "instances_available": len(MOCK_TOOL_INSTANCES)
    }
