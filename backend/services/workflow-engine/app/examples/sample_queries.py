"""
Sample queries for workflow engine interactions
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class QueryCategory(Enum):
    """Categories for sample queries"""
    WORKFLOWS = "workflows"
    EXECUTION = "execution"
    ORCHESTRATION = "orchestration"
    AUTOMATION = "automation"
    MONITORING = "monitoring"


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


# Workflow-specific sample queries
WORKFLOW_SAMPLE_QUERIES = {
    "workflow_creation": [
        SampleQuery(
            query="Create a new workflow for data processing pipeline",
            description="Define a multi-step workflow for automated data processing",
            category=QueryCategory.WORKFLOWS,
            expected_response_type="workflow_definition",
            tags=["create", "pipeline", "data"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Design a workflow for automated report generation",
            description="Create workflow that generates reports from multiple sources",
            category=QueryCategory.WORKFLOWS,
            expected_response_type="workflow_definition",
            tags=["create", "reports", "automation"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Build a conditional workflow with decision points",
            description="Create complex workflow with branching logic and conditions",
            category=QueryCategory.WORKFLOWS,
            expected_response_type="workflow_definition",
            tags=["create", "conditional", "branching"],
            complexity_level="advanced"
        )
    ],
    
    "workflow_execution": [
        SampleQuery(
            query="Execute my data processing workflow with sample data",
            description="Run a previously defined workflow with input parameters",
            category=QueryCategory.EXECUTION,
            expected_response_type="execution_result",
            tags=["execute", "data", "run"],
            complexity_level="beginner"
        ),
        SampleQuery(
            query="Run workflow in background with notification on completion",
            description="Execute long-running workflow asynchronously with alerts",
            category=QueryCategory.EXECUTION,
            expected_response_type="execution_id",
            tags=["execute", "async", "notifications"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Execute workflow with custom parameters and overrides",
            description="Run workflow with modified parameters for specific use case",
            category=QueryCategory.EXECUTION,
            expected_response_type="execution_result",
            tags=["execute", "parameters", "custom"],
            complexity_level="intermediate"
        )
    ],
    
    "workflow_monitoring": [
        SampleQuery(
            query="Show status of all running workflows",
            description="Get real-time status of active workflow executions",
            category=QueryCategory.MONITORING,
            expected_response_type="status_list",
            tags=["monitor", "status", "active"],
            complexity_level="beginner"
        ),
        SampleQuery(
            query="Get detailed execution history for my workflow",
            description="View complete execution history with performance metrics",
            category=QueryCategory.MONITORING,
            expected_response_type="history",
            tags=["monitor", "history", "metrics"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Monitor workflow performance and identify bottlenecks",
            description="Analyze workflow performance to optimize execution",
            category=QueryCategory.MONITORING,
            expected_response_type="performance_analysis",
            tags=["monitor", "performance", "optimization"],
            complexity_level="advanced"
        )
    ],
    
    "workflow_orchestration": [
        SampleQuery(
            query="Orchestrate multiple workflows in sequence",
            description="Chain multiple workflows to execute in order",
            category=QueryCategory.ORCHESTRATION,
            expected_response_type="orchestration_plan",
            tags=["orchestrate", "sequence", "chain"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Run parallel workflows and merge results",
            description="Execute workflows concurrently and combine outputs",
            category=QueryCategory.ORCHESTRATION,
            expected_response_type="merged_results",
            tags=["orchestrate", "parallel", "merge"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Set up workflow dependencies and triggers",
            description="Configure workflows to trigger based on events or conditions",
            category=QueryCategory.ORCHESTRATION,
            expected_response_type="dependency_config",
            tags=["orchestrate", "triggers", "dependencies"],
            complexity_level="advanced"
        )
    ],
    
    "workflow_automation": [
        SampleQuery(
            query="Schedule workflow to run daily at midnight",
            description="Set up automated workflow execution on a schedule",
            category=QueryCategory.AUTOMATION,
            expected_response_type="schedule_config",
            tags=["automate", "schedule", "recurring"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Create workflow that responds to file uploads",
            description="Set up event-driven workflow triggered by file events",
            category=QueryCategory.AUTOMATION,
            expected_response_type="event_config",
            tags=["automate", "events", "files"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Build self-healing workflow with error recovery",
            description="Create resilient workflow with automatic error handling",
            category=QueryCategory.AUTOMATION,
            expected_response_type="resilience_config",
            tags=["automate", "recovery", "resilience"],
            complexity_level="advanced"
        )
    ]
}


# Quick start queries for new users
QUICK_START_QUERIES = [
    SampleQuery(
        query="What workflows are available?",
        description="Get an overview of all available workflow templates",
        category=QueryCategory.WORKFLOWS,
        expected_response_type="overview",
        tags=["quickstart", "overview"],
        complexity_level="beginner"
    ),
    SampleQuery(
        query="How do I create my first workflow?",
        description="Learn the basics of workflow creation",
        category=QueryCategory.WORKFLOWS,
        expected_response_type="tutorial",
        tags=["quickstart", "create", "basic"],
        complexity_level="beginner"
    ),
    SampleQuery(
        query="Show me simple workflow examples",
        description="Get practical examples of basic workflows",
        category=QueryCategory.WORKFLOWS,
        expected_response_type="examples",
        tags=["quickstart", "examples"],
        complexity_level="beginner"
    ),
    SampleQuery(
        query="Execute a sample workflow",
        description="Run a pre-built workflow to see how execution works",
        category=QueryCategory.EXECUTION,
        expected_response_type="execution_result",
        tags=["quickstart", "execute", "sample"],
        complexity_level="beginner"
    )
]


# Contextual queries based on user role
CONTEXTUAL_QUERIES = {
    "business_analyst": [
        SampleQuery(
            query="Create automated reporting workflow for monthly KPIs",
            description="Build workflow for automated business intelligence reporting",
            category=QueryCategory.AUTOMATION,
            expected_response_type="workflow_definition",
            tags=["business", "reporting", "kpi"],
            complexity_level="intermediate"
        ),
        SampleQuery(
            query="Design approval workflow for budget requests",
            description="Create multi-stage approval process workflow",
            category=QueryCategory.WORKFLOWS,
            expected_response_type="workflow_definition",
            tags=["business", "approval", "budget"],
            complexity_level="intermediate"
        )
    ],
    
    "data_scientist": [
        SampleQuery(
            query="Build ML pipeline workflow for model training",
            description="Create workflow for automated machine learning pipeline",
            category=QueryCategory.WORKFLOWS,
            expected_response_type="workflow_definition",
            tags=["ml", "training", "pipeline"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Set up data validation workflow before model deployment",
            description="Create validation workflow to ensure data quality",
            category=QueryCategory.AUTOMATION,
            expected_response_type="workflow_definition",
            tags=["ml", "validation", "deployment"],
            complexity_level="advanced"
        )
    ],
    
    "devops": [
        SampleQuery(
            query="Create CI/CD workflow for application deployment",
            description="Build continuous integration and deployment workflow",
            category=QueryCategory.AUTOMATION,
            expected_response_type="workflow_definition",
            tags=["devops", "cicd", "deployment"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Monitor workflow infrastructure and resource usage",
            description="Track workflow performance and system resources",
            category=QueryCategory.MONITORING,
            expected_response_type="infrastructure_metrics",
            tags=["devops", "monitoring", "resources"],
            complexity_level="advanced"
        )
    ],
    
    "admin": [
        SampleQuery(
            query="Manage workflow permissions and access control",
            description="Configure security and access policies for workflows",
            category=QueryCategory.WORKFLOWS,
            expected_response_type="security_config",
            tags=["admin", "security", "permissions"],
            complexity_level="advanced"
        ),
        SampleQuery(
            query="Monitor system-wide workflow performance metrics",
            description="Access comprehensive workflow analytics and metrics",
            category=QueryCategory.MONITORING,
            expected_response_type="system_metrics",
            tags=["admin", "metrics", "system"],
            complexity_level="advanced"
        )
    ]
}


# All sample queries organized by category
ALL_SAMPLE_QUERIES = {
    "workflows": WORKFLOW_SAMPLE_QUERIES,
    "quick_start": QUICK_START_QUERIES,
    "contextual": CONTEXTUAL_QUERIES
}
