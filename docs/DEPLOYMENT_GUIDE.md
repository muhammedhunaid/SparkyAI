# SparkyAI Deployment Guide

## Overview
This guide covers deployment options for SparkyAI, from development environments to production setups.

## Deployment Options

### 1. Local Development Deployment

#### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Chrome/Chromium browser
- Git

#### Setup Steps
```bash
# Clone repository
git clone https://github.com/ashworks1706/SparkyAI.git
cd SparkyAI

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start supporting services
docker-compose up -d

# Configure environment
cp config/__sample__appConfig.json config/appConfig.json
cp config/sample__firebase_secret.json config/firebase_secret.json
```

#### Configuration
Update `config/appConfig.json` with your credentials:
```json
{
  "gemini_api_key": "your_gemini_api_key",
  "discord_bot_token": "your_discord_bot_token",
  "discord_target_guild_id": "your_guild_id",
  "qdrant": {
    "host": "localhost",
    "port": 6333,
    "collection_name": "sparky_ai_docs"
  },
  "firebase": {
    "credentials_path": "config/firebase_secret.json"
  }
}
```

#### Running the Application
```bash
# Terminal 1: Start main application
python main.py

# Terminal 2: Start Discord bot
python discord_bot.py

# Terminal 3: Background data collection (optional)
python background_fetch.py
```

### 2. Docker Deployment

#### Using Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  sparky-ai:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/config/firebase_secret.json
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - qdrant
      - chrome

  discord-bot:
    build: .
    command: python discord_bot.py
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - GOOGLE_APPLICATION_CREDENTIALS=/app/config/firebase_secret.json
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - qdrant
      - chrome

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

  chrome:
    image: selenium/standalone-chrome:latest
    ports:
      - "4444:4444"
    shm_size: 2gb

volumes:
  qdrant_storage:
```

#### Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]
```

#### Build and Deploy
```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f sparky-ai
docker-compose logs -f discord-bot

# Scale services if needed
docker-compose up --scale discord-bot=2 -d
```

### 3. Cloud Deployment

#### Google Cloud Platform

##### App Engine Deployment
Create `app.yaml`:
```yaml
runtime: python39

env_variables:
  GEMINI_API_KEY: "your_api_key"
  DISCORD_BOT_TOKEN: "your_bot_token"
  GOOGLE_APPLICATION_CREDENTIALS: "config/firebase_secret.json"

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

resources:
  cpu: 2
  memory_gb: 4
  disk_size_gb: 10
```

Deploy:
```bash
# Install Google Cloud SDK
# Configure authentication
gcloud auth login
gcloud config set project your-project-id

# Deploy main application
gcloud app deploy app.yaml

# Deploy Discord bot as separate service
gcloud app deploy discord-bot.yaml
```

##### Cloud Run Deployment
```bash
# Build container
docker build -t gcr.io/your-project/sparky-ai .

# Push to Container Registry
docker push gcr.io/your-project/sparky-ai

# Deploy to Cloud Run
gcloud run deploy sparky-ai \
  --image gcr.io/your-project/sparky-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
```

#### AWS Deployment

##### Elastic Container Service (ECS)
Create `task-definition.json`:
```json
{
  "family": "sparky-ai",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "sparky-ai",
      "image": "your-account.dkr.ecr.region.amazonaws.com/sparky-ai:latest",
      "environment": [
        {"name": "GEMINI_API_KEY", "value": "your_api_key"},
        {"name": "DISCORD_BOT_TOKEN", "value": "your_bot_token"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/sparky-ai",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Deploy:
```bash
# Create ECR repository
aws ecr create-repository --repository-name sparky-ai

# Build and push image
docker build -t sparky-ai .
docker tag sparky-ai:latest your-account.dkr.ecr.region.amazonaws.com/sparky-ai:latest
docker push your-account.dkr.ecr.region.amazonaws.com/sparky-ai:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster your-cluster \
  --service-name sparky-ai \
  --task-definition sparky-ai:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

##### Lambda Deployment (Serverless)
For lightweight operations, deploy specific agents as Lambda functions:

```python
# lambda_handler.py
import json
import asyncio
from agents.courses_agent import CoursesModel

def lambda_handler(event, context):
    """AWS Lambda handler for courses agent"""
    query = event.get('query', '')
    
    # Initialize agent (with minimal dependencies)
    agent = CoursesModel(...)
    
    # Process query
    response = asyncio.run(agent.determine_action(query, ""))
    
    return {
        'statusCode': 200,
        'body': json.dumps({'response': response})
    }
```

#### Azure Deployment

##### Container Instances
```bash
# Create resource group
az group create --name sparky-ai-rg --location eastus

# Create container instance
az container create \
  --resource-group sparky-ai-rg \
  --name sparky-ai \
  --image your-registry.azurecr.io/sparky-ai:latest \
  --cpu 2 \
  --memory 4 \
  --environment-variables GEMINI_API_KEY=$GEMINI_API_KEY DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN \
  --ports 8080
```

### 4. Kubernetes Deployment

#### Kubernetes Manifests
Create deployment manifests:

```yaml
# sparky-ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sparky-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sparky-ai
  template:
    metadata:
      labels:
        app: sparky-ai
    spec:
      containers:
      - name: sparky-ai
        image: sparky-ai:latest
        ports:
        - containerPort: 8080
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: sparky-ai-secrets
              key: gemini-api-key
        - name: DISCORD_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: sparky-ai-secrets
              key: discord-bot-token
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: sparky-ai-service
spec:
  selector:
    app: sparky-ai
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

```yaml
# qdrant-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
spec:
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
spec:
  selector:
    app: qdrant
  ports:
    - protocol: TCP
      port: 6333
      targetPort: 6333
  type: ClusterIP
```

#### Deploy to Kubernetes
```bash
# Create secrets
kubectl create secret generic sparky-ai-secrets \
  --from-literal=gemini-api-key=$GEMINI_API_KEY \
  --from-literal=discord-bot-token=$DISCORD_BOT_TOKEN

# Create persistent volume claim for Qdrant
kubectl apply -f qdrant-pvc.yaml

# Deploy applications
kubectl apply -f qdrant-deployment.yaml
kubectl apply -f sparky-ai-deployment.yaml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/sparky-ai
```

## Environment-Specific Configurations

### Development Environment
```json
{
  "environment": "development",
  "debug": true,
  "log_level": "DEBUG",
  "selenium_headless": false,
  "qdrant": {
    "host": "localhost",
    "port": 6333
  }
}
```

### Staging Environment
```json
{
  "environment": "staging",
  "debug": false,
  "log_level": "INFO",
  "selenium_headless": true,
  "qdrant": {
    "host": "qdrant-staging.internal",
    "port": 6333
  }
}
```

### Production Environment
```json
{
  "environment": "production",
  "debug": false,
  "log_level": "WARNING",
  "selenium_headless": true,
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 60
  },
  "monitoring": {
    "enabled": true,
    "metrics_endpoint": "/metrics"
  }
}
```

## Monitoring and Observability

### Logging Configuration
```python
import logging
import structlog
from pythonjsonlogger import jsonlogger

# Configure structured logging for production
def setup_logging(environment: str):
    if environment == "production":
        # JSON logging for production
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    else:
        # Human-readable logging for development
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
```

### Health Checks
Add health check endpoints:
```python
# health_check.py
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "sparky-ai"}

@app.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check - verify dependencies"""
    try:
        # Check database connection
        await verify_database_connection()
        
        # Check vector store connection
        await verify_vector_store_connection()
        
        # Check AI service connection
        await verify_ai_service_connection()
        
        return {"status": "ready", "service": "sparky-ai"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}

@app.get("/metrics")
async def metrics() -> Dict[str, any]:
    """Prometheus-compatible metrics endpoint"""
    return {
        "queries_processed_total": get_query_count(),
        "active_sessions": get_active_session_count(),
        "response_time_seconds": get_average_response_time(),
        "error_rate": get_error_rate()
    }
```

### Monitoring with Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sparky-ai'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Alerting with Grafana
Create dashboards and alerts for:
- Response time degradation
- Error rate increases
- Memory/CPU usage spikes
- Database connection issues
- Vector store performance

## Security Considerations

### Secrets Management
```bash
# Use environment-specific secret managers
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id sparky-ai/prod/api-keys

# Azure Key Vault
az keyvault secret show --vault-name sparky-ai-vault --name discord-bot-token

# Google Secret Manager
gcloud secrets versions access latest --secret="gemini-api-key"
```

### Network Security
```yaml
# Network policies for Kubernetes
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sparky-ai-netpol
spec:
  podSelector:
    matchLabels:
      app: sparky-ai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: qdrant
    ports:
    - protocol: TCP
      port: 6333
  - to: []  # Allow outbound internet for API calls
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
```

### SSL/TLS Configuration
```yaml
# Ingress with TLS termination
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sparky-ai-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.sparky-ai.com
    secretName: sparky-ai-tls
  rules:
  - host: api.sparky-ai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sparky-ai-service
            port:
              number: 80
```

## Scaling and Performance

### Horizontal Scaling
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sparky-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sparky-ai
  minReplicas: 3
  maxReplicas: 20
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

### Load Balancing
Configure load balancing strategies:
- Round-robin for general queries
- Session affinity for user-specific operations
- Geographic routing for global deployments

### Caching Strategy
```python
# Redis caching configuration
import redis
import json
from datetime import timedelta

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
    
    async def get_cached_response(self, query_hash: str) -> str:
        """Get cached response for query"""
        cached = self.redis_client.get(query_hash)
        return json.loads(cached) if cached else None
    
    async def cache_response(self, query_hash: str, response: str, ttl: int = 3600):
        """Cache response with TTL"""
        self.redis_client.setex(
            query_hash,
            timedelta(seconds=ttl),
            json.dumps(response)
        )
```

## Backup and Recovery

### Database Backups
```bash
# Firebase/Firestore backup
gcloud firestore export gs://your-backup-bucket/firestore-backups/$(date +%Y-%m-%d)

# Qdrant backup
curl -X POST "http://qdrant:6333/collections/sparky_ai_docs/snapshots"
```

### Disaster Recovery Plan
1. **Data Recovery**: Restore from latest backups
2. **Service Recovery**: Deploy from container registry
3. **Configuration Recovery**: Restore from version control
4. **Monitoring**: Verify all services are operational

## Troubleshooting

### Common Deployment Issues

1. **Container Startup Failures**
   ```bash
   # Check logs
   kubectl logs deployment/sparky-ai
   
   # Debug container
   kubectl exec -it deployment/sparky-ai -- /bin/bash
   ```

2. **Database Connection Issues**
   ```bash
   # Test connectivity
   kubectl exec -it deployment/sparky-ai -- curl -v http://qdrant-service:6333/health
   ```

3. **Memory Issues**
   ```bash
   # Check resource usage
   kubectl top pods
   
   # Increase memory limits
   kubectl patch deployment sparky-ai -p '{"spec":{"template":{"spec":{"containers":[{"name":"sparky-ai","resources":{"limits":{"memory":"8Gi"}}}]}}}}'
   ```

4. **API Rate Limiting**
   - Implement exponential backoff
   - Use multiple API keys with rotation
   - Add circuit breaker patterns

### Performance Tuning
1. **Optimize Docker Images**: Use multi-stage builds, minimal base images
2. **Database Optimization**: Index frequently queried fields
3. **Caching**: Implement multi-level caching strategy
4. **Connection Pooling**: Use connection pools for database connections
5. **Async Processing**: Use async/await patterns throughout the application

This deployment guide covers various deployment scenarios from development to production. Choose the deployment method that best fits your infrastructure requirements and scaling needs.