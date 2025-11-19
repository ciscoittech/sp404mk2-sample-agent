# Self-Hosting Guide

This guide will help you deploy SP404MK2 Sample Agent on your own infrastructure. The application is designed to run completely free using self-hosted databases and free-tier AI APIs.

## Table of Contents

- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [System Requirements](#system-requirements)
- [Database Options](#database-options)
- [Deployment Methods](#deployment-methods)
- [Configuration](#configuration)
- [Production Considerations](#production-considerations)
- [Troubleshooting](#troubleshooting)
- [Cost Breakdown](#cost-breakdown)

## Quick Start (5 Minutes)

The fastest way to get running is with Docker:

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sp404mk2-sample-agent
cd sp404mk2-sample-agent

# 2. Set up environment
cp .env.example .env

# 3. Get your OpenRouter API key (FREE tier available)
# Visit https://openrouter.ai/
# Sign up and copy your API key

# 4. Edit .env and add your API key
# OPENROUTER_API_KEY=your-key-here

# 5. Start the application
make docker-build
make docker-up
make docker-db-init

# 6. Access the web UI
open http://localhost:8000
```

That's it! The application is now running locally with a PostgreSQL database in Docker.

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB (plus space for samples)
- **OS**: Linux, macOS, or Windows (with WSL2)
- **Network**: Outbound HTTPS access for API calls

### Recommended for Production

- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **OS**: Linux (Ubuntu 22.04 LTS or similar)

### Software Dependencies

- **Docker** 24.0+ and **Docker Compose** 2.0+ (for Docker deployment)
- **Python** 3.13+ (for local deployment)
- **Node.js** 20+ (for frontend development)
- **FFmpeg** (for audio processing)
- **PostgreSQL** 15+ (if not using Docker)

## Database Options

Choose the database that best fits your needs:

### Option 1: PostgreSQL (Recommended)

**Best for**: Full-featured local deployment

**Setup with Docker** (included in docker-compose.yml):
```bash
# Already configured! Just run:
make docker-up
make docker-db-init
```

**Setup manually**:
```bash
# Install PostgreSQL
sudo apt-get install postgresql-15

# Create database and user
sudo -u postgres psql
postgres=# CREATE DATABASE sp404_samples;
postgres=# CREATE USER sp404_user WITH PASSWORD 'changeme123';
postgres=# GRANT ALL PRIVILEGES ON DATABASE sp404_samples TO sp404_user;
postgres=# \q

# Update .env
DATABASE_URL=postgresql+asyncpg://sp404_user:changeme123@localhost:5432/sp404_samples
```

### Option 2: Turso (LibSQL)

**Best for**: Edge-distributed database with vector search

**Why Turso?**
- Free tier: 500 databases, 9GB storage
- Built-in vector search (no extra setup)
- Global edge replication
- Low latency worldwide

**Setup**:
```bash
# 1. Sign up at https://turso.tech/
# 2. Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# 3. Login and create database
turso auth login
turso db create sp404-samples

# 4. Get connection details
turso db show sp404-samples

# 5. Update .env
TURSO_DATABASE_URL=libsql://sp404-samples-YOUR_ORG.turso.io
TURSO_AUTH_TOKEN=your-token-here
```

### Option 3: SQLite (Development Only)

**Best for**: Local development and testing

```bash
# Update .env
DATABASE_URL=sqlite+aiosqlite:///./backend/sp404_samples.db
```

**Note**: SQLite is not recommended for production due to limited concurrent write support.

## Deployment Methods

### Method 1: Docker (Recommended)

Complete containerized deployment with all dependencies.

```bash
# Development mode (with hot reload)
make docker-dev

# Production mode
make docker-prod

# View logs
make docker-logs

# Stop services
make docker-down
```

**Docker Compose Profiles**:
- `dev`: Development with hot reload
- `prod`: Production with optimizations
- `init`: Database initialization

### Method 2: Local Python

Run directly on your system without Docker.

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.13 python3-pip ffmpeg postgresql-client

# 2. Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -e .

# 4. Initialize database
cd backend
../venv/bin/python -m app.db.init_db
cd ..

# 5. Start backend
./venv/bin/python backend/run.py

# 6. Start frontend (in another terminal)
cd react-app
npm install
npm run build
npm run preview
```

### Method 3: VPS/Cloud Deployment

Deploy to a cloud provider like DigitalOcean, Linode, or AWS.

**Example: Ubuntu 22.04 on DigitalOcean**

```bash
# 1. Create droplet (2GB RAM minimum)
# 2. SSH into server
ssh root@your-server-ip

# 3. Install dependencies
apt-get update
apt-get install -y docker.io docker-compose git

# 4. Clone repository
git clone https://github.com/YOUR_USERNAME/sp404mk2-sample-agent
cd sp404mk2-sample-agent

# 5. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 6. Start services
docker compose --profile prod up -d

# 7. Set up reverse proxy (optional)
apt-get install -y nginx certbot python3-certbot-nginx

# Configure nginx for your domain
cat > /etc/nginx/sites-available/sp404 << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/sp404 /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get SSL certificate
certbot --nginx -d your-domain.com
```

## Configuration

### Required Configuration

Only one setting is required to get started:

```bash
# .env
OPENROUTER_API_KEY=your-key-here  # Get from https://openrouter.ai/
```

### Database Configuration

Choose one database option (see [Database Options](#database-options)):

```bash
# PostgreSQL (default)
DATABASE_URL=postgresql+asyncpg://sp404_user:changeme123@localhost:5432/sp404_samples

# OR Turso
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-token-here
```

### Optional Enhancements

```bash
# YouTube channel monitoring (requires API key)
YOUTUBE_API_KEY=your-key-here  # Get from https://console.cloud.google.com/

# Security (change in production!)
SECRET_KEY=generate-a-random-secret-key-here

# Cost limits
MONTHLY_BUDGET_USD=10.0
DAILY_TOKEN_LIMIT=100000
```

### Audio Analysis Configuration

```bash
# Use Essentia for improved BPM detection (requires installation)
USE_ESSENTIA=false  # Set to true after installing Essentia

# Enable genre classification (requires TensorFlow models)
ENABLE_GENRE_CLASSIFICATION=false

# Audio processing timeout
AUDIO_ANALYSIS_TIMEOUT=30
```

## Production Considerations

### Security

1. **Change default secrets**:
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use environment variables** instead of .env file:
   ```bash
   export OPENROUTER_API_KEY="your-key"
   export DATABASE_URL="your-db-url"
   ```

3. **Enable HTTPS** with Let's Encrypt (see VPS deployment example)

4. **Restrict CORS origins**:
   ```bash
   BACKEND_CORS_ORIGINS=https://your-domain.com
   ```

### Performance Optimization

1. **Enable Redis caching** (optional):
   ```bash
   # Install Redis
   docker run -d -p 6379:6379 redis:7-alpine

   # Update .env
   REDIS_URL=redis://localhost:6379
   ```

2. **Adjust worker processes** in docker-compose.yml:
   ```yaml
   environment:
     - WORKERS=4  # Number of CPU cores
   ```

3. **Configure audio analysis timeout**:
   ```bash
   # For batch processing, increase timeout
   AUDIO_ANALYSIS_TIMEOUT=60
   ```

### Monitoring

1. **Check application logs**:
   ```bash
   # Docker
   make docker-logs

   # Local
   tail -f backend/logs/app.log
   ```

2. **Monitor database**:
   ```bash
   # PostgreSQL
   docker compose exec db psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM samples;"

   # Turso
   turso db shell sp404-samples
   ```

3. **Track API costs**:
   - Visit `/usage` page in web UI
   - Monitor OpenRouter dashboard: https://openrouter.ai/activity

### Backups

1. **Database backups** (PostgreSQL):
   ```bash
   # Backup
   docker compose exec db pg_dump -U sp404_user sp404_samples > backup.sql

   # Restore
   docker compose exec -T db psql -U sp404_user sp404_samples < backup.sql
   ```

2. **Database backups** (Turso):
   ```bash
   # Turso has automatic backups
   turso db backup list sp404-samples
   turso db backup restore sp404-samples backup-id
   ```

3. **Sample files**:
   ```bash
   # Backup samples directory
   tar -czf samples-backup.tar.gz samples/ downloads/
   ```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
make docker-build
make docker-up

# Run migrations
docker compose exec backend alembic upgrade head
```

## Troubleshooting

### Database Connection Issues

**PostgreSQL "connection refused"**:
```bash
# Check if PostgreSQL is running
docker compose ps

# View PostgreSQL logs
docker compose logs db

# Test connection
docker compose exec db psql -U sp404_user -d sp404_samples -c "SELECT 1;"
```

**Turso "authentication failed"**:
```bash
# Verify token
turso db tokens create sp404-samples

# Check database status
turso db show sp404-samples
```

### Audio Processing Errors

**FFmpeg not found**:
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
```

**librosa import error**:
```bash
# Install system audio libraries
sudo apt-get install libsndfile1 libsndfile1-dev

# Reinstall librosa
pip uninstall librosa
pip install librosa
```

### API Issues

**OpenRouter 401 Unauthorized**:
- Verify API key is correct in .env
- Check key has not expired: https://openrouter.ai/keys

**Rate limiting**:
- Free tier has rate limits
- Upgrade at https://openrouter.ai/credits

### Memory Issues

**Docker out of memory**:
```bash
# Check Docker memory limits
docker stats

# Increase memory in Docker settings (macOS/Windows)
# Or increase container limits in docker-compose.yml
```

### Port Conflicts

**Port 8000 already in use**:
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
```

## Cost Breakdown

### Free Tier Setup

- **Database**: Turso free tier (9GB storage)
- **AI API**: OpenRouter free tier with rate limits
- **Hosting**: Self-hosted on your hardware (no cost)

**Total monthly cost**: $0

### Low-Cost Setup

- **Database**: Turso free tier (9GB storage)
- **AI API**: OpenRouter pay-as-you-go (~$0.00001 per sample with Qwen 7B)
- **Hosting**: DigitalOcean droplet ($6/month for 2GB RAM)

**Sample analysis cost**: ~$1 per 100,000 samples
**Total monthly cost**: ~$6-7/month

### Full-Featured Setup

- **Database**: Turso pro tier ($29/month for unlimited storage)
- **AI API**: OpenRouter with GPT-4 models (~$0.0001 per sample)
- **Hosting**: DigitalOcean droplet ($12/month for 4GB RAM)

**Sample analysis cost**: ~$10 per 100,000 samples
**Total monthly cost**: ~$41/month + API usage

## Support

Having trouble? Here's how to get help:

1. **Check documentation**: Review this guide and `docs/` folder
2. **Search issues**: https://github.com/YOUR_USERNAME/sp404mk2-sample-agent/issues
3. **Ask for help**: Open a new issue with:
   - Steps to reproduce
   - Error messages/logs
   - Environment details (OS, Docker version, etc.)

---

Happy self-hosting! Remember: this is YOUR instance. Customize, modify, and make it work for your workflow.
