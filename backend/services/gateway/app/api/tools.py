"""
API for tools registry with full signature support
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from ..core.database import get_database
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/")
async def get_all_tools(db: AsyncSession = Depends(get_database)):
    """Get all tools with basic information"""
    
    try:
        result_query = await db.execute(
            text("""
                SELECT name, display_name, description, category, type, version, status,
                dns_name, health_url, tags, execution_count, success_rate, is_active
                FROM tool_templates
            """)
        )
        tools = result_query.fetchall()
        
        result = []
        for tool in tools:
            result.append({
                "name": tool.name,
                "display_name": tool.display_name,
                "description": tool.description,
                "category": tool.category,
                "type": tool.type,
                "version": tool.version,
                "status": tool.status,
                "dns_name": tool.dns_name,
                "health_url": tool.health_url,
                "tags": tool.tags or [],
                "execution_count": tool.execution_count,
                "success_rate": float(tool.success_rate) if tool.success_rate else None,
                "is_active": tool.is_active
            })
        
        return {"tools": result}
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return {"tools": []}


@router.get("/templates")
async def get_tool_templates(db: AsyncSession = Depends(get_database)):
    """Get all tool templates with their fields"""
    try:
        # Get templates
        templates_query = await db.execute(
            text("""
                SELECT id, name, display_name, description, category, type, version, 
                is_active, icon, tags, created_at
                FROM tool_templates
            """)
        )
        templates = templates_query.fetchall()
        
        result = []
        for template in templates:
            # Get fields for this template
            fields_query = await db.execute(
                text("""
                    SELECT id, field_name, field_label, field_type, field_description,
                    is_required, is_secret, default_value, validation_rules,
                    field_options, field_order
                    FROM tool_template_fields
                    WHERE tool_template_id = :template_id
                """), {"template_id": template.id}
            )
            fields = fields_query.fetchall()
            
            # Build fields array
            template_fields = []
            for field in fields:
                template_fields.append({
                    "id": str(field.id),
                    "field_name": field.field_name,
                    "field_label": field.field_label,
                    "field_type": field.field_type,
                    "field_description": field.field_description,
                    "is_required": field.is_required,
                    "is_secret": field.is_secret,
                    "default_value": field.default_value,
                    "validation_rules": field.validation_rules,
                    "field_options": field.field_options,
                    "field_order": field.field_order
                })
            
            # Sort fields by field_order
            template_fields.sort(key=lambda x: x.get("field_order", 0))
            
            result.append({
                "id": str(template.id),
                "name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "category": template.category,
                "type": template.type,
                "version": template.version,
                "is_active": template.is_active,
                "icon": template.icon,
                "tags": template.tags or [],
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "fields": template_fields
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting tool templates: {e}")
        # Return empty result if tables don't exist
        return []


@router.get("/instances")
async def get_tool_instances(db: AsyncSession = Depends(get_database)):
    """Get all tool instances from tool_instances table"""
    
    try:
        result_query = await db.execute(
            text("""
                SELECT id, name, display_name, template_name, status, configuration,
                created_at, updated_at, created_by
                FROM tool_instances
            """)
        )
        instances = result_query.fetchall()
        
        result = []
        for instance in instances:
            # Parse JSON configuration safely
            config = instance.configuration
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except (json.JSONDecodeError, TypeError):
                    config = {}
            
            result.append({
                "id": str(instance.id),
                "name": instance.name,
                "display_name": instance.display_name,
                "template_name": instance.template_name,
                "status": instance.status,
                "configuration": config,
                "created_at": instance.created_at.isoformat() if instance.created_at else None,
                "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
                "created_by": instance.created_by
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting tool instances: {e}")
        return []


@router.get("/llm-models")
async def get_llm_models(db: AsyncSession = Depends(get_database)):
    """Get all LLM models with full details"""
    
    try:
        result_query = await db.execute(
            text("""
                SELECT id, name, display_name, provider, model_type, api_endpoint, 
                status, capabilities, pricing_info, performance_metrics,
                model_config, api_key, health_url, dns_name,
                created_at, updated_at
                FROM llm_models
            """)
        )
        models = result_query.fetchall()
        
        result = []
        for model in models:
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
            
            result.append({
                "id": str(model.id),
                "name": model.name,
                "display_name": model.display_name,
                "provider": model.provider,
                "model_type": model.model_type,
                "api_endpoint": model.api_endpoint,
                "status": model.status,
                "capabilities": safe_json_parse(model.capabilities),
                "pricing_info": safe_json_parse(model.pricing_info),
                "performance_metrics": safe_json_parse(model.performance_metrics),
                "model_config": safe_json_parse(model.model_config),
                "api_key": "***" if model.api_key else None,  # Hide actual API key
                "health_url": model.health_url,
                "dns_name": model.dns_name,
                "created_at": model.created_at.isoformat() if model.created_at else None,
                "updated_at": model.updated_at.isoformat() if model.updated_at else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting LLM models: {e}")
        return []


@router.post("/llm-models")
async def create_llm_model(model_data: dict, db: AsyncSession = Depends(get_database)):
    """Create a new LLM model"""
    try:
        # Convert dict fields to JSON strings for database storage
        capabilities = json.dumps(model_data.get('capabilities', {}))
        pricing_info = json.dumps(model_data.get('pricing_info', {}))
        performance_metrics = json.dumps(model_data.get('performance_metrics', {}))
        model_config = json.dumps(model_data.get('model_config', {}))
        
        query = text("""
            INSERT INTO llm_models (
                name, display_name, provider, model_type, api_endpoint,
                status, capabilities, pricing_info, performance_metrics,
                model_config, api_key, health_url, dns_name, created_at, updated_at
            ) VALUES (
                :name, :display_name, :provider, :model_type, :api_endpoint,
                :status, :capabilities, :pricing_info, :performance_metrics,
                :model_config, :api_key, :health_url, :dns_name, NOW(), NOW()
            ) RETURNING id
        """)
        
        result = await db.execute(query, {
            'name': model_data['name'],
            'display_name': model_data['display_name'],
            'provider': model_data['provider'],
            'model_type': model_data['model_type'],
            'api_endpoint': model_data.get('api_endpoint'),
            'status': model_data.get('status', 'inactive'),
            'capabilities': capabilities,
            'pricing_info': pricing_info,
            'performance_metrics': performance_metrics,
            'model_config': model_config,
            'api_key': model_data.get('api_key'),
            'health_url': model_data.get('health_url'),
            'dns_name': model_data.get('dns_name')
        })
        
        await db.commit()
        row = result.fetchone()
        if row:
            new_id = row[0]
            return {"id": str(new_id), "message": "LLM model created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to get new model ID")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating LLM model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create LLM model: {str(e)}")


@router.put("/llm-models/{model_id}")
async def update_llm_model(model_id: str, model_data: dict, db: AsyncSession = Depends(get_database)):
    """Update an existing LLM model"""
    try:
        # Convert dict fields to JSON strings for database storage
        capabilities = json.dumps(model_data.get('capabilities', {}))
        pricing_info = json.dumps(model_data.get('pricing_info', {}))
        performance_metrics = json.dumps(model_data.get('performance_metrics', {}))
        model_config = json.dumps(model_data.get('model_config', {}))
        
        query = text("""
            UPDATE llm_models SET
                name = :name,
                display_name = :display_name,
                provider = :provider,
                model_type = :model_type,
                api_endpoint = :api_endpoint,
                status = :status,
                capabilities = :capabilities,
                pricing_info = :pricing_info,
                performance_metrics = :performance_metrics,
                model_config = :model_config,
                api_key = :api_key,
                health_url = :health_url,
                dns_name = :dns_name,
                updated_at = NOW()
            WHERE id = :model_id
        """)
        
        await db.execute(query, {
            'model_id': model_id,
            'name': model_data['name'],
            'display_name': model_data['display_name'],
            'provider': model_data['provider'],
            'model_type': model_data['model_type'],
            'api_endpoint': model_data.get('api_endpoint'),
            'status': model_data.get('status', 'inactive'),
            'capabilities': capabilities,
            'pricing_info': pricing_info,
            'performance_metrics': performance_metrics,
            'model_config': model_config,
            'api_key': model_data.get('api_key'),
            'health_url': model_data.get('health_url'),
            'dns_name': model_data.get('dns_name')
        })
        
        await db.commit()
        return {"message": "LLM model updated successfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating LLM model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update LLM model: {str(e)}")


@router.delete("/llm-models/{model_id}")
async def delete_llm_model(model_id: str, db: AsyncSession = Depends(get_database)):
    """Delete an LLM model"""
    try:
        query = text("DELETE FROM llm_models WHERE id = :model_id")
        await db.execute(query, {'model_id': model_id})
        await db.commit()
        
        # Check if the model exists by trying to find it first
        check_query = text("SELECT id FROM llm_models WHERE id = :model_id")
        check_result = await db.execute(check_query, {'model_id': model_id})
        if check_result.fetchone():
            raise HTTPException(status_code=500, detail="Failed to delete LLM model")
        
        return {"message": "LLM model deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting LLM model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete LLM model: {str(e)}")


@router.post("/llm-models/{model_id}/test")
async def test_llm_model(model_id: str, db: AsyncSession = Depends(get_database)):
    """Test an LLM model connection"""
    try:
        # Get model details
        query = text("SELECT * FROM llm_models WHERE id = :model_id")
        result = await db.execute(query, {'model_id': model_id})
        model = result.fetchone()
        
        if not model:
            raise HTTPException(status_code=404, detail="LLM model not found")
        
        # Here you would implement actual model testing logic
        # For now, we'll return a mock response
        
        # Update model status to testing
        await db.execute(
            text("UPDATE llm_models SET status = 'testing' WHERE id = :model_id"),
            {'model_id': model_id}
        )
        await db.commit()
        
        # Simulate API test (replace with actual testing logic)
        import asyncio
        await asyncio.sleep(1)  # Simulate network delay
        
        # For demo purposes, randomly succeed or fail
        import random
        success = random.random() > 0.3  # 70% success rate
        
        # Update status based on test result
        new_status = 'active' if success else 'error'
        await db.execute(
            text("UPDATE llm_models SET status = :status WHERE id = :model_id"),
            {'model_id': model_id, 'status': new_status}
        )
        await db.commit()
        
        return {
            "success": success,
            "message": "Model connection successful" if success else "Model connection failed",
            "status": new_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing LLM model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test LLM model: {str(e)}")


@router.get("/llm-models/{model_id}")
async def get_llm_model(model_id: str, db: AsyncSession = Depends(get_database)):
    """Get a specific LLM model by ID"""
    try:
        query = text("""
            SELECT id, name, display_name, provider, model_type, api_endpoint,
                   status, capabilities, pricing_info, performance_metrics,
                   model_config, api_key, health_url, dns_name,
                   created_at, updated_at
            FROM llm_models WHERE id = :model_id
        """)
        result = await db.execute(query, {'model_id': model_id})
        model = result.fetchone()
        
        if not model:
            raise HTTPException(status_code=404, detail="LLM model not found")
        
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
            "id": str(model.id),
            "name": model.name,
            "display_name": model.display_name,
            "provider": model.provider,
            "model_type": model.model_type,
            "api_endpoint": model.api_endpoint,
            "status": model.status,
            "capabilities": safe_json_parse(model.capabilities),
            "pricing_info": safe_json_parse(model.pricing_info),
            "performance_metrics": safe_json_parse(model.performance_metrics),
            "model_config": safe_json_parse(model.model_config),
            "api_key": "***" if model.api_key else None,  # Hide actual API key
            "health_url": model.health_url,
            "dns_name": model.dns_name,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LLM model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get LLM model: {str(e)}")


@router.get("/embedding-models")
async def get_embedding_models(db: AsyncSession = Depends(get_database)):
    """Get all embedding models"""
    
    try:
        result_query = await db.execute(
            text("""
                SELECT id, name, display_name, provider, model_type, api_endpoint,
                status, capabilities, pricing_info, performance_metrics,
                input_signature, output_signature, health_url, dns_name,
                created_at, updated_at
                FROM embedding_models
            """)
        )
        models = result_query.fetchall()
        
        result = []
        for model in models:
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
            
            result.append({
                "id": str(model.id),
                "name": model.name,
                "display_name": model.display_name,
                "provider": model.provider,
                "model_type": model.model_type,
                "api_endpoint": model.api_endpoint,
                "status": model.status,
                "capabilities": safe_json_parse(model.capabilities),
                "pricing_info": safe_json_parse(model.pricing_info),
                "performance_metrics": safe_json_parse(model.performance_metrics),
                "input_signature": safe_json_parse(model.input_signature),
                "output_signature": safe_json_parse(model.output_signature),
                "health_url": model.health_url,
                "dns_name": model.dns_name,
                "created_at": model.created_at.isoformat() if model.created_at else None,
                "updated_at": model.updated_at.isoformat() if model.updated_at else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting embedding models: {e}")
        return []


@router.get("/{tool_name}")
async def get_tool_details(tool_name: str, db: AsyncSession = Depends(get_database)):
    """Get detailed tool information including signatures"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, description, category, type, version, status, url, health_url, 
                   dns_name, card_url, default_input_modes, default_output_modes, capabilities,
                   input_signature, output_signature, ai_provider, model_name, model_config,
                   health_check_config, usage_metrics, external_services,
                   author, organization, environment, search_keywords,
                   tags, execution_count, success_rate, avg_response_time, is_active, icon,
                   created_at, updated_at, created_by
            FROM tool_templates 
            WHERE name = :tool_name
        """), {"tool_name": tool_name}
    )
    tool = result_query.fetchone()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
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
        "name": tool.name,
        "display_name": tool.display_name,
        "description": tool.description,
        "category": tool.category,
        "type": tool.type,
        "version": tool.version,
        "status": tool.status,
        "url": tool.url,
        "health_url": tool.health_url,
        "dns_name": tool.dns_name,
        "card_url": tool.card_url,
        "default_input_modes": tool.default_input_modes or [],
        "default_output_modes": tool.default_output_modes or [],
        "capabilities": safe_json_parse(tool.capabilities),
        "input_signature": safe_json_parse(tool.input_signature),
        "output_signature": safe_json_parse(tool.output_signature),
        "ai_provider": tool.ai_provider,
        "model_name": tool.model_name,
        "model_config": safe_json_parse(tool.model_config),
        "health_check_config": safe_json_parse(tool.health_check_config),
        "usage_metrics": safe_json_parse(tool.usage_metrics),
        "external_services": safe_json_parse(tool.external_services),
        "author": tool.author,
        "organization": tool.organization,
        "environment": tool.environment,
        "search_keywords": tool.search_keywords or [],
        "tags": tool.tags or [],
        "execution_count": tool.execution_count,
        "success_rate": float(tool.success_rate) if tool.success_rate else None,
        "avg_response_time": tool.avg_response_time,
        "is_active": tool.is_active,
        "icon": tool.icon,
        "created_at": tool.created_at.isoformat() if tool.created_at else None,
        "updated_at": tool.updated_at.isoformat() if tool.updated_at else None,
        "created_by": tool.created_by
    }


@router.get("/{tool_name}/signature")
async def get_tool_signature(tool_name: str, db: AsyncSession = Depends(get_database)):
    """Get tool input/output signature for integration"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, input_signature, output_signature, 
                   default_input_modes, default_output_modes, capabilities
            FROM tool_templates 
            WHERE name = :tool_name
        """), {"tool_name": tool_name}
    )
    tool = result_query.fetchone()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
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
        "name": tool.name,
        "display_name": tool.display_name,
        "input_signature": safe_json_parse(tool.input_signature),
        "output_signature": safe_json_parse(tool.output_signature),
        "default_input_modes": tool.default_input_modes or [],
        "default_output_modes": tool.default_output_modes or [],
        "capabilities": safe_json_parse(tool.capabilities)
    }


@router.get("/{tool_name}/health")
async def get_tool_health_config(tool_name: str, db: AsyncSession = Depends(get_database)):
    """Get tool health check configuration"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, health_url, dns_name, health_check_config
            FROM tool_templates 
            WHERE name = :tool_name
        """), {"tool_name": tool_name}
    )
    tool = result_query.fetchone()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
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
        "name": tool.name,
        "display_name": tool.display_name,
        "health_url": tool.health_url,
        "dns_name": tool.dns_name,
        "health_check_config": safe_json_parse(tool.health_check_config)
    }


@router.get("/category/{category}")
async def get_tools_by_category(category: str, db: AsyncSession = Depends(get_database)):
    """Get tools filtered by category"""
    
    result_query = await db.execute(
        text("""
            SELECT name, display_name, description, type, version, status,
                   dns_name, health_url, tags, execution_count, success_rate
            FROM tool_templates 
            WHERE category = :category
            ORDER BY name
        """), {"category": category}
    )
    tools = result_query.fetchall()
    
    result = []
    for tool in tools:
        result.append({
            "name": tool.name,
            "display_name": tool.display_name,
            "description": tool.description,
            "type": tool.type,
            "version": tool.version,
            "status": tool.status,
            "dns_name": tool.dns_name,
            "health_url": tool.health_url,
            "tags": tool.tags or [],
            "execution_count": tool.execution_count,
            "success_rate": float(tool.success_rate) if tool.success_rate else None
        })
    
    return {
        "category": category,
        "tools": result
    }
