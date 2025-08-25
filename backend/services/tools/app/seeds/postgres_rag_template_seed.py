"""
Database seeder for PostgreSQL Enhanced RAG Template
Populates the database with the PostgreSQL RAG template and its fields
"""

import asyncio
import asyncpg
import json
import logging
from datetime import datetime
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from templates.postgres_rag_template import (
    get_postgres_rag_template, 
    get_postgres_rag_template_fields
)

logger = logging.getLogger(__name__)

class PostgresRAGTemplateSeed:
    """Seeder for PostgreSQL RAG template"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection_pool = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.connection_pool = await asyncpg.create_pool(self.database_url)
        logger.info("Database connection initialized for template seeding")
    
    async def seed_template(self) -> bool:
        """Seed the PostgreSQL RAG template and fields"""
        try:
            template = get_postgres_rag_template()
            template_fields = get_postgres_rag_template_fields()
            
            async with self.connection_pool.acquire() as conn:
                # Start transaction
                async with conn.transaction():
                    # Insert or update template
                    existing_template = await conn.fetchrow(
                        "SELECT id FROM tool_templates WHERE name = $1",
                        template["name"]
                    )
                    
                    if existing_template:
                        logger.info(f"Updating existing template: {template['name']}")
                        # Update existing template
                        await conn.execute("""
                            UPDATE tool_templates SET
                                display_name = $2,
                                type = $3,
                                category = $4,
                                description = $5,
                                long_description = $6,
                                version = $7,
                                tags = $8,
                                is_active = $9,
                                documentation = $10,
                                schema_definition = $11,
                                default_config = $12,
                                input_schema = $13,
                                output_schema = $14,
                                updated_at = $15
                            WHERE name = $1
                        """, 
                        template["name"],
                        template["display_name"],
                        template["type"],
                        template["category"],
                        template["description"],
                        template.get("long_description", ""),
                        template["version"],
                        template["tags"],
                        template["is_active"],
                        template.get("documentation", ""),
                        json.dumps(template["schema_definition"]),
                        json.dumps(template["default_config"]),
                        json.dumps(template["input_schema"]), 
                        json.dumps(template["output_schema"]),
                        datetime.utcnow()
                        )
                        template_id = existing_template["id"]
                    else:
                        logger.info(f"Creating new template: {template['name']}")
                        # Insert new template
                        template_id = await conn.fetchval("""
                            INSERT INTO tool_templates 
                            (name, display_name, type, category, description, long_description,
                             version, tags, is_active, documentation, schema_definition, 
                             default_config, input_schema, output_schema, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                            RETURNING id
                        """,
                        template["name"],
                        template["display_name"], 
                        template["type"],
                        template["category"],
                        template["description"],
                        template.get("long_description", ""),
                        template["version"],
                        template["tags"],
                        template["is_active"],
                        template.get("documentation", ""),
                        json.dumps(template["schema_definition"]),
                        json.dumps(template["default_config"]),
                        json.dumps(template["input_schema"]),
                        json.dumps(template["output_schema"]),
                        datetime.utcnow(),
                        datetime.utcnow()
                        )
                    
                    # Clear existing template fields
                    await conn.execute(
                        "DELETE FROM tool_template_fields WHERE tool_template_id = $1",
                        template_id
                    )
                    
                    # Insert template fields
                    for field in template_fields:
                        await conn.execute("""
                            INSERT INTO tool_template_fields
                            (tool_template_id, field_name, field_label, field_description,
                             field_type, is_required, validation_rules, default_value,
                             field_options, conditional_logic, display_order, created_at)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        """,
                        template_id,
                        field["field_name"],
                        field["field_label"], 
                        field["field_description"],
                        field["field_type"],
                        field["is_required"],
                        json.dumps(field.get("validation_rules", {})),
                        field.get("default_value"),
                        json.dumps(field.get("field_options", [])),
                        json.dumps(field.get("conditional_logic", {})),
                        field.get("display_order", 0),
                        datetime.utcnow()
                        )
                    
                    logger.info(f"Successfully seeded template '{template['name']}' with {len(template_fields)} fields")
                    return True
                    
        except Exception as e:
            logger.error(f"Error seeding PostgreSQL RAG template: {e}")
            return False
    
    async def verify_template(self) -> bool:
        """Verify that the template was seeded correctly"""
        try:
            async with self.connection_pool.acquire() as conn:
                # Check template exists
                template_row = await conn.fetchrow("""
                    SELECT id, name, display_name, version, type, category
                    FROM tool_templates 
                    WHERE name = 'postgres_enhanced_rag'
                """)
                
                if not template_row:
                    logger.error("PostgreSQL RAG template not found in database")
                    return False
                
                # Check template fields exist
                fields_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM tool_template_fields
                    WHERE tool_template_id = $1
                """, template_row["id"])
                
                expected_fields = len(get_postgres_rag_template_fields())
                if fields_count != expected_fields:
                    logger.error(f"Expected {expected_fields} template fields, found {fields_count}")
                    return False
                
                logger.info(f"Template verification successful:")
                logger.info(f"  - Template: {template_row['display_name']} (v{template_row['version']})")
                logger.info(f"  - Type: {template_row['type']}")
                logger.info(f"  - Category: {template_row['category']}")
                logger.info(f"  - Fields: {fields_count}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error verifying template: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.connection_pool:
            await self.connection_pool.close()

async def main():
    """Main seeder function"""
    # Get database URL from environment or use default
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/agenticai"
    )
    
    # Initialize seeder
    seeder = PostgresRAGTemplateSeed(database_url)
    
    try:
        # Initialize connection
        await seeder.initialize()
        
        # Seed template
        success = await seeder.seed_template()
        
        if success:
            # Verify seeding
            verified = await seeder.verify_template()
            if verified:
                logger.info("✅ PostgreSQL RAG template seeded and verified successfully!")
            else:
                logger.error("❌ Template seeded but verification failed")
                return 1
        else:
            logger.error("❌ Failed to seed PostgreSQL RAG template")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Seeder error: {e}")
        return 1
        
    finally:
        await seeder.close()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run seeder
    exit_code = asyncio.run(main())
    exit(exit_code)