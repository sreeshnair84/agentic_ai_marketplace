"""
Sample queries for tools service interactions
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class QueryCategory(Enum):
    """Categories for sample queries"""
    TOOLS = "tools"
    MCP = "mcp"
    REGISTRY = "registry"
    EXECUTION = "execution"
    INTEGRATION = "integration"


@dataclass
class SampleQuery:
    """Represents a sample query with metadata"""
    query: str
    description: str
    category: QueryCategory
    expected_response_type: str
    tags: List[str]
    context: Optional[str] = None
    complexity_level: str = "beginner"


# Tool-specific sample queries
TOOL_SAMPLE_QUERIES = {
    "mcp_tools": [
        SampleQuery(
            query="List all available MCP servers and their capabilities",
            description="Get a comprehensive list of all MCP servers with their supported tools",
            category=QueryCategory.MCP,
            expected_response_type="list",
            tags=["mcp", "discovery", "servers"],
            complexity_level="beginner"
        ),
        SampleQuery(
            query="Execute the file_operations/read_file tool on README.md",
            description="Use MCP file operations to read a specific file",
            category=QueryCategory.EXECUTION,
            expected_response_type="text",
            tags=["mcp", "file", "read"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Show me the schema for the search/semantic_search tool",
            description="Get detailed schema information for a specific MCP tool",
            category=QueryCategory.TOOLS,
            expected_response_type="schema",
            tags=["mcp", "schema", "search"],
            complexity_level="intermediate"
        )
    ],
    
    "custom_tools": [
        SampleQuery(
            query="Register a new custom tool for data processing",
            description="Create and register a custom tool in the tool registry",
            category=QueryCategory.REGISTRY,
            expected_response_type="success",
            tags=["custom", "register", "data"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Execute my custom data transformation tool with sample data",
            description="Run a previously registered custom tool with input data",
            category=QueryCategory.EXECUTION,
            expected_response_type="result",
            tags=["custom", "execute", "transform"],
            complexity_level="intermediate"
        )
    ],
    
    "tool_discovery": [
        SampleQuery(
            query="Find all tools that can process PDF files",
            description="Search for tools based on capability and file type support",
            category=QueryCategory.TOOLS,
            expected_response_type="list",
            tags=["discovery", "pdf", "search"],
            complexity_level="beginner"
        ),
        SampleQuery(
            query="Show me tools available for data analysis and visualization",
            description="Get tools filtered by specific functional categories",
            category=QueryCategory.TOOLS,
            expected_response_type="list",
            tags=["discovery", "analysis", "visualization"],
            complexity_level="beginner"
        )
    ],
    
    "tool_execution": [
        SampleQuery(
            query="Execute the web_scraper tool on https://example.com",
            description="Run a web scraping tool with a specific URL parameter",
            category=QueryCategory.EXECUTION,
            expected_response_type="data",
            tags=["execute", "web", "scraper"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Run batch processing on multiple files using the image_processor tool",
            description="Execute tool with multiple inputs for batch processing",
            category=QueryCategory.EXECUTION,
            expected_response_type="batch_results",
            tags=["execute", "batch", "image"],
            complexity_level="advanced"
        )
    ],
    
    "tool_integration": [
        SampleQuery(
            query="Connect Slack tool to post workflow notifications",
            description="Integrate external service tools with workflow notifications",
            category=QueryCategory.INTEGRATION,
            expected_response_type="integration",
            tags=["integration", "slack", "notifications"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Set up database tool connection for persistent storage",
            description="Configure database tools for data persistence",
            category=QueryCategory.INTEGRATION,
            expected_response_type="configuration",
            tags=["integration", "database", "storage"],
            complexity_level="advanced"
        )
    ]
}


# Quick start queries for new users
QUICK_START_QUERIES = [
    SampleQuery(
        query="What tools are available?",
        description="Get an overview of all available tools",
        category=QueryCategory.TOOLS,
        expected_response_type="overview",
        tags=["quickstart", "overview"],
        complexity_level="beginner"
    ),
    SampleQuery(
        query="How do I execute a simple file operation?",
        description="Learn basic tool execution with file operations",
        category=QueryCategory.EXECUTION,
        expected_response_type="tutorial",
        tags=["quickstart", "file", "basic"],
        complexity_level="beginner"
    ),
    SampleQuery(
        query="Show me examples of tool usage",
        description="Get practical examples of how to use different tools",
        category=QueryCategory.TOOLS,
        expected_response_type="examples",
        tags=["quickstart", "examples"],
        complexity_level="beginner"
    )
]


# Contextual queries based on user role
CONTEXTUAL_QUERIES = {
    "developer": [
        SampleQuery(
            query="Debug tool execution errors and check logs",
            description="Access debugging information for failed tool executions",
            category=QueryCategory.EXECUTION,
            expected_response_type="debug_info",
            tags=["debug", "logs", "developer"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Create a custom tool with input validation",
            description="Develop custom tools with proper input validation",
            category=QueryCategory.REGISTRY,
            expected_response_type="development",
            tags=["custom", "validation", "developer"],
            complexity_level="advanced"
        )
    ],
    
    "analyst": [
        SampleQuery(
            query="Extract insights from CSV data using analysis tools",
            description="Perform data analysis on structured data files",
            category=QueryCategory.EXECUTION,
            expected_response_type="insights",
            tags=["analysis", "csv", "insights"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Generate reports from multiple data sources",
            description="Create comprehensive reports using data processing tools",
            category=QueryCategory.EXECUTION,
            expected_response_type="report",
            tags=["analysis", "report", "multi-source"],
            complexity_level="intermediate"
        )
    ],
    
    "admin": [
        SampleQuery(
            query="Monitor tool usage and performance metrics",
            description="Access system metrics and tool usage statistics",
            category=QueryCategory.REGISTRY,
            expected_response_type="metrics",
            tags=["admin", "monitoring", "metrics"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Configure tool access permissions and security",
            description="Manage tool security and access control settings",
            category=QueryCategory.REGISTRY,
            expected_response_type="configuration",
            tags=["admin", "security", "permissions"],
            complexity_level="advanced"
        )
    ]
}


# All sample queries organized by category
ALL_SAMPLE_QUERIES = {
    "tools": TOOL_SAMPLE_QUERIES,
    "quick_start": QUICK_START_QUERIES,
    "contextual": CONTEXTUAL_QUERIES
}
