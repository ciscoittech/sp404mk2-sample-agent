# React 19 Deployment Guide

**Application**: SP-404MK2 Sample Agent
**Frontend**: React 19 SPA
**Backend**: FastAPI
**Status**: Production Ready
**Last Updated**: 2025-11-18

---

## Overview

The SP404MK2 Sample Agent now uses a pure React 19 single-page application (SPA) frontend with a FastAPI backend. This guide covers deployment strategies, configuration, and best practices.

---

## Architecture

### Frontend (React 19)
- **Framework**: React 19
- **Router**: React Router v7 (client-side routing)
- **UI Framework**: shadcn/ui + Tailwind CSS
- **State Management**: React Query + Zustand
- **Build Tool**: Vite
- **Language**: TypeScript (strict mode)
- **Bundle Size**: ~270 KB gzipped

### Backend (FastAPI)
- **Framework**: FastAPI
- **Database**: PostgreSQL (production) / SQLite (local dev)
- **ORM**: SQLAlchemy (async)
- **WebSocket**: Real-time updates for batch processing and vibe analysis
- **API**: RESTful JSON endpoints

### Integration
- React SPA served by FastAPI from `/` route
- API endpoints at `/api/v1/*`
- WebSocket at `/ws/*`
- Static assets at `/assets/*`

---

## Development Setup

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 14+ (production) or SQLite (local)

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database
cd backend
python -m app.db.init_db

# Start backend server
cd ..
./venv/bin/python backend/run.py
# Server runs on http://localhost:8100
```

### Frontend Setup
```bash
# Navigate to React app
cd react-app

# Install dependencies
npm install

# Start dev server (with hot reload)
npm run dev
# Dev server runs on http://localhost:5173
```

### Environment Variables

Create `.env` in project root:
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/sp404
OPENROUTER_API_KEY=your_api_key_here

# Frontend (build time)
VITE_API_URL=http://localhost:8100
```

---

## Production Build

### Build React App
```bash
cd react-app

# Install dependencies
npm install

# Build for production
npm run build

# Output: react-app/dist/
# - index.html
# - assets/*.js (code-split chunks)
# - assets/*.css (optimized styles)
```

### Expected Build Output
```
dist/
├── index.html                   0.76 kB
├── assets/
│   ├── index-[hash].css        79.08 kB (13.14 kB gzipped)
│   ├── audio-[hash].js         33.72 kB (10.07 kB gzipped)
│   ├── ui-[hash].js            33.94 kB (11.15 kB gzipped)
│   ├── vendor-[hash].js        44.29 kB (15.71 kB gzipped)
│   ├── query-[hash].js         76.39 kB (25.29 kB gzipped)
│   └── index-[hash].js        951.89 kB (270.66 kB gzipped)

Total: ~270 KB gzipped
```

### FastAPI Serving Configuration

FastAPI automatically serves the React build from `react-app/dist/`:

**File**: `backend/app/main.py`
```python
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Get absolute path to React build
react_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "react-app",
    "dist"
)

# Mount static assets
app.mount("/assets", StaticFiles(directory=os.path.join(react_dist, "assets")), name="assets")

# Serve React app for all routes (SPA fallback)
@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    """Serve React SPA for all non-API routes"""
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        # Let API routes handle themselves
        return None

    return FileResponse(os.path.join(react_dist, "index.html"))
```

---

## Docker Deployment

### Dockerfile (Multi-stage Build)

**File**: `Dockerfile`
```dockerfile
# Stage 1: Build React app
FROM node:20-alpine AS frontend-builder
WORKDIR /app/react-app
COPY react-app/package*.json ./
RUN npm ci
COPY react-app/ ./
RUN npm run build

# Stage 2: Python backend + serve React
FROM python:3.13-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY src/ ./src/

# Copy React build from frontend-builder stage
COPY --from=frontend-builder /app/react-app/dist ./react-app/dist

# Expose port
EXPOSE 8100

# Start FastAPI server
CMD ["python", "backend/run.py"]
```

### Docker Compose

**File**: `docker-compose.yml`
```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: sp404
      POSTGRES_PASSWORD: sp404pass
      POSTGRES_DB: sp404
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    ports:
      - "8100:8100"
    environment:
      DATABASE_URL: postgresql://sp404:sp404pass@db:5432/sp404
      OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}
    depends_on:
      - db
    volumes:
      - ./samples:/app/samples
      - ./downloads:/app/downloads

volumes:
  postgres_data:
```

### Docker Commands
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up --build

# Stop all services
docker-compose down

# Clean up (including volumes)
docker-compose down -v
```

---

## Cloud Deployment

### Vercel (Frontend Only)

**Not recommended** - Vercel only deploys frontend, backend needs separate hosting.

### Fly.io (Full Stack - Recommended)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly launch

# Deploy
fly deploy

# Set environment variables
fly secrets set OPENROUTER_API_KEY=your_key
fly secrets set DATABASE_URL=your_postgres_url
```

**File**: `fly.toml`
```toml
app = "sp404-sample-agent"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8100"

[[services]]
  internal_port = 8100
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.http_checks]]
    interval = 10000
    timeout = 2000
    path = "/api/v1/health"
```

### Railway (Full Stack)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up

# Link database
railway add postgresql
```

### Render (Full Stack)

1. Connect GitHub repository
2. Create Web Service (Docker)
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

---

## Performance Optimization

### Code Splitting

React app already uses automatic code splitting:
- Vendor chunk: React core libraries
- UI chunk: shadcn/ui components
- Audio chunk: Audio processing utilities
- Query chunk: React Query and data fetching

### Bundle Analysis

```bash
cd react-app

# Install analyzer
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

### Production Optimizations

Already configured in `vite.config.ts`:
```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react', 'react-dom', 'react-router-dom'],
        ui: ['@radix-ui/*', 'lucide-react'],
        audio: ['wavesurfer.js'],
        query: ['@tanstack/react-query']
      }
    }
  }
}
```

---

## Monitoring & Logging

### Backend Logging

FastAPI includes built-in logging:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Request processed")
logger.error("Error occurred", exc_info=True)
```

### Frontend Error Tracking (Optional)

Add Sentry for production error tracking:
```bash
npm i @sentry/react @sentry/vite-plugin
```

**File**: `react-app/src/main.tsx`
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

### Performance Monitoring

Web Vitals already included in React app:
- LCP (Largest Contentful Paint): < 300ms
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): 0.00

---

## Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use different keys for dev/staging/prod
- Rotate API keys regularly

### CORS Configuration

**File**: `backend/app/main.py`
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Content Security Policy

Add to `react-app/index.html`:
```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline'">
```

---

## Troubleshooting

### Build Errors

**Issue**: "Module not found"
```bash
cd react-app
rm -rf node_modules package-lock.json
npm install
```

**Issue**: "Out of memory"
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Runtime Errors

**Issue**: 404 on routes
- Verify FastAPI fallback route configured
- Check React Router routes

**Issue**: WebSocket connection failed
- Verify backend WebSocket endpoint running
- Check CORS configuration
- Verify proxy settings in dev mode

**Issue**: API calls failing
- Verify `VITE_API_URL` in `.env`
- Check backend server running on port 8100
- Verify CORS headers

---

## Production Checklist

### Pre-Deploy
- [ ] Run tests: `npm test` and `pytest`
- [ ] Build locally: `npm run build`
- [ ] Check bundle size: < 300 KB gzipped
- [ ] Update environment variables
- [ ] Review error boundaries
- [ ] Check TypeScript errors: `npm run type-check`

### Deploy
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Check WebSocket connections
- [ ] Test audio playback
- [ ] Verify API endpoints
- [ ] Check responsive design

### Post-Deploy
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify analytics tracking
- [ ] Set up uptime monitoring
- [ ] Configure alerts

---

## Resources

### Documentation
- [React 19 Docs](https://react.dev/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Bundle Analyzer](https://github.com/btd/rollup-plugin-visualizer)
- [Web Vitals](https://web.dev/vitals/)

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0 (React 19 Migration Complete)
**Maintainer**: SP-404MK2 Sample Agent Team
