"""
Intelligent SQL Agent Tool Implementation
Natural language to SQL with safety controls and query optimization
"""

import asyncio
import re
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
import json

# Database connectivity
import asyncpg
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# AI/NLP for query generation
import openai

logger = logging.getLogger(__name__)

class IntelligentSQLAgent:
    """
    Intelligent SQL Agent with natural language processing,
    safety controls, and query optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SQL Agent with configuration"""
        self.config = config
        self.database_url = config.get("database_url")
        self.database_type = config.get("database_type", "postgresql")
        self.safety_mode = config.get("safety_mode", "strict")
        self.max_rows = config.get("max_rows", 1000)
        self.query_timeout = config.get("query_timeout", 30)
        self.allowed_operations = config.get("allowed_operations", ["SELECT"])
        
        # AI model configuration
        self.llm_model = config.get("llm_model", "gpt-4")
        self.openai_client = None
        
        # Database connection
        self.connection_pool = None
        self.engine = None
        
        logger.info(f"Initialized SQL Agent for {self.database_type}")
    
    async def initialize(self):
        """Initialize database connections and AI models"""
        try:
            # Initialize OpenAI client
            self.openai_client = openai.AsyncOpenAI(
                api_key=self.config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            )
            
            # Initialize database connection
            if self.database_type == "postgresql":
                self.connection_pool = await asyncpg.create_pool(self.database_url)
            else:
                self.engine = create_engine(self.database_url)
            
            logger.info("SQL Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQL Agent: {e}")
            raise
    
    async def natural_language_query(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert natural language question to SQL and execute
        
        Args:
            question: Natural language question
            context: Additional context for query generation
            
        Returns:
            Dictionary with query results
        """
        try:
            # Get database schema
            schema_info = await self._get_schema_info()
            
            # Generate SQL query from natural language
            sql_query = await self._generate_sql_query(question, schema_info, context or {})
            
            # Validate and sanitize query
            validation_result = await self._validate_query(sql_query)
            if not validation_result["is_safe"]:
                return {
                    "status": "error",
                    "error": f"Query validation failed: {validation_result['reason']}",
                    "suggested_query": validation_result.get("suggested_query")
                }
            
            # Execute query
            result = await self._execute_query(sql_query)
            
            # Format results
            formatted_result = await self._format_results(result, question)
            
            return {
                "status": "success",
                "question": question,
                "sql_query": sql_query,
                "results": formatted_result,
                "metadata": {
                    "execution_time": result.get("execution_time"),
                    "row_count": len(result.get("data", [])),
                    "columns": result.get("columns", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {
                "status": "error",
                "error": str(e),
                "question": question
            }
    
    async def execute_sql(self, sql_query: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a SQL query directly with safety checks
        
        Args:
            sql_query: SQL query to execute
            parameters: Query parameters
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Validate query
            validation_result = await self._validate_query(sql_query)
            if not validation_result["is_safe"]:
                return {
                    "status": "error",
                    "error": f"Query validation failed: {validation_result['reason']}"
                }
            
            # Execute query
            result = await self._execute_query(sql_query, parameters or {})
            
            return {
                "status": "success",
                "sql_query": sql_query,
                "results": result,
                "metadata": {
                    "execution_time": result.get("execution_time"),
                    "row_count": len(result.get("data", []))
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return {
                "status": "error",
                "error": str(e),
                "sql_query": sql_query
            }
    
    async def explain_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Explain a SQL query execution plan
        
        Args:
            sql_query: SQL query to explain
            
        Returns:
            Dictionary with explanation results
        """
        try:
            # Add EXPLAIN to the query
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql_query}"
            
            # Execute explain
            result = await self._execute_query(explain_query)
            
            # Parse and format explanation
            explanation = await self._format_explanation(result["data"][0][0])
            
            return {
                "status": "success",
                "sql_query": sql_query,
                "execution_plan": explanation,
                "performance_insights": await self._analyze_performance(explanation)
            }
            
        except Exception as e:
            logger.error(f"Error explaining query: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def optimize_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Suggest optimizations for a SQL query
        
        Args:
            sql_query: SQL query to optimize
            
        Returns:
            Dictionary with optimization suggestions
        """
        try:
            # Analyze current query
            current_plan = await self.explain_query(sql_query)
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(sql_query, current_plan)
            
            return {
                "status": "success",
                "original_query": sql_query,
                "optimization_suggestions": suggestions,
                "current_performance": current_plan.get("performance_insights")
            }
            
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            schema_info = await self._get_schema_info()
            return {
                "status": "success",
                "schema": schema_info
            }
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Private methods
    
    async def _get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive database schema information"""
        try:
            if self.database_type == "postgresql":
                return await self._get_postgresql_schema()
            else:
                return await self._get_generic_schema()
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            return {}
    
    async def _get_postgresql_schema(self) -> Dict[str, Any]:
        """Get PostgreSQL-specific schema information"""
        schema_query = """
        SELECT 
            t.table_name,
            t.table_type,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            tc.constraint_type,
            kcu.constraint_name
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c 
            ON t.table_name = c.table_name
        LEFT JOIN information_schema.table_constraints tc 
            ON t.table_name = tc.table_name
        LEFT JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name 
            AND c.column_name = kcu.column_name
        WHERE t.table_schema = 'public'
        ORDER BY t.table_name, c.ordinal_position;
        """
        
        result = await self._execute_query(schema_query)
        
        # Organize schema data
        tables = {}
        for row in result["data"]:
            table_name = row[0]
            if table_name not in tables:
                tables[table_name] = {
                    "table_type": row[1],
                    "columns": [],
                    "constraints": []
                }
            
            if row[2]:  # column_name
                column_info = {
                    "name": row[2],
                    "type": row[3],
                    "nullable": row[4] == "YES",
                    "default": row[5]
                }
                if column_info not in tables[table_name]["columns"]:
                    tables[table_name]["columns"].append(column_info)
            
            if row[6]:  # constraint_type
                constraint_info = {
                    "type": row[6],
                    "name": row[7]
                }
                if constraint_info not in tables[table_name]["constraints"]:
                    tables[table_name]["constraints"].append(constraint_info)
        
        return {
            "database_type": self.database_type,
            "tables": tables,
            "table_count": len(tables)
        }
    
    async def _generate_sql_query(self, question: str, schema_info: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate SQL query from natural language using AI"""
        try:
            # Prepare schema context for the AI model
            schema_context = self._format_schema_for_ai(schema_info)
            
            # Create prompt for SQL generation
            prompt = f"""
            You are an expert SQL query generator. Given the following database schema and a natural language question, generate a safe and efficient SQL query.
            
            Database Schema:
            {schema_context}
            
            Question: {question}
            
            Additional Context: {json.dumps(context)}
            
            Rules:
            1. Only generate SELECT queries unless explicitly asked for modifications
            2. Use proper table and column names from the schema
            3. Include appropriate WHERE clauses for filtering
            4. Use JOINs when necessary to relate tables
            5. Limit results to prevent excessive data retrieval
            6. Use proper SQL syntax for {self.database_type}
            
            Generate only the SQL query, no explanations:
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a SQL query generator. Return only valid SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the query
            sql_query = re.sub(r'^```sql\s*', '', sql_query)
            sql_query = re.sub(r'\s*```$', '', sql_query)
            sql_query = sql_query.strip()
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise
    
    def _format_schema_for_ai(self, schema_info: Dict[str, Any]) -> str:
        """Format schema information for AI prompt"""
        formatted_schema = []
        
        for table_name, table_info in schema_info.get("tables", {}).items():
            columns = []
            for col in table_info.get("columns", []):
                col_def = f"{col['name']} {col['type']}"
                if not col['nullable']:
                    col_def += " NOT NULL"
                columns.append(col_def)
            
            table_def = f"Table: {table_name}\nColumns: {', '.join(columns)}\n"
            formatted_schema.append(table_def)
        
        return "\n".join(formatted_schema)
    
    async def _validate_query(self, sql_query: str) -> Dict[str, Any]:
        """Validate SQL query for safety and compliance"""
        try:
            # Remove comments and normalize
            clean_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
            clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
            clean_query = clean_query.strip().upper()
            
            # Check for dangerous operations
            dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER', 'CREATE']
            
            if self.safety_mode == "strict":
                for keyword in dangerous_keywords:
                    if keyword in clean_query and keyword not in self.allowed_operations:
                        return {
                            "is_safe": False,
                            "reason": f"Operation '{keyword}' not allowed in strict safety mode"
                        }
            
            # Check for SQL injection patterns
            injection_patterns = [
                r"';.*--",
                r"UNION.*SELECT",
                r"1=1",
                r"OR.*1=1",
                r"EXEC\s*\(",
                r"EXECUTE\s*\("
            ]
            
            for pattern in injection_patterns:
                if re.search(pattern, clean_query, re.IGNORECASE):
                    return {
                        "is_safe": False,
                        "reason": f"Potential SQL injection detected: {pattern}"
                    }
            
            # Check for row limit
            if "LIMIT" not in clean_query and "TOP" not in clean_query:
                if clean_query.startswith("SELECT"):
                    # Suggest adding LIMIT
                    return {
                        "is_safe": True,
                        "suggested_query": f"{sql_query} LIMIT {self.max_rows}",
                        "warning": f"Consider adding LIMIT to prevent large result sets"
                    }
            
            return {"is_safe": True}
            
        except Exception as e:
            logger.error(f"Error validating query: {e}")
            return {
                "is_safe": False,
                "reason": f"Validation error: {str(e)}"
            }
    
    async def _execute_query(self, sql_query: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute SQL query with timeout and error handling"""
        start_time = datetime.now()
        
        try:
            if self.database_type == "postgresql" and self.connection_pool:
                async with self.connection_pool.acquire() as conn:
                    # Set query timeout
                    await conn.execute(f"SET statement_timeout = '{self.query_timeout}s'")
                    
                    # Execute query
                    result = await conn.fetch(sql_query, *(parameters.values() if parameters else []))
                    
                    # Format result
                    data = [list(row) for row in result]
                    columns = list(result[0].keys()) if result else []
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "data": data,
                        "columns": columns,
                        "row_count": len(data),
                        "execution_time": execution_time
                    }
            else:
                # Use SQLAlchemy for other databases
                with self.engine.connect() as conn:
                    result = conn.execute(text(sql_query), parameters or {})
                    
                    data = [list(row) for row in result.fetchall()]
                    columns = list(result.keys())
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        "data": data,
                        "columns": columns,
                        "row_count": len(data),
                        "execution_time": execution_time
                    }
                    
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query execution failed: {e}")
            raise Exception(f"Query execution failed after {execution_time:.2f}s: {str(e)}")
    
    async def _format_results(self, result: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Format query results with AI-powered insights"""
        try:
            # Basic formatting
            formatted_result = {
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "summary": ""
            }
            
            # Generate summary using AI
            if result["data"] and len(result["data"]) > 0:
                summary_prompt = f"""
                Analyze the following SQL query results for the question: "{question}"
                
                Columns: {result['columns']}
                Sample data (first 3 rows): {result['data'][:3]}
                Total rows: {result['row_count']}
                
                Provide a brief, human-readable summary of what the data shows:
                """
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": summary_prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                formatted_result["summary"] = response.choices[0].message.content.strip()
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return result
    
    async def _format_explanation(self, explain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format query execution plan explanation"""
        # Parse and format PostgreSQL EXPLAIN output
        plan = explain_data.get("Plan", {})
        
        return {
            "total_cost": plan.get("Total Cost"),
            "execution_time": explain_data.get("Execution Time"),
            "planning_time": explain_data.get("Planning Time"),
            "node_type": plan.get("Node Type"),
            "startup_cost": plan.get("Startup Cost"),
            "rows": plan.get("Actual Rows"),
            "loops": plan.get("Actual Loops")
        }
    
    async def _analyze_performance(self, explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query performance and provide insights"""
        insights = []
        
        if explanation.get("execution_time", 0) > 1000:  # > 1 second
            insights.append("Query execution time is high. Consider optimization.")
        
        if explanation.get("total_cost", 0) > 10000:
            insights.append("Query cost is high. Check for missing indexes.")
        
        return {
            "performance_score": "good" if len(insights) == 0 else "needs_improvement",
            "insights": insights,
            "recommendations": []
        }
    
    async def _generate_optimization_suggestions(self, sql_query: str, current_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate SQL optimization suggestions using AI"""
        try:
            optimization_prompt = f"""
            Analyze this SQL query and its execution plan to suggest optimizations:
            
            SQL Query: {sql_query}
            Current Performance: {current_plan.get('performance_insights', {})}
            
            Suggest specific optimizations such as:
            1. Index recommendations
            2. Query rewriting
            3. JOIN optimization
            4. WHERE clause improvements
            
            Format as a list of actionable suggestions:
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "user", "content": optimization_prompt}
                ],
                max_tokens=400,
                temperature=0.2
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            
            # Parse suggestions (simplified)
            suggestions = []
            for line in suggestions_text.split('\n'):
                if line.strip() and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    suggestions.append({
                        "type": "optimization",
                        "description": line.strip().lstrip('-•* '),
                        "impact": "medium"  # Could be enhanced with more analysis
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return []

# Tool configuration schema
TOOL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "database_url": {
            "type": "string",
            "description": "Database connection URL"
        },
        "database_type": {
            "type": "string",
            "enum": ["postgresql", "mysql", "sqlite", "mssql"],
            "default": "postgresql",
            "description": "Type of database"
        },
        "safety_mode": {
            "type": "string",
            "enum": ["strict", "moderate", "permissive"],
            "default": "strict",
            "description": "Safety mode for query validation"
        },
        "max_rows": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10000,
            "default": 1000,
            "description": "Maximum number of rows to return"
        },
        "query_timeout": {
            "type": "integer",
            "minimum": 1,
            "maximum": 300,
            "default": 30,
            "description": "Query timeout in seconds"
        },
        "llm_model": {
            "type": "string",
            "enum": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "default": "gpt-4",
            "description": "LLM model for query generation"
        },
        "allowed_operations": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["SELECT", "INSERT", "UPDATE", "DELETE"]
            },
            "default": ["SELECT"],
            "description": "Allowed SQL operations"
        }
    },
    "required": ["database_url"]
}

# Tool input/output schemas
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["natural_query", "execute_sql", "explain_query", "optimize_query", "get_schema"],
            "description": "Operation to perform"
        },
        "question": {
            "type": "string",
            "description": "Natural language question (for natural_query)"
        },
        "sql_query": {
            "type": "string",
            "description": "SQL query to execute (for execute_sql, explain_query, optimize_query)"
        },
        "parameters": {
            "type": "object",
            "description": "Query parameters"
        },
        "context": {
            "type": "object",
            "description": "Additional context for query generation"
        }
    },
    "required": ["operation"]
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["success", "error"]
        },
        "results": {
            "type": "object",
            "description": "Query results or operation output"
        },
        "sql_query": {
            "type": "string",
            "description": "Generated or executed SQL query"
        },
        "metadata": {
            "type": "object",
            "description": "Execution metadata"
        },
        "error": {
            "type": "string",
            "description": "Error message if status is error"
        }
    },
    "required": ["status"]
}
