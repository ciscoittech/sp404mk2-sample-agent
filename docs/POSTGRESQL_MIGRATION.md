# PostgreSQL Migration Guide

**SP404 MK2 Sample Agent - Database Migration**

This guide covers the complete migration process from SQLite to PostgreSQL for production deployment.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migration Process](#migration-process)
4. [Testing & Verification](#testing--verification)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Configuration Examples](#configuration-examples)
8. [Production Deployment](#production-deployment)

---

## Overview

### Why PostgreSQL?

**Problem**: SQLite database lock errors during batch sample import
- Only 1,115 of 7,284 samples successfully committed (15% success rate)
- Multiple parallel processes writing simultaneously caused lock contention
- Not suitable for multi-user SaaS application

**Solution**: PostgreSQL migration
- True multi-user concurrent write support
- ACID compliance with row-level locking
- Production-ready for SaaS deployment
- Better performance for complex queries

### Migration Scope

- **Database Size**: 16 MB SQLite database with 1,512 samples
- **Tables**: All tables including samples, batches, user_preferences, api_usage, etc.
- **Zero Downtime**: Migration can be performed offline with minimal disruption
- **Data Integrity**: Full verification of row counts after migration

---

## Prerequisites

### 1. Install Dependencies

```bash
# Install PostgreSQL Python drivers
pip install asyncpg>=0.29.0 psycopg2-binary>=2.9.9
```

### 2. Docker or OrbStack

Choose one:

**Docker Desktop**:
```bash
# macOS/Linux
brew install docker

# Or download from https://www.docker.com/products/docker-desktop
```

**OrbStack** (macOS recommended):
```bash
# Install OrbStack (faster, lighter than Docker Desktop)
brew install orbstack

# Start OrbStack
orbstack start
```

### 3. Backup SQLite Database

**CRITICAL**: Always backup before migration!

```bash
# Create timestamped backup
cp backend/sp404_samples.db backend/sp404_samples.db.backup-$(date +%Y%m%d-%H%M%S)

# Verify backup
ls -lh backend/sp404_samples.db*
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

---

## Migration Process

### Step 1: Configure Environment

Edit `.env` file with PostgreSQL settings:

```bash
# PostgreSQL Connection Settings
POSTGRES_USER=sp404_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=sp404_samples
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Database URL (will be auto-constructed)
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# API Settings
API_HOST=0.0.0.0
API_PORT=8100

# OpenRouter API (from existing .env)
OPENROUTER_API_KEY=your_existing_api_key_here
```

### Step 2: Start PostgreSQL Database

**Using Docker Compose**:

```bash
# Start PostgreSQL service only
docker-compose up -d postgres

# Check service status
docker-compose ps

# View logs
docker-compose logs -f postgres

# Wait for healthy status (look for "database system is ready to accept connections")
```

**Using OrbStack**:

```bash
# Start PostgreSQL service
docker-compose up -d postgres

# PostgreSQL will be available at:
# - postgres.orb.local:5432 (via OrbStack domain)
# - localhost:5432 (via port mapping)
```

### Step 3: Verify PostgreSQL Connection

```bash
# Test connection using psql
docker exec -it sp404-postgres psql -U sp404_user -d sp404_samples

# You should see:
# psql (16.x)
# Type "help" for help.
# sp404_samples=#

# Check extensions
\dx

# Should show:
# - uuid-ossp (for UUID generation)
# - pg_trgm (for full-text search)

# Exit psql
\q
```

### Step 4: Run Alembic Migrations

Create database schema in PostgreSQL:

```bash
# Navigate to backend directory
cd backend

# Run all migrations
alembic upgrade head

# You should see output like:
# INFO  [alembic.runtime.migration] Running upgrade -> 20251114_115218, add_user_preferences
# INFO  [alembic.runtime.migration] Running upgrade 20251114_115218 -> 1419beeb89a6, add_sp404_export_tables

# Return to project root
cd ..
```

### Step 5: Test Migration (Dry Run)

**IMPORTANT**: Always test with dry-run first!

```bash
# Run migration script in dry-run mode
python backend/scripts/migrate_sqlite_to_postgres.py --dry-run

# Expected output:
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ SQLite to PostgreSQL Migration                                ┃
# ┃                                                                ┃
# ┃ Source: ./backend/sp404_samples.db                            ┃
# ┃ Target: PostgreSQL (via DATABASE_URL)                         ┃
# ┃ Batch Size: 100                                               ┃
# ┃ Mode: DRY RUN                                                 ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
#
# Found 8 tables to migrate:
#   - samples: 1512 rows
#   - batches: 3 rows
#   - user_preferences: 1 rows
#   - api_usage: 245 rows
#   - audio_features: 1512 rows
#   - sp404_exports: 0 rows
#   - sp404_export_samples: 0 rows
#   - youtube: 12 rows
#
# DRY RUN MODE: No data will be written
```

### Step 6: Execute Live Migration

**WARNING**: This will clear all existing data in PostgreSQL!

```bash
# Run live migration
python backend/scripts/migrate_sqlite_to_postgres.py

# You will be prompted:
# WARNING: This will clear all existing data in PostgreSQL!
# Continue? (yes/no): yes

# Migration progress will show:
# Migrating table: samples
#   Total rows: 1512
#   Clearing existing data in PostgreSQL...
#   ⠋ Migrating samples... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:05
#   ✓ Migrated 1512/1512 rows
#
# [... repeats for all tables ...]
#
# Verifying Migration...
#   ✓ samples: 1512 rows match
#   ✓ batches: 3 rows match
#   ✓ user_preferences: 1 rows match
#   ✓ api_usage: 245 rows match
#   ✓ audio_features: 1512 rows match
#   ✓ sp404_exports: 0 rows match
#   ✓ sp404_export_samples: 0 rows match
#   ✓ youtube: 12 rows match
#
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
# ┃ Metric                    ┃ Value     ┃
# ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
# │ Tables Migrated           │ 8         │
# │ Total Rows Migrated       │ 3285      │
# │ Duration                  │ 12.45s    │
# │ Errors                    │ 0         │
# │ Verification Mismatches   │ 0         │
# └───────────────────────────┴───────────┘
#
# ✓ Migration completed successfully!
```

### Step 7: Update Application Configuration

Update `.env` to use PostgreSQL as default:

```bash
# Set PostgreSQL as active database
DATABASE_URL=postgresql+asyncpg://sp404_user:your_password@localhost:5432/sp404_samples

# Or for Docker/OrbStack:
# DATABASE_URL=postgresql+asyncpg://sp404_user:your_password@postgres:5432/sp404_samples
```

### Step 8: Start Backend Service

```bash
# Start full stack (PostgreSQL + Backend)
docker-compose up -d

# Check all services are healthy
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Access API
open http://localhost:8100
# Or with OrbStack: http://api.orb.local:8100
```

---

## Testing & Verification

### 1. Database Connection Test

```bash
# Test database connectivity
python -c "
import asyncio
from backend.app.db.base import engine
from sqlalchemy import text

async def test():
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT version()'))
        print(f'PostgreSQL version: {result.scalar()}')

asyncio.run(test())
"

# Expected output:
# PostgreSQL version: PostgreSQL 16.x on ...
```

### 2. Sample Count Verification

```bash
# Check sample counts in PostgreSQL
docker exec -it sp404-postgres psql -U sp404_user -d sp404_samples -c "
SELECT
    'samples' as table_name, COUNT(*) as row_count FROM samples
UNION ALL
SELECT 'batches', COUNT(*) FROM batches
UNION ALL
SELECT 'user_preferences', COUNT(*) FROM user_preferences
UNION ALL
SELECT 'api_usage', COUNT(*) FROM api_usage
UNION ALL
SELECT 'audio_features', COUNT(*) FROM audio_features;
"

# Compare with SQLite counts
sqlite3 backend/sp404_samples.db "
SELECT 'samples' as table_name, COUNT(*) as row_count FROM samples
UNION ALL
SELECT 'batches', COUNT(*) FROM batches
UNION ALL
SELECT 'user_preferences', COUNT(*) FROM user_preferences
UNION ALL
SELECT 'api_usage', COUNT(*) FROM api_usage
UNION ALL
SELECT 'audio_features', COUNT(*) FROM audio_features;
"
```

### 3. API Endpoint Testing

```bash
# Test sample listing
curl http://localhost:8100/api/v1/samples | jq

# Test sample upload
curl -X POST http://localhost:8100/api/v1/samples/upload \
  -F "file=@test-sample.wav" \
  -F "title=Test Sample" | jq

# Test batch processing
curl http://localhost:8100/api/v1/batches | jq

# Test user preferences
curl http://localhost:8100/api/v1/preferences | jq
```

### 4. Concurrent Write Test

Test PostgreSQL's concurrent write capabilities (the reason for migration):

```bash
# Run concurrent batch import test
python backend/scripts/batch_import_samples.py --batch-size 100 --parallel 4

# Monitor progress in real-time
docker-compose logs -f backend

# Expected: All samples should commit successfully (vs 15% with SQLite)
```

### 5. Web UI Testing

```bash
# Open web interface
open http://localhost:8100

# Or with OrbStack
open http://api.orb.local:8100

# Test workflows:
# 1. Upload sample (samples page)
# 2. Trigger vibe analysis
# 3. Start batch processing
# 4. Check usage costs
# 5. Update user preferences
# 6. Export to SP-404MK2 format
```

---

## Rollback Procedures

### Scenario 1: Migration Failed - Rollback to SQLite

If migration fails or PostgreSQL issues occur:

```bash
# 1. Stop all services
docker-compose down

# 2. Restore from backup
cp backend/sp404_samples.db.backup-YYYYMMDD-HHMMSS backend/sp404_samples.db

# 3. Update .env to use SQLite
DATABASE_URL=sqlite+aiosqlite:///./backend/sp404_samples.db

# 4. Start backend only (no PostgreSQL)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload

# 5. Verify SQLite working
open http://localhost:8100
```

### Scenario 2: PostgreSQL Running, Need SQLite for Testing

Keep both databases for development:

```bash
# Edit .env to use SQLite
DATABASE_URL=sqlite+aiosqlite:///./backend/sp404_samples.db

# Restart backend
docker-compose restart backend

# PostgreSQL container keeps running but isn't used
```

### Scenario 3: Data Corruption After Migration

```bash
# 1. Drop PostgreSQL database
docker exec -it sp404-postgres psql -U sp404_user -c "DROP DATABASE sp404_samples;"

# 2. Recreate database
docker exec -it sp404-postgres psql -U sp404_user -c "CREATE DATABASE sp404_samples;"

# 3. Run migrations again
cd backend && alembic upgrade head && cd ..

# 4. Re-run migration script
python backend/scripts/migrate_sqlite_to_postgres.py
```

---

## Troubleshooting

### Issue: "Connection Refused" Error

**Symptoms**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused
```

**Solutions**:

1. **Check PostgreSQL is running**:
```bash
docker-compose ps postgres
# Should show "Up" status and "(healthy)"
```

2. **Check PostgreSQL logs**:
```bash
docker-compose logs postgres
# Look for "database system is ready to accept connections"
```

3. **Verify port mapping**:
```bash
docker-compose ps
# postgres should show "0.0.0.0:5432->5432/tcp"
```

4. **Test direct connection**:
```bash
docker exec -it sp404-postgres pg_isready -U sp404_user
# Should show: postgres:5432 - accepting connections
```

### Issue: "Database Does Not Exist"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  database "sp404_samples" does not exist
```

**Solutions**:

1. **Recreate database**:
```bash
docker exec -it sp404-postgres psql -U sp404_user -c "CREATE DATABASE sp404_samples;"
```

2. **Or restart PostgreSQL container** (initialization script will run):
```bash
docker-compose down postgres
docker-compose up -d postgres
```

### Issue: "Authentication Failed"

**Symptoms**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  password authentication failed for user "sp404_user"
```

**Solutions**:

1. **Check .env credentials match docker-compose.yml**:
```bash
grep POSTGRES .env
grep POSTGRES docker-compose.yml
```

2. **Reset PostgreSQL password**:
```bash
docker exec -it sp404-postgres psql -U postgres -c "ALTER USER sp404_user WITH PASSWORD 'new_password';"
```

3. **Update .env with new password**:
```bash
POSTGRES_PASSWORD=new_password
DATABASE_URL=postgresql+asyncpg://sp404_user:new_password@localhost:5432/sp404_samples
```

### Issue: "Migration Script Hangs"

**Symptoms**:
- Migration script stops responding
- No progress updates for several minutes

**Solutions**:

1. **Check batch size** (might be too large):
```bash
# Reduce batch size
python backend/scripts/migrate_sqlite_to_postgres.py --batch-size 50
```

2. **Check PostgreSQL resources**:
```bash
docker stats sp404-postgres
# Look for high CPU/memory usage
```

3. **Increase Docker resources**:
```bash
# Docker Desktop: Settings → Resources → Increase Memory/CPU
# OrbStack: Settings → Resources → Increase limits
```

### Issue: "Row Count Mismatch"

**Symptoms**:
```
Verifying Migration...
  ✗ samples: SQLite=1512, PostgreSQL=1510
```

**Solutions**:

1. **Re-run migration**:
```bash
# Migration script truncates tables before inserting
python backend/scripts/migrate_sqlite_to_postgres.py
```

2. **Check for foreign key constraints**:
```bash
docker exec -it sp404-postgres psql -U sp404_user -d sp404_samples -c "
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f';
"
```

3. **Disable constraints during migration** (if needed):
```bash
# Add to migration script before bulk insert:
# conn.execute(text("SET session_replication_role = replica;"))
# [... insert data ...]
# conn.execute(text("SET session_replication_role = DEFAULT;"))
```

### Issue: "OrbStack Domain Not Resolving"

**Symptoms**:
- `postgres.orb.local` doesn't resolve
- Connection timeout errors

**Solutions**:

1. **Verify OrbStack is running**:
```bash
orbstack status
# Should show "Running"
```

2. **Check OrbStack DNS**:
```bash
ping postgres.orb.local
# Should resolve to 127.0.0.1 or OrbStack IP
```

3. **Use localhost fallback**:
```bash
# Edit .env
POSTGRES_HOST=localhost
DATABASE_URL=postgresql+asyncpg://sp404_user:password@localhost:5432/sp404_samples
```

### Issue: "Port Already in Use"

**Symptoms**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use
```

**Solutions**:

1. **Find process using port 5432**:
```bash
lsof -i :5432
# Or on macOS:
sudo lsof -i :5432
```

2. **Stop conflicting PostgreSQL**:
```bash
# Homebrew PostgreSQL
brew services stop postgresql

# Or kill specific process
kill -9 <PID>
```

3. **Use non-standard port**:
```bash
# Edit .env
POSTGRES_PORT=5433

# Edit docker-compose.yml ports section:
ports:
  - "5433:5432"

# Update DATABASE_URL
DATABASE_URL=postgresql+asyncpg://sp404_user:password@localhost:5433/sp404_samples
```

---

## Configuration Examples

### Local Development (SQLite)

For fast local development without Docker:

```bash
# .env
DATABASE_URL=sqlite+aiosqlite:///./backend/sp404_samples.db
API_HOST=localhost
API_PORT=8100
OPENROUTER_API_KEY=your_key_here
ENVIRONMENT=development
```

### Local Development (PostgreSQL via Docker)

For testing PostgreSQL features locally:

```bash
# .env
POSTGRES_USER=sp404_user
POSTGRES_PASSWORD=devpassword123
POSTGRES_DB=sp404_samples
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

API_HOST=0.0.0.0
API_PORT=8100
OPENROUTER_API_KEY=your_key_here
ENVIRONMENT=development
```

### Local Development (OrbStack)

For macOS with OrbStack domain support:

```bash
# .env
POSTGRES_USER=sp404_user
POSTGRES_PASSWORD=devpassword123
POSTGRES_DB=sp404_samples
POSTGRES_HOST=postgres.orb.local
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

API_HOST=0.0.0.0
API_PORT=8100
OPENROUTER_API_KEY=your_key_here
ENVIRONMENT=development
```

### Staging Environment (Vultr VPS)

For staging server deployment:

```bash
# .env
POSTGRES_USER=sp404_staging
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
POSTGRES_DB=sp404_staging
POSTGRES_HOST=10.0.0.5  # Internal VPS IP
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

API_HOST=0.0.0.0
API_PORT=8100
OPENROUTER_API_KEY=your_key_here
ENVIRONMENT=staging

# S3 Configuration
S3_BUCKET=sp404-staging-samples
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Production Environment (Vultr VPS)

For production SaaS deployment:

```bash
# .env (NEVER commit this file!)
POSTGRES_USER=sp404_prod
POSTGRES_PASSWORD=VERY_STRONG_RANDOM_PASSWORD
POSTGRES_DB=sp404_production
POSTGRES_HOST=postgres-primary.internal  # Internal hostname
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=require

API_HOST=0.0.0.0
API_PORT=8100
OPENROUTER_API_KEY=your_production_key
ENVIRONMENT=production

# S3 Configuration (production bucket)
S3_BUCKET=sp404-production-samples
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=production_access_key
AWS_SECRET_ACCESS_KEY=production_secret_key

# Security
SECRET_KEY=RANDOMLY_GENERATED_SECRET_KEY
ALLOWED_HOSTS=app.sp404agent.com,api.sp404agent.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
LOG_LEVEL=WARNING
```

### Non-Standard Port Configuration

For running PostgreSQL on alternate port (e.g., 5433):

```bash
# .env
POSTGRES_PORT=5433
DATABASE_URL=postgresql+asyncpg://sp404_user:password@localhost:5433/sp404_samples

# docker-compose.yml
services:
  postgres:
    ports:
      - "5433:5432"  # Map host 5433 to container 5432
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Database backup created and verified
- [ ] Migration tested in staging environment
- [ ] All tests passing (pytest backend/tests/)
- [ ] E2E tests passing (playwright frontend/tests/e2e/)
- [ ] Environment variables configured for production
- [ ] SSL certificates installed and configured
- [ ] PostgreSQL connection pooling configured
- [ ] Database credentials rotated and secured
- [ ] S3 buckets created and configured
- [ ] Monitoring and logging configured (Sentry, etc.)
- [ ] Rollback plan documented and tested

### Deployment Steps (Vultr VPS)

#### 1. Server Preparation

```bash
# SSH into Vultr VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create application user
useradd -m -s /bin/bash sp404
usermod -aG docker sp404
```

#### 2. Application Setup

```bash
# Switch to application user
su - sp404

# Clone repository (or deploy via CI/CD)
git clone https://github.com/yourusername/sp404mk2-sample-agent.git
cd sp404mk2-sample-agent

# Create production .env (use secure values!)
cp .env.example .env
nano .env  # Edit with production values
```

#### 3. PostgreSQL Configuration

```bash
# Start PostgreSQL only first
docker-compose up -d postgres

# Wait for healthy status
docker-compose ps postgres

# Run Alembic migrations
cd backend
alembic upgrade head
cd ..

# Optional: Import existing data
python backend/scripts/migrate_sqlite_to_postgres.py
```

#### 4. Start Full Stack

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f

# Test API endpoint
curl http://localhost:8100/api/v1/health
```

#### 5. Configure Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/sp404-api
server {
    listen 80;
    server_name api.sp404agent.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sp404agent.com;

    # SSL certificates (from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.sp404agent.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sp404agent.com/privkey.pem;

    # Proxy to FastAPI backend
    location / {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for real-time updates
    location /ws {
        proxy_pass http://localhost:8100;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/sp404-api /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

#### 6. SSL Certificate Setup

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Obtain certificate
certbot --nginx -d api.sp404agent.com

# Test auto-renewal
certbot renew --dry-run
```

#### 7. Configure Monitoring

```bash
# Install Prometheus node exporter
docker run -d \
  --name node-exporter \
  --restart unless-stopped \
  -p 9100:9100 \
  prom/node-exporter

# Configure log rotation
cat > /etc/logrotate.d/sp404 <<EOF
/var/log/sp404/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 sp404 sp404
    sharedscripts
    postrotate
        docker-compose -f /home/sp404/sp404mk2-sample-agent/docker-compose.yml restart backend
    endscript
}
EOF
```

#### 8. Setup Automated Backups

```bash
# Create backup script
cat > /home/sp404/backup-postgres.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/home/sp404/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CONTAINER="sp404-postgres"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
docker exec $CONTAINER pg_dump -U sp404_prod -d sp404_production | gzip > $BACKUP_DIR/postgres-$TIMESTAMP.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "postgres-*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/postgres-$TIMESTAMP.sql.gz s3://sp404-backups/
EOF

chmod +x /home/sp404/backup-postgres.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line: 0 2 * * * /home/sp404/backup-postgres.sh
```

### Post-Deployment Verification

```bash
# 1. Test API health endpoint
curl https://api.sp404agent.com/api/v1/health

# 2. Test database connection
curl https://api.sp404agent.com/api/v1/samples | jq

# 3. Test sample upload
curl -X POST https://api.sp404agent.com/api/v1/samples/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test-sample.wav" | jq

# 4. Monitor logs
docker-compose logs -f backend

# 5. Check PostgreSQL performance
docker exec -it sp404-postgres psql -U sp404_prod -d sp404_production -c "
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Production Best Practices

1. **Connection Pooling**: Already configured with NullPool (asyncpg handles pooling)
2. **Database Backups**: Automated daily backups with 30-day retention
3. **SSL/TLS**: All connections encrypted (PostgreSQL sslmode=require, HTTPS for API)
4. **Monitoring**: Prometheus, Sentry for error tracking
5. **Logging**: Structured JSON logging with log rotation
6. **Resource Limits**: Docker resource constraints configured
7. **Health Checks**: Database and API health checks for monitoring
8. **Secrets Management**: Environment variables, never commit .env
9. **Updates**: Regular security updates for base images
10. **Disaster Recovery**: Documented rollback procedures and backup restoration

---

## Summary

**Migration Path**: SQLite → PostgreSQL for production SaaS deployment

**Key Benefits**:
- ✅ Concurrent write support (solves database lock errors)
- ✅ Production-ready multi-user database
- ✅ Better performance for complex queries
- ✅ Full-text search capabilities (pg_trgm)
- ✅ Row-level locking for batch operations

**Migration Tools**:
- `migrate_sqlite_to_postgres.py` - Automated data migration script
- `docker-compose.yml` - Local development environment
- `alembic` - Database schema management
- `.env` - Environment configuration

**Support**:
- GitHub Issues: https://github.com/yourusername/sp404mk2-sample-agent/issues
- Documentation: https://github.com/yourusername/sp404mk2-sample-agent/docs

**Next Steps**:
1. Review this documentation thoroughly
2. Test migration in local environment
3. Deploy to staging environment
4. Verify all functionality
5. Deploy to production with confidence

Good luck with your PostgreSQL migration! 🚀
