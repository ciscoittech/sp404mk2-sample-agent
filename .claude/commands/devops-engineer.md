# DevOps Engineer Specialist

**Command**: `/devops-engineer`

DevOps specialist for CI/CD pipelines, infrastructure as code, monitoring, and deployment strategies for the SP404MK2 system.

## Expertise Areas

### CI/CD Pipeline
- **GitHub Actions**: Automated workflows, matrix builds
- **Testing Pipeline**: Unit, integration, E2E automation
- **Code Quality**: Linting, formatting, security scanning
- **Release Management**: Semantic versioning, changelogs

### Infrastructure as Code
- **Docker**: Containerization, multi-stage builds
- **Docker Compose**: Local development environment
- **Terraform**: Cloud resource provisioning
- **Kubernetes**: Container orchestration (when needed)

### Monitoring & Observability
- **Logging**: Structured logging, log aggregation
- **Metrics**: Prometheus, Grafana dashboards
- **Tracing**: Distributed tracing, performance
- **Alerts**: PagerDuty, Slack notifications

### Security & Compliance
- **Secret Management**: Vault, environment variables
- **Security Scanning**: Dependency vulnerabilities
- **Access Control**: IAM policies, RBAC
- **Audit Logging**: Compliance tracking

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "20"

jobs:
  # Python Backend Tests
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          
      - name: Run linting
        run: |
          ruff check .
          black --check .
          mypy src/
          
      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=html \
            --cov-fail-under=80
            
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  # Frontend Tests
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Type checking
        run: npm run typecheck
        
      - name: Linting
        run: npm run lint
        
      - name: Unit tests
        run: npm run test:unit
        
      - name: Build
        run: npm run build

  # E2E Tests
  e2e-tests:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          
      - name: Install Playwright
        run: |
          npm ci
          npx playwright install --with-deps
          
      - name: Run E2E tests
        run: |
          docker-compose up -d
          npm run test:e2e
        env:
          BASE_URL: http://localhost:3000
          
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-results
          path: test-results/

  # Security Scanning
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # Build and Push Docker Images
  docker-build:
    needs: [backend-tests, frontend-tests, e2e-tests]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: |
            sp404/backend:latest
            sp404/backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: |
            sp404/frontend:latest
            sp404/frontend:${{ github.sha }}
          build-args: |
            API_URL=${{ secrets.PRODUCTION_API_URL }}

  # Deploy to Production
  deploy:
    needs: [docker-build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Deploy using your preferred method
          echo "Deploying to production..."
```

### Docker Configuration

#### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

# Environment
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:20-alpine

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nuxtjs -u 1001

WORKDIR /app

COPY --from=builder --chown=nuxtjs:nodejs /app/.output ./.output
COPY --from=builder --chown=nuxtjs:nodejs /app/package.json ./

USER nuxtjs

EXPOSE 3000

ENV HOST=0.0.0.0
ENV PORT=3000

CMD ["node", ".output/server/index.mjs"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NUXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - sp404-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - redis
      - db
    volumes:
      - ./uploads:/app/uploads
    networks:
      - sp404-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=sp404
      - POSTGRES_USER=sp404user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - sp404-network

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    networks:
      - sp404-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - sp404-network

volumes:
  db_data:

networks:
  sp404-network:
    driver: bridge
```

### Monitoring Setup

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "SP404 Sample Agent Monitoring",
    "panels": [
      {
        "title": "API Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Sample Processing Queue",
        "targets": [
          {
            "expr": "sp404_processing_queue_size"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

### Infrastructure as Code

#### Terraform Configuration
```hcl
# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# S3 bucket for sample storage
resource "aws_s3_bucket" "samples" {
  bucket = "sp404-samples-${var.environment}"
  
  lifecycle_rule {
    enabled = true
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "app" {
  enabled             = true
  default_root_object = "index.html"
  
  origin {
    domain_name = aws_s3_bucket.app.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.app.id}"
  }
  
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.app.id}"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
  }
}
```

### Deployment Scripts

#### Rolling Update Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=$1
VERSION=$2

echo "Deploying version $VERSION to $ENVIRONMENT"

# Run database migrations
echo "Running database migrations..."
kubectl exec -it deploy/backend -- alembic upgrade head

# Update backend
echo "Updating backend..."
kubectl set image deployment/backend \
  backend=sp404/backend:$VERSION \
  --record

# Wait for rollout
kubectl rollout status deployment/backend

# Update frontend
echo "Updating frontend..."
kubectl set image deployment/frontend \
  frontend=sp404/frontend:$VERSION \
  --record

# Wait for rollout
kubectl rollout status deployment/frontend

# Run smoke tests
echo "Running smoke tests..."
./scripts/smoke-tests.sh $ENVIRONMENT

echo "Deployment complete!"
```

### Security Best Practices

#### Secret Management
```yaml
# .github/workflows/secrets.yml
- name: Setup secrets
  run: |
    # Create .env file from GitHub secrets
    cat > .env << EOF
    DATABASE_URL=${{ secrets.DATABASE_URL }}
    OPENROUTER_API_KEY=${{ secrets.OPENROUTER_API_KEY }}
    REDIS_URL=${{ secrets.REDIS_URL }}
    EOF
    
    # Encrypt for production
    openssl enc -aes-256-cbc -salt -in .env -out .env.enc -k ${{ secrets.ENCRYPTION_KEY }}
```

#### Security Scanning
```yaml
# security-scan.yml
- name: Dependency check
  run: |
    # Python dependencies
    pip-audit --desc
    
    # JavaScript dependencies
    npm audit --audit-level=moderate
    
    # Docker image scanning
    trivy image sp404/backend:latest
```

### Backup & Disaster Recovery

#### Automated Backups
```bash
#!/bin/bash
# scripts/backup.sh

# Database backup
pg_dump $DATABASE_URL | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Upload to S3
aws s3 cp backup-*.sql.gz s3://sp404-backups/db/

# Sample files backup
aws s3 sync /app/uploads s3://sp404-backups/uploads/

# Clean old backups (keep 30 days)
find . -name "backup-*.sql.gz" -mtime +30 -delete
```

## Integration Points

### With Backend Developer
- API endpoint monitoring
- Log format standards
- Performance metrics
- Deployment hooks

### With Frontend Developer
- Build optimization
- CDN configuration
- Environment variables
- Error tracking

### With Database Engineer
- Backup strategies
- Migration automation
- Performance monitoring
- Replica configuration

## Success Metrics

- Deployment frequency: Daily
- Lead time: < 30 minutes
- MTTR: < 15 minutes
- Change failure rate: < 5%
- Uptime: 99.9%
- Build time: < 5 minutes