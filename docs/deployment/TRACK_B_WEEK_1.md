# Track B Week 1: Infrastructure Setup

**Duration**: 5 days (30 hours total)
**Focus**: Production VPS + Docker + PostgreSQL + Redis + Nginx + SSL
**Dependencies**: Vultr account, domain name, DNS access
**Risk**: Low

---

## OVERVIEW

Deploy a production-ready infrastructure stack on Vultr VPS for SP-404 Sample Manager. Setup Docker containers for PostgreSQL and Redis, configure Nginx reverse proxy with SSL, and establish deployment pipelines.

**Current State**:
- Local development with OrbStack Docker
- PostgreSQL 16 on localhost:5433
- 2,328+ samples in local database
- Backend API running on localhost:8100

**Target State**:
- Vultr VPS with 4GB RAM, 2 vCPUs
- Docker + Docker Compose production setup
- PostgreSQL 16 container with sample data
- Redis 7 container for caching
- Nginx reverse proxy with SSL (Let's Encrypt)
- Secure firewall configuration
- Automated backup system

---

## PREREQUISITES

### Required Access
- [ ] Vultr account (https://www.vultr.com)
- [ ] Domain name (e.g., sp404.yourdomain.com)
- [ ] DNS management access
- [ ] SSH key pair generated

### Required Tools (Local Machine)
```bash
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "your_email@example.com"

# Install tools
brew install postgresql  # For pg_dump/pg_restore
brew install redis       # For redis-cli testing
```

---

## TASK 1: Prepare Vultr VPS

**Duration**: 4 hours
**Complexity**: Low
**Prerequisites**: Vultr account, SSH key

### Objective
Provision and secure a Vultr VPS for production deployment.

### Step 1.1: Create VPS Instance (30 min)

**Login to Vultr Dashboard**:
1. Visit https://my.vultr.com
2. Click "Deploy" → "Deploy New Server"

**Select Configuration**:
- **Server Type**: Cloud Compute - Shared CPU
- **Location**: Choose closest to your users (e.g., Los Angeles, New York, Frankfurt)
- **Image**: Ubuntu 24.04 LTS x64
- **Plan**: 4 GB RAM / 2 vCPUs / 80 GB SSD / 3 TB bandwidth ($12/month)
- **Additional Features**:
  - [x] Enable IPv6
  - [x] Enable Auto Backups (+20%)
  - [ ] DDOS Protection (not needed for MVP)
- **Server Hostname**: `sp404-production`
- **Label**: SP-404 Sample Manager Production

**Add SSH Key**:
1. Click "Add SSH Key"
2. Paste your public key: `cat ~/.ssh/id_ed25519.pub`
3. Name: "Development Machine"

**Deploy**:
1. Click "Deploy Now"
2. Wait 2-3 minutes for provisioning

**Validation**:
```bash
# Note the IP address from Vultr dashboard
export VPS_IP="YOUR_VPS_IP_HERE"

# Test SSH connection
ssh root@$VPS_IP
# Should connect without password

# Check system info
uname -a
# Should show: Linux sp404-production 6.8.0 Ubuntu 24.04 LTS

# Check resources
free -h
# Should show: ~4GB total memory

df -h
# Should show: ~75GB available on /
```

### Step 1.2: Initial Server Hardening (1 hour)

**Update System Packages**:
```bash
# SSH into VPS
ssh root@$VPS_IP

# Update package lists
apt update

# Upgrade all packages
apt upgrade -y

# Install essential tools
apt install -y \
  curl \
  wget \
  git \
  vim \
  htop \
  ufw \
  fail2ban \
  unattended-upgrades \
  ca-certificates \
  gnupg \
  lsb-release

# Verify installation
docker --version || echo "Docker not yet installed (expected)"
```

**Create Non-Root User**:
```bash
# Create deploy user
adduser deploy
# Set strong password when prompted

# Add to sudo group
usermod -aG sudo deploy

# Copy SSH keys to deploy user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Test deploy user SSH (from local machine)
ssh deploy@$VPS_IP
# Should connect without password

# Verify sudo access
sudo whoami
# Should output: root
```

**Disable Root SSH Login**:
```bash
# Edit SSH config
sudo vim /etc/ssh/sshd_config

# Change these settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH service
sudo systemctl restart ssh

# Verify (from local machine)
ssh root@$VPS_IP
# Should be denied

ssh deploy@$VPS_IP
# Should work
```

**Validation**:
- ✅ System packages updated
- ✅ Deploy user created with sudo access
- ✅ SSH key authentication working
- ✅ Root SSH login disabled

### Step 1.3: Configure Firewall (1 hour)

**Setup UFW (Uncomplicated Firewall)**:
```bash
# SSH as deploy user
ssh deploy@$VPS_IP

# Allow SSH (CRITICAL - do this first!)
sudo ufw allow 22/tcp comment 'SSH'

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Allow PostgreSQL (only for development, will restrict later)
sudo ufw allow 5432/tcp comment 'PostgreSQL'

# Allow Redis (only for development, will restrict later)
sudo ufw allow 6379/tcp comment 'Redis'

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status verbose
# Should show:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW IN    Anywhere
# 80/tcp                     ALLOW IN    Anywhere
# 443/tcp                    ALLOW IN    Anywhere
# 5432/tcp                   ALLOW IN    Anywhere
# 6379/tcp                   ALLOW IN    Anywhere
```

**Install and Configure Fail2Ban**:
```bash
# Fail2Ban prevents brute-force SSH attacks
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status
# Should show: ssh jail enabled

# View banned IPs (should be empty initially)
sudo fail2ban-client status sshd
```

**Validation**:
```bash
# From local machine, verify firewall allows SSH
ssh deploy@$VPS_IP

# From VPS, verify firewall is active
sudo ufw status numbered
# Should list all allowed ports

# Verify fail2ban is running
sudo systemctl status fail2ban
# Should show: active (running)
```

### Step 1.4: Configure DNS (30 min)

**Setup A Record** (Your DNS Provider):
1. Login to your DNS provider (e.g., Cloudflare, Namecheap, etc.)
2. Add A record:
   - **Type**: A
   - **Name**: sp404 (or api.sp404)
   - **Value**: `YOUR_VPS_IP`
   - **TTL**: 3600 (1 hour)
3. Add AAAA record (IPv6):
   - **Type**: AAAA
   - **Name**: sp404
   - **Value**: `YOUR_VPS_IPv6` (from Vultr dashboard)
   - **TTL**: 3600

**Test DNS Resolution**:
```bash
# From local machine
dig sp404.yourdomain.com +short
# Should return: YOUR_VPS_IP

# Test IPv6
dig sp404.yourdomain.com AAAA +short
# Should return: YOUR_VPS_IPv6

# Test from VPS
ssh deploy@$VPS_IP
nslookup sp404.yourdomain.com
# Should resolve to VPS IP
```

**Validation**:
- ✅ A record points to VPS IP
- ✅ AAAA record points to VPS IPv6
- ✅ DNS resolution works from multiple locations
- ✅ TTL set to 3600 seconds

### Step 1.5: Setup Automatic Security Updates (1 hour)

**Configure Unattended Upgrades**:
```bash
# Edit unattended-upgrades config
sudo vim /etc/apt/apt.conf.d/50unattended-upgrades

# Ensure these lines are uncommented:
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

# Enable automatic reboot if needed
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";

# Enable email notifications (optional)
# Unattended-Upgrade::Mail "your-email@example.com";
```

**Enable Auto-Updates**:
```bash
# Edit auto-upgrade config
sudo vim /etc/apt/apt.conf.d/20auto-upgrades

# Add these lines:
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";

# Test unattended-upgrades
sudo unattended-upgrade --dry-run --debug

# Enable service
sudo systemctl enable unattended-upgrades
sudo systemctl start unattended-upgrades
```

**Validation**:
```bash
# Check service status
sudo systemctl status unattended-upgrades
# Should show: active (running)

# View upgrade logs
sudo cat /var/log/unattended-upgrades/unattended-upgrades.log
# Should show recent activity
```

**Time Estimate**: 4 hours (30min + 1hr + 1hr + 30min + 1hr)

---

## TASK 2: Install Docker and Docker Compose

**Duration**: 3 hours
**Complexity**: Low
**Prerequisites**: Task 1 complete

### Objective
Install Docker Engine and Docker Compose for container orchestration.

### Step 2.1: Install Docker Engine (1 hour)

```bash
# SSH to VPS
ssh deploy@$VPS_IP

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update

# Install Docker Engine and plugins
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# Verify installation
docker --version
# Should show: Docker version 27.x.x

docker compose version
# Should show: Docker Compose version v2.x.x
```

**Add Deploy User to Docker Group**:
```bash
# Add user to docker group
sudo usermod -aG docker deploy

# Apply group changes (logout and login)
exit
ssh deploy@$VPS_IP

# Test Docker without sudo
docker ps
# Should show: CONTAINER ID ... (empty list)

# Test with hello-world
docker run hello-world
# Should pull image and print success message
```

**Validation**:
```bash
# Check Docker service
sudo systemctl status docker
# Should show: active (running)

# Check Docker info
docker info
# Should show server version, storage driver, etc.

# List Docker networks
docker network ls
# Should show: bridge, host, none

# Check Docker Compose
docker compose version
# Should show: v2.x.x
```

### Step 2.2: Configure Docker Daemon (1 hour)

**Create Docker Daemon Config**:
```bash
# Create daemon.json
sudo vim /etc/docker/daemon.json

# Add configuration:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "userland-proxy": false,
  "default-address-pools": [
    {
      "base": "172.20.0.0/16",
      "size": 24
    }
  ]
}

# Restart Docker
sudo systemctl restart docker

# Verify config applied
docker info | grep -i "logging driver"
# Should show: Logging Driver: json-file

docker info | grep -i "storage driver"
# Should show: Storage Driver: overlay2
```

**Setup Docker Network for SP-404**:
```bash
# Create custom bridge network
docker network create sp404-network \
  --driver bridge \
  --subnet 172.20.1.0/24 \
  --gateway 172.20.1.1

# Verify network
docker network ls
# Should show: sp404-network

docker network inspect sp404-network
# Should show subnet and gateway
```

**Validation**:
- ✅ Docker daemon configured
- ✅ Logging limited to 10MB × 3 files
- ✅ Custom network created
- ✅ Storage driver is overlay2

### Step 2.3: Create Docker Compose File (1 hour)

**Create Project Directory**:
```bash
# Create app directory
sudo mkdir -p /opt/sp404
sudo chown -R deploy:deploy /opt/sp404
cd /opt/sp404

# Create directory structure
mkdir -p {backend,nginx,postgres,redis,backups,logs}

# Create .env file
vim .env
```

**Environment Variables** (`.env`):
```bash
# PostgreSQL Configuration
POSTGRES_USER=sp404_user
POSTGRES_PASSWORD=CHANGE_THIS_STRONG_PASSWORD
POSTGRES_DB=sp404_samples
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PORT=6379

# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8100
ENVIRONMENT=production

# OpenRouter API (add your key)
OPENROUTER_API_KEY=your_openrouter_key_here

# Database URLs
DATABASE_URL=postgresql+asyncpg://sp404_user:CHANGE_THIS_STRONG_PASSWORD@postgres:5432/sp404_samples
REDIS_URL=redis://redis:6379/0
```

**Create Docker Compose File** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: sp404-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=en_US.UTF-8"
    ports:
      - "127.0.0.1:${POSTGRES_PORT}:5432"  # Only localhost access
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - sp404-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: sp404-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    ports:
      - "127.0.0.1:${REDIS_PORT}:6379"  # Only localhost access
    volumes:
      - ./redis/data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - sp404-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # FastAPI Backend (Week 2)
  # backend:
  #   build:
  #     context: ./backend
  #     dockerfile: Dockerfile
  #   container_name: sp404-backend
  #   restart: unless-stopped
  #   environment:
  #     DATABASE_URL: ${DATABASE_URL}
  #     REDIS_URL: ${REDIS_URL}
  #     OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
  #     ENVIRONMENT: ${ENVIRONMENT}
  #   ports:
  #     - "127.0.0.1:8100:8100"
  #   depends_on:
  #     postgres:
  #       condition: service_healthy
  #     redis:
  #       condition: service_healthy
  #   networks:
  #     - sp404-network

networks:
  sp404-network:
    external: true

volumes:
  postgres-data:
  redis-data:
```

**Validation**:
```bash
# Verify docker-compose.yml syntax
docker compose config
# Should show parsed configuration without errors

# Check environment variables
cat .env
# Ensure passwords are strong (20+ characters)
```

**Time Estimate**: 3 hours (1hr + 1hr + 1hr)

---

## TASK 3: Setup PostgreSQL Container + Restore Data

**Duration**: 5 hours
**Complexity**: Medium
**Prerequisites**: Task 2 complete

### Objective
Deploy PostgreSQL 16 container and restore sample database from local development.

### Step 3.1: Start PostgreSQL Container (30 min)

```bash
# In /opt/sp404
cd /opt/sp404

# Start PostgreSQL only (not backend yet)
docker compose up -d postgres

# Check container status
docker compose ps
# Should show: sp404-postgres running

# Check logs
docker compose logs postgres
# Should show: database system is ready to accept connections

# Verify healthcheck
docker inspect sp404-postgres --format='{{.State.Health.Status}}'
# Should show: healthy
```

**Test Database Connection**:
```bash
# Connect to PostgreSQL container
docker compose exec postgres psql -U sp404_user -d sp404_samples

# Run test query
\dt
# Should show: No relations found (empty database)

# Check database encoding
\l
# Should show: sp404_samples | UTF8

# Exit
\q
```

**Validation**:
- ✅ PostgreSQL container running
- ✅ Healthcheck passing
- ✅ Database accessible
- ✅ UTF-8 encoding set

### Step 3.2: Backup Local Database (1 hour)

**From Local Development Machine**:
```bash
# Navigate to project root
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent

# Create backup directory
mkdir -p backups

# Dump PostgreSQL database (OrbStack port 5433)
pg_dump -h localhost -p 5433 -U sp404_user -d sp404_samples \
  --format=custom \
  --compress=9 \
  --file=backups/sp404_samples_$(date +%Y%m%d_%H%M%S).backup

# Verify backup file
ls -lh backups/
# Should show: sp404_samples_YYYYMMDD_HHMMSS.backup (several MB)

# Test backup integrity
pg_restore --list backups/sp404_samples_*.backup | head -20
# Should show: TABLE sample, TABLE user, etc.

# Create a SQL dump as well (for inspection)
pg_dump -h localhost -p 5433 -U sp404_user -d sp404_samples \
  --format=plain \
  --no-owner \
  --no-acl \
  --file=backups/sp404_samples_$(date +%Y%m%d_%H%M%S).sql

# Check sample count
psql -h localhost -p 5433 -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM sample;"
# Should show: 2328 (or similar)
```

**Validation**:
```bash
# Verify backup files exist
ls -lh backups/
# Should show:
# - sp404_samples_YYYYMMDD_HHMMSS.backup (compressed)
# - sp404_samples_YYYYMMDD_HHMMSS.sql (plain SQL)

# Check backup size
du -h backups/
# Should be 5-50MB depending on sample metadata
```

### Step 3.3: Transfer Backup to VPS (1 hour)

```bash
# From local machine
export VPS_IP="YOUR_VPS_IP"

# Create backups directory on VPS
ssh deploy@$VPS_IP "mkdir -p /opt/sp404/backups"

# Transfer backup file via SCP
scp backups/sp404_samples_*.backup deploy@$VPS_IP:/opt/sp404/backups/

# Verify transfer
ssh deploy@$VPS_IP "ls -lh /opt/sp404/backups/"
# Should show: sp404_samples_YYYYMMDD_HHMMSS.backup

# Check file integrity (compare checksums)
md5 backups/sp404_samples_*.backup
ssh deploy@$VPS_IP "md5sum /opt/sp404/backups/sp404_samples_*.backup"
# MD5 hashes should match
```

**Alternative: Transfer via Compressed Archive**:
```bash
# If backup is large, compress first
tar -czf backups.tar.gz backups/

# Transfer archive
scp backups.tar.gz deploy@$VPS_IP:/opt/sp404/

# Extract on VPS
ssh deploy@$VPS_IP
cd /opt/sp404
tar -xzf backups.tar.gz
rm backups.tar.gz
```

**Validation**:
- ✅ Backup file transferred to VPS
- ✅ File size matches local backup
- ✅ MD5 checksum matches

### Step 3.4: Restore Database on VPS (1.5 hours)

```bash
# SSH to VPS
ssh deploy@$VPS_IP
cd /opt/sp404

# Check PostgreSQL container is running
docker compose ps postgres
# Should show: Up (healthy)

# Restore database from backup
docker compose exec -T postgres pg_restore \
  --username=sp404_user \
  --dbname=sp404_samples \
  --verbose \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  < backups/sp404_samples_*.backup

# Check for errors in output
# Should see: processing data for table "sample", "user", etc.

# Verify restoration
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM sample;"
# Should show: 2328 (or your sample count)

# Check table structure
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "\dt"
# Should show: sample, user, kit, etc.

# Verify specific sample
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT id, name, genre FROM sample LIMIT 5;"
# Should show sample data
```

**Handle Restoration Errors** (if any):
```bash
# If restore fails, check logs
docker compose logs postgres

# Common issues:
# 1. Permission denied → Add --no-owner --no-acl
# 2. Database not empty → Add --clean --if-exists
# 3. Role doesn't exist → Ignore (use --no-owner)

# If needed, drop and recreate database
docker compose exec postgres psql -U sp404_user -d postgres -c "DROP DATABASE IF EXISTS sp404_samples;"
docker compose exec postgres psql -U sp404_user -d postgres -c "CREATE DATABASE sp404_samples OWNER sp404_user;"

# Retry restoration
```

**Validation**:
```bash
# Verify all tables exist
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "\dt" | wc -l
# Should show: 10+ tables

# Check sample count
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM sample;"
# Should match local count

# Verify foreign keys
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM kit_pad WHERE sample_id IS NOT NULL;"
# Should show: samples assigned to pads

# Check indexes
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "\di"
# Should show: indexes on sample, user, etc.
```

### Step 3.5: Optimize Database Performance (1 hour)

**Vacuum and Analyze Database**:
```bash
# Vacuum and analyze all tables
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "VACUUM ANALYZE;"

# Update statistics
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "ANALYZE;"

# Check database size
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT pg_size_pretty(pg_database_size('sp404_samples'));"
# Should show: XX MB
```

**Create Additional Indexes** (if needed):
```bash
# Check existing indexes
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"

# Add indexes for common queries (example)
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "
CREATE INDEX IF NOT EXISTS idx_sample_genre ON sample(genre);
CREATE INDEX IF NOT EXISTS idx_sample_bpm ON sample(bpm);
CREATE INDEX IF NOT EXISTS idx_sample_created_at ON sample(created_at);
"

# Verify new indexes
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "\di idx_sample*"
```

**Configure PostgreSQL Settings**:
```bash
# Edit postgresql.conf (via Docker environment)
# Create custom config file
cat > postgres/postgresql.conf << 'EOF'
# SP-404 Sample Manager PostgreSQL Configuration

# Connection Settings
max_connections = 100
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
work_mem = 10MB

# Query Planning
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_min_duration_statement = 1000  # Log slow queries (>1s)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Autovacuum
autovacuum = on
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
EOF

# Mount config in docker-compose.yml (update)
# Add to postgres volumes:
# - ./postgres/postgresql.conf:/etc/postgresql/postgresql.conf

# Restart PostgreSQL
docker compose restart postgres

# Verify settings
docker compose exec postgres psql -U sp404_user -d sp404_samples -c "SHOW shared_buffers;"
# Should show: 1GB
```

**Validation**:
- ✅ Database vacuumed and analyzed
- ✅ Indexes optimized
- ✅ PostgreSQL tuned for 4GB RAM server
- ✅ Slow query logging enabled

**Time Estimate**: 5 hours (30min + 1hr + 1hr + 1.5hr + 1hr)

---

## TASK 4: Setup Redis Container

**Duration**: 3 hours
**Complexity**: Low
**Prerequisites**: Task 2 complete

### Objective
Deploy Redis 7 container for caching and session management.

### Step 4.1: Start Redis Container (30 min)

```bash
# In /opt/sp404
cd /opt/sp404

# Start Redis
docker compose up -d redis

# Check container status
docker compose ps redis
# Should show: Up (healthy)

# Check logs
docker compose logs redis
# Should show: Ready to accept connections

# Verify healthcheck
docker inspect sp404-redis --format='{{.State.Health.Status}}'
# Should show: healthy
```

**Test Redis Connection**:
```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Test commands
PING
# Should return: PONG

SET test "Hello SP-404"
GET test
# Should return: "Hello SP-404"

DEL test
# Should return: (integer) 1

# Check memory usage
INFO memory
# Should show: used_memory_human

# Exit
QUIT
```

**Validation**:
- ✅ Redis container running
- ✅ Healthcheck passing
- ✅ Commands execute successfully
- ✅ Persistence enabled (appendonly yes)

### Step 4.2: Configure Redis Persistence (1 hour)

**Create Redis Config File**:
```bash
# Create redis.conf
cat > redis/redis.conf << 'EOF'
# SP-404 Sample Manager Redis Configuration

# Network
bind 0.0.0.0
protected-mode yes
port 6379
timeout 300

# Persistence
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Logging
loglevel notice
logfile ""

# Performance
tcp-keepalive 300
tcp-backlog 511
EOF

# Update docker-compose.yml to use config
# Modify redis service:
# command: redis-server /usr/local/etc/redis/redis.conf
# volumes:
#   - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
#   - ./redis/data:/data

# Restart Redis
docker compose restart redis

# Verify config loaded
docker compose exec redis redis-cli CONFIG GET maxmemory
# Should show: 536870912 (512MB in bytes)

docker compose exec redis redis-cli CONFIG GET appendonly
# Should show: yes
```

**Validation**:
```bash
# Check Redis info
docker compose exec redis redis-cli INFO persistence
# Should show: aof_enabled:1

docker compose exec redis redis-cli INFO memory
# Should show: maxmemory:536870912

# Test persistence
docker compose exec redis redis-cli SET persistent_test "data"
docker compose restart redis
docker compose exec redis redis-cli GET persistent_test
# Should still return: "data"
```

### Step 4.3: Setup Redis Backup Script (1 hour)

**Create Backup Script**:
```bash
# Create backup script
cat > /opt/sp404/scripts/backup_redis.sh << 'EOF'
#!/bin/bash

# Redis Backup Script for SP-404
# Saves RDB snapshot and AOF file

set -e

BACKUP_DIR="/opt/sp404/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "Starting Redis backup at $(date)"

# Save Redis snapshot
docker compose exec -T redis redis-cli BGSAVE

# Wait for save to complete
while [ $(docker compose exec -T redis redis-cli LASTSAVE) == $(docker compose exec -T redis redis-cli LASTSAVE) ]; do
    sleep 1
done

# Copy RDB file
docker cp sp404-redis:/data/dump.rdb "$BACKUP_DIR/dump_${DATE}.rdb"

# Copy AOF file
docker cp sp404-redis:/data/appendonly.aof "$BACKUP_DIR/appendonly_${DATE}.aof"

# Compress backups
gzip "$BACKUP_DIR/dump_${DATE}.rdb"
gzip "$BACKUP_DIR/appendonly_${DATE}.aof"

# Remove backups older than 7 days
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete

echo "Redis backup completed at $(date)"
echo "Backup files:"
ls -lh "$BACKUP_DIR" | tail -2
EOF

# Make executable
chmod +x /opt/sp404/scripts/backup_redis.sh

# Test backup script
./scripts/backup_redis.sh

# Verify backups created
ls -lh /opt/sp404/backups/redis/
# Should show: dump_YYYYMMDD_HHMMSS.rdb.gz, appendonly_YYYYMMDD_HHMMSS.aof.gz
```

**Setup Cron Job for Daily Backups**:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/sp404/scripts/backup_redis.sh >> /opt/sp404/logs/redis_backup.log 2>&1

# Verify cron job
crontab -l
# Should show: 0 2 * * * /opt/sp404/scripts/backup_redis.sh
```

**Validation**:
- ✅ Backup script executes successfully
- ✅ RDB and AOF files backed up
- ✅ Backups compressed with gzip
- ✅ Cron job scheduled

### Step 4.4: Test Redis Performance (30 min)

**Run Redis Benchmark**:
```bash
# Test SET operations
docker compose exec redis redis-benchmark -t set -n 100000 -q
# Should show: ~50,000+ requests/sec

# Test GET operations
docker compose exec redis redis-benchmark -t get -n 100000 -q
# Should show: ~80,000+ requests/sec

# Test PING
docker compose exec redis redis-benchmark -t ping -n 100000 -q
# Should show: ~100,000+ requests/sec

# Full benchmark
docker compose exec redis redis-benchmark -q
# Should show results for all operations
```

**Monitor Redis Stats**:
```bash
# Check connected clients
docker compose exec redis redis-cli CLIENT LIST
# Should show: current connections

# Monitor commands in real-time
docker compose exec redis redis-cli MONITOR
# Ctrl+C to stop

# Check slow log
docker compose exec redis redis-cli SLOWLOG GET 10
# Should show: slow commands (if any)
```

**Validation**:
- ✅ Benchmark shows >50K ops/sec for SET
- ✅ No slow commands in log
- ✅ Memory usage within limits

**Time Estimate**: 3 hours (30min + 1hr + 1hr + 30min)

---

## TASK 5: Configure Nginx Reverse Proxy

**Duration**: 5 hours
**Complexity**: Medium
**Prerequisites**: Tasks 1-4 complete

### Objective
Setup Nginx as reverse proxy with SSL/TLS termination, rate limiting, and security headers.

### Step 5.1: Install Nginx (30 min)

```bash
# SSH to VPS
ssh deploy@$VPS_IP

# Install Nginx
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
# Should show: active (running)

# Test Nginx config
sudo nginx -t
# Should show: syntax is ok, test is successful

# Verify Nginx is serving default page
curl http://localhost
# Should return: HTML content
```

**Open Firewall for HTTP/HTTPS**:
```bash
# Firewall should already allow 80/443 from Task 1
sudo ufw status
# Should show: 80/tcp ALLOW, 443/tcp ALLOW

# Test from local machine
curl http://$VPS_IP
# Should return: Welcome to nginx!
```

**Validation**:
- ✅ Nginx installed and running
- ✅ Default page accessible
- ✅ Firewall allows HTTP/HTTPS

### Step 5.2: Configure SSL with Let's Encrypt (1.5 hours)

**Install Certbot**:
```bash
# Install Certbot and Nginx plugin
sudo apt install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
# Should show: certbot 2.x.x
```

**Obtain SSL Certificate**:
```bash
# Replace with your domain
export DOMAIN="sp404.yourdomain.com"

# Run Certbot (interactive)
sudo certbot --nginx -d $DOMAIN

# Answer prompts:
# Email: your-email@example.com (for renewal notices)
# Terms: Agree
# Newsletter: No (optional)
# Redirect HTTP to HTTPS: Yes

# Certbot will:
# 1. Verify domain ownership via HTTP challenge
# 2. Obtain certificate from Let's Encrypt
# 3. Configure Nginx for HTTPS
# 4. Setup auto-renewal

# Verify certificate
sudo certbot certificates
# Should show: Certificate Name: sp404.yourdomain.com
#              Expiry Date: (90 days from now)
```

**Test Auto-Renewal**:
```bash
# Dry-run renewal
sudo certbot renew --dry-run
# Should show: Congratulations, all simulated renewals succeeded

# Check renewal timer
sudo systemctl list-timers
# Should show: certbot.timer active
```

**Validation**:
```bash
# Test HTTPS
curl https://$DOMAIN
# Should return: HTML content (no SSL errors)

# Check SSL certificate
echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates
# Should show: notBefore and notAfter dates

# Test SSL Labs (from local machine)
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN
# Wait 2-3 minutes for scan
# Should achieve: A+ grade
```

### Step 5.3: Configure Nginx for FastAPI Backend (2 hours)

**Create Nginx Config for SP-404**:
```bash
# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Create SP-404 config
sudo vim /etc/nginx/sites-available/sp404

# Add configuration:
```

**Nginx Configuration** (`/etc/nginx/sites-available/sp404`):
```nginx
# SP-404 Sample Manager Nginx Configuration

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

# Upstream backend
upstream sp404_backend {
    server 127.0.0.1:8100 fail_timeout=30s max_fails=3;
    keepalive 32;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name sp404.yourdomain.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name sp404.yourdomain.com;

    # SSL certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/sp404.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sp404.yourdomain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/sp404.yourdomain.com/chain.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/sp404_access.log;
    error_log /var/log/nginx/sp404_error.log warn;

    # Max upload size (for audio samples)
    client_max_body_size 100M;

    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://sp404_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering off;
    }

    # WebSocket endpoints
    location ~ ^/ws/ {
        proxy_pass http://sp404_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Health check (no rate limit)
    location /health {
        proxy_pass http://sp404_backend;
        access_log off;
    }

    # React app static files
    location / {
        root /opt/sp404/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Static assets (images, fonts, etc.)
    location /assets/ {
        root /opt/sp404/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable Site and Test Config**:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sp404 /etc/nginx/sites-enabled/

# Test config
sudo nginx -t
# Should show: syntax is ok, test is successful

# Reload Nginx
sudo systemctl reload nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/sp404_error.log
# Should show: no errors
```

**Validation**:
```bash
# Test HTTP → HTTPS redirect
curl -I http://sp404.yourdomain.com
# Should show: 301 Moved Permanently
#              Location: https://sp404.yourdomain.com

# Test HTTPS (will fail until backend is deployed)
curl -I https://sp404.yourdomain.com
# Should show: 502 Bad Gateway (expected, backend not running yet)

# Test security headers
curl -I https://sp404.yourdomain.com
# Should show:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
```

### Step 5.4: Setup Monitoring and Logging (1 hour)

**Configure Log Rotation**:
```bash
# Create logrotate config
sudo vim /etc/logrotate.d/sp404

# Add configuration:
/var/log/nginx/sp404_*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}

# Test logrotate
sudo logrotate -d /etc/logrotate.d/sp404
# Should show: rotation schedule
```

**Install Fail2Ban for Nginx**:
```bash
# Create Nginx filter
sudo vim /etc/fail2ban/filter.d/nginx-sp404.conf

# Add filter:
[Definition]
failregex = ^<HOST> .* "(GET|POST|HEAD).*" (4\d\d|5\d\d)
ignoreregex =

# Create jail
sudo vim /etc/fail2ban/jail.d/nginx-sp404.conf

# Add jail:
[nginx-sp404]
enabled = true
port = http,https
filter = nginx-sp404
logpath = /var/log/nginx/sp404_access.log
maxretry = 10
findtime = 600
bantime = 3600

# Restart Fail2Ban
sudo systemctl restart fail2ban

# Check status
sudo fail2ban-client status nginx-sp404
# Should show: Currently banned: 0
```

**Validation**:
- ✅ Logrotate configured
- ✅ Fail2Ban protecting Nginx
- ✅ Logs rotating daily

**Time Estimate**: 5 hours (30min + 1.5hr + 2hr + 1hr)

---

## DELIVERABLES CHECKLIST

### Task 1: Prepare Vultr VPS
- [ ] VPS provisioned (4GB RAM, 2 vCPUs)
- [ ] SSH key authentication working
- [ ] Deploy user created with sudo access
- [ ] UFW firewall configured and active
- [ ] Fail2Ban protecting SSH
- [ ] DNS A/AAAA records pointing to VPS
- [ ] Automatic security updates enabled

### Task 2: Install Docker
- [ ] Docker Engine installed (v27+)
- [ ] Docker Compose plugin installed (v2+)
- [ ] Deploy user in docker group
- [ ] Docker daemon configured (log limits, overlay2)
- [ ] Custom sp404-network created
- [ ] docker-compose.yml created

### Task 3: Setup PostgreSQL
- [ ] PostgreSQL 16 container running
- [ ] Database restored from local backup
- [ ] 2,328+ samples in database
- [ ] Healthcheck passing
- [ ] Database optimized (vacuum, analyze)
- [ ] Performance tuning applied

### Task 4: Setup Redis
- [ ] Redis 7 container running
- [ ] Persistence enabled (AOF)
- [ ] Memory limit set (512MB)
- [ ] Healthcheck passing
- [ ] Backup script created and scheduled
- [ ] Performance benchmark passed

### Task 5: Configure Nginx
- [ ] Nginx installed and running
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Auto-renewal configured
- [ ] Reverse proxy configured for API
- [ ] WebSocket support enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Fail2Ban protecting Nginx

---

## VALIDATION GATES

Before marking Week 1 complete, verify:

### Infrastructure
- ✅ VPS accessible via SSH (deploy user)
- ✅ Firewall active and ports configured
- ✅ Docker and Docker Compose installed
- ✅ PostgreSQL container healthy
- ✅ Redis container healthy
- ✅ Nginx serving HTTPS with valid cert

### Security
- ✅ Root SSH login disabled
- ✅ SSH key authentication only
- ✅ UFW firewall active
- ✅ Fail2Ban protecting SSH and Nginx
- ✅ SSL certificate valid (A+ grade)
- ✅ Security headers configured

### Database
- ✅ PostgreSQL 16 running
- ✅ Sample database restored (2,328+ samples)
- ✅ Database queries execute successfully
- ✅ Backups scheduled

### Performance
- ✅ PostgreSQL tuned for 4GB RAM
- ✅ Redis benchmark >50K ops/sec
- ✅ Nginx response time <200ms
- ✅ SSL handshake <100ms

### Monitoring
- ✅ Log rotation configured
- ✅ Fail2Ban banning IPs
- ✅ Healthchecks passing
- ✅ Resource usage monitored

---

## TIME TRACKING

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| Task 1: VPS Setup | 4 hrs | | |
| Task 2: Docker | 3 hrs | | |
| Task 3: PostgreSQL | 5 hrs | | |
| Task 4: Redis | 3 hrs | | |
| Task 5: Nginx | 5 hrs | | |
| **Total** | **20 hrs** | | |

**Note**: 20 hours estimated, but allocated 30 hours (6 hrs/day × 5 days) to account for unexpected issues.

---

## TROUBLESHOOTING

### Cannot SSH to VPS
**Issue**: Connection refused or timeout
**Solution**:
1. Check VPS is running in Vultr dashboard
2. Verify IP address is correct
3. Check firewall allows SSH: `sudo ufw status`
4. Check SSH service: `sudo systemctl status ssh`

### Docker Containers Won't Start
**Issue**: Container exits immediately
**Solution**:
1. Check logs: `docker compose logs postgres`
2. Verify environment variables: `cat .env`
3. Check port conflicts: `sudo netstat -tlnp | grep 5432`
4. Increase resources in docker-compose.yml

### Database Restore Fails
**Issue**: pg_restore errors
**Solution**:
1. Add `--no-owner --no-acl` flags
2. Drop and recreate database
3. Check backup file integrity: `pg_restore --list backup.backup`

### SSL Certificate Fails
**Issue**: Certbot cannot verify domain
**Solution**:
1. Verify DNS: `dig sp404.yourdomain.com`
2. Check firewall allows 80: `sudo ufw allow 80`
3. Stop Nginx: `sudo systemctl stop nginx`
4. Retry Certbot: `sudo certbot certonly --standalone -d sp404.yourdomain.com`

### Nginx 502 Bad Gateway
**Issue**: Nginx cannot reach backend
**Solution**:
1. Check backend is running: `curl http://localhost:8100/health`
2. Verify upstream in Nginx config
3. Check Nginx logs: `sudo tail -f /var/log/nginx/sp404_error.log`

---

## NEXT STEPS (Week 2)

After Week 1 completion:
1. Deploy FastAPI backend container
2. Setup CI/CD with GitHub Actions
3. Configure monitoring (Prometheus + Grafana)
4. Deploy Laravel 11 for auth/billing
5. Setup automated database backups
6. Implement blue-green deployment

**Track A Integration**: Deploy React build from Track A to `/opt/sp404/frontend/dist`.
