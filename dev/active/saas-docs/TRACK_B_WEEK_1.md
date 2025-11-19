# Track B - Week 1: Infrastructure Setup

**Developer Role:** DevOps/Infrastructure specialist
**Total Hours:** 30 hours (6 hours/day × 5 days)
**Tech Stack:** Vultr VPS, Docker, PostgreSQL 16, Redis 7, Nginx, Let's Encrypt

---

## Task 1: Prepare Vultr VPS (4 hours)
**Monday Morning**

### Objectives
- Provision production-ready VPS
- Configure SSH access and security
- Setup domain DNS
- Enable auto-updates

### Step 1: Provision VPS

1. **Create Vultr Account** (if needed)
   - Go to https://www.vultr.com
   - Verify email
   - Add payment method

2. **Deploy Instance**
   - Product: Cloud Compute
   - Server Type: Regular Performance
   - Location: Closest to your users (e.g., US East)
   - OS: Ubuntu 22.04 LTS
   - Size: 2 vCPU, 4GB RAM, 80GB SSD (~$12/month)
   - Click "Deploy Now"
   - Wait 2-3 minutes for server to boot

3. **Get Credentials**
   - Check email for root password
   - Note IP address (e.g., 203.0.113.45)

### Step 2: Initial Server Setup

```bash
# 1. SSH into server as root
ssh root@YOUR_VPS_IP
# Enter password from email

# 2. Update system
apt-get update && apt-get upgrade -y

# 3. Create non-root user
useradd -m -s /bin/bash deploy
usermod -aG sudo deploy

# 4. Set password
passwd deploy
# Enter strong password twice

# 5. Setup SSH keys (on YOUR LOCAL MACHINE)
ssh-copy-id -i ~/.ssh/id_rsa.pub deploy@YOUR_VPS_IP
# Enter deploy password

# 6. Login as deploy user
ssh deploy@YOUR_VPS_IP
# Should login without password

# 7. Disable root login
sudo nano /etc/ssh/sshd_config
# Change:
#   PermitRootLogin no
#   PasswordAuthentication no
# Press Ctrl+X, then Y, Enter to save

sudo systemctl restart ssh
```

### Step 3: Configure Firewall

```bash
# 1. Enable UFW firewall
sudo ufw enable

# 2. Allow SSH (CRITICAL - do this first!)
sudo ufw allow 22/tcp

# 3. Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 4. Check rules
sudo ufw status
# Expected output:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

### Step 4: Setup Domain DNS

1. **Point Domain**
   - Go to your domain registrar (Namecheap, GoDaddy, etc.)
   - Add A record: `api.yourdomain.com` → `YOUR_VPS_IP`
   - Wait 5-10 minutes for DNS propagation

2. **Verify DNS**
   ```bash
   nslookup api.yourdomain.com
   # Should return YOUR_VPS_IP
   ```

### Step 5: Enable Auto-Updates

```bash
# 1. Install unattended-upgrades
sudo apt-get install -y unattended-upgrades

# 2. Enable automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades

# 3. Verify
sudo systemctl status unattended-upgrades
# Should show: active (running)
```

### Validation Checklist
- ✅ VPS accessible via SSH as deploy user
- ✅ Root login disabled
- ✅ Firewall enabled (22, 80, 443 open)
- ✅ Domain points to VPS IP
- ✅ Auto-updates enabled

### Expected Deliverable
- Production VPS ready with security hardened
- SSH access working
- Domain DNS configured

---

## Task 2: Install Docker and Docker Compose (3 hours)
**Monday Afternoon**

### Objectives
- Install Docker Engine
- Install Docker Compose
- Configure permissions
- Test installation

### Step 1: Install Docker Engine

```bash
# 1. Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. Add Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. Setup Docker repository
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 5. Verify installation
docker --version
# Expected: Docker version 27.x.x
```

### Step 2: Install Docker Compose

```bash
# 1. Download latest Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 2. Make executable
sudo chmod +x /usr/local/bin/docker-compose

# 3. Verify
docker-compose --version
# Expected: Docker Compose version 2.x.x
```

### Step 3: Configure Docker Daemon

```bash
# 1. Create daemon config
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
EOF

# 2. Reload Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 3. Add deploy user to docker group (logout/login required)
sudo usermod -aG docker deploy

# 4. Verify (logout and login first)
docker ps
# Should return: CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS
```

### Validation Checklist
- ✅ Docker Engine running
- ✅ Docker Compose installed
- ✅ deploy user can run docker commands
- ✅ Log rotation configured
- ✅ Daemon restart policy enabled

### Expected Deliverable
- Docker ready for production use
- Deployment permissions configured

---

## Task 3: Setup PostgreSQL Container (5 hours)
**Tuesday Morning**

### Objectives
- Create PostgreSQL 16 Docker container
- Restore 2,328 sample records from backup
- Configure replication and backups
- Optimize for performance

### Step 1: Create Docker Compose

Create `docker-compose.yml` on VPS:
```bash
# Create app directory
mkdir -p ~/sp404-saas
cd ~/sp404-saas

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: sp404_postgres
    environment:
      POSTGRES_DB: sp404_samples
      POSTGRES_USER: sp404_user
      POSTGRES_PASSWORD: STRONG_PASSWORD_HERE
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups:ro
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sp404_user -d sp404_samples"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - sp404_network

  redis:
    image: redis:7-alpine
    container_name: sp404_redis
    command: redis-server --appendonly yes --maxmemory 512m --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - sp404_network

volumes:
  postgres_data:
  redis_data:

networks:
  sp404_network:
    driver: bridge
EOF
```

### Step 2: Start PostgreSQL

```bash
# 1. Start containers
docker-compose up -d

# 2. Wait for healthy status
sleep 10
docker-compose ps

# 3. Verify database is ready
docker-compose exec postgres pg_isready -U sp404_user -d sp404_samples
# Expected: accepting connections
```

### Step 3: Restore Sample Data

```bash
# 1. Copy backup file to VPS (from your local machine)
scp /path/to/sp404_samples_backup.sql deploy@YOUR_VPS_IP:~/sp404-saas/backups/

# 2. Connect to database
docker-compose exec postgres psql -U sp404_user -d sp404_samples

# 3. In psql prompt, check existing tables:
\dt
# Note what tables exist

# 4. Exit psql
\q

# 5. Restore from backup
docker-compose exec -T postgres pg_restore \
  --no-owner --no-acl \
  -U sp404_user \
  -d sp404_samples \
  /backups/sp404_samples_backup.sql

# 6. Verify restore
docker-compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM samples;"
# Expected: 2328

docker-compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM collections;"
# Expected: Count of collections
```

### Step 4: Optimize PostgreSQL

```bash
# 1. Connect to PostgreSQL
docker-compose exec postgres psql -U sp404_user -d sp404_samples

# 2. Run ANALYZE to update stats
ANALYZE;

# 3. Check indexes
\d samples
# Should show indexes for frequently queried columns

# 4. Exit
\q

# 5. Create additional indexes if needed (for vibe search, etc.)
docker-compose exec postgres psql -U sp404_user -d sp404_samples -c "
CREATE INDEX IF NOT EXISTS idx_samples_user_id ON samples(user_id);
CREATE INDEX IF NOT EXISTS idx_samples_created_at ON samples(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_samples_bpm ON samples(bpm);
"
```

### Validation Checklist
- ✅ PostgreSQL container running and healthy
- ✅ Sample data restored (2,328 samples)
- ✅ Tables and indexes present
- ✅ Database accessible from command line
- ✅ Performance optimized (ANALYZE complete)
- ✅ Backups directory ready

### Expected Deliverable
- PostgreSQL 16 running with sample data
- Database optimized and indexed

---

## Task 4: Setup Redis Container (3 hours)
**Tuesday Afternoon**

### Objectives
- Redis container configured
- Persistence enabled
- Backup strategy implemented
- Performance tuning done

### Already Running from Task 3

Redis was started in `docker-compose.yml`. Verify:

```bash
# 1. Check Redis is running
docker-compose ps redis
# Expected: sp404_redis   redis:7-alpine   Up 10 seconds

# 2. Test Redis connection
docker-compose exec redis redis-cli ping
# Expected: PONG

# 3. Check memory configuration
docker-compose exec redis redis-cli CONFIG GET maxmemory
# Expected: 512m

# 4. Check persistence
docker-compose exec redis redis-cli CONFIG GET appendonly
# Expected: yes
```

### Backup Strategy

```bash
# 1. Create backup script
cat > ~/sp404-saas/backup_redis.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/sp404-saas/backups
mkdir -p $BACKUP_DIR

# Backup Redis
docker-compose exec -T redis redis-cli BGSAVE

sleep 2

# Copy dump file
docker cp sp404_redis:/data/dump.rdb $BACKUP_DIR/redis_dump_$(date +%Y%m%d_%H%M%S).rdb

# Keep only last 7 days
find $BACKUP_DIR -name "redis_dump_*.rdb" -mtime +7 -delete

echo "Redis backup complete"
EOF

chmod +x ~/sp404-saas/backup_redis.sh

# 2. Schedule daily backups (7 AM)
crontab -e
# Add: 0 7 * * * ~/sp404-saas/backup_redis.sh
```

### Validation Checklist
- ✅ Redis container running
- ✅ Persistence (AOF) enabled
- ✅ Memory limit set to 512MB
- ✅ Eviction policy: allkeys-lru
- ✅ Backup script created
- ✅ Cron job scheduled

### Expected Deliverable
- Redis running with persistence
- Daily backups configured

---

## Task 5: Configure Nginx Reverse Proxy (5 hours)
**Wednesday → Thursday Morning**

### Objectives
- Setup Nginx reverse proxy
- Configure SSL with Let's Encrypt
- Setup rate limiting
- Enable security headers

### Step 1: Install Nginx

```bash
# 1. Install Nginx and Certbot
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Stop default Nginx (for now)
sudo systemctl stop nginx

# 3. Create config directory
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
```

### Step 2: Create Nginx Configuration

```bash
# 1. Create sp404 site config
sudo tee /etc/nginx/sites-available/sp404 > /dev/null << 'EOF'
upstream laravel {
    server 127.0.0.1:8000;
}

upstream fastapi {
    server 127.0.0.1:8100;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (will be created by Certbot)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    client_max_body_size 500M;

    # Logging
    access_log /var/log/nginx/sp404_access.log;
    error_log /var/log/nginx/sp404_error.log;

    # Laravel backend
    location ~ ^/api/(auth|billing|admin) {
        limit_req zone=api_limit burst=5 nodelay;

        proxy_pass http://laravel;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # FastAPI backend
    location ~ ^/api/v1 {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://fastapi;
    }

    # Default deny
    location / {
        return 404;
    }
}
EOF

# 2. Enable site
sudo ln -s /etc/nginx/sites-available/sp404 /etc/nginx/sites-enabled/

# 3. Test config
sudo nginx -t
# Expected: syntax is ok, test is successful
```

### Step 3: Get SSL Certificate

```bash
# 1. Restart Nginx (temporarily)
sudo systemctl restart nginx

# 2. Get Let's Encrypt certificate
sudo certbot certonly --nginx -d api.yourdomain.com --email your@email.com --agree-tos

# 3. Verify certificate
sudo certbot status
# Expected: 1 certificate found

# 4. Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# 5. Test renewal
sudo certbot renew --dry-run
# Expected: The following certs would be renewed
```

### Step 4: Start and Verify

```bash
# 1. Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 2. Check status
sudo systemctl status nginx
# Expected: active (running)

# 3. Test with curl
curl -I https://api.yourdomain.com/health
# Expected: HTTP/2 200

# 4. Check SSL grade
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=api.yourdomain.com
# Expected: A+ grade
```

### Validation Checklist
- ✅ Nginx running and enabled
- ✅ HTTP redirects to HTTPS
- ✅ SSL certificate issued and valid
- ✅ SSL grade: A+
- ✅ Rate limiting enabled
- ✅ Security headers present
- ✅ WebSocket support working
- ✅ Logs configured

### Expected Deliverable
- Nginx reverse proxy running
- SSL/HTTPS configured with A+ grade
- Rate limiting and security headers in place

---

## Daily Deliverables

| Day | Task | Deliverable |
|-----|------|------------|
| Mon | Task 1 | VPS provisioned, secured, DNS configured |
| Mon | Task 2 | Docker ready, permissions configured |
| Tue | Task 3 | PostgreSQL 16 running with 2,328 samples |
| Tue | Task 4 | Redis running with persistence |
| Wed-Thu | Task 5 | Nginx proxy live, HTTPS enabled, A+ SSL |

---

## Integration with Track A

### Wednesday 12:00 PM
- You confirm backend health check
- Track A tests CORS with your VPS

### Thursday 3:00 PM
- You have Nginx redirecting API calls
- Track A creates React API client

### Friday 3:00 PM
- You deploy Laravel + FastAPI containers
- Track A deploys React build
- Full system live

---

## Success Criteria for Week 1

- ✅ Vultr VPS secured and hardened
- ✅ Docker + Docker Compose installed
- ✅ PostgreSQL 16 running with sample data
- ✅ Redis 7 running with persistence
- ✅ Nginx reverse proxy active
- ✅ HTTPS with A+ SSL grade
- ✅ Rate limiting configured
- ✅ Automated backups scheduled
- ✅ All health checks passing
- ✅ Ready for Week 2 deployments

---

## Resources

- Vultr Documentation: https://www.vultr.com/docs/
- Docker Documentation: https://docs.docker.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Nginx Documentation: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/
