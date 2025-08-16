"""
SQL Tool Service - Database query execution and schema introspection
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
from datetime import datetime
import json
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect
import asyncpg
import aiomysql
import aiosqlite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SQL Tool Service",
    description="Database query execution and schema introspection service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection registry
db_engines: Dict[str, Any] = {}
db_sessions: Dict[str, Any] = {}

# Pydantic models
class DatabaseConnection(BaseModel):
    name: str = Field(..., description="Unique connection name")
    database_type: str = Field(..., description="Database type: postgresql, mysql, sqlite")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    connection_string: Optional[str] = Field(None, description="Full connection string")

class SQLQuery(BaseModel):
    connection_name: str = Field(..., description="Database connection to use")
    query: str = Field(..., description="SQL query to execute")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    limit: Optional[int] = Field(1000, description="Maximum rows to return")

class QueryResult(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    row_count: int = 0
    execution_time_ms: float = 0
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SchemaResult(BaseModel):
    success: bool
    tables: Optional[List[Dict[str, Any]]] = None
    views: Optional[List[Dict[str, Any]]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


def create_connection_string(conn: DatabaseConnection) -> str:
    """Create connection string from connection details"""
    
    if conn.connection_string:
        return conn.connection_string
    
    if conn.database_type == "postgresql":
        return f"postgresql+asyncpg://{conn.username}:{conn.password}@{conn.host}:{conn.port or 5432}/{conn.database}"
    elif conn.database_type == "mysql":
        return f"mysql+aiomysql://{conn.username}:{conn.password}@{conn.host}:{conn.port or 3306}/{conn.database}"
    elif conn.database_type == "sqlite":
        return f"sqlite+aiosqlite:///{conn.database}"
    else:
        raise ValueError(f"Unsupported database type: {conn.database_type}")


async def get_database_engine(connection_name: str):
    """Get or create database engine"""
    
    if connection_name not in db_engines:
        raise HTTPException(status_code=404, detail=f"Connection '{connection_name}' not found")
    
    return db_engines[connection_name]


async def get_database_session(connection_name: str) -> AsyncSession:
    """Get database session"""
    
    engine = await get_database_engine(connection_name)
    session_maker = db_sessions[connection_name]
    
    async with session_maker() as session:
        return session


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sql-tool",
        "version": "1.0.0",
        "features": {
            "database_types": ["postgresql", "mysql", "sqlite"],
            "query_execution": True,
            "schema_introspection": True,
            "connection_management": True
        },
        "active_connections": list(db_engines.keys())
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SQL Tool Service",
        "version": "1.0.0",
        "description": "Database query execution and schema introspection service",
        "endpoints": {
            "connections": "/connections",
            "query": "/query",
            "schema": "/schema",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.post("/connections", status_code=201)
async def create_connection(connection: DatabaseConnection):
    """Create a new database connection"""
    
    try:
        # Create connection string
        conn_string = create_connection_string(connection)
        
        # Create async engine
        engine = create_async_engine(
            conn_string,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        # Store engine and session maker
        db_engines[connection.name] = engine
        db_sessions[connection.name] = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        logger.info(f"Created database connection: {connection.name}")
        
        return {
            "message": f"Connection '{connection.name}' created successfully",
            "connection_name": connection.name,
            "database_type": connection.database_type,
            "status": "connected"
        }
        
    except Exception as e:
        logger.error(f"Failed to create connection {connection.name}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create connection: {str(e)}"
        )


@app.get("/connections")
async def list_connections():
    """List all database connections"""
    
    connections = []
    
    for name, engine in db_engines.items():
        try:
            # Test connection health
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            status = "healthy"
        except Exception:
            status = "unhealthy"
        
        connections.append({
            "name": name,
            "status": status,
            "url": str(engine.url).replace(engine.url.password or "", "***") if engine.url.password else str(engine.url)
        })
    
    return {
        "connections": connections,
        "total": len(connections)
    }


@app.delete("/connections/{connection_name}")
async def delete_connection(connection_name: str):
    """Delete a database connection"""
    
    if connection_name not in db_engines:
        raise HTTPException(status_code=404, detail=f"Connection '{connection_name}' not found")
    
    try:
        # Close engine
        await db_engines[connection_name].dispose()
        
        # Remove from registries
        del db_engines[connection_name]
        del db_sessions[connection_name]
        
        logger.info(f"Deleted database connection: {connection_name}")
        
        return {"message": f"Connection '{connection_name}' deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete connection {connection_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete connection: {str(e)}"
        )


@app.post("/query", response_model=QueryResult)
async def execute_query(query_request: SQLQuery):
    """Execute SQL query"""
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        engine = await get_database_engine(query_request.connection_name)
        
        async with engine.begin() as conn:
            # Execute query with parameters
            if query_request.params:
                result = await conn.execute(text(query_request.query), query_request.params)
            else:
                result = await conn.execute(text(query_request.query))
            
            # Fetch results for SELECT queries
            if query_request.query.strip().upper().startswith('SELECT'):
                rows = result.fetchmany(query_request.limit or 1000)
                columns = list(result.keys()) if rows else []
                data = [dict(row._mapping) for row in rows]
                row_count = len(data)
            else:
                # For INSERT, UPDATE, DELETE
                data = None
                columns = None
                row_count = result.rowcount
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return QueryResult(
                success=True,
                data=data,
                columns=columns,
                row_count=row_count,
                execution_time_ms=execution_time
            )
            
    except Exception as e:
        execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
        logger.error(f"Query execution failed: {e}")
        
        return QueryResult(
            success=False,
            error=str(e),
            execution_time_ms=execution_time
        )


@app.get("/schema/{connection_name}", response_model=SchemaResult)
async def get_schema(connection_name: str):
    """Get database schema information"""
    
    try:
        engine = await get_database_engine(connection_name)
        
        async with engine.begin() as conn:
            # Use SQLAlchemy inspector for schema introspection
            inspector = inspect(engine)
            
            # Get tables
            tables = []
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "default": column.get("default"),
                        "primary_key": column.get("primary_key", False)
                    })
                
                # Get primary keys
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint.get("constrained_columns", [])
                
                # Get foreign keys
                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name):
                    foreign_keys.append({
                        "columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    })
                
                tables.append({
                    "name": table_name,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys
                })
            
            # Get views
            views = []
            try:
                for view_name in inspector.get_view_names():
                    views.append({
                        "name": view_name,
                        "definition": inspector.get_view_definition(view_name)
                    })
            except (AttributeError, NotImplementedError):
                # Some databases don't support view introspection
                pass
            
            return SchemaResult(
                success=True,
                tables=tables,
                views=views,
                functions=[]  # Function introspection can be added later
            )
            
    except Exception as e:
        logger.error(f"Schema introspection failed: {e}")
        
        return SchemaResult(
            success=False,
            error=str(e)
        )


@app.get("/tables/{connection_name}")
async def list_tables(connection_name: str):
    """List all tables in database"""
    
    try:
        engine = await get_database_engine(connection_name)
        inspector = inspect(engine)
        
        tables = inspector.get_table_names()
        
        return {
            "connection": connection_name,
            "tables": tables,
            "count": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tables: {str(e)}"
        )


@app.get("/tables/{connection_name}/{table_name}")
async def describe_table(connection_name: str, table_name: str):
    """Get detailed table information"""
    
    try:
        engine = await get_database_engine(connection_name)
        inspector = inspect(engine)
        
        # Check if table exists
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get table details
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        return {
            "table_name": table_name,
            "columns": columns,
            "primary_key": pk_constraint,
            "foreign_keys": foreign_keys,
            "indexes": indexes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to describe table: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to describe table: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
