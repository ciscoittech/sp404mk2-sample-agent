# Docker Deployment Guide

## Overview

The SP404MK2 Sample Agent is packaged as a single Docker image containing:
- FastAPI backend (Python 3.13)
- React 19 frontend (pre-built and served by FastAPI)
- Audio processing libraries (librosa, ffmpeg)
- PostgreSQL database (separate container)

## Quick Start

### Development Mode (with docker-compose)

```bash
# Start all services
docker-compose up -d

# Initialize database (first time only)
docker-compose exec backend python -m app.db.init_db

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Access the application at: http://localhost:8100

### Production Mode

```bash
# Build the image
docker build -t sp404-sample-agent:latest .

# Run with docker-compose
ENVIRONMENT=production docker-compose up -d

# Or run standalone
docker run -d \
  --name sp404-backend \
  -p 8100:8100 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@postgres:5432/sp404_samples" \
  -e OPENROUTER_API_KEY="your-api-key" \
  -e ENVIRONMENT=production \
  -v sp404-downloads:/app/downloads \
  -v sp404-samples:/app/samples \
  sp404-sample-agent:latest
```

## Architecture

### Multi-Stage Build

The Dockerfile uses a 3-stage build process:

1. **Backend Builder Stage** (Python 3.13-slim)
   - Installs build dependencies
   - Compiles Python packages
   - Builds audio processing libraries

2. **Frontend Builder Stage** (Node 20-alpine)
   - Installs npm dependencies
   - Builds React app with Vite
   - Outputs to `dist/` directory

3. **Runtime Stage** (Python 3.13-slim)
   - Copies Python packages from backend builder
   - Copies React dist from frontend builder
   - Configures FastAPI to serve React SPA
   - Minimal runtime dependencies only

### Image Size

- **Builder stages**: ~2GB (discarded after build)
- **Final image**: ~600MB
  - Python 3.13-slim: ~150MB
  - Python packages: ~300MB
  - React build: ~2MB
  - Audio libraries: ~100MB
  - System dependencies: ~50MB

## Configuration

### Environment Variables

#### Required
- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql+asyncpg://user:pass@host:port/database`
  - Example: `postgresql+asyncpg://sp404_user:changeme123@postgres:5432/sp404_samples`

#### Optional
- `OPENROUTER_API_KEY`: API key for AI analysis (optional for basic features)
- `ENVIRONMENT`: `development` or `production` (default: `development`)
- `API_HOST`: Host to bind to (default: `0.0.0.0`)
- `API_PORT`: Port to listen on (default: `8100`)

### Volumes

#### Data Volumes (Persistent Storage)
- `/app/downloads`: Downloaded sample files
- `/app/samples`: Processed sample collections
- `/app/backend/uploads`: File uploads from web UI

#### Development Volumes (Optional)
- `./backend:/app/backend`: Hot reload for backend code
- `./react-app/dist:/app/react-app/dist`: Hot reload for frontend changes

Remove development volumes in production for better security.

### Ports

- `8100`: FastAPI server (serves both API and React app)
- `5432`: PostgreSQL database (postgres container only)

## docker-compose Configuration

### Services

#### PostgreSQL Database
```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: sp404_user
    POSTGRES_PASSWORD: changeme123
    POSTGRES_DB: sp404_samples
  volumes:
    - postgres-data:/var/lib/postgresql/data
```

#### Backend + Frontend
```yaml
backend:
  build: .
  ports:
    - "8100:8100"
  environment:
    DATABASE_URL: postgresql+asyncpg://sp404_user:changeme123@postgres:5432/sp404_samples
    ENVIRONMENT: development
  volumes:
    - ./backend:/app/backend  # Development only
    - ./react-app/dist:/app/react-app/dist  # Development only
    - ./downloads:/app/downloads  # Data persistence
    - ./samples:/app/samples  # Data persistence
```

### Profiles

The docker-compose.yml supports different profiles:

```bash
# Development (with source mounting)
docker-compose up

# Production (no source mounting - edit docker-compose.yml first)
docker-compose --profile prod up -d
```

## Health Checks

### Container Health Check
The container includes a built-in health check:

```bash
# Check container health
docker ps

# Should show "healthy" status after ~30 seconds
```

### Manual Health Check
```bash
curl http://localhost:8100/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

### API Test
```bash
# Test samples endpoint
curl http://localhost:8100/api/v1/samples

# Test React app
curl http://localhost:8100
# Should return index.html
```

## Database Setup

### First-Time Initialization

```bash
# With docker-compose
docker-compose up -d postgres
docker-compose exec backend python -m app.db.init_db

# Standalone
docker exec sp404-backend python -m app.db.init_db
```

### Migrations

Database migrations are managed by Alembic:

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Database Backup

```bash
# Backup
docker exec sp404-postgres pg_dump -U sp404_user sp404_samples > backup.sql

# Restore
docker exec -i sp404-postgres psql -U sp404_user sp404_samples < backup.sql
```

## Networking

### Container Communication

- Backend connects to PostgreSQL via Docker network (`sp404-network`)
- PostgreSQL hostname in container: `postgres`
- Backend hostname in container: `backend`

### External Access

- Application (React + API): http://localhost:8100
- PostgreSQL: localhost:5432 (if port is exposed)

### WebSocket

WebSocket connections work automatically:
- URL: `ws://localhost:8100/ws/vibe/{sample_id}`
- No special configuration needed for Docker

## Development Workflow

### Live Development with Docker

```bash
# 1. Start services
docker-compose up -d

# 2. Backend changes auto-reload (via mounted volume + --reload flag)
# Edit files in ./backend/

# 3. Frontend changes require rebuild
cd react-app && npm run build

# 4. View logs
docker-compose logs -f backend
```

### Testing in Docker

```bash
# Run backend tests
docker-compose exec backend pytest

# Run specific test
docker-compose exec backend pytest backend/tests/test_collection_api.py

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

## Production Deployment

### Pre-Deployment Checklist

1. Set environment variables:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
   export OPENROUTER_API_KEY="sk-..."
   export ENVIRONMENT=production
   ```

2. Remove development volumes from docker-compose.yml:
   ```yaml
   # REMOVE these lines:
   - ./backend:/app/backend:delegated
   - ./react-app/dist:/app/react-app/dist:delegated
   ```

3. Update command to remove --reload:
   ```yaml
   command: uvicorn app.main:app --host 0.0.0.0 --port 8100
   # NO --reload flag in production
   ```

4. Build fresh image:
   ```bash
   docker-compose build --no-cache
   ```

### Deployment Steps

```bash
# 1. Stop old containers
docker-compose down

# 2. Backup database
docker exec sp404-postgres pg_dump -U sp404_user sp404_samples > backup_$(date +%Y%m%d).sql

# 3. Pull/build new image
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec backend alembic upgrade head

# 6. Health check
curl http://localhost:8100/health

# 7. Smoke test
curl http://localhost:8100/api/v1/samples
open http://localhost:8100
```

### Rollback Plan

```bash
# 1. Stop new containers
docker-compose down

# 2. Restore database
docker exec -i sp404-postgres psql -U sp404_user sp404_samples < backup_YYYYMMDD.sql

# 3. Revert to previous image
docker tag sp404-sample-agent:previous sp404-sample-agent:latest
docker-compose up -d

# 4. Verify
curl http://localhost:8100/health
```

## Monitoring

### Logs

```bash
# View all logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow new logs
docker-compose logs -f --tail=0 backend
```

### Resource Usage

```bash
# Container stats
docker stats sp404-backend

# Disk usage
docker system df

# Container inspect
docker inspect sp404-backend
```

### Error Tracking

Common issues and solutions:

1. **Container won't start**
   - Check logs: `docker-compose logs backend`
   - Check env vars: `docker-compose config`
   - Check network: `docker network inspect sp404-network`

2. **Database connection failed**
   - Verify DATABASE_URL format
   - Check postgres container: `docker-compose ps postgres`
   - Check network: `docker exec sp404-backend ping postgres`

3. **React app not loading**
   - Verify dist exists: `docker exec sp404-backend ls -la react-app/dist`
   - Check logs for static file errors
   - Verify build completed: `docker history sp404-sample-agent:latest`

4. **High memory usage**
   - Normal: 200-400MB
   - Check for memory leaks in audio processing
   - Limit container memory: `docker update --memory=1g sp404-backend`

## Security Best Practices

### Production Security

1. **Change default passwords**
   ```bash
   export POSTGRES_PASSWORD="$(openssl rand -base64 32)"
   ```

2. **Use secrets management**
   ```yaml
   # docker-compose.yml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

3. **Run as non-root user**
   ```dockerfile
   # Add to Dockerfile
   RUN useradd -m -u 1000 sp404user
   USER sp404user
   ```

4. **Limit container capabilities**
   ```yaml
   security_opt:
     - no-new-privileges:true
   cap_drop:
     - ALL
   cap_add:
     - NET_BIND_SERVICE
   ```

5. **Use read-only filesystem where possible**
   ```yaml
   read_only: true
   tmpfs:
     - /tmp
     - /var/tmp
   ```

### Network Security

1. **Use internal networks**
   ```yaml
   networks:
     sp404-network:
       driver: bridge
       internal: true  # No external access
   ```

2. **Expose only necessary ports**
   ```yaml
   # DON'T expose PostgreSQL to host in production
   # postgres:
   #   ports:
   #     - "5432:5432"  # REMOVE THIS
   ```

3. **Use reverse proxy (nginx/traefik)**
   ```nginx
   # nginx.conf
   server {
     listen 80;
     location / {
       proxy_pass http://localhost:8100;
       proxy_set_header Host $host;
     }
   }
   ```

## Troubleshooting

### Build Failures

**Node build fails:**
```bash
# Check Node version in Dockerfile (should be 20)
docker run --rm node:20-alpine node --version

# Build frontend separately to debug
cd react-app && npm run build
```

**Python packages fail:**
```bash
# Check Python version (should be 3.13)
docker run --rm python:3.13-slim python --version

# Build backend separately to debug
docker build --target backend-builder .
```

### Runtime Issues

**Import errors:**
```bash
# Check PYTHONPATH
docker exec sp404-backend env | grep PYTHON

# Check installed packages
docker exec sp404-backend pip list
```

**Static files not found:**
```bash
# Verify dist directory
docker exec sp404-backend ls -la /app/react-app/dist

# Check FastAPI static mounting
docker exec sp404-backend cat backend/app/main.py | grep -A5 "react_dist"
```

### Performance Tuning

**Optimize image size:**
```dockerfile
# Use multi-stage builds (already implemented)
# Remove dev dependencies
# Use .dockerignore
```

**Optimize build time:**
```bash
# Use BuildKit
DOCKER_BUILDKIT=1 docker build -t sp404-sample-agent:latest .

# Cache npm modules
# Already implemented: COPY package*.json FIRST
```

**Optimize runtime:**
```yaml
# Allocate more resources
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

## FAQ

### Why single container for backend + frontend?

- Simpler deployment (one service)
- FastAPI efficiently serves static files
- No CORS issues
- Single health check
- Easier to scale (replicate entire stack)

### Can I run frontend separately?

Yes, for development:
```bash
# Start backend only
docker-compose up postgres backend

# Start frontend dev server separately
cd react-app && npm run dev
```

Configure VITE_API_URL in react-app/.env

### How do I update just the frontend?

```bash
# Rebuild React app
cd react-app && npm run build

# Rebuild Docker image
docker-compose build backend

# Restart container
docker-compose up -d backend
```

### How do I scale horizontally?

```yaml
# docker-compose.yml
backend:
  deploy:
    replicas: 3

# Or with docker-compose
docker-compose up -d --scale backend=3
```

Add load balancer (nginx/traefik) in front.

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Docker Documentation: https://docs.docker.com/
- PostgreSQL Docker: https://hub.docker.com/_/postgres
- React Deployment: https://vitejs.dev/guide/static-deploy.html

## Support

For issues:
1. Check logs: `docker-compose logs -f backend`
2. Verify config: `docker-compose config`
3. Test health: `curl http://localhost:8100/health`
4. Review documentation: `docs/`
