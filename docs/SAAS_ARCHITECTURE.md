# SP404MK2 Sample Agent - SaaS Architecture

**Date**: 2025-11-15
**Status**: Design Proposal for Multi-Tenant Edge Deployment

---

## 🎯 Architecture Overview

Queue-based async processing with edge delivery for global performance and cost control.

### Core Principles
1. **Async Processing**: No instant results, queue-based with SLA tiers
2. **Resource Limits**: File size, bandwidth, processing quotas per tier
3. **Edge Delivery**: Fast query/playback via Cloudflare + Turso + R2
4. **Cost Control**: Limits prevent runaway AI/compute costs

---

## 🏗️ System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge Layer                    │
├─────────────────────────────────────────────────────────────┤
│  Workers API (TypeScript)                                   │
│  ├─ POST /api/upload                                        │
│  │  ├─ Validate file (size, format, duration)              │
│  │  ├─ Check user quota (daily/monthly limits)             │
│  │  ├─ Upload to R2 /uploads-pending/                      │
│  │  ├─ Create job record in Turso                          │
│  │  ├─ Push to queue (free-tier or pro-tier)              │
│  │  └─ Return: { job_id, status, estimated_completion }    │
│  │                                                          │
│  ├─ GET /api/jobs/{job_id}                                 │
│  │  └─ Query Turso for job status                          │
│  │                                                          │
│  ├─ GET /api/samples                                        │
│  │  └─ Query Turso, return processed samples only          │
│  │                                                          │
│  └─ GET /api/samples/{id}/play                             │
│     └─ Return R2 public URL (CDN-cached)                   │
│                                                             │
│  Turso Database (libSQL, edge-replicated)                  │
│  ├─ users (id, email, tier, quota_used, quota_limit)       │
│  ├─ processing_jobs (id, user_id, status, queue, eta)      │
│  ├─ samples (id, user_id, file_url, metadata, created_at)  │
│  └─ audio_features (sample_id, bpm, key, spectral_data)    │
│                                                             │
│  R2 Storage (Object Storage)                               │
│  ├─ /uploads-pending/{user_id}/{job_id}.wav (24hr TTL)    │
│  ├─ /processed/{user_id}/{sample_id}.wav (permanent)      │
│  └─ /exports/{user_id}/{export_id}.zip (7-day TTL)        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Message Queue Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Cloudflare Queues (or BullMQ on Redis)                    │
│  ├─ free-tier-queue                                         │
│  │  ├─ FIFO processing                                      │
│  │  ├─ Low priority                                         │
│  │  └─ SLA: 12-24 hours                                     │
│  │                                                          │
│  └─ pro-tier-queue                                          │
│     ├─ Priority processing                                  │
│     ├─ Dedicated workers                                    │
│     └─ SLA: <5 minutes                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Processing Workers (VPS/Railway)               │
├─────────────────────────────────────────────────────────────┤
│  Python Worker Service (FastAPI + Celery/Dramatiq)         │
│  ├─ Poll queue for pending jobs                            │
│  ├─ Download file from R2 /uploads-pending/                │
│  ├─ Validate audio (duration, sample rate, corrupted)      │
│  ├─ Run audio analysis:                                     │
│  │  ├─ librosa: BPM, key, spectral features                │
│  │  ├─ OpenRouter: AI vibe analysis (rate-limited)         │
│  │  └─ Cost tracking: Log to Turso                         │
│  ├─ Upload processed file to R2 /processed/                │
│  ├─ Write metadata to Turso (samples + audio_features)     │
│  ├─ Update job status: "completed"                         │
│  ├─ Send notification (webhook or email)                   │
│  └─ Delete from /uploads-pending/                          │
│                                                             │
│  Resource Management:                                       │
│  ├─ Free tier: Max 10 concurrent workers                   │
│  ├─ Pro tier: Max 50 concurrent workers (dedicated)        │
│  ├─ Auto-scale: Spawn workers based on queue depth         │
│  └─ Cost limits: Skip AI analysis if budget exceeded       │
│                                                             │
│  Deployment:                                                │
│  ├─ Railway: Auto-scaling, $5-20/mo for free tier load    │
│  ├─ Fly.io: Edge regions, similar pricing                  │
│  └─ Your VPS: Full control, cheapest at scale              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Tiered Pricing Model

### Free Tier (Forever Free)

**Limits**:
- **Uploads**: 10 files/day, 10MB max per file, 60s max duration
- **Storage**: 100MB total, 30-day retention (auto-delete old files)
- **Processing**: 12-24 hour SLA (FIFO queue)
- **Features**:
  - Basic audio analysis (BPM, key, spectral)
  - AI vibe analysis (Qwen-7B only, ~$0.00001/file)
  - No batch processing
  - No SP-404 export

**Cost to You**: ~$0.001/file (AI only)
**Monthly Cost**: ~$0.30/user (assuming 10 files/day)

### Pro Tier ($9.99/mo or $99/year)

**Limits**:
- **Uploads**: 1,000 files/month, 100MB max per file, 5min duration
- **Storage**: 10GB total, permanent retention
- **Processing**: <5 minute SLA (priority queue)
- **Features**:
  - Full audio analysis
  - AI vibe analysis (all models: Qwen-7B, Qwen-235B)
  - Batch processing (up to 100 files at once)
  - SP-404MK2 export (48kHz/16-bit WAV/AIFF)
  - API access (1000 requests/day)
- **Free Trial**: 1 day of instant processing (runs on your VPS)

**Cost to You**: ~$2-5/user/month (heavy AI usage)
**Profit**: $5-8/user/month

### Enterprise Tier (Custom Pricing)

**Features**:
- **Unlimited**: Custom quotas negotiated
- **SLA**: <1 minute (dedicated workers)
- **API**: Full REST API, unlimited requests
- **White Label**: Custom branding, subdomain
- **Support**: Priority email + Slack channel

**Pricing**: $99-499/mo based on usage

---

## 🚦 Upload Flow with Validation

### 1. Client Uploads File

```javascript
// Frontend (HTMX + Alpine.js)
<form hx-post="/api/upload"
      hx-encoding="multipart/form-data"
      x-data="{ uploading: false, progress: 0 }">

  <input type="file" name="audio"
         accept="audio/wav,audio/mp3,audio/aiff"
         @change="uploading = true">

  <div x-show="uploading">
    <progress :value="progress" max="100"></progress>
    <p>Uploading... This will take 12-24 hours to process.</p>
  </div>
</form>
```

### 2. Workers API Validates

```typescript
// Cloudflare Worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const formData = await request.formData()
    const file = formData.get('audio') as File

    // 1. Check file size
    if (file.size > 10 * 1024 * 1024) { // 10MB for free tier
      return new Response('File too large (max 10MB)', { status: 413 })
    }

    // 2. Check file format
    if (!['audio/wav', 'audio/mpeg', 'audio/aiff'].includes(file.type)) {
      return new Response('Invalid format (WAV, MP3, AIFF only)', { status: 400 })
    }

    // 3. Check user quota (query Turso)
    const user = await getUser(request.headers.get('Authorization'))
    const today = new Date().toISOString().split('T')[0]
    const uploadsToday = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM processing_jobs WHERE user_id = ? AND DATE(created_at) = ?'
    ).bind(user.id, today).first()

    if (user.tier === 'free' && uploadsToday.count >= 10) {
      return new Response('Daily limit reached (10 files/day)', { status: 429 })
    }

    // 4. Upload to R2
    const jobId = crypto.randomUUID()
    const r2Key = `uploads-pending/${user.id}/${jobId}.${file.name.split('.').pop()}`
    await env.R2_BUCKET.put(r2Key, file.stream(), {
      httpMetadata: { contentType: file.type },
      customMetadata: { userId: user.id, tier: user.tier }
    })

    // 5. Create job in Turso
    const queue = user.tier === 'pro' ? 'pro-tier-queue' : 'free-tier-queue'
    const eta = user.tier === 'pro' ?
      new Date(Date.now() + 5 * 60 * 1000) : // 5 minutes
      new Date(Date.now() + 18 * 60 * 60 * 1000) // 18 hours

    await env.DB.prepare(`
      INSERT INTO processing_jobs (id, user_id, status, queue, file_key, estimated_completion)
      VALUES (?, ?, 'pending', ?, ?, ?)
    `).bind(jobId, user.id, queue, r2Key, eta.toISOString()).run()

    // 6. Push to queue
    await env.QUEUE.send({
      jobId,
      userId: user.id,
      fileKey: r2Key,
      tier: user.tier
    })

    // 7. Return response
    return new Response(JSON.stringify({
      job_id: jobId,
      status: 'pending',
      estimated_completion: eta.toISOString(),
      message: user.tier === 'pro' ?
        'Processing will complete in ~5 minutes' :
        'Processing will complete in 12-24 hours. Upgrade to Pro for instant results!'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
}
```

### 3. Worker Processes Job

```python
# Python Worker (VPS/Railway)
import asyncio
from dramatiq import actor
from turso import TursoClient
from r2 import R2Client

@actor(queue_name='free-tier-queue', max_retries=3)
def process_audio_job(job_id: str, user_id: str, file_key: str, tier: str):
    """Process audio file with librosa + AI analysis."""

    # 1. Update status
    db.execute(
        "UPDATE processing_jobs SET status = 'processing', started_at = ? WHERE id = ?",
        (datetime.utcnow(), job_id)
    )

    # 2. Download from R2
    file_bytes = r2.download(file_key)
    local_path = f'/tmp/{job_id}.wav'
    with open(local_path, 'wb') as f:
        f.write(file_bytes)

    # 3. Validate audio
    try:
        y, sr = librosa.load(local_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        # Check duration limits
        max_duration = 300 if tier == 'pro' else 60  # 5min vs 60s
        if duration > max_duration:
            raise ValueError(f'Duration {duration}s exceeds {max_duration}s limit')
    except Exception as e:
        db.execute(
            "UPDATE processing_jobs SET status = 'failed', error = ? WHERE id = ?",
            (str(e), job_id)
        )
        r2.delete(file_key)
        return

    # 4. Run audio analysis
    features = await audio_features_service.analyze(local_path)

    # 5. Run AI analysis (with cost tracking)
    user_prefs = await preferences_service.get_preferences(user_id)
    model = 'qwen/qwen3-235b' if tier == 'pro' else 'qwen/qwen3-7b'

    vibe = await openrouter_service.analyze_vibe(
        audio_features=features,
        model=model,
        user_id=user_id
    )

    # 6. Upload processed file to permanent storage
    processed_key = f'processed/{user_id}/{job_id}.wav'
    r2.copy(file_key, processed_key)
    r2.delete(file_key)  # Clean up pending

    # 7. Save to database
    sample_id = db.execute("""
        INSERT INTO samples (user_id, filename, file_url, duration, sample_rate)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """, (user_id, f'{job_id}.wav', processed_key, duration, sr)).fetchone()[0]

    db.execute("""
        INSERT INTO audio_features (sample_id, bpm, musical_key, spectral_centroid, ...)
        VALUES (?, ?, ?, ?, ...)
    """, (sample_id, features.bpm, features.key, features.spectral_centroid))

    # 8. Update job status
    db.execute(
        "UPDATE processing_jobs SET status = 'completed', completed_at = ? WHERE id = ?",
        (datetime.utcnow(), job_id)
    )

    # 9. Send notification (webhook or email)
    await notify_user(user_id, job_id, sample_id)
```

---

## 💾 Database Schema (Turso)

```sql
-- Users and quotas
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free', -- free, pro, enterprise
    quota_used_mb REAL DEFAULT 0,
    quota_limit_mb REAL DEFAULT 100, -- 100MB for free, 10GB for pro
    daily_uploads_count INTEGER DEFAULT 0,
    daily_uploads_reset_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processing jobs queue
CREATE TABLE processing_jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL, -- pending, processing, completed, failed
    queue TEXT NOT NULL, -- free-tier-queue, pro-tier-queue
    file_key TEXT NOT NULL, -- R2 object key
    estimated_completion TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Processed samples (same as current schema)
CREATE TABLE samples (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_url TEXT NOT NULL, -- R2 public URL
    duration REAL,
    sample_rate INTEGER,
    ai_analysis_json TEXT, -- Store vibe analysis
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Audio features (same as current schema)
CREATE TABLE audio_features (
    id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    bpm REAL,
    bpm_confidence REAL,
    musical_key TEXT,
    scale TEXT,
    spectral_centroid REAL,
    spectral_rolloff REAL,
    -- ... (all existing fields)
    FOREIGN KEY (sample_id) REFERENCES samples(id)
);

-- Cost tracking (same as current schema)
CREATE TABLE api_usage (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    model TEXT NOT NULL,
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost_usd REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_jobs_user_status ON processing_jobs(user_id, status);
CREATE INDEX idx_jobs_queue_status ON processing_jobs(queue, status);
CREATE INDEX idx_samples_user ON samples(user_id);
CREATE INDEX idx_usage_user_date ON api_usage(user_id, created_at);
```

---

## 📈 Cost Analysis (Per User)

### Free Tier User (10 files/day)

**Monthly Costs**:
- **R2 Storage**: 100MB × $0.015/GB = $0.0015/mo
- **R2 Requests**: 300 uploads × $0.36/million = $0.0001/mo
- **Turso DB**: Included in free tier (500 MB)
- **Workers**: 300 requests × free tier = $0
- **Queue**: Cloudflare Queues free tier = $0
- **VPS Processing**: $0.001/file × 300 = $0.30/mo
- **AI Costs** (Qwen-7B): $0.00001/file × 300 = $0.003/mo

**Total Cost**: ~$0.30/user/month
**Revenue**: $0
**Loss**: $0.30/user/month

**Break-even**: Need 1 pro user per 33 free users

### Pro Tier User (1000 files/month)

**Monthly Costs**:
- **R2 Storage**: 10GB × $0.015/GB = $0.15/mo
- **R2 Requests**: 1000 uploads × $0.36/million = $0.0004/mo
- **Turso DB**: Included in $29/mo plan (shared across users)
- **Workers**: 1000 requests × free tier = $0
- **Queue**: Priority queue (Cloudflare) = $0
- **VPS Processing**: $0.01/file × 1000 = $10/mo (heavy AI)
- **AI Costs** (Qwen-235B): $0.00005/file × 1000 = $0.05/mo

**Total Cost**: ~$10.20/user/month
**Revenue**: $9.99/month
**Loss**: $0.21/user/month (near break-even!)

**Profit Strategy**:
- Upsell to annual ($99/year = $8.25/mo) for guaranteed profit
- Limit free tier AI to Qwen-7B only
- Charge extra for Qwen-235B ($0.01/file for deep analysis)

---

## 🚀 Deployment Strategy

### Phase 1: MVP Launch (Month 1-2)

**Stack**:
- **Frontend**: Cloudflare Pages (free)
- **API**: Cloudflare Workers (free tier: 100K requests/day)
- **Database**: Turso free tier (500MB, edge replication)
- **Storage**: Cloudflare R2 (pay-as-you-go, ~$1/mo to start)
- **Queue**: Cloudflare Queues (beta, free)
- **Workers**: Single Railway instance ($5/mo)

**Features**:
- Free tier only (validate demand)
- Email auth (Clerk or Auth0 free tier)
- Basic audio analysis (librosa only, no AI)
- 10 files/day, 10MB limit

**Goal**: 100 active users, validate product-market fit

### Phase 2: Pro Tier (Month 3-4)

**Add**:
- AI vibe analysis (OpenRouter Qwen-7B)
- Pro tier with priority queue
- Stripe billing integration
- Email notifications (Resend free tier)

**Goal**: 10 paying users ($100 MRR)

### Phase 3: Scale (Month 5-6)

**Add**:
- Auto-scaling workers (Railway or Fly.io)
- Advanced AI models (Qwen-235B for pro)
- Batch processing
- SP-404MK2 export

**Goal**: 100 paying users ($1000 MRR)

---

## 🛡️ Rate Limiting & Abuse Prevention

### File Upload Limits

```typescript
// Cloudflare Worker
const LIMITS = {
  free: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    maxDuration: 60, // seconds
    dailyUploads: 10,
    totalStorage: 100 * 1024 * 1024 // 100MB
  },
  pro: {
    maxFileSize: 100 * 1024 * 1024, // 100MB
    maxDuration: 300, // 5 minutes
    monthlyUploads: 1000,
    totalStorage: 10 * 1024 * 1024 * 1024 // 10GB
  }
}

async function checkQuota(userId: string, tier: string, fileSize: number) {
  const limit = LIMITS[tier]

  // Check file size
  if (fileSize > limit.maxFileSize) {
    throw new Error(`File too large (max ${limit.maxFileSize / 1024 / 1024}MB)`)
  }

  // Check daily/monthly uploads
  const period = tier === 'free' ? 'DAY' : 'MONTH'
  const count = await db.execute(`
    SELECT COUNT(*) as count
    FROM processing_jobs
    WHERE user_id = ? AND created_at >= datetime('now', '-1 ${period}')
  `, [userId])

  if (count.rows[0].count >= limit.dailyUploads) {
    throw new Error(`Upload limit reached (${limit.dailyUploads}/${period})`)
  }

  // Check total storage
  const storage = await db.execute(`
    SELECT SUM(file_size) as total
    FROM samples
    WHERE user_id = ?
  `, [userId])

  if (storage.rows[0].total + fileSize > limit.totalStorage) {
    throw new Error(`Storage limit reached (${limit.totalStorage / 1024 / 1024}MB)`)
  }
}
```

### AI Cost Limits

```python
# Python Worker
async def check_ai_budget(user_id: str, model: str) -> bool:
    """Prevent runaway AI costs."""

    # Get user's monthly AI spend
    result = db.execute("""
        SELECT SUM(cost_usd) as total
        FROM api_usage
        WHERE user_id = ? AND created_at >= datetime('now', '-30 days')
    """, (user_id,)).fetchone()

    monthly_spend = result['total'] or 0.0

    # Set budget limits
    BUDGET_LIMITS = {
        'free': 0.10,  # $0.10/month max
        'pro': 5.00,   # $5/month max
        'enterprise': 100.00
    }

    user = get_user(user_id)
    if monthly_spend >= BUDGET_LIMITS[user.tier]:
        # Log warning
        logger.warning(f'User {user_id} exceeded AI budget: ${monthly_spend}')

        # Degrade gracefully - skip AI analysis
        return False

    return True
```

---

## 📧 Notification System

### Webhook When Job Completes

```python
# Python Worker
async def notify_user(user_id: str, job_id: str, sample_id: str):
    """Notify user when processing completes."""

    user = await get_user(user_id)

    # Option 1: Webhook (for API users)
    if user.webhook_url:
        await httpx.post(user.webhook_url, json={
            'event': 'sample.processed',
            'job_id': job_id,
            'sample_id': sample_id,
            'play_url': f'https://yourdomain.com/samples/{sample_id}/play',
            'download_url': f'https://yourdomain.com/api/samples/{sample_id}/download'
        })

    # Option 2: Email (for web users)
    if user.email_notifications:
        await send_email(
            to=user.email,
            subject='Your sample is ready!',
            body=f'''
            Your audio file has been processed!

            View it here: https://yourdomain.com/samples/{sample_id}

            BPM: {sample.bpm}
            Key: {sample.key}
            Vibe: {sample.vibe_tags}
            '''
        )

    # Option 3: Push notification (future)
    # Option 4: WebSocket real-time update (if user online)
```

---

## 🎯 Migration from Current Local Setup

### Step 1: Add Job Queue to Current Code

```python
# backend/app/api/v1/endpoints/public.py

from dramatiq import actor
from app.services.hybrid_analysis_service import HybridAnalysisService

@router.post("/upload", response_class=HTMLResponse)
async def upload_sample_async(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Upload sample and queue for processing (FREE TIER: 12-24 hours)."""

    # 1. Validate file
    if file.size > 10 * 1024 * 1024:  # 10MB
        return HTMLResponse("File too large (max 10MB for free tier)", status_code=413)

    # 2. Save to temp storage
    file_path = f"backend/uploads-pending/{uuid4()}.wav"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 3. Create job record
    job = ProcessingJob(
        id=str(uuid4()),
        user_id="1",  # TODO: Get from auth
        status="pending",
        queue="free-tier-queue",
        file_key=file_path,
        estimated_completion=datetime.utcnow() + timedelta(hours=18)
    )
    db.add(job)
    await db.commit()

    # 4. Queue background task
    background_tasks.add_task(process_audio_job, job.id, job.file_key)

    # 5. Return immediate response
    return templates.TemplateResponse("upload-queued.html", {
        "request": {},
        "job_id": job.id,
        "eta": "12-24 hours",
        "message": "Your file is queued for processing. We'll email you when it's ready!"
    })
```

### Step 2: Deploy Workers to Railway

```bash
# Create new Railway project
railway init

# Add Python worker service
railway add

# Set environment variables
railway vars set DATABASE_URL=<turso-url>
railway vars set R2_ACCESS_KEY=<r2-key>
railway vars set OPENROUTER_API_KEY=<key>

# Deploy
railway up
```

### Step 3: Move to Cloudflare Edge (Optional)

Convert FastAPI routes to Workers, keep Python processing separate.

---

## 💡 Next Steps

Would you like me to:

**A)** Build the queue system into your current FastAPI backend (add async processing)?

**B)** Create a Cloudflare Workers API prototype with Turso + R2?

**C)** Design the pricing page and upgrade flow (Stripe integration)?

**D)** Build the job status polling UI (HTMX + Alpine.js)?

**E)** Set up the cost tracking dashboard for you to monitor margins?

This architecture keeps costs low (~$0.30/free user, ~$10/pro user) while delivering global performance. The key is the async queue - users expect processing time for audio analysis anyway!
