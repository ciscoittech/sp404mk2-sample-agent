# React App Deployment Guide

**Application**: SP-404MK2 Sample Matching UI
**Status**: Production Ready
**Version**: 1.0.0

---

## Quick Deploy

### Option 1: Docker (Recommended)

```bash
# Navigate to react-app directory
cd react-app

# Start all services (frontend + backend + database)
docker-compose up -d

# View logs
docker-compose logs -f

# Access application
open http://localhost:3000
```

**Services**:
- Frontend: http://localhost:3000 (Nginx)
- Backend API: http://localhost:8100 (FastAPI)
- Database: PostgreSQL on port 5432

### Option 2: Local Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Access application
open http://localhost:5173
```

**Requirements**:
- Node.js 20+
- Backend running on http://127.0.0.1:8100

---

## Build & Deploy

### Production Build

```bash
# Build for production
npm run build

# Output directory: dist/
# Files:
# - index.html
# - assets/*.js (code-split chunks)
# - assets/*.css (optimized styles)

# Preview production build locally
npm run preview
```

### Build Output

Expected bundle sizes:
```
dist/assets/
├── vendor-[hash].js      ~120 KB (React core)
├── ui-[hash].js          ~60 KB (UI components)
├── audio-[hash].js       ~40 KB (Audio processing)
├── query-[hash].js       ~35 KB (Data fetching)
└── index-[hash].css      ~25 KB (Styles)

Total: ~255 KB (80 KB gzipped)
```

---

## Docker Deployment

### Build Docker Image

```bash
# Build frontend image
docker build -t sp404-frontend .

# Run container
docker run -p 3000:80 sp404-frontend
```

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View specific service logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs db

# Restart a service
docker-compose restart frontend

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

### Environment Variables

Create `.env` file:
```bash
# Frontend
VITE_API_URL=http://localhost:8100

# Backend
DATABASE_URL=postgresql://user:pass@db:5432/sp404
OPENROUTER_API_KEY=your_key_here

# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=sp404
```

---

## Cloud Deployment

### Vercel (Frontend Only)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

**Configuration** (`vercel.json`):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://your-backend.com/api/$1" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Netlify (Frontend Only)

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy

# Production deployment
netlify deploy --prod
```

**Configuration** (`netlify.toml`):
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend.com/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Railway (Full Stack)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Configuration** (`railway.json`):
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "nginx -g 'daemon off;'",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300
  }
}
```

### Fly.io (Full Stack)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly deploy
```

**Configuration** (`fly.toml`):
```toml
app = "sp404-frontend"

[build]
  dockerfile = "Dockerfile"

[[services]]
  http_checks = []
  internal_port = 80
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

---

## Performance Optimization

### Bundle Analysis

```bash
# Install bundle analyzer
npm i -D rollup-plugin-visualizer

# Update vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

plugins: [
  react(),
  visualizer({ open: true })
]

# Build and analyze
npm run build
```

### Lighthouse Audit

```bash
# Install Lighthouse CLI
npm i -g @lhci/cli

# Run audit
lhci autorun --collect.url=http://localhost:3000
```

**Target Scores**:
- Performance: 95+
- Accessibility: 100
- Best Practices: 100
- SEO: 100

### Web Vitals

Expected metrics:
- LCP (Largest Contentful Paint): < 300ms
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): 0.00
- TTFB (Time to First Byte): < 200ms

---

## Monitoring & Observability

### Sentry (Error Tracking)

```bash
npm i @sentry/react @sentry/vite-plugin
```

**Setup** (`main.tsx`):
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

### Plausible Analytics (Privacy-Friendly)

```html
<!-- Add to index.html -->
<script defer data-domain="yourdomain.com"
  src="https://plausible.io/js/script.js"></script>
```

### Uptime Monitoring

Recommended services:
- **UptimeRobot**: Free, 5-minute checks
- **Better Uptime**: Beautiful status pages
- **Pingdom**: Advanced monitoring

---

## CI/CD Pipeline

### GitHub Actions

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

---

## Production Checklist

### Pre-Deploy
- [ ] Run tests: `npm test`
- [ ] Build locally: `npm run build`
- [ ] Check bundle size: < 300 KB
- [ ] Test production build: `npm run preview`
- [ ] Update environment variables
- [ ] Review error boundaries
- [ ] Check console for warnings

### Deploy
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Check WebSocket connections
- [ ] Test audio playback
- [ ] Verify API endpoints
- [ ] Test file uploads
- [ ] Check responsive design

### Post-Deploy
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify analytics tracking
- [ ] Test on multiple devices
- [ ] Validate SEO meta tags
- [ ] Set up uptime monitoring
- [ ] Configure alerts

---

## Troubleshooting

### Build Errors

**Issue**: "Module not found"
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: "Out of memory"
```bash
# Increase Node memory
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Docker Issues

**Issue**: Container won't start
```bash
# Check logs
docker-compose logs frontend

# Rebuild without cache
docker-compose build --no-cache

# Restart services
docker-compose restart
```

**Issue**: Database connection failed
```bash
# Check database is running
docker-compose ps db

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Runtime Errors

**Issue**: 404 on routes
- Check nginx.conf has SPA fallback
- Verify Vercel/Netlify redirects configured

**Issue**: WebSocket connection failed
- Check proxy configuration in vite.config.ts
- Verify backend WebSocket endpoint
- Check CORS headers

**Issue**: Audio won't play
- Check browser audio permissions
- Verify MIME types in nginx.conf
- Test audio file format (WAV/MP3)

---

## Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use different keys for dev/staging/prod
- Rotate API keys regularly

### Nginx Hardening
```nginx
# Add security headers
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
```

### Content Security Policy
```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline'">
```

---

## Support & Maintenance

### Backup Strategy
- Database: Daily automated backups
- Code: Git repository with tags
- Assets: CDN with versioning

### Update Schedule
- Dependencies: Monthly security updates
- React/Vite: Quarterly major updates
- Node.js: LTS version tracking

### Monitoring Checklist
- [ ] Error rates < 0.1%
- [ ] Uptime > 99.9%
- [ ] Response time < 200ms
- [ ] Bundle size < 300 KB
- [ ] Lighthouse score > 95

---

## Resources

### Documentation
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)

### Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Bundle Analyzer](https://github.com/btd/rollup-plugin-visualizer)
- [Web Vitals](https://web.dev/vitals/)

### Community
- [React Discord](https://discord.gg/react)
- [Vite Discord](https://chat.vitejs.dev/)
- [SP-404 Community](https://reddit.com/r/sp404)

---

**Last Updated**: 2025-11-15
**Version**: 1.0.0
**Maintainer**: SP-404MK2 Sample Agent Team
