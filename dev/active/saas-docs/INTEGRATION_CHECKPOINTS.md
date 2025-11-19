# Integration Checkpoints: Week 1 Coordination

**Purpose:** Synchronize Track A (UI/UX) and Track B (Infrastructure) work
**Timeline:** 3 checkpoints across the week (Wed, Thu, Fri)
**Success:** Both tracks merge successfully Friday 5 PM

---

## Checkpoint 1: API Connectivity (Wednesday 12:00 PM)

**Time Budget:** 15 minutes
**Goal:** Confirm backend services can communicate
**Responsible:** Track B Lead (infrastructure ready)

### Setup Phase

```bash
# Track B: Verify all services running
docker-compose ps

# Expected output:
# NAME              STATUS              PORTS
# sp404_postgres    Up 10 seconds       0.0.0.0:5432->5432/tcp
# sp404_redis       Up 10 seconds       0.0.0.0:6379->6379/tcp
```

### Health Check Procedures

**Test 1: FastAPI Health**
```bash
# From your local machine
curl http://YOUR_VPS_IP:8100/health

# Expected response:
# {
#   "status": "ok",
#   "database": "connected",
#   "redis": "connected"
# }
```

**Test 2: PostgreSQL Connectivity**
```bash
# From VPS
docker-compose exec postgres psql -U sp404_user -d sp404_samples -c "SELECT COUNT(*) FROM samples;"

# Expected: 2328
```

**Test 3: Redis Connectivity**
```bash
# From VPS
docker-compose exec redis redis-cli ping

# Expected: PONG
```

### CORS Configuration

If Track A is running locally, test CORS:

```bash
# From Track A dev server
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     http://YOUR_VPS_IP:8100/health

# Expected: Access-Control-Allow-Origin header present
```

### Checkpoint 1 Success Criteria

- ✅ All Docker containers running
- ✅ FastAPI responds to health checks
- ✅ Database queries return correct sample count
- ✅ Redis accepts connections
- ✅ CORS headers present (if testing from localhost)

### Action if Failed

| Issue | Solution |
|-------|----------|
| Services not running | Run `docker-compose up -d` |
| Health check fails | Check `docker-compose logs` for errors |
| CORS error | Add origin to FastAPI CORS config |
| Database empty | Re-run restore: `docker-compose exec -T postgres pg_restore...` |

---

## Checkpoint 2: Component Integration (Thursday 3:00 PM)

**Time Budget:** 30 minutes
**Goal:** React components receive data from backend
**Responsible:** Track A Lead (with Track B support)

### API Endpoints Required

Track B must provide these endpoints by Thursday 3 PM:

```typescript
// GET /health
{
  "status": "ok",
  "database": "connected"
}

// GET /api/v1/samples
{
  "data": [
    {
      "id": 1,
      "name": "Sample 1",
      "duration": 3.5,
      "bpm": 120,
      "created_at": "2025-11-18T00:00:00Z"
    }
  ],
  "total": 2328
}

// GET /api/v1/samples/{id}
{
  "id": 1,
  "name": "Sample 1",
  "duration": 3.5,
  "bpm": 120,
  "key": "C",
  "genre": "Hip-Hop",
  "created_at": "2025-11-18T00:00:00Z"
}

// GET /api/v1/preferences
{
  "user_id": "default",
  "model": "qwen/qwen3-7b-it",
  "auto_analyze": true
}
```

### API Client Implementation

Track A creates API client:

```typescript
// saas-frontend/src/api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8100';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.message);
    throw error;
  }
);

export async function getSamples() {
  return apiClient.get('/api/v1/samples');
}

export async function getSample(id: number) {
  return apiClient.get(`/api/v1/samples/${id}`);
}
```

### Component Integration Test

Track A runs data loading test:

```typescript
// saas-frontend/src/components/SampleList.tsx
import { useQuery } from '@tanstack/react-query';
import { getSamples } from '../api/client';

export function SampleList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['samples'],
    queryFn: getSamples,
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <Box>
      {data.data.map((sample) => (
        <SampleCard key={sample.id} sample={sample} />
      ))}
    </Box>
  );
}
```

### Integration Test Procedure

```bash
# 1. Track B: Confirm services running
docker-compose ps

# 2. Track A: Start React dev server
npm run dev
# Should be running on http://localhost:3000

# 3. Track A: Open browser and check console
# Should see: Fetching samples from http://YOUR_VPS_IP:8100/api/v1/samples

# 4. Track A: Verify data displays
# Should see: List of samples from database (2,328 total)

# 5. Track A: Check network tab
# Should see: 200 responses, proper CORS headers
```

### Checkpoint 2 Success Criteria

- ✅ React dev server running
- ✅ API client successfully configured
- ✅ Sample list displays data from backend
- ✅ No CORS errors in console
- ✅ Network requests show 200 status
- ✅ Data matches database (2,328 samples)

### Action if Failed

| Issue | Solution |
|-------|----------|
| CORS error | Add React origin to FastAPI CORS config |
| API 404 | Verify endpoint paths match exactly |
| Empty data | Check database restore completed |
| Network timeout | Check VPS firewall allows port 8100 |
| Type errors | Update API response types in TypeScript |

---

## Checkpoint 3: Full Deployment (Friday 3:00 PM)

**Time Budget:** 60 minutes
**Goal:** Complete E2E test from browser to database
**Responsible:** Both tracks (coordinated)

### Pre-Deployment Checklist

**Track B:**
- ✅ Nginx reverse proxy running
- ✅ HTTPS certificate installed
- ✅ Rate limiting active
- ✅ Health checks passing
- ✅ Docker containers healthy
- ✅ Database restored and verified
- ✅ Redis persistence enabled
- ✅ Backups scheduled

**Track A:**
- ✅ React build optimized
- ✅ API client updated for production URLs
- ✅ Environment variables configured
- ✅ E2E tests passing
- ✅ Dark theme verified
- ✅ Responsive design validated
- ✅ No console errors

### Deployment Steps

**1. Track A: Build React (10 min)**
```bash
npm run build
# Expected output: build/ directory created

# Verify build
ls -lh build/
# Should be < 500KB for optimized build
```

**2. Track B: Prepare deployment (10 min)**
```bash
# Copy React build to VPS
scp -r build/* deploy@YOUR_VPS_IP:~/sp404-saas/public/

# Verify file transfer
ssh deploy@YOUR_VPS_IP "ls -la ~/sp404-saas/public/ | head -10"
```

**3. Track A: Update API URLs (5 min)**
```typescript
// Update for production
const API_BASE_URL = 'https://api.yourdomain.com';
```

**4. Track B: Start application containers (10 min)**
```bash
# Pull latest code
cd ~/sp404-saas
git pull origin main

# Start all services
docker-compose up -d

# Verify health
docker-compose ps
curl https://api.yourdomain.com/health
```

**5. Both: Run E2E Tests (15 min)**
```bash
# Track A: Run Playwright tests against production
npx playwright test --config=playwright.config.prod.ts

# Expected: All tests pass
```

**6. Both: Smoke Test (10 min)**
```bash
# From any browser
open https://api.yourdomain.com

# Manually test:
# 1. Page loads
# 2. Samples list displays
# 3. Click sample → details modal
# 4. Dark theme applies
# 5. Responsive on mobile
```

### E2E Test Scenarios

```typescript
// tests/e2e.spec.ts
test.describe('Production Deployment', () => {
  test('should load homepage', async ({ page }) => {
    await page.goto('https://api.yourdomain.com');
    await expect(page).toHaveTitle(/SP-404/);
  });

  test('should fetch samples', async ({ page }) => {
    await page.goto('https://api.yourdomain.com');
    const samples = page.locator('[data-testid="sample-list"]');
    await expect(samples).toBeVisible();
  });

  test('should show sample details', async ({ page }) => {
    await page.goto('https://api.yourdomain.com');
    const firstSample = page.locator('[data-testid="sample-card"]').first();
    await firstSample.click();

    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();
  });

  test('should apply dark theme', async ({ page }) => {
    await page.goto('https://api.yourdomain.com');
    const background = await page.locator('body').evaluate(
      (el) => getComputedStyle(el).backgroundColor
    );
    // Should be dark color, not white
    expect(background).not.toContain('255, 255');
  });
});
```

### Checkpoint 3 Success Criteria

- ✅ React build successful and optimized
- ✅ React deployed to VPS
- ✅ HTTPS working (no mixed content warnings)
- ✅ All Docker containers running
- ✅ Health checks passing
- ✅ E2E tests passing
- ✅ Smoke tests successful
- ✅ Performance acceptable (<3s load time)
- ✅ No console errors or warnings
- ✅ Dark theme displays correctly
- ✅ Responsive on mobile/tablet/desktop

### Rollback Procedure (if deployment fails)

```bash
# Track B: Rollback to previous state
docker-compose down

# Restore from backup
docker cp ~/sp404-saas/backups/sp404_backup_YYYYMMDD.sql.gz - | \
  docker run -i --rm -v sp404_postgres:/var/lib/postgresql/data \
  postgres:16-alpine pg_restore --no-owner --no-acl -U sp404_user -d sp404_samples

# Restart services
docker-compose up -d

# Verify
docker-compose ps
curl https://api.yourdomain.com/health
```

---

## Week 1 Integration Summary

### By Wednesday
- ✅ Infrastructure team confirms backend healthy
- ✅ UI team begins testing API connectivity

### By Thursday
- ✅ React components receive live data
- ✅ Both teams complete their Week 1 tasks
- ✅ Integration testing begins

### By Friday 5 PM
- ✅ React deployed to production VPS
- ✅ Full E2E test suite passes
- ✅ System live and functional
- ✅ Ready for Week 2 development

---

## Week 2 Preview

### Track A Tasks
- Form components for sample upload
- Authentication UI components
- Billing/subscription pages
- Integration with Auth API

### Track B Tasks
- Laravel Auth endpoints
- Stripe integration
- API quota enforcement
- WebSocket support for real-time updates

### Integration
- Full user authentication flow
- API key management
- Subscription status checking

---

## Communication Protocol

### Daily Standup (10:00 AM)
```
What I completed:
What I'm working on:
Blockers:
```

### Escalation Procedure
1. **Minor issue:** Post in #sp404-saas Slack (resolve within 1 hour)
2. **Blocking issue:** @ mention team lead (resolve within 2 hours)
3. **Critical issue:** Call/meet immediately (paging available 24/7)

### Issue Template

```markdown
## [Component] Issue Title

**Impact:** High/Medium/Low
**Blocking:** Yes/No (does this stop other work?)

### Description
[What's the problem?]

### Steps to Reproduce
1.
2.
3.

### Expected vs Actual
Expected: [what should happen]
Actual: [what's happening]

### Attempted Solutions
- [What have you tried?]
- [Did it work?]

### Request
[What help do you need?]
```

---

## Success Metrics

### Infrastructure (Track B)
- Uptime: >99% during Week 1
- Response time: <200ms p95
- Memory: <80% utilization
- Disk: >20% free space

### Frontend (Track A)
- Load time: <3s
- Lighthouse score: >80
- TypeScript errors: 0
- Test coverage: >80%

### Integration
- E2E tests: 100% passing
- API errors: <1%
- CORS issues: 0
- Deployment success: First attempt

---

## Resources

- Deployment runbooks: `/dev/active/saas-docs/`
- API documentation: Track B provides
- Test data: 2,328 sample records in database
- Monitoring dashboard: (Week 2 setup)
