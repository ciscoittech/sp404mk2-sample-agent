# SP404-SaaS Repository Structure

**Last Updated:** 2025-11-18
**Purpose:** Commercial SaaS wrapper around open-source sp404mk2-sample-agent
**License:** Proprietary (Private Repository)

---

## Overview

This repository contains the commercial SaaS layer that wraps the open-source sp404mk2-sample-agent. The architecture uses Git submodules to maintain a clear boundary between open-source features and commercial enhancements.

---

## Directory Structure

```
sp404-saas/
├── open-source/                    # Git submodule pointing to sp404mk2-sample-agent
│   ├── backend/                    # Open-source FastAPI backend
│   ├── react-app/                  # Open-source React 19 frontend
│   ├── src/                        # Open-source CLI tools
│   └── docs/                       # Open-source documentation
│
├── saas-backend/                   # Commercial Laravel backend (NEW)
│   ├── app/
│   │   ├── Http/
│   │   │   ├── Controllers/
│   │   │   │   ├── Auth/          # Laravel Breeze auth controllers
│   │   │   │   ├── Billing/       # Stripe subscription management
│   │   │   │   └── Admin/         # Admin panel controllers
│   │   │   └── Middleware/
│   │   │       ├── CheckSubscription.php  # Subscription validation
│   │   │       ├── EnforceQuotas.php      # API quota enforcement
│   │   │       └── TrackUsage.php         # Usage analytics tracking
│   │   ├── Models/
│   │   │   ├── User.php           # Laravel user model (extends open-source)
│   │   │   ├── Subscription.php   # Stripe subscription model
│   │   │   ├── Usage.php          # API usage tracking
│   │   │   └── Team.php           # Multi-tenant teams
│   │   ├── Services/
│   │   │   ├── StripeService.php  # Payment processing
│   │   │   ├── QuotaService.php   # Quota management
│   │   │   └── ProxyService.php   # FastAPI backend proxy
│   │   └── Policies/
│   │       └── SamplePolicy.php   # Authorization rules
│   ├── database/
│   │   ├── migrations/            # Laravel migrations for SaaS tables
│   │   └── seeders/               # Test data for development
│   ├── routes/
│   │   ├── web.php                # Laravel web routes
│   │   ├── api.php                # Laravel API routes (auth/billing)
│   │   └── admin.php              # Admin panel routes
│   ├── config/
│   │   ├── services.php           # Stripe, Cloudflare config
│   │   └── quotas.php             # Plan quotas configuration
│   ├── tests/
│   │   ├── Feature/               # Laravel feature tests
│   │   └── Unit/                  # Laravel unit tests
│   └── artisan                    # Laravel CLI
│
├── cloudflare-workers/             # Cloudflare Workers API Gateway (NEW)
│   ├── src/
│   │   ├── index.ts               # Main worker entry point
│   │   ├── middleware/
│   │   │   ├── auth.ts            # JWT validation
│   │   │   ├── rateLimit.ts       # Rate limiting (KV store)
│   │   │   └── cors.ts            # CORS handling
│   │   ├── routes/
│   │   │   ├── proxy.ts           # Proxy to FastAPI backend
│   │   │   └── health.ts          # Health check endpoint
│   │   └── utils/
│   │       ├── quotas.ts          # Quota checking (KV store)
│   │       └── analytics.ts       # Usage analytics (Workers Analytics)
│   ├── wrangler.toml              # Cloudflare deployment config
│   ├── package.json
│   └── tsconfig.json
│
├── deployment/                     # Vultr VPS deployment configuration (NEW)
│   ├── docker/
│   │   ├── docker-compose.prod.yml     # Production compose file
│   │   ├── Dockerfile.laravel          # Laravel container
│   │   └── Dockerfile.fastapi          # FastAPI container (extends open-source)
│   ├── nginx/
│   │   ├── nginx.conf                  # Nginx configuration
│   │   ├── sites/
│   │   │   ├── laravel.conf            # Laravel vhost
│   │   │   └── fastapi.conf            # FastAPI vhost
│   │   └── ssl/                        # SSL certificates (Let's Encrypt)
│   ├── scripts/
│   │   ├── deploy.sh                   # Deployment automation
│   │   ├── backup.sh                   # Database backup script
│   │   ├── restore.sh                  # Database restore script
│   │   └── health-check.sh             # System health monitoring
│   ├── ansible/                        # Infrastructure as Code (optional)
│   │   ├── playbook.yml
│   │   └── inventory.yml
│   └── monitoring/
│       ├── prometheus.yml              # Metrics collection
│       └── grafana-dashboard.json      # Monitoring dashboard
│
├── saas-frontend/                  # Commercial frontend extensions (NEW)
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/              # Login/register components
│   │   │   ├── billing/           # Subscription management UI
│   │   │   ├── admin/             # Admin dashboard
│   │   │   └── teams/             # Team management
│   │   ├── pages/
│   │   │   ├── SubscriptionPage.tsx
│   │   │   ├── TeamSettingsPage.tsx
│   │   │   └── AdminDashboard.tsx
│   │   ├── api/
│   │   │   ├── auth.ts            # Auth API client
│   │   │   └── billing.ts         # Billing API client
│   │   └── hooks/
│   │       ├── useSubscription.ts
│   │       └── useQuotas.ts
│   ├── package.json
│   └── vite.config.ts
│
├── shared/                         # Shared configuration and types
│   ├── types/
│   │   ├── user.ts                # Shared user types
│   │   ├── subscription.ts        # Subscription types
│   │   └── quotas.ts              # Quota types
│   └── config/
│       └── plans.json             # Subscription plans configuration
│
├── docs/                           # SaaS-specific documentation
│   ├── ARCHITECTURE.md            # System architecture overview
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── API_GATEWAY.md             # Cloudflare Workers documentation
│   ├── BILLING.md                 # Stripe integration guide
│   └── SECURITY.md                # Security practices
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore (excludes secrets)
├── .gitmodules                     # Submodule configuration
├── docker-compose.yml              # Local development compose file
├── Makefile                        # Common commands
└── README.md                       # Repository overview
```

---

## Build Process Flow

### Local Development

```
Clone repo with submodules → Install dependencies → Start services → Development ready
                                        ↓
                    Laravel composer install
                    React npm install
                    Cloudflare npm install
                    Open-source setup
```

**Commands:**
```bash
# 1. Clone with submodules
git clone --recursive git@github.com:yourusername/sp404-saas.git

# 2. Install all dependencies
make install-all

# 3. Start local development
make dev

# 4. Access services
# - React SaaS UI: http://localhost:3000
# - Laravel API: http://localhost:8000
# - FastAPI (open-source): http://localhost:8100
# - Cloudflare Workers (local): http://localhost:8787
```

---

## Component Integration

### Request Flow (Production)

```
User Browser
    ↓
Cloudflare Workers (API Gateway)
    ├─ Auth check (JWT)
    ├─ Rate limiting (KV)
    ├─ Quota enforcement
    └─ Route to backend
        ↓
    Laravel Backend (saas-backend)
        ├─ /api/auth/* → Authentication
        ├─ /api/billing/* → Stripe integration
        ├─ /api/admin/* → Admin functions
        └─ /api/proxy/* → Proxy to FastAPI
            ↓
        FastAPI Backend (open-source/backend)
            ├─ /api/v1/samples → Sample management
            ├─ /api/v1/batch → Batch processing
            ├─ /api/v1/projects → Project builder
            └─ /api/v1/collections → Collections
```

---

## Validation

**Validation Gates:**
- ✅ Directory structure is clear and logical
- ✅ Git submodule integration is explained correctly
- ✅ No sensitive files are in wrong locations
- ✅ Build/deployment process is achievable in Docker
- ✅ Developer could follow setup guide without outside help
- ✅ Feature split is unambiguous
