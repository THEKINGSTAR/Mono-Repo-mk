# CambioML Computer Use Agent Backend - Deployment Guide

Complete guide for deploying the CambioML Computer Use Agent Backend to production environments.

## 🎯 Overview

This guide covers deployment strategies for various environments:
- Docker Compose (Single Server)
- Kubernetes (Container Orchestration)
- Cloud Platforms (AWS ECS, Google Cloud Run, Azure Container Instances)
- CI/CD Pipeline Setup

## 🐳 Docker Compose Deployment

### Single Server Deployment

1. **Server Requirements**
   - Ubuntu 20.04+ or CentOS 8+
   - 4+ CPU cores
   - 8GB+ RAM
   - 50GB+ storage
   - Docker and Docker Compose installed

2. **Setup Production Environment**
   \`\`\`bash
   # Clone repository
   git clone <your-repo-url>
   cd cambioml-backend
   
   # Set up environment
   ./scripts/setup_env.sh
   # Edit .env with production values
   
   # Install Docker (if needed)
   ./scripts/docker_setup.sh
   \`\`\`

3. **Production Configuration**
   \`\`\`bash
   # Use production compose file
   docker-compose -f docker-compose.prod.yml up -d
   
   # Or use the management script
   ./scripts/docker_commands.sh start
   \`\`\`

4. **SSL/TLS Setup**
   \`\`\`bash
   # Generate SSL certificates (Let's Encrypt)
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   
   # Copy certificates
   sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
   sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
   \`\`\`

### Load Balancer Configuration

\`\`\`nginx
# /etc/nginx/sites-available/cambioml
upstream cambioml_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;  # If running multiple instances
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/ssl/fullchain.pem;
    ssl_certificate_key /path/to/ssl/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=websocket:10m rate=5r/s;
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://cambioml_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws/ {
        limit_req zone=websocket burst=10 nodelay;
        proxy_pass http://cambioml_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
    
    location / {
        proxy_pass http://cambioml_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
\`\`\`

## ☸️ Kubernetes Deployment

### Kubernetes Manifests

\`\`\`yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cambioml
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cambioml-config
  namespace: cambioml
data:
  DATABASE_URL: "postgresql://cambioml:password@postgres:5432/cambioml"
  REDIS_URL: "redis://redis:6379"
  DEBUG: "false"
  LOG_LEVEL: "info"
---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cambioml-secrets
  namespace: cambioml
type: Opaque
data:
  ANTHROPIC_API_KEY: <base64-encoded-api-key>
  POSTGRES_PASSWORD: <base64-encoded-password>
---
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: cambioml
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: cambioml
        - name: POSTGRES_USER
          value: cambioml
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cambioml-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: cambioml
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: cambioml
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: cambioml
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cambioml-backend
  namespace: cambioml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cambioml-backend
  template:
    metadata:
      labels:
        app: cambioml-backend
    spec:
      containers:
      - name: backend
        image: cambioml-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: cambioml-secrets
              key: ANTHROPIC_API_KEY
        envFrom:
        - configMapRef:
            name: cambioml-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cambioml-backend
  namespace: cambioml
spec:
  selector:
    app: cambioml-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cambioml-ingress
  namespace: cambioml
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/websocket-services: cambioml-backend
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: cambioml-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cambioml-backend
            port:
              number: 80
\`\`\`

### Kubernetes Deployment Commands

\`\`\`bash
# Create namespace and deploy
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n cambioml

# View logs
kubectl logs -f deployment/cambioml-backend -n cambioml

# Scale deployment
kubectl scale deployment cambioml-backend --replicas=5 -n cambioml

# Update deployment
kubectl set image deployment/cambioml-backend backend=cambioml-backend:v2 -n cambioml
\`\`\`

## ☁️ Cloud Platform Deployments

### AWS ECS Deployment

\`\`\`json
{
  "family": "cambioml-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "cambioml-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/cambioml-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/cambioml"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://elasticache-endpoint:6379"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:cambioml/api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cambioml-backend",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
\`\`\`

### Google Cloud Run Deployment

\`\`\`yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: cambioml-backend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/execution-environment: gen2
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/cambioml-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@cloud-sql-proxy:5432/cambioml"
        - name: REDIS_URL
          value: "redis://memorystore-ip:6379"
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: cambioml-secrets
              key: api-key
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
          requests:
            cpu: "1"
            memory: "1Gi"
\`\`\`

\`\`\`bash
# Deploy to Cloud Run
gcloud run services replace cloud-run.yaml --region=us-central1
\`\`\`

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

\`\`\`yaml
# .github/workflows/deploy.yml
name: Deploy CambioML Backend

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security check
      run: |
        chmod +x scripts/security_check.sh
        ./scripts/security_check.sh

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile.prod
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        # e.g., kubectl, docker-compose, cloud CLI commands
        echo "Deploying to production..."
\`\`\`

## 📊 Monitoring and Observability

### Prometheus Metrics

\`\`\`python
# Add to app/main.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
\`\`\`

### Grafana Dashboard

\`\`\`json
{
  "dashboard": {
    "title": "CambioML Backend Metrics",
    "panels": [
      {
        "title": "Active Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(active_sessions_total)"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
\`\`\`

### Health Checks

\`\`\`python
# Add to app/main.py
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check Redis
        redis_client.ping()
        
        # Check Docker
        docker_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "up",
                "redis": "up",
                "docker": "up"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")
\`\`\`

## 💾 Backup and Recovery

### Database Backup

\`\`\`bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="cambioml"

# Create backup
docker-compose exec postgres pg_dump -U cambioml $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
\`\`\`

### Automated Backup with Cron

\`\`\`bash
# Add to crontab
0 2 * * * /path/to/backup_db.sh >> /var/log/backup.log 2>&1
\`\`\`

### Disaster Recovery

\`\`\`bash
#!/bin/bash
# restore_db.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop application
docker-compose stop backend

# Restore database
gunzip -c $BACKUP_FILE | docker-compose exec -T postgres psql -U cambioml -d cambioml

# Start application
docker-compose start backend

echo "Database restored from $BACKUP_FILE"
\`\`\`

## 🔒 Security Hardening

### Container Security

\`\`\`dockerfile
# Use non-root user
FROM python:3.11-slim
RUN groupadd -r cambioml && useradd -r -g cambioml cambioml
USER cambioml

# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Read-only filesystem
VOLUME ["/tmp"]
\`\`\`

### Network Security

\`\`\`yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    networks:
      - internal
      - external
  
  postgres:
    networks:
      - internal
  
  redis:
    networks:
      - internal

networks:
  internal:
    driver: bridge
    internal: true
  external:
    driver: bridge
\`\`\`

### Secrets Management

\`\`\`bash
# Using Docker Secrets
echo "your_api_key" | docker secret create anthropic_api_key -

# In docker-compose.yml
services:
  backend:
    secrets:
      - anthropic_api_key
    environment:
      - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_api_key

secrets:
  anthropic_api_key:
    external: true
\`\`\`

## 📈 Performance Tuning

### Database Optimization

\`\`\`sql
-- PostgreSQL configuration
-- postgresql.conf

shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
\`\`\`

### Application Optimization

\`\`\`python
# app/main.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # CPU cores
        loop="uvloop",  # Faster event loop
        http="httptools",  # Faster HTTP parser
        access_log=False,  # Disable in production
        server_header=False,  # Security
    )
\`\`\`

### Load Balancing

\`\`\`nginx
upstream cambioml_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://cambioml_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://cambioml_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
\`\`\`

## 🐛 Troubleshooting Production Issues

### Common Production Problems

1. **High Memory Usage**
   \`\`\`bash
   # Monitor memory usage
   docker stats
   
   # Check for memory leaks
   docker-compose exec backend python -c "
   import psutil
   process = psutil.Process()
   print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
   "
   \`\`\`

2. **Database Connection Pool Exhaustion**
   \`\`\`python
   # Increase pool size in database.py
   engine = create_engine(
       DATABASE_URL,
       pool_size=30,
       max_overflow=50,
       pool_timeout=60
   )
   \`\`\`

3. **WebSocket Connection Issues**
   \`\`\`bash
   # Check WebSocket connections
   netstat -an | grep :8000
   
   # Monitor WebSocket metrics
   curl http://localhost:8000/metrics | grep websocket
   \`\`\`

### Log Analysis

\`\`\`bash
# Centralized logging with ELK stack
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  elasticsearch:7.14.0

docker run -d \
  --name kibana \
  -p 5601:5601 \
  --link elasticsearch:elasticsearch \
  kibana:7.14.0

# Configure Filebeat for log shipping
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
\`\`\`

This comprehensive deployment guide covers all aspects of taking the CambioML Computer Use Agent Backend from development to production, including security, monitoring, and troubleshooting considerations.
