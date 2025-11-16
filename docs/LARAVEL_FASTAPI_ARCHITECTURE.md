# SP404MK2 Sample Agent - Laravel + FastAPI Architecture

**Date**: 2025-11-15
**Status**: Design Proposal - Separation of Concerns

---

## 🎯 Architecture Philosophy

**Laravel**: Web app layer (users, billing, queues, UI)
**FastAPI**: Processing engine (audio analysis, AI, compute)

### Why This Works
- ✅ Laravel = Battle-tested for SaaS (Cashier, Sanctum, Horizon)
- ✅ FastAPI = Pure processing API (stateless, fast, Python-native)
- ✅ Clear separation of concerns
- ✅ Scale independently (web vs workers)
- ✅ Best tool for each job

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge                          │
├─────────────────────────────────────────────────────────────┤
│  - CDN for Laravel assets                                   │
│  - R2 for audio file storage                                │
│  - DDoS protection                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Laravel Application                      │
│                  (Web Layer + Business Logic)               │
├─────────────────────────────────────────────────────────────┤
│  Web Routes (Blade or Inertia.js)                          │
│  ├─ /dashboard - User dashboard                            │
│  ├─ /upload - File upload form                             │
│  ├─ /samples - Sample library                              │
│  ├─ /samples/{id} - Sample details                         │
│  ├─ /billing - Subscription management (Cashier)           │
│  └─ /settings - User preferences                           │
│                                                             │
│  API Routes (Laravel Sanctum auth)                         │
│  ├─ POST /api/upload - Upload file, create job            │
│  ├─ GET /api/jobs/{id} - Job status polling               │
│  ├─ GET /api/samples - List user's samples                │
│  └─ GET /api/samples/{id}/download - Download sample      │
│                                                             │
│  Authentication (Laravel Sanctum)                          │
│  ├─ Session-based for web                                 │
│  └─ Token-based for API                                    │
│                                                             │
│  Billing (Laravel Cashier)                                 │
│  ├─ Stripe integration                                     │
│  ├─ Subscription management (Free/Pro/Enterprise)          │
│  ├─ Usage-based billing (overage charges)                 │
│  └─ Webhook handling (subscription updates)               │
│                                                             │
│  Queue Management (Laravel Queues)                         │
│  ├─ ProcessAudioJob (dispatched to Redis queue)           │
│  ├─ Priority queues: free-tier, pro-tier                  │
│  ├─ Rate limiting: 10/day (free), 1000/month (pro)       │
│  ├─ Job monitoring (Laravel Horizon dashboard)            │
│  └─ Failed job handling (auto-retry)                      │
│                                                             │
│  Database (MySQL or PostgreSQL via Turso libSQL)          │
│  ├─ users (auth, tier, quotas)                            │
│  ├─ subscriptions (Cashier schema)                        │
│  ├─ processing_jobs (status, queue, progress)             │
│  ├─ samples (metadata, R2 URLs)                           │
│  ├─ audio_features (BPM, key, spectral data)              │
│  └─ api_usage (cost tracking)                             │
│                                                             │
│  Storage (Cloudflare R2 via Laravel Filesystem)           │
│  ├─ config/filesystems.php - S3-compatible R2             │
│  ├─ Storage::disk('r2')->put()                            │
│  └─ Signed URLs for private files                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Redis Queue                              │
├─────────────────────────────────────────────────────────────┤
│  - free-tier queue (FIFO, delayed 12-24 hours)             │
│  - pro-tier queue (high priority, immediate)               │
│  - retry queue (failed jobs)                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Laravel Queue Workers                         │
│            (Polls Redis, calls FastAPI)                     │
├─────────────────────────────────────────────────────────────┤
│  ProcessAudioJob.php                                        │
│  ├─ 1. Get job from queue                                  │
│  ├─ 2. Update job status: "processing"                     │
│  ├─ 3. Generate R2 signed URL for file access              │
│  ├─ 4. Call FastAPI: POST /api/process                     │
│  │    {                                                     │
│  │      "file_url": "https://r2.../sample.wav",           │
│  │      "user_id": "123",                                  │
│  │      "tier": "pro",                                     │
│  │      "options": {                                       │
│  │        "ai_analysis": true,                            │
│  │        "model": "qwen/qwen3-235b",                     │
│  │        "export_sp404": false                           │
│  │      }                                                  │
│  │    }                                                    │
│  ├─ 5. Wait for FastAPI response                           │
│  ├─ 6. Save results to database                            │
│  ├─ 7. Update job status: "completed"                      │
│  ├─ 8. Trigger notification (email/webhook)                │
│  └─ 9. Clean up temp files                                 │
│                                                             │
│  Deployment:                                                │
│  ├─ php artisan queue:work --queue=pro-tier,free-tier     │
│  ├─ Supervisor to keep workers running                     │
│  └─ Laravel Horizon for monitoring                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Processing Engine                  │
│               (Stateless Audio Processing API)              │
├─────────────────────────────────────────────────────────────┤
│  POST /api/process                                          │
│  ├─ Download file from R2 signed URL                       │
│  ├─ Validate audio (format, duration, corrupted)           │
│  ├─ Run librosa analysis                                    │
│  │  ├─ BPM detection                                       │
│  │  ├─ Key detection                                       │
│  │  └─ Spectral features                                   │
│  ├─ Run OpenRouter AI analysis (if enabled)                │
│  │  ├─ Call OpenRouter API                                │
│  │  ├─ Track tokens/cost                                   │
│  │  └─ Return vibe analysis                                │
│  ├─ Export SP-404 format (if requested)                    │
│  │  ├─ Convert to 48kHz/16-bit                            │
│  │  └─ Upload to R2                                        │
│  └─ Return JSON response:                                   │
│     {                                                       │
│       "success": true,                                      │
│       "audio_features": { ... },                           │
│       "ai_analysis": { ... },                              │
│       "cost": 0.00005,                                     │
│       "processing_time": 3.2                               │
│     }                                                       │
│                                                             │
│  GET /api/health - Health check for queue workers          │
│                                                             │
│  Configuration:                                             │
│  ├─ No database connection (stateless!)                    │
│  ├─ No user management                                     │
│  ├─ Just processes files and returns results               │
│  └─ Can scale horizontally without coordination            │
│                                                             │
│  Deployment:                                                │
│  ├─ Railway / Fly.io (multiple regions)                    │
│  ├─ Auto-scaling based on queue depth                      │
│  └─ Internal-only API (not publicly accessible)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Laravel Project Structure

```
laravel-sp404/
├── app/
│   ├── Models/
│   │   ├── User.php
│   │   ├── ProcessingJob.php
│   │   ├── Sample.php
│   │   ├── AudioFeature.php
│   │   └── ApiUsage.php
│   │
│   ├── Jobs/
│   │   ├── ProcessAudioJob.php         # Main processing job
│   │   ├── CleanupTempFilesJob.php     # Delete old pending files
│   │   └── SendProcessingCompleteEmail.php
│   │
│   ├── Http/
│   │   ├── Controllers/
│   │   │   ├── UploadController.php    # File upload
│   │   │   ├── SampleController.php    # Sample CRUD
│   │   │   ├── JobController.php       # Job status API
│   │   │   └── BillingController.php   # Subscription management
│   │   │
│   │   └── Middleware/
│   │       ├── CheckUserQuota.php      # Enforce tier limits
│   │       └── TrackApiUsage.php       # Log API calls
│   │
│   ├── Services/
│   │   ├── FastApiService.php          # HTTP client for FastAPI
│   │   ├── QuotaService.php            # Check/enforce quotas
│   │   └── R2Service.php               # Cloudflare R2 wrapper
│   │
│   └── Notifications/
│       └── ProcessingComplete.php      # Email notification
│
├── database/
│   └── migrations/
│       ├── 2025_11_15_create_processing_jobs_table.php
│       ├── 2025_11_15_create_samples_table.php
│       ├── 2025_11_15_create_audio_features_table.php
│       └── 2025_11_15_create_api_usage_table.php
│
├── resources/
│   └── views/
│       ├── dashboard.blade.php
│       ├── samples/
│       │   ├── index.blade.php         # Sample library
│       │   └── show.blade.php          # Sample details
│       └── billing/
│           └── subscribe.blade.php     # Pricing page
│
├── routes/
│   ├── web.php                         # Web routes (Blade UI)
│   └── api.php                         # API routes (Sanctum auth)
│
└── config/
    ├── filesystems.php                 # R2 configuration
    ├── services.php                    # FastAPI endpoint
    └── cashier.php                     # Stripe configuration
```

---

## 🔧 Key Laravel Components

### 1. ProcessAudioJob (Queue Job)

```php
<?php

namespace App\Jobs;

use App\Models\ProcessingJob;
use App\Services\FastApiService;
use App\Services\R2Service;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

class ProcessAudioJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $tries = 3;
    public $timeout = 300; // 5 minutes max

    public function __construct(
        public ProcessingJob $job
    ) {}

    public function handle(FastApiService $fastApi, R2Service $r2)
    {
        // 1. Update job status
        $this->job->update([
            'status' => 'processing',
            'started_at' => now()
        ]);

        try {
            // 2. Generate signed URL for FastAPI to download file
            $signedUrl = $r2->getSignedUrl($this->job->file_key, 3600); // 1 hour

            // 3. Call FastAPI processing endpoint
            $response = $fastApi->process([
                'file_url' => $signedUrl,
                'user_id' => $this->job->user_id,
                'tier' => $this->job->user->tier,
                'options' => [
                    'ai_analysis' => $this->job->user->tier === 'pro',
                    'model' => $this->job->user->tier === 'pro'
                        ? 'qwen/qwen3-235b'
                        : 'qwen/qwen3-7b',
                    'export_sp404' => $this->job->export_sp404 ?? false
                ]
            ]);

            // 4. Save results to database
            $sample = Sample::create([
                'user_id' => $this->job->user_id,
                'filename' => basename($this->job->file_key),
                'file_url' => $this->job->file_key,
                'duration' => $response['audio_features']['duration'],
                'sample_rate' => $response['audio_features']['sample_rate'],
                'ai_analysis_json' => json_encode($response['ai_analysis']),
            ]);

            // 5. Save audio features
            $sample->audioFeatures()->create($response['audio_features']);

            // 6. Track API costs
            ApiUsage::create([
                'user_id' => $this->job->user_id,
                'model' => $response['model'],
                'tokens_input' => $response['tokens_input'],
                'tokens_output' => $response['tokens_output'],
                'cost_usd' => $response['cost'],
            ]);

            // 7. Update job status
            $this->job->update([
                'status' => 'completed',
                'completed_at' => now(),
                'sample_id' => $sample->id
            ]);

            // 8. Send notification
            $this->job->user->notify(new ProcessingComplete($sample));

        } catch (\Exception $e) {
            // Handle failure
            $this->job->update([
                'status' => 'failed',
                'error' => $e->getMessage()
            ]);

            throw $e; // Let Laravel queue retry
        }
    }
}
```

### 2. UploadController (File Upload)

```php
<?php

namespace App\Http\Controllers;

use App\Models\ProcessingJob;
use App\Services\R2Service;
use App\Services\QuotaService;
use App\Jobs\ProcessAudioJob;
use Illuminate\Http\Request;

class UploadController extends Controller
{
    public function store(Request $request, R2Service $r2, QuotaService $quota)
    {
        // 1. Validate request
        $request->validate([
            'audio' => 'required|file|mimes:wav,mp3,aiff|max:10240', // 10MB for free
        ]);

        $user = $request->user();

        // 2. Check quota
        $quota->checkCanUpload($user);

        // 3. Upload to R2
        $file = $request->file('audio');
        $path = $r2->uploadPending($file, $user->id);

        // 4. Create processing job
        $job = ProcessingJob::create([
            'user_id' => $user->id,
            'status' => 'pending',
            'queue' => $user->tier === 'pro' ? 'pro-tier' : 'free-tier',
            'file_key' => $path,
            'estimated_completion' => $user->tier === 'pro'
                ? now()->addMinutes(5)
                : now()->addHours(18),
        ]);

        // 5. Dispatch to queue with delay for free tier
        $delay = $user->tier === 'pro' ? null : now()->addHours(12);

        ProcessAudioJob::dispatch($job)
            ->onQueue($job->queue)
            ->delay($delay);

        // 6. Return response
        return response()->json([
            'job_id' => $job->id,
            'status' => 'pending',
            'estimated_completion' => $job->estimated_completion,
            'message' => $user->tier === 'pro'
                ? 'Processing will complete in ~5 minutes'
                : 'Processing will complete in 12-24 hours. Upgrade to Pro for instant results!'
        ]);
    }
}
```

### 3. FastApiService (HTTP Client)

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class FastApiService
{
    private string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = config('services.fastapi.url');
    }

    public function process(array $data): array
    {
        $response = Http::timeout(300) // 5 minutes
            ->post("{$this->baseUrl}/api/process", $data);

        if (!$response->successful()) {
            throw new \Exception('FastAPI processing failed: ' . $response->body());
        }

        return $response->json();
    }

    public function health(): bool
    {
        try {
            $response = Http::timeout(5)
                ->get("{$this->baseUrl}/api/health");

            return $response->successful();
        } catch (\Exception $e) {
            return false;
        }
    }
}
```

### 4. QuotaService (Tier Limits)

```php
<?php

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Cache;

class QuotaService
{
    private const LIMITS = [
        'free' => [
            'max_file_size' => 10 * 1024 * 1024, // 10MB
            'daily_uploads' => 10,
            'total_storage' => 100 * 1024 * 1024, // 100MB
        ],
        'pro' => [
            'max_file_size' => 100 * 1024 * 1024, // 100MB
            'monthly_uploads' => 1000,
            'total_storage' => 10 * 1024 * 1024 * 1024, // 10GB
        ]
    ];

    public function checkCanUpload(User $user): void
    {
        $limits = self::LIMITS[$user->tier];

        // Check daily/monthly upload count
        $period = $user->tier === 'free' ? 'day' : 'month';
        $count = $user->processingJobs()
            ->where('created_at', '>=', now()->{"sub{$period}"}())
            ->count();

        $maxUploads = $limits['daily_uploads'] ?? $limits['monthly_uploads'];

        if ($count >= $maxUploads) {
            throw new \Exception("Upload limit reached ({$maxUploads}/{$period})");
        }

        // Check total storage
        $totalStorage = $user->samples()->sum('file_size');

        if ($totalStorage >= $limits['total_storage']) {
            throw new \Exception("Storage limit reached");
        }
    }

    public function getRemainingQuota(User $user): array
    {
        $limits = self::LIMITS[$user->tier];
        $period = $user->tier === 'free' ? 'day' : 'month';

        $used = $user->processingJobs()
            ->where('created_at', '>=', now()->{"sub{$period}"}())
            ->count();

        $maxUploads = $limits['daily_uploads'] ?? $limits['monthly_uploads'];

        return [
            'used' => $used,
            'limit' => $maxUploads,
            'remaining' => $maxUploads - $used,
            'period' => $period
        ];
    }
}
```

### 5. Cashier Configuration (config/cashier.php)

```php
<?php

return [
    'key' => env('STRIPE_KEY'),
    'secret' => env('STRIPE_SECRET'),
    'webhook' => [
        'secret' => env('STRIPE_WEBHOOK_SECRET'),
        'tolerance' => env('STRIPE_WEBHOOK_TOLERANCE', 300),
    ],
];
```

### 6. Subscription Model

```php
<?php

namespace App\Models;

use Laravel\Cashier\Billable;

class User extends Authenticatable
{
    use Billable;

    public function tier(): string
    {
        if ($this->subscribed('pro')) {
            return 'pro';
        }

        if ($this->subscribed('enterprise')) {
            return 'enterprise';
        }

        return 'free';
    }

    public function canUpload(): bool
    {
        return app(QuotaService::class)
            ->getRemainingQuota($this)['remaining'] > 0;
    }
}
```

---

## 🐍 FastAPI Service (Simplified)

### No Database, No Users - Just Processing

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from app.services.audio_features_service import AudioFeaturesService
from app.services.openrouter_service import OpenRouterService
from app.services.sp404_export_service import SP404ExportService

app = FastAPI()

class ProcessRequest(BaseModel):
    file_url: str  # R2 signed URL
    user_id: str
    tier: str
    options: dict = {}

class ProcessResponse(BaseModel):
    success: bool
    audio_features: dict
    ai_analysis: dict | None = None
    cost: float = 0.0
    processing_time: float

@app.post("/api/process", response_model=ProcessResponse)
async def process_audio(request: ProcessRequest):
    """
    Process audio file from R2 URL.

    This is a STATELESS endpoint - no database, no user management.
    Laravel handles all of that.
    """
    import time
    start = time.time()

    try:
        # 1. Download file from R2 signed URL
        async with httpx.AsyncClient() as client:
            response = await client.get(request.file_url)
            response.raise_for_status()

        local_path = f"/tmp/{request.user_id}_{int(time.time())}.wav"
        with open(local_path, "wb") as f:
            f.write(response.content)

        # 2. Run audio analysis (librosa)
        audio_service = AudioFeaturesService()
        audio_features = await audio_service.analyze(local_path)

        # 3. Run AI analysis (if enabled)
        ai_analysis = None
        cost = 0.0

        if request.options.get('ai_analysis'):
            openrouter = OpenRouterService()
            model = request.options.get('model', 'qwen/qwen3-7b')

            ai_result = await openrouter.analyze_vibe(
                audio_features=audio_features.dict(),
                model=model
            )

            ai_analysis = ai_result['analysis']
            cost = ai_result['cost']

        # 4. Export SP-404 format (if requested)
        if request.options.get('export_sp404'):
            sp404_service = SP404ExportService()
            # ... export logic
            pass

        # 5. Return results
        return ProcessResponse(
            success=True,
            audio_features=audio_features.dict(),
            ai_analysis=ai_analysis,
            cost=cost,
            processing_time=time.time() - start
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

@app.get("/api/health")
async def health_check():
    """Health check for Laravel queue workers."""
    return {"status": "healthy", "service": "fastapi-audio-processor"}
```

---

## 🚀 Deployment Strategy

### Laravel (Web Layer)

```bash
# Laravel on Laravel Forge or Ploi
# - Managed server provisioning
# - Auto-deployment from GitHub
# - SSL, queues, horizon, scheduler all configured

# Or DIY with Railway/Fly.io
railway init
railway add # Add MySQL/PostgreSQL
railway add # Add Redis
railway up

# Environment variables
DATABASE_URL=mysql://...
REDIS_URL=redis://...
R2_ACCESS_KEY=...
FASTAPI_URL=https://fastapi-processor.railway.app
STRIPE_KEY=...
```

### FastAPI (Processing Engine)

```bash
# FastAPI on Railway (separate service)
railway init
railway up

# No database needed!
# Environment variables
OPENROUTER_API_KEY=...
R2_ACCESS_KEY=... # Only for reading signed URLs
```

### Queue Workers

```bash
# Laravel queue workers (on same server as Laravel)
php artisan queue:work --queue=pro-tier,free-tier --tries=3 --timeout=300

# Or use Laravel Horizon for better monitoring
php artisan horizon
```

---

## 💰 Cost Analysis (Revised)

### With Laravel + FastAPI

**Laravel Hosting** (Forge + DigitalOcean):
- $12/mo (DigitalOcean droplet)
- $19/mo (Forge management)
- **Total**: $31/mo (handles 1000s of users)

**FastAPI Processing** (Railway):
- $5/mo base (hobby tier)
- Scales to $20/mo under load
- **Total**: $5-20/mo

**Database** (Turso or PlanetScale):
- Free tier: 500MB (plenty for user/job data)
- Paid: $29/mo for 10GB
- **Total**: $0-29/mo

**Redis** (Upstash or Railway):
- Free tier: 10K commands/day
- Paid: $10/mo for unlimited
- **Total**: $0-10/mo

**R2 Storage**:
- $0.015/GB storage
- $0 egress (!)
- ~$5/mo for 100s of users
- **Total**: $5/mo

**Total Infrastructure**: $41-95/mo
**Break-even**: 5-10 pro users ($50-100 MRR)

---

## 🎯 Migration Path

### Phase 1: Set Up Laravel

```bash
# 1. Create new Laravel project
composer create-project laravel/laravel sp404-laravel
cd sp404-laravel

# 2. Install Cashier (Stripe)
composer require laravel/cashier

# 3. Install Sanctum (API auth)
php artisan install:api

# 4. Configure R2 storage
# Edit config/filesystems.php - add R2 disk

# 5. Create models and migrations
php artisan make:model ProcessingJob -m
php artisan make:model Sample -m
php artisan make:model AudioFeature -m

# 6. Create job
php artisan make:job ProcessAudioJob

# 7. Run migrations
php artisan migrate
```

### Phase 2: Configure FastAPI Endpoint

```python
# Modify current FastAPI to be processing-only
# Remove: User management, auth, database writes
# Keep: Audio processing, AI analysis
# Add: Single /api/process endpoint
```

### Phase 3: Connect Laravel to FastAPI

```php
// app/Services/FastApiService.php
// HTTP client to call FastAPI
```

### Phase 4: Set Up Billing

```bash
# Install Cashier
composer require laravel/cashier

# Publish migrations
php artisan vendor:publish --tag="cashier-migrations"
php artisan migrate

# Create pricing page
# resources/views/billing/subscribe.blade.php
```

---

## 📋 Next Steps

Would you like me to:

**A)** **Create the Laravel project skeleton** with all migrations, models, and jobs?

**B)** **Modify the existing FastAPI** to be a stateless processing endpoint?

**C)** **Build the Stripe billing integration** with Laravel Cashier?

**D)** **Set up the R2 configuration** for both Laravel and FastAPI?

**E)** **Create the deployment configs** for Railway/Forge?

This architecture is much cleaner! Laravel handles all the "business logic" (users, money, queues) and FastAPI is just a pure processing engine.
