# API Endpoint Inventory
**Total Endpoints**: 92
**Contaminated with HTMX**: 47 (51%)
**Clean JSON-only**: 45 (49%)

---

## Contaminated Endpoints (MUST FIX)

### batch.py (7 endpoints) ❌
```
POST   /api/v1/public/batch/                    - Create batch (returns HTML)
GET    /api/v1/public/batch/                    - List batches (returns HTML)
GET    /api/v1/public/batch/{id}                - Get batch (returns HTML)
POST   /api/v1/public/batch/{id}/import         - Import results (returns HTML)
POST   /api/v1/public/batch/{id}/cancel         - Cancel batch (returns HTML)
POST   /api/v1/public/batch/{id}/retry          - Retry batch (returns HTML)
GET    /api/v1/public/batch/{id}/export         - Export batch (FileResponse) ✅
```

### kits.py (4 endpoints) ❌
```
GET    /api/v1/kits                             - List kits (returns HTML)
GET    /api/v1/kits/{id}                        - Get kit (returns HTML)
POST   /api/v1/kits/{id}/assign                 - Assign to pad (returns HTML)
GET    /api/v1/kits/{id}/recommendations/{pad}  - Get recommendations (returns HTML)
```

### sp404_export.py (4 endpoints) ❌
```
POST   /api/v1/sp404/samples/{id}/export        - Export sample (returns HTML)
POST   /api/v1/sp404/samples/export-batch       - Batch export (returns HTML)
POST   /api/v1/sp404/kits/{kit_id}/export       - Export kit (returns HTML)
GET    /api/v1/sp404/exports                    - List exports (returns HTML)
```

### samples.py (3 endpoints) ❌
```
GET    /api/v1/samples/                         - List samples (returns HTML)
GET    /api/v1/public/samples/                  - List public samples (returns HTML)
POST   /api/v1/public/samples/{id}/analyze      - Analyze sample (returns HTML)
```

### public.py (3 endpoints) ❌
```
GET    /api/v1/public/samples/                  - List samples (returns HTML)
POST   /api/v1/public/samples/                  - Upload sample (JSON only) ✅
POST   /api/v1/public/samples/{id}/analyze      - Analyze sample (returns HTML)
```

### preferences.py (2 endpoints) ❌
```
GET    /api/v1/preferences                      - Get preferences (returns HTML)
PATCH  /api/v1/preferences                      - Update preferences (returns HTML)
```

---

## Clean Endpoints (JSON-only) ✅

### auth.py (2 endpoints)
```
POST   /api/v1/auth/register                    - Register user
POST   /api/v1/auth/login                       - Login user
```

### samples.py (8 clean endpoints)
```
POST   /api/v1/samples/                         - Create sample
GET    /api/v1/samples/search                   - Search samples
GET    /api/v1/samples/{id}                     - Get sample
GET    /api/v1/samples/{id}/analysis-debug      - Analysis debug
PATCH  /api/v1/samples/{id}                     - Update sample
DELETE /api/v1/samples/{id}                     - Delete sample
POST   /api/v1/samples/{id}/analyze             - Analyze sample
GET    /api/v1/samples/{id}/download            - Download sample (FileResponse)
GET    /api/v1/public/samples/{id}/download     - Download public sample (FileResponse)
```

### batch.py (5 clean endpoints)
```
POST   /api/v1/batch/                           - Create batch
GET    /api/v1/batch/                           - List batches
GET    /api/v1/batch/{id}                       - Get batch
POST   /api/v1/batch/{id}/cancel                - Cancel batch
WS     /api/v1/batch/{id}/progress              - Progress WebSocket
```

### usage.py (10 endpoints)
```
GET    /api/v1/usage/summary                    - Usage summary
GET    /api/v1/usage/daily                      - Daily usage
GET    /api/v1/usage/budget                     - Budget status
GET    /api/v1/usage/recent                     - Recent calls
GET    /api/v1/usage/export                     - Export CSV
GET    /api/v1/public/usage/summary             - Public summary
GET    /api/v1/public/usage/budget              - Public budget
GET    /api/v1/public/usage/daily               - Public daily
GET    /api/v1/public/usage/recent              - Public recent
```

### preferences.py (1 clean endpoint)
```
GET    /api/v1/preferences/models               - Available models
```

### sp404_export.py (1 clean endpoint)
```
GET    /api/v1/sp404/exports/{id}/download      - Download export (FileResponse)
```

### kits.py (8 clean endpoints)
```
POST   /api/v1/kits                             - Create kit
PATCH  /api/v1/kits/{id}                        - Update kit
DELETE /api/v1/kits/{id}                        - Delete kit
DELETE /api/v1/kits/{id}/pads/{bank}/{number}   - Remove pad
POST   /api/v1/kits/{id}/export                 - Export kit (StreamingResponse)
POST   /api/v1/kits/build                       - AI build kit
POST   /api/v1/kits/{id}/complete-from-sample/{sample_id} - Complete kit
```

### vibe_search.py (2 endpoints)
```
GET    /api/v1/search/vibe                      - Vibe search
GET    /api/v1/search/similar/{sample_id}       - Similar samples
```

### projects.py (2 endpoints)
```
POST   /api/v1/projects/from-kit/{kit_id}       - Build project
GET    /api/v1/projects/download/{export_id}    - Download project (FileResponse)
```

### collections.py (9 endpoints)
```
POST   /api/v1/collections                      - Create collection
GET    /api/v1/collections                      - List collections
GET    /api/v1/collections/{id}                 - Get collection
PUT    /api/v1/collections/{id}                 - Update collection
DELETE /api/v1/collections/{id}                 - Delete collection
POST   /api/v1/collections/{id}/samples         - Add samples
DELETE /api/v1/collections/{id}/samples/{sample_id} - Remove sample
GET    /api/v1/collections/{id}/samples         - Get samples
POST   /api/v1/collections/{id}/evaluate        - Evaluate smart collection
```

### public.py (1 clean endpoint)
```
GET    /api/v1/public/debug/env                 - Debug environment
```

---

## Fix Priority

### High Priority (User-facing features)
1. **batch.py** - Batch processing UI (7 endpoints)
2. **kits.py** - Kit builder UI (4 endpoints)
3. **samples.py** - Sample browsing (3 endpoints)

### Medium Priority (Admin/Export features)
4. **sp404_export.py** - Export functionality (4 endpoints)
5. **preferences.py** - Settings page (2 endpoints)

### Low Priority (Duplicate functionality)
6. **public.py** - Duplicates samples.py public endpoints (consider deleting)

---

## Templates to Delete (After Fixing Endpoints)

```
backend/templates/
├── partials/
│   ├── sample-grid.html               ← Used by samples.py
│   ├── batch-details.html             ← Used by batch.py
│   ├── active-batches.html            ← Used by batch.py
│   └── batch-history.html             ← Used by batch.py
├── kits/
│   ├── kit-list.html                  ← Used by kits.py
│   ├── kit-detail.html                ← Used by kits.py
│   ├── pad-assignment.html            ← Used by kits.py
│   └── recommendations-dropdown.html  ← Used by kits.py
├── sp404/
│   ├── export-result.html             ← Used by sp404_export.py
│   ├── export-progress.html           ← Used by sp404_export.py
│   └── export-list.html               ← Used by sp404_export.py
└── preferences/
    ├── preferences-form.html          ← Used by preferences.py
    └── preferences-success.html       ← Used by preferences.py
```

**Total Templates**: 13 files to delete

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Endpoints | 92 |
| Contaminated | 47 (51%) |
| Clean | 45 (49%) |
| Files with Issues | 6 |
| Files Clean | 5 |
| Templates to Delete | 13 |

---

**Last Updated**: 2025-11-18
