# Docker Setup Guide

This guide explains how to use Docker with the SP404MK2 Sample Agent project.

## Quick Start

1. **Copy environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

2. **Build and start all services:**
   ```bash
   make docker-build
   make docker-up
   ```

3. **Initialize the database:**
   ```bash
   make docker-db-init
   ```

4. **Access the application:**
   - Web UI: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Docker Commands

### Basic Operations

```bash
# Build all images
make docker-build

# Start all services
make docker-up

# Stop all services  
make docker-down

# View logs
make docker-logs

# Clean up everything
make docker-clean
```

### Development

```bash
# Start with hot reload
make docker-dev

# Shell into backend
make docker-shell

# Run tests
make docker-test

# Run E2E tests
make docker-e2e
```

### Production

```bash
# Start production services
make docker-prod
```

## Architecture

The Docker setup includes:

- **Backend**: FastAPI application with async support
- **Database**: SQLite with persistent volume
- **Frontend**: Static files served by FastAPI
- **Redis**: For caching and real-time features (optional)
- **Nginx**: Reverse proxy for production (optional)

## Services

### Backend Service
- Port: 8000
- Auto-reload in development
- Health check endpoint
- WebSocket support

### Database
- SQLite with volume persistence
- Automatic initialization on first run
- Test data seeding available

### Testing
- Unit tests run in container
- E2E tests with Playwright
- Coverage reporting

## Volumes

- `./data`: Database files
- `./downloads`: Downloaded samples
- `./logs`: Application logs

## Environment Variables

Key variables in `.env`:

```bash
# API Keys
OPENROUTER_API_KEY=your-key-here

# Security
SECRET_KEY=change-in-production

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/sp404.db

# Redis (optional)
REDIS_URL=redis://redis:6379/0
```

## Troubleshooting

### Port Conflicts
If port 8000 is already in use:
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Database Issues
Reset the database:
```bash
make docker-clean
make docker-up
make docker-db-init
```

### Permission Issues
If you get permission errors:
```bash
# Fix ownership
sudo chown -R $USER:$USER ./data ./downloads
```

## Production Deployment

For production:

1. Update `.env` with production values
2. Enable HTTPS in nginx config
3. Use production profile:
   ```bash
   make docker-prod
   ```

## Monitoring

View container status:
```bash
docker compose ps
```

Check resource usage:
```bash
docker stats
```

## Backup

Backup database:
```bash
docker compose exec backend cp /app/data/sp404.db /app/data/sp404-backup.db
```

## Security Notes

- Change `SECRET_KEY` in production
- Use strong passwords
- Enable HTTPS for production
- Regularly update dependencies
- Monitor logs for suspicious activity