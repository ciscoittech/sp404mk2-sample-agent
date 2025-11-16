# SP404MK2 Sample Agent - User Journey Testing & Validation

**Last Updated:** 2025-11-16
**Status:** Real Data, No Mocks, Live API Integration
**Testing Framework:** Playwright + MCP Chrome DevTools + CLI Validation

---

## Executive Summary

This document maps complete user journeys through the SP404MK2 Sample Agent system with comprehensive testing strategies. All testing uses:
- **Real database** (PostgreSQL with actual samples)
- **Real API calls** (OpenRouter for AI analysis)
- **Real files** (audio samples, embeddings)
- **No mock data** or stubs

Users interact with the system through three interfaces:
1. **Web Dashboard** (HTMX + Alpine.js, DaisyUI components)
2. **CLI Tools** (sp404_chat.py, download manager)
3. **API Endpoints** (FastAPI, async operations)

---

## System Architecture Overview

### Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interfaces (3)                         │
├─────────────────────────────────────────────────────────────────┤
│  Web UI               │  CLI Chat         │  Download Manager   │
│  (localhost:8100)     │  (sp404_chat.py)  │  (CLI commands)    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│              (localhost:8000 internal API)                      │
├─────────────────────────────────────────────────────────────────┤
│  Routes (8 groups) → Services (6) → Database Layer              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Data & Processing Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database │  Embedding Service │  Audio Processing   │
│  • samples           │  • OpenRouter      │  • librosa         │
│  • sample_embeddings │  • Vector storage  │  • Feature extract |
│  • downloads         │  • Similarity calc │  • BPM/Key detect  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Frontend**: HTMX (server-driven), Alpine.js (interactivity), DaisyUI
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **AI**: OpenRouter (Qwen models), text-embedding-3-small
- **Audio**: librosa, soundfile, essentia
- **Testing**: Playwright, pytest, MCP Chrome DevTools

---

## Core User Journeys (7 Total)

## Journey 1: Sample Collection Discovery & Analysis

**Goal**: Discover samples from YouTube videos and add to collection
**Entry Points**:
- Web: `/pages/dashboard.html` + `/pages/samples.html`
- CLI: `python sp404_chat.py`

### Journey Map

```
User Opens Dashboard
    ↓
Browse Recent Samples or Search
    ↓
Enter YouTube URL (Web UI or Chat)
    ↓
System Analyzes Video & Extracts Timestamps
    ↓
User Reviews Timestamps
    ↓
Download Sample or Batch Download
    ↓
System Converts to 48kHz/16-bit WAV
    ↓
Sample Added to Database
```

### Step-by-Step Expected Behavior

#### 1.1 Dashboard Load
**Action**: User navigates to `http://localhost:8100/pages/dashboard.html`

**Expected UI State**:
- Header with logo and nav links visible
- Sidebar shows: Dashboard, Samples, Vibe Search, Kits, Batch, Settings
- Main content shows:
  - Stats cards: Total Samples, Recent Downloads, Kits Created, Analysis Status
  - Recent activity section with latest 5 samples
  - Quick action buttons: Upload, New Kit, Start Batch

**Expected API Calls**: None (static HTML load)

**MCP Test**:
```javascript
test('dashboard loads with correct components', async ({ page }) => {
    await page.goto('http://localhost:8100/pages/dashboard.html');
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('.stats-grid')).toBeVisible();
    const statCards = page.locator('[data-testid="stat-card"]');
    await expect(statCards).toHaveCount(4);
});
```

**CLI Validation**: N/A (Web UI only)

---

#### 1.2 Browse Samples
**Action**: User clicks "Samples" in sidebar

**Expected Route**: `/pages/samples.html`

**Expected API Calls**:
- `GET /api/v1/samples?page=1&limit=20`

**Expected Response**:
```json
{
    "items": [
        {
            "id": 1,
            "title": "Dark Trap Loop",
            "duration_seconds": 4.5,
            "bpm": 140,
            "genre": "trap",
            "file_format": "wav",
            "file_size_bytes": 350000,
            "created_at": "2025-11-15T10:30:00",
            "has_embedding": true,
            "vibe_tags": ["dark", "moody", "atmospheric"]
        }
    ],
    "total": 2328,
    "pages": 117,
    "current_page": 1
}
```

**Expected UI**:
- Sample grid with cards showing:
  - Thumbnail placeholder (generic audio icon)
  - Title
  - BPM, genre, duration
  - Play button
  - Action buttons: Download, Use in Kit, Export, Delete
- Pagination controls at bottom
- Search/filter bar at top

**MCP Test**:
```javascript
test('samples page loads and displays sample grid', async ({ page }) => {
    await page.goto('http://localhost:8100/pages/samples.html');

    // Wait for API response
    const response = await page.waitForResponse(
        resp => resp.url().includes('/api/v1/samples')
    );
    const data = await response.json();

    // Validate response
    expect(data).toHaveProperty('items');
    expect(data).toHaveProperty('total');

    // Validate UI
    const cards = page.locator('[data-testid="sample-card"]');
    expect(await cards.count()).toBe(Math.min(20, data.items.length));
});
```

**CLI Validation**: N/A

---

#### 1.3 YouTube Analysis (Web UI)
**Action**: User enters YouTube URL in search bar or dedicated form

**Expected Form**:
- Text input field
- Analyze button
- Optional: Batch download checkbox

**Input**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

**Expected API Call**: `POST /api/v1/public/analyze-youtube`
```json
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "max_timestamps": 20
}
```

**Expected Response**:
```json
{
    "success": true,
    "video_info": {
        "title": "Sample Pack Name",
        "channel": "Producer Channel",
        "duration_seconds": 600,
        "thumbnail_url": "https://...",
        "upload_date": "2025-11-01"
    },
    "timestamp_count": 12,
    "timestamps": [
        {
            "time_seconds": 15,
            "duration_seconds": 4.5,
            "description": "Kick drum break",
            "confidence": 0.95,
            "suggested_type": "drum_sample"
        },
        {
            "time_seconds": 30,
            "duration_seconds": 8.0,
            "description": "Snare roll pattern",
            "confidence": 0.88,
            "suggested_type": "drum_sample"
        }
    ],
    "analysis_time_seconds": 2.3
}
```

**Expected UI**:
- Form submission state changes
- Loading spinner appears
- Video preview shows
- Timestamps populate in table with columns:
  - Time (0:15)
  - Duration (4.5s)
  - Description
  - Type badge (drum_sample, melody, effect)
  - Download checkbox

**Error Handling**:
- Invalid URL → "Invalid YouTube URL format"
- Video not found → "Unable to access video"
- Analysis failed → "Could not analyze video. Try again."

**MCP Test**:
```javascript
test('youtube analysis extracts timestamps correctly', async ({ page }) => {
    await page.goto('http://localhost:8100/pages/samples.html');

    // Fill and submit form
    const youtubeInput = page.locator('input[name="youtube_url"]');
    await youtubeInput.fill('https://www.youtube.com/watch?v=...');

    // Wait for API response
    const responsePromise = page.waitForResponse(
        resp => resp.url().includes('/analyze-youtube')
    );
    await page.click('button[type="submit"]');
    const response = await responsePromise;

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.timestamps.length).toBeGreaterThan(0);
    expect(data.timestamps[0]).toHaveProperty('time_seconds');
    expect(data.timestamps[0]).toHaveProperty('description');

    // Verify UI updates
    await page.waitForSelector('table tbody tr');
    const rows = page.locator('table tbody tr');
    expect(await rows.count()).toBe(data.timestamp_count);
});
```

**CLI Validation**: N/A (Web only in this step)

---

#### 1.4 YouTube Analysis (CLI Chat)
**Action**: User runs `python sp404_chat.py` and enters YouTube URL

**CLI Session**:
```
$ python sp404_chat.py

🎵 SP-404MK2 Sample Agent

You: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Agent: Analyzing YouTube video for sample opportunities...

Video Information:
  • Title: Sample Pack Name
  • Channel: Producer Channel
  • Duration: 10 minutes

Sample Timestamps Found (12):

┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Time   ┃ Duration ┃ Description      ┃ Type     ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 0:15   │ 4.5s     │ Kick drum break  │ drum     │
│ 0:30   │ 8.0s     │ Snare roll       │ drum     │
│ 1:05   │ 6.2s     │ Bass line        │ bass     │
└────────┴──────────┴──────────────────┴──────────┘

Would you like to:
1. Download selected samples
2. Review timestamps in more detail
3. Analyze another video

You: 1
```

**Expected Output Validation**:
- Table uses Rich library formatting
- All timestamps displayed
- Each timestamp has time, duration, description, type
- User options presented clearly

**CLI Test**:
```python
def test_youtube_analysis_cli_output():
    output = validate_cli_output(
        command=['python', 'sp404_chat.py'],
        user_input='https://www.youtube.com/watch?v=dQw4w9WgXcQ\n1\n',
        expected_patterns=[
            r'Analyzing YouTube video',
            r'Video Information:',
            r'Sample Timestamps Found \(\d+\)',
            r'┏━+┳',  # Rich table border
            r'Time.*Duration.*Description.*Type',
            r'Would you like to:'
        ]
    )
    assert result['all_patterns_matched']
```

---

#### 1.5 Download Samples
**Action**: User selects timestamps and clicks "Download"

**Expected API Call**: `POST /api/v1/downloads`
```json
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "timestamps": [
        {
            "start_seconds": 15,
            "end_seconds": 19.5,
            "title": "Kick drum break"
        },
        {
            "start_seconds": 30,
            "end_seconds": 38,
            "title": "Snare roll pattern"
        }
    ]
}
```

**Expected Response**:
```json
{
    "download_ids": [123, 124],
    "status": "processing",
    "estimated_time_seconds": 30
}
```

**Expected Behavior**:
- Submit button disabled
- Loading spinner shows
- Progress message: "Downloading 2 samples..."
- After completion: "Successfully downloaded 2 samples"
- New samples appear in samples grid

**UI State Transitions**:
- Initial: Button enabled, text "Download"
- Submitting: Button disabled, text "Downloading...", spinner
- Success: Button enabled, text "Download", success message
- Error: Button enabled, text "Download", error message

**MCP Test**:
```javascript
test('download samples initiates batch conversion', async ({ page }) => {
    // Assume we're on analysis page with timestamps loaded

    // Select first two timestamps
    await page.check('[data-timestamp="0"]');
    await page.check('[data-timestamp="1"]');

    // Click download
    const responsePromise = page.waitForResponse(
        resp => resp.url().includes('/api/v1/downloads') && resp.request().method() === 'POST'
    );
    await page.click('button:has-text("Download")');

    const response = await responsePromise;
    const data = await response.json();

    expect(data.status).toBe('processing');
    expect(data.download_ids).toHaveLength(2);

    // Verify UI updates
    await expect(page.locator('.success-message')).toBeVisible();
});
```

---

#### 1.6 Sample Added to Database
**Action**: System completes download conversion

**Expected Database State**:
- New rows in `samples` table:
```sql
SELECT id, title, duration_seconds, bpm, genre, file_path
FROM samples
WHERE created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC LIMIT 2;
```

Expected result:
```
id  title              duration  bpm  genre  file_path
124 Kick drum break    4.5       140  trap   /samples/124.wav
125 Snare roll pattern 8.0       140  trap   /samples/125.wav
```

**File System Check**:
```bash
ls -lh /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/samples/124.wav
# Should be ~350KB
# Format check: file 124.wav
# Should output: RIFF (little-endian) data, WAVE audio
```

**Backend Log Check**:
```
[2025-11-16 10:00:00] Downloading sample: Kick drum break
[2025-11-16 10:00:02] Downloaded: 350KB in 1.2s
[2025-11-16 10:00:03] Converting to 48kHz/16-bit
[2025-11-16 10:00:04] Analyzing audio features (BPM: 140, Key: D)
[2025-11-16 10:00:05] Processing complete
```

**Validation**:
- File exists and readable
- File format is WAV
- Audio parameters: 48kHz, 16-bit, mono/stereo
- Duration matches expected
- BPM/key detected correctly
- Database record created with correct metadata

---

## Journey 2: Vibe Search (Semantic Sample Discovery)

**Goal**: Find samples using natural language descriptions
**Entry Points**: `/pages/vibe-search.html`
**Critical Requirement**: Samples MUST have embeddings in `sample_embeddings` table

### Pre-Flight Check: Embedding Availability

**Before Any Vibe Search Testing**:

```python
# Run this query
SELECT
    COUNT(DISTINCT s.id) as total_samples,
    COUNT(DISTINCT se.sample_id) as embedded_samples,
    ROUND(100.0 * COUNT(DISTINCT se.sample_id) / COUNT(DISTINCT s.id), 1) as coverage_pct
FROM samples s
LEFT JOIN sample_embeddings se ON s.id = se.sample_id;
```

**Expected Result**:
```
total_samples | embedded_samples | coverage_pct
2328          | 1800+            | 77%+
```

**Handling Insufficient Embeddings**:

If `coverage_pct < 30`:
1. **CLI Alert User**:
   ```
   ⚠️  VIBE SEARCH REQUIRES EMBEDDINGS

   Only 15% of samples have embeddings (350/2328)

   Generate embeddings:
   ./venv/bin/python backend/scripts/generate_embeddings.py --resume

   Expected time: ~2 hours
   ```

2. **Web UI Banner**:
   ```html
   <div class="alert alert-warning">
       <div class="alert-title">Limited Search Results</div>
       <p>Only 15% of samples have embeddings for vibe search.
          Generating embeddings now...</p>
       <div class="progress">
           <div class="progress-bar" style="width: 15%"></div>
       </div>
       <p>Progress: 350/2328 samples</p>
   </div>
   ```

3. **Wait/Retry Logic**:
   ```python
   async def wait_for_embeddings(
       db: AsyncSession,
       min_samples: int = 30,
       timeout_seconds: int = 300  # 5 minutes
   ) -> bool:
       """Wait for embeddings with retry logic."""
       start = time.time()

       while time.time() - start < timeout_seconds:
           query = select(func.count(SampleEmbedding.sample_id))
           result = await db.execute(query)
           count = result.scalar()

           if count >= min_samples:
               return True

           await asyncio.sleep(5)  # Check every 5 seconds
           logger.info(f"Waiting for embeddings: {count}/{min_samples}")

       # Timeout - alert user
       logger.warning(f"Timeout waiting for embeddings after {timeout_seconds}s")
       return False
   ```

### Journey Map

```
User Opens Vibe Search
    ↓
Check Embedding Availability
    ├─ If < 30: Show warning, wait/retry, or disable
    └─ If >= 30: Continue
    ↓
Enter Natural Language Query
    ↓
Submit Search (GET /api/v1/search/vibe)
    ↓
System Generates Query Embedding
    ↓
Calculate Similarity to Sample Embeddings
    ↓
Return Top 20 Results Sorted by Similarity
    ↓
User Reviews Results with Filters
    ↓
Apply Filters (BPM, Genre, Energy, etc.)
    ↓
Re-submit with Filter Parameters
    ↓
Updated Results Display
```

### Step-by-Step Expected Behavior

#### 2.1 Open Vibe Search Page
**Action**: User navigates to `/pages/vibe-search.html`

**Expected UI Components**:
- Hero section with title "Vibe Search"
- Tagline: "Describe the vibe you want. We'll find it."
- Large search textarea
- Search button (centered)
- Example queries as clickable pills:
  - "Dark moody trap with heavy bass"
  - "Bright uplifting electronic synths"
  - "Vintage jazz drums from the 70s"
- Collapsed advanced filters section
- Empty state message: "Start typing to search..."

**MCP Test**:
```javascript
test('vibe search page loads with correct components', async ({ page }) => {
    await page.goto('http://localhost:8100/pages/vibe-search.html');

    // Check components
    await expect(page.locator('h1')).toContainText('Vibe Search');
    await expect(page.locator('textarea[name="query"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Check example pills exist
    const pills = page.locator('[data-testid="example-pill"]');
    expect(await pills.count()).toBeGreaterThan(0);

    // Verify filters collapsed
    const filters = page.locator('[data-testid="filters-section"]');
    expect(await filters.evaluate(el =>
        getComputedStyle(el).display === 'none' ? true : false
    )).toBe(true);
});
```

#### 2.2 Execute Vibe Search
**Action**: User types "dark moody trap loops with heavy bass" and clicks search

**Expected API Call**: `GET /api/v1/search/vibe?query=dark moody trap loops with heavy bass&limit=20`

**Backend Processing**:
1. Generate embedding for query (OpenRouter)
2. Calculate cosine similarity to all sample embeddings
3. Return top 20 by similarity
4. Include metadata for each result

**Expected Response** (2000ms max):
```json
{
    "query": "dark moody trap loops with heavy bass",
    "embedding_model": "text-embedding-3-small",
    "results": [
        {
            "id": 45,
            "title": "Dark Trap Loop 808",
            "similarity": 0.92,
            "bpm": 140,
            "genre": "trap",
            "duration_seconds": 4.5,
            "vibe_tags": ["moody", "dark", "atmospheric", "bass"],
            "mood_primary": "dark",
            "energy_level": 0.85,
            "file_size_bytes": 350000,
            "preview_url": "/api/v1/samples/45/preview"
        },
        {
            "id": 67,
            "title": "Heavy 808 Sub",
            "similarity": 0.88,
            "bpm": 140,
            "genre": "trap",
            "duration_seconds": 3.2,
            "vibe_tags": ["bass-heavy", "dark", "moody"],
            "mood_primary": "dark",
            "energy_level": 0.80,
            "file_size_bytes": 245000,
            "preview_url": "/api/v1/samples/67/preview"
        }
    ],
    "total_results": 15,
    "execution_time_ms": 1250
}
```

**Expected UI Updates**:
- Results grid populates with cards
- Stats bar appears: "Found 15 results in 1.25s"
- Each card shows:
  - Similarity score as percentage (92%)
  - Title
  - BPM and genre badges
  - Mood tags
  - Play button for preview
  - Action buttons: Use in Kit, Download, Export
- Sort options appear: Similarity, BPM, Genre

**MCP Test**:
```javascript
test('vibe search returns semantically similar samples', async ({ page }) => {
    // Check embedding availability first
    const statusResp = await page.request.get('/api/v1/search/status');
    const status = await statusResp.json();
    if (!status.ready) {
        test.skip('Insufficient embeddings');
    }

    await page.goto('http://localhost:8100/pages/vibe-search.html');

    // Submit search
    await page.fill('textarea[name="query"]', 'dark moody trap loops with heavy bass');
    const respPromise = page.waitForResponse(
        resp => resp.url().includes('/search/vibe')
    );
    await page.click('button[type="submit"]');

    const response = await respPromise;
    const data = await response.json();

    // Validate response structure
    expect(data).toHaveProperty('results');
    expect(data).toHaveProperty('total_results');
    expect(data).toHaveProperty('execution_time_ms');

    // Validate results
    expect(data.results.length).toBeGreaterThan(0);
    expect(data.results.length).toBeLessThanOrEqual(20);

    // Check similarity scores are descending
    for (let i = 0; i < data.results.length - 1; i++) {
        expect(data.results[i].similarity).toBeGreaterThanOrEqual(
            data.results[i + 1].similarity
        );
    }

    // Verify UI populated
    await page.waitForSelector('[data-testid="result-card"]');
    const cards = page.locator('[data-testid="result-card"]');
    expect(await cards.count()).toBe(data.results.length);

    // Check stats bar
    await expect(page.locator('[data-testid="result-count"]'))
        .toContainText(data.total_results.toString());
});
```

#### 2.3 Apply Filters
**Action**: User expands filters and sets BPM 130-150, energy 0.7-1.0

**Filter Options**:
- BPM Range (slider: 60-200)
- Genre (checkboxes: trap, hip-hop, jazz, electronic, etc.)
- Energy Level (slider: 0.0-1.0)
- Duration (slider: 0-30 seconds)
- Mood (checkboxes: dark, bright, energetic, calm, etc.)

**Expected API Call**: `GET /api/v1/search/vibe?query=...&bpm_min=130&bpm_max=150&energy_min=0.7&energy_max=1.0&limit=20`

**Expected Behavior**:
- Results update via HTMX
- Filtered results show only matching samples
- If no results: "No samples match these filters. Try adjusting."

**MCP Test**:
```javascript
test('filters update search results correctly', async ({ page }) => {
    // Execute initial search (from previous test)

    // Expand filters
    await page.click('[data-testid="filters-toggle"]');

    // Set BPM range
    await page.fill('input[name="bpm_min"]', '130');
    await page.fill('input[name="bpm_max"]', '150');

    // Wait for HTMX update
    const updatePromise = page.waitForResponse(
        resp => resp.url().includes('bpm_min=130')
    );
    await page.click('button[name="apply-filters"]');

    await updatePromise;

    // Verify all results have BPM in range
    const cards = page.locator('[data-testid="result-card"]');
    const count = await cards.count();

    for (let i = 0; i < count; i++) {
        const bpmText = await cards.nth(i)
            .locator('[data-testid="bpm"]')
            .textContent();
        const bpm = parseInt(bpmText.match(/\d+/)[0]);
        expect(bpm).toBeGreaterThanOrEqual(130);
        expect(bpm).toBeLessThanOrEqual(150);
    }
});
```

#### 2.4 Play Sample Preview
**Action**: User clicks play button on first result

**Expected Behavior**:
- Audio player loads
- Play/pause controls appear
- Duration bar shows
- Current time updates as playing

**URL Format**: `/api/v1/samples/{sample_id}/preview` (3-5 second clip)

**MCP Test**:
```javascript
test('audio preview loads and plays', async ({ page }) => {
    // Execute search and get first result

    // Click play button on first result
    const firstCard = page.locator('[data-testid="result-card"]').first();
    await firstCard.click('button[data-testid="play"]');

    // Wait for audio player
    await expect(page.locator('audio')).toBeVisible();

    // Verify audio element
    const audio = page.locator('audio');
    const src = await audio.getAttribute('src');
    expect(src).toContain('/api/v1/samples');
    expect(src).toContain('preview');

    // Verify it plays
    await page.evaluate(() => {
        document.querySelector('audio').play();
    });

    const duration = await page.evaluate(() => {
        return document.querySelector('audio').duration;
    });
    expect(duration).toBeGreaterThan(0);
});
```

---

## Journey 3: Kit Building & Pad Assignment

**Goal**: Assemble SP-404MK2 compatible kits with semantic recommendations
**Entry Points**: `/pages/kits.html`
**Database**: `kits`, `kit_assignments` tables

### Journey Map

```
User Creates New Kit
    ↓
Assigns Samples to 16 Pads (4x4 Grid)
    ├─ Manual: Browse and select
    ├─ Semantic: "Find kick for pad 13"
    └─ Auto: AI recommends based on kit theme
    ↓
Configure Per-Pad Settings (volume, pitch)
    ↓
Export Kit as ZIP
    ↓
Transfer to SP-404MK2 SD Card
```

### Step-by-Step Expected Behavior

#### 3.1 Create New Kit
**Action**: User clicks "New Kit" button on kits page

**Expected Modal**:
- Title input: "Kit Name" placeholder
- Description textarea
- Genre selector (optional)
- BPM input (optional)
- Create button

**Expected API Call**: `POST /api/v1/kits`
```json
{
    "name": "My Hip Hop Kit",
    "description": "Boom bap drums with retro samples",
    "genre": "hip-hop",
    "bpm": 90
}
```

**Expected Response**:
```json
{
    "id": 5,
    "name": "My Hip Hop Kit",
    "description": "Boom bap drums with retro samples",
    "genre": "hip-hop",
    "bpm": 90,
    "user_id": 1,
    "assignments": [],
    "created_at": "2025-11-16T10:00:00",
    "sp404_compatible": true
}
```

**Expected Database Insert**:
```sql
INSERT INTO kits (name, description, genre, bpm, user_id)
VALUES ('My Hip Hop Kit', 'Boom bap drums...', 'hip-hop', 90, 1);
```

**MCP Test**:
```javascript
test('create new kit shows 4x4 pad grid', async ({ page }) => {
    await page.goto('http://localhost:8100/pages/kits.html');

    // Click new kit
    await page.click('button:has-text("New Kit")');
    await expect(page.locator('dialog')).toBeVisible();

    // Fill form
    await page.fill('input[name="name"]', 'My Hip Hop Kit');
    await page.fill('textarea[name="description"]', 'Boom bap drums...');

    // Submit
    const createPromise = page.waitForResponse(
        resp => resp.url().includes('/api/v1/kits') && resp.request().method() === 'POST'
    );
    await page.click('dialog button[type="submit"]');

    const response = await createPromise;
    const data = await response.json();
    expect(data.id).toBeDefined();

    // Verify kit page loads
    await page.waitForURL(/.*kits\/\d+/);

    // Verify 4x4 grid
    const pads = page.locator('[data-testid="pad"]');
    expect(await pads.count()).toBe(16);
});
```

#### 3.2 View Kit Pad Grid
**Action**: User views newly created kit

**Expected UI**:
- Kit name displayed as header
- Description shown
- Stats: 0/16 pads assigned, genre, BPM
- 4x4 pad grid with labels:
  - Rows: Loops, Textures, Accents, Heart
  - Columns: 1, 2, 3, 4
- Each pad shows either:
  - "Empty" + "Assign" button (empty state)
  - Sample title + "Remove" button (filled state)

**Layout Example**:
```
╔═══════════════════════════════╗
║ My Hip Hop Kit (0/16 filled)  ║
╚═══════════════════════════════╝

LOOPS    │ TEXTURES  │ ACCENTS   │ HEART
────────┼───────────┼───────────┼────────
Empty   │ Empty     │ Empty     │ Empty
Assign  │ Assign    │ Assign    │ Assign
────────┼───────────┼───────────┼────────
Empty   │ Empty     │ Empty     │ Empty
Assign  │ Assign    │ Assign    │ Assign
```

**MCP Test**:
```javascript
test('kit pad grid displays with 16 empty pads', async ({ page }) => {
    // Assume we're on newly created kit page

    // Verify grid exists
    const grid = page.locator('[data-testid="pad-grid"]');
    await expect(grid).toBeVisible();

    // Verify pad count
    const pads = grid.locator('[data-testid="pad"]');
    expect(await pads.count()).toBe(16);

    // Verify all empty
    const emptyPads = grid.locator('[data-testid="pad-empty"]');
    expect(await emptyPads.count()).toBe(16);

    // Verify labels
    const rowLabels = grid.locator('[data-testid="row-label"]');
    const expectedLabels = ['Loops', 'Textures', 'Accents', 'Heart'];
    for (let i = 0; i < 4; i++) {
        await expect(rowLabels.nth(i)).toContainText(expectedLabels[i]);
    }
});
```

#### 3.3 Get Pad Recommendations
**Action**: User clicks on empty pad #13 (usually kick pad) to assign a sample

**Expected Modal**:
- Pad label shown: "Pad 13 - Kick (Heart Row)"
- AI input: "Describe the kick you want"
- AI button: "Get Recommendations"
- OR browse button: "Browse Samples"

**User Action**: Clicks "Get Recommendations" and enters "punchy 808 kick"

**Expected API Call**: `GET /api/v1/kits/{kit_id}/recommendations?pad=13&query=punchy 808 kick&limit=20`

**Backend Processing**:
1. Query vibe search for "punchy 808 kick"
2. Filter by typical kick parameters (short duration, low frequency)
3. Rank by relevance to pad type
4. Return top 20 recommendations with reasons

**Expected Response**:
```json
{
    "kit_id": 5,
    "pad": 13,
    "pad_name": "Kick (Heart Row)",
    "query": "punchy 808 kick",
    "recommendations": [
        {
            "sample_id": 45,
            "title": "Punchy 808 Kick",
            "similarity": 0.95,
            "bpm": 140,
            "genre": "trap",
            "duration_seconds": 0.5,
            "recommendation_reason": "High similarity to query. Punchy attack, 808 character."
        },
        {
            "sample_id": 67,
            "title": "Sub Kick Low",
            "similarity": 0.88,
            "bpm": 140,
            "genre": "trap",
            "duration_seconds": 0.6,
            "recommendation_reason": "Deep sub character matches '808' keyword."
        }
    ],
    "total": 20
}
```

**MCP Test**:
```javascript
test('pad recommendations use vibe search', async ({ page }) => {
    // Assume we're on kit page with empty pad

    // Click on empty pad
    const pad13 = page.locator('[data-testid="pad"][data-pad-id="13"]');
    await pad13.click();

    // Modal opens
    await expect(page.locator('dialog')).toBeVisible();

    // Enter recommendation query
    const aiInput = page.locator('textarea[placeholder*="Describe"]');
    await aiInput.fill('punchy 808 kick');

    // Get recommendations
    const respPromise = page.waitForResponse(
        resp => resp.url().includes('/recommendations')
    );
    await page.click('button:has-text("Get Recommendations")');

    const response = await respPromise;
    const data = await response.json();

    // Validate response
    expect(data.recommendations.length).toBeGreaterThan(0);
    expect(data.recommendations[0]).toHaveProperty('sample_id');
    expect(data.recommendations[0]).toHaveProperty('recommendation_reason');

    // Verify UI displays recommendations
    const items = page.locator('dialog li');
    expect(await items.count()).toBe(data.recommendations.length);
});
```

#### 3.4 Assign Sample to Pad
**Action**: User clicks "Assign" on a recommended sample

**Expected API Call**: `POST /api/v1/kits/{kit_id}/assignments`
```json
{
    "sample_id": 45,
    "pad": 13,
    "volume": 1.0,
    "pitch_shift": 0
}
```

**Expected Database Insert**:
```sql
INSERT INTO kit_assignments (kit_id, sample_id, pad, volume, pitch_shift)
VALUES (5, 45, 13, 1.0, 0);
```

**Expected Response**:
```json
{
    "success": true,
    "assignment_id": 123,
    "kit_id": 5,
    "pad": 13,
    "sample_id": 45,
    "sample_title": "Punchy 808 Kick",
    "position": "13/16"
}
```

**Expected UI**:
- Modal closes
- Pad 13 updates to show "Punchy 808 Kick"
- Remove button appears on pad
- Stats update: "1/16 pads assigned"
- Optional: Show "Add snare to pad 14?" or next recommendation

**MCP Test**:
```javascript
test('assign sample to pad updates grid', async ({ page }) => {
    // Recommendations modal is open with results

    // Click assign on first recommendation
    const firstAssignBtn = page.locator('dialog')
        .locator('[data-testid="assign-btn"]')
        .first();

    const assignPromise = page.waitForResponse(
        resp => resp.url().includes('/assignments') && resp.request().method() === 'POST'
    );
    await firstAssignBtn.click();

    const response = await assignPromise;
    const data = await response.json();
    expect(data.success).toBe(true);

    // Modal closes
    await expect(page.locator('dialog')).not.toBeVisible();

    // Pad updates
    const pad13 = page.locator('[data-testid="pad"][data-pad-id="13"]');
    await expect(pad13).toContainText(data.sample_title);

    // Stats update
    await expect(page.locator('[data-testid="pad-count"]'))
        .toContainText('1/16');
});
```

#### 3.5 Export Kit as ZIP
**Action**: User clicks "Export" button when kit is filled

**Expected Export Options Modal**:
- Format: WAV (48kHz/16-bit) or AIFF
- Organization:
  - Flat (all in root)
  - By genre (samples in genre folders)
  - By BPM range
  - By kit theme
- Download button

**Expected API Call**: `POST /api/v1/kits/{kit_id}/export`
```json
{
    "format": "wav",
    "organize_by": "flat"
}
```

**Expected Response**:
```json
{
    "success": true,
    "export_id": 456,
    "kit_id": 5,
    "format": "wav",
    "file_count": 16,
    "total_size_bytes": 5600000,
    "download_url": "/api/v1/exports/456/download"
}
```

**ZIP Contents**:
```
My Hip Hop Kit.zip
├── pad_assignments.txt
│   01_Kick.wav
│   02_Kick Variation.wav
│   ...
│   16_Cymbal.wav
└── README.txt (SP-404MK2 transfer instructions)
```

**Backend Processing**:
1. Collect 16 samples from kit assignments
2. Convert each to 48kHz/16-bit WAV (if not already)
3. Sanitize filenames for SP-404 compatibility
4. Create pad mapping file (for manual assignment reference)
5. ZIP everything
6. Store in `/exports/{export_id}/`

**MCP Test**:
```javascript
test('export kit creates downloadable zip', async ({ page }) => {
    // Assume kit has 16 pads assigned

    // Click export
    await page.click('button:has-text("Export")');

    // Options modal appears
    await expect(page.locator('dialog')).toBeVisible();

    // Select options and submit
    await page.selectOption('[name="format"]', 'wav');
    await page.selectOption('[name="organize_by"]', 'flat');

    // Intercept download
    const downloadPromise = page.context().waitForEvent('download');
    const exportPromise = page.waitForResponse(
        resp => resp.url().includes('/export')
    );

    await page.click('dialog button[type="submit"]');

    const response = await exportPromise;
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.file_count).toBe(16);

    // Verify download starts
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.zip');
});
```

---

## Journey 4: Batch Processing & Automation

**Goal**: Process large collections of samples automatically
**Entry Points**: `/pages/batch.html`, CLI scripts
**Technology**: Queue-based processing with lock file safety

### Journey Map

```
User Configures Batch Job
    ├─ Directory path
    ├─ Batch size (5, 10, 20)
    ├─ Analysis depth (basic, full, vibe-search)
    └─ Auto-import option
    ↓
Submit Batch Configuration
    ↓
System Creates Queue Entry
    ↓
Web UI Shows Job Status
    ↓
Monitor Progress (Real-time Updates)
    ├─ Files processed
    ├─ Current file
    ├─ Estimated time remaining
    └─ Any errors
    ↓
Job Completes
    ↓
Import Results into Database
    ↓
Generate Embeddings (if vibe-search enabled)
    ↓
Samples Available for Vibe Search
```

### Step-by-Step Expected Behavior

#### 4.1 Configure & Submit Batch Job (Web UI)
**Action**: User navigates to `/pages/batch.html` and fills form

**Expected Form**:
```html
<form>
  <input type="text"
         name="collection_path"
         placeholder="/path/to/samples" required>

  <select name="batch_size">
    <option value="5">5 files at a time</option>
    <option value="10" selected>10 files at a time</option>
    <option value="20">20 files at a time</option>
  </select>

  <fieldset>
    <legend>Analysis Options</legend>
    <checkbox name="analyze_audio">Audio Features (BPM, Key)</checkbox>
    <checkbox name="analyze_vibe" checked>Vibe Analysis (AI)</checkbox>
    <checkbox name="generate_embeddings" checked>Generate Embeddings</checkbox>
  </fieldset>

  <checkbox name="auto_import" checked>
    Auto-import results when complete
  </checkbox>

  <button type="submit">Start Batch</button>
</form>
```

**User Input**:
- Collection path: `/Volumes/Crate_vol5/`
- Batch size: 10
- All analysis options checked
- Auto-import checked

**Expected API Call**: `POST /api/v1/batch`
```json
{
    "collection_path": "/Volumes/Crate_vol5/",
    "batch_size": 10,
    "analyze_audio": true,
    "analyze_vibe": true,
    "generate_embeddings": true,
    "auto_import": true
}
```

**Backend Processing**:
1. Scan directory for `.wav`, `.mp3`, `.flac` files
2. Create batch entries in queue
3. Save job configuration
4. Return batch job ID

**Expected Response**:
```json
{
    "batch_id": "batch_20251116_103000",
    "status": "created",
    "total_files": 250,
    "batch_count": 25,
    "estimated_duration_minutes": 180,
    "first_batch_start_time": "2025-11-16T10:30:10"
}
```

**MCP Test**:
```javascript
test('batch submission creates processing job', async ({ page }) => {
    await page.goto('http://localhost:8100/pages/batch.html');

    // Fill form
    await page.fill('[name="collection_path"]', '/Volumes/Crate_vol5/');
    await page.selectOption('[name="batch_size"]', '10');
    await page.check('[name="analyze_vibe"]');
    await page.check('[name="generate_embeddings"]');

    // Submit
    const respPromise = page.waitForResponse(
        resp => resp.url().includes('/api/v1/batch') && resp.request().method() === 'POST'
    );
    await page.click('button[type="submit"]');

    const response = await respPromise;
    const data = await response.json();

    expect(data.batch_id).toBeDefined();
    expect(data.status).toBe('created');
    expect(data.total_files).toBeGreaterThan(0);

    // Verify success message
    await expect(page.locator('.success-message'))
        .toContainText(`Batch ${data.batch_id} created`);
});
```

#### 4.2 Monitor Batch Progress (Web UI)
**Action**: User watches batch processing status in real-time

**Expected Polling**: `GET /api/v1/batch/{batch_id}/status` every 2 seconds

**Expected Response** (in progress):
```json
{
    "batch_id": "batch_20251116_103000",
    "status": "processing",
    "total_files": 250,
    "processed_files": 45,
    "current_file": "sample_045.wav",
    "current_file_status": "analyzing_vibe",
    "progress_pct": 18,
    "errors": 0,
    "estimated_time_remaining_minutes": 155,
    "start_time": "2025-11-16T10:30:10",
    "current_time": "2025-11-16T10:35:20",
    "elapsed_minutes": 5
}
```

**Expected UI**:
- Progress bar: 18% filled
- Stats: "45/250 files processed (5 mins elapsed, ~155 mins remaining)"
- Current file: "sample_045.wav - analyzing_vibe..."
- Batch history showing recent 5 batches
- Stop button (if batch can be paused)

**MCP Test**:
```javascript
test('batch progress updates in real-time', async ({ page }) => {
    // Assume batch is running

    await page.goto('http://localhost:8100/pages/batch.html');

    // Wait for progress element
    await page.waitForSelector('[data-testid="progress-bar"]');

    // Monitor progress updates
    const progressBar = page.locator('[data-testid="progress-bar"]');
    const initialPercent = await progressBar.getAttribute('style');

    // Wait for update
    await page.waitForTimeout(2500);

    // Trigger refresh (HTMX or manual)
    await page.reload();

    // Check that percentage changed
    const updatedPercent = await progressBar.getAttribute('style');
    expect(updatedPercent).not.toBe(initialPercent);

    // Verify stats display
    const stats = page.locator('[data-testid="batch-stats"]');
    await expect(stats).toContainText(/\d+\/250 files/);
});
```

#### 4.3 Job Completion & Embedding Generation
**Action**: Batch job completes and embeddings are generated

**Expected Database State After Batch**:
```sql
SELECT COUNT(*) FROM samples WHERE created_at > (NOW() - INTERVAL '3 hours');
-- Should show 250 new samples

SELECT COUNT(*) FROM sample_embeddings
WHERE sample_id IN (
    SELECT id FROM samples WHERE created_at > (NOW() - INTERVAL '3 hours')
);
-- Should show 250 (if generate_embeddings was true)
```

**Expected API Call** (final status):
```json
{
    "batch_id": "batch_20251116_103000",
    "status": "completed",
    "total_files": 250,
    "processed_files": 250,
    "successful_imports": 250,
    "failed_imports": 0,
    "embeddings_generated": 250,
    "embeddings_failed": 0,
    "completion_time": "2025-11-16T13:30:20",
    "total_duration_minutes": 180
}
```

**Expected UI**:
- Batch card changes to green "Completed"
- Stats update: "250/250 files processed, 250 embeddings generated"
- New section: "Samples added to library"
- Vibe Search now available with 250 new samples

**MCP Test**:
```javascript
test('completed batch generates embeddings', async ({ page }) => {
    // Monitor batch until completion
    let completed = false;
    let attempts = 0;

    while (!completed && attempts < 180) { // 3-hour timeout
        const response = await page.request.get(`/api/v1/batch/batch_20251116_103000/status`);
        const data = await response.json();

        if (data.status === 'completed') {
            completed = true;

            // Validate completion
            expect(data.processed_files).toBe(data.total_files);
            expect(data.embeddings_generated).toBe(250);
            expect(data.embeddings_failed).toBe(0);
        }

        await page.waitForTimeout(30000); // Check every 30 seconds
        attempts++;
    }

    expect(completed).toBe(true);
});
```

#### 4.4 Automated Batch Processing (CLI)
**Action**: User runs automation script via cron or manually

**Command**:
```bash
./scripts/batch_automation/automated_batch_runner.sh
```

**Expected Behavior**:

1. **Lock File Check**:
   ```bash
   if [ -f .lock ]; then
       echo "Batch processing already running"
       exit 1
   fi
   ```

2. **Load Queue**:
   ```bash
   # Read automation_state.json
   # Get list of pending directories
   ```

3. **Process Batches**:
   ```bash
   for directory in $PENDING_DIRS; do
       python -m backend.app.cli_batch_processor \
           --path "$directory" \
           --analyze-vibe \
           --generate-embeddings
   done
   ```

4. **Log Output**:
   ```
   [2025-11-16 10:00:00] Starting automated batch processing
   [2025-11-16 10:00:05] Lock file created: scripts/batch_automation/.lock
   [2025-11-16 10:00:10] Processing queue with 3 pending directories
   [2025-11-16 10:00:15] Directory 1/3: /Volumes/Collection_A
   [2025-11-16 10:00:20] Scanning for files... found 150 files
   [2025-11-16 10:05:30] Batch A-001: processed 50 files
   [2025-11-16 10:10:40] Batch A-002: processed 50 files
   [2025-11-16 10:15:50] Batch A-003: processed 50 files
   [2025-11-16 10:20:00] Directory 1 complete: 150 files in 1200 seconds
   [2025-11-16 10:20:05] Generating embeddings for 150 samples...
   [2025-11-16 10:25:00] Embeddings generated: 150/150
   [2025-11-16 10:25:05] Directory 2/3: /Volumes/Collection_B
   [2025-11-16 10:25:10] Scanning for files... found 100 files
   ... (continues)
   [2025-11-16 11:30:00] All batches complete
   [2025-11-16 11:30:05] Total files processed: 350
   [2025-11-16 11:30:10] Total embeddings generated: 350
   [2025-11-16 11:30:15] Lock file removed
   [2025-11-16 11:30:20] Automation complete
   ```

**CLI Test**:
```python
def test_automated_batch_processing():
    result = validate_cli_output(
        command=['bash', 'scripts/batch_automation/automated_batch_runner.sh'],
        expected_patterns=[
            r'\[.*\] Starting automated batch processing',
            r'Processing queue with \d+ pending',
            r'Directory \d+/\d+: /',
            r'processed \d+ files',
            r'Generating embeddings for',
            r'Embeddings generated: \d+/\d+',
            r'All batches complete',
            r'Automation complete'
        ]
    )
    assert result['all_patterns_matched']
    assert result['success']
```

---

## Journey 5: SP-404MK2 Hardware Export

**Goal**: Export samples in hardware-compatible format
**Entry Points**: Sample card "Export" button, Kit export
**Format**: 48kHz/16-bit WAV, ASCII-safe filenames

### Journey Map

```
User Selects Sample(s)
    ↓
Clicks Export → Format Options Modal
    ├─ Format: WAV or AIFF
    ├─ Organization: flat/genre/BPM/kit
    └─ Target: SP-404MK2
    ↓
Submit Export
    ↓
System Validates Samples
    ├─ Duration <= 30 seconds
    ├─ Format convertible
    └─ Filename compatible
    ↓
Convert to 48kHz/16-bit
    ↓
Sanitize Filenames
    ↓
ZIP and Return for Download
    ↓
User Transfers to SD Card
    ↓
Load into SP-404MK2
```

### Step-by-Step Expected Behavior

#### 5.1 Single Sample Export
**Action**: User clicks export on a sample card

**Expected Modal**:
```html
<dialog>
  <h2>Export Sample</h2>
  <div>Sample: "Dark Trap Loop" (4.5s)</div>

  <select name="format">
    <option value="wav" selected>WAV (48kHz/16-bit)</option>
    <option value="aiff">AIFF (48kHz/16-bit)</option>
  </select>

  <button>Export for SP-404MK2</button>
  <button>Cancel</button>
</dialog>
```

**Expected API Call**: `POST /api/v1/sp404/export`
```json
{
    "sample_ids": [123],
    "format": "wav",
    "target_device": "sp404mk2"
}
```

**Backend Validation**:
1. Sample exists and file accessible
2. Duration <= 30 seconds (SP-404 limit)
3. File format supported (wav, mp3, flac, aiff)
4. Not corrupted (attempt to read metadata)

**Expected Response** (validation success):
```json
{
    "success": true,
    "export_id": 789,
    "samples": [
        {
            "sample_id": 123,
            "original_title": "Dark Trap Loop",
            "export_filename": "Dark_Trap_Loop.wav",
            "output_format": "wav",
            "sample_rate": 48000,
            "bit_depth": 16,
            "file_size_bytes": 350000,
            "conversion_time_seconds": 0.5,
            "status": "success"
        }
    ],
    "download_url": "/api/v1/sp404/exports/789/download",
    "zip_filename": "export_123.zip"
}
```

**Expected UI**:
- Modal shows "Export in progress..."
- Progress bar fills
- Completion: "Export ready. Click here to download"
- Download link appears

**MCP Test**:
```javascript
test('single sample export converts to SP-404 format', async ({ page }) => {
    // Open sample page
    await page.goto('http://localhost:8100/pages/samples.html');

    // Click export on first sample
    const firstCard = page.locator('[data-testid="sample-card"]').first();
    await firstCard.click('button[data-testid="export"]');

    // Modal appears
    await expect(page.locator('dialog')).toBeVisible();

    // Submit export
    const exportPromise = page.waitForResponse(
        resp => resp.url().includes('/api/v1/sp404/export')
    );
    await page.click('dialog button[type="submit"]');

    const response = await exportPromise;
    const data = await response.json();

    // Validate export
    expect(data.success).toBe(true);
    expect(data.samples[0].output_format).toBe('wav');
    expect(data.samples[0].sample_rate).toBe(48000);
    expect(data.samples[0].bit_depth).toBe(16);

    // Verify download link
    expect(data.download_url).toBeDefined();
});
```

#### 5.2 Batch Export
**Action**: User selects multiple samples with checkboxes and batch exports

**Expected Selection**:
- User checks 3-5 samples in grid
- "Export Selected" button appears
- Click to open batch export modal

**Expected Modal**:
```html
<dialog>
  <h2>Export 5 Samples</h2>
  <p>Total size: ~1.8 MB (when converted)</p>

  <select name="format">
    <option value="wav" selected>WAV</option>
    <option value="aiff">AIFF</option>
  </select>

  <select name="organize_by">
    <option value="flat" selected>Flat (all files in root)</option>
    <option value="genre">By Genre</option>
    <option value="bpm">By BPM Range</option>
  </select>

  <button>Export</button>
</dialog>
```

**Expected API Call**: `POST /api/v1/sp404/export-batch`
```json
{
    "sample_ids": [123, 124, 125, 126, 127],
    "format": "wav",
    "organize_by": "flat"
}
```

**Expected Response**:
```json
{
    "success": true,
    "export_id": 790,
    "samples": [
        {
            "sample_id": 123,
            "export_filename": "Sample_1.wav",
            "status": "success"
        },
        {
            "sample_id": 124,
            "export_filename": "Sample_2.wav",
            "status": "success"
        },
        {
            "sample_id": 125,
            "export_filename": "Sample_3.wav",
            "status": "success"
        }
    ],
    "successful": 3,
    "failed": 0,
    "download_url": "/api/v1/sp404/exports/790/download",
    "zip_size_bytes": 1800000
}
```

**MCP Test**:
```javascript
test('batch export creates organized ZIP', async ({ page }) => {
    // Select multiple samples
    const cards = page.locator('[data-testid="sample-card"]');
    for (let i = 0; i < 3; i++) {
        await cards.nth(i).locator('[type="checkbox"]').check();
    }

    // Click batch export
    await page.click('button:has-text("Export Selected")');

    // Modal appears
    await expect(page.locator('dialog')).toBeVisible();

    // Select options
    await page.selectOption('[name="organize_by"]', 'genre');

    // Submit
    const exportPromise = page.waitForResponse(
        resp => resp.url().includes('/export-batch')
    );
    await page.click('dialog button[type="submit"]');

    const response = await exportPromise;
    const data = await response.json();

    // Validate export
    expect(data.successful).toBe(3);
    expect(data.samples.length).toBe(3);
    expect(data.download_url).toBeDefined();
});
```

#### 5.3 Download & Verify
**Action**: User downloads exported ZIP and checks contents

**Expected ZIP Structure** (flat organization):
```
export_789.zip
├── Dark_Trap_Loop.wav (48kHz, 16-bit, ~350KB)
├── Heavy_Bass_Line.wav (48kHz, 16-bit, ~280KB)
├── Snare_Pattern.wav (48kHz, 16-bit, ~220KB)
└── README.txt
    Contents:
    - Instructions for SP-404MK2 transfer
    - Filename mapping
    - Compatibility info
```

**Expected ZIP Structure** (organized by genre):
```
export_790.zip
├── Trap/
│   ├── Dark_Trap_Loop.wav
│   └── Heavy_Bass_Line.wav
├── Hip-Hop/
│   └── Snare_Pattern.wav
└── README.txt
```

**File Validation**:
```bash
# Check ZIP contents
unzip -l export_789.zip

# Check audio format
file export_789/Dark_Trap_Loop.wav
# Expected: RIFF (little-endian) data, WAVE audio, mono, ...

# Check sample rate (should be 48000 Hz)
ffprobe -v quiet -select_streams a:0 \
    -show_entries stream=sample_rate \
    export_789/Dark_Trap_Loop.wav
# Expected output: sample_rate=48000
```

**CLI Test**:
```python
def test_sp404_export_creates_valid_wav():
    # Trigger export
    response = requests.post(
        'http://localhost:8000/api/v1/sp404/export',
        json={'sample_ids': [123], 'format': 'wav'}
    )

    export_id = response.json()['export_id']

    # Download ZIP
    download_response = requests.get(
        f'http://localhost:8000/api/v1/sp404/exports/{export_id}/download'
    )

    # Verify ZIP
    import zipfile
    with zipfile.ZipFile(io.BytesIO(download_response.content)) as z:
        assert len(z.namelist()) > 0

        # Check WAV files
        wav_files = [f for f in z.namelist() if f.endswith('.wav')]
        assert len(wav_files) > 0

        # Extract and check format
        for wav_file in wav_files:
            wav_data = z.read(wav_file)
            # Use ffprobe or librosa to verify format
```

---

## Embedding Requirements & Testing Strategy

### Embedding System Overview

**Purpose**: Enable semantic vibe search using vector similarity
**Model**: `text-embedding-3-small` via OpenRouter (1536 dimensions)
**Storage**: PostgreSQL `sample_embeddings` table
**Cost**: ~$0.00002 per sample

### Pre-Flight Check

**Before ANY Vibe Search Testing**:

```sql
-- Check current embedding coverage
SELECT
    COUNT(DISTINCT s.id) as total_samples,
    COUNT(DISTINCT se.sample_id) as embedded_samples,
    ROUND(100.0 * COUNT(DISTINCT se.sample_id) / NULLIF(COUNT(DISTINCT s.id), 0), 1) as coverage_pct
FROM samples s
LEFT JOIN sample_embeddings se ON s.id = se.sample_id
WHERE s.deleted_at IS NULL;
```

**Minimum Requirements**:
- **30 samples minimum** for any vibe search testing
- **80+ coverage** for production-like testing
- **All test samples** must have non-NULL embedding vectors

### Handling Missing Embeddings

**Scenario 1: Coverage 0-30% (Insufficient)**

Action: Skip vibe search tests, run embedding generation
```python
if coverage < 30:
    logger.warning(f"Only {coverage}% coverage - skipping vibe search")
    logger.info("Running: python scripts/generate_embeddings.py --all")
    # Wait 5 minutes for embeddings to generate
    await wait_for_embeddings(min_samples=30, timeout=300)
```

**Scenario 2: Coverage 30-80% (Partial)**

Action: Run tests with banner warning
```javascript
// In web UI
if (status.coverage_pct < 80) {
    showBanner(
        `⚠️  Vibe Search: ${status.coverage_pct}% of samples ready. ` +
        `${100 - status.coverage_pct}% still processing...`
    );
}
```

**Scenario 3: Coverage 80%+ (Production)**

Action: Full testing enabled, all features available

### Wait/Retry Logic

```python
async def wait_for_embeddings_with_alert(
    db: AsyncSession,
    min_samples: int = 30,
    timeout_seconds: int = 300,
    check_interval: int = 5
) -> dict:
    """
    Wait for embeddings with progress alerts.

    Returns:
        {
            'success': bool,
            'embedded_count': int,
            'wait_time': int,
            'message': str
        }
    """
    start = time.time()
    last_count = 0

    while time.time() - start < timeout_seconds:
        query = select(func.count(SampleEmbedding.sample_id))
        result = await db.execute(query)
        current_count = result.scalar()

        if current_count != last_count:
            progress_pct = (current_count / min_samples * 100) if min_samples > 0 else 0
            logger.info(
                f"Embeddings: {current_count}/{min_samples} ({progress_pct:.0f}%) "
                f"- elapsed: {int(time.time() - start)}s"
            )
            last_count = current_count

        if current_count >= min_samples:
            return {
                'success': True,
                'embedded_count': current_count,
                'wait_time': int(time.time() - start),
                'message': f'Ready: {current_count} embeddings'
            }

        await asyncio.sleep(check_interval)

    # Timeout reached
    return {
        'success': False,
        'embedded_count': last_count,
        'wait_time': timeout_seconds,
        'message': f'Timeout: Only {last_count}/{min_samples} embeddings after {timeout_seconds}s'
    }
```

### Alert User Strategy

**CLI Alert**:
```
⚠️  VIBE SEARCH REQUIRES EMBEDDINGS

Status: Only 15% of samples have embeddings (350/2328)

Generating embeddings in background...
Estimated time: ~2 hours

Check progress:
  ./venv/bin/python backend/scripts/generate_embeddings.py --status

Run immediately:
  ./venv/bin/python backend/scripts/generate_embeddings.py --resume
```

**Web UI Alert**:
```html
<div role="alert" class="alert alert-info">
    <div class="alert-header">
        <svg class="icon">⏳</svg>
        <span>Embeddings Processing</span>
    </div>
    <div class="alert-body">
        <p>Generating embeddings for vibe search...</p>
        <progress value="350" max="2328"></progress>
        <p>350/2328 samples complete (15%) - ~2 hours remaining</p>
    </div>
    <a href="/pages/batch.html" class="btn btn-sm">View Progress</a>
</div>
```

---

## Test Execution Plan

### Phase 1: Pre-Flight Setup (15 minutes)

1. **Verify Database**:
   ```bash
   # Check PostgreSQL running
   psql -d sp404_samples -c "SELECT COUNT(*) FROM samples;"
   # Expected: 2000+ samples

   # Check embeddings
   psql -d sp404_samples -c "SELECT COUNT(*) FROM sample_embeddings;"
   # Expected: 30+ (minimum for testing)
   ```

2. **Start Services**:
   ```bash
   # Terminal 1: Backend
   ./venv/bin/python backend/run.py

   # Terminal 2: Frontend
   cd react-app && npm run dev

   # Terminal 3: Embedding generation (if needed)
   ./venv/bin/python backend/scripts/generate_embeddings.py --resume
   ```

3. **Generate Test Data** (if needed):
   ```bash
   # Ensure 30+ samples have embeddings
   ./venv/bin/python backend/scripts/generate_embeddings.py --sample-ids 1-50
   ```

### Phase 2: Web UI Testing (45 minutes)

1. **Dashboard & Sample Collection** (15 min):
   ```bash
   npx playwright test frontend/tests/e2e/journey-1-samples.spec.js
   ```

2. **Vibe Search** (15 min):
   ```bash
   npx playwright test frontend/tests/e2e/journey-2-vibe-search.spec.js
   ```

3. **Kit Building** (10 min):
   ```bash
   npx playwright test frontend/tests/e2e/journey-3-kits.spec.js
   ```

4. **Batch Processing** (5 min):
   ```bash
   npx playwright test frontend/tests/e2e/journey-4-batch.spec.js
   ```

### Phase 3: CLI Testing (20 minutes)

1. **YouTube Analysis**:
   ```bash
   python backend/tests/test_cli_youtube.py
   ```

2. **Download Manager**:
   ```bash
   python backend/tests/test_cli_downloads.py
   ```

3. **Batch Automation**:
   ```bash
   python backend/tests/test_cli_batch.py
   ```

### Phase 4: Integration Testing (20 minutes)

1. **End-to-End Flow**:
   ```bash
   python backend/tests/test_journey_e2e.py
   ```

2. **Database Consistency**:
   ```bash
   python backend/tests/test_db_integrity.py
   ```

---

## Standards & Acceptance Criteria

### Performance Standards

| Journey | Metric | Standard | Test |
|---------|--------|----------|------|
| Sample Collection | YouTube analysis | < 3 seconds | `test_youtube_speed` |
| Vibe Search | Full search + render | < 2000ms | `test_vibe_search_latency` |
| Kit Building | Recommendation load | < 1500ms | `test_kit_rec_latency` |
| Batch Processing | Per-file time | < 10 seconds | `test_batch_speed` |
| SP-404 Export | Single sample | < 5000ms | `test_export_speed` |

### Data Integrity Standards

- No duplicate samples in database
- All embeddings have valid vectors (1536 dimensions)
- Audio files match metadata (duration, format)
- Kit assignments reference valid samples
- Batch jobs track all processed files

### User Experience Standards

- Loading states clearly visible
- Error messages actionable ("Generate embeddings" not "Error")
- No UI freezes during API calls
- Keyboard shortcuts functional
- Mobile responsive (if applicable)

---

## Common Issues & Troubleshooting

### Issue 1: Vibe Search Returns No Results

**Check**:
1. Do 30+ samples have embeddings?
   ```sql
   SELECT COUNT(*) FROM sample_embeddings;
   ```

2. Is query valid?
   ```python
   # Check for special characters
   if not query or len(query) < 3:
       return "Query too short"
   ```

3. Are filters too restrictive?
   - Try without filters first

**Fix**:
```bash
# Generate missing embeddings
./venv/bin/python backend/scripts/generate_embeddings.py --resume
```

### Issue 2: Batch Processing Stalled

**Check**:
1. Lock file exists?
   ```bash
   ls -la scripts/batch_automation/.lock
   ```

2. Check logs:
   ```bash
   tail -f scripts/batch_automation/automation.log
   ```

3. Database connection alive?
   ```bash
   psql -d sp404_samples -c "SELECT 1;"
   ```

**Fix**:
```bash
# Remove stale lock (if sure batch isn't running)
rm scripts/batch_automation/.lock

# Check processes
ps aux | grep generate_embeddings

# Restart batch
./scripts/batch_automation/automated_batch_runner.sh
```

### Issue 3: SP-404 Export Failed

**Check**:
1. Sample file exists?
   ```bash
   ls -lah samples/123.wav
   ```

2. Audio format valid?
   ```bash
   file samples/123.wav
   ffprobe samples/123.wav
   ```

3. Disk space available?
   ```bash
   df -h /exports
   ```

**Fix**:
```python
# Validate sample before export
from backend.app.services.sp404_export_service import SP404ExportService

service = SP404ExportService()
validation = await service.validate_sample(123)
print(validation)  # Shows specific issues
```

---

## Deliverables Checklist

- [x] User Journey Documentation (7 journeys)
- [x] Embedding pre-flight checks and wait/retry logic
- [x] MCP Chrome DevTools test patterns
- [x] CLI validation strategies
- [x] Performance and integrity standards
- [x] Troubleshooting guide
- [ ] Actual test implementations (Phase 2)
- [ ] Test execution report (Phase 2)
- [ ] Identified broken features (Phase 2)
- [ ] Fixed features with regression tests (Phase 2)

---

## Next Steps

1. Create Playwright test suite files (`frontend/tests/e2e/`)
2. Create Python CLI validation utilities (`backend/tests/utils/`)
3. Run comprehensive testing and identify broken features
4. Fix broken functionality against standards
5. Document results in testing report

---

*Last updated: 2025-11-16*
*Framework: MCP Chrome DevTools + Playwright + pytest*
*Status: Ready for test implementation*
