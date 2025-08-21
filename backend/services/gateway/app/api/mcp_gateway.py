"""
MCP Gateway API endpoints for dynamic endpoint creation and management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_, or_
from typing import List, Optional, Dict, Any
import json
import logging
import uuid
from datetime import datetime, timezone
import asyncio
import aiohttp

from ..core.database import get_database
from ..models.mcp_models import (
    MCPEndpointCreate, MCPEndpointUpdate, MCPEndpointResponse,
    MCPToolBindingCreate, MCPToolBindingUpdate, MCPToolBindingResponse,
    MCPExecutionLogResponse, MCPExecutionRequest, MCPHealthStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp-gateway", tags=["mcp-gateway"])

# =====================================================
# MCP ENDPOINTS MANAGEMENT
# =====================================================

@router.get("/endpoints", response_model=List[MCPEndpointResponse])
async def list_mcp_endpoints(
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    project_tags: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_database)
):
    """List all MCP endpoints with optional filtering"""
    try:
        query = """
            SELECT id, endpoint_name, display_name, description, endpoint_path, endpoint_url,
                   status, authentication_required, is_public, tags, metadata,
                   created_at, updated_at
            FROM mcp_endpoints
            WHERE 1=1
        """
        params = {}
        
        if status:
            query += " AND status = :status"
            params['status'] = status
            
        if is_public is not None:
            query += " AND is_public = :is_public"
            params['is_public'] = is_public
            
        if project_tags:
            query += " AND project_tags && :project_tags"
            params['project_tags'] = project_tags
            
        query += " ORDER BY created_at DESC"
        
        result = await db.execute(text(query), params)
        endpoints = result.fetchall()
        
        return [
            MCPEndpointResponse(
                id=str(endpoint.id),
                endpoint_name=endpoint.endpoint_name,
                display_name=endpoint.display_name,
                description=endpoint.description,
                endpoint_path=endpoint.endpoint_path,
                endpoint_url=endpoint.endpoint_url,
                transport_config=endpoint.metadata.get('transport_config', {}) if endpoint.metadata else {},
                authentication_required=endpoint.authentication_required,
                status=endpoint.status,
                health_status=MCPHealthStatus(endpoint.metadata.get('health_status', 'unknown')) if endpoint.metadata and endpoint.metadata.get('health_status') in ['healthy', 'unhealthy', 'unknown', 'degraded'] else MCPHealthStatus.unknown,
                usage_analytics=endpoint.metadata.get('usage_analytics', {}) if endpoint.metadata else {},
                tags=endpoint.tags or [],
                project_tags=endpoint.metadata.get('project_tags', []) if endpoint.metadata else [],
                is_public=endpoint.is_public,
                created_at=endpoint.created_at,
                updated_at=endpoint.updated_at,
                last_health_check=endpoint.metadata.get('last_health_check') if endpoint.metadata else None
            )
            for endpoint in endpoints
        ]
    except Exception as e:
        logger.error(f"Error listing MCP endpoints: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list MCP endpoints: {str(e)}")


@router.post("/endpoints", response_model=MCPEndpointResponse)
async def create_mcp_endpoint(
    endpoint_data: MCPEndpointCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new MCP endpoint"""
    try:
        endpoint_id = str(uuid.uuid4())
        
        # Generate endpoint URL based on path
        base_url = "http://localhost:8000"  # This should come from config
        endpoint_url = f"{base_url}{endpoint_data.endpoint_path}"
        
        query = text("""
            INSERT INTO mcp_endpoints (
                id, endpoint_name, display_name, description, endpoint_path, endpoint_url,
                transport_config, authentication_required, authentication_config,
                rate_limiting, timeout_config, middleware_config, status,
                metadata, tags, project_tags, is_public
            ) VALUES (
                :id, :endpoint_name, :display_name, :description, :endpoint_path, :endpoint_url,
                :transport_config, :authentication_required, :authentication_config,
                :rate_limiting, :timeout_config, :middleware_config, :status,
                :metadata, :tags, :project_tags, :is_public
            ) RETURNING *
        """)
        
        params = {
            'id': endpoint_id,
            'endpoint_name': endpoint_data.endpoint_name,
            'display_name': endpoint_data.display_name,
            'description': endpoint_data.description,
            'endpoint_path': endpoint_data.endpoint_path,
            'endpoint_url': endpoint_url,
            'transport_config': json.dumps(endpoint_data.transport_config),
            'authentication_required': endpoint_data.authentication_required,
            'authentication_config': json.dumps(endpoint_data.authentication_config),
            'rate_limiting': json.dumps(endpoint_data.rate_limiting),
            'timeout_config': json.dumps(endpoint_data.timeout_config),
            'middleware_config': json.dumps(endpoint_data.middleware_config),
            'status': endpoint_data.status,
            'metadata': json.dumps(endpoint_data.metadata),
            'tags': endpoint_data.tags,
            'project_tags': endpoint_data.project_tags,
            'is_public': endpoint_data.is_public
        }
        
        result = await db.execute(query, params)
        await db.commit()
        
        endpoint = result.fetchone()
        return MCPEndpointResponse(
            id=str(endpoint.id),
            endpoint_name=endpoint.endpoint_name,
            display_name=endpoint.display_name,
            description=endpoint.description,
            endpoint_path=endpoint.endpoint_path,
            endpoint_url=endpoint.endpoint_url,
            transport_config=endpoint.transport_config or {},
            authentication_required=endpoint.authentication_required,
            status=endpoint.status,
            health_status=endpoint.health_status,
            usage_analytics=endpoint.usage_analytics or {},
            tags=endpoint.tags or [],
            project_tags=endpoint.project_tags or [],
            is_public=endpoint.is_public,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            last_health_check=endpoint.last_health_check
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create MCP endpoint: {str(e)}")


@router.get("/endpoints/{endpoint_id}", response_model=MCPEndpointResponse)
async def get_mcp_endpoint(
    endpoint_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get a specific MCP endpoint by ID"""
    try:
        query = text("""
            SELECT id, endpoint_name, display_name, description, endpoint_path, endpoint_url,
                   transport_config, authentication_required, authentication_config,
                   rate_limiting, timeout_config, middleware_config, status, health_status,
                   usage_analytics, metadata, tags, project_tags, is_public,
                   created_at, updated_at, last_health_check
            FROM mcp_endpoints
            WHERE id = :endpoint_id
        """)
        
        result = await db.execute(query, {'endpoint_id': endpoint_id})
        endpoint = result.fetchone()
        
        if not endpoint:
            raise HTTPException(status_code=404, detail="MCP endpoint not found")
            
        return MCPEndpointResponse(
            id=str(endpoint.id),
            endpoint_name=endpoint.endpoint_name,
            display_name=endpoint.display_name,
            description=endpoint.description,
            endpoint_path=endpoint.endpoint_path,
            endpoint_url=endpoint.endpoint_url,
            transport_config=endpoint.transport_config or {},
            authentication_required=endpoint.authentication_required,
            status=endpoint.status,
            health_status=endpoint.health_status,
            usage_analytics=endpoint.usage_analytics or {},
            tags=endpoint.tags or [],
            project_tags=endpoint.project_tags or [],
            is_public=endpoint.is_public,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            last_health_check=endpoint.last_health_check
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get MCP endpoint: {str(e)}")


@router.put("/endpoints/{endpoint_id}", response_model=MCPEndpointResponse)
async def update_mcp_endpoint(
    endpoint_id: str,
    endpoint_data: MCPEndpointUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update an existing MCP endpoint"""
    try:
        # Build dynamic update query
        update_fields = []
        params = {'endpoint_id': endpoint_id}
        
        for field, value in endpoint_data.dict(exclude_unset=True).items():
            if field in ['transport_config', 'authentication_config', 'rate_limiting', 
                        'timeout_config', 'middleware_config', 'metadata']:
                update_fields.append(f"{field} = :{field}")
                params[field] = json.dumps(value)
            else:
                update_fields.append(f"{field} = :{field}")
                params[field] = value
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = text(f"""
            UPDATE mcp_endpoints 
            SET {', '.join(update_fields)}
            WHERE id = :endpoint_id
            RETURNING *
        """)
        
        result = await db.execute(query, params)
        await db.commit()
        
        endpoint = result.fetchone()
        if not endpoint:
            raise HTTPException(status_code=404, detail="MCP endpoint not found")
            
        return MCPEndpointResponse(
            id=str(endpoint.id),
            endpoint_name=endpoint.endpoint_name,
            display_name=endpoint.display_name,
            description=endpoint.description,
            endpoint_path=endpoint.endpoint_path,
            endpoint_url=endpoint.endpoint_url,
            transport_config=endpoint.transport_config or {},
            authentication_required=endpoint.authentication_required,
            status=endpoint.status,
            health_status=endpoint.health_status,
            usage_analytics=endpoint.usage_analytics or {},
            tags=endpoint.tags or [],
            project_tags=endpoint.project_tags or [],
            is_public=endpoint.is_public,
            created_at=endpoint.created_at,
            updated_at=endpoint.updated_at,
            last_health_check=endpoint.last_health_check
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update MCP endpoint: {str(e)}")


@router.delete("/endpoints/{endpoint_id}")
async def delete_mcp_endpoint(
    endpoint_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete an MCP endpoint"""
    try:
        query = text("DELETE FROM mcp_endpoints WHERE id = :endpoint_id")
        result = await db.execute(query, {'endpoint_id': endpoint_id})
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="MCP endpoint not found")
            
        return {"message": "MCP endpoint deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete MCP endpoint: {str(e)}")


# =====================================================
# TOOL BINDINGS MANAGEMENT
# =====================================================

@router.get("/endpoints/{endpoint_id}/bindings", response_model=List[MCPToolBindingResponse])
async def list_endpoint_tool_bindings(
    endpoint_id: str,
    is_enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_database)
):
    """List tool bindings for an MCP endpoint"""
    try:
        query = """
            SELECT b.id, b.endpoint_id, b.tool_registry_id, b.server_id, b.tool_name,
                   b.binding_name, b.binding_config, b.parameter_mapping, b.execution_order,
                   b.is_enabled, b.created_at, b.updated_at,
                   t.display_name as tool_display_name, t.description as tool_description,
                   s.name as server_name, s.display_name as server_display_name
            FROM mcp_endpoint_tool_bindings b
            LEFT JOIN mcp_tools_registry t ON b.tool_registry_id = t.id
            LEFT JOIN mcp_servers s ON b.server_id = s.id
            WHERE b.endpoint_id = :endpoint_id
        """
        params = {'endpoint_id': endpoint_id}
        
        if is_enabled is not None:
            query += " AND b.is_enabled = :is_enabled"
            params['is_enabled'] = is_enabled
            
        query += " ORDER BY b.execution_order, b.binding_name"
        
        result = await db.execute(text(query), params)
        bindings = result.fetchall()
        
        return [
            MCPToolBindingResponse(
                id=str(binding.id),
                endpoint_id=str(binding.endpoint_id),
                tool_registry_id=str(binding.tool_registry_id) if binding.tool_registry_id else None,
                server_id=str(binding.server_id) if binding.server_id else None,
                tool_name=binding.tool_name,
                binding_name=binding.binding_name,
                binding_config=binding.binding_config or {},
                parameter_mapping=binding.parameter_mapping or {},
                execution_order=binding.execution_order,
                is_enabled=binding.is_enabled,
                tool_display_name=binding.tool_display_name,
                tool_description=binding.tool_description,
                server_name=binding.server_name,
                created_at=binding.created_at,
                updated_at=binding.updated_at
            )
            for binding in bindings
        ]
    except Exception as e:
        logger.error(f"Error listing tool bindings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tool bindings: {str(e)}")


@router.post("/endpoints/{endpoint_id}/bindings", response_model=MCPToolBindingResponse)
async def create_tool_binding(
    endpoint_id: str,
    binding_data: MCPToolBindingCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new tool binding for an MCP endpoint"""
    try:
        binding_id = str(uuid.uuid4())
        
        query = text("""
            INSERT INTO mcp_endpoint_tool_bindings (
                id, endpoint_id, tool_registry_id, server_id, tool_name, binding_name,
                binding_config, parameter_mapping, middleware_config, execution_order,
                is_enabled, conditional_execution, error_handling, retry_config
            ) VALUES (
                :id, :endpoint_id, :tool_registry_id, :server_id, :tool_name, :binding_name,
                :binding_config, :parameter_mapping, :middleware_config, :execution_order,
                :is_enabled, :conditional_execution, :error_handling, :retry_config
            ) RETURNING *
        """)
        
        params = {
            'id': binding_id,
            'endpoint_id': endpoint_id,
            'tool_registry_id': binding_data.tool_registry_id,
            'server_id': binding_data.server_id,
            'tool_name': binding_data.tool_name,
            'binding_name': binding_data.binding_name,
            'binding_config': json.dumps(binding_data.binding_config),
            'parameter_mapping': json.dumps(binding_data.parameter_mapping),
            'middleware_config': json.dumps(binding_data.middleware_config),
            'execution_order': binding_data.execution_order,
            'is_enabled': binding_data.is_enabled,
            'conditional_execution': json.dumps(binding_data.conditional_execution),
            'error_handling': json.dumps(binding_data.error_handling),
            'retry_config': json.dumps(binding_data.retry_config)
        }
        
        result = await db.execute(query, params)
        await db.commit()
        
        binding = result.fetchone()
        return MCPToolBindingResponse(
            id=str(binding.id),
            endpoint_id=str(binding.endpoint_id),
            tool_registry_id=str(binding.tool_registry_id) if binding.tool_registry_id else None,
            server_id=str(binding.server_id) if binding.server_id else None,
            tool_name=binding.tool_name,
            binding_name=binding.binding_name,
            binding_config=binding.binding_config or {},
            parameter_mapping=binding.parameter_mapping or {},
            execution_order=binding.execution_order,
            is_enabled=binding.is_enabled,
            created_at=binding.created_at,
            updated_at=binding.updated_at
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating tool binding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tool binding: {str(e)}")


# =====================================================
# DYNAMIC ENDPOINT EXECUTION
# =====================================================

@router.post("/endpoints/{endpoint_name}/execute")
async def execute_endpoint(
    endpoint_name: str,
    execution_request: MCPExecutionRequest,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Execute tools bound to an MCP endpoint"""
    try:
        # Get endpoint information (simplified without tool bindings for now)
        query = text("""
            SELECT e.*
            FROM mcp_endpoints e
            WHERE e.endpoint_name = :endpoint_name AND e.status = 'active'
        """)
        
        result = await db.execute(query, {'endpoint_name': endpoint_name})
        endpoint_data = result.fetchone()
        
        if not endpoint_data:
            raise HTTPException(status_code=404, detail="MCP endpoint not found or inactive")
            
        execution_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        # Since we don't have tool bindings table yet, simulate a simple execution
        # In the future, this would execute actual MCP tools bound to the endpoint
        results = []
        total_execution_time = 0
        
        # Mock execution for the endpoint
        try:
            binding_start = datetime.now(timezone.utc)
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            binding_end = datetime.now(timezone.utc)
            execution_time = int((binding_end - binding_start).total_seconds() * 1000)
            total_execution_time += execution_time
            
            # Mock successful result
            result_data = {
                'tool_name': f"{endpoint_data.endpoint_name}_mock_tool",
                'binding_name': 'default_binding',
                'status': 'completed',
                'execution_time_ms': execution_time,
                'result': {
                    'message': f'Successfully executed endpoint {endpoint_data.endpoint_name}',
                    'parameters': execution_request.parameters,
                    'timestamp': start_time.isoformat()
                },
                'error': None
            }
            results.append(result_data)
            
        except Exception as e:
            logger.error(f"Error executing endpoint {endpoint_data.endpoint_name}: {e}")
            binding_end = datetime.now(timezone.utc)
            execution_time = int((binding_end - binding_start).total_seconds() * 1000)
            total_execution_time += execution_time
            
            result_data = {
                'tool_name': f"{endpoint_data.endpoint_name}_mock_tool",
                'binding_name': 'default_binding',
                'status': 'failed',
                'execution_time_ms': execution_time,
                'result': None,
                'error': str(e)
            }
            results.append(result_data)
        
        end_time = datetime.now(timezone.utc)
        total_execution_time = int((end_time - start_time).total_seconds() * 1000)
        
        # Log execution to database
        try:
            log_query = text("""
                INSERT INTO mcp_execution_logs (
                    endpoint_id, tool_id, execution_type, input_parameters, 
                    output_result, execution_status, execution_time_ms,
                    error_message, user_id, created_at
                ) VALUES (
                    :endpoint_id, :tool_id, :execution_type, :input_parameters,
                    :output_result, :execution_status, :execution_time_ms,
                    :error_message, :user_id, :created_at
                )
            """)
            
            await db.execute(log_query, {
                'endpoint_id': str(endpoint_data.id),
                'tool_id': None,  # No specific tool ID for mock execution
                'execution_type': 'endpoint_execution',
                'input_parameters': json.dumps(execution_request.parameters),
                'output_result': json.dumps(results),
                'execution_status': 'completed' if all(r['status'] == 'completed' for r in results) else 'failed',
                'execution_time_ms': total_execution_time,
                'error_message': None,
                'user_id': getattr(request.state, 'user_id', 'anonymous'),
                'created_at': end_time
            })
            await db.commit()
        except Exception as log_error:
            logger.warning(f"Failed to log execution: {log_error}")
        
        return {
            "execution_id": execution_id,
            "endpoint_name": endpoint_data.endpoint_name,
            "status": "completed" if all(r['status'] == 'completed' for r in results) else "failed",
            "total_execution_time_ms": total_execution_time,
            "results": results,
            "executed_at": start_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute MCP endpoint: {str(e)}")


# =====================================================
# EXECUTION LOGS
# =====================================================

@router.get("/execution-logs")
async def get_execution_logs(
    endpoint_id: Optional[str] = None,
    execution_status: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_database)
):
    """Get MCP execution logs with filtering and pagination"""
    try:
        query = """
            SELECT l.*, e.endpoint_name, e.display_name as endpoint_display_name
            FROM mcp_execution_logs l
            LEFT JOIN mcp_endpoints e ON l.endpoint_id = e.id
            WHERE 1=1
        """
        params = {'limit': limit, 'offset': offset}
        
        if endpoint_id:
            query += " AND l.endpoint_id = :endpoint_id"
            params['endpoint_id'] = endpoint_id
            
        if execution_status:
            query += " AND l.execution_status = :execution_status"
            params['execution_status'] = execution_status
            
        query += " ORDER BY l.created_at DESC LIMIT :limit OFFSET :offset"
        
        result = await db.execute(text(query), params)
        logs = result.fetchall()
        
        return [
            MCPExecutionLogResponse(
                id=str(log.id),
                endpoint_id=str(log.endpoint_id) if log.endpoint_id else None,
                endpoint_name=log.endpoint_name if hasattr(log, 'endpoint_name') else None,
                tool_name=log.execution_type if hasattr(log, 'execution_type') else 'unknown',
                execution_id=str(log.id),  # Use log id as execution_id
                execution_status='completed' if log.execution_status == 'success' else log.execution_status,
                execution_time_ms=log.execution_time_ms,
                server_name=None,  # No server info available in current schema
                started_at=log.created_at,  # Use created_at as started_at
                completed_at=log.created_at  # Use created_at as completed_at for now
            )
            for log in logs
        ]
    except Exception as e:
        logger.error(f"Error getting execution logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get execution logs: {str(e)}")


@router.get("/endpoints/{endpoint_id}/analytics")
async def get_endpoint_analytics(
    endpoint_id: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_database)
):
    """Get analytics for a specific MCP endpoint"""
    try:
        # For now, return mock analytics since we don't have comprehensive logging yet
        return {
            "endpoint_id": endpoint_id,
            "analytics_period_days": days,
            "total_executions": 42,
            "successful_executions": 38,
            "failed_executions": 4,
            "success_rate": 90.5,
            "average_execution_time_ms": 156,
            "last_execution": "2024-01-15T10:30:00Z",
            "executions_per_day": [
                {"date": "2024-01-15", "count": 12},
                {"date": "2024-01-14", "count": 8},
                {"date": "2024-01-13", "count": 15},
            ],
            "most_used_tools": [
                {"tool_name": "mock_tool_1", "count": 25},
                {"tool_name": "mock_tool_2", "count": 17},
            ],
            "error_breakdown": [
                {"error_type": "timeout", "count": 2},
                {"error_type": "connection_error", "count": 2},
            ]
        }
    except Exception as e:
        logger.error(f"Error getting endpoint analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get endpoint analytics: {str(e)}")
