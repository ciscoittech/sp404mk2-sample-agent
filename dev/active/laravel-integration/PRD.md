# Product Requirements Document: Laravel Integration for SP-404MK2 Sample Agent

**Version**: 1.0
**Date**: 2025-11-18
**Timeline**: 8-12 weeks (Production-ready)
**Status**: Ready for Implementation

---

## 1. Executive Summary

Transform the SP-404MK2 Sample Agent from a single-service architecture into a production-ready SaaS platform by adding Laravel 11 as the **User/Auth/Billing layer**, while keeping FastAPI as the **high-performance domain logic layer**.

### Current State
- Single FastAPI backend with basic file handling
- React 19 frontend (modern, feature-complete)
- PostgreSQL database
- No user authentication or billing

### Target State
- **Distributed architecture** with clear separation of concerns
- **Laravel**: User management, authentication, subscriptions, billing
- **FastAPI**: Audio processing, AI analysis, sample management (unchanged logic)
- **React**: Modern frontend consuming both APIs
- **Cloudflare**: Edge routing, R2 storage, Workers gateway
- **Production-ready**: Multi-user, quota enforcement, monitoring

### Business Value
- ✅ **SaaS-ready**: Support multiple users with billing
- ✅ **Scalability**: Services can scale independently
- ✅ **Reliability**: Clear service boundaries with fallback patterns
- ✅ **Cost control**: Track usage per user, enforce quotas
- ✅ **Compliance**: User data isolation, audit trails

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-1: User Management
- [ ] User registration (email/password)
- [ ] User login (JWT token issuance)
- [ ] User logout (token invalidation)
- [ ] Password reset workflow
- [ ] Email verification
- [ ] Profile management (name, avatar)
- [ ] User data export (GDPR compliance)

#### FR-2: Authentication & Authorization
- [ ] JWT token generation (RS256 asymmetric)
- [ ] Token refresh mechanism (1-hour access, 7-day refresh)
- [ ] Multi-service token validation (Workers gateway)
- [ ] Automatic token expiration
- [ ] Token revocation on logout
- [ ] Rate limiting per user

#### FR-3: Billing & Subscriptions
- [ ] Three subscription tiers: Free, Pro, Enterprise
- [ ] Stripe integration (via Laravel Cashier)
- [ ] Subscription management (create, upgrade, downgrade, cancel)
- [ ] Invoice generation and archival
- [ ] Payment failure handling and retry logic
- [ ] Subscription status tracking
- [ ] Trial period support (14 days for Pro)

#### FR-4: Usage Tracking & Quotas
- [ ] Track storage usage per user
- [ ] Track AI analysis count per user
- [ ] Track API call frequency
- [ ] Enforce storage quotas by tier:
  - Free: 100MB
  - Pro: 5GB
  - Enterprise: Unlimited
- [ ] Enforce analysis limits by tier:
  - Free: 10/month
  - Pro: 500/month
  - Enterprise: Unlimited
- [ ] Queue prioritization by tier

#### FR-5: Multi-User Data Isolation
- [ ] All samples scoped to user_id
- [ ] All collections scoped to user_id
- [ ] All audio features scoped to sample_id (via sample)
- [ ] User can only access their own data
- [ ] Admin can view all users (future)

#### FR-6: Stripe Integration
- [ ] Webhook receivers (payment success/failure)
- [ ] Subscription lifecycle management
- [ ] Automatic invoice generation
- [ ] Payment retry logic
- [ ] Billing dashboard

### 2.2 Non-Functional Requirements

#### Performance
- [ ] Authentication response < 200ms
- [ ] API gateway routing < 50ms
- [ ] Database queries < 500ms
- [ ] JWT validation < 10ms

#### Reliability
- [ ] 99.9% uptime target
- [ ] Graceful degradation if FastAPI unavailable
- [ ] Retry logic with exponential backoff
- [ ] Circuit breaker pattern for service calls
- [ ] Comprehensive error logging

#### Security
- [ ] HTTPS everywhere
- [ ] JWT RS256 signing
- [ ] CORS properly configured
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (CSP headers)
- [ ] Rate limiting (100 requests/minute per user)
- [ ] Secrets management (.env only, never committed)
- [ ] Password hashing (bcrypt)

#### Scalability
- [ ] Stateless service design
- [ ] Horizontal scaling for Laravel and FastAPI
- [ ] Database connection pooling
- [ ] Caching strategy (Redis for sessions)
- [ ] Load testing to 1000 concurrent users

#### Monitoring & Observability
- [ ] Structured JSON logging
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic / Datadog)
- [ ] Health checks for all services
- [ ] Uptime monitoring
- [ ] Email alerts for critical errors

---

## 3. User Stories & Acceptance Criteria

### Story 1: User Registration & Login
**As a** music producer
**I want to** create an account and login
**So that** I can access the sample collection system

**Acceptance Criteria:**
- [ ] User can register with email and password
- [ ] Password must be 8+ characters
- [ ] Email must be verified via confirmation link
- [ ] User receives confirmation email within 60 seconds
- [ ] User can login with correct credentials
- [ ] System returns JWT token valid for 1 hour
- [ ] Invalid credentials return 401 Unauthorized
- [ ] User cannot login before email verification

**Story 2: Subscription Management**
**As a** pro user
**I want to** upgrade/downgrade my subscription
**So that** I can manage my billing and features

**Acceptance Criteria:**
- [ ] User can view current subscription details
- [ ] User can select a new plan
- [ ] Stripe payment modal appears on plan selection
- [ ] Payment succeeds and subscription updates
- [ ] Invoice is generated and sent via email
- [ ] User is immediately granted new tier features
- [ ] Downgrade takes effect at end of current period
- [ ] Cancelled subscription disables features after expiry

**Story 3: Usage Tracking**
**As a** free user
**I want to** see how much of my quota I've used
**So that** I know when I'll be limited

**Acceptance Criteria:**
- [ ] Dashboard shows storage usage (50MB / 100MB)
- [ ] Dashboard shows analysis count (3 / 10)
- [ ] Quota warnings appear at 80% usage
- [ ] Uploads block when storage quota exceeded
- [ ] Analytics queue when analysis quota exceeded
- [ ] Pro user has 50x more quota
- [ ] Quota resets on monthly subscription date

**Story 4: Multi-User Isolation**
**As a** platform owner
**I want to** ensure users cannot access other users' data
**So that** the platform is secure

**Acceptance Criteria:**
- [ ] User A cannot view User B's samples (401 when accessing)
- [ ] User A cannot modify User B's collections
- [ ] Database queries automatically filter by user_id
- [ ] API returns 404 for samples not owned by user
- [ ] Logs contain audit trail of access attempts

---

## 4. Architecture Overview

### 4.1 System Components

```
┌─────────────────────────────────────────────────────┐
│           React 19 SPA (Cloudflare Pages)           │
│   Modern UI with Tailwind CSS + shadcn/ui          │
│   - Auth flows (login, register, reset password)   │
│   - Sample library UI (list, upload, organize)     │
│   - Billing dashboard (view plans, manage sub)     │
│   - User settings (profile, preferences)           │
└─────────────────┬─────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│    Cloudflare Workers (API Gateway + Router)        │
│   - JWT validation (RS256 asymmetric)              │
│   - Route to Laravel or FastAPI                    │
│   - CORS handling                                   │
│   - Rate limiting                                   │
│   - Direct R2 uploads (no backend required)        │
└──────┬──────────────────────────────────┬──────────┘
       │                                  │
       ▼                                  ▼
┌──────────────────────────┐  ┌────────────────────────────┐
│   Laravel 11 API         │  │   FastAPI Audio Engine     │
│   (Auth & Billing)       │  │   (Domain Logic)           │
├──────────────────────────┤  ├────────────────────────────┤
│ • User registration      │  │ • Audio analysis (librosa) │
│ • JWT token issuance     │  │ • AI analysis (OpenRouter) │
│ • Email verification     │  │ • Sample CRUD              │
│ • Stripe Cashier        │  │ • Collections              │
│ • Subscription mgmt     │  │ • Similarity search        │
│ • Invoice generation    │  │ • SP-404 export            │
│ • Queue management      │  │ • Stateless design         │
│ • User preferences      │  │                            │
└──────────┬───────────────┘  └──────────────┬─────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          ▼
                 ┌──────────────────┐
                 │   PostgreSQL     │
                 │   (Shared)       │
                 │                  │
                 │ • users          │
                 │ • subscriptions  │
                 │ • samples        │
                 │ • audio_features │
                 │ • collections    │
                 │ • api_usage      │
                 └──────────────────┘
```

### 4.2 Service Responsibilities

#### Laravel (Port 8000)
**Primary Responsibilities:**
- User lifecycle (register, login, verify, reset)
- JWT token generation (RS256 private key)
- Subscription management (Stripe Cashier)
- Billing and invoicing
- Email delivery
- Queue job management (Redis)

**Does NOT handle:**
- Audio processing
- AI analysis
- Sample file storage
- Collection organization (that's FastAPI)

#### FastAPI (Port 8100)
**Primary Responsibilities:**
- Audio file analysis (BPM, key, features)
- AI-powered vibe analysis (OpenRouter)
- Sample CRUD operations
- Collections management
- Similarity search
- SP-404 project export

**Does NOT handle:**
- User authentication
- Billing
- Email delivery
- Subscription management

#### Cloudflare Workers (Edge)
**Primary Responsibilities:**
- JWT validation at edge
- Route to correct backend
- CORS handling
- Rate limiting
- Direct R2 uploads
- Caching headers

**Does NOT handle:**
- Business logic
- Database queries
- Long-running operations

---

## 5. Database Schema

### Users Table (Laravel Managed)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified_at TIMESTAMP,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    avatar_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Subscriptions Table (Stripe)
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    tier VARCHAR(50) NOT NULL, -- 'free', 'pro', 'enterprise'
    status VARCHAR(50) NOT NULL, -- 'active', 'trialing', 'past_due', 'cancelled'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    trial_ends_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    auto_analyze_enabled BOOLEAN DEFAULT true,
    selected_model VARCHAR(100) DEFAULT 'qwen/qwen3-7b-it',
    notification_email_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Usage Tracking Table
```sql
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    response_time_ms INTEGER,
    status_code INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_created (user_id, created_at)
);
```

### Existing Tables (Updated with user_id)
```sql
ALTER TABLE samples ADD COLUMN user_id UUID NOT NULL REFERENCES users(id);
ALTER TABLE collections ADD COLUMN user_id UUID NOT NULL REFERENCES users(id);
ALTER TABLE processing_jobs ADD COLUMN user_id UUID NOT NULL REFERENCES users(id);

CREATE INDEX idx_samples_user ON samples(user_id);
CREATE INDEX idx_collections_user ON collections(user_id);
CREATE INDEX idx_jobs_user ON processing_jobs(user_id);
```

---

## 6. API Contracts

### Authentication Endpoints (Laravel)

#### POST /api/auth/register
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "message": "Registration successful. Please verify your email.",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /api/auth/login
**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "tier": "free"
  },
  "expires_in": 3600
}
```

#### POST /api/auth/refresh
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "token": "new_token...",
  "expires_in": 3600
}
```

#### POST /api/auth/logout
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### Billing Endpoints (Laravel)

#### GET /api/billing/plans
**Response (200):**
```json
{
  "plans": [
    {
      "id": "free",
      "name": "Free",
      "price": 0,
      "features": {
        "storage_gb": 0.1,
        "analyses_per_month": 10,
        "api_requests_per_day": 100
      }
    },
    {
      "id": "pro",
      "name": "Pro",
      "price": 29,
      "trial_days": 14,
      "features": {
        "storage_gb": 5,
        "analyses_per_month": 500,
        "api_requests_per_day": 10000
      }
    }
  ]
}
```

#### POST /api/billing/subscribe
**Request:**
```json
{
  "plan_id": "pro"
}
```

**Response (200):**
```json
{
  "client_secret": "pi_1234567890...",
  "subscription_id": "uuid"
}
```

#### GET /api/billing/subscription
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": "uuid",
  "tier": "pro",
  "status": "active",
  "current_period_end": "2025-12-18T00:00:00Z",
  "next_billing_date": "2025-12-18",
  "price": 29,
  "usage": {
    "storage_mb": 1500,
    "storage_limit_mb": 5120,
    "analyses_used": 45,
    "analyses_limit": 500
  }
}
```

### Sample Endpoints (FastAPI - unchanged, now with auth)

#### GET /api/samples
**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "samples": [
    {
      "id": "uuid",
      "filename": "sample.wav",
      "duration": 4.5,
      "created_at": "2025-11-18T10:00:00Z",
      "vibe": "Smooth jazzy break with vintage warmth"
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

#### POST /api/samples (Upload)
**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Form Data:**
- `audio`: File (WAV, MP3, FLAC, etc.)
- `tags`: (optional) Comma-separated tags

**Response (201):**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "filename": "sample.wav",
  "estimated_completion": "2025-11-18T10:05:00Z"
}
```

---

## 7. Authentication & Authorization Flow

### JWT Token Structure (RS256)

**Token is signed by Laravel (private key), verified by all services (public key)**

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "tier": "pro",
  "verified": true,
  "iat": 1700300400,
  "exp": 1700304000
}
```

### Login Flow

```
1. User submits email/password
   └─> POST /api/auth/login (Laravel)

2. Laravel validates credentials
   └─> Query users table, verify password hash

3. If valid:
   └─> Generate JWT with RS256 (Laravel private key)
   └─> Add to blacklist cache (Redis) if logout
   └─> Return token + user info

4. React stores token in localStorage
   └─> Include in Authorization header for all requests

5. Cloudflare Workers validates token
   └─> Verify signature (RS256 public key)
   └─> Extract user_id from claims
   └─> Pass X-User-ID header to FastAPI

6. FastAPI trusts user_id (already validated by Workers)
   └─> Filter queries by user_id
   └─> No need for re-validation
```

### Request Flow

```
React Client
    │
    ├─► POST /api/auth/login ──► Laravel ──► JWT token
    │
    ├─► GET /api/samples ──► Cloudflare Workers
    │                            │
    │                            ├─ Validate JWT (RS256)
    │                            ├─ Extract user_id
    │                            │
    │                            └─► FastAPI
    │                                 ├─ Header: X-User-ID: user-uuid
    │                                 ├─ Header: X-User-Tier: pro
    │                                 │
    │                                 └─► SELECT * FROM samples WHERE user_id = user-uuid
    │
    └─◄── JSON response with user's samples only
```

---

## 8. Quota & Usage Enforcement

### Quota Limits by Tier

| Feature | Free | Pro | Enterprise |
|---------|------|-----|-----------|
| Storage | 100 MB | 5 GB | Unlimited |
| Analyses/month | 10 | 500 | Unlimited |
| API calls/day | 100 | 10,000 | Unlimited |
| Collections | 5 | Unlimited | Unlimited |
| Concurrent uploads | 1 | 5 | 10 |

### Enforcement Points

**1. Upload Handler (Workers/FastAPI)**
```python
# Before accepting upload:
quota = await get_user_quota(user_id, tier)
if quota['storage_used_mb'] + file_size_mb > quota['limit_mb']:
    return HTTPException(status_code=429, detail="Storage quota exceeded")
```

**2. Analysis Handler (FastAPI)**
```python
# Before queuing analysis:
usage = await get_monthly_usage(user_id)
if usage['analyses_used'] >= usage['limit']:
    return HTTPException(status_code=429, detail="Analysis quota exceeded")
```

**3. API Rate Limiter (Workers)**
```typescript
// Enforce daily API call limit
const dailyUsage = await env.REDIS.get(`usage:${userId}:${today}`)
if (parseInt(dailyUsage || '0') >= dailyLimit) {
    return new Response('Rate limit exceeded', { status: 429 })
}
```

---

## 9. Deployment Architecture

### Development Environment
- Docker Compose with Laravel, FastAPI, PostgreSQL
- Local Cloudflare Workers emulation
- Redis for session/queue management

### Staging Environment
- Railway: Laravel API
- Railway: FastAPI
- PostgreSQL (Supabase or RDS)
- Cloudflare Workers (staging)
- Sentry error tracking

### Production Environment
- Railway: Laravel (auto-scaling)
- Railway: FastAPI (auto-scaling)
- PostgreSQL (managed, backups)
- Cloudflare Pages: React frontend
- Cloudflare Workers: API Gateway
- Cloudflare R2: File storage
- Redis (for queues/sessions)
- Stripe: Billing

---

## 10. Success Criteria & Metrics

### Technical Metrics
- [ ] All 150+ existing tests passing
- [ ] New integration tests: 50+ passing
- [ ] API response time < 200ms (p95)
- [ ] Database query time < 500ms (p95)
- [ ] Zero service-to-service errors in production
- [ ] 99.9% uptime (SLA compliance)

### Business Metrics
- [ ] 100 free users can signup
- [ ] 10 users successfully subscribe to Pro
- [ ] $100/month MRR (2 months post-launch)
- [ ] < 5% payment failure rate
- [ ] < 0.1% fraud rate

### User Experience Metrics
- [ ] Auth flow < 2 seconds
- [ ] Subscription flow < 3 steps
- [ ] Upload success rate > 99%
- [ ] User satisfaction > 4.5/5

---

## 11. Risk Assessment

### Risk 1: Multi-Service Complexity
**Impact:** High | **Probability:** Medium
**Mitigation:**
- Clear API contracts and documentation
- Comprehensive integration tests
- Circuit breaker pattern for service failures

### Risk 2: Database Performance
**Impact:** High | **Probability:** Low
**Mitigation:**
- Proper indexing on user_id
- Connection pooling
- Query optimization and caching

### Risk 3: Billing Integration Issues
**Impact:** High | **Probability:** Low
**Mitigation:**
- Stripe sandbox testing
- Webhook verification
- Manual payment override capability

### Risk 4: Token Expiration Edge Cases
**Impact:** Medium | **Probability:** Medium
**Mitigation:**
- Refresh token mechanism
- Clear error messages
- Automatic retry on 401

### Risk 5: Existing Data Migration
**Impact:** Medium | **Probability:** Low
**Mitigation:**
- Dry run migration first
- Backup before migration
- Rollback plan documented
- Data validation scripts

---

## 12. Timeline & Milestones

### Phase 1: Foundation (Weeks 1-3)
- [ ] Laravel project creation and setup
- [ ] Database schema migrations
- [ ] User auth endpoints (register, login, logout)
- [ ] JWT generation (RS256)
- [ ] Email verification setup
- [ ] First integration tests passing

### Phase 2: Integration (Weeks 4-5)
- [ ] Cloudflare Workers gateway setup
- [ ] FastAPI user_id scoping
- [ ] Token validation middleware
- [ ] Cross-service routing
- [ ] CORS configuration
- [ ] Integration test suite (25+ tests)

### Phase 3: Billing (Weeks 6-8)
- [ ] Stripe Cashier integration
- [ ] Subscription endpoints
- [ ] Webhook handlers
- [ ] Invoice generation
- [ ] Quota enforcement
- [ ] Billing dashboard UI

### Phase 4: Production (Weeks 9-12)
- [ ] Docker Compose setup
- [ ] Railway deployment
- [ ] Monitoring and alerts
- [ ] Load testing (1000 concurrent users)
- [ ] Documentation and runbooks
- [ ] Go-live preparation

---

## 13. Definition of Done

A feature/phase is complete when:

- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] All tests passing (unit + integration)
- [ ] No console errors in development
- [ ] Performance benchmarks met
- [ ] Security checklist passed
- [ ] Documentation updated
- [ ] Monitoring alerts configured
- [ ] Staged tested in staging environment
- [ ] Ready for production deployment

---

## Appendix: Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Backend Auth** | Laravel | 11 | Battle-tested SaaS features |
| **Backend API** | FastAPI | Latest | Async, high-performance |
| **API Gateway** | Cloudflare Workers | Latest | Edge routing, global |
| **Frontend** | React | 19 | Already implemented |
| **Database** | PostgreSQL | 16 | Robust, feature-rich |
| **Sessions** | Redis | 7 | Fast cache for tokens |
| **Billing** | Stripe | API v3 | Industry standard |
| **Email** | SendGrid / Mailgun | Latest | Reliable delivery |
| **File Storage** | Cloudflare R2 | Latest | S3-compatible, cheap |
| **Deployment** | Railway | - | Simple Laravel deployment |
| **Monitoring** | Sentry | Latest | Error tracking |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-18 | Claude Code | Initial PRD |

