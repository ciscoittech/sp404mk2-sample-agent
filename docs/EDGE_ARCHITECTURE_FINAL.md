# SP404MK2 Sample Agent - Edge-First SaaS Architecture

**Date**: 2025-11-15
**Status**: Final Architecture - Production Ready Design

---

## 🎯 Architecture Overview

**Modern Edge Stack**: React → Workers → Laravel/FastAPI → Turso/R2

### Technology Stack
- **Frontend**: React (SPA) on Cloudflare Pages
- **Edge API**: Cloudflare Workers (TypeScript)
- **Business Logic**: Laravel API (users, billing, queues)
- **Processing**: FastAPI (audio analysis, AI)
- **Database**: Turso (edge-replicated libSQL)
- **Storage**: Cloudflare R2 (object storage)
- **Queue**: Redis or Cloudflare Queues

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Cloudflare Pages (Frontend)                │
├─────────────────────────────────────────────────────────────┤
│  React SPA (Vite + TypeScript)                             │
│  ├─ /dashboard - User dashboard                            │
│  ├─ /upload - File upload with drag-drop                   │
│  ├─ /samples - Sample library (infinite scroll)            │
│  ├─ /samples/:id - Sample details (waveform, analysis)     │
│  ├─ /billing - Subscription management                     │
│  └─ /settings - User preferences                           │
│                                                             │
│  State Management: React Query (server state caching)      │
│  ├─ Automatic refetch on job completion                    │
│  ├─ Optimistic updates for instant UI                      │
│  └─ Background polling for job status                      │
│                                                             │
│  API Client:                                                │
│  ├─ Fetch wrapper with auth headers                        │
│  ├─ Automatic retry on 429 (rate limit)                    │
│  └─ Error boundary for graceful failures                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Cloudflare Workers (Edge API)                 │
├─────────────────────────────────────────────────────────────┤
│  TypeScript API Routes (Hono framework)                    │
│  ├─ /api/auth/* - Proxy to Laravel (login, register)      │
│  ├─ /api/upload - File validation + R2 upload             │
│  ├─ /api/jobs/:id - Job status (read from Turso)          │
│  ├─ /api/samples - Sample list (read from Turso)          │
│  ├─ /api/samples/:id - Sample details (read from Turso)   │
│  └─ /api/billing/* - Proxy to Laravel (Stripe)            │
│                                                             │
│  Responsibilities:                                          │
│  ├─ 1. Authentication (JWT validation)                     │
│  ├─ 2. File upload validation (size, format, quota)       │
│  ├─ 3. Upload to R2 (direct from edge)                     │
│  ├─ 4. Create job in Turso                                 │
│  ├─ 5. Push to queue (Cloudflare Queues)                  │
│  ├─ 6. Fast read queries (Turso at edge)                  │
│  └─ 7. Proxy writes to Laravel (user updates, billing)    │
│                                                             │
│  Integrations:                                              │
│  ├─ Turso DB (read/write job status, samples)             │
│  ├─ R2 Storage (upload pending/processed files)           │
│  ├─ Cloudflare Queues (push processing jobs)              │
│  └─ Laravel API (proxy auth, billing, complex writes)     │
│                                                             │
│  Performance:                                               │
│  ├─ 200+ edge locations worldwide                          │
│  ├─ <20ms response time globally                           │
│  ├─ 10M requests/day on free tier                          │
│  └─ Auto-scaling (no cold starts)                          │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Laravel API (Origin)   │  │  Turso Database (Edge)   │
├──────────────────────────┤  ├──────────────────────────┤
│  JSON API (No Blade)     │  │  libSQL (SQLite-compat)  │
│                          │  │                          │
│  POST /api/auth/register │  │  Tables:                 │
│  POST /api/auth/login    │  │  ├─ users                │
│  POST /api/auth/logout   │  │  ├─ processing_jobs      │
│  GET  /api/user          │  │  ├─ samples              │
│                          │  │  ├─ audio_features       │
│  Billing (Cashier):      │  │  └─ api_usage            │
│  POST /api/subscribe     │  │                          │
│  POST /api/cancel        │  │  Edge Replicas:          │
│  GET  /api/subscription  │  │  ├─ US West              │
│  POST /api/webhook       │  │  ├─ US East              │
│                          │  │  ├─ EU (Amsterdam)       │
│  Queue Management:       │  │  └─ Asia (Tokyo)         │
│  POST /api/jobs/retry    │  │                          │
│  POST /api/jobs/cancel   │  │  Latency: <10ms global   │
│                          │  └──────────────────────────┘
│  Deployed on:            │
│  ├─ Railway / Fly.io     │
│  └─ Single region (US)   │
└──────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Cloudflare Queues (Message Queue)             │
├─────────────────────────────────────────────────────────────┤
│  - free-tier-queue (delayed 12-24 hours)                   │
│  - pro-tier-queue (immediate processing)                   │
│  - retry-queue (failed jobs)                               │
│                                                             │
│  Consumer: Cloudflare Worker (queue consumer)              │
│  ├─ Triggered when message arrives                         │
│  ├─ Calls FastAPI processing endpoint                      │
│  ├─ Updates job status in Turso                            │
│  └─ Sends notification (email/webhook)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Processing Engine                  │
│                    (Pure JSON API)                          │
├─────────────────────────────────────────────────────────────┤
│  POST /api/process                                          │
│  {                                                          │
│    "file_url": "https://r2.../sample.wav",                 │
│    "user_id": "123",                                        │
│    "tier": "pro",                                           │
│    "options": {                                             │
│      "ai_analysis": true,                                   │
│      "model": "qwen/qwen3-235b",                           │
│      "export_sp404": false                                 │
│    }                                                        │
│  }                                                          │
│  ↓                                                          │
│  Response: {                                                │
│    "success": true,                                         │
│    "audio_features": {                                      │
│      "bpm": 128.5,                                         │
│      "key": "C",                                           │
│      "spectral_centroid": 1500.3,                          │
│      ...                                                    │
│    },                                                       │
│    "ai_analysis": {                                         │
│      "vibe": "dark, brooding, atmospheric",                │
│      "genre": "ambient hip-hop",                           │
│      "tags": ["lofi", "chill", "melancholic"]             │
│    },                                                       │
│    "cost": 0.00005,                                        │
│    "processing_time": 3.2                                  │
│  }                                                          │
│                                                             │
│  GET /api/health - Health check                            │
│  GET /api/metrics - Prometheus metrics                     │
│                                                             │
│  Stateless Design:                                          │
│  ├─ No database connections                                │
│  ├─ No user management                                     │
│  ├─ No session state                                       │
│  └─ Pure processing API                                    │
│                                                             │
│  Auto-scaling:                                              │
│  ├─ Railway: Scale based on CPU                            │
│  ├─ Fly.io: Multi-region replicas                         │
│  └─ Can run 100s of concurrent jobs                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Cloudflare R2 Storage                     │
├─────────────────────────────────────────────────────────────┤
│  Buckets:                                                   │
│  ├─ /uploads-pending/ (temp, 24hr TTL)                    │
│  ├─ /processed/ (permanent, public CDN)                   │
│  └─ /exports/ (SP-404 exports, 7-day TTL)                 │
│                                                             │
│  Access:                                                    │
│  ├─ Workers: Direct R2 bindings (no API calls)            │
│  ├─ FastAPI: Signed URLs (read-only)                      │
│  └─ React: Public URLs for playback                        │
│                                                             │
│  Performance:                                               │
│  ├─ $0 egress (unlimited bandwidth!)                       │
│  ├─ <50ms global CDN delivery                             │
│  └─ Auto-scaling                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

### React Frontend (Cloudflare Pages)

```
react-sp404/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Upload.tsx
│   │   ├── SampleLibrary.tsx
│   │   ├── SampleDetail.tsx
│   │   ├── Billing.tsx
│   │   └── Settings.tsx
│   │
│   ├── components/
│   │   ├── FileUploader.tsx       # Drag-drop with progress
│   │   ├── SampleCard.tsx         # Sample grid item
│   │   ├── Waveform.tsx           # Audio waveform visualization
│   │   ├── JobStatusBadge.tsx     # Processing status indicator
│   │   └── PricingTable.tsx       # Free/Pro/Enterprise tiers
│   │
│   ├── hooks/
│   │   ├── useUpload.ts           # File upload with progress
│   │   ├── useSamples.ts          # React Query for samples
│   │   ├── useJobStatus.ts        # Polling for job status
│   │   └── useAuth.ts             # Authentication state
│   │
│   ├── api/
│   │   └── client.ts              # Fetch wrapper with auth
│   │       ├─ uploadFile()
│   │       ├─ getJobStatus()
│   │       ├─ getSamples()
│   │       └─ subscribe()
│   │
│   └── lib/
│       ├── auth.ts                # JWT token management
│       └── constants.ts           # API URLs, limits, etc.
│
├── package.json
└── vite.config.ts
```

### Cloudflare Workers (Edge API)

```
workers-api/
├── src/
│   ├── index.ts                   # Main router (Hono)
│   │
│   ├── routes/
│   │   ├── auth.ts                # Proxy to Laravel
│   │   ├── upload.ts              # File upload to R2
│   │   ├── jobs.ts                # Job status queries
│   │   ├── samples.ts             # Sample queries
│   │   └── billing.ts             # Proxy to Laravel
│   │
│   ├── middleware/
│   │   ├── auth.ts                # JWT validation
│   │   ├── rateLimit.ts           # Rate limiting (KV store)
│   │   └── cors.ts                # CORS headers
│   │
│   ├── services/
│   │   ├── turso.ts               # Turso DB client
│   │   ├── r2.ts                  # R2 storage client
│   │   ├── queue.ts               # Cloudflare Queues client
│   │   └── laravel.ts             # Laravel API client
│   │
│   └── lib/
│       ├── validation.ts          # File validation
│       └── quota.ts               # Quota checking
│
├── wrangler.toml                  # Cloudflare config
└── package.json
```

### Laravel API (Business Logic)

```
laravel-sp404/
├── app/
│   ├── Http/
│   │   └── Controllers/
│   │       └── Api/
│   │           ├── AuthController.php      # Login, register, logout
│   │           ├── UserController.php      # User profile
│   │           ├── BillingController.php   # Stripe Cashier
│   │           └── WebhookController.php   # Stripe webhooks
│   │
│   ├── Models/
│   │   ├── User.php               # Billable trait
│   │   └── Subscription.php       # Cashier model
│   │
│   └── Services/
│       ├── FastApiService.php     # Call FastAPI
│       └── QuotaService.php       # Enforce limits
│
├── routes/
│   └── api.php                    # JSON API routes only (NO web routes)
│
└── config/
    ├── cors.php                   # Allow Workers origin
    └── sanctum.php                # JWT tokens
```

### FastAPI Processing Engine

```
fastapi-processor/
├── app/
│   ├── main.py                    # FastAPI app (JSON only, NO templates)
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── process.py         # POST /api/process
│   │       └── health.py          # GET /api/health
│   │
│   ├── services/
│   │   ├── audio_features_service.py   # librosa analysis
│   │   ├── openrouter_service.py       # AI analysis
│   │   └── sp404_export_service.py     # Format conversion
│   │
│   └── schemas/
│       ├── process_request.py     # Input schema
│       └── process_response.py    # Output schema
│
└── requirements.txt
```

---

## 🔄 Request Flow Examples

### 1. File Upload Flow

```typescript
// React Frontend
const uploadFile = async (file: File) => {
  // 1. Call Workers API
  const response = await fetch('https://api.sp404.app/api/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData
  })

  const { job_id, eta } = await response.json()

  // 2. Poll for status
  const interval = setInterval(async () => {
    const status = await fetch(`https://api.sp404.app/api/jobs/${job_id}`)
    const job = await status.json()

    if (job.status === 'completed') {
      clearInterval(interval)
      // Refresh sample list
      queryClient.invalidateQueries(['samples'])
    }
  }, 5000) // Poll every 5 seconds
}
```

```typescript
// Cloudflare Worker
app.post('/api/upload', async (c) => {
  // 1. Validate auth
  const user = await validateJWT(c.req.header('Authorization'))

  // 2. Check quota
  const quota = await checkQuota(c.env.TURSO, user.id, user.tier)
  if (!quota.canUpload) {
    return c.json({ error: 'Quota exceeded' }, 429)
  }

  // 3. Validate file
  const formData = await c.req.formData()
  const file = formData.get('audio') as File

  if (file.size > 10 * 1024 * 1024) { // 10MB for free tier
    return c.json({ error: 'File too large' }, 413)
  }

  // 4. Upload to R2
  const jobId = crypto.randomUUID()
  const r2Key = `uploads-pending/${user.id}/${jobId}.wav`

  await c.env.R2_BUCKET.put(r2Key, file.stream(), {
    httpMetadata: { contentType: file.type }
  })

  // 5. Create job in Turso
  const eta = user.tier === 'pro'
    ? new Date(Date.now() + 5 * 60 * 1000)
    : new Date(Date.now() + 18 * 60 * 60 * 1000)

  await c.env.TURSO.execute({
    sql: `INSERT INTO processing_jobs (id, user_id, status, queue, file_key, estimated_completion)
          VALUES (?, ?, 'pending', ?, ?, ?)`,
    args: [jobId, user.id, user.tier === 'pro' ? 'pro-tier' : 'free-tier', r2Key, eta.toISOString()]
  })

  // 6. Push to queue
  await c.env.PROCESSING_QUEUE.send({
    jobId,
    userId: user.id,
    fileKey: r2Key,
    tier: user.tier
  })

  // 7. Return response
  return c.json({
    job_id: jobId,
    status: 'pending',
    estimated_completion: eta.toISOString()
  })
})
```

### 2. Queue Consumer (Cloudflare Worker)

```typescript
// workers-api/src/consumer.ts
export default {
  async queue(batch: MessageBatch<ProcessingJob>, env: Env) {
    for (const message of batch.messages) {
      const { jobId, userId, fileKey, tier } = message.body

      try {
        // 1. Update job status
        await env.TURSO.execute({
          sql: 'UPDATE processing_jobs SET status = ?, started_at = ? WHERE id = ?',
          args: ['processing', new Date().toISOString(), jobId]
        })

        // 2. Generate signed URL for FastAPI
        const signedUrl = await env.R2_BUCKET.createSignedUrl(fileKey, {
          expiresIn: 3600 // 1 hour
        })

        // 3. Call FastAPI
        const response = await fetch('https://fastapi-processor.railway.app/api/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            file_url: signedUrl,
            user_id: userId,
            tier: tier,
            options: {
              ai_analysis: true,
              model: tier === 'pro' ? 'qwen/qwen3-235b' : 'qwen/qwen3-7b'
            }
          })
        })

        const result = await response.json()

        // 4. Save results to Turso
        const sampleId = crypto.randomUUID()

        await env.TURSO.execute({
          sql: `INSERT INTO samples (id, user_id, filename, file_url, duration, sample_rate, ai_analysis_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)`,
          args: [
            sampleId,
            userId,
            fileKey.split('/').pop(),
            fileKey,
            result.audio_features.duration,
            result.audio_features.sample_rate,
            JSON.stringify(result.ai_analysis)
          ]
        })

        // 5. Update job status
        await env.TURSO.execute({
          sql: 'UPDATE processing_jobs SET status = ?, completed_at = ?, sample_id = ? WHERE id = ?',
          args: ['completed', new Date().toISOString(), sampleId, jobId]
        })

        // 6. Send notification (email or webhook)
        await sendNotification(env, userId, jobId, sampleId)

        // 7. Acknowledge message
        message.ack()

      } catch (error) {
        // Mark as failed and retry
        await env.TURSO.execute({
          sql: 'UPDATE processing_jobs SET status = ?, error = ? WHERE id = ?',
          args: ['failed', error.message, jobId]
        })

        message.retry()
      }
    }
  }
}
```

### 3. Sample Library (Fast Edge Query)

```typescript
// Cloudflare Worker
app.get('/api/samples', async (c) => {
  const user = await validateJWT(c.req.header('Authorization'))

  // Query Turso at edge (super fast!)
  const samples = await c.env.TURSO.execute({
    sql: `SELECT s.*, af.bpm, af.musical_key
          FROM samples s
          LEFT JOIN audio_features af ON s.id = af.sample_id
          WHERE s.user_id = ?
          ORDER BY s.created_at DESC
          LIMIT 50`,
    args: [user.id]
  })

  return c.json(samples.rows)
})
```

```tsx
// React Frontend
const SampleLibrary = () => {
  const { data: samples, isLoading } = useQuery({
    queryKey: ['samples'],
    queryFn: async () => {
      const res = await fetch('https://api.sp404.app/api/samples', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      return res.json()
    }
  })

  if (isLoading) return <Spinner />

  return (
    <div className="grid grid-cols-3 gap-4">
      {samples.map(sample => (
        <SampleCard key={sample.id} sample={sample} />
      ))}
    </div>
  )
}
```

---

## 💰 Cost Analysis (Final)

### Infrastructure Costs

**Cloudflare** (Frontend + Edge API):
- Pages: Free (unlimited bandwidth!)
- Workers: Free (100K requests/day, then $0.50/million)
- R2: $0.015/GB storage, $0 egress
- Queues: Free (1M operations/month)
- **Total**: ~$5/mo for 10K users

**Laravel** (Railway or Fly.io):
- $5/mo base (hobby tier)
- Scales to $20/mo under load
- **Total**: $5-20/mo

**FastAPI** (Railway or Fly.io):
- $5/mo base
- Auto-scales to $20/mo
- **Total**: $5-20/mo

**Turso** (Database):
- Free tier: 500MB, 1M row reads/month
- Paid: $29/mo for 10GB
- **Total**: $0-29/mo

**Redis** (if not using Cloudflare Queues):
- Upstash free tier: 10K commands/day
- Paid: $10/mo
- **Total**: $0-10/mo (optional)

### Total Monthly Cost
- **Minimum**: $15/mo (all free tiers + minimal paid)
- **At Scale** (1000s of users): $50-80/mo

### Break-Even Analysis
- Free tier user cost: ~$0.30/mo (AI + compute)
- Pro tier user cost: ~$10/mo
- Pro tier revenue: $9.99/mo

**Break-even**: 5-10 pro users ($50-100 MRR)

---

## 🚀 Deployment Guide

### 1. Deploy React Frontend

```bash
# Build and deploy to Cloudflare Pages
cd react-sp404
npm run build
npx wrangler pages publish dist

# Configure custom domain
# Settings → Custom domains → sp404.app
```

### 2. Deploy Cloudflare Workers

```bash
# Deploy API workers
cd workers-api
npx wrangler deploy

# Set secrets
npx wrangler secret put TURSO_URL
npx wrangler secret put TURSO_AUTH_TOKEN
npx wrangler secret put JWT_SECRET

# Configure bindings in wrangler.toml
[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "sp404-samples"

[[queues.producers]]
binding = "PROCESSING_QUEUE"
queue = "audio-processing"
```

### 3. Deploy Laravel API

```bash
# Deploy to Railway
cd laravel-sp404
railway init
railway up

# Set environment variables
railway vars set APP_URL=https://api-sp404.railway.app
railway vars set DATABASE_URL=<turso-url>
railway vars set STRIPE_KEY=<stripe-key>
```

### 4. Deploy FastAPI Processor

```bash
# Deploy to Railway (separate service)
cd fastapi-processor
railway init
railway up

# Set environment variables
railway vars set OPENROUTER_API_KEY=<key>
```

---

## 📋 Next Steps

Which component should we build first?

**A)** **Cloudflare Workers API** (edge routing, upload, queries)
   - Hono router setup
   - R2 upload handler
   - Turso client integration
   - JWT auth middleware

**B)** **React Frontend** (SPA with React Query)
   - Vite + TypeScript setup
   - File upload component
   - Sample library with infinite scroll
   - Job status polling

**C)** **Laravel API** (auth, billing, business logic)
   - Sanctum auth endpoints
   - Cashier billing setup
   - User management
   - CORS for Workers

**D)** **FastAPI Simplification** (remove all HTML, pure JSON API)
   - Remove templates/HTMX
   - Single `/api/process` endpoint
   - Health check endpoint
   - Stateless design

**E)** **Queue Consumer** (Cloudflare Worker that processes queue)
   - Queue message handler
   - FastAPI integration
   - Turso updates
   - Error handling

This is the **production architecture** - edge-first, globally fast, cost-efficient, and scales to millions of users. Which piece should we start building?
