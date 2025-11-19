# Detailed Migration Plan: Laravel Integration

**Timeline**: 8-12 weeks
**Status**: Ready for Phase 1 Kickoff
**Risk Level**: Medium (managed)

---

## Phase 1: Foundation Setup (Weeks 1-3)

### Week 1: Project & Database Setup

#### Task 1.1: Create Laravel Project Structure
**Duration**: 4 hours
**Owner**: Laravel Architect

**Steps**:
```bash
# 1. Create Laravel project at project root
composer create-project laravel/laravel laravel-sp404 --no-interaction

# 2. Install key packages
cd laravel-sp404
composer require laravel/fortify laravel/sanctum laravel/cashier laravel-queue/tinker

# 3. Publish config files
php artisan vendor:publish --provider="Laravel\Fortify\FortifyServiceProvider"
php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"
php artisan vendor:publish --provider="Laravel\Cashier\CashierServiceProvider"

# 4. Create .env configuration
cp .env.example .env
php artisan key:generate
```

**Deliverables**:
- [ ] `laravel-sp404/` directory structure
- [ ] All packages installed
- [ ] `.env` configured for PostgreSQL
- [ ] APP_KEY generated

---

#### Task 1.2: Configure Database Connection
**Duration**: 2 hours
**Owner**: DevOps Architect

**Steps**:
```bash
# 1. Update .env file
# .env configuration:
DB_CONNECTION=pgsql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=sp404_samples
DB_USERNAME=sp404_user
DB_PASSWORD=changeme123

# 2. Test connection
php artisan tinker
>>> DB::connection()->getPdo()

# 3. Run migrations
php artisan migrate
```

**Validation**:
- [ ] PostgreSQL connection successful
- [ ] Base Laravel migrations complete
- [ ] Users table created
- [ ] Migrations table exists

---

#### Task 1.3: Create User Model & Migrations
**Duration**: 3 hours
**Owner**: Laravel Architect

**Steps**:
```bash
# 1. Generate model with migration
php artisan make:model User --migration --factory --seeder

# 2. Update migration (database/migrations/xxxx_create_users_table.php)
# Add fields:
# - email (unique)
# - password_hash (from Laravel's default)
# - first_name
# - last_name
# - avatar_url
# - email_verified_at
# - created_at, updated_at

# 3. Generate additional migrations
php artisan make:migration create_subscriptions_table
php artisan make:migration create_user_preferences_table
php artisan make:migration add_user_id_to_existing_tables

# 4. Run all migrations
php artisan migrate
```

**Deliverables**:
- [ ] User model (app/Models/User.php)
- [ ] Subscription model
- [ ] UserPreferences model
- [ ] All migrations executed
- [ ] Tables exist in PostgreSQL

**SQL Verification**:
```sql
-- Verify tables exist
\dt  -- in psql

-- Verify user columns
\d users;
\d subscriptions;
```

---

#### Task 1.4: Setup Authentication Middleware
**Duration**: 3 hours
**Owner**: Laravel Architect

**Steps**:
```bash
# 1. Setup Fortify (headless auth)
php artisan fortify:install

# 2. Create AuthController
php artisan make:controller Api/AuthController

# 3. Configure routes (routes/api.php)
Route::post('/auth/register', [AuthController::class, 'register']);
Route::post('/auth/login', [AuthController::class, 'login']);
Route::post('/auth/logout', [AuthController::class, 'logout'])->middleware('auth:sanctum');
Route::post('/auth/refresh', [AuthController::class, 'refresh']);

# 4. Create JWT utility class
php artisan make:class Services/JwtService
```

**Files to Create**:
- [ ] `app/Http/Controllers/Api/AuthController.php`
- [ ] `app/Services/JwtService.php`
- [ ] JWT key pair (`storage/keys/jwt-private.pem`, `storage/keys/jwt-public.pem`)

---

#### Task 1.5: Generate JWT Key Pair
**Duration**: 1 hour
**Owner**: DevOps Architect

**Steps**:
```bash
# 1. Create keys directory
mkdir -p storage/keys
chmod 700 storage/keys

# 2. Generate RSA key pair for RS256 signing
openssl genrsa -out storage/keys/jwt-private.pem 4096
openssl rsa -in storage/keys/jwt-private.pem -pubout -out storage/keys/jwt-public.pem

# 3. Set permissions
chmod 600 storage/keys/jwt-private.pem
chmod 644 storage/keys/jwt-public.pem

# 4. Add to .gitignore (keep keys local, not in repo)
echo "storage/keys/*" >> .gitignore
```

**Validation**:
- [ ] Private key exists and is readable
- [ ] Public key exists and is readable
- [ ] Keys are in PEM format

---

### Week 2: Authentication Implementation

#### Task 2.1: Implement JWT Token Service
**Duration**: 4 hours
**Owner**: Laravel Architect

**File**: `app/Services/JwtService.php`

```php
<?php

namespace App\Services;

use Firebase\JWT\JWT;
use Firebase\JWT\Key;

class JwtService
{
    private string $privateKey;
    private string $publicKey;
    private string $algo = 'RS256';
    private int $ttl = 3600; // 1 hour

    public function __construct()
    {
        $this->privateKey = file_get_contents(storage_path('keys/jwt-private.pem'));
        $this->publicKey = file_get_contents(storage_path('keys/jwt-public.pem'));
    }

    public function generateToken(array $payload): string
    {
        $payload['iat'] = time();
        $payload['exp'] = time() + $this->ttl;

        return JWT::encode($payload, $this->privateKey, $this->algo);
    }

    public function verifyToken(string $token): array|null
    {
        try {
            return (array) JWT::decode(
                $token,
                new Key($this->publicKey, $this->algo)
            );
        } catch (\Exception $e) {
            return null;
        }
    }

    public function getPublicKey(): string
    {
        return $this->publicKey;
    }
}
```

**Deliverables**:
- [ ] JwtService class created and tested
- [ ] Token generation working
- [ ] Token verification working

---

#### Task 2.2: Implement AuthController
**Duration**: 6 hours
**Owner**: Laravel Architect

**File**: `app/Http/Controllers/Api/AuthController.php`

**Methods to Implement**:
1. `register(Request $request)` - Create new user
2. `login(Request $request)` - Authenticate and issue token
3. `logout(Request $request)` - Revoke token
4. `refresh(Request $request)` - Issue new token
5. `publicKey()` - Share public key for verification

**Validation Rules**:
```php
// Register
'email' => 'required|email|unique:users',
'password' => 'required|min:8|confirmed',
'first_name' => 'required|string',
'last_name' => 'required|string'

// Login
'email' => 'required|email|exists:users',
'password' => 'required|min:8'
```

**Response Format**:
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tier": "free"
  },
  "expires_in": 3600
}
```

**Deliverables**:
- [ ] AuthController fully implemented
- [ ] All endpoints returning correct responses
- [ ] Validation working
- [ ] Password hashing (bcrypt)

---

#### Task 2.3: Email Verification Setup
**Duration**: 3 hours
**Owner**: Laravel Architect

**Steps**:
```bash
# 1. Create mailable
php artisan make:mail VerifyEmail

# 2. Create verification middleware
php artisan make:middleware EnsureEmailIsVerified

# 3. Register middleware in auth.php
'verify' => \App\Http\Middleware\EnsureEmailIsVerified::class,

# 4. Add route for verification
Route::get('/verify-email/{id}/{hash}', [AuthController::class, 'verifyEmail'])
    ->name('verification.verify');
```

**Deliverables**:
- [ ] Email verification mailable
- [ ] Verification middleware
- [ ] Verification endpoint
- [ ] Email templates

---

#### Task 2.4: Create Unit Tests
**Duration**: 4 hours
**Owner**: QA Architect

**Test Files**:
- `tests/Unit/Services/JwtServiceTest.php`
- `tests/Feature/Auth/RegisterTest.php`
- `tests/Feature/Auth/LoginTest.php`
- `tests/Feature/Auth/LogoutTest.php`
- `tests/Feature/Auth/RefreshTest.php`

**Minimum Test Coverage**:
- [ ] JWT generation and verification
- [ ] Register with valid credentials
- [ ] Register with invalid credentials
- [ ] Login with correct password
- [ ] Login with incorrect password
- [ ] Refresh token
- [ ] Logout revokes token

```bash
# Run tests
php artisan test tests/Feature/Auth/

# Verify all passing
vendor/bin/phpunit --testdox
```

---

### Week 3: Database & Integration Setup

#### Task 3.1: Add User Scoping to Existing Tables
**Duration**: 2 hours
**Owner**: Database Architect

**Create Migration**: `database/migrations/xxxx_add_user_id_to_tables.php`

```php
public function up(): void
{
    // Add user_id to samples
    Schema::table('samples', function (Blueprint $table) {
        $table->uuid('user_id')->nullable();
        $table->foreign('user_id')
            ->references('id')
            ->on('users')
            ->onDelete('cascade');
        $table->index('user_id');
    });

    // Add user_id to collections
    Schema::table('collections', function (Blueprint $table) {
        $table->uuid('user_id')->nullable();
        $table->foreign('user_id')
            ->references('id')
            ->on('users')
            ->onDelete('cascade');
        $table->index('user_id');
    });

    // Add user_id to processing_jobs
    Schema::table('processing_jobs', function (Blueprint $table) {
        $table->uuid('user_id')->nullable();
        $table->foreign('user_id')
            ->references('id')
            ->on('users')
            ->onDelete('cascade');
        $table->index('user_id');
    });
}

public function down(): void
{
    // Drop foreign keys and columns
}
```

**Execution**:
```bash
php artisan migrate

# Verify
SELECT * FROM samples LIMIT 1;  -- Should have user_id column
```

---

#### Task 3.2: Seed Test Data
**Duration**: 2 hours
**Owner**: QA Architect

**Create Seeders**:
```bash
php artisan make:seeder UserSeeder
php artisan make:seeder SampleSeeder
```

**Seeder Content**:
```php
// UserSeeder
User::create([
    'email' => 'test@example.com',
    'password' => Hash::make('password123'),
    'first_name' => 'Test',
    'last_name' => 'User'
]);

// SampleSeeder
Sample::create([
    'user_id' => User::first()->id,
    'filename' => 'test.wav',
    'file_url' => 's3://...',
    'duration' => 4.5
]);
```

**Run**:
```bash
php artisan db:seed --class=UserSeeder
php artisan db:seed --class=SampleSeeder
```

---

#### Task 3.3: Setup Logging & Error Handling
**Duration**: 2 hours
**Owner**: DevOps Architect

**Files to Update**:
- `config/logging.php` - Structured JSON logging
- `app/Exceptions/Handler.php` - Global error handler

**Configuration**:
```php
// Structured JSON logging
'channels' => [
    'stack' => [
        'driver' => 'stack',
        'channels' => ['single', 'sentry'],
    ],
    'sentry' => [
        'driver' => 'sentry',
    ],
]

// Error handler
public function render($request, Throwable $exception)
{
    if ($request->is('api/*')) {
        return response()->json([
            'error' => $exception->getMessage(),
            'status' => $this->getStatusCode($exception)
        ], $this->getStatusCode($exception));
    }
}
```

---

#### Task 3.4: Integration Test Suite (Phase 1)
**Duration**: 4 hours
**Owner**: QA Architect

**Test Files**:
- `tests/Feature/Auth/FullAuthFlowTest.php`
- `tests/Feature/Api/AuthApiTest.php`

**Test Scenarios**:
- [ ] User registers → receives confirmation email → verifies → logs in
- [ ] User logs in → receives JWT token → can access protected routes
- [ ] Invalid token returns 401
- [ ] Expired token returns 401
- [ ] Token refresh works
- [ ] Logout invalidates token

```bash
php artisan test tests/Feature/Auth/FullAuthFlowTest.php --testdox
```

**Milestone Check**:
```bash
# Run all Phase 1 tests
php artisan test

# Expected: 20+ tests passing, 0 failures
```

---

## Phase 2: API Gateway & FastAPI Integration (Weeks 4-5)

### Week 4: Cloudflare Workers Setup

#### Task 4.1: Create Workers Project
**Duration**: 3 hours
**Owner**: DevOps Architect

**Setup**:
```bash
# 1. Create project
cd ../
npm create cloudflare@latest workers-api
cd workers-api

# 2. Install dependencies
npm install hono

# 3. Create basic structure
mkdir src/{middleware,routes,services}
touch src/index.ts src/middleware/auth.ts src/routes/index.ts
```

**Project Structure**:
```
workers-api/
├── src/
│   ├── index.ts           # Main entry point
│   ├── middleware/
│   │   ├── auth.ts        # JWT validation
│   │   ├── cors.ts        # CORS handling
│   │   └── rateLimit.ts   # Rate limiting
│   ├── routes/
│   │   ├── auth.ts        # Route to Laravel
│   │   ├── api.ts         # Route to FastAPI
│   │   └── index.ts
│   └── services/
│       ├── jwt.ts         # JWT validation logic
│       └── cache.ts       # Redis caching
├── wrangler.toml          # Workers config
├── package.json
└── tsconfig.json
```

---

#### Task 4.2: Implement JWT Validation Middleware
**Duration**: 4 hours
**Owner**: DevOps Architect

**File**: `src/middleware/auth.ts`

```typescript
import { Context, Next } from 'hono'
import { verify } from '@tsndr/cloudflare-worker-jwt'

export async function authMiddleware(c: Context, next: Next) {
  const authHeader = c.req.header('Authorization')

  if (!authHeader) {
    return c.json({ error: 'Missing Authorization header' }, 401)
  }

  const token = authHeader.replace('Bearer ', '')

  try {
    // Get public key from Laravel
    const publicKey = await getPublicKey(c)

    // Verify JWT signature (RS256)
    const isValid = await verify(token, publicKey, { algorithm: 'RS256' })

    if (!isValid) {
      return c.json({ error: 'Invalid token' }, 401)
    }

    // Decode and set user context
    const decoded = decodeToken(token)
    c.set('user', {
      id: decoded.sub,
      email: decoded.email,
      tier: decoded.tier
    })

    await next()
  } catch (error) {
    return c.json({ error: 'Token verification failed' }, 401)
  }
}

async function getPublicKey(c: Context): Promise<string> {
  // Cache public key for 1 hour
  const cached = await c.env.CACHE.get('laravel_public_key')
  if (cached) return cached

  const response = await fetch(`${c.env.LARAVEL_API_URL}/api/auth/public-key`)
  const publicKey = await response.text()

  await c.env.CACHE.put('laravel_public_key', publicKey, {
    expirationTtl: 3600
  })

  return publicKey
}

function decodeToken(token: string) {
  const parts = token.split('.')
  const payload = JSON.parse(atob(parts[1]))
  return payload
}
```

**Deliverables**:
- [ ] Auth middleware implemented
- [ ] JWT validation working
- [ ] User context set on all requests

---

#### Task 4.3: Implement Routing Logic
**Duration**: 3 hours
**Owner**: DevOps Architect

**File**: `src/routes/index.ts`

```typescript
import { Hono } from 'hono'
import { authMiddleware } from '../middleware/auth'

const app = new Hono()

// Public routes (no auth required)
app.post('/api/auth/login', async (c) => {
  // Forward to Laravel
  const response = await fetch(
    `${c.env.LARAVEL_API_URL}/api/auth/login`,
    {
      method: c.req.method,
      headers: c.req.header(),
      body: await c.req.text()
    }
  )
  return new Response(await response.text(), response)
})

app.post('/api/auth/register', async (c) => {
  // Forward to Laravel
  // Similar to above
})

// Protected routes (auth required)
app.use('/api/samples/*', authMiddleware)
app.use('/api/collections/*', authMiddleware)
app.use('/api/billing/*', authMiddleware)

// Route to FastAPI
app.all('/api/samples/*', async (c) => {
  const user = c.get('user')
  const response = await fetch(
    `${c.env.FASTAPI_API_URL}${c.req.path}`,
    {
      method: c.req.method,
      headers: {
        ...Object.fromEntries(c.req.header()),
        'X-User-ID': user.id,
        'X-User-Tier': user.tier
      },
      body: c.req.method !== 'GET' ? await c.req.text() : undefined
    }
  )
  return new Response(await response.text(), response)
})

// Route to Laravel
app.all('/api/billing/*', async (c) => {
  // Similar routing to Laravel
})

export default app
```

**Validation**:
- [ ] Routes defined for all endpoints
- [ ] Auth middleware applied to protected routes
- [ ] Headers forwarded correctly

---

#### Task 4.4: Configure Wrangler & Deploy
**Duration**: 2 hours
**Owner**: DevOps Architect

**File**: `wrangler.toml`

```toml
name = "sp404-api-gateway"
main = "src/index.ts"
compatibility_date = "2024-11-01"

[env.development]
vars = { LARAVEL_API_URL = "http://localhost:8000", FASTAPI_API_URL = "http://localhost:8100" }

[env.production]
vars = { LARAVEL_API_URL = "https://laravel-api.railway.app", FASTAPI_API_URL = "https://fastapi-api.railway.app" }

[[kv_namespaces]]
binding = "CACHE"
id = "cache-namespace-id"
```

**Deploy Commands**:
```bash
# Development (local)
npx wrangler dev

# Production
npx wrangler deploy --env production
```

---

### Week 5: FastAPI User Scoping

#### Task 5.1: Add User Validation Middleware to FastAPI
**Duration**: 3 hours
**Owner**: FastAPI Architect

**File**: `backend/app/api/v1/dependencies.py`

```python
from fastapi import Header, HTTPException
from typing import Optional

async def get_current_user(
    x_user_id: str = Header(None),
    x_user_tier: str = Header('free')
) -> dict:
    """Extract user context from Workers-validated headers"""
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized - no user context"
        )

    return {
        'id': x_user_id,
        'tier': x_user_tier
    }

async def get_user_or_404(
    user: dict = Depends(get_current_user),
    sample_id: str = None
) -> dict:
    """Ensure user owns the resource"""
    # Verify in task 5.2
    return user
```

---

#### Task 5.2: Update All FastAPI Endpoints
**Duration**: 6 hours
**Owner**: FastAPI Architect

**Pattern to Apply**:
```python
# Before (no user scoping)
@router.get("/api/samples")
async def get_samples(db: AsyncSession = Depends(get_db)):
    samples = await db.execute(select(Sample))
    return samples

# After (with user scoping)
@router.get("/api/samples")
async def get_samples(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    samples = await db.execute(
        select(Sample).where(Sample.user_id == user['id'])
    )
    return samples
```

**Endpoints to Update**:
- [ ] GET /api/samples
- [ ] POST /api/samples (upload)
- [ ] GET /api/samples/{id}
- [ ] DELETE /api/samples/{id}
- [ ] GET /api/collections
- [ ] POST /api/collections
- [ ] GET /api/collections/{id}
- [ ] PUT /api/projects/{id} (export)
- [ ] All other endpoints using user data

**Validation Script**:
```bash
# Search for all routes
grep -r "@router" backend/app/api/v1/endpoints/ | grep "def " | wc -l

# All should have user_id filtering
```

---

#### Task 5.3: Create Integration Tests (FastAPI)
**Duration**: 4 hours
**Owner**: QA Architect

**File**: `backend/tests/test_user_isolation.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_can_only_see_own_samples():
    """User A cannot see User B's samples"""

    # Create User A and sample
    user_a_id = "uuid-a"
    sample_a = await create_sample(user_a_id, "sample-a.wav")

    # Create User B and sample
    user_b_id = "uuid-b"
    sample_b = await create_sample(user_b_id, "sample-b.wav")

    # User A requests User B's sample
    response = await client.get(
        f"/api/samples/{sample_b.id}",
        headers={"X-User-ID": user_a_id}
    )

    assert response.status_code == 404  # Not found for User A

@pytest.mark.asyncio
async def test_user_list_only_shows_own_samples():
    """GET /api/samples returns only user's samples"""

    user_a_id = "uuid-a"
    user_b_id = "uuid-b"

    # Create 5 samples for User A
    for i in range(5):
        await create_sample(user_a_id, f"sample-a-{i}.wav")

    # Create 3 samples for User B
    for i in range(3):
        await create_sample(user_b_id, f"sample-b-{i}.wav")

    # User A lists samples
    response = await client.get(
        "/api/samples",
        headers={"X-User-ID": user_a_id}
    )

    assert response.status_code == 200
    assert len(response.json()['samples']) == 5  # Only User A's samples
```

---

#### Task 5.4: Update Existing Tests
**Duration**: 3 hours
**Owner**: QA Architect

**Changes**:
- Add X-User-ID headers to all test requests
- Create test fixtures for users
- Update assertions to expect filtered results
- Verify database isolation

```bash
# Run all tests
python -m pytest backend/tests/test_user_isolation.py -v

# Expected: 20+ tests passing
```

---

## Phase 3: Billing & Subscriptions (Weeks 6-8)

### Week 6: Stripe Integration

#### Task 6.1: Setup Laravel Cashier
**Duration**: 2 hours
**Owner**: Laravel Architect

**Installation**:
```bash
cd laravel-sp404

# Install Cashier
composer require laravel/cashier-stripe

# Publish assets
php artisan vendor:publish --tag="cashier-migrations"
php artisan vendor:publish --tag="cashier-config"

# Run migrations
php artisan migrate

# Update .env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...
```

**Model Setup**:
```php
// app/Models/User.php
use Laravel\Cashier\Billable;

class User extends Model {
    use Billable;
}
```

---

#### Task 6.2: Create Billing Endpoints
**Duration**: 4 hours
**Owner**: Laravel Architect

**File**: `app/Http/Controllers/Api/BillingController.php`

**Endpoints to Implement**:
1. `GET /api/billing/plans` - List subscription plans
2. `POST /api/billing/subscribe` - Create subscription
3. `GET /api/billing/subscription` - Get current subscription
4. `PUT /api/billing/subscription` - Update subscription (upgrade/downgrade)
5. `DELETE /api/billing/subscription` - Cancel subscription
6. `GET /api/billing/invoices` - List invoices

**Subscription Plans** (hardcoded or Stripe dashboard):
```php
const PLANS = [
    'free' => [
        'name' => 'Free',
        'price' => 0,
        'features' => ['storage_gb' => 0.1, 'analyses_per_month' => 10]
    ],
    'pro' => [
        'stripe_price_id' => 'price_1234567890',
        'name' => 'Pro',
        'price' => 2900, // in cents
        'features' => ['storage_gb' => 5, 'analyses_per_month' => 500]
    ],
    'enterprise' => [
        'stripe_price_id' => 'price_0987654321',
        'name' => 'Enterprise',
        'price' => 9900,
        'features' => ['storage_gb' => null, 'analyses_per_month' => null]
    ]
];
```

**Validation**:
```bash
curl -X GET http://localhost:8000/api/billing/plans
# Should return list of plans with pricing
```

---

#### Task 6.3: Setup Webhook Handlers
**Duration**: 3 hours
**Owner**: Laravel Architect

**File**: `app/Http/Controllers/WebhookController.php`

**Webhook Events to Handle**:
- `charge.succeeded` - Payment successful
- `charge.failed` - Payment failed
- `customer.subscription.created` - New subscription
- `customer.subscription.updated` - Subscription changed
- `customer.subscription.deleted` - Subscription cancelled

**Implementation**:
```php
public function handleStripeWebhook(Request $request)
{
    $payload = json_decode($request->getContent(), true);
    $event = $payload['type'];

    switch ($event) {
        case 'charge.succeeded':
            $this->handlePaymentSuccess($payload['data']);
            break;
        case 'customer.subscription.created':
            $this->handleSubscriptionCreated($payload['data']);
            break;
        // ... other events
    }

    return response('success');
}

private function handlePaymentSuccess(array $data)
{
    $charge = $data['object'];
    $customer = Customer::where('stripe_id', $charge['customer'])->first();

    // Update subscription status
    $customer->subscription->update(['status' => 'active']);

    // Log transaction
    // Send confirmation email
}
```

**Route**:
```php
// routes/api.php
Route::post('/webhooks/stripe', [WebhookController::class, 'handleStripeWebhook']);
```

**Testing**:
```bash
# Use Stripe CLI to forward webhooks
stripe listen --forward-to localhost:8000/api/webhooks/stripe

# Trigger test events
stripe trigger charge.succeeded
```

---

#### Task 6.4: Create Quota Enforcement Service
**Duration**: 3 hours
**Owner**: Laravel Architect

**File**: `app/Services/QuotaService.php`

```php
namespace App\Services;

class QuotaService
{
    public static function getUserQuota(User $user): array
    {
        $tier = $user->subscription?->tier ?? 'free';
        $quotas = [
            'free' => ['storage_mb' => 100, 'analyses_per_month' => 10],
            'pro' => ['storage_mb' => 5120, 'analyses_per_month' => 500],
            'enterprise' => ['storage_mb' => PHP_INT_MAX, 'analyses_per_month' => PHP_INT_MAX]
        ];

        return $quotas[$tier] ?? $quotas['free'];
    }

    public static function getUsage(User $user): array
    {
        return [
            'storage_mb' => $user->samples()->sum('file_size_mb'),
            'analyses_used' => $user->analyses()->thisMonth()->count()
        ];
    }

    public static function canUpload(User $user, int $fileSizeMb): bool
    {
        $quota = self::getUserQuota($user);
        $usage = self::getUsage($user);

        return ($usage['storage_mb'] + $fileSizeMb) <= $quota['storage_mb'];
    }

    public static function canAnalyze(User $user): bool
    {
        $quota = self::getUserQuota($user);
        $usage = self::getUsage($user);

        return $usage['analyses_used'] < $quota['analyses_per_month'];
    }
}
```

**Usage in FastAPI**:
```python
# Call from Laravel before queuing analysis
result = await http_client.get(
    f"{LARAVEL_API_URL}/api/quotas/can-analyze",
    headers={"X-User-ID": user_id}
)

if not result['can_analyze']:
    raise HTTPException(status_code=429, detail="Quota exceeded")
```

---

### Week 7: Invoice & Billing Dashboard

#### Task 7.1: Create Invoice Generation
**Duration**: 2 hours
**Owner**: Laravel Architect

**Implementation**:
```php
// Automatically generated by Cashier after payment
// Customize templates in resources/views/vendor/cashier/

public function downloadInvoice(Invoice $invoice)
{
    return $invoice->download();
}

// In routes/api.php
Route::get('/api/billing/invoices/{invoice}', [BillingController::class, 'downloadInvoice']);
```

---

#### Task 7.2: Create Billing Dashboard UI
**Duration**: 4 hours
**Owner**: React Architect

**Components**:
- `BillingDashboard.tsx` - Main billing view
- `SubscriptionCard.tsx` - Current subscription display
- `PlanSelector.tsx` - Plan selection and upgrade
- `InvoiceList.tsx` - Historical invoices
- `UsageMetrics.tsx` - Storage and quota display

**Sample Component**:
```tsx
export function SubscriptionCard({ subscription }: Props) {
  return (
    <Card>
      <CardHeader>
        <h2>Current Plan</h2>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-2xl font-bold">{subscription.tier}</p>
          <p className="text-gray-600">${subscription.price}/month</p>
          <p>Next billing: {format(new Date(subscription.current_period_end), 'PPP')}</p>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleUpgrade}>Upgrade Plan</Button>
      </CardFooter>
    </Card>
  )
}
```

**API Integration**:
```tsx
// hooks/useBilling.ts
export function useSubscription() {
  return useQuery({
    queryKey: ['subscription'],
    queryFn: () => apiClient.get('/api/billing/subscription')
  })
}

export function useUpgradeSubscription() {
  return useMutation({
    mutationFn: (planId: string) =>
      apiClient.post('/api/billing/subscribe', { plan_id: planId })
  })
}
```

---

#### Task 7.3: Integration Tests (Billing)
**Duration**: 3 hours
**Owner**: QA Architect

**Test Scenarios**:
- [ ] Free user cannot exceed quota
- [ ] Pro user has larger quota
- [ ] Quota resets monthly
- [ ] Upgrade tier increases quota immediately
- [ ] Downgrade tier takes effect at period end
- [ ] Failed payment retries
- [ ] Invoice generated on successful payment
- [ ] User can download invoice

```bash
php artisan test tests/Feature/Billing/

# Expected: 15+ tests passing
```

---

### Week 8: Advanced Billing Features

#### Task 8.1: Payment Failure Handling
**Duration**: 2 hours
**Owner**: Laravel Architect

**Retry Logic**:
```php
// Handle invoice.payment_failed webhook
private function handlePaymentFailed(array $data)
{
    $invoice = $data['object'];
    $customer = Customer::where('stripe_id', $invoice['customer'])->first();

    // Attempt to collect after 3 days (Stripe handles automatic retries)
    // Send email notification
    Mail::send(new PaymentFailedNotification($customer));

    // After 3 failed attempts, mark as past due
    if ($invoice['attempt_count'] >= 3) {
        $customer->subscription->update(['status' => 'past_due']);
        // Restrict features or downgrade user
    }
}
```

---

#### Task 8.2: Trial Period & Proration
**Duration**: 2 hours
**Owner**: Laravel Architect

**Implementation**:
```php
// Create trial subscription
$user->newSubscription('default', 'price_pro')
    ->trialDays(14)
    ->create($stripeToken);

// Proration on upgrade
$user->subscription('default')
    ->swapAndInvoice('price_enterprise');

// Downgrade at period end (no proration)
$user->subscription('default')
    ->swap('price_free')
    ->noProrate();
```

---

## Phase 4: Production Ready (Weeks 9-12)

### Week 9: Docker & Deployment

#### Task 9.1: Create Docker Compose Setup
**Duration**: 3 hours
**Owner**: DevOps Architect

**File**: `docker-compose.yml` (at project root)

```yaml
version: '3.8'

services:
  postgresql:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sp404_samples
      POSTGRES_USER: sp404_user
      POSTGRES_PASSWORD: changeme123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  laravel:
    build:
      context: ./laravel-sp404
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgresql
      - DB_DATABASE=sp404_samples
      - DB_USERNAME=sp404_user
      - REDIS_HOST=redis
    depends_on:
      - postgresql
      - redis
    volumes:
      - ./laravel-sp404:/var/www/html

  fastapi:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8100:8100"
    environment:
      - DATABASE_URL=postgresql+asyncpg://sp404_user:changeme123@postgresql:5432/sp404_samples
    depends_on:
      - postgresql
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

**Dockerfile for Laravel**:
```dockerfile
FROM php:8.2-fpm

RUN apt-get update && apt-get install -y \
    postgresql-client \
    composer

WORKDIR /var/www/html

COPY . .

RUN composer install
RUN php artisan migrate
RUN php artisan cache:clear

CMD ["php", "-S", "0.0.0.0:8000", "public/index.php"]
```

**Start Services**:
```bash
docker-compose up --build
```

---

#### Task 9.2: Deploy to Railway (Laravel)
**Duration**: 2 hours
**Owner**: DevOps Architect

**Setup**:
```bash
cd laravel-sp404

# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variables
railway vars set DB_HOST=$RAILWAY_POSTGRES_HOST
railway vars set DB_DATABASE=$RAILWAY_POSTGRES_DB
railway vars set STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
```

**Verification**:
```bash
# Check deployment
railway status

# View logs
railway logs

# Test endpoint
curl https://laravel-api.railway.app/api/health
```

---

#### Task 9.3: Deploy Cloudflare Workers
**Duration**: 1 hour
**Owner**: DevOps Architect

**Deploy**:
```bash
cd workers-api

# Set secrets
npx wrangler secret put LARAVEL_API_URL
# https://laravel-api.railway.app

npx wrangler secret put FASTAPI_API_URL
# https://fastapi-api.railway.app

# Deploy
npx wrangler deploy

# Verify
curl https://sp404-api.workers.dev/api/health
```

---

### Week 10: Monitoring & Observability

#### Task 10.1: Setup Sentry for Error Tracking
**Duration**: 2 hours
**Owner**: DevOps Architect

**Laravel**:
```bash
composer require sentry/sentry-laravel

# Publish config
php artisan sentry:publish --dsn=YOUR_SENTRY_DSN

# Update .env
SENTRY_DSN=https://...@sentry.io/...
```

**FastAPI**:
```bash
pip install sentry-sdk

# In main.py
import sentry_sdk
sentry_sdk.init("https://...@sentry.io/...")
```

**Workers**:
```typescript
// Report errors to Sentry
async function reportError(error: Error) {
  await fetch('https://...@sentry.io/..., {
    method: 'POST',
    body: JSON.stringify({
      message: error.message,
      timestamp: new Date().toISOString()
    })
  })
}
```

---

#### Task 10.2: Setup Health Checks & Monitoring
**Duration**: 2 hours
**Owner**: DevOps Architect

**Health Check Endpoints**:

Laravel:
```php
// routes/api.php
Route::get('/api/health', function () {
    return response()->json([
        'status' => 'healthy',
        'service' => 'laravel-auth',
        'database' => DB::connection()->getPdo() ? 'ok' : 'error',
        'timestamp' => now()->toIso8601String()
    ]);
});
```

FastAPI:
```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-audio",
        "timestamp": datetime.utcnow().isoformat()
    }
```

Workers:
```typescript
app.get('/api/health', (c) => {
  return c.json({
    status: 'healthy',
    service: 'workers-gateway',
    timestamp: new Date().toISOString()
  })
})
```

**Monitoring Setup** (Better Uptime):
```bash
# Monitor each endpoint every 5 minutes
- https://sp404-api.workers.dev/api/health
- https://laravel-api.railway.app/api/health
- https://fastapi-api.railway.app/api/health

# Alert if any down
- Email notification
- Slack notification
- PagerDuty integration
```

---

#### Task 10.3: Performance Monitoring
**Duration**: 2 hours
**Owner**: DevOps Architect

**New Relic / Datadog Setup**:
```php
// Laravel
composer require newrelic/newrelic-php-agent

// FastAPI
pip install datadog
```

**Key Metrics to Track**:
- API response time (p50, p95, p99)
- Database query time
- Error rate
- JWT validation time
- Stripe API latency

---

### Week 11: Load Testing & Optimization

#### Task 11.1: Load Testing
**Duration**: 3 hours
**Owner**: QA Architect

**Tool**: Apache JMeter or k6

```bash
# k6 load test
npm install -g k6

# Create test script (load-test.js)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '5m', target: 100 },  // Ramp to 100 users
    { duration: '5m', target: 500 },  // Ramp to 500 users
    { duration: '5m', target: 1000 }, // Ramp to 1000 users
    { duration: '5m', target: 0 },    // Ramp down
  ],
};

export default function() {
  let res = http.get('https://sp404-api.workers.dev/api/samples', {
    headers: {
      'Authorization': 'Bearer ' + __ENV.JWT_TOKEN
    }
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });

  sleep(1);
}

# Run test
k6 run load-test.js
```

**Success Criteria**:
- [ ] API handles 1000 concurrent users
- [ ] p95 response time < 200ms
- [ ] No errors under load
- [ ] Database connections stable

---

#### Task 11.2: Performance Optimization
**Duration**: 2 hours
**Owner**: FastAPI Architect

**Optimizations**:
1. Database query optimization
   - Add indexes on frequently queried columns
   - Use `select()` to avoid N+1 queries

2. Caching
   - Cache public key (1 hour)
   - Cache user quotas (5 minutes)
   - Cache subscription data

3. Connection pooling
   - Configure SQLAlchemy pool_size
   - Configure Redis connection pool

```python
# Caching example
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1000)
def get_user_quota(user_id: str):
    # This gets called once per user_id per request window
    return db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
```

---

### Week 12: Final Testing & Go-Live

#### Task 12.1: End-to-End Testing
**Duration**: 3 hours
**Owner**: QA Architect

**Scenarios to Test**:
- [ ] New user registration → verify email → login → upload sample
- [ ] Free user hits quota → cannot upload → upgrade → can upload
- [ ] Pro user subscription workflow
- [ ] Payment failure handling
- [ ] Token refresh on expiration
- [ ] Concurrent uploads from multiple users
- [ ] All CRUD operations on samples, collections
- [ ] Download and share functionality

**Test Framework**: Playwright or Cypress

```typescript
// e2e test
test('user registration and first upload', async ({ page }) => {
  // 1. Register
  await page.goto('https://sp404.app')
  await page.click('text=Sign Up')
  // ... fill form
  // ... verify email

  // 2. Login
  await page.fill('input[name=email]', 'test@example.com')
  await page.fill('input[name=password]', 'password123')
  await page.click('button:has-text("Login")')

  // 3. Upload
  await page.click('text=Upload Sample')
  await page.upload('input[name=audio]', 'sample.wav')
  await page.click('button:has-text("Upload")')

  // 4. Verify
  await expect(page).toContainText('sample.wav')
})
```

---

#### Task 12.2: Documentation & Runbooks
**Duration**: 2 hours
**Owner**: DevOps Architect

**Create**:
- [ ] `docs/DEPLOYMENT.md` - How to deploy
- [ ] `docs/TROUBLESHOOTING.md` - Common issues
- [ ] `docs/RUNBOOKS.md` - Operational procedures
  - How to restart services
  - How to handle database issues
  - How to investigate errors
  - How to manage quotas
  - How to handle Stripe issues

---

#### Task 12.3: Go-Live Checklist
**Duration**: 1 hour
**Owner**: All

**Final Checklist**:
- [ ] All tests passing (backend + frontend)
- [ ] Staging deployment successful
- [ ] Stripe webhook configured and tested
- [ ] Email delivery working (verification, invoices, alerts)
- [ ] Error tracking (Sentry) configured
- [ ] Monitoring and alerts active
- [ ] Database backed up
- [ ] Runbooks documented
- [ ] Team trained
- [ ] Marketing ready
- [ ] Support ready
- [ ] Metrics dashboards created

**Go-Live Steps**:
```bash
# 1. Final database backup
pg_dump sp404_samples > backup-$(date +%Y%m%d-%H%M%S).sql

# 2. Deploy to production
railway deploy --production
npx wrangler deploy --env production

# 3. Verify all services
curl https://sp404.app/api/health
curl https://api.sp404.app/api/health

# 4. Monitor for issues
tail -f /var/log/laravel.log
tail -f /var/log/fastapi.log

# 5. Monitor Sentry dashboard for errors
```

---

## Migration Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Database migration data loss | Low | High | Test migration with backup, validate data |
| Token validation failures | Medium | Medium | Comprehensive testing, fallback auth |
| Payment integration issues | Low | High | Stripe sandbox testing, manual fallback |
| Performance degradation | Medium | Medium | Load testing, query optimization |
| Existing data orphaned | Low | High | Add default user for legacy data |

---

## Success Metrics

### Phase 1 Success
- [ ] 20+ backend tests passing
- [ ] User registration and login working
- [ ] JWT tokens valid and refreshable
- [ ] Email verification working

### Phase 2 Success
- [ ] Cloudflare Workers routing all requests
- [ ] FastAPI endpoints returning user-scoped data
- [ ] 50+ integration tests passing
- [ ] Multi-user data isolation verified

### Phase 3 Success
- [ ] Stripe subscriptions working
- [ ] Quotas enforced correctly
- [ ] Invoices generated
- [ ] Webhook handlers working

### Phase 4 Success
- [ ] All services deployed to production
- [ ] 99.9% uptime
- [ ] < 200ms response time (p95)
- [ ] Zero data loss during migration
- [ ] First paying user onboarded

---

## Post-Launch Roadmap

**Month 2**:
- [ ] Team/organization support
- [ ] Advanced analytics dashboard
- [ ] Sample sharing between users
- [ ] Bulk operations

**Month 3+**:
- [ ] MIDI controller integration
- [ ] Advanced search (full-text)
- [ ] Machine learning recommendations
- [ ] Mobile app

---

*This migration plan is comprehensive and production-ready. Adjust timelines based on team size and experience.*

