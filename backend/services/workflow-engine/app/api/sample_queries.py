"""
API endpoints for sample queries related to workflows
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..examples.sample_queries import ALL_SAMPLE_QUERIES, QueryCategory

router = APIRouter(prefix="/sample-queries", tags=["sample-queries"])


@router.get("/workflows")
async def get_workflow_sample_queries():
    """Get all sample queries for workflows"""
    
    result = {}
    for workflow_category, queries in ALL_SAMPLE_QUERIES["workflows"].items():
        result[workflow_category] = [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags,
                "complexity_level": q.complexity_level
            }
            for q in queries
        ]
    
    return result


@router.get("/workflows/{workflow_category}")
async def get_workflow_category_queries(workflow_category: str):
    """Get sample queries for a specific workflow category"""
    
    if workflow_category not in ALL_SAMPLE_QUERIES["workflows"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow category '{workflow_category}' not found. Available categories: {list(ALL_SAMPLE_QUERIES['workflows'].keys())}"
        )
    
    queries = ALL_SAMPLE_QUERIES["workflows"][workflow_category]
    
    return {
        "workflow_category": workflow_category,
        "sample_queries": [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags,
                "complexity_level": q.complexity_level
            }
            for q in queries
        ]
    }


@router.get("/workflows/by-tags")
async def get_workflow_queries_by_tags(
    tags: List[str] = Query(..., description="Filter by tags")
):
    """Get workflow sample queries filtered by tags"""
    
    matching_queries = []
    
    for workflow_category, queries in ALL_SAMPLE_QUERIES["workflows"].items():
        for q in queries:
            if any(tag in q.tags for tag in tags):
                matching_queries.append({
                    "query": q.query,
                    "description": q.description,
                    "category": q.category.value,
                    "expected_response_type": q.expected_response_type,
                    "tags": q.tags,
                    "complexity_level": q.complexity_level,
                    "workflow_category": workflow_category
                })
    
    return {
        "filter_tags": tags,
        "matching_queries": matching_queries
    }


@router.get("/workflows/by-complexity")
async def get_workflow_queries_by_complexity(
    complexity: str = Query(..., description="Filter by complexity level: beginner, intermediate, advanced")
):
    """Get workflow sample queries filtered by complexity level"""
    
    valid_levels = ["beginner", "intermediate", "advanced"]
    if complexity not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid complexity level. Must be one of: {valid_levels}"
        )
    
    matching_queries = []
    
    for workflow_category, queries in ALL_SAMPLE_QUERIES["workflows"].items():
        for q in queries:
            if q.complexity_level == complexity:
                matching_queries.append({
                    "query": q.query,
                    "description": q.description,
                    "category": q.category.value,
                    "expected_response_type": q.expected_response_type,
                    "tags": q.tags,
                    "complexity_level": q.complexity_level,
                    "workflow_category": workflow_category
                })
    
    return {
        "complexity_level": complexity,
        "matching_queries": matching_queries
    }


@router.get("/quick-start")
async def get_quick_start_queries():
    """Get quick start queries for workflow beginners"""
    
    queries = ALL_SAMPLE_QUERIES["quick_start"]
    
    return {
        "quick_start_queries": [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags,
                "complexity_level": q.complexity_level
            }
            for q in queries
        ]
    }


@router.get("/contextual/{role}")
async def get_contextual_queries(role: str):
    """Get contextual queries based on user role"""
    
    if role not in ALL_SAMPLE_QUERIES["contextual"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role}' not found. Available roles: {list(ALL_SAMPLE_QUERIES['contextual'].keys())}"
        )
    
    queries = ALL_SAMPLE_QUERIES["contextual"][role]
    
    return {
        "role": role,
        "contextual_queries": [
            {
                "query": q.query,
                "description": q.description,
                "category": q.category.value,
                "expected_response_type": q.expected_response_type,
                "tags": q.tags,
                "complexity_level": q.complexity_level
            }
            for q in queries
        ]
    }
