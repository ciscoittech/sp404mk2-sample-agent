# Production Deployment Checklist

## Pre-Deployment Validation

### Code Quality
- [ ] All tests pass locally (`pytest backend/tests/`)
- [ ] No TypeScript errors (`cd react-app && npm run build`)
- [ ] No linting errors (`ruff check backend/`)
- [ ] No type errors (`mypy backend/app/`)
- [ ] Code reviewed and approved
- [ ] All dependencies updated to stable versions

### Frontend Verification
- [ ] React app builds successfully (`npm run build`)
- [ ] Build output exists in `react-app/dist/`
- [ ] No console errors in browser
- [ ] All routes work correctly
- [ ] API calls succeed from UI
- [ ] WebSocket connections stable
- [ ] No broken images or assets
- [ ] Mobile responsive design verified

### Backend Verification
- [ ] Database migrations created (`alembic revision`)
- [ ] Migrations tested locally
- [ ] API endpoints respond correctly
- [ ] WebSocket endpoints functional
- [ ] Audio processing works (librosa)
- [ ] File uploads work
- [ ] Error handling tested
- [ ] Rate limiting configured (if applicable)

### Docker Configuration
- [ ] Dockerfile builds successfully
- [ ] Multi-stage build optimized
- [ ] Image size reasonable (<1GB)
- [ ] No sensitive data in image
- [ ] Health check configured
- [ ] Proper base image versions (Python 3.13, Node 20)
- [ ] .dockerignore configured

### docker-compose.yml
- [ ] Production environment variables set
- [ ] Development volumes commented out
- [ ] Database credentials secured
- [ ] Correct port mappings (8100:8100)
- [ ] Volume persistence configured
- [ ] Network isolation configured
- [ ] Health checks enabled
- [ ] Restart policies set (`unless-stopped`)

### Environment Variables
- [ ] `DATABASE_URL` configured
- [ ] `OPENROUTER_API_KEY` set (if using AI features)
- [ ] `ENVIRONMENT=production` set
- [ ] `SECRET_KEY` configured (if using auth)
- [ ] `POSTGRES_PASSWORD` changed from default
- [ ] `.env` file NOT committed to git
- [ ] Environment variables documented

### Security
- [ ] Default passwords changed
- [ ] Database password is strong (32+ characters)
- [ ] No hardcoded secrets in code
- [ ] CORS origins properly configured
- [ ] SQL injection protection verified (SQLAlchemy ORM)
- [ ] File upload size limits set
- [ ] Rate limiting configured (if public)
- [ ] HTTPS/TLS configured (if applicable)
- [ ] Security headers configured

### Database
- [ ] PostgreSQL 16 container ready
- [ ] Database initialized (`app.db.init_db`)
- [ ] Migrations applied (`alembic upgrade head`)
- [ ] Database backup created
- [ ] Connection pool configured
- [ ] Index optimization verified
- [ ] Database credentials stored securely

---

## Deployment Process

### 1. Backup Current State
- [ ] Database backup created
  ```bash
  docker exec sp404-postgres pg_dump -U sp404_user sp404_samples > backup_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] Backup location documented
- [ ] Backup tested (can restore)
- [ ] Previous Docker image tagged
  ```bash
  docker tag sp404-sample-agent:latest sp404-sample-agent:previous
  ```

### 2. Build New Image
- [ ] Latest code pulled from git
- [ ] Git commit hash documented
- [ ] React app built locally (verify no errors)
  ```bash
  cd react-app && npm run build
  ```
- [ ] Docker image built
  ```bash
  docker build -t sp404-sample-agent:latest .
  ```
- [ ] Build logs reviewed (no errors)
- [ ] Image size verified (<1GB)
  ```bash
  docker images sp404-sample-agent:latest
  ```

### 3. Stop Current Services
- [ ] Current deployment documented (version, commit)
- [ ] Active users notified (if applicable)
- [ ] Containers stopped gracefully
  ```bash
  docker-compose down
  ```
- [ ] Volumes preserved (not deleted)
- [ ] Logs archived
  ```bash
  docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
  ```

### 4. Deploy New Version
- [ ] Environment variables verified
  ```bash
  docker-compose config
  ```
- [ ] Containers started
  ```bash
  docker-compose up -d
  ```
- [ ] Startup logs monitored
  ```bash
  docker-compose logs -f backend
  ```
- [ ] Health check passed
  ```bash
  curl http://localhost:8100/health
  ```
- [ ] Database migrations applied
  ```bash
  docker-compose exec backend alembic upgrade head
  ```

### 5. Post-Deployment Verification
- [ ] Application accessible at http://localhost:8100
- [ ] React app loads correctly
- [ ] API responds to requests
  ```bash
  curl http://localhost:8100/api/v1/samples
  ```
- [ ] WebSocket connections work
- [ ] Database queries succeed
- [ ] File uploads work
- [ ] Audio processing works
- [ ] No errors in logs
- [ ] Container health: `healthy`
  ```bash
  docker ps
  ```

---

## Smoke Tests

### Web UI Tests
- [ ] Homepage loads
- [ ] Navigation works
- [ ] Samples page displays samples
- [ ] Sample cards render correctly
- [ ] Audio preview works
- [ ] Search/filter works
- [ ] Collections page works
- [ ] Project builder page works
- [ ] Settings page loads
- [ ] No console errors

### API Tests
- [ ] GET /health returns 200
- [ ] GET /api/v1/samples returns data
- [ ] POST /api/v1/samples/analyze works
- [ ] GET /api/v1/collections returns data
- [ ] POST /api/v1/collections works
- [ ] GET /api/v1/usage/summary returns data
- [ ] WebSocket /ws/vibe/{sample_id} connects

### Audio Processing Tests
- [ ] Upload sample file
- [ ] Audio features extracted (BPM, key)
- [ ] AI vibe analysis completes (if API key set)
- [ ] Waveform visualization displays
- [ ] Audio playback works
- [ ] Export to SP-404 format works

### Integration Tests
- [ ] Create new collection
- [ ] Add samples to collection
- [ ] Build kit from collection
- [ ] Generate SP-404 project
- [ ] Download project files
- [ ] Verify PADCONF.BIN format

---

## Performance Verification

### Response Times
- [ ] Homepage loads < 2 seconds
- [ ] API requests < 500ms
- [ ] Sample analysis < 10 seconds
- [ ] Database queries < 100ms
- [ ] WebSocket latency < 200ms

### Resource Usage
- [ ] Container memory < 1GB
- [ ] CPU usage < 50% (idle)
- [ ] Disk space sufficient (>10GB free)
- [ ] Database connections < pool limit
- [ ] No memory leaks detected

### Monitoring
- [ ] Logs flowing correctly
- [ ] Error tracking configured (if applicable)
- [ ] Metrics collection configured (if applicable)
- [ ] Alerts configured (if applicable)

---

## Rollback Plan

### Rollback Triggers
- [ ] Critical bugs discovered
- [ ] Database corruption
- [ ] Service unavailable >5 minutes
- [ ] Data loss detected
- [ ] Security vulnerability found

### Rollback Steps
1. [ ] Stop new containers
   ```bash
   docker-compose down
   ```

2. [ ] Restore previous image
   ```bash
   docker tag sp404-sample-agent:previous sp404-sample-agent:latest
   ```

3. [ ] Restore database backup
   ```bash
   docker exec -i sp404-postgres psql -U sp404_user sp404_samples < backup_YYYYMMDD.sql
   ```

4. [ ] Start previous version
   ```bash
   docker-compose up -d
   ```

5. [ ] Verify rollback successful
   ```bash
   curl http://localhost:8100/health
   ```

6. [ ] Document rollback reason
   - [ ] Issue logged
   - [ ] Root cause identified
   - [ ] Fix planned

---

## Post-Deployment Tasks

### Documentation
- [ ] Deployment documented in CHANGELOG.md
- [ ] Version number updated
- [ ] Git tag created
  ```bash
  git tag -a v1.0.0 -m "Production release"
  git push origin v1.0.0
  ```
- [ ] Release notes written

### Monitoring
- [ ] Monitor logs for errors (first 24 hours)
- [ ] Monitor resource usage
- [ ] Monitor user reports (if applicable)
- [ ] Check database performance

### Communication
- [ ] Stakeholders notified of successful deployment
- [ ] Users informed of new features
- [ ] Known issues documented
- [ ] Support team briefed

### Cleanup
- [ ] Old Docker images removed
  ```bash
  docker image prune -a
  ```
- [ ] Old logs archived
- [ ] Temporary files cleaned
- [ ] Development volumes removed (if mounted)

---

## Deployment Metrics

### Deployment Information
- **Date**: _______________
- **Time**: _______________
- **Deployed By**: _______________
- **Git Commit**: _______________
- **Version**: _______________
- **Environment**: Production / Staging / Development

### Build Information
- **Build Time**: _______________ seconds
- **Image Size**: _______________ MB
- **Frontend Build Size**: _______________ MB
- **Backend Dependencies**: _______________ packages

### Deployment Results
- **Deployment Duration**: _______________ minutes
- **Downtime**: _______________ minutes
- **Issues Encountered**: _______________
- **Rollback Required**: Yes / No

### Performance Baselines
- **Homepage Load Time**: _______________ ms
- **API Response Time**: _______________ ms
- **Container Memory**: _______________ MB
- **Container CPU**: _______________ %

---

## Sign-Off

### Technical Validation
- [ ] Lead Developer: _______________
- [ ] QA Engineer: _______________
- [ ] DevOps Engineer: _______________

### Deployment Approval
- [ ] Technical Lead: _______________
- [ ] Product Owner: _______________
- [ ] Date/Time: _______________

### Notes
```
[Add any deployment notes, issues, or observations here]
```

---

## Quick Reference

### Useful Commands

```bash
# Health check
curl http://localhost:8100/health

# View logs
docker-compose logs -f backend

# Container status
docker ps

# Resource usage
docker stats sp404-backend

# Database connection
docker exec -it sp404-postgres psql -U sp404_user -d sp404_samples

# Execute command in container
docker-compose exec backend python -m app.db.init_db

# Restart service
docker-compose restart backend

# View environment
docker-compose config
```

### Emergency Contacts
- **Technical Lead**: _______________
- **On-Call DevOps**: _______________
- **Database Admin**: _______________

### Important Links
- **Application**: http://localhost:8100
- **API Docs**: http://localhost:8100/api/v1/docs
- **Database**: localhost:5432
- **Repository**: _______________
- **Issue Tracker**: _______________
