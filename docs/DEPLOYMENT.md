# 🚢 OllamaStack Deployment Guide

This guide covers various deployment options for OllamaStack, from development to production environments.

## Table of Contents

- [Quick Start Deployment](#quick-start-deployment)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Security Configuration](#security-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)

## Quick Start Deployment

### Using Docker Compose (Recommended)

The fastest way to deploy OllamaStack is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/saki007ster/ollamastack.git
cd ollamastack

# Copy environment template
cp backend/env.example backend/.env

# Start all services
docker-compose up --build -d

# Pull a model
docker exec ollamastack-ollama-1 ollama pull llama3.2

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Next.js application |
| Backend | 8000 | FastAPI server |
| Ollama | 11434 | LLM inference server |

## Local Development

### Prerequisites

- **Node.js** 20+ and **npm**
- **Python** 3.11+
- **Docker** and **Docker Compose**
- **Git**

### Development Setup

```bash
# Install dependencies
npm run install:all

# Start services separately
npm run dev:frontend  # Port 3000
npm run dev:backend   # Port 8000

# Or use Docker for dependencies only
docker-compose up ollama -d
```

### Environment Configuration

Create `backend/.env` file:

```env
# Development settings
DEBUG=true
RELOAD=true
LOG_LEVEL=DEBUG

# Server settings
HOST=0.0.0.0
PORT=8000

# CORS settings (allow frontend)
CORS_ORIGINS=["http://localhost:3000"]

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# LangChain settings
LANGCHAIN_VERBOSE=true
```

### Development Workflow

```bash
# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format

# Check types
npm run type-check

# View logs
docker-compose logs -f
```

## Production Deployment

### Production Docker Compose

Use the production configuration:

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d --build

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Production Environment Variables

Create `backend/.env` for production:

```env
# Production settings
DEBUG=false
RELOAD=false
LOG_LEVEL=INFO

# Server settings
HOST=0.0.0.0
PORT=8000

# CORS settings (your domain)
CORS_ORIGINS=["https://yourdomain.com"]

# Ollama settings
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2

# Security settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@db:5432/ollamastack

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    
    upstream backend {
        server backend:8000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=frontend:10m rate=20r/s;
    
    server {
        listen 80;
        server_name yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # Frontend
        location / {
            limit_req zone=frontend burst=20 nodelay;
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API
        location /api/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout settings for long LLM responses
            proxy_read_timeout 300s;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
        }
        
        # Static files
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### Health Checks

Configure health checks for each service:

```yaml
# docker-compose.prod.yml
services:
  frontend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  backend:
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  ollama:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

Create `ecs-task-definition.json`:

```json
{
  "family": "ollamastack",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ollamastack-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NEXT_PUBLIC_API_URL",
          "value": "https://api.yourdomain.com"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ollamastack",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "frontend"
        }
      }
    },
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ollamastack-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@db.region.rds.amazonaws.com:5432/ollamastack"
        }
      ]
    }
  ]
}
```

#### Deploy with Terraform

Create `main.tf`:

```hcl
provider "aws" {
  region = "us-west-2"
}

# VPC and networking
resource "aws_vpc" "ollamastack" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "ollamastack-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "ollamastack" {
  name = "ollamastack"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Load Balancer
resource "aws_lb" "ollamastack" {
  name               = "ollamastack-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.public[*].id
  
  enable_deletion_protection = true
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.ollamastack.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}
```

### Google Cloud Deployment

#### Using Google Cloud Run

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/ollamastack-frontend frontend/
gcloud builds submit --tag gcr.io/PROJECT_ID/ollamastack-backend backend/

# Deploy services
gcloud run deploy ollamastack-frontend \
  --image gcr.io/PROJECT_ID/ollamastack-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1

gcloud run deploy ollamastack-backend \
  --image gcr.io/PROJECT_ID/ollamastack-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

#### Cloud Build Configuration

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ollamastack-frontend', 'frontend/']
  
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ollamastack-backend', 'backend/']
  
  # Push images
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ollamastack-frontend']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ollamastack-backend']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'ollamastack-frontend',
           '--image', 'gcr.io/$PROJECT_ID/ollamastack-frontend',
           '--platform', 'managed', '--region', 'us-central1']

images:
  - 'gcr.io/$PROJECT_ID/ollamastack-frontend'
  - 'gcr.io/$PROJECT_ID/ollamastack-backend'
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name ollamastack-rg --location eastus

# Create container group
az container create \
  --resource-group ollamastack-rg \
  --name ollamastack \
  --image your-registry/ollamastack:latest \
  --cpu 2 \
  --memory 4 \
  --restart-policy Always \
  --ports 3000 8000 \
  --environment-variables \
    NODE_ENV=production \
    DATABASE_URL=$DATABASE_URL
```

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ollamastack

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ollamastack-config
  namespace: ollamastack
data:
  OLLAMA_BASE_URL: "http://ollama:11434"
  CORS_ORIGINS: '["https://yourdomain.com"]'
  LOG_LEVEL: "INFO"
```

### Deployments

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ollamastack
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: ollamastack/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.yourdomain.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ollamastack
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ollamastack/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: ollamastack-config
        - secretRef:
            name: ollamastack-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
# ollama-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: ollamastack
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc
```

### Services and Ingress

```yaml
# services.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: ollamastack
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: ollamastack
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: ollama
  namespace: ollamastack
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ollamastack-ingress
  namespace: ollamastack
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - api.yourdomain.com
    secretName: ollamastack-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

### Persistent Storage

```yaml
# storage.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-pvc
  namespace: ollamastack
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd
```

### Secrets Management

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ollamastack-secrets
  namespace: ollamastack
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  SECRET_KEY: <base64-encoded-secret-key>
  OPENAI_API_KEY: <base64-encoded-openai-key>
```

### Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: ollamastack
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
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

## Security Configuration

### SSL/TLS Setup

#### Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Environment Security

```bash
# Use secrets management
export DATABASE_URL=$(aws ssm get-parameter --name "/ollamastack/database-url" --with-decryption --query "Parameter.Value" --output text)
export SECRET_KEY=$(aws ssm get-parameter --name "/ollamastack/secret-key" --with-decryption --query "Parameter.Value" --output text)

# Restrict file permissions
chmod 600 backend/.env
chown app:app backend/.env
```

### Firewall Configuration

```bash
# UFW firewall rules
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct backend access
sudo ufw deny 11434/tcp # Block direct Ollama access
sudo ufw enable
```

## Monitoring & Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
- job_name: 'ollamastack-backend'
  static_configs:
  - targets: ['backend:8000']
  metrics_path: '/metrics'

- job_name: 'ollama'
  static_configs:
  - targets: ['ollama:11434']
  metrics_path: '/metrics'
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "OllamaStack Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Centralized Logging

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.8.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
```

## Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="ollamastack"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Compress
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### Disaster Recovery Plan

1. **Data Recovery**
   ```bash
   # Restore from backup
   gunzip backup_20240101_120000.sql.gz
   psql $DATABASE_URL < backup_20240101_120000.sql
   ```

2. **Service Recovery**
   ```bash
   # Quick rollback
   docker-compose down
   git checkout last-known-good-commit
   docker-compose up --build -d
   ```

3. **Model Recovery**
   ```bash
   # Re-pull models
   docker exec ollama ollama pull llama3.2
   docker exec ollama ollama pull codellama
   ```

### Automated Backup

```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
  namespace: ollamastack
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL > /backup/backup_$(date +%Y%m%d_%H%M%S).sql
              aws s3 cp /backup/backup_*.sql s3://your-backup-bucket/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: ollamastack-secrets
                  key: DATABASE_URL
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            emptyDir: {}
          restartPolicy: OnFailure
```

---

This deployment guide provides comprehensive coverage for deploying OllamaStack in various environments. Choose the deployment method that best fits your infrastructure requirements and scale. 