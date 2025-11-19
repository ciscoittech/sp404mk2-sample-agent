# Architecture Documentation: Laravel + FastAPI + React Integration

**Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Design Complete

---

## 1. System Architecture Overview

### 1.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              INTERNET (Global Users)                            │
│                                                                 │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloudflare Global Network                    │
│  - DDoS Protection, SSL/TLS, WAF                               │
│  - Cache Rules, Workers Edge Logic                            │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
        ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
        │  Pages (React)  │  │  R2 Storage  │  │  Workers     │
        │  Frontend       │  │  File Uploads│  │  API Gateway │
        │  https://...    │  │              │  │  Routes      │
        └─────────────────┘  └──────────────┘  └──────┬───────┘
                                                       │
                    ┌──────────────────────────────────┼──────────────────────────────┐
                    │                                  │                              │
                    ▼                                  ▼                              ▼
        ┌────────────────────────┐      ┌────────────────────────┐      ┌─────────────────────┐
        │   Laravel 11 API       │      │   FastAPI Processing   │      │  Shared Services    │
        │   (Railway)            │      │   (Railway)            │      │                     │
        │                        │      │                        │      │ ├─ PostgreSQL       │
        │ ├─ Auth (Fortify)      │      │ ├─ Audio Analysis      │      │ ├─ Redis (Queue)    │
        │ ├─ JWT (RS256)         │      │ ├─ AI Analysis         │      │ └─ Monitoring       │
        │ ├─ Stripe Cashier      │      │ ├─ Sample CRUD         │      └─────────────────────┘
        │ ├─ Subscriptions       │      │ ├─ Collections         │
        │ ├─ Billing             │      │ ├─ Similarity Search   │
        │ ├─ User Management     │      │ └─ Export (SP-404)     │
        │ └─ Queue Management    │      │                        │
        │                        │      │                        │
        │ Port: 8000            │      │ Port: 8100            │
        └────────────────────────┘      └────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibilities | Does NOT Handle |
|-----------|------------------|-----------------|
| **React Frontend** | UI rendering, form handling, client-side routing | Server logic, authentication validation |
| **Cloudflare Workers** | JWT validation, routing to correct backend, rate limiting | Business logic, database access |
| **Laravel** | User auth, billing, subscriptions, email | Audio processing, file storage, AI analysis |
| **FastAPI** | Audio processing, AI analysis, sample management | User management, billing, authentication |
| **PostgreSQL** | Data persistence across all services | Application logic |
| **Redis** | Session storage, queue jobs, caching | Data at rest |

---

## 2. Data Flow Architecture

### 2.1 Authentication Flow

```
React Client
    │
    ├─────────────────────────────────────────────────────┐
    │                                                     │
    ▼                                                     │
┌─────────────────┐                                      │
│ Login Page      │                                      │
│ email, password │                                      │
└────────┬────────┘                                      │
         │                                               │
         └─────► POST /api/auth/login ───────────────┐  │
                                                      │  │
                                     Cloudflare Workers  │
                                     ├─ No JWT yet      │
                                     ├─ Pass through    │
                                     │                  │
                                     ▼                  │
                                Laravel API             │
                                ├─ Validate email/pass  │
                                ├─ Generate JWT (RS256) │
                                │                       │
                                ▼                       │
                            ┌─────────────────┐        │
                            │ JWT Token       │        │
                            │ + User Info     │        │
                            └─────────────────┘        │
                                │                      │
                                └────────────────────┐ │
                                                    │ │
                                     ◄──────────────┘ │
                                                      │
React Store (Redux/Zustand)                          │
├─ Save JWT to localStorage ◄───────────────────────┘
├─ Set auth state: authenticated
└─ Trigger redirect to /samples
```

### 2.2 API Request Flow

```
React Component
    │
    ├─ GET /api/samples (with Bearer token)
    │
    ▼
Local Storage
├─ Retrieve JWT token
│
▼
HTTP Headers
├─ Authorization: Bearer eyJhbGci...
├─ Content-Type: application/json
│
▼
Cloudflare Workers
├─ Extract token from Authorization header
├─ Verify JWT signature (RS256 public key)
├─ Decode token and extract: user_id, email, tier
├─ Check blacklist (token revoked?)
├─ Add headers:
│   ├─ X-User-ID: uuid
│   └─ X-User-Tier: pro
│
├─ Route decision:
│   ├─ /api/samples/* ──► FastAPI
│   ├─ /api/billing/* ──► Laravel
│   └─ /api/auth/* ──► Laravel
│
▼
FastAPI (if samples route)
├─ Extract user_id from X-User-ID header
├─ Query: SELECT * FROM samples WHERE user_id = ?
├─ Return only user's samples
│
▼
Response JSON
├─ Samples array (filtered by user)
├─ Total count
│
▼
React Component
├─ Parse response
├─ Update state
├─ Re-render UI
```

### 2.3 Subscription/Billing Flow

```
User clicks "Upgrade to Pro"
    │
    ▼
React opens Plan Selector
    │
    ├─ Display price ($29/month)
    ├─ Trial: 14 days
    │
    ▼
User clicks "Subscribe"
    │
    ▼
POST /api/billing/subscribe
    │
    ├─ Auth header: JWT token
    ├─ Body: { plan_id: 'pro' }
    │
    ▼
Cloudflare Workers
├─ Validate JWT (user_id = uuid)
├─ Route to Laravel with X-User-ID header
    │
    ▼
Laravel Billing Controller
├─ Get current user (from database, verified by user_id)
├─ Check if already subscribed
├─ Create Stripe subscription
│   ├─ Create customer in Stripe
│   ├─ Create subscription with price_id
│   ├─ Set trial for 14 days
    │
    ▼
Stripe API Response
├─ subscription_id
├─ client_secret (for 3D Secure if needed)
├─ status: 'trialing'
    │
    ▼
Laravel saves subscription
├─ INSERT INTO subscriptions (...)
├─ UPDATE users SET tier = 'pro'
    │
    ▼
Return to React
├─ Include Stripe client_secret
    │
    ▼
React Stripe Payment Modal
├─ Show card entry form
├─ User enters card details
├─ Confirm payment
    │
    ▼
Stripe processes payment
├─ If success: trigger webhook
    │
    ▼
Laravel Webhook Handler
├─ Received: charge.succeeded event
├─ Verify webhook signature
├─ Update subscription status to 'active'
├─ Send confirmation email
├─ Log transaction
    │
    ▼
User now has Pro access
├─ React detects tier change
├─ Unlocks Pro features
└─ Quota increased (5GB, 500 analyses)
```

---

## 3. Database Schema

### 3.1 ERD (Entity Relationship Diagram)

```
┌─────────────────────┐
│      USERS          │
├─────────────────────┤
│ id (PK, UUID)       │◄──────┐
│ email (UNIQUE)      │       │
│ password_hash       │       │
│ first_name          │       │
│ last_name           │       │
│ avatar_url          │       │
│ email_verified_at   │       │
│ created_at          │       │
│ updated_at          │       │
└─────────────────────┘       │
         ▲                     │
         │                     │
         │         ┌───────────┼──────────────────┐
         │         │           │                  │
         │         │           ▼                  │
         │         │    ┌─────────────────────┐   │
         │         │    │ SUBSCRIPTIONS       │   │
         │         │    ├─────────────────────┤   │
         │         │    │ id (PK, UUID)       │   │
         │         └────┤ user_id (FK) ◄──────   │
         │              │ stripe_customer_id  │   │
         │              │ stripe_price_id     │   │
         │              │ tier                │   │
         │              │ status              │   │
         │              │ current_period_*    │   │
         │              │ trial_ends_at       │   │
         │              │ created_at          │   │
         │              └─────────────────────┘   │
         │                                        │
         ├────────┬──────────────────────┬────────┘
         │        │                      │
         │        ▼                      ▼
    ┌─────────────────────┐      ┌──────────────────────┐
    │  SAMPLES            │      │ USER_PREFERENCES     │
    ├─────────────────────┤      ├──────────────────────┤
    │ id (PK, UUID)       │      │ user_id (PK, FK) ◄──┘
    │ user_id (FK) ◄──────┤      │ auto_analyze         │
    │ filename            │      │ selected_model       │
    │ file_url            │      │ notification_email   │
    │ duration            │      │ created_at           │
    │ created_at          │      └──────────────────────┘
    └─────┬───────────────┘
         │
         │
         ▼
    ┌─────────────────────┐
    │ AUDIO_FEATURES      │
    ├─────────────────────┤
    │ id (PK, UUID)       │
    │ sample_id (FK) ◄────┤ to SAMPLES
    │ bpm                 │
    │ musical_key         │
    │ spectral_centroid   │
    │ created_at          │
    └─────────────────────┘

         ▲
         │
    ┌────┴────────────────────┐
    │                         │
    │         ▼               │
    │  ┌─────────────────────┐ │
    │  │ COLLECTIONS         │ │
    │  ├─────────────────────┤ │
    │  │ id (PK, UUID)       │ │
    │  │ user_id (FK) ◄──────┤─┘
    │  │ name                │
    │  │ description         │
    │  │ created_at          │
    │  └─────────────────────┘

         ▲
         │
    ┌────┴─────────────────────────┐
    │                              │
    │      ┌──────────────────────┐│
    │      │ API_USAGE            ││
    │      ├──────────────────────┤│
    │      │ id (PK, UUID)        ││
    │      │ user_id (FK) ◄───────┤┤
    │      │ endpoint             ││
    │      │ method               ││
    │      │ response_time_ms     ││
    │      │ status_code          ││
    │      │ tokens_used          ││
    │      │ cost_usd             ││
    │      │ created_at           ││
    │      └──────────────────────┘│
    │                              │
    └──────────────────────────────┘
```

### 3.2 Key Indexes

```sql
-- Users
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created ON users(created_at);

-- Subscriptions
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE UNIQUE INDEX idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);

-- Samples
CREATE INDEX idx_samples_user ON samples(user_id);
CREATE INDEX idx_samples_created ON samples(user_id, created_at);
CREATE INDEX idx_samples_user_filename ON samples(user_id, filename);

-- Collections
CREATE INDEX idx_collections_user ON collections(user_id);
CREATE INDEX idx_collections_created ON collections(user_id, created_at);

-- API Usage (for analytics)
CREATE INDEX idx_api_usage_user_date ON api_usage(user_id, created_at);
```

---

## 4. Service Communication Patterns

### 4.1 Synchronous Request/Response

**Pattern**: Used for immediate operations

```
React ──► Workers ──► Service ──► Database ──► Response

Examples:
- GET /api/samples (list samples)
- POST /api/auth/login (authenticate)
- GET /api/billing/subscription (current subscription)

Response Time: < 200ms (target p95)
```

**Laravel ↔ FastAPI Communication**:
```python
# FastAPI needs to check quotas with Laravel
from httpx import AsyncClient

async def get_user_quota(user_id: str):
    async with AsyncClient() as client:
        response = await client.get(
            f"{LARAVEL_API_URL}/api/quotas/{user_id}",
            timeout=5.0,
            retry=3  # Retry up to 3 times
        )
    return response.json()
```

### 4.2 Asynchronous Job Queue

**Pattern**: Used for long-running operations

```
React ──► Workers ──► FastAPI
    ├─ Receive upload
    ├─ Store in R2
    ├─ Create job record
    └─ Return job_id immediately (202 Accepted)
                │
                ▼
        Queue System (Redis)
        ├─ job_id enqueued
        ├─ Audio Analysis Worker
        │   ├─ Download from R2
        │   ├─ Extract BPM/key
        │   ├─ Send to OpenRouter for AI
        │   └─ Store results in DB
                │
                ▼
        Webhook/Polling
        ├─ React polls /api/jobs/{job_id}
        ├─ Returns status: pending → processing → complete
        └─ Updates UI when complete
```

**Implementation**:
```python
# FastAPI - Queue upload
@router.post("/api/samples")
async def upload_sample(
    file: UploadFile,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check quota
    quota = await check_quota(user['id'])

    # Upload to R2
    r2_key = f"uploads/{user['id']}/{uuid4()}.wav"
    await r2_client.put(r2_key, file.file)

    # Create job
    job = ProcessingJob(
        id=str(uuid4()),
        user_id=user['id'],
        file_key=r2_key,
        status='pending'
    )
    db.add(job)
    await db.commit()

    # Queue job
    await queue.enqueue('process_audio', job_id=job.id)

    # Return immediately
    return {
        'job_id': job.id,
        'status': 'pending'
    }

# Redis Queue Worker (background process)
async def process_audio(job_id: str):
    job = await db.get(ProcessingJob, job_id)
    job.status = 'processing'

    try:
        # Download from R2
        audio_data = await r2_client.get(job.file_key)

        # Analyze locally
        features = extract_audio_features(audio_data)

        # Get AI analysis
        vibe = await openrouter.analyze(audio_data)

        # Store results
        sample = Sample(
            id=str(uuid4()),
            user_id=job.user_id,
            file_key=job.file_key,
            duration=features.duration
        )
        audio_feature = AudioFeature(
            sample_id=sample.id,
            bpm=features.bpm,
            vibe=vibe
        )

        db.add(sample)
        db.add(audio_feature)
        job.status = 'completed'
        await db.commit()

    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        await db.commit()
```

---

## 5. Security Architecture

### 5.1 Authentication Security

```
┌─────────────────────────────────┐
│   User Account                  │
│   - password hashing (bcrypt)   │
│   - email verification          │
│   - 2FA (future)                │
└──────────┬──────────────────────┘
           │
           ▼
    ┌──────────────────┐
    │  JWT Token       │
    │  RS256 (asymm.)  │
    │  1-hour TTL      │
    │  Refresh token   │
    └──────────┬───────┘
               │
    ┌──────────┴─────────────┐
    │                        │
    ▼                        ▼
Verify (Public Key)    Sign (Private Key)
├─ Workers can verify  ├─ Only Laravel
├─ All services accept ├─ Never shared
└─ No key needed       └─ Stored locally
```

**Key Management**:
```bash
# Keys stored locally, NEVER in repo
storage/keys/
├── jwt-private.pem (600 permissions, read-only)
└── jwt-public.pem (644 permissions)

# Added to .gitignore
storage/keys/*

# In production (Railway)
Railway Secrets:
├── JWT_PRIVATE_KEY (pasted as env var)
└── JWT_PUBLIC_KEY (pasted as env var)
```

### 5.2 Authorization Levels

```
┌────────────────────────────────────┐
│  Public (No Auth Required)          │
├────────────────────────────────────┤
│ POST /api/auth/register             │
│ POST /api/auth/login                │
│ GET /api/billing/plans              │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Authenticated (Valid JWT)          │
├────────────────────────────────────┤
│ GET /api/samples (own samples)      │
│ POST /api/samples (upload)          │
│ GET /api/billing/subscription       │
│ POST /api/auth/logout               │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Tier-Specific (Pro/Enterprise)     │
├────────────────────────────────────┤
│ POST /api/samples (higher quota)    │
│ POST /api/billing/subscribe (Pro)   │
│ GET /api/advanced-search (Pro)      │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│  Admin Only (Future)                │
├────────────────────────────────────┤
│ GET /api/admin/users                │
│ PUT /api/admin/users/{id}           │
│ DELETE /api/admin/users/{id}        │
└────────────────────────────────────┘
```

### 5.3 Data Isolation

```
Each API request carries:
├─ X-User-ID header (from JWT)
└─ Used to filter ALL database queries

SELECT * FROM samples
WHERE user_id = X-User-ID  ◄── ALWAYS required

Result:
├─ User A never sees User B's samples
├─ Even if they guess sample_id, 404 returned
├─ Database enforces at query level
└─ Defense in depth (no single point of failure)
```

---

## 6. Error Handling Architecture

### 6.1 Error Flow

```
Error at any layer
    │
    ├─ Application error (400)
    │   ├─ Validation failed
    │   └─ User error (bad input)
    │
    ├─ Authentication error (401)
    │   ├─ Token expired
    │   ├─ Token invalid
    │   └─ No token provided
    │
    ├─ Authorization error (403)
    │   ├─ User lacks permission
    │   └─ Quota exceeded
    │
    ├─ Not found (404)
    │   ├─ Resource doesn't exist
    │   └─ User doesn't own resource
    │
    ├─ Server error (500)
    │   ├─ Database connection fail
    │   ├─ External API fail
    │   └─ Unexpected exception
    │
    ▼
Log to Sentry
├─ Environment
├─ User ID
├─ Stack trace
├─ Request context
└─ Error severity (error, warning, critical)

    │
    ▼
Return JSON Response
├─ Consistent format
├─ Safe error message (no secrets)
├─ Request ID for debugging
└─ HTTP status code

    │
    ▼
React Error Boundary
├─ Catch and display user-friendly message
├─ Suggest action (retry, login, upgrade)
└─ Report to analytics
```

### 6.2 Graceful Degradation

```
FastAPI down?
├─ Cloudflare Workers detects 502
├─ Return 503 Service Unavailable
├─ React shows "Service temporarily down"
├─ Queue jobs for later
└─ User can still browse

Laravel down?
├─ Auth routes fail
├─ User cannot login
├─ Workers denies access
├─ React shows "Please try again later"
└─ Sentry alerts on-call engineer

Both down?
├─ Cloudflare continues serving static React app
├─ Shows offline message
├─ Queue messages locally (service worker)
└─ Auto-retry when services recover
```

---

## 7. Caching Strategy

### 7.1 Cache Layers

```
┌──────────────────────────────────┐
│  Browser Cache                   │
│  (React + React Query)           │
│  TTL: 5-30 minutes               │
├──────────────────────────────────┤
│ - Sample list                    │
│ - User subscription              │
│ - Billing plans                  │
└──────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│  Cloudflare Cache                │
│  (CDN)                           │
│  TTL: 30 minutes - 1 hour        │
├──────────────────────────────────┤
│ - Static assets (JS, CSS)        │
│ - Billing plans (public)         │
│ - Public key endpoint            │
└──────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│  Redis Cache                     │
│  (Application Layer)             │
│  TTL: 5-60 minutes               │
├──────────────────────────────────┤
│ - User quotas                    │
│ - Session tokens                 │
│ - Token blacklist                │
│ - Subscription data              │
└──────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│  PostgreSQL                      │
│  (Source of Truth)               │
│  No cache expiration             │
├──────────────────────────────────┤
│ - All persistent data            │
└──────────────────────────────────┘
```

### 7.2 Cache Invalidation

```
User uploads sample:
1. POST /api/samples
2. FastAPI processes
3. Invalidate caches:
   ├─ React Query invalidates 'samples' key
   ├─ Redis deletes user_samples:user_id
   └─ Cloudflare purges sample list endpoint
4. Next GET /api/samples fetches fresh data

User upgrades subscription:
1. POST /api/billing/subscribe
2. Laravel updates database
3. Invalidate caches:
   ├─ Redis deletes user_quotas:user_id
   ├─ Redis deletes user_tier:user_id
   └─ React Query invalidates 'subscription' key
4. FastAPI checks fresh quota on next upload
```

---

## 8. Deployment Topology

### 8.1 Development Environment

```
Local Machine (Docker Compose)
├─ PostgreSQL (5432)
├─ Redis (6379)
├─ Laravel (8000) - php artisan serve
├─ FastAPI (8100) - uvicorn backend:app
├─ React Dev Server (5173) - npm run dev
└─ Cloudflare Workers (local emulation)
```

### 8.2 Staging Environment

```
Staging (Railway.app)
├─ Database
│   └─ PostgreSQL (managed, automated backups)
│
├─ Auth Service
│   └─ Laravel on Railway (1x Standard dyno)
│       ├─ 512 MB RAM
│       ├─ Auto-scaling (2-5 instances)
│       └─ Health checks enabled
│
├─ Processing Service
│   └─ FastAPI on Railway (1x Standard dyno)
│       ├─ 512 MB RAM
│       ├─ Auto-scaling (2-5 instances)
│       └─ Health checks enabled
│
├─ API Gateway
│   └─ Cloudflare Workers (edge)
│       ├─ <200 routes
│       ├─ Rate limiting 1000 req/min
│       └─ Logging to Logflare
│
├─ Frontend
│   └─ Cloudflare Pages
│       ├─ Static site generation
│       ├─ Auto-deploy on git push
│       └─ Caching enabled
│
├─ Monitoring
│   ├─ Sentry (error tracking)
│   ├─ Better Uptime (health checks)
│   └─ LogRocket (session replay)
│
└─ Backup
    └─ PostgreSQL automatic backups (daily)
```

### 8.3 Production Environment

```
Production (Railway.app + Cloudflare)
├─ Database
│   └─ PostgreSQL (RDS or Railway managed)
│       ├─ Multi-AZ deployment
│       ├─ Daily automated backups
│       ├─ Point-in-time recovery enabled
│       └─ Read replicas for analytics
│
├─ Auth Service (Laravel)
│   └─ Railway (2-10 instances, auto-scaling)
│       ├─ Memory: 1-2 GB per instance
│       ├─ CPU: Shared, auto-scaling
│       ├─ Health checks (every 10s)
│       └─ 99.9% uptime SLA
│
├─ Processing Service (FastAPI)
│   └─ Railway (2-10 instances, auto-scaling)
│       ├─ Memory: 1-2 GB per instance
│       ├─ CPU: Shared, auto-scaling
│       ├─ Health checks (every 10s)
│       └─ 99.9% uptime SLA
│
├─ Queue System (Redis)
│   └─ Railway or Upstash
│       ├─ Persistence enabled
│       ├─ Max 100GB memory
│       └─ Auto-failover enabled
│
├─ API Gateway (Workers)
│   ├─ Cloudflare Workers (edge)
│   ├─ Unlimited requests/month (free tier)
│   ├─ 200 routes deployed
│   ├─ JWT validation at edge
│   ├─ Rate limiting per user
│   └─ DDoS protection automatic
│
├─ Frontend (React)
│   ├─ Cloudflare Pages (CDN)
│   ├─ 200+ edge locations globally
│   ├─ Automatic HTTPS/SSL
│   ├─ HTTP/2 push enabled
│   ├─ Gzip compression
│   └─ Browser caching (1 year for hashed assets)
│
├─ File Storage (R2)
│   ├─ Cloudflare R2
│   ├─ S3-compatible API
│   ├─ Zero egress fees
│   └─ 10 GB included in free plan
│
├─ Monitoring & Alerting
│   ├─ Sentry (error tracking)
│   │   └─ Performance monitoring enabled
│   ├─ Better Uptime (status page)
│   │   └─ Alert on 2 failures in 5 min
│   ├─ Datadog (optional)
│   │   └─ APM for detailed tracing
│   └─ PagerDuty (on-call rotation)
│
├─ Email Delivery
│   ├─ SendGrid or Mailgun
│   ├─ Transactional emails (verification, invoices)
│   ├─ Bounce handling
│   └─ Deliverability tracking
│
├─ Payment Processing
│   ├─ Stripe API
│   ├─ Webhook verification
│   ├─ PCI compliance
│   └─ 3D Secure support
│
└─ Backup & Disaster Recovery
    ├─ Daily PostgreSQL backups (7-day retention)
    ├─ Backup to S3 (cross-region)
    ├─ Recovery test monthly
    ├─ RTO: 1 hour
    └─ RPO: 1 day
```

---

## 9. Scalability Considerations

### 9.1 Horizontal Scaling

```
Current Single Instance:
├─ Rails: 1 instance (512MB RAM)
├─ FastAPI: 1 instance (512MB RAM)
└─ Can handle: ~100 concurrent users

Scaling to 1000 Users:
├─ Laravel: 5-10 instances (auto-scaling)
├─ FastAPI: 5-10 instances (auto-scaling)
├─ Redis: 1 instance with persistence
├─ PostgreSQL: 1 primary + 1 read replica
└─ Can handle: 10,000+ concurrent users

Key Scaling Strategies:
├─ Load balancing (Railway provides)
├─ Connection pooling (PgBouncer)
├─ Caching layer (Redis)
├─ CDN for static assets
├─ Query optimization
└─ Vertical scaling when needed
```

### 9.2 Database Optimization

```
Bottlenecks & Solutions:
├─ N+1 queries
│   └─ Solution: Eager loading, select() clauses
│
├─ Missing indexes
│   └─ Solution: Index frequently queried columns
│
├─ Slow queries
│   └─ Solution: EXPLAIN ANALYZE, query optimization
│
├─ Connection exhaustion
│   └─ Solution: Connection pooling (max 20 per service)
│
└─ Large result sets
    └─ Solution: Pagination, lazy loading
```

---

## 10. Monitoring & Observability

### 10.1 Metrics to Track

```
Application Metrics:
├─ Response time (p50, p95, p99)
├─ Error rate (4xx, 5xx)
├─ Throughput (requests/sec)
├─ JWT validation time
├─ Database query time
└─ Queue job duration

Business Metrics:
├─ User signups
├─ Subscription conversions
├─ MRR (Monthly Recurring Revenue)
├─ Churn rate
├─ Trial to paid conversion
└─ Feature usage

Infrastructure Metrics:
├─ CPU usage
├─ Memory usage
├─ Disk I/O
├─ Network throughput
├─ Database connections
└─ Redis memory
```

### 10.2 Alerting Rules

```
Critical (Page On-Call):
├─ API error rate > 5% for 5 minutes
├─ Database connection pool exhausted
├─ Redis unavailable
├─ JWT validation failing > 10% requests
└─ FastAPI offline (health check failed)

Warning (Email):
├─ Response time p95 > 500ms for 10 min
├─ Error rate > 1% for 10 minutes
├─ Memory usage > 80%
├─ Disk usage > 85%
└─ Stripe webhook failures

Info (Logs):
├─ Deployment started/completed
├─ Database migration started/completed
├─ User signup
├─ Subscription created
└─ Payment processed
```

---

## 11. Security Hardening Checklist

### Pre-Launch Security

- [ ] HTTPS/TLS on all endpoints
- [ ] HSTS headers configured
- [ ] CSP (Content Security Policy) headers
- [ ] CORS properly restricted
- [ ] Rate limiting configured (100 req/min per user)
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (HTML escaping)
- [ ] CSRF tokens on state-changing operations
- [ ] Secrets never committed to repo
- [ ] Dependencies scanned for vulnerabilities
- [ ] Encryption in transit (TLS) ✓
- [ ] Encryption at rest (database passwords)
- [ ] API keys rotated every 90 days
- [ ] SSH keys for server access
- [ ] Database backups encrypted
- [ ] WAF rules on Cloudflare
- [ ] DDoS protection enabled
- [ ] Audit logging enabled
- [ ] Password policy (8+ chars, complexity)
- [ ] Email verification required
- [ ] Token revocation on logout
- [ ] Stripe PCI compliance

---

## 12. Conclusion

This architecture provides:

✅ **Scalability**: Horizontal scaling on demand
✅ **Reliability**: Redundancy and failover mechanisms
✅ **Security**: Multi-layer defense and data isolation
✅ **Performance**: Edge caching, async processing, query optimization
✅ **Maintainability**: Clear service boundaries and responsibilities
✅ **Cost-Effectiveness**: Free tier services (Cloudflare, Railway free tier)

The design is production-ready and can support 10,000+ users with proper monitoring and optimization.

