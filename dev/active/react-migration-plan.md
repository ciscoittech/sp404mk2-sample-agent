# React Migration Plan: Remove HTMX/Alpine.js Stack

**Status**: In Planning
**Created**: 2025-11-18
**Target Completion**: 3-4 days
**Complexity**: Medium
**Risk Level**: Low (React SPA fully implemented, fallback available)

---

## EXECUTIVE SUMMARY

Remove the deprecated Jinja2/HTMX/Alpine.js server-side rendering stack (15 templates, 44 HTMX attributes, 5 Alpine directives) and consolidate to the production-ready React 19 SPA that already implements all features.

**Impact**:
- Eliminate 906 lines of Jinja2 templates
- Remove 147 lines of template serving code
- Simplify API responses (JSON only)
- Reduce deployment complexity
- Eliminate client-side Alpine.js components

**Benefit**:
- Single unified frontend (React 19)
- Improved developer experience (TypeScript)
- Better code reusability
- Easier testing and debugging
- Cleaner API contracts

---

## CURRENT STATE ANALYSIS

### What Exists in HTMX/Alpine Stack
- **15 Jinja2 templates** (906 lines total)
- **5 FastAPI routes** serving HTML
- **44 HTMX attributes** for interactivity
- **5 Alpine.js directives** for UI state
- **2 WebSocket endpoints** with dual support
- **14 endpoints** with dual JSON/HTML response modes

### What Exists in React Stack
- **63+ components** (production-ready)
- **13 page components** (full coverage)
- **14 custom hooks** (data fetching, WebSocket, state)
- **10 API client modules** (complete coverage)
- **React Query** integration (caching, mutations)
- **TypeScript strict mode** (100% type-safe)
- **Tailwind CSS + shadcn/ui** (modern UI)
- **Already serving on port 8100**

### Migration Readiness: ✅ 95%
- React app implements 100% of features
- API endpoints support dual modes
- WebSocket integration exists
- No missing functionality
- Zero breaking changes required

---

## ARCHITECTURE DESIGN

### Phase 1: Validation & Preparation
1. Verify React app fully replaces all HTMX pages
2. Test all API endpoints return correct JSON
3. Verify WebSocket connections work
4. Build React production bundle
5. Document migration approach

### Phase 2: Backend Cleanup
1. Remove dual-response logic from endpoints
2. Simplify API responses (JSON only)
3. Remove template routing
4. Remove Jinja2 configuration
5. Update API documentation

### Phase 3: Frontend Cleanup
1. Remove HTML fallback pages
2. Remove Alpine.js components from static
3. Remove unused static assets
4. Clean up CSS overrides
5. Verify all routes work

### Phase 4: Final Cleanup & Testing
1. Remove template directories
2. Remove template configuration files
3. Run full test suite
4. End-to-end testing
5. Update documentation

---

## DETAILED TASK BREAKDOWN

### PHASE 1: VALIDATION & PREPARATION (4-6 hours)

#### Task 1.1: Verify React Feature Parity
- **What**: Ensure React implements all HTMX functionality
- **Files to Check**:
  - `react-app/src/pages/KitsPage.tsx` vs `backend/templates/kits/*`
  - `react-app/src/pages/SettingsPage.tsx` vs `backend/templates/preferences/*`
  - `react-app/src/pages/SamplesPage.tsx` vs `backend/templates/partials/sample-grid.html`
  - `react-app/src/pages/DashboardPage.tsx` vs `backend/templates/sp404/export-list.html`
  - `react-app/src/components/layout/AppShell.tsx` vs `frontend/pages/base.html`
- **Success Criteria**:
  - All HTMX workflows work in React
  - All Alpine.js state managed in React
  - All API calls return correct data
  - Form submissions work correctly

#### Task 1.2: Test API Endpoints (JSON Mode)
- **What**: Verify all endpoints return valid JSON without HX-Request header
- **Endpoints to Test** (24 total):
  ```
  GET  /api/v1/kits
  GET  /api/v1/kits/{kit_id}
  POST /api/v1/kits
  POST /api/v1/kits/{kit_id}/assign
  GET  /api/v1/kits/{kit_id}/recommendations/{pad}
  PATCH /api/v1/preferences
  GET  /api/v1/preferences
  GET  /api/v1/sp404/exports
  GET  /api/v1/public/batch
  GET  /api/v1/public/batch/{batch_id}
  GET  /api/v1/public/samples
  + 13 more endpoints
  ```
- **Test Method**: Use `curl` without HX-Request header, verify JSON response
- **Success Criteria**: All endpoints return valid JSON (no HTML)

#### Task 1.3: Verify WebSocket Integration
- **What**: Test both WebSocket endpoints work correctly
- **Endpoints**:
  - `/ws/vibe/{sample_id}` - Vibe analysis real-time
  - `/api/v1/batch/{batch_id}/progress` - Batch progress
- **React Hooks**: Verify `useWebSocket` hook
- **Success Criteria**: Real-time messages arrive correctly

#### Task 1.4: Build React Production Bundle
- **What**: Create optimized production build
- **Command**: `cd react-app && npm run build`
- **Output**: `react-app/dist/` directory with optimized assets
- **Success Criteria**:
  - Build completes without errors
  - Bundle size acceptable (<500KB gzipped)
  - Source maps generated for debugging

#### Task 1.5: Documentation & Approach
- **Create Migration Checklist**: Document all pages/features to migrate
- **Update CLAUDE.md**: Note React as primary frontend
- **Create Rollback Plan**: Document how to revert if needed

---

### PHASE 2: BACKEND CLEANUP (3-4 hours)

#### Task 2.1: Remove Dual-Response Logic
- **Files to Modify**:
  1. `backend/app/api/v1/endpoints/kits.py` (828 lines)
     - Remove `hx_request: Optional[str] = Header(None)` checks (4 locations)
     - Remove all `if hx_request:` branches
     - Keep JSON responses

  2. `backend/app/api/v1/endpoints/preferences.py` (147 lines)
     - Remove HX-Request detection (lines 45-51)
     - Remove template response (lines 51-53)
     - Keep JSON response

  3. `backend/app/api/v1/endpoints/samples.py`
     - Remove HX-Request detection
     - Keep JSON response

  4. `backend/app/api/v1/endpoints/batch.py`
     - Remove all template responses
     - Keep JSON responses

  5. `backend/app/api/v1/endpoints/sp404_export.py`
     - Remove template responses
     - Keep JSON responses

- **Pattern to Remove**:
  ```python
  # REMOVE THIS PATTERN
  hx_request: Optional[str] = Header(None)

  if hx_request:
      return templates.TemplateResponse("template.html", {...})
  return JSONResponse(...)

  # KEEP ONLY
  return JSONResponse(...) or Model(...)
  ```

- **Lines to Delete**: ~150 lines across 5 files
- **Success Criteria**: Endpoints return only JSON

#### Task 2.2: Remove Template Routing
- **File**: `backend/app/main.py` (108 lines)
- **Remove**:
  - Lines 73-76: `/health` endpoint (keep but simplify)
  - Lines 80-89: `/pages/usage.html` and `/pages/settings.html` routes
  - Lines 101-107: WebSocket wrapper (keep but simplify)

- **Keep**: Static file mounting for React build, CORS, exception handlers

- **Result**: Main.py reduced to ~80 lines

#### Task 2.3: Remove Jinja2 Configuration
- **Files to Delete**:
  1. `backend/app/templates_config.py` (36 lines)
     - No longer needed - templates removed

  2. Remove from `backend/app/main.py`:
     - `from app.templates_config import templates, frontend_dir` (line 70)
     - Template rendering imports

- **Files to Update**:
  1. `backend/app/main.py`:
     - Remove Jinja2Templates import
     - Remove template imports

- **Result**: Cleaner imports, faster startup

#### Task 2.4: Update API Response Types
- **What**: Add type hints for JSON-only responses
- **Files to Update**:
  - All endpoint files (5 files)

- **Pattern**:
  ```python
  # Before
  async def get_kits(...) -> Union[TemplateResponse, List[KitSchema]]:
      if hx_request:
          return templates.TemplateResponse(...)
      return [...]

  # After
  async def get_kits(...) -> List[KitSchema]:
      return [...]
  ```

- **Success Criteria**: Type hints match JSON-only responses

#### Task 2.5: Update API Documentation
- **Files**:
  - OpenAPI schema (auto-generated by FastAPI)
  - Any endpoint documentation files

- **What to Update**:
  - Remove template response examples
  - Remove HX-Request header from docs
  - Update response schemas

- **Success Criteria**: OpenAPI docs reflect JSON-only responses

---

### PHASE 3: FRONTEND CLEANUP (2-3 hours)

#### Task 3.1: Remove HTML Fallback Pages
- **Directory**: `backend/frontend/pages/` (contains HTML pages)
- **Files to Delete** (if present):
  - `dashboard.html`
  - `samples.html`
  - `kits.html`
  - `settings.html`
  - `usage.html`
  - Any other `.html` pages

- **Why**: React handles all routing; HTML fallbacks no longer needed

#### Task 3.2: Remove Alpine.js Components
- **Files to Delete**:
  1. `frontend/static/js/components.js` (Alpine sample player)
  2. Any Alpine-specific utilities

- **What to Keep**:
  - CSS files (Tailwind base)
  - Images/assets
  - Theme utilities (if standalone)

#### Task 3.3: Remove Unused Static Assets
- **Files to Delete**:
  - `frontend/static/js/filters.js` (if Alpine-dependent)
  - `frontend/static/js/vibe-search-demo.js` (if HTMX-dependent)
  - Any HTML that's not part of React build

- **Files to Keep**:
  - Tailwind CSS
  - Fonts
  - Images
  - Icons

#### Task 3.4: Simplify CSS
- **What**: Remove CSS that only applies to HTMX/Alpine components
- **Example Classes to Remove**:
  - `.htmx-loading` indicators
  - `.htmx-swapping` animations
  - Alpine-specific styles

- **What to Keep**:
  - Tailwind base styles
  - Custom component styles
  - Theme variables

#### Task 3.5: Update Static File Mounting
- **File**: `backend/app/main.py`
- **Change**:
  ```python
  # Remove old frontend mounts
  app.mount("/static", StaticFiles(...))
  app.mount("/pages", StaticFiles(...))

  # Keep React dist mount
  app.mount("/", StaticFiles(directory="react-app/dist", html=True))
  ```

- **Result**: Only React build artifacts served

---

### PHASE 4: FINAL CLEANUP & TESTING (3-4 hours)

#### Task 4.1: Remove Template Directories
- **Directories to Delete**:
  1. `backend/templates/` (entire directory)
     - `kits/` (6 files)
     - `preferences/` (2 files)
     - `sp404/` (3 files)
     - `partials/` (4 files)

  2. `frontend/pages/` (all HTML pages except index.html for React)

  3. Related directories:
     - `frontend/static/js/` (Alpine components)
     - Keep only: `frontend/static/css/`, images, fonts

- **Impact**: Removes 906 lines of code

#### Task 4.2: Remove Template Configuration
- **Files to Delete**:
  1. `backend/app/templates_config.py` (36 lines)

- **Files to Update**:
  1. `backend/requirements.txt` or `pyproject.toml`
     - No dependency on Jinja2 needed (remove if not used elsewhere)
     - Check: `pip freeze | grep jinja` to see if needed

  2. `backend/app/db/init_db.py` or similar
     - Ensure no Jinja2 usage in data initialization

#### Task 4.3: Run Full Test Suite
- **Commands**:
  ```bash
  # Backend tests
  cd backend && ../venv/bin/pytest -v

  # Frontend tests (if any)
  cd react-app && npm test

  # Type checking
  mypy backend/app
  cd react-app && npm run type-check
  ```

- **Success Criteria**:
  - All backend tests pass (150+ tests)
  - All React tests pass
  - Zero type errors
  - Zero lint errors

#### Task 4.4: End-to-End Testing
- **Scenarios to Test**:
  1. **Kit Management**
     - Create kit
     - Assign samples to pads
     - Remove samples
     - Export kit to SP-404

  2. **Settings**
     - Change model preference
     - Toggle auto-analysis
     - Set cost limits
     - Save settings

  3. **Sample Browse**
     - View samples
     - Play audio preview
     - Filter/search
     - Lazy load on scroll

  4. **Real-time Features**
     - WebSocket vibe analysis
     - Real-time progress updates
     - Live notifications

  5. **Dashboard**
     - View stats
     - Recent activity
     - Quick actions

- **Test Method**: Manual testing in browser
- **Success Criteria**: All workflows work without errors

#### Task 4.5: Verify React App Deployment
- **What**: Ensure React app serves correctly at port 8100
- **Steps**:
  1. Build React app: `npm run build`
  2. Start backend: `./venv/bin/python backend/run.py`
  3. Visit `http://localhost:8100`
  4. Verify routing works
  5. Verify API calls succeed

- **Success Criteria**:
  - React app loads
  - All routes work
  - All API calls succeed
  - Real-time features work

#### Task 4.6: Update Documentation
- **Files to Update**:
  1. `CLAUDE.md` - Update project memory
     - Note: Pure React frontend
     - Remove references to HTMX/Alpine
     - Update quick start

  2. `docs/INDEX.md` - Update docs index

  3. `README.md` - Update if exists

  4. `.github/` - Update CI/CD if exists

- **What to Add**:
  - React tech stack
  - Frontend build process
  - Frontend deployment steps
  - Removed HTMX stack

---

## ROLLBACK PLAN

**If Issues Arise**:

1. **Partial Rollback** (React + JSON API still running):
   ```bash
   git stash
   git checkout [previous-commit]
   ```

2. **Full Rollback** (Return to HTMX):
   ```bash
   git revert [migration-commits]
   git checkout templates/
   git checkout frontend/pages/
   ```

3. **No Breaking Changes**: API endpoints were backward-compatible
   - React app works with either JSON-only or dual-mode APIs
   - Can run parallel during migration

---

## DEPENDENCY ANALYSIS

### Python Dependencies
- ✅ **Jinja2**: Can remove if no other template engine needed
- ✅ **jinja2-env**: Template environment - can remove

### Frontend Dependencies
- ✅ **Alpine.js**: Can remove from CDN/assets
- ✅ **HTMX**: Can remove from CDN/assets
- ✅ **DaisyUI**: Keep if using Tailwind (or migrate to shadcn/ui)

### What to Keep
- ✅ **React 19**: Core frontend
- ✅ **Tailwind CSS**: Styling
- ✅ **shadcn/ui**: Components
- ✅ **React Query**: Data fetching
- ✅ **Zustand**: State management
- ✅ **WebSocket**: Real-time communication

---

## TIMELINE ESTIMATE

| Phase | Duration | Critical Path |
|-------|----------|---|
| Phase 1: Validation | 4-6 hrs | Build React, test endpoints |
| Phase 2: Backend | 3-4 hrs | Remove dual-mode logic |
| Phase 3: Frontend | 2-3 hrs | Clean static files |
| Phase 4: Testing | 3-4 hrs | Full E2E validation |
| **Total** | **12-17 hrs** | **3-4 days of work** |

---

## SUCCESS CRITERIA

### Technical
- ✅ All backend tests pass (150+)
- ✅ All React components work
- ✅ All API endpoints return JSON
- ✅ WebSocket connections work
- ✅ Real-time features operational
- ✅ Zero console errors/warnings

### Code Quality
- ✅ No template files remain
- ✅ No dual-response logic
- ✅ TypeScript strict mode clean
- ✅ Zero linting errors

### User Experience
- ✅ All features work
- ✅ No performance degradation
- ✅ Smooth animations
- ✅ Real-time updates functional
- ✅ Loading states working

### Documentation
- ✅ CLAUDE.md updated
- ✅ API docs updated
- ✅ Development guide updated
- ✅ Deployment guide updated

---

## RISK ANALYSIS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| React app missing feature | Low | High | Task 1.1 validates parity |
| WebSocket breaks | Low | Medium | Task 1.3 verifies connections |
| Build issues | Low | Medium | Task 1.4 tests production build |
| API regression | Low | High | Task 4.3 runs full test suite |
| Deployment failure | Low | High | Task 4.5 verifies serving |

---

## NEXT STEPS

1. **Proceed to Implementation**: Start with Phase 1 validation
2. **Document Findings**: Update this plan as work progresses
3. **Create Commits**: One commit per phase for easy rollback
4. **Notify Team**: Update CLAUDE.md when complete

---

## RELATED DOCUMENTATION

- **Current State Analysis**: See HTMX_ALPINE_ANALYSIS.md
- **React Architecture**: See react-app/
- **API Documentation**: See docs/
- **Deployment Guide**: See DEPLOYMENT_GUIDE.md
