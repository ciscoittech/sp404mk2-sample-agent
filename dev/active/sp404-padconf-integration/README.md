# SP-404MK2 PADCONF Integration

**Status:** Planning Complete - Ready for Implementation
**Priority:** HIGH - Completes end-to-end workflow
**Estimated Effort:** 2-3 days

---

## Quick Links

- **Full Plan:** [sp404-padconf-integration-plan.md](./sp404-padconf-integration-plan.md)
- **PADCONF Spec:** https://github.com/gsterlin/sp404mk2-tools/blob/main/padconf/mk2_notes.txt
- **Reference Implementation:** https://github.com/gsterlin/sp404mk2-tools/blob/main/padconf/mk2_bpm_edit.py

---

## What We're Building

Complete SP-404MK2 project export system that generates hardware-ready projects with:

1. **PADCONF.BIN** - Binary configuration file (52,000 bytes)
2. **Converted Audio** - 48kHz/16-bit WAV/AIFF samples (already working)
3. **ZIP Package** - Ready to copy to SD card
4. **AI Integration** - Uses existing BPM/key/genre analysis

---

## User Flow

```
User clicks "Generate SP-404MK2 Project"
           ↓
System builds project:
  - Converts audio samples
  - Generates PADCONF.BIN with pad assignments
  - Creates ZIP archive
           ↓
User downloads ZIP
           ↓
User copies to SD card: /SP-404MKII/IMPORT/
           ↓
Hardware loads project with all samples ready to play
```

---

## Implementation Phases

### Phase 1: PADCONF Library (1 day)

**Goal:** Low-level binary file manipulation

**Deliverables:**
- `backend/app/services/padconf_service.py`
- `PadConfig` and `ProjectConfig` schemas
- Binary read/write methods
- Unit tests

**Key Challenge:** Byte-level accuracy (20+ parameters per pad)

---

### Phase 2: Project Builder (2 days)

**Goal:** User-facing project export feature

**Deliverables:**
- `backend/app/services/sp404_project_builder.py`
- API endpoint: `POST /api/v1/sp404/project/{kit_id}`
- Web UI templates
- Integration tests

**Key Challenge:** Orchestrating multiple services (audio export, PADCONF generation, ZIP creation)

---

## Technical Architecture

### New Services

```python
PadconfService
├── create_padconf()       # Generate 52KB binary
├── read_padconf()         # Parse existing file
├── _write_header()        # Project settings
├── _write_pad_metadata()  # Pad configuration
└── _write_pad_filename()  # Sample names

SP404ProjectBuilder
├── build_project()        # Main orchestration
├── _export_audio_samples() # Convert audio
├── _build_pad_configs()   # Map kit → PADCONF
├── _auto_detect_bpm()     # Intelligent defaults
└── _create_zip()          # Package for download
```

### Integration Points

```python
# Existing services we leverage
SP404ExportService    → Audio conversion
AudioFeaturesService  → BPM/key detection
KitService            → Kit data
SampleService         → Sample metadata

# New services we create
PadconfService        → Binary generation
SP404ProjectBuilder   → Orchestration
```

---

## PADCONF.BIN Format (Simplified)

```
File Size: 52,000 bytes

Header (160 bytes)
  - Project name
  - Project BPM
  - Bank BPMs (A-J)
  - Bank volumes

Pad Metadata (160 pads × 172 bytes)
  Each pad:
    - BPM value (2 bytes at offset +0x22)
    - Volume, pitch, pan
    - Loop settings
    - Effects routing
    - Envelope (attack, hold, release)

Filenames (160 pads × 24 bytes)
  - 23 characters max
  - Null-terminated ASCII
```

---

## Success Criteria

### Phase 1
- [ ] Binary is exactly 52,000 bytes
- [ ] BPM encoded correctly (9000 = 90.00 BPM)
- [ ] Round-trip test passes (write → read → verify)
- [ ] 3-5 unit tests passing

### Phase 2
- [ ] API returns valid ZIP file
- [ ] ZIP contains PADCONF.BIN + audio samples
- [ ] Pad assignments match kit configuration
- [ ] BPM auto-detection works
- [ ] Web UI displays success/download link
- [ ] 3-5 integration tests passing

---

## Risks & Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Binary format bugs | MEDIUM | Reference implementation, comprehensive tests |
| Hardware compatibility | MEDIUM | Test with actual SP-404MK2, collect user feedback |
| Sample offset rules | LOW | Use conservative defaults, iterate based on feedback |

---

## Timeline

| Phase | Hours | Days |
|-------|-------|------|
| Phase 1: PADCONF Library | 8h | 1 day |
| Phase 2: Project Builder | 14.5h | 2 days |
| **Total** | **22.5h** | **2-3 days** |

---

## Next Steps

1. Review full plan: [sp404-padconf-integration-plan.md](./sp404-padconf-integration-plan.md)
2. Confirm approach and timeline
3. Begin Phase 1 implementation
4. Test with actual hardware (if available)
5. Release MVP

---

## Resources

- **gsterlin/sp404mk2-tools:** Complete PADCONF reverse engineering
- **Existing Export Service:** `/backend/app/services/sp404_export_service.py`
- **Kit System:** `/backend/app/models/kit.py`
- **Audio Features:** `/backend/app/services/audio_features_service.py`

---

**Ready for implementation approval.**
