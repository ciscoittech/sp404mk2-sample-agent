# Storage Strategy & Batch Processing Plan

**Created**: 2025-11-14
**Status**: Active Implementation
**Current Storage**: 3.0 GB samples + 3.8 MB database

---

## 📊 CURRENT STATE ANALYSIS

### Storage Breakdown
```
samples/                  3.0 GB (7,284 WAV files)
├── mediafire/           55 MB (50 files)
├── google_drive/        2.0 GB (6,474 files)
└── gumroad/             908 MB (760 files)

Databases:
├── sp404_samples.db     3.8 MB (root)
└── backend/sp404_samples.db  76 KB

backend/uploads/         TBD (web UI uploads)
```

### Sample Quality Distribution
- **24-bit WAV**: 760 files (The Crate vol.5)
- **16-bit WAV**: 6,524 files (Various sources)
- **Sample Rates**: 44.1kHz, 48kHz

### Database Size Projection
**Without Analysis**:
- Current: 3.8 MB (3 samples analyzed)
- Projected: ~9.2 MB for 7,284 samples (metadata only)

**With Hybrid Analysis**:
- Audio features: ~20 fields × 7,284 samples = ~3 MB
- AI vibe analysis: ~500 chars × 7,284 samples = ~3.5 MB
- **Total Projected**: ~16 MB for full analysis

**Conclusion**: Database storage is negligible, focus on WAV file management

---

## 🎯 LONG-TERM STORAGE STRATEGY

### Strategy 1: Tiered Storage Architecture

#### **Tier 1: Active Production Library** (Hot Storage)
**Location**: `./samples/production/`
**Contents**: Curated, analyzed samples ready for immediate use
**Target Size**: 5-10 GB
**Criteria**:
- High-quality rating (≥7/10)
- Complete metadata (audio features + AI analysis)
- SP-404 MK2 compatible (48kHz/16-bit or convertible)
- Genre-organized, searchable

**Actions**:
- Import all 7,284 samples to database
- Run hybrid analysis
- Filter best samples based on analysis
- Export to production tier

#### **Tier 2: Archive Library** (Warm Storage)
**Location**: `./samples/archive/`
**Contents**: Original downloads, lower-quality samples, duplicates
**Target Size**: 10-20 GB
**Criteria**:
- Original source files (preserve quality)
- Less frequently accessed
- Bulk collections not yet curated

**Actions**:
- Keep current `./samples/` structure
- Add archive metadata (source, date downloaded)
- Create archive index

#### **Tier 3: Cold Storage** (External/Cloud Backup)
**Location**: External HD or cloud (Google Drive, Dropbox, S3)
**Contents**: Complete backup of all tiers
**Target Size**: Full mirror
**Frequency**: Weekly/monthly sync

**Actions**:
- Set up automated backup script
- Consider compression for cold storage
- Maintain backup manifest

### Strategy 2: Deduplication & Compression

#### Audio File Deduplication
**Problem**: Potential duplicates across sources
**Solution**:
```python
# Use audio fingerprinting
# Compare MD5 hashes of WAV files
# Identify identical samples with different names
# Keep highest quality version
```

**Expected Savings**: 10-20% storage reduction

#### Lossless Compression (FLAC)
**Trade-off**:
- **Pro**: 30-40% size reduction (WAV → FLAC)
- **Con**: Requires decompression for SP-404 MK2
- **Decision**: Use for Tier 2 (Archive) only

**Implementation**:
```bash
# Convert archive to FLAC
for file in samples/archive/**/*.wav; do
  ffmpeg -i "$file" -c:a flac "${file%.wav}.flac"
  # Verify, then delete original
done
```

### Strategy 3: Metadata-First Approach

**Concept**: Database as source of truth
**Benefit**: Delete WAV files, keep metadata, re-download if needed

**Database Schema**:
```sql
-- Add source_url and download_metadata columns
ALTER TABLE samples ADD COLUMN source_url TEXT;
ALTER TABLE samples ADD COLUMN source_hash TEXT;
ALTER TABLE samples ADD COLUMN archive_location TEXT;
```

**Workflow**:
1. Analyze all samples → database
2. Keep only high-value WAVs locally
3. Store source URLs and hashes
4. Re-download on demand from original sources

**Expected Savings**: 50-70% active storage reduction

---

## ⚡ BATCH PROCESSING IMPLEMENTATION

### Phase 1: Database Import (Metadata Only)

**Goal**: Import all 7,284 samples with basic metadata

**Script**: `backend/scripts/batch_import_samples.py`

```bash
# Test with small batch first (50 samples)
python backend/scripts/batch_import_samples.py \
  --directory ./samples/mediafire \
  --batch-size 50 \
  --skip-analysis

# Full import (all folders)
python backend/scripts/batch_import_samples.py \
  --directory ./samples \
  --batch-size 100 \
  --skip-analysis \
  --parallel-workers 4
```

**Estimated Time**: 10-15 minutes
**Storage Impact**: +5 MB database

### Phase 2: Audio Feature Extraction (Librosa)

**Goal**: Extract 20+ audio features for all samples

**Configuration**:
```python
# backend/app/core/config.py
BATCH_PROCESSING_CONFIG = {
    "parallel_workers": 10,  # CPU cores to use
    "batch_size": 100,
    "audio_analysis_timeout": 60,  # seconds per sample
}
```

**Execution**:
```bash
python backend/scripts/batch_audio_analysis.py \
  --parallel-workers 10 \
  --batch-size 100 \
  --resume-on-failure
```

**Estimated Time**: 6-8 hours (3-5 seconds per sample × 7,284)
**Cost**: $0 (local processing)
**Storage Impact**: +3 MB database

**Monitoring**:
```bash
# Watch progress
tail -f backend/logs/batch_audio_analysis.log

# Check database size
du -sh backend/sp404_samples.db
```

### Phase 3: AI Vibe Analysis (OpenRouter)

**Goal**: Generate AI vibe descriptions for all samples

**Cost Estimates**:
- **Qwen3-7B** (recommended): ~$0.00001 per sample × 7,284 = ~$0.07
- **Qwen3-235B** (deep): ~$0.00005 per sample × 7,284 = ~$0.36

**Configuration**:
```python
# User preferences
{
  "vibe_model": "qwen/qwen3-7b-it",  # Fast & cheap
  "auto_analysis_batch": True,
  "max_cost_per_request": 0.001,  # $0.001 limit
  "parallel_api_requests": 5  # Rate limit friendly
}
```

**Execution**:
```bash
python backend/scripts/batch_vibe_analysis.py \
  --model qwen/qwen3-7b-it \
  --parallel-requests 5 \
  --max-cost 0.10 \
  --resume-on-failure
```

**Estimated Time**: 4-6 hours
**Cost**: ~$0.07 total
**Storage Impact**: +3.5 MB database

**Budget Control**:
- Stop if daily cost > $1.00
- Resume next day if needed
- Prioritize high-quality samples first

### Phase 4: Quality Filtering & Organization

**Goal**: Identify best samples, organize into production library

**Criteria**:
```python
# Quality scoring algorithm
def calculate_sample_quality(sample):
    score = 0

    # Audio features (40 points)
    if sample.bpm_confidence > 0.8: score += 10
    if sample.spectral_centroid in [2000, 4000]: score += 10  # Sweet spot
    if sample.harmonic_percussive_ratio > 0.5: score += 10
    if sample.rms_energy > 0.3: score += 10

    # AI vibe analysis (40 points)
    if sample.vibe_confidence > 0.7: score += 20
    if len(sample.genre_tags) >= 2: score += 10
    if sample.production_quality in ["high", "professional"]: score += 10

    # File quality (20 points)
    if sample.bit_depth == 24: score += 10
    if sample.sample_rate >= 48000: score += 10

    return score  # 0-100
```

**Actions**:
```bash
python backend/scripts/curate_production_library.py \
  --min-quality-score 70 \
  --output-dir ./samples/production \
  --organize-by genre
```

**Expected Output**:
- Production library: 2,000-3,000 samples (5-8 GB)
- Archive: 4,000-5,000 samples (keep as-is)

---

## 🔄 AUTOMATED WORKFLOWS

### Workflow 1: Weekly Sample Discovery

**Goal**: Continuously find and import new sample packs

**Schedule**: Every Sunday
```bash
# Cron job
0 2 * * 0 /path/to/sample_discovery_agent.sh
```

**Script**:
```bash
#!/bin/bash
# sample_discovery_agent.sh

# Search Reddit r/drumkits for new packs
python scripts/reddit_sample_scraper.py \
  --subreddit drumkits \
  --since 7days

# Download new packs (up to 5 GB)
python scripts/download_new_packs.py \
  --max-size 5GB

# Auto-import and analyze
python backend/scripts/batch_import_samples.py \
  --directory ./samples/new \
  --auto-analyze
```

### Workflow 2: Database Optimization

**Goal**: Compress database, remove orphans, rebuild indexes

**Schedule**: Monthly
```bash
# Vacuum and analyze
sqlite3 backend/sp404_samples.db "VACUUM; ANALYZE;"

# Remove orphaned records
python backend/scripts/cleanup_database.py \
  --remove-orphans \
  --verify-files

# Backup
cp backend/sp404_samples.db backend/backups/sp404_samples_$(date +%Y%m%d).db
```

### Workflow 3: Cold Storage Sync

**Goal**: Backup to external storage

**Schedule**: Weekly
```bash
# Rsync to external drive
rsync -avz --progress \
  ./samples/ \
  /Volumes/ExternalDrive/SP404_Samples/

# Or cloud backup
rclone sync ./samples/ gdrive:SP404_Samples/
```

---

## 📈 SCALING CONSIDERATIONS

### Current Capacity (7,284 samples)
- **Database**: ~16 MB (with full analysis)
- **WAV Files**: 3.0 GB
- **Total**: 3.02 GB

### Projected Growth (50,000 samples)
- **Database**: ~110 MB
- **WAV Files**: 20-25 GB
- **Total**: ~25 GB

### Storage Limits
**macOS Disk**:
- Current free space: Check with `df -h`
- Recommended reserve: 50 GB minimum
- **Sample library limit**: 25-30 GB max

**Solutions at Scale**:
1. **Aggressive Curation**: Keep only 10,000 best samples
2. **External Storage**: Move archive to external HD
3. **Cloud Hybrid**: Database local, WAV files in cloud
4. **FLAC Compression**: Archive tier only

---

## 🛠 IMPLEMENTATION CHECKLIST

### Immediate (This Week)
- [ ] Run Phase 1: Import all 7,284 samples (metadata only)
- [ ] Test Phase 2: Audio analysis on 100 samples
- [ ] Verify Phase 3: AI vibe analysis on 50 samples (cost: ~$0.0005)
- [ ] Monitor storage growth and database size
- [ ] Set up backup script to external/cloud

### Short Term (This Month)
- [ ] Complete Phase 2: Full audio feature extraction
- [ ] Complete Phase 3: AI vibe analysis (budget: $0.50)
- [ ] Run Phase 4: Quality filtering and curation
- [ ] Organize production library (5-10 GB)
- [ ] Archive remaining samples

### Long Term (Ongoing)
- [ ] Weekly sample discovery automation
- [ ] Monthly database optimization
- [ ] Quarterly storage audit
- [ ] Continuous production library refinement

---

## 📊 MONITORING DASHBOARD

### Key Metrics to Track
```python
# Database queries
SELECT COUNT(*) FROM samples;  -- Total samples
SELECT COUNT(*) FROM samples WHERE audio_features IS NOT NULL;  -- Analyzed
SELECT COUNT(*) FROM samples WHERE vibe_analysis IS NOT NULL;  -- AI analyzed
SELECT AVG(quality_score) FROM samples;  -- Average quality
SELECT SUM(file_size) FROM samples;  -- Total storage

# Storage breakdown
du -sh samples/**/  # By source
du -sh backend/sp404_samples.db  # Database size
```

### Cost Tracking
```sql
SELECT
  DATE(timestamp) as date,
  SUM(total_cost) as daily_cost,
  COUNT(*) as api_calls
FROM api_usage
WHERE timestamp >= DATE('now', '-30 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

---

## 🎯 SUCCESS CRITERIA

**Phase 1 Complete**:
- ✅ All 7,284 samples imported to database
- ✅ Metadata validated (file size, format, sample rate)
- ✅ Database size < 10 MB

**Phase 2 Complete**:
- ✅ Audio features extracted for 100% of samples
- ✅ BPM, key, spectral features available
- ✅ Processing time < 10 hours

**Phase 3 Complete**:
- ✅ AI vibe analysis for 100% of samples
- ✅ Total cost < $0.50
- ✅ Vibe confidence > 70% average

**Phase 4 Complete**:
- ✅ Production library: 2,000+ curated samples
- ✅ Quality score ≥ 70 for all production samples
- ✅ Organized by genre/BPM/key

**Long-Term Success**:
- ✅ Storage < 25 GB total
- ✅ Database < 100 MB
- ✅ 90%+ samples have full analysis
- ✅ Automated workflows running smoothly

---

**Last Updated**: 2025-11-14
**Next Review**: After Phase 1 completion
