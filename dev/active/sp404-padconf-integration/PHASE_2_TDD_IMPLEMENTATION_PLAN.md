# PHASE 2: SP-404MK2 PROJECT BUILDER - TDD IMPLEMENTATION PLAN

**Status**: Ready for Implementation
**Total Effort**: 24 hours (3 phases × 8 hours)
**Approach**: Test-Driven Development (TDD)
**Final Validation**: Complete user journey with MCP Chrome DevTools

---

## QUICK REFERENCE: PHASE BREAKDOWN

### PHASE 2A: Foundation & Schemas (8 hours)
**Goal**: Define all data contracts and validate request/response flows

**Deliverables**:
- ✅ `backend/app/schemas/sp404_project.py` (100 lines)
- ✅ `backend/tests/schemas/test_sp404_project_schemas.py` (150 lines)
- ✅ 100% test coverage for schemas
- ✅ mypy type checking passes

**Stage Gate**: Schemas validated, ready for service implementation

**Tests First** (2 hrs):
```python
# test_project_build_request_valid()
# test_project_build_request_invalid_project_name()
# test_project_build_request_invalid_bpm()
# test_project_build_request_invalid_format()
# test_project_build_result_serialization()
# test_request_json_roundtrip()
```

**Architecture** (3 hrs):
- Request schema: project_name (1-31 ASCII), bpm (20-300), format (wav/aiff), bank_layout
- Result schema: success, export_id, project_name, sample_count, file_size, download_url
- Validation rules: min/max lengths, numeric ranges, enum values

**Implementation** (2 hrs):
```python
class ProjectBuildRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=31)
    project_bpm: Optional[float] = Field(None, ge=20.0, le=300.0)
    audio_format: str = Field("wav", pattern="^(wav|aiff)$")
    include_bank_layout: bool = Field(False)

    @field_validator('project_name')
    def validate_ascii_only(v: str) -> str:
        if not v.isascii(): raise ValueError("ASCII only")
        return v
```

**Validation Checklist**:
- [ ] All schema validation tests passing
- [ ] Request/response models correct
- [ ] mypy type checking passes
- [ ] No circular dependencies

---

### PHASE 2B: Service & API (8 hours)
**Goal**: Implement project building logic and API endpoints

**Deliverables**:
- ✅ `backend/app/services/sp404_project_builder_service.py` (400 lines)
- ✅ `backend/tests/services/test_sp404_project_builder_service.py` (500 lines)
- ✅ `backend/tests/api/test_kits_project_endpoints.py` (200 lines)
- ✅ Extended `backend/app/api/v1/endpoints/kits.py` (+100 lines)
- ✅ >90% test coverage
- ✅ All endpoints responding correctly

**Stage Gate**: Service working, API functional, ready for UI

**Tests First** (3 hrs):
```python
# Service tests:
# async test_build_project_success()
# async test_build_project_kit_not_found()
# async test_build_project_no_samples()
# async test_detect_project_bpm_median()
# async test_detect_project_bpm_fallback()

# API tests:
# async test_build_project_endpoint_success()
# async test_build_project_endpoint_invalid_request()
# async test_download_project_endpoint_success()
```

**Architecture** (1 hr):
- Service: `build_project()` → BPM detection → audio conversion → PADCONF generation → ZIP creation
- API: `POST /kits/{id}/export-project` and `GET /exports/download/{id}`
- Database: Reuse existing sp404_exports table (type='project')
- File system: `/tmp/sp404_projects/{uuid}/samples/` + PADCONF.BIN + ZIP

**Implementation** (3 hrs):
```python
class SP404ProjectBuilderService:
    async def build_project(kit_id, request) -> ProjectBuildResult:
        1. Get kit and samples
        2. Detect BPM if auto
        3. Create temp directory
        4. Convert samples (audio)
        5. Generate PADCONF.BIN
        6. Create PROJECT_INFO.txt
        7. Create ZIP archive
        8. Track export in database
        9. Return result

    def _detect_project_bpm(samples) -> float:
        # Median BPM from samples, fallback to 120.0
```

**Validation Checklist**:
- [ ] Service unit tests >90% coverage
- [ ] Integration tests with real services
- [ ] API endpoints responding correctly
- [ ] Error handling working (404, 400, 500)
- [ ] Database queries verified
- [ ] ZIP file generation working
- [ ] PADCONF.BIN is 52,000 bytes

---

### PHASE 2C: Frontend & E2E (8 hours)
**Goal**: Implement UI and validate complete user journey

**Deliverables**:
- ✅ Updated `frontend/pages/kits.html` (+300 lines)
- ✅ `frontend/tests/e2e/test_project_builder.spec.ts` (100 lines)
- ✅ All E2E tests passing (4/4)
- ✅ Manual MCP test successful
- ✅ User journey validated end-to-end

**Stage Gate**: Complete user journey works, ready for production

**Tests First** (2 hrs):
```typescript
// E2E tests (Playwright):
// test('complete project builder flow')
// test('form validation errors')
// test('close modal without submitting')
// test('error handling - no samples')
```

**Architecture** (1 hr):
- Modal dialog (Alpine.js state management)
- Form with validation (project name, BPM, format, bank layout)
- Loading state with progress indicator
- Success screen with download link
- Error handling with user-friendly messages

**Implementation** (4 hrs):
```html
<button @click="showProjectBuilderModal()">
  Generate SP-404MK2 Project
</button>

<div x-show="projectBuilderOpen" class="modal">
  <!-- Form state -->
  <!-- Processing state (loading spinner) -->
  <!-- Success state (results + download) -->
  <!-- Error state (error message) -->
</div>
```

```javascript
function projectBuilderModal() {
  return {
    async submitProject():
      POST /api/v1/kits/{id}/export-project
      Handle response (success/error)
      Update state

    downloadProject():
      Click download link
      Browser downloads ZIP
  };
}
```

**Validation Checklist**:
- [ ] UI renders correctly
- [ ] Form validation works (client-side)
- [ ] Loading indicator shows
- [ ] Success screen displays results
- [ ] Download link works
- [ ] Error states show correctly
- [ ] E2E tests passing (4/4)
- [ ] Manual MCP test successful

---

## COMPLETE USER JOURNEY (FINAL TEST)

### Test: Project Builder E2E with MCP Chrome DevTools

**Step 1**: Navigate to kit detail page
```
URL: http://localhost:8100/kits/1
Expected: Kit name, description, pad grid visible
```

**Step 2**: Click "Generate SP-404MK2 Project" button
```
Action: Click button
Expected: Modal opens with form
```

**Step 3**: Fill form
```
Project Name: "E2E Test Project"
BPM: (leave empty for auto-detect)
Format: WAV (default)
Bank Layout: unchecked
```

**Step 4**: Submit form
```
Action: Click "Generate Project"
Expected: Loading spinner shows, processing message
```

**Step 5**: Wait for success
```
Expected: Success message within 15 seconds
- Project name: "E2E Test Project"
- Sample count: 12
- File size: displayed in MB
- Download link: visible
```

**Step 6**: Download ZIP
```
Action: Click download link
Expected: ZIP file downloads to browser
```

**Step 7**: Manual verification
```
Extract ZIP and verify:
- samples/ folder (12 .wav files)
- PADCONF.BIN (exactly 52,000 bytes)
- PROJECT_INFO.txt (human-readable)

Hex dump PADCONF.BIN:
- Offset 0x12: 0x01 (project tempo mode)
- Offset 0x13-0x14: project BPM (big-endian)
- Offset 0x81: project name (ASCII)
- Offset 0x6C20: sample filenames

Audio files:
- Format: 48kHz/16-bit WAV
- Stereo or mono
```

**Test Passes If**:
- ✅ All UI states work correctly
- ✅ Form submission succeeds
- ✅ ZIP downloads successfully
- ✅ ZIP structure is correct
- ✅ PADCONF.BIN is 52,000 bytes
- ✅ Audio files are correct format
- ✅ All manual verification checks pass

**Optional Hardware Test**:
```
IF SP-404MK2 available:
1. Copy extracted folder to SD card
2. Insert into hardware
3. Load project (MENU → PROJECT → LOAD)
4. Verify samples playable on pads 1-12
5. Verify BPM correct
```

---

## STAGE GATES & APPROVAL PROCESS

### Gate 1: Phase 2A Complete
**Before Proceeding to Phase 2B**:

- [ ] All schema validation tests passing
- [ ] Request/response models finalized
- [ ] mypy type checking: 0 errors
- [ ] No circular dependencies
- [ ] Architect approval: ✅
- [ ] Schemas follow existing patterns

**If blocked**: Return to architect, simplify validation rules, resolve circular deps

---

### Gate 2: Phase 2B Complete
**Before Proceeding to Phase 2C**:

- [ ] Service unit tests >90% coverage (28/30)
- [ ] Service integration tests passing
- [ ] API endpoint tests 100% passing
- [ ] Error handling tested (404, 400, 500)
- [ ] Database queries verified
- [ ] ZIP generation working
- [ ] PADCONF.BIN: 52,000 bytes
- [ ] Performance: <30 seconds for 16 samples
- [ ] Architect approval: ✅

**If blocked**: Profile performance, optimize queries, fix error handling

---

### Gate 3: Phase 2C Complete
**Ready for Production**:

- [ ] UI rendering correctly
- [ ] Form validation working (client-side)
- [ ] State management working (no stuck states)
- [ ] Loading indicator shows during processing
- [ ] Success screen displays correct data
- [ ] Error handling shows helpful messages
- [ ] E2E tests passing (4/4)
- [ ] Manual MCP test: PASSED
- [ ] ZIP structure verified
- [ ] PADCONF.BIN verified (hex dump)
- [ ] Audio files verified (format, sample rate)
- [ ] Architect approval: ✅

**If blocked**: Fix state management, simplify UI, increase timeouts

---

## RISK MITIGATION SUMMARY

| Risk | Severity | Mitigation | Rollback |
|------|----------|-----------|----------|
| PADCONF.BIN incorrect | 🔴 Critical | Extensive testing, hex comparison | Manual generation |
| Slow conversion (>30s) | 🟡 Medium | Profiling, parallelization, caching | Show progress indicator |
| File permission issues | 🟡 Medium | Use `/tmp`, test early | User temp dir |
| State management bugs | 🟡 Medium | Simple state machine (4 states) | Single-state modal |
| E2E test flakiness | 🟢 Low | Explicit waits, retry logic | Manual verification |

---

## CRITICAL ABORT CRITERIA

**Stop Phase 2A If**:
- Validators conflict with hardware requirements
- >5 validation rules per field (over-engineering)
- Schema fields don't match actual data flow

**Stop Phase 2B If**:
- Service exceeds 500 lines (refactor)
- Database queries are complex (>3 joins)
- API response time >30 seconds
- File permission issues prevent ZIP creation

**Stop Phase 2C If**:
- Modal rendering fails
- State management becomes chaotic (>300 lines)
- HTMX conflicts with existing patterns
- E2E test is flaky (>50% failure rate)

**Action**: Return to architect, redesign, resume phase

---

## SUCCESS METRICS

### Phase 2A: Schemas
- ✅ 10/10 tests passing (100% coverage)
- ✅ mypy: 0 errors
- ✅ No circular dependencies
- ✅ All validation rules correct

### Phase 2B: Service & API
- ✅ 28/30 tests passing (>90% coverage)
- ✅ API responses correct (JSON format)
- ✅ ZIP generation working
- ✅ PADCONF.BIN: 52,000 bytes
- ✅ Performance: <30 seconds per project

### Phase 2C: Frontend & E2E
- ✅ 4/4 E2E tests passing
- ✅ Manual MCP test: PASSED
- ✅ ZIP structure verified
- ✅ PADCONF.BIN verified (hex dump)
- ✅ Audio files verified (format, sample rate)
- ✅ User journey: complete end-to-end

---

## NEXT STEPS

1. **Review this plan** with architect
2. **Approve gates and criteria**
3. **Begin Phase 2A**: Create schemas with TDD
4. **Gate review**: Verify schemas before Phase 2B
5. **Begin Phase 2B**: Implement service and API
6. **Gate review**: Verify API before Phase 2C
7. **Begin Phase 2C**: Implement frontend and E2E tests
8. **Final validation**: Complete user journey with MCP
9. **Production ready**: Deploy to main branch

**Estimated Timeline**: 24 hours (3 × 8-hour phases)

---

Generated: 2025-11-17
Framework: Test-Driven Development (TDD)
Validation: MCP Chrome DevTools + Manual Testing
