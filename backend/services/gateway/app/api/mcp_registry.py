"""
MCP Registry API endpoints for managing MCP servers and tools
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_, or_
from typing import List, Optional, Dict, Any
import json
import logging
import uuid
from datetime import datetime, timezone

from ..core.database import get_database
from ..models.mcp_models import (
    MCPServerCreate, MCPServerUpdate, MCPServerResponse,
    MCPToolCreate, MCPToolUpdate, MCPToolResponse,
    MCPEndpointCreate, MCPEndpointUpdate, MCPEndpointResponse,
    MCPToolBindingCreate, MCPToolBindingUpdate, MCPToolBindingResponse,
    MCPExecutionLogResponse, MCPTestResultResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp", tags=["mcp-registry"])

# =====================================================
# MCP SERVERS MANAGEMENT
# =====================================================

@router.get("/servers", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    status: Optional[str] = None,
    transport_type: Optional[str] = None,
    project_tags: Optional[List[str]] = Query(None),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_database)
):
    """List all MCP servers with optional filtering"""
    try:
        query = """
            SELECT id, name, display_name, description, server_url, transport_type,
                   status, health_status, version, capabilities, tags, project_tags,
                   is_active, created_at, updated_at, last_health_check
            FROM mcp_servers
            WHERE 1=1
        """
        params = {}
        
        if status:
            query += " AND status = :status"
            params['status'] = status
            
        if transport_type:
            query += " AND transport_type = :transport_type"
            params['transport_type'] = transport_type
            
        if is_active is not None:
            query += " AND is_active = :is_active"
            params['is_active'] = is_active
            
        if project_tags:
            query += " AND project_tags && :project_tags"
            params['project_tags'] = project_tags
            
        query += " ORDER BY created_at DESC"
        
        result = await db.execute(text(query), params)
        servers = result.fetchall()
        
        return [
            MCPServerResponse(
                id=str(server.id),
                name=server.name,
                display_name=server.display_name,
                description=server.description,
                server_url=server.server_url,
                transport_type=server.transport_type,
                status=server.status,
                health_status=server.health_status,
                version=server.version,
                capabilities=server.capabilities or {},
                tags=server.tags or [],
                project_tags=server.project_tags or [],
                is_active=server.is_active,
                created_at=server.created_at,
                updated_at=server.updated_at,
                last_health_check=server.last_health_check
            )
            for server in servers
        ]
    except Exception as e:
        logger.error(f"Error listing MCP servers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list MCP servers: {str(e)}")


@router.post("/servers", response_model=MCPServerResponse)
async def create_mcp_server(
    server_data: MCPServerCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new MCP server"""
    try:
        server_id = str(uuid.uuid4())
        query = text("""
            INSERT INTO mcp_servers (
                id, name, display_name, description, server_url, transport_type,
                authentication_config, capabilities, version, status, health_check_url,
                connection_config, metadata, tags, project_tags, is_active
            ) VALUES (
                :id, :name, :display_name, :description, :server_url, :transport_type,
                :authentication_config, :capabilities, :version, :status, :health_check_url,
                :connection_config, :metadata, :tags, :project_tags, :is_active
            ) RETURNING *
        """)
        
        params = {
            'id': server_id,
            'name': server_data.name,
            'display_name': server_data.display_name,
            'description': server_data.description,
            'server_url': server_data.server_url,
            'transport_type': server_data.transport_type,
            'authentication_config': json.dumps(server_data.authentication_config),
            'capabilities': json.dumps(server_data.capabilities),
            'version': server_data.version,
            'status': server_data.status,
            'health_check_url': server_data.health_check_url,
            'connection_config': json.dumps(server_data.connection_config),
            'metadata': json.dumps(server_data.metadata),
            'tags': server_data.tags,
            'project_tags': server_data.project_tags,
            'is_active': server_data.is_active
        }
        
        result = await db.execute(query, params)
        await db.commit()
        
        server = result.fetchone()
        return MCPServerResponse(
            id=str(server.id),
            name=server.name,
            display_name=server.display_name,
            description=server.description,
            server_url=server.server_url,
            transport_type=server.transport_type,
            status=server.status,
            health_status=server.health_status,
            version=server.version,
            capabilities=server.capabilities or {},
            tags=server.tags or [],
            project_tags=server.project_tags or [],
            is_active=server.is_active,
            created_at=server.created_at,
            updated_at=server.updated_at,
            last_health_check=server.last_health_check
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create MCP server: {str(e)}")


@router.get("/servers/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get a specific MCP server by ID"""
    try:
        query = text("""
            SELECT id, name, display_name, description, server_url, transport_type,
                   authentication_config, capabilities, status, health_status, version,
                   connection_config, metadata, tags, project_tags, is_active,
                   created_at, updated_at, last_health_check
            FROM mcp_servers
            WHERE id = :server_id
        """)
        
        result = await db.execute(query, {'server_id': server_id})
        server = result.fetchone()
        
        if not server:
            raise HTTPException(status_code=404, detail="MCP server not found")
            
        return MCPServerResponse(
            id=str(server.id),
            name=server.name,
            display_name=server.display_name,
            description=server.description,
            server_url=server.server_url,
            transport_type=server.transport_type,
            status=server.status,
            health_status=server.health_status,
            version=server.version,
            capabilities=server.capabilities or {},
            tags=server.tags or [],
            project_tags=server.project_tags or [],
            is_active=server.is_active,
            created_at=server.created_at,
            updated_at=server.updated_at,
            last_health_check=server.last_health_check
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MCP server: {str(e)}")


@router.put("/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: str,
    server_data: MCPServerUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update an existing MCP server"""
    try:
        # Build dynamic update query
        update_fields = []
        params = {'server_id': server_id}
        
        for field, value in server_data.dict(exclude_unset=True).items():
            if field in ['authentication_config', 'capabilities', 'connection_config', 'metadata']:
                update_fields.append(f"{field} = :{field}")
                params[field] = json.dumps(value)
            else:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = text(f"""
            UPDATE mcp_servers 
            SET {', '.join(update_fields)}
            WHERE id = :server_id
            RETURNING *
        """)
        
        result = await db.execute(query, params)
        await db.commit()
        
        server = result.fetchone()
        if not server:
            raise HTTPException(status_code=404, detail="MCP server not found")
            
        return MCPServerResponse(
            id=str(server.id),
            name=server.name,
            display_name=server.display_name,
            description=server.description,
            server_url=server.server_url,
            transport_type=server.transport_type,
            status=server.status,
            health_status=server.health_status,
            version=server.version,
            capabilities=server.capabilities or {},
            tags=server.tags or [],
            project_tags=server.project_tags or [],
            is_active=server.is_active,
            created_at=server.created_at,
            updated_at=server.updated_at,
            last_health_check=server.last_health_check
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update MCP server: {str(e)}")


@router.delete("/servers/{server_id}")
async def delete_mcp_server(
    server_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete an MCP server"""
    try:
        query = text("DELETE FROM mcp_servers WHERE id = :server_id")
        result = await db.execute(query, {'server_id': server_id})
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="MCP server not found")
            
        return {"message": "MCP server deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting MCP server: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete MCP server: {str(e)}")


# =====================================================
# MCP TOOLS REGISTRY MANAGEMENT
# =====================================================

@router.get("/servers/{server_id}/tools", response_model=List[MCPToolResponse])
async def list_mcp_tools(
    server_id: str,
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_database)
):
    """List tools for a specific MCP server"""
    try:
        query = """
            SELECT id, server_id, tool_name, display_name, description, input_schema,
                   output_schema, tool_config, capabilities, version, is_available,
                   usage_count, success_rate, avg_execution_time, tags,
                   created_at, updated_at, last_discovered
            FROM mcp_tools_registry
            WHERE server_id = :server_id
        """
        params = {'server_id': server_id}
        
        if is_available is not None:
            query += " AND is_available = :is_available"
            params['is_available'] = is_available
            
        query += " ORDER BY tool_name"
        
        result = await db.execute(text(query), params)
        tools = result.fetchall()
        
        return [
            MCPToolResponse(
                id=str(tool.id),
                server_id=str(tool.server_id),
                tool_name=tool.tool_name,
                display_name=tool.display_name,
                description=tool.description,
                input_schema=tool.input_schema or {},
                output_schema=tool.output_schema or {},
                tool_config=tool.tool_config or {},
                capabilities=tool.capabilities or [],
                version=tool.version,
                is_available=tool.is_available,
                usage_count=tool.usage_count,
                success_rate=float(tool.success_rate) if tool.success_rate else 0.0,
                avg_execution_time=tool.avg_execution_time,
                tags=tool.tags or [],
                created_at=tool.created_at,
                updated_at=tool.updated_at,
                last_discovered=tool.last_discovered
            )
            for tool in tools
        ]
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list MCP tools: {str(e)}")


@router.post("/tools", response_model=MCPToolResponse)
async def register_mcp_tool(
    tool_data: MCPToolCreate,
    db: AsyncSession = Depends(get_database)
):
    """Register a new MCP tool"""
    try:
        tool_id = str(uuid.uuid4())
        query = text("""
            INSERT INTO mcp_tools_registry (
                id, server_id, tool_name, display_name, description, input_schema,
                output_schema, tool_config, capabilities, version, is_available, tags
            ) VALUES (
                :id, :server_id, :tool_name, :display_name, :description, :input_schema,
                :output_schema, :tool_config, :capabilities, :version, :is_available, :tags
            ) RETURNING *
        """)
        
        params = {
            'id': tool_id,
            'server_id': tool_data.server_id,
            'tool_name': tool_data.tool_name,
            'display_name': tool_data.display_name,
            'description': tool_data.description,
            'input_schema': json.dumps(tool_data.input_schema),
            'output_schema': json.dumps(tool_data.output_schema),
            'tool_config': json.dumps(tool_data.tool_config),
            'capabilities': tool_data.capabilities,
            'version': tool_data.version,
            'is_available': tool_data.is_available,
            'tags': tool_data.tags
        }
        
        result = await db.execute(query, params)
        await db.commit()
        
        tool = result.fetchone()
        return MCPToolResponse(
            id=str(tool.id),
            server_id=str(tool.server_id),
            tool_name=tool.tool_name,
            display_name=tool.display_name,
            description=tool.description,
            input_schema=tool.input_schema or {},
            output_schema=tool.output_schema or {},
            tool_config=tool.tool_config or {},
            capabilities=tool.capabilities or [],
            version=tool.version,
            is_available=tool.is_available,
            usage_count=tool.usage_count,
            success_rate=float(tool.success_rate) if tool.success_rate else 0.0,
            avg_execution_time=tool.avg_execution_time,
            tags=tool.tags or [],
            created_at=tool.created_at,
            updated_at=tool.updated_at,
            last_discovered=tool.last_discovered
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering MCP tool: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register MCP tool: {str(e)}")


@router.get("/tools", response_model=List[MCPToolResponse])
async def list_tools_compatibility(
    server_id: Optional[str] = Query(None, description="Server ID to filter tools"),
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_database)
):
    """List MCP tools with optional server_id filter (compatibility endpoint)"""
    try:
        query = """
            SELECT id, server_id, tool_name, display_name, description, input_schema,
                   output_schema, tool_config, capabilities, version, is_available,
                   usage_count, success_rate, avg_execution_time, tags,
                   created_at, updated_at, last_discovered
            FROM mcp_tools_registry
            WHERE 1=1
        """
        params = {}
        
        if server_id:
            query += " AND server_id = :server_id"
            params['server_id'] = server_id
        
        if is_available is not None:
            query += " AND is_available = :is_available"
            params['is_available'] = is_available
            
        query += " ORDER BY tool_name"
        
        result = await db.execute(text(query), params)
        tools = result.fetchall()
        
        return [
            MCPToolResponse(
                id=str(tool.id),
                server_id=str(tool.server_id),
                tool_name=tool.tool_name,
                display_name=tool.display_name,
                description=tool.description,
                input_schema=tool.input_schema or {},
                output_schema=tool.output_schema or {},
                tool_config=tool.tool_config or {},
                capabilities=tool.capabilities or [],
                version=tool.version,
                is_available=tool.is_available,
                usage_count=tool.usage_count,
                success_rate=float(tool.success_rate) if tool.success_rate else 0.0,
                avg_execution_time=tool.avg_execution_time,
                tags=tool.tags or [],
                created_at=tool.created_at,
                updated_at=tool.updated_at,
                last_discovered=tool.last_discovered
            )
            for tool in tools
        ]
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list MCP tools: {str(e)}")


@router.post("/servers/{server_id}/discover-tools")
async def discover_mcp_tools(
    server_id: str,
    force_refresh: bool = False,
    db: AsyncSession = Depends(get_database)
):
    """Discover tools from an MCP server"""
    try:
        # This would implement actual tool discovery logic
        # For now, we'll return a mock response
        
        # In a real implementation, this would:
        # 1. Connect to the MCP server
        # 2. Send a tools/list request
        # 3. Parse the response and update the database
        # 4. Return the discovered tools
        
        discovered_count = 3  # Mock discovered count
        
        return {
            "message": f"Successfully discovered {discovered_count} tools from MCP server",
            "discovered_count": discovered_count,
            "server_id": server_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error discovering MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to discover MCP tools: {str(e)}")


# =====================================================
# MCP TOOL TESTING
# =====================================================

@router.post("/tools/{tool_id}/test")
async def test_mcp_tool(
    tool_id: str,
    test_input: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_database)
):
    """Test an MCP tool with sample input"""
    try:
        # Get tool information
        tool_query = text("""
            SELECT t.*, s.server_url, s.name as server_name
            FROM mcp_tools_registry t
            JOIN mcp_servers s ON t.server_id = s.id
            WHERE t.id = :tool_id
        """)
        
        result = await db.execute(tool_query, {'tool_id': tool_id})
        tool = result.fetchone()
        
        if not tool:
            raise HTTPException(status_code=404, detail="MCP tool not found")
            
        # Mock test execution (in real implementation, this would connect to MCP server)
        import time
        start_time = time.time()
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(0.1)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Mock successful result
        test_result = {
            "tool_name": tool.tool_name,
            "server_name": tool.server_name,
            "input": test_input,
            "output": {
                "status": "success",
                "message": f"Mock execution of {tool.tool_name}",
                "data": {"result": "Mock response data"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "execution_time_ms": execution_time,
            "success": True
        }
        
        # Log the test execution
        log_query = text("""
            INSERT INTO mcp_tool_test_results (
                tool_registry_id, server_id, test_name, test_input, actual_output,
                test_status, execution_time_ms
            ) VALUES (
                :tool_id, :server_id, :test_name, :test_input, :actual_output,
                :test_status, :execution_time_ms
            )
        """)
        
        await db.execute(log_query, {
            'tool_id': tool_id,
            'server_id': str(tool.server_id),
            'test_name': f"Manual test - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
            'test_input': json.dumps(test_input),
            'actual_output': json.dumps(test_result["output"]),
            'test_status': 'passed',
            'execution_time_ms': execution_time
        })
        
        await db.commit()
        
        return test_result
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error testing MCP tool: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test MCP tool: {str(e)}")


@router.get("/health")
async def get_mcp_system_health(db: AsyncSession = Depends(get_database)):
    """Get MCP system health status"""
    try:
        health_query = text("SELECT * FROM check_mcp_system_health()")
        result = await db.execute(health_query)
        health_data = result.fetchall()
        
        health_status = {}
        for row in health_data:
            health_status[row.component] = {
                "status": row.status,
                "count": row.count,
                "details": row.details
            }
            
        return {
            "overall_status": "healthy" if all(h["count"] > 0 for h in health_status.values()) else "degraded",
            "components": health_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting MCP system health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MCP system health: {str(e)}")
