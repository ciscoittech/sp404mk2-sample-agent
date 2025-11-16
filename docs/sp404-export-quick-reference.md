# SP-404MK2 Export Service - Quick Reference Guide

**For**: Test Writer and Coder Agents
**Purpose**: Fast lookup of key implementation details

---

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── sp404_export.py          ← NEW: Export tracking models
│   │   ├── user_preferences.py      ← UPDATE: Add SP-404 preferences
│   │   ├── user.py                  ← UPDATE: Add export relationship
│   │   └── sample.py                ← UPDATE: Add export relationship
│   │
│   ├── schemas/
│   │   └── sp404_export.py          ← NEW: Export request/response schemas
│   │
│   ├── services/
│   │   └── sp404_export_service.py  ← NEW: Core export service
│   │
│   └── api/v1/endpoints/
│       └── sp404_export.py          ← NEW: Export API endpoints
│
└── tests/
    ├── services/
    │   └── test_sp404_export_service.py
    ├── api/
    │   └── test_sp404_export.py
    └── fixtures/
        └── audio/                   ← Test audio files
            ├── test_sample_48k.wav
            ├── test_sample_44k.mp3
            ├── test_sample_stereo.wav
            ├── test_sample_short.wav
            └── test_sample_unicode.wav
```

---

## Key Constants

```python
# SP-404MK2 Hardware Requirements
TARGET_SAMPLE_RATE = 48000  # Hz
TARGET_BIT_DEPTH = 16       # bit
MIN_DURATION_MS = 100       # milliseconds
MAX_FILENAME_LENGTH = 255   # characters

# Organization Strategies
ORGANIZE_STRATEGIES = ["flat", "genre", "bpm", "kit"]

# Supported Formats
INPUT_FORMATS = {'.wav', '.aiff', '.aif', '.mp3', '.flac', '.m4a', '.ogg'}
OUTPUT_FORMATS = {'wav', 'aiff'}

# BPM Ranges
BPM_RANGES = [
    (0, 70, "slow"),
    (70, 90, "70-90"),
    (90, 110, "90-110"),
    (110, 130, "110-130"),
    (130, 150, "130-150"),
    (150, 300, "fast")
]
```

---

## Core Method Signatures

### SP404ExportService

```python
async def convert_to_sp404_format(
    self,
    input_path: Path,
    output_path: Path,
    format: str = "wav"
) -> ConversionResult:
    """Convert audio to 48kHz/16-bit WAV or AIFF."""
    pass

def validate_sample(
    self,
    file_path: Path
) -> ValidationResult:
    """Validate sample meets SP-404MK2 requirements."""
    pass

def sanitize_filename(
    self,
    filename: str
) -> str:
    """Make filename ASCII-safe and hardware compatible."""
    pass

async def export_single_sample(
    self,
    sample_id: int,
    config: ExportConfig,
    db: AsyncSession
) -> ExportResult:
    """Export single sample with configuration."""
    pass

async def export_batch(
    self,
    sample_ids: List[int],
    config: ExportConfig,
    db: AsyncSession
) -> BatchExportResult:
    """Export multiple samples with organization."""
    pass

async def export_kit(
    self,
    kit_id: int,
    config: ExportConfig,
    db: AsyncSession
) -> ExportResult:
    """Export kit with bank/pad structure."""
    pass

async def create_export_zip(
    self,
    export_id: int,
    db: AsyncSession
) -> Path:
    """Create ZIP archive for download."""
    pass
```

---

## API Endpoint Summary

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| POST | `/sp404/samples/{id}/export` | Export single sample | ExportResult |
| POST | `/sp404/samples/export-batch` | Export multiple samples | BatchExportResult |
| POST | `/sp404/kits/{id}/export` | Export kit structure | ExportResult |
| GET | `/sp404/exports/{id}/download` | Download as ZIP | FileResponse |
| GET | `/sp404/exports` | List export history | ExportHistoryResponse |

---

## Request/Response Examples

### Export Single Sample

**Request:**
```json
POST /api/v1/sp404/samples/123/export

{
  "organize_by": "genre",
  "format": "wav",
  "include_metadata": true,
  "sanitize_filenames": true,
  "output_base_path": null
}
```

**Response:**
```json
{
  "success": true,
  "sample_id": 123,
  "output_path": "/exports/hip-hop",
  "output_filename": "sick_beat_2024.wav",
  "format": "wav",
  "file_size_bytes": 854016,
  "conversion_time_seconds": 2.3,
  "error": null
}
```

### Export Batch

**Request:**
```json
POST /api/v1/sp404/samples/export-batch

{
  "sample_ids": [1, 2, 3, 4, 5],
  "config": {
    "organize_by": "bpm",
    "format": "wav",
    "include_metadata": false,
    "sanitize_filenames": true
  }
}
```

**Response:**
```json
{
  "total_requested": 5,
  "successful": 4,
  "failed": 1,
  "total_size_bytes": 16384000,
  "total_time_seconds": 8.7,
  "output_base_path": "/exports/batch_789",
  "organized_by": "bpm",
  "results": [
    {
      "success": true,
      "sample_id": 1,
      "output_path": "/exports/batch_789/90-110",
      "output_filename": "sample_001.wav",
      "format": "wav",
      "file_size_bytes": 4096000,
      "conversion_time_seconds": 2.1
    },
    // ... more results
  ],
  "errors": [
    "Sample 3: Duration too short: 50ms (minimum: 100ms)"
  ]
}
```

---

## Database Schema Quick Reference

### SP404Export

```sql
CREATE TABLE sp404_exports (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,  -- FK to users.id
    export_type VARCHAR NOT NULL,  -- "single", "batch", "kit"
    sample_count INTEGER NOT NULL,
    output_path VARCHAR NOT NULL,
    organized_by VARCHAR NOT NULL,  -- "flat", "genre", "bpm", "kit"
    format VARCHAR NOT NULL,  -- "wav", "aiff"
    total_size_bytes BIGINT NOT NULL DEFAULT 0,
    export_duration_seconds FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_sp404_exports_user_created ON sp404_exports(user_id, created_at);
CREATE INDEX ix_sp404_exports_type_created ON sp404_exports(export_type, created_at);
```

### SP404ExportSample

```sql
CREATE TABLE sp404_export_samples (
    id INTEGER PRIMARY KEY,
    export_id INTEGER NOT NULL,  -- FK to sp404_exports.id
    sample_id INTEGER NOT NULL,  -- FK to samples.id
    output_filename VARCHAR NOT NULL,
    output_subfolder VARCHAR,
    conversion_successful BOOLEAN NOT NULL DEFAULT TRUE,
    error_message VARCHAR
);

CREATE INDEX ix_sp404_export_samples_export ON sp404_export_samples(export_id);
CREATE INDEX ix_sp404_export_samples_sample ON sp404_export_samples(sample_id);
CREATE INDEX ix_sp404_export_samples_sample_export ON sp404_export_samples(sample_id, export_id);
```

### UserPreference Updates

```sql
ALTER TABLE user_preferences ADD COLUMN sp404_export_format VARCHAR NOT NULL DEFAULT 'wav';
ALTER TABLE user_preferences ADD COLUMN sp404_default_organization VARCHAR NOT NULL DEFAULT 'flat';
ALTER TABLE user_preferences ADD COLUMN sp404_sanitize_filenames BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_preferences ADD COLUMN sp404_include_metadata BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE user_preferences ADD COLUMN sp404_export_base_path VARCHAR;
```

---

## Librosa/Soundfile Usage

### Load Audio

```python
# Load preserving original sample rate
y, sr = librosa.load(str(input_path), sr=None, mono=False)

# y: numpy array (samples,) for mono or (channels, samples) for stereo
# sr: original sample rate in Hz
```

### Resample

```python
# Resample single channel
y_resampled = librosa.resample(
    y,
    orig_sr=44100,
    target_sr=48000
)

# Resample stereo (process each channel)
y_resampled = np.array([
    librosa.resample(y[ch], orig_sr=sr, target_sr=48000)
    for ch in range(y.shape[0])
])
```

### Write Audio

```python
# Prepare: soundfile expects (time, channels) shape
y_transposed = y.T if y.ndim > 1 else y

# Write as 16-bit PCM WAV
sf.write(
    str(output_path),
    y_transposed,
    48000,  # sample rate
    subtype='PCM_16',  # 16-bit PCM
    format='WAV'  # or 'AIFF'
)
```

### Get Duration

```python
duration = librosa.get_duration(y=y, sr=sr)  # seconds
duration_ms = duration * 1000  # milliseconds
```

---

## Filename Sanitization Rules

```python
def sanitize_filename(self, filename: str) -> str:
    """
    Sanitization steps:
    1. Normalize unicode → ASCII (é → e)
    2. Replace spaces → underscores
    3. Remove non-alphanumeric except underscore/hyphen
    4. Remove consecutive separators
    5. Remove leading dots/dashes
    6. Ensure not empty (fallback: "sample")
    7. Limit length to 255 chars
    """

    # Examples:
    # "Sick Beat 🔥.mp3" → "sick_beat.mp3"
    # "Sample (2024).wav" → "sample_2024.wav"
    # "Café Music.aiff" → "cafe_music.aiff"
    # "名前.wav" → "sample.wav"  # Non-ASCII removed
```

---

## Organization Strategy Implementation

```python
def _organize_export_path(
    self,
    base_path: Path,
    sample: Sample,
    organize_by: str
) -> Path:
    """
    flat   → base_path/
    genre  → base_path/{genre}/
    bpm    → base_path/{bpm_range}/
    kit    → Handled separately in export_kit()
    """

    if organize_by == "flat":
        return base_path

    elif organize_by == "genre":
        genre = sample.genre or "unknown_genre"
        genre = self.sanitize_filename(genre)
        return base_path / genre

    elif organize_by == "bpm":
        bpm_folder = self._get_bpm_folder_name(sample.bpm)
        return base_path / bpm_folder

    else:
        return base_path  # Default to flat

def _get_bpm_folder_name(self, bpm: Optional[float]) -> str:
    """Map BPM to folder name."""
    if bpm is None:
        return "unknown_bpm"

    for min_bpm, max_bpm, folder_name in self.BPM_RANGES:
        if min_bpm <= bpm < max_bpm:
            return folder_name

    return "unknown_bpm"
```

---

## Error Handling Patterns

### Validation Errors

```python
# Validate before conversion
validation = self.validate_sample(input_path)

if not validation.valid:
    return ExportResult(
        success=False,
        sample_id=sample_id,
        output_path="",
        output_filename="",
        format=config.format,
        file_size_bytes=0,
        conversion_time_seconds=0,
        error=f"Validation failed: {', '.join(validation.errors)}"
    )
```

### Conversion Errors

```python
try:
    result = await self.convert_to_sp404_format(input_path, output_path, format)

    if not result.success:
        return ExportResult(
            success=False,
            error=result.error_message
        )

except Exception as e:
    logger.error(f"Conversion failed: {e}")
    return ExportResult(
        success=False,
        error=f"Conversion failed: {str(e)}"
    )
```

### Batch Processing (Continue on Error)

```python
for sample_id in sample_ids:
    try:
        result = await self.export_single_sample(sample_id, config, db)
        results.append(result)

        if result.success:
            successful += 1
        else:
            failed += 1
            errors.append(f"Sample {sample_id}: {result.error}")

    except Exception as e:
        failed += 1
        errors.append(f"Sample {sample_id}: {str(e)}")
        logger.error(f"Failed to export sample {sample_id}: {e}")

# Return partial success
return BatchExportResult(
    total_requested=len(sample_ids),
    successful=successful,
    failed=failed,
    errors=errors
)
```

---

## Test Coverage Checklist

### Unit Tests - Service

- [ ] `test_convert_to_sp404_format_wav()` - Convert to WAV
- [ ] `test_convert_to_sp404_format_aiff()` - Convert to AIFF
- [ ] `test_convert_44k_to_48k()` - Sample rate conversion
- [ ] `test_convert_stereo_preserves_channels()` - Stereo handling
- [ ] `test_validate_sample_valid()` - Valid sample passes
- [ ] `test_validate_sample_too_short()` - Duration < 100ms fails
- [ ] `test_validate_sample_unsupported_format()` - Format check
- [ ] `test_validate_sample_file_not_found()` - Missing file
- [ ] `test_sanitize_filename_unicode()` - Unicode normalization
- [ ] `test_sanitize_filename_special_chars()` - Special char removal
- [ ] `test_sanitize_filename_spaces()` - Space to underscore
- [ ] `test_organize_path_flat()` - Flat organization
- [ ] `test_organize_path_genre()` - Genre organization
- [ ] `test_organize_path_bpm()` - BPM organization
- [ ] `test_export_single_sample_success()` - Single export works
- [ ] `test_export_single_sample_validation_fails()` - Handle validation error
- [ ] `test_export_batch_all_success()` - Batch all succeed
- [ ] `test_export_batch_partial_failure()` - Batch partial success
- [ ] `test_export_kit_structure()` - Kit bank/pad layout
- [ ] `test_create_export_zip()` - ZIP creation

### Integration Tests - API

- [ ] `test_export_single_sample_endpoint()` - POST endpoint works
- [ ] `test_export_batch_endpoint()` - Batch endpoint works
- [ ] `test_export_kit_endpoint()` - Kit endpoint works
- [ ] `test_download_export_endpoint()` - ZIP download works
- [ ] `test_export_invalid_sample_id()` - 404 error
- [ ] `test_export_invalid_format()` - 422 error
- [ ] `test_export_creates_database_record()` - DB tracking
- [ ] `test_export_tracks_samples()` - Sample tracking

### E2E Tests - Browser

- [ ] `test_export_button_visible()` - UI element exists
- [ ] `test_export_modal_opens()` - Modal interaction
- [ ] `test_export_format_selection()` - Select format
- [ ] `test_export_organization_selection()` - Select strategy
- [ ] `test_export_initiates()` - Export starts
- [ ] `test_export_shows_success()` - Success message
- [ ] `test_export_download_link()` - Download link appears
- [ ] `test_batch_export_multiple_samples()` - Multi-select

---

## Common Gotchas

### 1. Stereo vs Mono Handling

```python
# ❌ Wrong: Assumes mono
y_resampled = librosa.resample(y, orig_sr=sr, target_sr=48000)

# ✅ Correct: Handle both
if y.ndim > 1:
    y_resampled = np.array([
        librosa.resample(y[ch], orig_sr=sr, target_sr=48000)
        for ch in range(y.shape[0])
    ])
else:
    y_resampled = librosa.resample(y, orig_sr=sr, target_sr=48000)
```

### 2. Soundfile Shape Requirements

```python
# ❌ Wrong: Librosa shape is (channels, time)
sf.write(path, y, sr, subtype='PCM_16')

# ✅ Correct: Transpose to (time, channels)
y_transposed = y.T if y.ndim > 1 else y
sf.write(path, y_transposed, sr, subtype='PCM_16')
```

### 3. Async Thread Pool for CPU Work

```python
# ❌ Wrong: Blocks event loop
result = self._convert_sync(input_path, output_path, format)

# ✅ Correct: Run in thread pool
result = await asyncio.to_thread(
    self._convert_sync,
    input_path,
    output_path,
    format
)
```

### 4. Batch Processing Error Handling

```python
# ❌ Wrong: Fails entire batch on error
for sample_id in sample_ids:
    result = await self.export_single_sample(sample_id, config, db)
    if not result.success:
        raise Exception("Export failed")  # Stops processing

# ✅ Correct: Continue on error
for sample_id in sample_ids:
    try:
        result = await self.export_single_sample(sample_id, config, db)
        results.append(result)
    except Exception as e:
        errors.append(f"Sample {sample_id}: {e}")
        continue  # Keep processing
```

### 5. Unicode Filename Handling

```python
# ❌ Wrong: Path might contain unicode
output_path = base_path / original_filename

# ✅ Correct: Sanitize before creating path
sanitized_name = self.sanitize_filename(original_filename)
output_path = base_path / sanitized_name
```

---

## Performance Tips

### 1. Skip Conversion if Already Correct

```python
# Check if already 48kHz/16-bit WAV
if sr == 48000 and input_path.suffix.lower() == '.wav':
    # Check bit depth
    info = sf.info(str(input_path))
    if info.subtype == 'PCM_16':
        # Just copy file instead of converting
        shutil.copy(input_path, output_path)
        return ConversionResult(success=True, ...)
```

### 2. Parallel Batch Processing

```python
# For future: Process multiple samples concurrently
import asyncio

tasks = [
    self.export_single_sample(sample_id, config, db)
    for sample_id in sample_ids[:5]  # Limit concurrency
]

results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. Memory Management

```python
# Clear variables after processing
y, sr = librosa.load(input_path)
# ... process ...
del y  # Free memory before next sample
```

---

## Migration Script Template

```python
"""Add SP-404 export tracking

Revision ID: sp404_export_001
Create Date: 2025-11-14
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create sp404_exports table
    op.create_table(
        'sp404_exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('export_type', sa.String(), nullable=False),
        sa.Column('sample_count', sa.Integer(), nullable=False),
        sa.Column('output_path', sa.String(), nullable=False),
        sa.Column('organized_by', sa.String(), nullable=False),
        sa.Column('format', sa.String(), nullable=False),
        sa.Column('total_size_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('export_duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sp404_exports_user_created', 'sp404_exports', ['user_id', 'created_at'])
    op.create_index('ix_sp404_exports_type_created', 'sp404_exports', ['export_type', 'created_at'])

    # Create sp404_export_samples table
    op.create_table(
        'sp404_export_samples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('export_id', sa.Integer(), nullable=False),
        sa.Column('sample_id', sa.Integer(), nullable=False),
        sa.Column('output_filename', sa.String(), nullable=False),
        sa.Column('output_subfolder', sa.String(), nullable=True),
        sa.Column('conversion_successful', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['export_id'], ['sp404_exports.id'], ),
        sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sp404_export_samples_export', 'sp404_export_samples', ['export_id'])
    op.create_index('ix_sp404_export_samples_sample', 'sp404_export_samples', ['sample_id'])

    # Add SP-404 preferences to user_preferences
    op.add_column('user_preferences', sa.Column('sp404_export_format', sa.String(), nullable=False, server_default='wav'))
    op.add_column('user_preferences', sa.Column('sp404_default_organization', sa.String(), nullable=False, server_default='flat'))
    op.add_column('user_preferences', sa.Column('sp404_sanitize_filenames', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('user_preferences', sa.Column('sp404_include_metadata', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('user_preferences', sa.Column('sp404_export_base_path', sa.String(), nullable=True))

def downgrade():
    # Remove columns from user_preferences
    op.drop_column('user_preferences', 'sp404_export_base_path')
    op.drop_column('user_preferences', 'sp404_include_metadata')
    op.drop_column('user_preferences', 'sp404_sanitize_filenames')
    op.drop_column('user_preferences', 'sp404_default_organization')
    op.drop_column('user_preferences', 'sp404_export_format')

    # Drop tables
    op.drop_table('sp404_export_samples')
    op.drop_table('sp404_exports')
```

---

**This quick reference provides all essential implementation details for the Test Writer and Coder agents.**
