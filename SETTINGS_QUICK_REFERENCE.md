# Settings Page - Quick Reference Card

## Page Load Sequence
```
1. Browser loads frontend/pages/settings.html
2. Base template loads (frontend/components/base.html)
3. HTMX v1.9.10 loads (CDN)
4. Alpine.js v3.x.x loads with defer (CDN)
5. Navigation rendered with theme switcher
6. Settings page content rendered
7. Global components.js loaded (themeSwitcher, samplePlayer, etc.)
8. Page-specific script block executes (settingsPage() defined)
9. Alpine.js initializes → finds x-data="settingsPage()"
10. settingsPage() factory called → init() runs
11. 3 API calls in parallel: preferences + models + usageData
12. Page becomes interactive after 200-300ms
```

## Alpine.js Component Tree
```
settingsPage()                              [MAIN COMPONENT @ Line 331]
├── State
│   ├── preferences {5 fields}              [Lines 334-341]
│   ├── models []                           [Line 342]
│   ├── usageData {}                        [Lines 343-346]
│   ├── loading, error, success             [Lines 347-350]
│   └── costValidationError                 [Line 350]
│
├── Initialization Methods
│   ├── init()                              [Line 353] → Promise.all(3 calls)
│   ├── loadPreferences()                   [Line 369] → GET /api/v1/preferences
│   ├── loadModels()                        [Line 392] → GET /api/v1/preferences/models
│   └── loadUsageData()                     [Line 408] → GET /api/v1/usage/public/summary
│
├── Event Handlers
│   ├── handleSaveResponse(event)           [Line 422] ← @htmx:after-request
│   ├── validateCostInput(event)            [Line 455] ← @input
│   ├── handleCostBlur(event)               [Line 485] ← @blur
│   └── resetToDefaults()                   [Line 494] ← @click
│
└── Computed Properties (Getters)
    ├── selectedVibeModel                   [Line 532] → Used in template L89-95
    ├── selectedBatchModel                  [Line 536] → Used in template L151-157
    └── batchCostEstimate                   [Line 540] → Used in template L190
```

## API Endpoints Map
```
GET /api/v1/preferences
├── Handler: get_preferences()              [preferences.py:41]
├── Called by: loadPreferences()            [settings.html:371]
├── Returns: JSON with current preferences
└── Auto-creates defaults if missing

GET /api/v1/preferences/models
├── Handler: get_available_models()        [preferences.py:138]
├── Called by: loadModels()                 [settings.html:394]
├── Returns: Array of available models with pricing
└── Populates dropdown options

PATCH /api/v1/preferences
├── Handler: update_preferences()           [preferences.py:72]
├── Called by: HTMX form elements
├── Accepts: JSON or form-encoded data
├── Validates: Pydantic UserPreferenceUpdate schema
└── Returns: 200 (success) or 422 (validation error)

GET /api/v1/usage/public/summary
├── Called by: loadUsageData()              [settings.html:410]
├── Non-critical: silently fails if unavailable
└── Default fallback: { total_cost: 0, call_count: 0 }
```

## HTMX Form Patterns
```
PATTERN 1: Checkbox with Auto-Save
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<input type="checkbox"
  x-model="preferences.auto_vibe_analysis"     ← Alpine binding
  hx-patch="/api/v1/preferences"               ← HTMX endpoint
  hx-vals='js:{...event.target.checked}'       ← Send checkbox value
  hx-swap="none"                               ← No DOM swap
  @htmx:after-request="handleSaveResponse()">  ← Handle response
</input>

PATTERN 2: Select Dropdown with Dynamic Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<select x-model="preferences.vibe_analysis_model"
  hx-patch="/api/v1/preferences"
  hx-trigger="change"
  @htmx:after-request="handleSaveResponse()">
  <template x-for="model in models">            ← Alpine x-for loop
    <option :value="model.model_id"             ← Dynamic binding
            x-text="model.name"></option>        ← Dynamic text
  </template>
</select>

PATTERN 3: Number Input with Validation + Save
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<input type="number"
  x-model="preferences.max_cost_per_request"
  @input="validateCostInput($event)"            ← Validate on keystroke
  @blur="handleCostBlur($event)"                ← Save on blur
  hx-patch="/api/v1/preferences"
  hx-trigger="cost-validated from:body"         ← Custom trigger
  @htmx:after-request="handleSaveResponse()">
</input>
```

## Validation Flow
```
USER TYPES IN COST INPUT
        ↓
@input fires validateCostInput()
        ↓
    ├─ Check: empty/null? → Clear error
    ├─ Check: NaN? → Set error "invalid number"
    ├─ Check: < 0? → Set error "negative"
    └─ Check: = 0? → Set error "must be > 0"
        ↓
costValidationError displayed in template
        ↓
USER LEAVES FIELD (@blur)
        ↓
handleCostBlur() called
        ↓
    ├─ If valid → htmx.trigger('cost-validated')
    │            → PATCH request sent
    │            → Backend validates again (security)
    │            → handleSaveResponse() shows result
    │
    └─ If invalid → No HTMX request
                   → Error message stays visible
```

## Data Flow: Single Setting Change
```
USER CLICKS CHECKBOX
           ↓
   Alpine x-model updates state immediately
           ↓
  HTMX detects element with hx-patch
           ↓
   PATCH /api/v1/preferences sent with value
           ↓
   Backend receives, validates, saves to DB
           ↓
   200 response returned with updated preferences
           ↓
   @htmx:after-request fires handleSaveResponse()
           ↓
   success = "Settings saved successfully"
           ↓
   Template shows green alert with message
           ↓
   After 3 seconds (setTimeout), message auto-clears
```

## State Management Pattern
```
OPTIMISTIC UI (No waiting for server)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. User clicks checkbox
2. x-model instantly updates preferences.auto_vibe_analysis
3. UI shows new value immediately (0ms latency)
4. HTMX sends PATCH request in background
5. If fails → handleSaveResponse() shows error
6. If succeeds → Server confirms, no UI change needed

BENEFIT: Instant responsive UI without waiting
RISK: False positive if server rejects (handled by error handler)
```

## Event Handler Responsibilities
```
handleSaveResponse($event)
├─ Check $event.detail.successful
├─ If true:
│  ├─ Show success alert
│  ├─ Clear error messages
│  └─ Auto-hide after 3 seconds
└─ If false:
   ├─ Check $event.detail.xhr.status
   ├─ If 422: Parse Pydantic error
   └─ Else: Show generic error

validateCostInput($event)
├─ Get $event.target.value
├─ Check: empty? null? NaN? negative? zero?
└─ Set costValidationError (shows in template immediately)

handleCostBlur($event)
├─ Call validateCostInput()
└─ If valid: htmx.trigger(event.target, 'cost-validated')

resetToDefaults()
├─ Confirm with user
├─ Set all preferences to defaults
└─ PATCH /api/v1/preferences with entire object
```

## Computed Properties Reference
```
selectedVibeModel
├─ Getter: finds model from this.models array
├─ Filters by: this.preferences.vibe_analysis_model
└─ Used to display pricing in template

selectedBatchModel
├─ Getter: finds model from this.models array
├─ Filters by: this.preferences.batch_processing_model
└─ Used to display pricing in template

batchCostEstimate
├─ Getter: calculates estimated cost
├─ Formula: (500 samples × 1000 tokens) × model.input_cost
└─ Used to show estimate in alert box
```

## Template Binding Reference
```
x-model          Two-way binding: input ↔ Alpine state
x-for            Loop: creates DOM for each array item
x-text           Set element text: reactive property binding
x-show           Toggle display: CSS display: none/block
x-transition     Animate show/hide with fade effect
:value           One-way binding: property → attribute
:key             List key for proper diffing
@htmx:after-request  HTMX event handler
@input           DOM input event
@blur            DOM blur event
@click           DOM click event
```

## Error Scenarios & Handling
```
API TIMEOUT (loadPreferences fails)
→ catch() sets this.error
→ throw error to init()
→ init() finally{} stops loading spinner
→ Page shows red alert: "Failed to load preferences"
→ User sees error on page load

VALIDATION ERROR (422 from PATCH)
→ xhr.status === 422
→ Parse JSON: errorData.detail
→ Set this.error = errorData.detail
→ Set this.costValidationError = this.error
→ Red alert shows validation details

NETWORK ERROR (no response)
→ catch() in loadUsageData() silently handles
→ usageData defaults to { total_cost: 0, call_count: 0 }
→ Page still loads, just shows zero usage

MALFORMED RESPONSE (invalid JSON)
→ JSON.parse() throws
→ catch() sets this.error = "Invalid input value"
→ User sees generic error message
```

## Key Implementation Details
```
WHY NO DOM UPDATES NEEDED? (hx-swap="none")
→ x-model already updated Alpine state
→ Template reactively reflects state changes
→ Server response only confirms save succeeded
→ No HTML needs to be swapped from server

WHY NOT USE HTMX FORM SUBMISSION?
→ Want optimistic UI (update before server response)
→ Want per-field save (each change = separate request)
→ Want full control of validation (client + server)
→ Want to show inline errors without page reload

WHY COMPUTED GETTERS?
→ Recalculate automatically when dependencies change
→ No need for watchers or explicit updates
→ React to model selection dropdown changes
→ Show pricing dynamically

WHY THREE PARALLEL API CALLS?
→ Independent data (preferences, models, usage)
→ Use Promise.all() for faster page load
→ All three fail independently
→ One failure doesn't prevent others
```

## Testing Checklist
```
LOAD PAGE
□ Loading spinner shows initially
□ 3 API calls made in parallel
□ Settings grid visible after ~200ms
□ All dropdowns populated with models
□ Cost usage stats show (or defaults)

CHANGE CHECKBOX
□ UI updates immediately
□ HTMX request sent
□ Success alert appears
□ Alert auto-hides after 3s

CHANGE DROPDOWN
□ UI updates immediately
□ Associated pricing displays
□ HTMX request sent on change (not on load)
□ Success message shows

CHANGE COST INPUT
□ Error shows immediately on invalid input
□ Error clears when fixed
□ Request sent only after blur (not on every keystroke)
□ Server validates (get 422 if rejected)

RESET BUTTON
□ Confirmation dialog appears
□ Cancel dismisses dialog
□ Confirm resets all settings
□ Bulk PATCH request sent
□ Success message shows
□ Page values reflect defaults
```

## File References Summary
```
Frontend
├── frontend/pages/settings.html          [Main page: 556 lines]
├── frontend/components/base.html         [Base template: 54 lines]
├── frontend/components/nav.html          [Navigation: 156 lines]
├── frontend/static/js/components.js      [Global Alpine: 361 lines]
└── frontend/static/js/filters.js         [HTMX utils]

Backend
├── backend/app/main.py                   [FastAPI app: 100 lines]
├── backend/app/api/v1/api.py             [Router aggregation: 19 lines]
├── backend/app/api/v1/endpoints/
│   ├── preferences.py                    [Preferences endpoints: 147 lines]
│   └── (other endpoints)
├── backend/app/services/
│   └── preferences_service.py            [Preferences logic: 267 lines]
├── backend/app/models/
│   └── user_preferences.py               [DB model: 40 lines]
└── backend/app/schemas/
    └── preferences.py                    [Pydantic schemas: 124 lines]

Database
└── sqlite:///sp404_samples.db
    └── user_preferences table            [Single row, id=1]
```

## Performance Profile
```
COLD PAGE LOAD
0ms     HTML parsing starts
10ms    HTMX script ready
50ms    Alpine.js script ready
60ms    Page script executes (settingsPage() defined)
70ms    Alpine.js initialization
77ms    init() runs 3 fetch() calls
150ms   API responses arrive
160ms   Template updates
200ms   Page fully interactive

INTERACTIONS
- Checkbox/select change: 50-100ms API round trip
- Cost input validation: 0ms (client-side)
- Cost input save: 50-100ms API round trip

MEMORY
- settingsPage() object: ~2KB
- models array: ~1KB (10-20 model entries)
- preferences object: ~500 bytes
- HTMX overhead: ~50KB (gzipped)
- Alpine.js overhead: ~30KB (gzipped)
```

---

**This card is autogenerated from SETTINGS_ARCHITECTURE_ANALYSIS.md**
**Keep synchronized when making page changes**

