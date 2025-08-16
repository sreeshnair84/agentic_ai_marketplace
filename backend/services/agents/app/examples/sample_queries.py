"""
Sample queries for agents, tools, and workflows to help users understand
how to interact with different components in the chat interface.
"""

from typing import Dict, List, Any, Optional
from enum import Enum

class QueryCategory(str, Enum):
    GENERAL = "general"
    CONVERSATION = "conversation"
    RAG = "rag"
    TASK_EXECUTION = "task_execution"
    TOOLS = "tools"
    WORKFLOWS = "workflows"

class SampleQuery:
    def __init__(self, query: str, description: str, category: QueryCategory, 
                 expected_response_type: str = "text", tags: Optional[List[str]] = None):
        self.query = query
        self.description = description
        self.category = category
        self.expected_response_type = expected_response_type
        self.tags = tags or []

# Agent Sample Queries
AGENT_SAMPLE_QUERIES = {
    "general_ai_agent": [
        SampleQuery(
            query="Analyze the pros and cons of remote work for software development teams",
            description="Ask the agent to provide a balanced analysis of a topic",
            category=QueryCategory.GENERAL,
            tags=["analysis", "comparison", "workplace"]
        ),
        SampleQuery(
            query="Explain machine learning concepts in simple terms",
            description="Request explanations of complex topics in accessible language",
            category=QueryCategory.GENERAL,
            tags=["explanation", "education", "technology"]
        ),
        SampleQuery(
            query="What are the best practices for API design?",
            description="Get expert advice on technical best practices",
            category=QueryCategory.GENERAL,
            tags=["best-practices", "api", "development"]
        ),
        SampleQuery(
            query="Help me brainstorm ideas for a mobile app that helps with productivity",
            description="Collaborative ideation and creative thinking",
            category=QueryCategory.GENERAL,
            tags=["brainstorming", "creativity", "mobile-apps"]
        ),
        SampleQuery(
            query="Compare different database types: SQL vs NoSQL vs Graph databases",
            description="Technical comparisons with detailed explanations",
            category=QueryCategory.GENERAL,
            tags=["databases", "comparison", "technical"]
        )
    ],
    
    "conversation_agent": [
        SampleQuery(
            query="Hi, I'm working on a new project and need some guidance",
            description="Start a conversational session with context setting",
            category=QueryCategory.CONVERSATION,
            tags=["greeting", "project-help", "guidance"]
        ),
        SampleQuery(
            query="Can you remember what we discussed about the database schema last time?",
            description="Reference previous conversation context",
            category=QueryCategory.CONVERSATION,
            tags=["memory", "context", "database"]
        ),
        SampleQuery(
            query="I'm feeling overwhelmed with all these technical decisions. Can you help prioritize?",
            description="Emotional context with request for structured help",
            category=QueryCategory.CONVERSATION,
            tags=["prioritization", "decision-making", "support"]
        ),
        SampleQuery(
            query="Let's continue where we left off with the API implementation",
            description="Resume previous conversation thread",
            category=QueryCategory.CONVERSATION,
            tags=["continuation", "api", "implementation"]
        ),
        SampleQuery(
            query="I need a quick recap of our discussion about microservices",
            description="Request summary of previous conversation topics",
            category=QueryCategory.CONVERSATION,
            tags=["recap", "summary", "microservices"]
        )
    ],
    
    "rag_agent": [
        SampleQuery(
            query="What does our company's security policy say about data encryption?",
            description="Query specific information from indexed documents",
            category=QueryCategory.RAG,
            tags=["security", "policy", "documentation"]
        ),
        SampleQuery(
            query="Find information about authentication implementation in our architecture docs",
            description="Search for technical implementation details",
            category=QueryCategory.RAG,
            tags=["authentication", "architecture", "implementation"]
        ),
        SampleQuery(
            query="Show me examples of error handling from our codebase documentation",
            description="Retrieve code examples and patterns from knowledge base",
            category=QueryCategory.RAG,
            tags=["error-handling", "examples", "code"]
        ),
        SampleQuery(
            query="What are the deployment requirements mentioned in our operations manual?",
            description="Extract specific requirements from operational documents",
            category=QueryCategory.RAG,
            tags=["deployment", "requirements", "operations"]
        ),
        SampleQuery(
            query="Compare the different payment gateway options discussed in our vendor evaluation docs",
            description="Comparative analysis based on documented evaluations",
            category=QueryCategory.RAG,
            tags=["comparison", "vendors", "payments"]
        )
    ],
    
    "task_executor_agent": [
        SampleQuery(
            query="Process this CSV file and generate a summary report with key statistics",
            description="Execute structured data processing tasks",
            category=QueryCategory.TASK_EXECUTION,
            tags=["data-processing", "csv", "statistics"]
        ),
        SampleQuery(
            query="Create a project plan with milestones for a 3-month software development project",
            description="Generate structured project deliverables",
            category=QueryCategory.TASK_EXECUTION,
            tags=["project-planning", "milestones", "structured-output"]
        ),
        SampleQuery(
            query="Analyze this dataset and identify trends, patterns, and anomalies",
            description="Complex analytical tasks with multiple outputs",
            category=QueryCategory.TASK_EXECUTION,
            tags=["analysis", "trends", "patterns", "anomalies"]
        ),
        SampleQuery(
            query="Generate a technical specification document based on these requirements",
            description="Document generation from structured input",
            category=QueryCategory.TASK_EXECUTION,
            tags=["documentation", "specifications", "requirements"]
        ),
        SampleQuery(
            query="Execute a multi-step data validation and transformation workflow",
            description="Complex multi-step task execution",
            category=QueryCategory.TASK_EXECUTION,
            tags=["validation", "transformation", "workflow"]
        )
    ]
}

# Tool Sample Queries
TOOL_SAMPLE_QUERIES = {
    "file_operations": [
        SampleQuery(
            query="List all Python files in the src directory",
            description="File system navigation and filtering",
            category=QueryCategory.TOOLS,
            tags=["files", "listing", "python"]
        ),
        SampleQuery(
            query="Read the contents of config.json and show me the database settings",
            description="File reading with specific information extraction",
            category=QueryCategory.TOOLS,
            tags=["file-reading", "configuration", "json"]
        ),
        SampleQuery(
            query="Create a backup copy of the database schema file",
            description="File manipulation and backup operations",
            category=QueryCategory.TOOLS,
            tags=["backup", "file-copy", "database"]
        )
    ],
    
    "data_tools": [
        SampleQuery(
            query="Convert this CSV data to JSON format with proper field mapping",
            description="Data format transformation",
            category=QueryCategory.TOOLS,
            tags=["conversion", "csv", "json"]
        ),
        SampleQuery(
            query="Validate email addresses in this dataset and flag invalid ones",
            description="Data validation and quality checks",
            category=QueryCategory.TOOLS,
            tags=["validation", "email", "data-quality"]
        ),
        SampleQuery(
            query="Generate sample test data for user registration with 100 records",
            description="Test data generation",
            category=QueryCategory.TOOLS,
            tags=["test-data", "generation", "users"]
        )
    ],
    
    "api_tools": [
        SampleQuery(
            query="Fetch user information from the external user service API",
            description="External API integration and data retrieval",
            category=QueryCategory.TOOLS,
            tags=["api", "external", "users"]
        ),
        SampleQuery(
            query="Send a notification to the Slack channel about deployment status",
            description="Integration with communication tools",
            category=QueryCategory.TOOLS,
            tags=["notifications", "slack", "deployment"]
        ),
        SampleQuery(
            query="Check the health status of all microservices in our environment",
            description="Service monitoring and health checks",
            category=QueryCategory.TOOLS,
            tags=["health-check", "monitoring", "microservices"]
        )
    ],
    
    "database_tools": [
        SampleQuery(
            query="Execute a query to find all users created in the last 30 days",
            description="Database querying with date filters",
            category=QueryCategory.TOOLS,
            tags=["database", "query", "users", "date-filter"]
        ),
        SampleQuery(
            query="Generate a database schema diagram for the user management tables",
            description="Database visualization and documentation",
            category=QueryCategory.TOOLS,
            tags=["schema", "diagram", "visualization"]
        ),
        SampleQuery(
            query="Backup the production database with timestamp",
            description="Database backup operations",
            category=QueryCategory.TOOLS,
            tags=["backup", "database", "production"]
        )
    ]
}

# Workflow Sample Queries
WORKFLOW_SAMPLE_QUERIES = {
    "data_processing_workflows": [
        SampleQuery(
            query="Run the customer data ingestion workflow for today's batch",
            description="Execute data pipeline workflows",
            category=QueryCategory.WORKFLOWS,
            tags=["data-ingestion", "batch-processing", "customers"]
        ),
        SampleQuery(
            query="Start the ETL workflow to process sales data and update the analytics dashboard",
            description="Complex data transformation and loading",
            category=QueryCategory.WORKFLOWS,
            tags=["etl", "sales-data", "analytics"]
        ),
        SampleQuery(
            query="Execute the data quality validation workflow on the user registration dataset",
            description="Data quality and validation workflows",
            category=QueryCategory.WORKFLOWS,
            tags=["data-quality", "validation", "user-data"]
        )
    ],
    
    "deployment_workflows": [
        SampleQuery(
            query="Deploy the latest version of the user service to staging environment",
            description="Application deployment automation",
            category=QueryCategory.WORKFLOWS,
            tags=["deployment", "staging", "user-service"]
        ),
        SampleQuery(
            query="Run the complete CI/CD pipeline for the frontend application",
            description="Full build and deployment pipeline",
            category=QueryCategory.WORKFLOWS,
            tags=["cicd", "frontend", "pipeline"]
        ),
        SampleQuery(
            query="Execute the rollback workflow to revert to the previous stable version",
            description="Rollback and recovery workflows",
            category=QueryCategory.WORKFLOWS,
            tags=["rollback", "recovery", "version-control"]
        )
    ],
    
    "monitoring_workflows": [
        SampleQuery(
            query="Run the system health check workflow across all environments",
            description="Comprehensive system monitoring",
            category=QueryCategory.WORKFLOWS,
            tags=["health-check", "monitoring", "all-environments"]
        ),
        SampleQuery(
            query="Execute the performance testing workflow on the API endpoints",
            description="Automated performance testing",
            category=QueryCategory.WORKFLOWS,
            tags=["performance", "testing", "api"]
        ),
        SampleQuery(
            query="Start the security scan workflow for vulnerability assessment",
            description="Security and compliance workflows",
            category=QueryCategory.WORKFLOWS,
            tags=["security", "vulnerability", "scanning"]
        )
    ],
    
    "business_workflows": [
        SampleQuery(
            query="Process the monthly report generation workflow for all departments",
            description="Automated business reporting",
            category=QueryCategory.WORKFLOWS,
            tags=["reporting", "monthly", "departments"]
        ),
        SampleQuery(
            query="Run the customer onboarding workflow for new enterprise clients",
            description="Business process automation",
            category=QueryCategory.WORKFLOWS,
            tags=["onboarding", "customers", "enterprise"]
        ),
        SampleQuery(
            query="Execute the invoice processing workflow for accounts payable",
            description="Financial process automation",
            category=QueryCategory.WORKFLOWS,
            tags=["invoices", "accounts-payable", "finance"]
        )
    ]
}

# Combined sample queries for easy access
ALL_SAMPLE_QUERIES = {
    "agents": AGENT_SAMPLE_QUERIES,
    "tools": TOOL_SAMPLE_QUERIES,
    "workflows": WORKFLOW_SAMPLE_QUERIES
}

def get_sample_queries_by_category(category: QueryCategory) -> List[SampleQuery]:
    """Get all sample queries for a specific category"""
    queries = []
    for component_type in ALL_SAMPLE_QUERIES.values():
        for component_queries in component_type.values():
            queries.extend([q for q in component_queries if q.category == category])
    return queries

def get_sample_queries_by_tags(tags: List[str]) -> List[SampleQuery]:
    """Get sample queries that match any of the provided tags"""
    queries = []
    for component_type in ALL_SAMPLE_QUERIES.values():
        for component_queries in component_type.values():
            for query in component_queries:
                if any(tag in query.tags for tag in tags):
                    queries.append(query)
    return queries

def get_random_sample_queries(count: int = 5) -> List[SampleQuery]:
    """Get a random selection of sample queries"""
    import random
    all_queries = []
    for component_type in ALL_SAMPLE_QUERIES.values():
        for component_queries in component_type.values():
            all_queries.extend(component_queries)
    
    return random.sample(all_queries, min(count, len(all_queries)))

# Quick start suggestions for new users
QUICK_START_QUERIES = [
    SampleQuery(
        query="What can you help me with?",
        description="Get an overview of available capabilities",
        category=QueryCategory.GENERAL,
        tags=["help", "overview", "capabilities"]
    ),
    SampleQuery(
        query="Show me examples of what I can ask",
        description="Get sample queries and use cases",
        category=QueryCategory.GENERAL,
        tags=["examples", "samples", "help"]
    ),
    SampleQuery(
        query="List all available agents and their specialties",
        description="Discover available agents",
        category=QueryCategory.GENERAL,
        tags=["agents", "discovery", "capabilities"]
    ),
    SampleQuery(
        query="What tools are available for data processing?",
        description="Explore available tools by category",
        category=QueryCategory.TOOLS,
        tags=["tools", "data-processing", "discovery"]
    ),
    SampleQuery(
        query="Show me the status of running workflows",
        description="Monitor workflow execution",
        category=QueryCategory.WORKFLOWS,
        tags=["workflows", "status", "monitoring"]
    )
]

# Context-aware suggestions based on user activity
CONTEXTUAL_SUGGESTIONS = {
    "first_time_user": [
        "What can you help me with?",
        "Show me examples of what I can ask",
        "List all available agents and their specialties"
    ],
    "data_analyst": [
        "Process this CSV file and generate a summary report",
        "Analyze this dataset and identify trends and patterns",
        "Run the data quality validation workflow"
    ],
    "developer": [
        "What are the best practices for API design?",
        "Show me examples of error handling from our codebase",
        "Execute a query to find all users created in the last 30 days"
    ],
    "project_manager": [
        "Create a project plan with milestones for a 3-month project",
        "Run the monthly report generation workflow",
        "Check the health status of all microservices"
    ],
    "devops_engineer": [
        "Deploy the latest version to staging environment",
        "Run the complete CI/CD pipeline",
        "Execute the system health check workflow"
    ]
}

def get_contextual_suggestions(user_role: Optional[str] = None, recent_queries: Optional[List[str]] = None) -> List[str]:
    """Get contextual suggestions based on user role or recent activity"""
    if user_role and user_role in CONTEXTUAL_SUGGESTIONS:
        return CONTEXTUAL_SUGGESTIONS[user_role]
    
    # If no role specified, return general quick start suggestions
    return [q.query for q in QUICK_START_QUERIES]

# Export main functions and data
__all__ = [
    'SampleQuery',
    'QueryCategory',
    'ALL_SAMPLE_QUERIES',
    'AGENT_SAMPLE_QUERIES',
    'TOOL_SAMPLE_QUERIES',
    'WORKFLOW_SAMPLE_QUERIES',
    'QUICK_START_QUERIES',
    'get_sample_queries_by_category',
    'get_sample_queries_by_tags',
    'get_random_sample_queries',
    'get_contextual_suggestions'
]
