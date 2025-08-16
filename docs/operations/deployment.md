# Deployment Documentation for Agentic AI Acceleration

## Overview

This document outlines the deployment strategies and considerations for the Agentic AI Acceleration. The platform consists of multiple Python FastAPI microservices, each responsible for different functionalities, including agent management, tool invocation, RAG processing, SQL querying, observability, and workflow execution. The backend is built with Python FastAPI for high performance and async capabilities.

## Architecture Components

### Backend Services (Python FastAPI)
- **Gateway Service**: API Gateway and routing
- **Orchestrator Service**: Multi-agent orchestration and supervision
- **Agents Service**: Agent lifecycle management and framework adapters
- **Tools Service**: Tool integration and MCP protocol support
- **RAG Service**: Document processing and vector search
- **SQL Tool Service**: Database connectivity and query execution
- **Workflow Engine**: Workflow definition and execution
- **Observability Service**: Monitoring, tracing, and metrics

### Frontend (Next.js)
- **Web Application**: React-based user interface with TypeScript

## Deployment Strategies

### 1. Containerization

All services are containerized using Docker with Python FastAPI runtime. The `docker-compose.yml` file defines the services, networks, and volumes required for local development and testing. Each service can be run independently or as part of a larger stack.

### 2. Kubernetes Deployment

For production environments, Kubernetes is recommended for orchestrating the deployment of services. The `infra/k8s` directory contains the necessary Kubernetes manifests for deploying each service, including:

- **Deployments**: Define the desired state for each service, including replicas, container images, and resource limits.
- **Services**: Expose the deployments to allow communication between services and external access.
- **Ingress**: Manage external access to the services through a single entry point.

### 3. Terraform Infrastructure

Terraform scripts located in the `infra/terraform` directory can be used to provision cloud infrastructure. This includes setting up Kubernetes clusters, networking, and any other required resources.

## Deployment Steps

### Local Development

1. **Clone the Repository**: 
   ```bash
   git clone <repository-url>
   cd lcnc-multiagent-platform
   ```

2. **Install Python Dependencies** (for each service):
   ```bash
   # Navigate to each service directory
   cd services/gateway
   pip install -r requirements.txt
   
   # Or using UV (recommended for faster installs)
   uv pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   ```bash
   # Copy and configure environment files
   cp .env.example .env
   # Edit .env with your database and API configurations
   ```

4. **Build and Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

5. **Alternative - Run Services Individually**:
   ```bash
   # Terminal 1 - Gateway Service
   cd services/gateway
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2 - Orchestrator Service
   cd services/orchestrator
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   
   # Terminal 3 - Frontend
   cd apps/web
   npm run dev
   ```

6. **Access the Application**: Open your browser and navigate to `http://localhost:3000` to access the Next.js frontend.

### Production Deployment

#### Prerequisites
- Kubernetes cluster (AKS, EKS, GKE, or on-premises)
- Container registry (Azure Container Registry, Docker Hub, etc.)
- PostgreSQL database
- Redis instance
- Vector database (Pinecone, Weaviate, or Chroma)

#### Build and Push Container Images

```bash
# Build all service images
docker build -t <registry>/lcnc-gateway:latest services/gateway/
docker build -t <registry>/lcnc-orchestrator:latest services/orchestrator/
docker build -t <registry>/lcnc-agents:latest services/agents/
docker build -t <registry>/lcnc-tools:latest services/tools/
docker build -t <registry>/lcnc-rag:latest services/rag/
docker build -t <registry>/lcnc-sqltool:latest services/sqltool/
docker build -t <registry>/lcnc-workflow:latest services/workflow_engine/
docker build -t <registry>/lcnc-observability:latest services/observability/
docker build -t <registry>/lcnc-web:latest apps/web/

# Push images to registry
docker push <registry>/lcnc-gateway:latest
docker push <registry>/lcnc-orchestrator:latest
# ... repeat for all services
```

#### Deploy to Kubernetes

1. **Prepare Kubernetes Manifests**: Ensure that all Kubernetes manifests in the `infra/k8s` directory are configured correctly for your environment.

2. **Create Namespace and Secrets**:
   ```bash
   # Create namespace
   kubectl create namespace lcnc-platform
   
   # Create database secrets
   kubectl create secret generic postgres-secret \
     --from-literal=username=<db-username> \
     --from-literal=password=<db-password> \
     --from-literal=host=<db-host> \
     --from-literal=database=<db-name> \
     -n lcnc-platform
   
   # Create Redis secrets
   kubectl create secret generic redis-secret \
     --from-literal=url=<redis-url> \
     --from-literal=password=<redis-password> \
     -n lcnc-platform
   
   # Create API keys and external service secrets
   kubectl create secret generic api-keys \
     --from-literal=openai-api-key=<openai-key> \
     --from-literal=anthropic-api-key=<anthropic-key> \
     --from-literal=jwt-secret=<jwt-secret> \
     -n lcnc-platform
   ```

3. **Deploy Services**:
   ```bash
   # Deploy infrastructure components first
   kubectl apply -f infra/k8s/deployments/ -n lcnc-platform
   kubectl apply -f infra/k8s/services/ -n lcnc-platform
   
   # Deploy ingress
   kubectl apply -f infra/k8s/ingress/ -n lcnc-platform
   ```

4. **Monitor Deployment**: Use the following commands to check the status:
   ```bash
   # Check pod status
   kubectl get pods -n lcnc-platform
   
   # Check service endpoints
   kubectl get services -n lcnc-platform
   
   # Check deployment status
   kubectl get deployments -n lcnc-platform
   
   # View logs for specific service
   kubectl logs -f deployment/gateway-deployment -n lcnc-platform
   ```

5. **Health Checks**: Verify all services are running:
   ```bash
   # Check gateway health
   curl http://<ingress-url>/api/gateway/health
   
   # Check orchestrator health
   curl http://<ingress-url>/api/orchestrator/health
   
   # Check individual service health endpoints
   curl http://<ingress-url>/api/agents/health
   curl http://<ingress-url>/api/tools/health
   curl http://<ingress-url>/api/rag/health
   ```

## Performance Configuration

### FastAPI Optimization Settings

```yaml
# Environment variables for production deployment
FASTAPI_ENV: "production"
UVICORN_WORKERS: "4"  # Number of worker processes
UVICORN_WORKER_CLASS: "uvicorn.workers.UvicornWorker"
UVICORN_MAX_REQUESTS: "1000"  # Max requests per worker before restart
UVICORN_MAX_REQUESTS_JITTER: "100"

# Database connection pooling
DATABASE_POOL_SIZE: "20"
DATABASE_MAX_OVERFLOW: "30"
DATABASE_POOL_TIMEOUT: "30"
DATABASE_POOL_RECYCLE: "3600"

# Redis connection pooling
REDIS_POOL_SIZE: "10"
REDIS_MAX_CONNECTIONS: "50"

# Async processing
ASYNC_BATCH_SIZE: "100"
ASYNC_TIMEOUT: "30"
```

### Resource Limits (Kubernetes)

```yaml
# Example resource configuration for each service
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

# Gateway service (higher limits for routing)
gateway:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"

# RAG service (higher memory for vector processing)
rag:
  requests:
    memory: "2Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "1000m"
```

## Database Migration

### Initial Setup

```bash
# Run database migrations for each service
cd services/gateway
alembic upgrade head

cd ../orchestrator
alembic upgrade head

cd ../agents
alembic upgrade head

# Repeat for all services with database dependencies
```

### Schema Updates

```bash
# Generate new migration
cd services/<service-name>
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

## Observability and Monitoring

The platform includes comprehensive observability through the dedicated observability service and OpenTelemetry integration.

### Key Observability Endpoints

- **Health Checks**: `GET /api/{service}/health`
- **Metrics**: `GET /api/observability/metrics`
- **Traces**: `GET /api/observability/traces`
- **Logs**: `GET /api/observability/logs`
- **Service Discovery**: `GET /api/observability/services`

### Monitoring Stack Integration

```yaml
# Prometheus configuration for metrics collection
prometheus:
  enabled: true
  scrape_configs:
    - job_name: 'lcnc-services'
      static_configs:
        - targets: ['gateway:8000', 'orchestrator:8001', 'agents:8002']
      metrics_path: '/metrics'
      scrape_interval: 15s

# Jaeger configuration for distributed tracing
jaeger:
  enabled: true
  collector:
    endpoint: "http://jaeger-collector:14268/api/traces"
  sampler:
    type: "probabilistic"
    param: 0.1  # Sample 10% of traces

# ELK Stack for log aggregation
elasticsearch:
  enabled: true
  hosts: ["elasticsearch:9200"]
  index_pattern: "lcnc-logs-*"
```

### Performance Metrics

Key metrics to monitor:

- **Request Rate**: Requests per second per service
- **Response Time**: P50, P95, P99 percentiles
- **Error Rate**: 4xx and 5xx response rates
- **Database Performance**: Query execution time, connection pool usage
- **Memory Usage**: Heap size, garbage collection metrics
- **CPU Utilization**: Per service and total cluster usage

## Security Considerations

### API Security

```yaml
# Environment variables for security
JWT_SECRET_KEY: "<secure-random-key>"
JWT_ALGORITHM: "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "30"
JWT_REFRESH_TOKEN_EXPIRE_DAYS: "7"

# CORS configuration
CORS_ORIGINS: '["http://localhost:3000", "https://yourdomain.com"]'
CORS_ALLOW_CREDENTIALS: "true"
CORS_ALLOW_METHODS: '["GET", "POST", "PUT", "DELETE"]'
CORS_ALLOW_HEADERS: '["*"]'

# Rate limiting
RATE_LIMIT_REQUESTS: "100"
RATE_LIMIT_WINDOW: "60"  # seconds
```

### Database Security

```yaml
# PostgreSQL security settings
DATABASE_SSL_MODE: "require"
DATABASE_SSL_CERT: "/path/to/client-cert.pem"
DATABASE_SSL_KEY: "/path/to/client-key.pem"
DATABASE_SSL_ROOT_CERT: "/path/to/ca-cert.pem"

# Connection encryption
DATABASE_URL: "postgresql+asyncpg://user:pass@host:5432/db?ssl=require"
```

## Scaling Strategy

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gateway-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Service-Specific Scaling

- **Gateway**: Scale based on request volume
- **Orchestrator**: Scale based on active workflows
- **RAG Service**: Scale based on document processing queue
- **Tools Service**: Scale based on tool execution requests
- **Observability**: Scale based on telemetry data volume

## Troubleshooting

### Common Issues

1. **Service Not Starting**:
   ```bash
   # Check pod logs
   kubectl logs <pod-name> -n lcnc-platform
   
   # Check resource constraints
   kubectl describe pod <pod-name> -n lcnc-platform
   ```

2. **Database Connection Issues**:
   ```bash
   # Test database connectivity
   kubectl exec -it <pod-name> -n lcnc-platform -- python -c "
   import asyncpg
   import asyncio
   async def test_db():
       conn = await asyncpg.connect('postgresql://...')
       result = await conn.fetchval('SELECT 1')
       print(f'DB Test: {result}')
       await conn.close()
   asyncio.run(test_db())
   "
   ```

3. **Performance Issues**:
   ```bash
   # Check resource usage
   kubectl top pods -n lcnc-platform
   
   # Check service metrics
   curl http://<service-url>/metrics
   ```

### Service Health Debugging

```bash
# Health check all services
services=("gateway" "orchestrator" "agents" "tools" "rag" "sqltool" "workflow" "observability")
for service in "${services[@]}"; do
  echo "Checking $service health..."
  curl -f http://<ingress-url>/api/$service/health || echo "$service is unhealthy"
done
```

## Conclusion

This document provides a comprehensive overview of the deployment strategies for the Agentic AI Acceleration. By following the outlined steps, developers can successfully deploy the platform in both local and production environments. For further details, refer to the individual service documentation and API specifications.