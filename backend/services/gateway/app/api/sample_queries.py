"""
Simple API for demo sample queries
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from ..core.database import get_database
from ..models.demo_queries import DemoSampleQuery

router = APIRouter(prefix="/sample-queries", tags=["sample-queries"])


@router.get("/")
async def get_all_demo_queries(db: AsyncSession = Depends(get_database)):
    """Get all demo sample queries grouped by service type"""
    
    result_query = await db.execute(
        select(DemoSampleQuery).order_by(
            DemoSampleQuery.service_type, 
            DemoSampleQuery.sort_order,
            DemoSampleQuery.category
        )
    )
    queries = result_query.scalars().all()
    
    # Group by service type
    result = {
        "agents": [],
        "tools": [],
        "workflows": []
    }
    
    for query in queries:
        query_data = {
            "id": str(query.id),
            "category": query.category,
            "query": query.query_text,
            "description": query.description,
            "complexity_level": query.complexity_level,
            "tags": query.tags or [],
            "is_featured": query.is_featured
        }
        
        if query.service_type in result:
            result[query.service_type].append(query_data)
    
    return result


@router.get("/featured")
async def get_featured_queries(db: AsyncSession = Depends(get_database)):
    """Get featured demo queries for quick start"""
    
    result_query = await db.execute(
        select(DemoSampleQuery).filter(
            DemoSampleQuery.is_featured == True
        ).order_by(
            DemoSampleQuery.service_type,
            DemoSampleQuery.sort_order
        )
    )
    queries = result_query.scalars().all()
    
    result = []
    for query in queries:
        result.append({
            "id": str(query.id),
            "service_type": query.service_type,
            "category": query.category,
            "query": query.query_text,
            "description": query.description,
            "complexity_level": query.complexity_level,
            "tags": query.tags or []
        })
    
    return {"featured_queries": result}


@router.get("/{service_type}")
async def get_queries_by_service(
    service_type: str,
    category: Optional[str] = None,
    complexity: Optional[str] = None,
    db: AsyncSession = Depends(get_database)
):
    """Get demo queries for a specific service type with optional filters"""
    
    if service_type not in ["agents", "tools", "workflows"]:
        raise HTTPException(status_code=400, detail="Invalid service type")
    
    query = select(DemoSampleQuery).filter(
        DemoSampleQuery.service_type == service_type
    )
    
    if category:
        query = query.filter(DemoSampleQuery.category == category)
    
    if complexity:
        query = query.filter(DemoSampleQuery.complexity_level == complexity)
    
    query = query.order_by(DemoSampleQuery.sort_order)
    
    result_query = await db.execute(query)
    queries = result_query.scalars().all()
    
    result = []
    for q in queries:
        result.append({
            "id": str(q.id),
            "category": q.category,
            "query": q.query_text,
            "description": q.description,
            "complexity_level": q.complexity_level,
            "tags": q.tags or [],
            "is_featured": q.is_featured
        })
    
    return {
        "service_type": service_type,
        "queries": result
    }


@router.get("/search")
async def search_queries(
    q: str = Query(..., description="Search term"),
    service_type: Optional[str] = None,
    db: AsyncSession = Depends(get_database)
):
    """Search demo queries by text"""
    
    query = select(DemoSampleQuery)
    
    if service_type:
        query = query.filter(DemoSampleQuery.service_type == service_type)
    
    # Simple text search
    search_term = f"%{q.lower()}%"
    query = query.filter(
        (DemoSampleQuery.query_text.ilike(search_term)) |
        (DemoSampleQuery.description.ilike(search_term))
    )
    
    query = query.order_by(DemoSampleQuery.sort_order)
    
    result_query = await db.execute(query)
    queries = result_query.scalars().all()
    
    result = []
    for query_obj in queries:
        result.append({
            "id": str(query_obj.id),
            "service_type": query_obj.service_type,
            "category": query_obj.category,
            "query": query_obj.query_text,
            "description": query_obj.description,
            "complexity_level": query_obj.complexity_level,
            "tags": query_obj.tags or [],
            "is_featured": query_obj.is_featured
        })
    
    return {
        "search_term": q,
        "results": result
    }
