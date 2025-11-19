# Integration Checkpoints: Track A ↔ Track B

**Purpose**: Ensure Track A (UI/UX) and Track B (Infrastructure) work together seamlessly
**Schedule**: 3 checkpoints during Week 1
**Risk**: Low (independent tracks, well-defined APIs)

---

## OVERVIEW

While Track A and Track B are independent during Week 1, they must integrate at specific checkpoints to ensure compatibility. This document defines:

1. **What** needs to integrate
2. **When** integration happens
3. **How** to test integration
4. **Who** is responsible

---

## INTEGRATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│ Track A: UI/UX Development (Local)                          │
│                                                              │
│  React App (localhost:5173)                                 │
│  ├── Material-UI Components                                 │
│  ├── SP-404 Cyan Theme                                      │
│  ├── AppShell Layout                                        │
│  └── Playwright E2E Tests                                   │
│                                                              │
│  API Client (Axios)                                         │
│  └── Connects to → Track B Staging API                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
                     HTTPS (443)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Track B: Infrastructure (VPS: sp404.yourdomain.com)         │
│                                                              │
│  Nginx Reverse Proxy                                        │
│  ├── SSL Termination (Let's Encrypt)                        │
│  ├── Rate Limiting                                          │
│  └── Security Headers                                       │
│                                                              │
│  FastAPI Backend (localhost:8100)                           │
│  ├── REST API Endpoints                                     │
│  ├── WebSocket Endpoints                                    │
│  └── JSON Responses                                         │
│                                                              │
│  PostgreSQL 16 (Docker)                                     │
│  └── 2,328+ Samples                                         │
│                                                              │
│  Redis 7 (Docker)                                           │
│  └── Caching & Sessions                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## CHECKPOINT 1: WEDNESDAY NOON (Day 3, 50% Complete)

**Goal**: Verify Track A can connect to Track B staging API

### Track A Deliverables (Required)
- ✅ Material-UI v7 installed and configured
- ✅ MUI theme with SP-404 cyan colors
- ✅ API client configured with staging URL
- ✅ At least 1 page component ready to test

### Track B Deliverables (Required)
- ✅ VPS accessible via HTTPS (SSL working)
- ✅ PostgreSQL container running with sample data
- ✅ Nginx reverse proxy configured
- ✅ CORS enabled for Track A local dev (http://localhost:5173)

### Integration Test: API Connectivity

**Performed By**: Track A Developer
**Location**: Local development machine
**Duration**: 15 minutes

#### Step 1: Configure API Client for Staging

**Track A: Update API client** (`react-app/src/api/client.ts`):
```typescript
import axios from 'axios';

// Switch to staging API for integration test
const API_BASE_URL = process.env.VITE_API_URL || 'https://sp404.yourdomain.com/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Track A: Create .env.staging**:
```bash
# react-app/.env.staging
VITE_API_URL=https://sp404.yourdomain.com/api/v1
```

#### Step 2: Test API Endpoints

**Track A: Run test script**:
```bash
# From react-app directory
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app

# Install curl or use Node.js fetch
node << 'EOF'
const fetch = require('node-fetch');

const API_URL = 'https://sp404.yourdomain.com/api/v1';

async function testAPI() {
  try {
    // Test 1: Health check
    console.log('Testing /health endpoint...');
    const healthRes = await fetch(`${API_URL}/../health`);
    console.log('Health:', healthRes.ok ? '✅ PASS' : '❌ FAIL', healthRes.status);

    // Test 2: Get samples
    console.log('\nTesting /samples endpoint...');
    const samplesRes = await fetch(`${API_URL}/public/samples?limit=5`);
    const samples = await samplesRes.json();
    console.log('Samples:', samplesRes.ok ? '✅ PASS' : '❌ FAIL', samples.length, 'samples');

    // Test 3: CORS headers
    console.log('\nTesting CORS headers...');
    const corsRes = await fetch(`${API_URL}/public/samples`, {
      headers: { 'Origin': 'http://localhost:5173' }
    });
    const corsHeader = corsRes.headers.get('access-control-allow-origin');
    console.log('CORS:', corsHeader ? '✅ PASS' : '❌ FAIL', corsHeader);

  } catch (error) {
    console.error('❌ API Test Failed:', error.message);
  }
}

testAPI();
EOF
```

**Expected Output**:
```
Testing /health endpoint...
Health: ✅ PASS 200

Testing /samples endpoint...
Samples: ✅ PASS 5 samples

Testing CORS headers...
CORS: ✅ PASS http://localhost:5173
```

#### Step 3: Test in React App

**Track A: Start dev server with staging API**:
```bash
# Load staging environment
export $(cat .env.staging | xargs)

# Start dev server
npm run dev

# Visit http://localhost:5173
# Navigate to /samples page
# Verify samples load from staging API
```

### Success Criteria
- ✅ Health endpoint returns 200 OK
- ✅ Samples endpoint returns JSON with 5+ samples
- ✅ CORS headers include `http://localhost:5173`
- ✅ React app loads samples from staging API
- ✅ No console errors related to CORS or API

### Troubleshooting

**Issue: CORS Blocked**
```
Access to fetch at 'https://sp404.yourdomain.com/api/v1/public/samples'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution (Track B)**:
```bash
# SSH to VPS
ssh deploy@$VPS_IP

# Check backend CORS configuration
# Ensure backend/app/core/config.py has:
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://sp404.yourdomain.com"
]

# Restart backend (when deployed in Week 2)
# For now, ensure Nginx allows CORS
```

**Issue: SSL Certificate Error**
```
unable to verify the first certificate
```

**Solution (Track B)**:
```bash
# Verify SSL certificate is valid
curl -I https://sp404.yourdomain.com
# Should not show SSL errors

# Check certificate chain
echo | openssl s_client -connect sp404.yourdomain.com:443 -showcerts

# If invalid, re-run Certbot
sudo certbot --nginx -d sp404.yourdomain.com
```

**Issue: 502 Bad Gateway**
```
nginx/1.18.0 (Ubuntu)
502 Bad Gateway
```

**Solution (Track B)**:
```bash
# Backend not deployed yet (expected in Week 1)
# For testing, deploy a minimal FastAPI container
# See "Emergency Backend Deployment" below
```

### Emergency Backend Deployment (If Needed)

**Track B: Quick FastAPI Deploy** (only if needed for testing):
```bash
# SSH to VPS
ssh deploy@$VPS_IP
cd /opt/sp404

# Clone backend code
git clone https://github.com/your-repo/sp404mk2-sample-agent.git temp-backend
cd temp-backend/backend

# Create Dockerfile (if not exists)
cat > Dockerfile << 'EOF'
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
EOF

# Build and run
docker build -t sp404-backend .
docker run -d \
  --name sp404-backend-temp \
  --network sp404-network \
  -p 127.0.0.1:8100:8100 \
  -e DATABASE_URL="postgresql+asyncpg://sp404_user:PASSWORD@postgres:5432/sp404_samples" \
  -e REDIS_URL="redis://redis:6379/0" \
  sp404-backend

# Test backend
curl http://localhost:8100/health
# Should return: {"status": "healthy"}

# Test through Nginx
curl https://sp404.yourdomain.com/health
# Should return: {"status": "healthy"}
```

---

## CHECKPOINT 2: THURSDAY 3PM (Day 4, 75% Complete)

**Goal**: Test Material-UI components with real API data

### Track A Deliverables (Required)
- ✅ AppShell layout component complete
- ✅ 3-5 Material-UI components styled with SP-404 theme
- ✅ Sample list page functional
- ✅ API client handles errors gracefully

### Track B Deliverables (Required)
- ✅ PostgreSQL optimized (indexes, vacuum)
- ✅ Redis container running
- ✅ Nginx rate limiting configured
- ✅ SSL certificate valid (A+ grade)

### Integration Test: Component + API

**Performed By**: Both developers
**Location**: Zoom/Slack call
**Duration**: 30 minutes

#### Step 1: Test Sample List Component

**Track A: Open sample list page**:
```bash
# Start React dev with staging API
npm run dev

# Open browser to http://localhost:5173/samples
# Expected:
# - Material-UI DataGrid with samples
# - SP-404 cyan theme applied
# - Loading states visible
# - Pagination working
```

**Track B: Monitor API requests**:
```bash
# SSH to VPS
ssh deploy@$VPS_IP

# Tail Nginx access logs
sudo tail -f /var/log/nginx/sp404_access.log

# Should see:
# "GET /api/v1/public/samples?limit=25&offset=0 HTTP/2.0" 200
```

#### Step 2: Test Real-Time Features (WebSocket)

**Track A: Test vibe analysis WebSocket**:
```typescript
// In React DevTools console
const ws = new WebSocket('wss://sp404.yourdomain.com/ws/vibe/123');
ws.onopen = () => console.log('✅ WebSocket connected');
ws.onmessage = (msg) => console.log('Message:', msg.data);
ws.onerror = (err) => console.error('❌ WebSocket error:', err);
```

**Expected Output**:
```
✅ WebSocket connected
Message: {"status": "analyzing", "progress": 25}
Message: {"status": "analyzing", "progress": 50}
Message: {"status": "complete", "vibe": {...}}
```

**Track B: Monitor WebSocket connections**:
```bash
# Check active WebSocket connections
sudo netstat -an | grep :8100 | grep ESTABLISHED
# Should show: connections from Nginx

# Check backend logs (if deployed)
docker logs sp404-backend-temp | grep -i websocket
```

#### Step 3: Performance Testing

**Track A: Measure page load time**:
```bash
# Open Chrome DevTools
# Navigate to /samples
# Check Network tab:
# - Initial load: <2 seconds
# - API call: <500ms
# - WebSocket connect: <200ms
```

**Track B: Monitor server resources**:
```bash
# Check CPU and memory
htop

# Check Docker stats
docker stats --no-stream

# Expected:
# - PostgreSQL: <25% CPU, <512MB RAM
# - Redis: <5% CPU, <256MB RAM
# - Nginx: <5% CPU, <64MB RAM
```

### Success Criteria
- ✅ Sample list page loads in <2 seconds
- ✅ API responses return in <500ms
- ✅ WebSocket connects successfully
- ✅ Material-UI theme applied correctly
- ✅ Pagination works (25 samples per page)
- ✅ Loading states show during API calls
- ✅ Error messages display for failed requests

### Troubleshooting

**Issue: Slow API Responses (>1 second)**

**Track B: Check PostgreSQL performance**:
```bash
# Check slow queries
docker exec sp404-postgres psql -U sp404_user -d sp404_samples -c "
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Add missing indexes
docker exec sp404-postgres psql -U sp404_user -d sp404_samples -c "
CREATE INDEX IF NOT EXISTS idx_sample_genre ON sample(genre);
CREATE INDEX IF NOT EXISTS idx_sample_created_at ON sample(created_at DESC);
"

# Vacuum and analyze
docker exec sp404-postgres psql -U sp404_user -d sp404_samples -c "VACUUM ANALYZE;"
```

**Issue: WebSocket Disconnects**

**Track B: Check Nginx WebSocket config**:
```bash
# Ensure Nginx config has:
location ~ ^/ws/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 7d;  # Long timeout for WebSocket
}

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

---

## CHECKPOINT 3: FRIDAY 3PM (Day 5, 100% Complete)

**Goal**: Full end-to-end integration demo

### Track A Deliverables (Required)
- ✅ All 5 tasks complete
- ✅ Playwright E2E tests passing (10+ scenarios)
- ✅ Production build created (`npm run build`)
- ✅ Build artifacts ready for deployment

### Track B Deliverables (Required)
- ✅ All 5 tasks complete
- ✅ VPS secured and hardened
- ✅ SSL certificate valid
- ✅ Database backup system operational
- ✅ Ready to deploy Track A build

### Integration Test: Full Deployment

**Performed By**: Both developers
**Location**: Zoom/Slack call (screen share)
**Duration**: 60 minutes

#### Step 1: Build React App for Production

**Track A: Create production build**:
```bash
# Navigate to react-app
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/react-app

# Update .env.production
cat > .env.production << 'EOF'
VITE_API_URL=https://sp404.yourdomain.com/api/v1
EOF

# Build for production
npm run build

# Verify build output
ls -lh dist/
# Should show:
# - index.html
# - assets/ (JS, CSS, fonts, images)

# Check bundle size
du -sh dist/
# Should be <5MB

# Test production build locally
npm run preview
# Visit http://localhost:4173
```

#### Step 2: Deploy React Build to VPS

**Track A: Transfer build to VPS**:
```bash
# Create archive
tar -czf react-build.tar.gz -C dist .

# Transfer to VPS
scp react-build.tar.gz deploy@sp404.yourdomain.com:/opt/sp404/

# Extract on VPS (Track B will do this)
```

**Track B: Deploy React build**:
```bash
# SSH to VPS
ssh deploy@$VPS_IP
cd /opt/sp404

# Create frontend directory
mkdir -p frontend/dist

# Extract build
tar -xzf react-build.tar.gz -C frontend/dist/

# Verify files
ls -la frontend/dist/
# Should show: index.html, assets/

# Update Nginx config (already done in Task 5)
# location / {
#     root /opt/sp404/frontend/dist;
#     try_files $uri $uri/ /index.html;
# }

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

#### Step 3: End-to-End User Journey Test

**Both Developers: Walk through user journey**:

1. **Landing Page**:
   ```
   Visit: https://sp404.yourdomain.com
   Expected:
   - React app loads
   - AppShell with sidebar visible
   - SP-404 cyan theme applied
   - No console errors
   ```

2. **Navigate to Samples**:
   ```
   Click: Samples in sidebar
   Expected:
   - Sample grid loads from API
   - Material-UI DataGrid renders
   - 25 samples per page
   - Pagination controls visible
   ```

3. **Filter Samples**:
   ```
   Action: Filter by genre "Jazz"
   Expected:
   - API call with filter parameter
   - Filtered results display
   - Loading spinner during fetch
   ```

4. **Play Sample**:
   ```
   Action: Click play button on sample
   Expected:
   - Audio player loads
   - Waveform visualizer displays
   - Sample plays correctly
   ```

5. **Real-Time Vibe Analysis** (if backend deployed):
   ```
   Action: Click "Analyze Vibe" button
   Expected:
   - WebSocket connects
   - Progress updates in real-time
   - Vibe results display
   ```

6. **Navigate to Settings**:
   ```
   Click: Settings in sidebar
   Expected:
   - Settings page loads
   - Material-UI form components render
   - Preferences load from API
   ```

7. **Mobile View**:
   ```
   Action: Resize browser to 375px width
   Expected:
   - Sidebar collapses
   - Menu button appears
   - Responsive layout works
   ```

#### Step 4: Performance Validation

**Track A: Run Lighthouse audit**:
```bash
# Open Chrome DevTools
# Navigate to Lighthouse tab
# Run audit for:
# - Performance
# - Accessibility
# - Best Practices
# - SEO

# Target scores:
# - Performance: 90+
# - Accessibility: 95+
# - Best Practices: 95+
# - SEO: 90+
```

**Track B: Monitor server during Lighthouse**:
```bash
# Watch server resources
htop

# Watch Nginx logs
sudo tail -f /var/log/nginx/sp404_access.log

# Check response times
# All requests should complete in <500ms
```

#### Step 5: E2E Tests Against Production

**Track A: Run Playwright tests against production**:
```bash
# Update Playwright config
cat > playwright.config.ts << 'EOF'
export default defineConfig({
  use: {
    baseURL: 'https://sp404.yourdomain.com',
  },
});
EOF

# Run E2E tests
npm run test:e2e

# Expected:
# - 10+ tests pass
# - 0 failures
# - <2 minutes total runtime
```

### Success Criteria
- ✅ React app deployed and accessible via HTTPS
- ✅ All pages load correctly
- ✅ API integration working (samples, settings, etc.)
- ✅ WebSocket real-time features functional
- ✅ Mobile responsive layout works
- ✅ SSL certificate valid (A+ grade)
- ✅ Lighthouse scores >90% in all categories
- ✅ Playwright E2E tests pass against production
- ✅ No console errors or warnings
- ✅ Page load time <2 seconds

### Demo Checklist

Present to stakeholders:
- [ ] Show https://sp404.yourdomain.com landing page
- [ ] Demonstrate navigation through all pages
- [ ] Filter and search samples
- [ ] Play audio sample
- [ ] Show mobile responsive view
- [ ] Display Lighthouse scores
- [ ] Run E2E test suite (screen share)
- [ ] Show server monitoring (htop, Docker stats)

---

## API CONTRACT VALIDATION

### Endpoints Used by Track A

Track A requires these API endpoints from Track B:

#### 1. Health Check
```http
GET /health
Response: 200 OK
{
  "status": "healthy"
}
```

#### 2. Get Samples (Public)
```http
GET /api/v1/public/samples?limit=25&offset=0&genre=Jazz
Response: 200 OK
[
  {
    "id": 1,
    "name": "Sample Name",
    "genre": "Jazz",
    "bpm": 120,
    "key": "C minor",
    "duration": 5.2,
    "file_path": "/samples/sample.wav",
    "created_at": "2025-01-15T10:30:00Z"
  },
  ...
]
```

#### 3. Get Sample Detail
```http
GET /api/v1/public/samples/{sample_id}
Response: 200 OK
{
  "id": 1,
  "name": "Sample Name",
  "genre": "Jazz",
  "bpm": 120,
  "key": "C minor",
  "vibe": "Smooth, laid-back jazz vibes",
  "audio_features": {
    "tempo": 119.8,
    "spectral_centroid": 1234.5
  }
}
```

#### 4. WebSocket Vibe Analysis
```http
WS /ws/vibe/{sample_id}
Messages:
→ Client: {"action": "analyze"}
← Server: {"status": "analyzing", "progress": 25}
← Server: {"status": "analyzing", "progress": 50}
← Server: {"status": "analyzing", "progress": 75}
← Server: {"status": "complete", "vibe": "..."}
```

#### 5. User Preferences
```http
GET /api/v1/preferences
Response: 200 OK
{
  "model": "qwen/qwen3-7b-it",
  "auto_analyze": true,
  "cost_limit": 10.0
}

PATCH /api/v1/preferences
Request: { "model": "qwen/qwen3-235b-a22b-2507" }
Response: 200 OK
{
  "model": "qwen/qwen3-235b-a22b-2507",
  ...
}
```

### CORS Configuration

Track B must allow these origins:
```python
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:5173",  # Track A dev server
    "http://localhost:4173",  # Track A preview server
    "https://sp404.yourdomain.com",  # Production
]
```

---

## MERGE STRATEGY

### End of Week 1: How to Merge Work

#### Track A: Prepare for Merge
```bash
# Ensure all changes committed
git status
# Should show: nothing to commit, working tree clean

# Create PR from feature branch
git checkout -b feat/track-a-week1
git add .
git commit -m "feat(ui): Week 1 Material-UI integration

- Install Material-UI v7 with SP-404 theme
- Create component catalog (15+ components)
- Build AppShell layout (responsive)
- Setup Playwright E2E testing (10+ tests)
- Document migration matrix

✅ All 5 tasks complete
✅ E2E tests passing
✅ Production build ready"

git push origin feat/track-a-week1

# Create PR on GitHub
# Title: "Week 1: Material-UI Integration (Track A)"
# Reviewers: Track B developer
```

#### Track B: Prepare for Merge
```bash
# Document infrastructure in code
# Create infrastructure-as-code files

# Commit configuration files
git checkout -b feat/track-b-week1
git add \
  docker-compose.yml \
  .env.example \
  nginx/sp404.conf \
  scripts/backup_*.sh \
  docs/deployment/

git commit -m "feat(infra): Week 1 production infrastructure

- Provision Vultr VPS (4GB RAM, 2 vCPUs)
- Deploy Docker + PostgreSQL + Redis
- Configure Nginx reverse proxy with SSL
- Restore 2,328+ samples to production DB
- Setup automated backups

✅ All 5 tasks complete
✅ HTTPS live at sp404.yourdomain.com
✅ A+ SSL grade
✅ Database optimized"

git push origin feat/track-b-week1

# Create PR on GitHub
# Title: "Week 1: Production Infrastructure (Track B)"
# Reviewers: Track A developer
```

#### Merge Order
1. **Track B merges first** (infrastructure must be live)
2. **Track A merges second** (deploys to Track B infrastructure)
3. **Create integration branch** (optional, for final testing)

#### Post-Merge Validation
```bash
# After both PRs merged to main
git checkout main
git pull

# Verify all files present
ls -la react-app/       # Track A work
ls -la docker-compose.yml  # Track B work

# Run full test suite
cd react-app && npm run test:e2e

# Deploy to production
# (See Week 2 CI/CD setup)
```

---

## COMMUNICATION PROTOCOL

### Daily Standup Template

**Posted in**: `#deployment-week1` Slack channel
**Time**: 9:00 AM daily

```
**Track [A/B] Daily Update - [Day X/5]**

✅ Completed Yesterday:
- [Task 1]
- [Task 2]

🔨 Working On Today:
- [Task 3]
- [Task 4]

🚧 Blockers:
- [None / Issue description]

📊 Progress: [X/5 tasks complete]

Integration Notes:
- [Anything Track A/B needs to know]
```

### Blocker Escalation

**Minor Blocker** (can wait 4+ hours):
- Post in `#deployment-week1`
- Tag other developer
- Continue with other tasks

**Major Blocker** (needs immediate help):
1. Post in `#deployment-week1` with `@channel`
2. DM other developer
3. Schedule quick call (15 min)

### Integration Issue Template

When integration test fails:

```
**Integration Test Failed: [Test Name]**

Track: [A/B]
Checkpoint: [1/2/3]
Severity: [Low/Medium/High]

**Expected**:
[What should happen]

**Actual**:
[What actually happened]

**Error Message**:
```
[Full error message/screenshot]
```

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]

**Suspected Cause**:
[Track A/B issue]

**Needs Help From**:
@[Track A/B developer]
```

---

## WEEK 2 HANDOFF

### What Gets Handed Off

**Track A → Week 2**:
- Material-UI component library (15+ components)
- SP-404 cyan theme system
- AppShell responsive layout
- Playwright E2E test framework
- Component migration matrix

**Track B → Week 2**:
- Live production infrastructure
- PostgreSQL with 2,328+ samples
- Redis caching layer
- Nginx reverse proxy (HTTPS)
- Backup and monitoring systems

**Integrated System → Week 2**:
- React app deployed to production
- API fully functional
- WebSocket real-time features
- SSL certificate (A+ grade)
- E2E tests running against production

### Week 2 Priorities

**Track A Week 2**:
1. Migrate 10+ shadcn/ui components to Material-UI
2. Implement sample library browser (DataGrid)
3. Build authentication UI components
4. Add 20+ E2E test scenarios

**Track B Week 2**:
1. Deploy Laravel 11 for auth/billing
2. Setup CI/CD with GitHub Actions
3. Configure monitoring (Prometheus + Grafana)
4. Implement blue-green deployment

**Integration Week 2**:
- Continuous deployment pipeline
- Automated E2E tests on every commit
- Performance monitoring dashboard
- Error tracking (Sentry)

---

## APPENDIX: Quick Reference

### Track A Developer Quick Commands
```bash
# Start dev with staging API
export VITE_API_URL=https://sp404.yourdomain.com/api/v1
npm run dev

# Build for production
npm run build

# Run E2E tests
npm run test:e2e

# Check API connectivity
curl https://sp404.yourdomain.com/health
```

### Track B Developer Quick Commands
```bash
# SSH to VPS
ssh deploy@sp404.yourdomain.com

# Check Docker containers
docker compose ps

# View logs
docker compose logs -f postgres
docker compose logs -f redis

# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Monitor server
htop
docker stats
```

### Integration Test Commands
```bash
# Test CORS from Track A
curl -H "Origin: http://localhost:5173" \
  -I https://sp404.yourdomain.com/api/v1/public/samples

# Test WebSocket
wscat -c wss://sp404.yourdomain.com/ws/vibe/123

# Test SSL certificate
curl -I https://sp404.yourdomain.com | grep -i "strict-transport"
```

---

## CONCLUSION

Week 1 integration is **low risk** because:
1. Tracks are independent (no blocking dependencies)
2. API contracts are well-defined (existing FastAPI endpoints)
3. CORS is simple to configure
4. WebSocket already implemented in both stacks
5. Three checkpoints catch issues early

**Key Success Factor**: Communication
- Daily standups keep both tracks aligned
- Integration checkpoints validate assumptions
- Slack channel provides real-time coordination
- Screen-share demos build confidence

By Friday 3 PM, both tracks will have:
- ✅ Independently completed all 5 tasks
- ✅ Successfully integrated 3 times
- ✅ Deployed a working production system
- ✅ Validated with E2E tests
- ✅ Ready for Week 2 development

**Let's ship Week 1!** 🚀
