# SP-404MK2 Export Service - Visual Architecture

## System Component Diagram

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER (Frontend)                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Sample Grid  │  │ Kit Builder  │  │ Batch Export │  │ Export Modal │    │
│  │              │  │              │  │              │  │              │    │
│  │ - Select     │  │ - Organize   │  │ - Multi-sel  │  │ - Configure  │    │
│  │ - Export btn │  │ - Export kit │  │ - Bulk ops   │  │ - Download   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │                  │             │
│         └─────────────────┴──────────────────┴──────────────────┘             │
│                                    │                                          │
└────────────────────────────────────┼──────────────────────────────────────────┘
                                     │
                                     │ HTTPS/REST API
                                     │
┌────────────────────────────────────▼──────────────────────────────────────────┐
│                         API LAYER (FastAPI Routes)                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  POST /api/v1/sp404/samples/{id}/export                                       │
│  ├─ Request: ExportConfig (format, organize_by, options)                      │
│  └─ Response: ExportResult (success, output_path, file_size, etc.)            │
│                                                                                │
│  POST /api/v1/sp404/samples/export-batch                                      │
│  ├─ Request: sample_ids[], ExportConfig                                       │
│  └─ Response: BatchExportResult (stats, results[], errors[])                  │
│                                                                                │
│  POST /api/v1/sp404/kits/{id}/export                                          │
│  ├─ Request: ExportConfig                                                     │
│  └─ Response: ExportResult (kit structure)                                    │
│                                                                                │
│  GET /api/v1/sp404/exports/{id}/download                                      │
│  └─ Response: FileResponse (ZIP archive)                                      │
│                                                                                │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
                                     │ Service Layer Call
                                     │
┌────────────────────────────────────▼──────────────────────────────────────────┐
│                      SERVICE LAYER (Business Logic)                            │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                      SP404ExportService                                  │ │
│  │                                                                          │ │
│  │  Core Methods:                                                           │ │
│  │  ├─ validate_sample(file_path)                                          │ │
│  │  │  └─ Check: duration >= 100ms, format supported, file readable        │ │
│  │  │                                                                       │ │
│  │  ├─ sanitize_filename(filename)                                         │ │
│  │  │  └─ ASCII-safe, hardware compatible                                  │ │
│  │  │                                                                       │ │
│  │  ├─ convert_to_sp404_format(input, output, format)                     │ │
│  │  │  ├─ Load audio (librosa)                                            │ │
│  │  │  ├─ Resample to 48kHz                                               │ │
│  │  │  └─ Write 16-bit PCM (soundfile)                                    │ │
│  │  │                                                                       │ │
│  │  ├─ export_single_sample(sample_id, config)                            │ │
│  │  │  ├─ Get sample from DB                                              │ │
│  │  │  ├─ Validate                                                         │ │
│  │  │  ├─ Organize path                                                    │ │
│  │  │  ├─ Convert                                                          │ │
│  │  │  └─ Track in DB                                                      │ │
│  │  │                                                                       │ │
│  │  ├─ export_batch(sample_ids[], config)                                 │ │
│  │  │  └─ Process all samples, aggregate results                          │ │
│  │  │                                                                       │ │
│  │  ├─ export_kit(kit_id, config)                                         │ │
│  │  │  └─ Organize by bank/pad structure                                  │ │
│  │  │                                                                       │ │
│  │  └─ create_export_zip(export_id)                                       │ │
│  │     └─ Bundle files for download                                        │ │
│  │                                                                          │ │
│  │  Helper Methods:                                                         │ │
│  │  ├─ _organize_export_path(base, sample, strategy)                      │ │
│  │  ├─ _get_bpm_folder_name(bpm)                                          │ │
│  │  ├─ _write_metadata_file(path, sample, conversion)                     │ │
│  │  └─ _create_export_record(type, count, path, ...)                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  Integration with Existing Services:                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ SampleService    │  │ PreferencesServ  │  │ AudioFeaturesServ│          │
│  │                  │  │                  │  │                  │          │
│  │ - get_sample()   │  │ - get_prefs()    │  │ - analyze_file() │          │
│  │ - File paths     │  │ - Defaults       │  │ - Validation     │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                                │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
┌─────────────────────────┐  ┌──────────────┐  ┌──────────────────┐
│   AUDIO LIBRARIES       │  │  DATABASE    │  │  FILE SYSTEM     │
├─────────────────────────┤  ├──────────────┤  ├──────────────────┤
│                         │  │              │  │                  │
│  ┌────────────────┐    │  │ SQLAlchemy   │  │ Input Samples    │
│  │ librosa        │    │  │ + aiosqlite  │  │ (/uploads/)      │
│  │                │    │  │              │  │                  │
│  │ - load()       │    │  │ Tables:      │  │ Output Exports   │
│  │ - resample()   │    │  │ - SP404Export│  │ (/exports/)      │
│  │ - get_duration │    │  │ - SP404Export│  │                  │
│  └────────────────┘    │  │   Sample     │  │ ZIP Archives     │
│                         │  │ - Sample     │  │                  │
│  ┌────────────────┐    │  │ - Kit        │  └──────────────────┘
│  │ soundfile      │    │  │ - UserPref   │
│  │                │    │  │              │
│  │ - write()      │    │  └──────────────┘
│  │ - PCM_16       │    │
│  │ - WAV/AIFF     │    │
│  └────────────────┘    │
│                         │
│  ┌────────────────┐    │
│  │ numpy          │    │
│  │                │    │
│  │ - Array ops    │    │
│  │ - Transpose    │    │
│  └────────────────┘    │
│                         │
└─────────────────────────┘
```

## Data Flow Diagram - Single Sample Export

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Single Sample Export Flow                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. User Action
   │
   └─► Click "Export" on sample in grid
       │
       ▼
2. Frontend
   │
   ├─► Open export modal
   ├─► User selects:
   │   ├─ Format (WAV/AIFF)
   │   ├─ Organization (flat/genre/BPM)
   │   └─ Options (metadata, sanitize)
   │
   └─► POST /api/v1/sp404/samples/123/export
       {
         "organize_by": "genre",
         "format": "wav",
         "include_metadata": true,
         "sanitize_filenames": true
       }
       │
       ▼
3. API Endpoint
   │
   └─► sp404_export.export_single_sample()
       │
       ▼
4. Service Layer
   │
   ├─► Get sample from database (id=123)
   │   Result: Sample(id=123, file_path="/uploads/1/abc.mp3", genre="hip-hop")
   │
   ├─► Validate sample
   │   ├─ Check file exists: ✓
   │   ├─ Check format supported: ✓ (MP3)
   │   ├─ Check duration >= 100ms: ✓ (4.5s)
   │   └─ Result: ValidationResult(valid=True)
   │
   ├─► Sanitize filename
   │   Input:  "Sick Beat (2024) 🔥.mp3"
   │   Output: "sick_beat_2024.wav"
   │
   ├─► Determine output path (genre organization)
   │   Base: /exports/
   │   Genre: hip-hop
   │   Output: /exports/hip-hop/sick_beat_2024.wav
   │
   ├─► Convert to SP-404 format
   │   │
   │   ├─► Load audio (librosa)
   │   │   y, sr = librosa.load("/uploads/1/abc.mp3", sr=None)
   │   │   Result: y.shape=(196608,), sr=44100
   │   │
   │   ├─► Resample to 48kHz
   │   │   y_48k = librosa.resample(y, orig_sr=44100, target_sr=48000)
   │   │   Result: y_48k.shape=(213504,)
   │   │
   │   └─► Write as 16-bit WAV (soundfile)
   │       sf.write("/exports/hip-hop/sick_beat_2024.wav", y_48k, 48000, subtype='PCM_16')
   │       Result: 854KB WAV file
   │
   ├─► Write metadata file (optional)
   │   File: /exports/hip-hop/sick_beat_2024_metadata.txt
   │   Content: Title, Genre, BPM, Key, Technical Details
   │
   ├─► Track in database
   │   Create: SP404Export(id=456, export_type="single", sample_count=1)
   │   Create: SP404ExportSample(export_id=456, sample_id=123)
   │
   └─► Return result
       ExportResult(
         success=True,
         sample_id=123,
         output_path="/exports/hip-hop",
         output_filename="sick_beat_2024.wav",
         format="wav",
         file_size_bytes=854016,
         conversion_time_seconds=2.3
       )
       │
       ▼
5. API Response
   │
   └─► 200 OK + ExportResult JSON
       │
       ▼
6. Frontend
   │
   ├─► Show success message
   ├─► Display download link
   └─► Update UI with export status
```

## Data Flow Diagram - Batch Export

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Batch Export Flow                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. User selects 10 samples in grid
   [Sample 1, Sample 2, ..., Sample 10]
   │
   ▼
2. POST /api/v1/sp404/samples/export-batch
   {
     "sample_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
     "config": {
       "organize_by": "bpm",
       "format": "wav"
     }
   }
   │
   ▼
3. Service: export_batch()
   │
   ├─► Create output directory: /exports/batch_789/
   │
   ├─► Process each sample (loop):
   │   │
   │   ├─► Sample 1 (BPM: 85)
   │   │   ├─ Organize: /exports/batch_789/70-90/
   │   │   ├─ Convert: sample_001.mp3 → sample_001.wav (48kHz/16-bit)
   │   │   └─ Result: ✓ Success (2.1s, 3.2MB)
   │   │
   │   ├─► Sample 2 (BPM: 120)
   │   │   ├─ Organize: /exports/batch_789/110-130/
   │   │   ├─ Convert: sample_002.wav → sample_002.wav
   │   │   └─ Result: ✓ Success (0.8s, 2.8MB) [already 48kHz]
   │   │
   │   ├─► Sample 3 (BPM: 140)
   │   │   ├─ Organize: /exports/batch_789/130-150/
   │   │   ├─ Convert: sample_003.mp3 → sample_003.wav
   │   │   └─ Result: ✓ Success (1.9s, 4.1MB)
   │   │
   │   ├─► Sample 4 (BPM: 95)
   │   │   ├─ Organize: /exports/batch_789/90-110/
   │   │   ├─ Convert: sample_004.flac → sample_004.wav
   │   │   └─ Result: ✓ Success (2.5s, 5.2MB)
   │   │
   │   ├─► Sample 5 (BPM: None)
   │   │   ├─ Organize: /exports/batch_789/unknown_bpm/
   │   │   ├─ Convert: sample_005.m4a → sample_005.wav
   │   │   └─ Result: ✓ Success (2.1s, 3.8MB)
   │   │
   │   ├─► Sample 6 (BPM: 128)
   │   │   ├─ Organize: /exports/batch_789/110-130/
   │   │   ├─ Validate: Duration 50ms < 100ms ✗
   │   │   └─ Result: ✗ Failed - "Duration too short"
   │   │
   │   ├─► Sample 7 (BPM: 100)
   │   │   ├─ Organize: /exports/batch_789/90-110/
   │   │   ├─ Convert: sample_007.wav → sample_007.wav
   │   │   └─ Result: ✓ Success (1.8s, 3.5MB)
   │   │
   │   ├─► Sample 8 (BPM: 75)
   │   │   ├─ Organize: /exports/batch_789/70-90/
   │   │   ├─ Convert: sample_008.mp3 → sample_008.wav
   │   │   └─ Result: ✓ Success (2.2s, 4.0MB)
   │   │
   │   ├─► Sample 9 (BPM: 160)
   │   │   ├─ Organize: /exports/batch_789/fast/
   │   │   ├─ Convert: sample_009.wav → sample_009.wav
   │   │   └─ Result: ✓ Success (1.5s, 2.9MB)
   │   │
   │   └─► Sample 10 (BPM: 110)
   │       ├─ Organize: /exports/batch_789/110-130/
   │       ├─ Convert: sample_010.aiff → sample_010.wav
   │       └─ Result: ✓ Success (1.9s, 3.7MB)
   │
   ├─► Create export record
   │   SP404Export(
   │     id=789,
   │     export_type="batch",
   │     sample_count=10,
   │     output_path="/exports/batch_789",
   │     organized_by="bpm",
   │     total_size_bytes=33200000,
   │     export_duration_seconds=18.8
   │   )
   │
   └─► Return batch result
       BatchExportResult(
         total_requested=10,
         successful=9,
         failed=1,
         total_size_bytes=33200000,
         total_time_seconds=18.8,
         output_base_path="/exports/batch_789",
         organized_by="bpm",
         results=[...],
         errors=["Sample 6: Duration too short"]
       )

4. Frontend displays:
   ┌──────────────────────────────────────┐
   │ Batch Export Complete                │
   ├──────────────────────────────────────┤
   │ ✓ 9 samples exported successfully    │
   │ ✗ 1 sample failed                    │
   │                                      │
   │ Total size: 31.7 MB                  │
   │ Time: 18.8 seconds                   │
   │                                      │
   │ Output: /exports/batch_789/          │
   │ Organization: By BPM                 │
   │                                      │
   │ [Download ZIP] [View Details]        │
   └──────────────────────────────────────┘
```

## Organization Structure Examples

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Export Organization Strategies                          │
└─────────────────────────────────────────────────────────────────────────────┘

Strategy 1: FLAT
────────────────
/exports/
  sample_001.wav
  sample_002.wav
  sample_003.wav
  sample_004.wav
  sample_005.wav

Use case: Simple export, all samples together


Strategy 2: BY GENRE
────────────────────
/exports/
  hip-hop/
    sample_001.wav
    sample_002.wav
    sample_005.wav
  jazz/
    sample_003.wav
  electronic/
    sample_004.wav
  unknown_genre/
    sample_006.wav

Use case: Organize by musical style


Strategy 3: BY BPM
──────────────────
/exports/
  70-90/
    sample_001.wav (85 BPM)
    sample_002.wav (88 BPM)
  90-110/
    sample_003.wav (95 BPM)
    sample_004.wav (102 BPM)
  110-130/
    sample_005.wav (120 BPM)
    sample_006.wav (128 BPM)
  fast/
    sample_007.wav (160 BPM)
  unknown_bpm/
    sample_008.wav (no BPM data)

Use case: Find samples by tempo


Strategy 4: KIT STRUCTURE
──────────────────────────
/exports/
  my_kit_name/
    bank_A/
      pad_01_kick.wav
      pad_02_snare.wav
      pad_03_hihat_closed.wav
      pad_04_hihat_open.wav
      ...
      pad_16_cymbal.wav
    bank_B/
      pad_01_bass_note_c.wav
      pad_02_bass_note_d.wav
      ...
    bank_C/
      pad_01_vocal_chop_01.wav
      ...
    bank_D/
      pad_01_synth_lead.wav
      ...

Use case: Ready for SP-404MK2 hardware loading
```

## Database Schema Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Database Entity Relationships                         │
└─────────────────────────────────────────────────────────────────────────────┘

User (1) ──────────► (M) SP404Export
  │                        │
  │                        │ (has many)
  │                        ▼
  │                   SP404ExportSample (M)
  │                        │
  │                        │ (references)
  │                        ▼
  └────────────────► Sample (M)
                       │
                       │ (organized into)
                       ▼
                    KitSample (M) ◄─────── Kit (M)
                                              ▲
                                              │
                                              │ (belongs to)
                                           User (1)

Table: SP404Export
──────────────────
id                      PK
user_id                 FK → users.id
export_type             "single" | "batch" | "kit"
sample_count            int
output_path             string
organized_by            "flat" | "genre" | "bpm" | "kit"
format                  "wav" | "aiff"
total_size_bytes        bigint
export_duration_seconds float
created_at              timestamp

Table: SP404ExportSample
─────────────────────────
id                      PK
export_id               FK → sp404_exports.id
sample_id               FK → samples.id
output_filename         string
output_subfolder        string (nullable)
conversion_successful   boolean
error_message           string (nullable)

Table: UserPreference (extended)
─────────────────────────────────
id                          PK (always 1)
...existing fields...
sp404_export_format         "wav" | "aiff"
sp404_default_organization  "flat" | "genre" | "bpm"
sp404_sanitize_filenames    boolean
sp404_include_metadata      boolean
sp404_export_base_path      string (nullable)


Query Examples:
───────────────

1. Get all exports by user:
   SELECT * FROM sp404_exports WHERE user_id = ? ORDER BY created_at DESC

2. Get samples in an export:
   SELECT s.* FROM samples s
   JOIN sp404_export_samples es ON s.id = es.sample_id
   WHERE es.export_id = ?

3. Get export history for a sample:
   SELECT e.* FROM sp404_exports e
   JOIN sp404_export_samples es ON e.id = es.export_id
   WHERE es.sample_id = ?

4. Get failed conversions:
   SELECT * FROM sp404_export_samples
   WHERE conversion_successful = FALSE
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Error Handling Strategy                            │
└─────────────────────────────────────────────────────────────────────────────┘

Validation Errors (422)
───────────────────────
Sample Not Found
  ├─► Check: Sample ID exists in database
  ├─► Return: 404 Not Found
  └─► Message: "Sample {id} not found"

File Not Found
  ├─► Check: File exists at sample.file_path
  ├─► Return: 422 Unprocessable Entity
  └─► Message: "Audio file not found: {path}"

Duration Too Short
  ├─► Check: Duration >= 100ms
  ├─► Return: 422 Unprocessable Entity
  └─► Message: "Duration too short: {ms}ms (minimum: 100ms)"

Unsupported Format
  ├─► Check: Extension in SUPPORTED_INPUT_FORMATS
  ├─► Return: 422 Unprocessable Entity
  └─► Message: "Unsupported format: {ext}"


Conversion Errors (422)
───────────────────────
Audio Loading Failed
  ├─► Librosa error: Can't decode file
  ├─► Return: 422 Unprocessable Entity
  └─► Message: "Failed to load audio: {error}"

Resampling Failed
  ├─► Librosa error: Out of memory / CPU timeout
  ├─► Retry: Once with lower quality
  ├─► Return: 422 Unprocessable Entity (if still fails)
  └─► Message: "Failed to resample audio: {error}"

File Write Failed
  ├─► Soundfile error: Permission denied / disk full
  ├─► Return: 500 Internal Server Error
  └─► Message: "Failed to write output file"


Batch Processing Errors
────────────────────────
Partial Failure
  ├─► Strategy: Continue processing remaining samples
  ├─► Collect: All errors in errors[] array
  ├─► Return: 200 OK with BatchExportResult
  └─► Result: {successful: 8, failed: 2, errors: [...]}

Complete Failure
  ├─► Strategy: Return early if critical error
  ├─► Return: 500 Internal Server Error
  └─► Message: "Batch export failed: {error}"


File System Errors (500)
────────────────────────
Permission Denied
  ├─► Check: Write access to output directory
  ├─► Fallback: Use temp directory
  └─► Log: Warning about permission issue

Disk Full
  ├─► Check: Available space before export
  ├─► Return: 507 Insufficient Storage
  └─► Message: "Not enough disk space for export"

Path Too Long
  ├─► Check: Path length < OS limit
  ├─► Sanitize: Shorten filename
  └─► Retry: With shorter path


Recovery Strategies
───────────────────
Validation Failure → Skip sample, continue batch
Conversion Failure → Retry once, then skip
File System Error → Try fallback location
Database Error    → Rollback, return error
Out of Memory     → Process in smaller chunks
```

This visual architecture document provides:
1. High-level system component diagram
2. Detailed data flow for single and batch exports
3. Organization strategy examples
4. Database schema relationships
5. Error handling flow

Use this alongside the main architecture document for complete system understanding.
