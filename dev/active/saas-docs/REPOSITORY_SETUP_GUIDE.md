# SP404-SaaS Repository Setup Guide

**Target Time:** 30 minutes from zero to running development environment
**Requirements:** Docker Desktop, Git, Node.js 20+, PHP 8.2+, Composer

---

## Prerequisites

### Required Software
```bash
# Verify installations
docker --version          # >= 24.0.0
docker-compose --version  # >= 2.20.0
git --version            # >= 2.40.0
node --version           # >= 20.0.0
php --version            # >= 8.2.0
composer --version       # >= 2.6.0
```

### Required Accounts
- GitHub account with repository access
- Stripe account (test mode keys)
- Cloudflare account with Workers enabled
- OpenRouter API key (for AI features)

---

## Step 1: Clone Repository with Submodule

```bash
# Clone the SaaS repository with the open-source submodule
git clone --recursive git@github.com:yourusername/sp404-saas.git
cd sp404-saas

# Verify submodule was cloned
ls -la open-source/backend  # Should show FastAPI files

# If submodule is empty (forgot --recursive), initialize it:
git submodule update --init --recursive
```

---

## Step 2: Environment Configuration

### Copy Environment Templates
```bash
# Root environment (shared settings)
cp .env.example .env

# Laravel backend environment
cp saas-backend/.env.example saas-backend/.env

# Open-source backend environment
cp open-source/.env.example open-source/.env

# Cloudflare Workers environment
cp cloudflare-workers/.dev.vars.example cloudflare-workers/.dev.vars
```

### Configure `.env` (Root)
```bash
# Edit .env with your preferred editor
vim .env
```

**Required Variables:**
```env
# Application
APP_ENV=local
APP_URL=http://localhost:3000

# Database (PostgreSQL via Docker)
DB_CONNECTION=pgsql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=sp404_saas
DB_USERNAME=sp404_user
DB_PASSWORD=changeme123

# Redis (via Docker)
REDIS_HOST=localhost
REDIS_PORT=6379

# Stripe (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# JWT
JWT_SECRET=generate_random_32_char_string_here

# Cloudflare (get from Workers dashboard)
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
```

---

## Step 3: Install Dependencies

### Install All Dependencies (Single Command)
```bash
make install-all
```

This runs:
1. `composer install` in `saas-backend/`
2. `npm install` in `saas-frontend/`
3. `npm install` in `cloudflare-workers/`
4. `pip install -r requirements.txt` in `open-source/backend/`

---

## Step 4: Start Infrastructure Services

### Start Docker Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# sp404-postgres      Up 10 seconds      0.0.0.0:5432->5432/tcp
# sp404-redis         Up 10 seconds      0.0.0.0:6379->6379/tcp
```

### Initialize Databases
```bash
# Run Laravel migrations (creates SaaS tables)
cd saas-backend
php artisan migrate
cd ..

# Run FastAPI database init (creates open-source tables)
cd open-source
./venv/bin/python -m backend.app.db.init_db
cd ..
```

---

## Step 5: Start Development Servers

### Option A: Start All Services (Makefile)
```bash
make dev
```

This starts all services automatically.

### Option B: Start Services Manually (Separate Terminals)

**Terminal 1: Laravel Backend**
```bash
cd saas-backend
php artisan serve --port=8000
```

**Terminal 2: FastAPI Backend**
```bash
cd open-source
./venv/bin/python backend/run.py
```

**Terminal 3: React Frontend**
```bash
cd saas-frontend
npm run dev
```

---

## Step 6: Verify Setup

### Check Service Health
```bash
# Laravel health check
curl http://localhost:8000/health

# FastAPI health check
curl http://localhost:8100/health

# React dev server
curl http://localhost:3000
```

### Access Web UI
```bash
# Open SaaS UI in browser
open http://localhost:3000

# Test login flow
```

---

## Step 7: Common Development Tasks

### Update Open-Source Submodule
```bash
# Navigate to submodule
cd open-source

# Pull latest changes
git checkout main
git pull origin main

# Return to root and commit submodule update
cd ..
git add open-source
git commit -m "chore: update open-source to latest"
```

### View Logs
```bash
# Laravel logs
tail -f saas-backend/storage/logs/laravel.log

# Docker logs
docker-compose logs -f postgres
```

### Reset Databases
```bash
# Reset Laravel database
cd saas-backend
php artisan migrate:fresh --seed
cd ..

# Reset FastAPI database
cd open-source
./venv/bin/python -m backend.app.db.init_db --reset
cd ..
```

---

## Troubleshooting

### Issue: Submodule is empty
```bash
git submodule update --init --recursive
```

### Issue: Database connection refused
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Issue: Laravel APP_KEY not set
```bash
cd saas-backend
php artisan key:generate
```

### Issue: Port already in use
```bash
# Find process using port
lsof -i :8000  # Replace with your port

# Kill process
kill -9 <PID>
```

---

## Time Checkpoint

**Expected Total Time:** 25-30 minutes

Breakdown:
- Clone and submodule setup: 3 min
- Environment configuration: 5 min
- Install dependencies: 8 min
- Start services and initialize DBs: 5 min
- Verification: 4 min

**✅ If you reached this point in <30 minutes, setup is complete!**
