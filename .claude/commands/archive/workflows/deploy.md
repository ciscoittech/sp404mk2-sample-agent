# /deploy Command - Production Deployment

Deploy the SP404MK2 Sample Agent to production with quality gates and validation.

## Usage
```
/deploy
/deploy "staging"
/deploy "production"
```

## Workflow

### Stage 1: Pre-Deployment Validation

```markdown
**Senior Engineer** - Run pre-deployment checks
- Prompt: "Run pre-deployment validation checks:
  1. All tests pass (pytest + playwright)
  2. No security vulnerabilities
  3. Database migrations ready
  4. Environment variables configured
  5. Dependencies up to date
  6. No hardcoded secrets
  Report any issues that would block deployment."
- Tools: Bash, Read, Grep
- Output: Validation report
```

#### Validation Checks
```bash
# 1. Run all tests
pytest backend/tests/ -v
cd frontend && npm run test:e2e

# 2. Check for secrets
grep -r "API_KEY\s*=\s*['\"]" backend/
grep -r "PASSWORD\s*=\s*['\"]" backend/

# 3. Check dependencies
pip list --outdated
cd frontend && npm outdated

# 4. Validate migrations
cd backend && alembic check

# 5. Check environment variables
python -c "from app.core.config import settings; print(settings.model_dump())"
```

### Stage 2: Build & Package

```markdown
**Senior Engineer** - Build deployment package
- Prompt: "Build the deployment package:
  1. Install production dependencies
  2. Build frontend assets (if applicable)
  3. Run database migrations
  4. Create deployment artifact
  Report build status and any issues."
- Tools: Bash
- Output: Deployment package
```

#### Build Steps
```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head

# Frontend (if applicable)
cd frontend
npm ci --production
npm run build

# Docker (if using containers)
docker-compose build
```

### Stage 3: Environment-Specific Configuration

#### Staging Deployment
```markdown
**Senior Engineer** - Deploy to staging
- Prompt: "Deploy to staging environment:
  1. Configure staging environment variables
  2. Start services in staging
  3. Run smoke tests
  4. Verify deployment health
  Report deployment status."
- Tools: Bash
- Output: Staging deployment status
```

```bash
# Configure staging
export ENV=staging
export DATABASE_URL="sqlite+aiosqlite:///./sp404_samples_staging.db"
export OPENROUTER_API_KEY="${STAGING_OPENROUTER_KEY}"

# Deploy
./venv/bin/python backend/run.py &

# Smoke tests
curl http://localhost:8100/health
curl http://localhost:8100/api/v1/samples
```

#### Production Deployment
```markdown
**Senior Engineer** - Deploy to production
- Prompt: "Deploy to production environment:
  1. Configure production environment variables
  2. Start services with production settings
  3. Run health checks
  4. Verify critical endpoints
  5. Monitor logs for errors
  Report deployment status and any issues."
- Tools: Bash
- Output: Production deployment status
```

```bash
# Configure production
export ENV=production
export DATABASE_URL="${PRODUCTION_DATABASE_URL}"
export OPENROUTER_API_KEY="${PRODUCTION_OPENROUTER_KEY}"

# Deploy
docker-compose up -d

# Health checks
curl http://your-domain.com/health
curl http://your-domain.com/api/v1/samples?limit=1
```

### Stage 4: Post-Deployment Validation

```markdown
**Senior Engineer** - Validate deployment
- Prompt: "Validate the deployment:
  1. Test critical user workflows (upload sample, analyze vibe, export)
  2. Check application logs for errors
  3. Verify database connectivity
  4. Test API endpoints
  5. Check WebSocket connections
  Report validation results."
- Tools: Bash, Read
- Output: Validation report
```

#### Validation Tests
```bash
# Test sample upload
curl -X POST http://localhost:8100/api/v1/samples \
  -F "audio_file=@test.wav" \
  -F "name=Deployment Test"

# Test vibe analysis
curl http://localhost:8100/api/v1/samples/1/analyze

# Check logs
tail -f backend/logs/app.log

# Check database
sqlite3 sp404_samples.db "SELECT COUNT(*) FROM samples;"

# Monitor health
watch -n 5 "curl -s http://localhost:8100/health"
```

### Stage 5: Rollback Plan (if issues detected)

```markdown
**Senior Engineer** - Execute rollback
- Prompt: "Rollback deployment due to: {issue_description}.
  1. Stop current services
  2. Revert to previous version
  3. Restore database if needed
  4. Restart services
  5. Verify rollback successful
  Report rollback status."
- Tools: Bash
- Output: Rollback status
```

```bash
# Docker rollback
docker-compose down
git checkout previous-tag
docker-compose up -d

# Database rollback (if needed)
cd backend && alembic downgrade -1

# Verify
curl http://localhost:8100/health
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (backend + E2E)
- [ ] No security vulnerabilities
- [ ] Environment variables configured
- [ ] Database migrations ready and tested
- [ ] Dependencies up to date
- [ ] No hardcoded secrets in code
- [ ] API rate limits configured
- [ ] Backup of production database taken

### During Deployment
- [ ] Services stopped gracefully
- [ ] Database migrations applied successfully
- [ ] New code deployed
- [ ] Services started successfully
- [ ] Health checks pass
- [ ] No errors in logs

### Post-Deployment
- [ ] Critical workflows tested
- [ ] API endpoints responding correctly
- [ ] WebSocket connections working
- [ ] Database queries successful
- [ ] No performance degradation
- [ ] Monitoring alerts configured
- [ ] Team notified of deployment

## Environment Configuration

### Required Environment Variables
```bash
# Application
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite+aiosqlite:///./sp404_samples.db

# OpenRouter API
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# File Upload
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=104857600  # 100MB

# SP-404MK2 Export
SP404_EXPORT_DIR=/app/exports
SP404_SAMPLE_RATE=48000
SP404_BIT_DEPTH=16
```

### Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8100:8100"
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./uploads:/app/uploads
      - ./exports:/app/exports
      - ./sp404_samples.db:/app/sp404_samples.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8100/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Monitoring & Alerts

### Health Endpoint
```python
@app.get("/health")
async def health_check():
    """Application health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Log Monitoring
```bash
# Check for errors
tail -f backend/logs/app.log | grep ERROR

# Monitor API usage
tail -f backend/logs/app.log | grep "API usage"

# Watch request patterns
tail -f backend/logs/app.log | grep "POST\|GET\|DELETE"
```

### Performance Monitoring
```bash
# Database size
ls -lh sp404_samples.db

# API response times (from logs)
grep "Request completed" backend/logs/app.log | tail -20

# Memory usage
docker stats sp404mk2-backend
```

## Rollback Procedures

### Quick Rollback (Docker)
```bash
# Stop current version
docker-compose down

# Revert to previous tag
git checkout v1.0.0

# Rebuild and start
docker-compose up -d

# Verify health
curl http://localhost:8100/health
```

### Database Rollback
```bash
# Downgrade one migration
cd backend && alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Restore from backup
cp sp404_samples.db.backup sp404_samples.db
```

## Success Criteria
- All pre-deployment checks passed
- Services deployed successfully
- Health checks passing
- Critical workflows tested and working
- No errors in logs
- Monitoring configured
- Rollback plan documented and tested
- Team notified of successful deployment
