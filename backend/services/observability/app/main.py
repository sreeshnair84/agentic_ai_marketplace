"""
Observability Service - Monitoring, metrics, and tracing
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from contextlib import asynccontextmanager
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['service', 'method', 'endpoint']
)

active_connections = Gauge(
    'active_connections_total',
    'Active connections',
    ['service']
)

# A2A Protocol metrics
a2a_messages_total = Counter(
    'a2a_messages_total',
    'Total A2A messages',
    ['from_service', 'to_service', 'method', 'status']
)

a2a_message_duration = Histogram(
    'a2a_message_duration_seconds',
    'A2A message processing time',
    ['from_service', 'to_service', 'method']
)

# Agent metrics
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_type', 'status']
)

agent_execution_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution time',
    ['agent_type']
)

# Workflow metrics
workflow_executions_total = Counter(
    'workflow_executions_total',
    'Total workflow executions',
    ['workflow_name', 'status']
)

workflow_execution_duration = Histogram(
    'workflow_execution_duration_seconds',
    'Workflow execution time',
    ['workflow_name']
)

# Tool metrics
tool_executions_total = Counter(
    'tool_executions_total',
    'Total tool executions',
    ['tool_name', 'status']
)

tool_execution_duration = Histogram(
    'tool_execution_duration_seconds',
    'Tool execution time',
    ['tool_name']
)

# System metrics
system_memory_usage = Gauge('system_memory_usage_bytes', 'System memory usage')
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage')

# Pydantic models
class MetricPoint(BaseModel):
    timestamp: datetime
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)

class LogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    service: str
    message: str
    data: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service: str
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "ok"  # ok, error, timeout
    tags: Dict[str, str] = Field(default_factory=dict)
    logs: List[Dict[str, Any]] = Field(default_factory=list)

class HealthStatus(BaseModel):
    service: str
    status: str  # healthy, unhealthy, unknown
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

# In-memory storage (in production, use proper time-series DB)
metrics_storage: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
logs_storage: deque = deque(maxlen=50000)
traces_storage: Dict[str, List[TraceSpan]] = defaultdict(list)
health_storage: Dict[str, HealthStatus] = {}

# Service discovery
MONITORED_SERVICES = {
    "gateway": "http://localhost:8000",
    "agents": "http://localhost:8002", 
    "orchestrator": "http://localhost:8003",
    "rag": "http://localhost:8004",
    "tools": "http://localhost:8005",
    "sqltool": "http://localhost:8006",
    "workflow-engine": "http://localhost:8007"
}

# HTTP client for health checks
http_client = httpx.AsyncClient(timeout=5.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    
    # Startup
    logger.info("Starting Observability service...")
    
    # Start background tasks
    asyncio.create_task(health_check_task())
    asyncio.create_task(system_metrics_task())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Observability service...")
    await http_client.aclose()

app = FastAPI(
    title="Observability Service",
    description="Monitoring, metrics, tracing, and logging service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    service_status = {}
    for service, url in MONITORED_SERVICES.items():
        if service in health_storage:
            status = health_storage[service]
            service_status[service] = {
                "status": status.status,
                "last_check": status.last_check,
                "response_time_ms": status.response_time_ms
            }
        else:
            service_status[service] = {"status": "unknown"}
    
    return {
        "status": "healthy",
        "service": "observability",
        "version": "1.0.0",
        "features": {
            "metrics_collection": True,
            "distributed_tracing": True,
            "log_aggregation": True,
            "health_monitoring": True,
            "prometheus_export": True
        },
        "monitored_services": service_status,
        "storage_stats": {
            "metrics_points": sum(len(q) for q in metrics_storage.values()),
            "log_entries": len(logs_storage),
            "active_traces": len(traces_storage)
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Observability Service",
        "version": "1.0.0",
        "description": "Monitoring, metrics, tracing, and logging service",
        "endpoints": {
            "metrics": "/metrics",
            "prometheus": "/prometheus",
            "traces": "/traces",
            "logs": "/logs",
            "health_status": "/services/health",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/prometheus", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.post("/metrics")
async def record_metric(
    name: str,
    value: float,
    labels: Optional[Dict[str, str]] = None,
    timestamp: Optional[datetime] = None
):
    """Record a custom metric"""
    
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    metric_point = MetricPoint(
        timestamp=timestamp,
        value=value,
        labels=labels or {}
    )
    
    metrics_storage[name].append(metric_point)
    
    return {"message": f"Metric '{name}' recorded successfully"}


@app.get("/metrics/{metric_name}")
async def get_metric(
    metric_name: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000
):
    """Get metric data"""
    
    if metric_name not in metrics_storage:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
    
    points = list(metrics_storage[metric_name])
    
    # Apply time filters
    if start_time:
        points = [p for p in points if p.timestamp >= start_time]
    if end_time:
        points = [p for p in points if p.timestamp <= end_time]
    
    # Apply limit
    points = points[-limit:]
    
    return {
        "metric_name": metric_name,
        "points": points,
        "count": len(points)
    }


@app.get("/metrics")
async def list_metrics():
    """List all available metrics"""
    
    metrics_info = {}
    
    for name, points in metrics_storage.items():
        if points:
            latest = points[-1]
            metrics_info[name] = {
                "latest_value": latest.value,
                "latest_timestamp": latest.timestamp,
                "point_count": len(points),
                "labels": latest.labels
            }
    
    return {
        "metrics": metrics_info,
        "total_metrics": len(metrics_info)
    }


@app.post("/logs")
async def record_log(log_entry: LogEntry):
    """Record a log entry"""
    
    logs_storage.append(log_entry)
    
    return {"message": "Log entry recorded successfully"}


@app.get("/logs")
async def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
    search: Optional[str] = None
):
    """Get log entries"""
    
    logs = list(logs_storage)
    
    # Apply filters
    if service:
        logs = [log for log in logs if log.service == service]
    if level:
        logs = [log for log in logs if log.level.lower() == level.lower()]
    if start_time:
        logs = [log for log in logs if log.timestamp >= start_time]
    if end_time:
        logs = [log for log in logs if log.timestamp <= end_time]
    if search:
        logs = [log for log in logs if search.lower() in log.message.lower()]
    
    # Sort by timestamp (newest first) and apply limit
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    logs = logs[:limit]
    
    return {
        "logs": logs,
        "count": len(logs),
        "total_in_storage": len(logs_storage)
    }


@app.post("/traces")
async def record_trace_span(span: TraceSpan):
    """Record a trace span"""
    
    # Calculate duration if end_time is provided
    if span.end_time and span.start_time:
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
    
    traces_storage[span.trace_id].append(span)
    
    return {"message": f"Trace span recorded for trace {span.trace_id}"}


@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get all spans for a trace"""
    
    if trace_id not in traces_storage:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found")
    
    spans = traces_storage[trace_id]
    
    # Sort by start time
    spans.sort(key=lambda x: x.start_time)
    
    # Calculate total trace duration
    if spans:
        start_time = min(span.start_time for span in spans)
        end_times = [span.end_time for span in spans if span.end_time]
        end_time = max(end_times) if end_times else None
        
        total_duration_ms = None
        if end_time:
            total_duration_ms = (end_time - start_time).total_seconds() * 1000
    else:
        start_time = None
        end_time = None
        total_duration_ms = None
    
    return {
        "trace_id": trace_id,
        "spans": spans,
        "span_count": len(spans),
        "start_time": start_time,
        "end_time": end_time,
        "total_duration_ms": total_duration_ms
    }


@app.get("/traces")
async def list_traces(
    service: Optional[str] = None,
    operation: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """List traces"""
    
    traces = []
    
    for trace_id, spans in traces_storage.items():
        if not spans:
            continue
        
        # Apply filters
        if service and not any(span.service == service for span in spans):
            continue
        if operation and not any(span.operation == operation for span in spans):
            continue
        if status and not any(span.status == status for span in spans):
            continue
        
        # Calculate trace summary
        start_time = min(span.start_time for span in spans)
        end_times = [span.end_time for span in spans if span.end_time]
        end_time = max(end_times) if end_times else None
        
        total_duration_ms = None
        if end_time:
            total_duration_ms = (end_time - start_time).total_seconds() * 1000
        
        services = list(set(span.service for span in spans))
        operations = list(set(span.operation for span in spans))
        
        traces.append({
            "trace_id": trace_id,
            "span_count": len(spans),
            "services": services,
            "operations": operations,
            "start_time": start_time,
            "end_time": end_time,
            "total_duration_ms": total_duration_ms,
            "status": "error" if any(span.status == "error" for span in spans) else "ok"
        })
    
    # Sort by start time (newest first) and apply limit
    traces.sort(key=lambda x: x["start_time"] or datetime.min, reverse=True)
    traces = traces[:limit]
    
    return {
        "traces": traces,
        "count": len(traces),
        "total_in_storage": len(traces_storage)
    }


@app.get("/services/health")
async def get_services_health():
    """Get health status of all monitored services"""
    
    return {
        "services": dict(health_storage),
        "total_services": len(MONITORED_SERVICES),
        "healthy_services": len([s for s in health_storage.values() if s.status == "healthy"]),
        "unhealthy_services": len([s for s in health_storage.values() if s.status == "unhealthy"])
    }


@app.get("/services/{service_name}/health")
async def get_service_health(service_name: str):
    """Get health status of specific service"""
    
    if service_name not in health_storage:
        # Try to check service immediately
        if service_name in MONITORED_SERVICES:
            await check_service_health(service_name, MONITORED_SERVICES[service_name])
        
        if service_name not in health_storage:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    return health_storage[service_name]


@app.post("/services/{service_name}/health/check")
async def force_health_check(service_name: str):
    """Force health check for specific service"""
    
    if service_name not in MONITORED_SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not monitored")
    
    await check_service_health(service_name, MONITORED_SERVICES[service_name])
    
    return {
        "message": f"Health check completed for {service_name}",
        "status": health_storage[service_name]
    }


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    
    # Service health summary
    healthy_services = len([s for s in health_storage.values() if s.status == "healthy"])
    total_services = len(MONITORED_SERVICES)
    
    # Recent activity
    recent_logs = len([log for log in logs_storage if log.timestamp > datetime.utcnow() - timedelta(hours=1)])
    recent_traces = len([tid for tid, spans in traces_storage.items() 
                        if spans and any(span.start_time > datetime.utcnow() - timedelta(hours=1) for span in spans)])
    
    # Error rates
    error_logs = len([log for log in logs_storage if log.level.lower() in ["error", "critical"]])
    error_traces = len([tid for tid, spans in traces_storage.items() 
                       if spans and any(span.status == "error" for span in spans)])
    
    return {
        "services": {
            "healthy": healthy_services,
            "total": total_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0
        },
        "activity": {
            "recent_logs": recent_logs,
            "recent_traces": recent_traces,
            "total_logs": len(logs_storage),
            "total_traces": len(traces_storage)
        },
        "errors": {
            "error_logs": error_logs,
            "error_traces": error_traces,
            "error_rate": (error_logs / len(logs_storage) * 100) if logs_storage else 0
        },
        "storage": {
            "metrics_points": sum(len(q) for q in metrics_storage.values()),
            "log_entries": len(logs_storage),
            "trace_count": len(traces_storage)
        }
    }


async def health_check_task():
    """Background task to check service health"""
    
    while True:
        try:
            # Check all monitored services
            tasks = []
            for service_name, url in MONITORED_SERVICES.items():
                tasks.append(check_service_health(service_name, url))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Wait before next check
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Health check task error: {e}")
            await asyncio.sleep(30)


async def check_service_health(service_name: str, url: str):
    """Check health of individual service"""
    
    start_time = time.time()
    
    try:
        async with http_client as client:
            response = await client.get(f"{url}/health")
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = "healthy"
                error_message = None
            else:
                status = "unhealthy"
                error_message = f"HTTP {response.status_code}"
            
            health_storage[service_name] = HealthStatus(
                service=service_name,
                status=status,
                last_check=datetime.utcnow(),
                response_time_ms=response_time_ms,
                error_message=error_message
            )
            
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        
        health_storage[service_name] = HealthStatus(
            service=service_name,
            status="unhealthy",
            last_check=datetime.utcnow(),
            response_time_ms=response_time_ms,
            error_message=str(e)
        )


async def system_metrics_task():
    """Background task to collect system metrics"""
    
    while True:
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.used)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Record as custom metrics too
            await record_metric("system_memory_usage_bytes", memory.used)
            await record_metric("system_cpu_usage_percent", cpu_percent)
            
            await asyncio.sleep(30)  # Collect every 30 seconds
            
        except ImportError:
            # psutil not available, skip system metrics
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"System metrics task error: {e}")
            await asyncio.sleep(30)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
