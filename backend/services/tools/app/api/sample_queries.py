"""
API endpoints for sample queries related to tools
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..examples.sample_queries import ALL_SAMPLE_QUERIES, QueryCategory

router = APIRouter(prefix="/sample-queries", tags=["sample-queries"])


@router.get("/tools")
async def get_tool_sample_queries():
    """Get all sample queries for tools"""
    
    result = {}
    for tool_category, queries in ALL_SAMPLE_QUERIES["tools"].items():
        result[tool_category] = [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags
            }
            for q in queries
        ]
    
    return result


@router.get("/tools/{tool_category}")
async def get_tool_category_queries(tool_category: str):
    """Get sample queries for a specific tool category"""
    
    if tool_category not in ALL_SAMPLE_QUERIES["tools"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool category '{tool_category}' not found. Available categories: {list(ALL_SAMPLE_QUERIES['tools'].keys())}"
        )
    
    queries = ALL_SAMPLE_QUERIES["tools"][tool_category]
    
    return {
        "tool_category": tool_category,
        "sample_queries": [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags
            }
            for q in queries
        ]
    }


@router.get("/tools/by-tags")
async def get_tool_queries_by_tags(
    tags: List[str] = Query(..., description="Filter by tags")
):
    """Get tool sample queries filtered by tags"""
    
    matching_queries = []
    
    for tool_category, queries in ALL_SAMPLE_QUERIES["tools"].items():
        for q in queries:
            if any(tag in q.tags for tag in tags):
                matching_queries.append({
                    "query": q.query,
                    "description": q.description,
                    "category": q.category.value,
                    "expected_response_type": q.expected_response_type,
                    "tags": q.tags,
                    "tool_category": tool_category
                })
    
    return {
        "filter_tags": tags,
        "matching_queries": matching_queries
    }
