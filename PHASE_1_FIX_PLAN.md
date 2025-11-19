# Phase 1 Fix Plan
**Goal**: Convert all 47 contaminated endpoints to JSON-only responses

---

## Overview

**Current State**: 47/92 endpoints (51%) have dual JSON/HTML response logic
**Target State**: 100% JSON-only responses (except file downloads)
**Estimated Time**: 4-6 hours

---

## Contaminated Files (Priority Order)

### 1. batch.py - 7 contaminated endpoints (PUBLIC ROUTER)
**File**: `backend/app/api/v1/endpoints/batch.py`
**Lines**: 154-522 (public_router section)

**Endpoints to Fix**:
- ❌ POST /public/batch/ (line 154)
- ❌ GET /public/batch/ (line 227)
- ❌ GET /public/batch/{id} (line 272)
- ❌ POST /public/batch/{id}/import (line 303)
- ❌ POST /public/batch/{id}/cancel (line 361)
- ❌ POST /public/batch/{id}/retry (line 409)
- ✅ GET /public/batch/{id}/export (line 479) - FileResponse, OK

**Changes Required**:
```python
# REMOVE this pattern:
hx_request: Optional[str] = Header(None)

if hx_request:
    return HTMLResponse(content=f"""...""")

# KEEP only:
return {json_response}
```

**Templates to DELETE** (after fixing):
- `templates/partials/active-batches.html`
- `templates/partials/batch-history.html`
- `templates/partials/batch-details.html`

---

### 2. kits.py - 4 contaminated endpoints
**File**: `backend/app/api/v1/endpoints/kits.py`
**Lines**: 96-542

**Endpoints to Fix**:
- ❌ GET /kits (line 96)
- ❌ GET /kits/{id} (line 188)
- ❌ POST /kits/{id}/assign (line 316)
- ❌ GET /kits/{id}/recommendations/{pad} (line 449)

**Changes**:
```python
# REMOVE:
hx_request: Optional[str] = Header(None)

# REMOVE:
if hx_request:
    return templates.TemplateResponse("kits/kit-list.html", {...})

# RETURN only JSON:
return KitListResponse(...)
```

**Templates to DELETE**:
- `templates/kits/kit-list.html`
- `templates/kits/kit-detail.html`
- `templates/kits/pad-assignment.html`
- `templates/kits/recommendations-dropdown.html`

---

### 3. sp404_export.py - 4 contaminated endpoints
**File**: `backend/app/api/v1/endpoints/sp404_export.py`
**Lines**: 49-539

**Endpoints to Fix**:
- ❌ POST /sp404/samples/{id}/export (line 49)
- ❌ POST /sp404/samples/export-batch (line 144)
- ❌ POST /sp404/kits/{kit_id}/export (line 259)
- ❌ GET /sp404/exports (line 481)

**Templates to DELETE**:
- `templates/sp404/export-result.html`
- `templates/sp404/export-progress.html`
- `templates/sp404/export-list.html`

---

### 4. samples.py - 3 contaminated endpoints
**File**: `backend/app/api/v1/endpoints/samples.py`
**Lines**: 93-544

**Endpoints to Fix**:
- ❌ GET /samples/ (line 93)
- ❌ GET /public/samples/ (line 417)
- ❌ POST /public/samples/{id}/analyze (line 204)

**Changes**:
```python
# Line 93-163 - list_samples()
# REMOVE lines 147-153 (HTMX response)
# KEEP lines 156-162 (JSON response)

# Line 417-484 - list_samples_public()
# REMOVE lines 467-474 (HTMX response)
# KEEP lines 477-483 (JSON response)
```

**Templates to DELETE**:
- `templates/partials/sample-grid.html`

---

### 5. public.py - 3 contaminated endpoints
**File**: `backend/app/api/v1/endpoints/public.py`
**Lines**: 19-256

**Endpoints to Fix**:
- ❌ GET /public/samples/ (line 19)
- ❌ POST /public/samples/ (line 124)
- ❌ POST /public/samples/{id}/analyze (line 204)

**Note**: This duplicates functionality from samples.py public_router
**Consider**: Deleting this entire file and using samples.py public endpoints instead

---

### 6. preferences.py - 2 contaminated endpoints
**File**: `backend/app/api/v1/endpoints/preferences.py`
**Lines**: 41-147

**Endpoints to Fix**:
- ❌ GET /preferences (line 41)
- ❌ PATCH /preferences (line 72)

**Templates to DELETE**:
- `templates/preferences/preferences-form.html`
- `templates/preferences/preferences-success.html`

---

## Step-by-Step Fix Process

### For Each Contaminated Endpoint:

1. **Locate the endpoint function**
2. **Remove the `hx_request` parameter**:
   ```python
   # REMOVE:
   hx_request: Optional[str] = Header(None)
   ```

3. **Delete the HTMX conditional block**:
   ```python
   # DELETE:
   if hx_request:
       return templates.TemplateResponse(...)
   ```

4. **Keep only the JSON return**:
   ```python
   # KEEP:
   return {
       "items": items,
       "total": total,
       ...
   }
   ```

5. **Verify imports** (remove if unused):
   ```python
   # May be able to remove:
   from fastapi import Header, Request
   from fastapi.responses import HTMLResponse
   from fastapi.templating import Jinja2Templates
   ```

6. **Test the endpoint** (after all fixes):
   ```bash
   curl -s http://localhost:8100/api/v1/endpoint | jq .
   ```

---

## Automated Cleanup Script

After fixing all endpoints, run:

```bash
# Create: scripts/cleanup-htmx.sh

#!/bin/bash

echo "🧹 Cleaning up HTMX artifacts..."

# Remove template directories
rm -rf backend/templates/partials/
rm -rf backend/templates/kits/
rm -rf backend/templates/sp404/
rm -rf backend/templates/preferences/

# Remove template config if no templates remain
REMAINING=$(find backend/templates -name "*.html" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "No templates remaining - safe to remove templates directory"
    rm -rf backend/templates/

    # Remove template imports from main.py
    sed -i '' '/templates/d' backend/app/main.py
    sed -i '' '/Jinja2Templates/d' backend/app/main.py
fi

echo "✅ Cleanup complete"
```

---

## Validation Script

After all fixes, run:

```bash
# Create: scripts/validate-json-responses.py

import requests
import json

BASE_URL = "http://localhost:8100"

ENDPOINTS = [
    ("GET", "/api/v1/kits"),
    ("GET", "/api/v1/samples"),
    ("GET", "/api/v1/preferences"),
    ("GET", "/api/v1/public/samples/"),
    ("GET", "/api/v1/public/batch/"),
    ("GET", "/api/v1/sp404/exports"),
    # ... all 92 endpoints
]

failed = []

for method, endpoint in ENDPOINTS:
    try:
        resp = requests.request(method, f"{BASE_URL}{endpoint}")

        # Check it's not HTML
        if resp.text.startswith("<"):
            failed.append(f"{method} {endpoint}: Returns HTML")
            continue

        # Check it's valid JSON
        json.loads(resp.text)
        print(f"✓ {method} {endpoint}")

    except json.JSONDecodeError:
        failed.append(f"{method} {endpoint}: Invalid JSON")
    except Exception as e:
        failed.append(f"{method} {endpoint}: {str(e)}")

if failed:
    print(f"\n❌ FAILED: {len(failed)} endpoints")
    for f in failed:
        print(f"  - {f}")
    exit(1)
else:
    print(f"\n✅ SUCCESS: All {len(ENDPOINTS)} endpoints return JSON")
```

---

## Checklist

### Pre-Fix
- [x] Identify all contaminated endpoints (47 found)
- [x] Create fix plan
- [ ] Create backup branch: `git checkout -b backup/before-htmx-removal`

### During Fix
- [ ] Fix batch.py (7 endpoints)
- [ ] Fix kits.py (4 endpoints)
- [ ] Fix sp404_export.py (4 endpoints)
- [ ] Fix samples.py (3 endpoints)
- [ ] Fix public.py (3 endpoints)
- [ ] Fix preferences.py (2 endpoints)

### Post-Fix
- [ ] Remove unused imports
- [ ] Delete template files
- [ ] Run validation script
- [ ] Test all user workflows
- [ ] Update API documentation

### Final Validation
- [ ] All endpoints return JSON
- [ ] No HTML responses
- [ ] WebSocket connections work
- [ ] React app can consume all APIs
- [ ] No console errors

---

## Estimated Timeline

| Task | Time |
|------|------|
| Fix batch.py | 45 min |
| Fix kits.py | 30 min |
| Fix sp404_export.py | 30 min |
| Fix samples.py | 20 min |
| Fix public.py | 20 min |
| Fix preferences.py | 15 min |
| Remove templates | 10 min |
| Validation testing | 1 hour |
| **Total** | **3.5-4 hours** |

---

## Next Steps After Phase 1

Once all 47 endpoints are fixed:

1. **Phase 2**: Remove `frontend/` directory (old HTMX UI)
2. **Phase 3**: Update documentation
3. **Phase 4**: Deploy React-only app

---

**Created**: 2025-11-18
**Status**: Ready to execute
