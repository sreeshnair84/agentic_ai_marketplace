"""
Tool Management Service
Central service for managing tool templates and instances
"""

import asyncio
import asyncpg
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

class ToolManagementService:
    """Service for managing tool templates and instances"""
    
    def __init__(self):
        self.connection_pool: Optional[asyncpg.Pool] = None
        self.logger = logger
    
    async def initialize(self, database_url: str):
        """Initialize the service with database connection pool and async limits"""
        min_size = int(os.getenv("TOOLS_DB_POOL_MIN_SIZE", 2))
        max_size = int(os.getenv("TOOLS_DB_POOL_MAX_SIZE", 10))
        self.connection_pool = await asyncpg.create_pool(
            database_url,
            min_size=min_size,
            max_size=max_size,
            timeout=10
        )

    def _get_pool(self):
        if self.connection_pool is None:
            raise RuntimeError("Database connection pool is not initialized. Call initialize() first.")
        return self.connection_pool

    # Retry decorator for DB operations
    @staticmethod
    def db_retry():
        return retry(stop=stop_after_attempt(3), wait=wait_fixed(1))

    # Health check method
    async def health_check(self) -> Dict[str, Any]:
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return {"status": "healthy", "db": "connected"}
        except Exception as e:
            self.logger.error(f"DB health check failed: {e}")
            return {"status": "unhealthy", "db": "disconnected", "error": str(e)}
    
    # Tool Template Methods
    
    @db_retry.__func__()
    async def create_tool_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tool template"""
        try:
            template_id = str(uuid.uuid4())
            pool = self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tool_templates 
                    (id, name, description, tool_type, category, version, 
                     configuration_schema, input_schema, output_schema, 
                     template_config, default_config, is_active, 
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                    template_id,
                    template_data["name"],
                    template_data["description"],
                    template_data["tool_type"],
                    template_data.get("category"),
                    template_data.get("version", "1.0.0"),
                    json.dumps(template_data.get("configuration_schema", {})),
                    json.dumps(template_data.get("input_schema", {})),
                    json.dumps(template_data.get("output_schema", {})),
                    json.dumps(template_data.get("template_config", {})),
                    json.dumps(template_data.get("default_config", {})),
                    template_data.get("is_active", True),
                    datetime.utcnow(),
                    datetime.utcnow()
                )
            result = await self.get_tool_template(template_id)
            return result or {"error": "Tool template not found after creation."}
        except Exception as e:
            self.logger.error(f"Error creating tool template: {e}")
            return {"error": str(e)}
    
    async def get_tool_template(self, template_id: str) -> Dict[str, Any]:
        """Get a tool template by ID"""
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM tool_templates WHERE id = $1
                """, template_id)
            if not result:
                return {"error": f"Tool template {template_id} not found"}
            return self._format_template_result(result)
        except Exception as e:
            self.logger.error(f"Error getting tool template {template_id}: {e}")
            return {"error": str(e)}
    
    async def list_tool_templates(
        self, 
        category: Optional[str] = None, 
        tool_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List tool templates with filtering"""
        try:
            pool = self._get_pool()
            conditions = []
            params = []
            param_count = 0
            if category:
                param_count += 1
                conditions.append(f"category = ${param_count}")
                params.append(category)
            if tool_type:
                param_count += 1
                conditions.append(f"tool_type = ${param_count}")
                params.append(tool_type)
            if is_active is not None:
                param_count += 1
                conditions.append(f"is_active = ${param_count}")
                params.append(is_active)
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            # Add pagination
            param_count += 1
            limit_clause = f"LIMIT ${param_count}"
            params.append(limit)
            param_count += 1
            offset_clause = f"OFFSET ${param_count}"
            params.append(offset)
            async with pool.acquire() as conn:
                results = await conn.fetch(f"""
                    SELECT * FROM tool_templates 
                    {where_clause}
                    ORDER BY created_at DESC
                    {limit_clause} {offset_clause}
                """, *params)
                # Get total count
                count_result = await conn.fetchval(f"""
                    SELECT COUNT(*) FROM tool_templates {where_clause}
                """, *params[:-2])  # Exclude limit and offset
            templates = [self._format_template_result(row) for row in results]
            return {
                "templates": templates,
                "total": count_result,
                "offset": offset,
                "limit": limit
            }
        except Exception as e:
            self.logger.error(f"Error listing tool templates: {e}")
            return {"error": str(e)}
# NOTE: You must install the 'tenacity' package for retry logic:
#   pip install tenacity
    
    async def update_tool_template(self, template_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a tool template"""
        
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            param_count = 0
            
            for field, value in update_data.items():
                if field in ["name", "description", "tool_type", "category", "version", "is_active"]:
                    param_count += 1
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(value)
                elif field in ["configuration_schema", "input_schema", "output_schema", "template_config", "default_config"]:
                    param_count += 1
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(json.dumps(value))
            
            if not set_clauses:
                result = await self.get_tool_template(template_id)
                return result or {"error": f"Tool template {template_id} not found after update."}
            
            # Add updated_at
            param_count += 1
            set_clauses.append(f"updated_at = ${param_count}")
            params.append(datetime.utcnow())
            
            # Add template_id for WHERE clause
            param_count += 1
            params.append(template_id)
            
            pool = self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(f"""
                    UPDATE tool_templates 
                    SET {', '.join(set_clauses)}
                    WHERE id = ${param_count}
                """, *params)
            result = await self.get_tool_template(template_id)
            return result or {"error": f"Tool template {template_id} not found after update."}
        except Exception as e:
            self.logger.error(f"Error updating tool template {template_id}: {e}")
            return {"error": str(e)}
    
    async def delete_tool_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a tool template"""
        
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                # Check if template has instances
                instance_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM tool_instances WHERE template_id = $1
                """, template_id)
                if instance_count > 0:
                    # Soft delete - just mark as inactive
                    await conn.execute("""
                        UPDATE tool_templates 
                        SET is_active = false, updated_at = $1
                        WHERE id = $2
                    """, datetime.utcnow(), template_id)
                else:
                    # Hard delete
                    await conn.execute("""
                        DELETE FROM tool_templates WHERE id = $1
                    """, template_id)
            return {"success": True}
        except Exception as e:
            self.logger.error(f"Error deleting tool template {template_id}: {e}")
            return {"error": str(e)}
    
    # Tool Instance Methods
    
    async def create_tool_instance(self, instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tool instance"""
        
        try:
            instance_id = str(uuid.uuid4())
            pool = self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tool_instances 
                    (id, name, description, template_id, configuration, 
                     input_data, status, created_by, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                    instance_id,
                    instance_data["name"],
                    instance_data.get("description"),
                    instance_data["template_id"],
                    json.dumps(instance_data.get("configuration", {})),
                    json.dumps(instance_data.get("input_data", {})),
                    instance_data.get("status", "created"),
                    instance_data.get("created_by"),
                    datetime.utcnow(),
                    datetime.utcnow()
                )
            result = await self.get_tool_instance(instance_id)
            return result or {"error": f"Tool instance {instance_id} not found after creation."}
        except Exception as e:
            self.logger.error(f"Error creating tool instance: {e}")
            return {"error": str(e)}
    
    async def get_tool_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get a tool instance by ID"""
        
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT ti.*, tt.name as template_name, tt.tool_type
                    FROM tool_instances ti
                    LEFT JOIN tool_templates tt ON ti.template_id = tt.id
                    WHERE ti.id = $1
                """, instance_id)
            if not result:
                return {"error": f"Tool instance {instance_id} not found"}
            return self._format_instance_result(result)
        except Exception as e:
            self.logger.error(f"Error getting tool instance {instance_id}: {e}")
            return {"error": str(e)}
    
    async def list_tool_instances(
        self,
        template_id: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List tool instances with filtering"""
        
        try:
            conditions = []
            params = []
            param_count = 0
            
            if template_id:
                param_count += 1
                conditions.append(f"ti.template_id = ${param_count}")
                params.append(template_id)
            
            if status:
                param_count += 1
                conditions.append(f"ti.status = ${param_count}")
                params.append(status)
            
            if created_by:
                param_count += 1
                conditions.append(f"ti.created_by = ${param_count}")
                params.append(created_by)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Add pagination
            param_count += 1
            limit_clause = f"LIMIT ${param_count}"
            params.append(limit)
            
            param_count += 1
            offset_clause = f"OFFSET ${param_count}"
            params.append(offset)
            
            pool = self._get_pool()
            async with pool.acquire() as conn:
                results = await conn.fetch(f"""
                    SELECT ti.*, tt.name as template_name, tt.tool_type
                    FROM tool_instances ti
                    LEFT JOIN tool_templates tt ON ti.template_id = tt.id
                    {where_clause}
                    ORDER BY ti.created_at DESC
                    {limit_clause} {offset_clause}
                """, *params)
                
                # Get total count
                count_result = await conn.fetchval(f"""
                    SELECT COUNT(*) FROM tool_instances ti {where_clause}
                """, *params[:-2])  # Exclude limit and offset
            
            instances = [self._format_instance_result(row) for row in results]
            
            return {
                "instances": instances,
                "total": count_result,
                "offset": offset,
                "limit": limit
            }
            
        except Exception as e:
            self.logger.error(f"Error listing tool instances: {e}")
            raise
    
    async def update_tool_instance(self, instance_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a tool instance"""
        
        try:
            # Build dynamic update query
            set_clauses = []
            params = []
            param_count = 0
            
            for field, value in update_data.items():
                if field in ["name", "description", "status", "created_by"]:
                    param_count += 1
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(value)
                elif field in ["configuration", "input_data", "output_data"]:
                    param_count += 1
                    set_clauses.append(f"{field} = ${param_count}")
                    params.append(json.dumps(value))
            
            if not set_clauses:
                result = await self.get_tool_instance(instance_id)
                return result or {"error": f"Tool instance {instance_id} not found after update."}
            
            # Add updated_at
            param_count += 1
            set_clauses.append(f"updated_at = ${param_count}")
            params.append(datetime.utcnow())
            
            # Add instance_id for WHERE clause
            param_count += 1
            params.append(instance_id)
            
            pool = self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(f"""
                    UPDATE tool_instances 
                    SET {', '.join(set_clauses)}
                    WHERE id = ${param_count}
                """, *params)
            result = await self.get_tool_instance(instance_id)
            return result or {"error": f"Tool instance {instance_id} not found after update."}
        except Exception as e:
            self.logger.error(f"Error updating tool instance {instance_id}: {e}")
            return {"error": str(e)}
    
    async def delete_tool_instance(self, instance_id: str) -> Dict[str, Any]:
        """Delete a tool instance"""
        
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM tool_instances WHERE id = $1
                """, instance_id)
            return {"success": True}
        except Exception as e:
            self.logger.error(f"Error deleting tool instance {instance_id}: {e}")
            return {"error": str(e)}
    
    # Utility Methods
    
    async def get_template_categories(self) -> List[str]:
        """Get all unique template categories"""
        
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT DISTINCT category 
                    FROM tool_templates 
                    WHERE category IS NOT NULL 
                    ORDER BY category
                """)
            return [row["category"] for row in results]
        except Exception as e:
            self.logger.error(f"Error getting template categories: {e}")
            return []
    
    async def get_template_types(self) -> List[str]:
        """Get all unique template types"""
        
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT DISTINCT tool_type 
                    FROM tool_templates 
                    WHERE tool_type IS NOT NULL 
                    ORDER BY tool_type
                """)
            return [row["tool_type"] for row in results]
        except Exception as e:
            self.logger.error(f"Error getting template types: {e}")
            return []
    
    async def get_instance_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool instances"""
        
        try:
            pool = self._get_pool()
            async with pool.acquire() as conn:
                # Total instances
                total_instances = await conn.fetchval("""
                    SELECT COUNT(*) FROM tool_instances
                """)
                # Instances by status
                status_stats = await conn.fetch("""
                    SELECT status, COUNT(*) as count 
                    FROM tool_instances 
                    GROUP BY status
                """)
                # Instances by template
                template_stats = await conn.fetch("""
                    SELECT tt.name, COUNT(ti.id) as count
                    FROM tool_templates tt
                    LEFT JOIN tool_instances ti ON tt.id = ti.template_id
                    GROUP BY tt.id, tt.name
                    ORDER BY count DESC
                """)
                # Recent instances
                recent_instances = await conn.fetch("""
                    SELECT id, name, status, created_at
                    FROM tool_instances
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
            return {
                "total_instances": total_instances,
                "status_distribution": [
                    {"status": row["status"], "count": row["count"]} 
                    for row in status_stats
                ],
                "template_usage": [
                    {"template": row["name"], "count": row["count"]} 
                    for row in template_stats
                ],
                "recent_instances": [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "status": row["status"],
                        "created_at": row["created_at"]
                    }
                    for row in recent_instances
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting instance statistics: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    def _format_template_result(self, row) -> Dict[str, Any]:
        """Format a database row into a template dictionary"""
        
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "tool_type": row["tool_type"],
            "category": row["category"],
            "version": row["version"],
            "configuration_schema": json.loads(row["configuration_schema"]) if row["configuration_schema"] else {},
            "input_schema": json.loads(row["input_schema"]) if row["input_schema"] else {},
            "output_schema": json.loads(row["output_schema"]) if row["output_schema"] else {},
            "template_config": json.loads(row["template_config"]) if row["template_config"] else {},
            "default_config": json.loads(row["default_config"]) if row["default_config"] else {},
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    def _format_instance_result(self, row) -> Dict[str, Any]:
        """Format a database row into an instance dictionary"""
        
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "template_id": row["template_id"],
            "template_name": row.get("template_name"),
            "tool_type": row.get("tool_type"),
            "configuration": json.loads(row["configuration"]) if row["configuration"] else {},
            "input_data": json.loads(row["input_data"]) if row["input_data"] else {},
            "output_data": json.loads(row["output_data"]) if row["output_data"] else {},
            "status": row["status"],
            "created_by": row["created_by"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_execution": row.get("last_execution")
        }
