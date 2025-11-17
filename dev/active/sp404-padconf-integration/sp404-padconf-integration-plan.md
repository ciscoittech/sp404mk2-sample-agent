# SP-404MK2 PADCONF.BIN Integration Plan

**Status:** Planning Complete - Ready for Implementation
**Estimated Effort:** 2-3 days (MVP)
**Last Updated:** 2025-11-17
**Feature Priority:** HIGH - Completes end-to-end SP-404MK2 workflow

---

## Executive Summary

We will integrate **PADCONF.BIN generation** into the SP404MK2 Sample Agent to provide complete, hardware-ready project exports. This feature builds on the existing export service (which already converts audio to 48kHz/16-bit) by adding the binary configuration file that the SP-404MK2 hardware requires to load samples into its pad banks.

**What we're building:**
A complete SP-404MK2 project export system that generates downloadable ZIP files containing:
1. Converted audio samples (48kHz/16-bit WAV/AIFF) - **ALREADY WORKING**
2. PADCONF.BIN binary configuration file - **NEW**
3. Proper folder structure for SD card import - **NEW**
4. Intelligent pad assignments using AI-analyzed sample data - **NEW**

**Why it's valuable:**
- **One-click workflow:** Users go from sample discovery to hardware-ready project with zero manual file editing
- **AI-powered defaults:** Automatically sets BPM, volume, and pitch based on analysis data
- **Professional quality:** Generates binary files that match hardware manufacturer specifications
- **Complete integration:** Leverages existing AI analysis (BPM, key, genre, vibe) for intelligent pad configuration

**Expected timeline:**
- **Phase 1 (PADCONF Library):** 1 day
- **Phase 2 (Project Builder):** 1-2 days
- **Total MVP:** 2-3 days

---

## Architecture Design

### 1. PADCONF.BIN File Format Overview

**Source:** [gsterlin/sp404mk2-tools](https://github.com/gsterlin/sp404mk2-tools/blob/main/padconf/mk2_notes.txt)

**File Structure:**
```
Total Size: 52,000 bytes
├── Header (160 bytes)
│   ├── Bank tempo settings
│   ├── Bank volumes (A-J, 10 banks)
│   ├── Project BPM
│   └── Project name (null-terminated string)
├── Pad Metadata (160 pads × 172 bytes = 27,520 bytes)
│   ├── Sample start/end positions
│   ├── BPM value (2 bytes, e.g., 9000 = 90.00 BPM)
│   ├── Volume, pitch, pan settings
│   ├── Loop mode and points
│   ├── Gate, mute groups
│   ├── Effects routing
│   └── Envelope (attack, hold, release)
└── Filenames (160 pads × 24 bytes = 3,840 bytes)
    └── 23-character limit, null-terminated
```

### 2. Byte-Level Specification

#### Header Structure (Bytes 0-159)

| Offset | Length | Parameter | Format | Notes |
|--------|--------|-----------|--------|-------|
| 0x0012 | 1 | Tempo Mode | 0x00=Bank, 0x01=Project | |
| 0x0013-0x0014 | 2 | Project BPM | Decimal (9000=90.00) | Big-endian |
| 0x0041-0x0044 | 4 | Bank A BPM | Decimal/2 (18500=92.50) | |
| 0x0045-0x0048 | 4 | Bank B BPM | Decimal/2 | |
| ... | | Banks C-J | Same pattern | 10 banks total |
| 0x006D-0x006E | 2 | Bank B Volume | 0x00-0x7F | |
| 0x006F-0x0070 | 2 | Bank A Volume | 0x00-0x7F | |
| ... | | Banks C-J Volume | Same pattern | |
| 0x0081-0x00A0 | 32 | Project Name | Null-terminated string | |

#### Pad Metadata (172 bytes per pad)

**Formula:** `byte_offset = 0xA5 + ((pad_index - 1) * 172)`

| Offset | Length | Parameter | Format | Range | Notes |
|--------|--------|-----------|--------|-------|-------|
| +0x00 | 4 | Sample Start | Integer | 0-max | 1 pos = 4 value change (stereo) |
| +0x04 | 4 | Sample End | Integer | 0-max | Follows 512/872 offset rules |
| +0x08 | 4 | Volume | Integer | 0x00-0x7F | Pitch/Speed page setting |
| +0x0C | 4 | Gate | Boolean | 0x00000001=On | |
| +0x10 | 4 | Loop | Boolean | 0x7FFFFFFF=On | 0x00000000=Off |
| +0x18 | 4 | Mute Group | Integer | 0x00-0xFF | 0x00=None, 0x01=Group A |
| +0x1C | 4 | BPM Sync | Boolean | 0x00000001=On | |
| +0x22 | 2 | BPM Value | Integer | 9000=90.00 | **Key field** |
| +0x24 | 4 | One Shot Mode | Flags | 0x20=Gate blink | 0x02=Vari Backing |
| +0x28 | 4 | Loop Point | Integer | Offset from start | |
| +0x30 | 4 | Pitch | Integer | 0x0C=+12 semi | |
| +0x34 | 4 | Fine Tune | Integer | 0x03=+0.03 | |
| +0x38 | 4 | Loop Mode | Integer | 0x01=Loop, 0x02=Ping-Pong | |
| +0x3C | 4 | Speed | Integer | 0x2710=100% | 0x1388=50% |
| +0x40 | 4 | Vinyl Effect | Boolean | 0x01=On | |
| +0x44 | 4 | Pan | Integer | 0x40=Center | 0x41=R1 |
| +0x48 | 4 | Pad Link | Integer | 0x01=A, 0x02=B | |
| +0x4C | 4 | Bus Route | Integer | 0x00=Dry, 0x01=Bus1 | |
| +0x54 | 4 | Attack | Integer | 0x00-0x7F | Envelope |
| +0x58 | 4 | Hold | Integer | 0x00-0x7F | Envelope |
| +0x5C | 4 | Release | Integer | 0x00-0x7F | Envelope |

#### Filenames Section

**Formula:** `byte_offset = 0x6C20 + ((pad_index - 1) * 24)`

| Offset | Length | Parameter | Format |
|--------|--------|-----------|--------|
| Variable | 24 | Filename | Null-terminated ASCII (23 char max) |

### 3. New Services Architecture

```
backend/app/services/
├── padconf_service.py          # NEW - Core PADCONF binary manipulation
└── sp404_project_builder.py   # NEW - Orchestrates complete project export
```

**Integration Points:**

```python
# Existing services that provide data
AudioFeaturesService    → BPM, key, spectral features
OpenRouterService       → AI vibe analysis
SP404ExportService      → Audio conversion (48kHz/16-bit)
KitService              → Kit and pad assignment data

# New service dependencies
PadconfService          → Binary PADCONF.BIN generation
SP404ProjectBuilder     → Coordinates all services above
```

### 4. Data Flow Diagram

```
User: "Export Kit to SP-404MK2 Project"
           ↓
┌──────────────────────────────────────┐
│   API: POST /api/v1/sp404/project   │
│   Endpoint: sp404_export.py          │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│   SP404ProjectBuilder                │
│   - Fetches kit data                 │
│   - Fetches samples + analysis       │
│   - Coordinates services             │
└──────────────────────────────────────┘
           ↓
     ┌────┴─────┬──────────────┬─────────────┐
     ↓          ↓              ↓             ↓
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Audio   │ │ Padconf  │ │ Kit      │ │ Sample   │
│ Export  │ │ Service  │ │ Service  │ │ Service  │
└─────────┘ └──────────┘ └──────────┘ └──────────┘
     │          │              │             │
     │          │              │             │
     ↓          ↓              ↓             ↓
┌─────────────────────────────────────────────┐
│          File System Output                 │
│  /tmp/sp404_projects/kit_name/              │
│  ├── PADCONF.BIN                            │
│  ├── sample_001.wav                         │
│  ├── sample_002.wav                         │
│  └── ...                                    │
└─────────────────────────────────────────────┘
     │
     ↓
┌─────────────────────────────────────────────┐
│   ZIP Archive Creation                      │
│   sp404_project_kit_name.zip                │
└─────────────────────────────────────────────┘
     │
     ↓
   User Download
```

### 5. API Contracts

#### New Endpoint: Generate Project

```python
POST /api/v1/sp404/project/{kit_id}

Request Body:
{
    "format": "wav",                    # or "aiff"
    "project_name": "My Beat Kit",      # Optional, defaults to kit name
    "project_bpm": 90.0,                # Optional, auto-detected from samples
    "tempo_mode": "project",            # or "bank"
    "include_metadata": true,
    "pad_defaults": {                   # Optional pad-level defaults
        "volume": 100,                  # 0-127
        "gate": true,
        "loop": false,
        "bpm_sync": false
    }
}

Response:
{
    "success": true,
    "project_id": 42,
    "kit_id": 10,
    "kit_name": "Dusty Drums",
    "sample_count": 16,
    "project_name": "My Beat Kit",
    "project_bpm": 90.0,
    "output_path": "/tmp/sp404_projects/my_beat_kit",
    "download_url": "/api/v1/sp404/project/42/download",
    "file_size_bytes": 15728640,
    "generation_time_seconds": 3.5,
    "files": [
        "PADCONF.BIN",
        "sample_001.wav",
        "sample_002.wav",
        ...
    ]
}
```

#### Existing Endpoint: Modified Kit Export

```python
# Extend existing export_kit endpoint
POST /api/v1/sp404/kits/{kit_id}/export

# Add new field to ExportConfig schema:
{
    "format": "wav",
    "organize_by": "kit",
    "include_padconf": true,        # NEW - Generate PADCONF.BIN
    "padconf_options": {            # NEW - Optional configuration
        "project_name": "...",
        "project_bpm": 90.0
    }
}
```

---

## Phase 1: PADCONF Library (Core Infrastructure)

### File: `backend/app/services/padconf_service.py`

**Purpose:** Low-level PADCONF.BIN binary file manipulation

**Classes:**

```python
class PadConfig(BaseModel):
    """Configuration for a single pad (Pydantic schema)"""
    pad_index: int = Field(..., ge=1, le=160)
    filename: str = Field(..., max_length=23)

    # Audio properties
    sample_start: int = 0
    sample_end: int = 0
    volume: int = Field(100, ge=0, le=127)

    # Playback
    bpm: Optional[float] = None
    pitch: int = Field(0, ge=-12, le=12)
    fine_tune: int = Field(0, ge=-50, le=50)
    speed: int = Field(10000, ge=5000, le=20000)  # 10000 = 100%

    # Switches
    gate: bool = False
    loop: bool = False
    bpm_sync: bool = False
    vinyl_effect: bool = False

    # Loop settings
    loop_point: int = 0
    loop_mode: int = 0  # 0=Off, 1=Loop, 2=Ping-Pong

    # Routing
    pan: int = Field(64, ge=0, le=127)  # 64 = center
    mute_group: int = Field(0, ge=0, le=255)
    pad_link: int = Field(0, ge=0, le=2)  # 0=None, 1=A, 2=B
    bus_route: int = Field(0, ge=0, le=2)  # 0=Dry, 1=Bus1, 2=Bus2

    # Envelope
    attack: int = Field(0, ge=0, le=127)
    hold: int = Field(0, ge=0, le=127)
    release: int = Field(0, ge=0, le=127)

    # Advanced
    one_shot_mode: int = 0


class ProjectConfig(BaseModel):
    """Global project configuration"""
    project_name: str = Field("Untitled", max_length=31)
    project_bpm: float = Field(120.0, ge=20.0, le=300.0)
    tempo_mode: str = Field("project", pattern="^(project|bank)$")

    # Bank settings (10 banks: A-J)
    bank_bpms: Dict[str, float] = Field(default_factory=dict)
    bank_volumes: Dict[str, int] = Field(default_factory=dict)


class PadconfService:
    """Service for reading/writing PADCONF.BIN files"""

    # Constants
    FILE_SIZE = 52000
    HEADER_SIZE = 160
    PAD_METADATA_SIZE = 172
    PAD_FILENAME_SIZE = 24
    PAD_COUNT = 160

    # Byte offsets
    HEADER_TEMPO_MODE = 0x12
    HEADER_PROJECT_BPM = 0x13
    HEADER_PROJECT_NAME = 0x81

    PAD_METADATA_START = 0xA5
    PAD_FILENAME_START = 0x6C20

    def __init__(self):
        """Initialize service"""
        pass

    def create_padconf(
        self,
        project_config: ProjectConfig,
        pad_configs: List[PadConfig]
    ) -> bytes:
        """
        Create PADCONF.BIN binary data from configuration.

        Args:
            project_config: Global project settings
            pad_configs: List of pad configurations (0-160 pads)

        Returns:
            52,000 bytes of PADCONF.BIN data
        """
        # Initialize 52KB buffer with zeros
        buffer = bytearray(self.FILE_SIZE)

        # Write header
        self._write_header(buffer, project_config)

        # Write pad metadata
        for pad_config in pad_configs:
            self._write_pad_metadata(buffer, pad_config)

        # Write filenames
        for pad_config in pad_configs:
            self._write_pad_filename(buffer, pad_config)

        return bytes(buffer)

    def _write_header(
        self,
        buffer: bytearray,
        config: ProjectConfig
    ) -> None:
        """Write header section (bytes 0-159)"""
        # Tempo mode (0x12)
        buffer[self.HEADER_TEMPO_MODE] = 0x01 if config.tempo_mode == "project" else 0x00

        # Project BPM (0x13-0x14, big-endian)
        bpm_int = int(config.project_bpm * 100)  # 90.00 → 9000
        buffer[self.HEADER_PROJECT_BPM:self.HEADER_PROJECT_BPM+2] = \
            bpm_int.to_bytes(2, 'big')

        # Bank BPMs (0x41-0x68)
        bank_offsets = {
            'A': 0x41, 'B': 0x45, 'C': 0x49, 'D': 0x4D, 'E': 0x51,
            'F': 0x55, 'G': 0x59, 'H': 0x5D, 'I': 0x61, 'J': 0x65
        }
        for bank, offset in bank_offsets.items():
            bpm = config.bank_bpms.get(bank, config.project_bpm)
            bpm_value = int(bpm * 100) * 2  # Div by 2 rule
            buffer[offset:offset+4] = bpm_value.to_bytes(4, 'big')

        # Bank volumes (0x6D-0x80, interleaved pattern)
        volume_offsets = {
            'B': 0x6D, 'A': 0x6F, 'D': 0x71, 'C': 0x73, 'F': 0x75,
            'E': 0x77, 'H': 0x79, 'G': 0x7B, 'J': 0x7D, 'I': 0x7F
        }
        for bank, offset in volume_offsets.items():
            volume = config.bank_volumes.get(bank, 127)
            buffer[offset:offset+2] = volume.to_bytes(2, 'big')

        # Project name (0x81-0xA0, null-terminated)
        name_bytes = config.project_name.encode('ascii', errors='ignore')[:31]
        buffer[self.HEADER_PROJECT_NAME:self.HEADER_PROJECT_NAME+len(name_bytes)] = name_bytes
        buffer[self.HEADER_PROJECT_NAME+len(name_bytes)] = 0x00  # Null terminator

    def _write_pad_metadata(
        self,
        buffer: bytearray,
        pad: PadConfig
    ) -> None:
        """Write single pad metadata (172 bytes)"""
        offset = self.PAD_METADATA_START + ((pad.pad_index - 1) * self.PAD_METADATA_SIZE)

        # Sample start/end (0x00-0x07)
        buffer[offset:offset+4] = pad.sample_start.to_bytes(4, 'big')
        buffer[offset+4:offset+8] = pad.sample_end.to_bytes(4, 'big')

        # Volume (0x08-0x0B)
        buffer[offset+8:offset+12] = pad.volume.to_bytes(4, 'big')

        # Gate (0x0C-0x0F)
        buffer[offset+12:offset+16] = (1 if pad.gate else 0).to_bytes(4, 'big')

        # Loop (0x10-0x13)
        loop_value = 0x7FFFFFFF if pad.loop else 0x00000000
        buffer[offset+16:offset+20] = loop_value.to_bytes(4, 'big')

        # Mute group (0x18-0x1B)
        buffer[offset+24:offset+28] = pad.mute_group.to_bytes(4, 'big')

        # BPM sync (0x1C-0x1F)
        buffer[offset+28:offset+32] = (1 if pad.bpm_sync else 0).to_bytes(4, 'big')

        # BPM value (0x22-0x23) - KEY FIELD
        if pad.bpm:
            bpm_int = int(pad.bpm * 100)
            buffer[offset+34:offset+36] = bpm_int.to_bytes(2, 'big')

        # Loop point (0x28-0x2B)
        buffer[offset+40:offset+44] = pad.loop_point.to_bytes(4, 'big')

        # Pitch (0x30-0x33)
        buffer[offset+48:offset+52] = pad.pitch.to_bytes(4, 'big')

        # Fine tune (0x34-0x37)
        buffer[offset+52:offset+56] = pad.fine_tune.to_bytes(4, 'big')

        # Loop mode (0x38-0x3B)
        buffer[offset+56:offset+60] = pad.loop_mode.to_bytes(4, 'big')

        # Speed (0x3C-0x3F)
        buffer[offset+60:offset+64] = pad.speed.to_bytes(4, 'big')

        # Vinyl effect (0x40-0x43)
        buffer[offset+64:offset+68] = (1 if pad.vinyl_effect else 0).to_bytes(4, 'big')

        # Pan (0x44-0x47)
        buffer[offset+68:offset+72] = pad.pan.to_bytes(4, 'big')

        # Pad link (0x48-0x4B)
        buffer[offset+72:offset+76] = pad.pad_link.to_bytes(4, 'big')

        # Bus route (0x4C-0x4F)
        buffer[offset+76:offset+80] = pad.bus_route.to_bytes(4, 'big')

        # Envelope (0x54-0x5F)
        buffer[offset+84:offset+88] = pad.attack.to_bytes(4, 'big')
        buffer[offset+88:offset+92] = pad.hold.to_bytes(4, 'big')
        buffer[offset+92:offset+96] = pad.release.to_bytes(4, 'big')

    def _write_pad_filename(
        self,
        buffer: bytearray,
        pad: PadConfig
    ) -> None:
        """Write pad filename (24 bytes, null-terminated)"""
        offset = self.PAD_FILENAME_START + ((pad.pad_index - 1) * self.PAD_FILENAME_SIZE)

        # Sanitize and encode filename
        filename_bytes = pad.filename.encode('ascii', errors='ignore')[:23]
        buffer[offset:offset+len(filename_bytes)] = filename_bytes
        buffer[offset+len(filename_bytes)] = 0x00  # Null terminator

    def read_padconf(self, file_path: Path) -> tuple[ProjectConfig, List[PadConfig]]:
        """
        Read PADCONF.BIN file and parse into configuration objects.

        Args:
            file_path: Path to PADCONF.BIN file

        Returns:
            Tuple of (ProjectConfig, List[PadConfig])
        """
        with open(file_path, 'rb') as f:
            data = f.read()

        if len(data) != self.FILE_SIZE:
            raise ValueError(f"Invalid PADCONF.BIN size: {len(data)} (expected {self.FILE_SIZE})")

        # Parse header
        project_config = self._read_header(data)

        # Parse pad metadata
        pad_configs = []
        for i in range(1, self.PAD_COUNT + 1):
            pad_config = self._read_pad_metadata(data, i)
            pad_config.filename = self._read_pad_filename(data, i)
            pad_configs.append(pad_config)

        return project_config, pad_configs

    def _read_header(self, data: bytes) -> ProjectConfig:
        """Parse header section"""
        # Implementation similar to _write_header but reversed
        pass

    def _read_pad_metadata(self, data: bytes, pad_index: int) -> PadConfig:
        """Parse single pad metadata"""
        # Implementation similar to _write_pad_metadata but reversed
        pass

    def _read_pad_filename(self, data: bytes, pad_index: int) -> str:
        """Parse pad filename"""
        # Implementation similar to _write_pad_filename but reversed
        pass
```

### Integration with Existing Services

```python
# Use existing SP404ExportService for filename sanitization
from app.services.sp404_export_service import SP404ExportService

# In PadconfService:
def sanitize_filename_for_pad(self, filename: str) -> str:
    """Use existing sanitization logic"""
    export_service = SP404ExportService(None)
    return export_service.sanitize_filename(filename)
```

### Testing Approach (MVP-Level)

**File:** `backend/tests/test_padconf_service.py`

```python
import pytest
from pathlib import Path
from app.services.padconf_service import PadconfService, PadConfig, ProjectConfig


def test_create_empty_padconf():
    """Test creating minimal PADCONF.BIN file"""
    service = PadconfService()

    project = ProjectConfig(
        project_name="Test Kit",
        project_bpm=90.0,
        tempo_mode="project"
    )

    data = service.create_padconf(project, [])

    assert len(data) == 52000
    assert data[0x12] == 0x01  # Project tempo mode


def test_write_single_pad():
    """Test writing single pad with BPM"""
    service = PadconfService()

    project = ProjectConfig(project_name="Test", project_bpm=120.0)

    pad = PadConfig(
        pad_index=1,
        filename="kick.wav",
        bpm=90.0,
        volume=100
    )

    data = service.create_padconf(project, [pad])

    # Verify BPM at correct offset (0xA5 + 0x22)
    bpm_offset = 0xA5 + 0x22
    bpm_value = int.from_bytes(data[bpm_offset:bpm_offset+2], 'big')
    assert bpm_value == 9000  # 90.00 BPM

    # Verify filename at 0x6C20
    filename_offset = 0x6C20
    filename = data[filename_offset:filename_offset+8].decode('ascii').rstrip('\x00')
    assert filename == "kick.wav"


def test_round_trip():
    """Test write → read → verify consistency"""
    service = PadconfService()

    # Create test data
    original_project = ProjectConfig(project_name="Round Trip Test", project_bpm=140.0)
    original_pads = [
        PadConfig(pad_index=1, filename="sample1.wav", bpm=120.0),
        PadConfig(pad_index=2, filename="sample2.wav", bpm=130.0)
    ]

    # Write
    data = service.create_padconf(original_project, original_pads)

    # Save to temp file
    temp_file = Path("/tmp/test_padconf.bin")
    temp_file.write_bytes(data)

    # Read
    read_project, read_pads = service.read_padconf(temp_file)

    # Verify
    assert read_project.project_name == "Round Trip Test"
    assert read_project.project_bpm == 140.0
    assert len(read_pads) == 160  # Always 160 pads
    assert read_pads[0].bpm == 120.0
    assert read_pads[1].bpm == 130.0

    # Cleanup
    temp_file.unlink()
```

### Hour Estimates - Phase 1

| Task | Hours | Notes |
|------|-------|-------|
| Create `PadConfig` schema | 0.5 | Pydantic models |
| Create `ProjectConfig` schema | 0.5 | Pydantic models |
| Implement `_write_header()` | 1.0 | Binary format complexity |
| Implement `_write_pad_metadata()` | 2.0 | Most complex, 20+ fields |
| Implement `_write_pad_filename()` | 0.5 | Simple |
| Implement `create_padconf()` | 0.5 | Orchestration |
| Implement `_read_header()` | 0.5 | Reverse of write |
| Implement `_read_pad_metadata()` | 1.0 | Reverse of write |
| Implement `_read_pad_filename()` | 0.5 | Reverse of write |
| Write unit tests | 1.5 | 3-5 basic tests |
| **Total Phase 1** | **8 hours** | **~1 day** |

---

## Phase 2: Project Builder (User-Facing Feature)

### File: `backend/app/services/sp404_project_builder.py`

**Purpose:** Orchestrates complete project export (audio + PADCONF.BIN)

```python
from pathlib import Path
from typing import List, Optional
import zipfile
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.kit import Kit, KitSample
from app.models.sample import Sample
from app.services.padconf_service import PadconfService, PadConfig, ProjectConfig
from app.services.sp404_export_service import SP404ExportService
from app.schemas.sp404_export import ExportConfig


logger = logging.getLogger(__name__)


class SP404ProjectBuilder:
    """
    Build complete SP-404MK2 projects with audio + PADCONF.BIN.

    Orchestrates:
    - Audio conversion (via SP404ExportService)
    - PADCONF.BIN generation (via PadconfService)
    - ZIP packaging for download
    """

    def __init__(self, db: AsyncSession):
        """Initialize with database session"""
        self.db = db
        self.padconf_service = PadconfService()
        self.export_service = SP404ExportService(db)

    async def build_project(
        self,
        kit_id: int,
        project_name: Optional[str] = None,
        project_bpm: Optional[float] = None,
        format: str = "wav",
        output_base: Optional[Path] = None
    ) -> "ProjectBuildResult":
        """
        Build complete SP-404MK2 project from kit.

        Args:
            kit_id: Database ID of kit to export
            project_name: Optional project name (defaults to kit name)
            project_bpm: Optional project BPM (auto-detected if not provided)
            format: Audio format (wav or aiff)
            output_base: Base directory for output

        Returns:
            ProjectBuildResult with paths and metadata
        """
        # 1. Fetch kit data
        kit = await self._get_kit(kit_id)
        kit_samples = await self._get_kit_samples(kit_id)

        if not kit_samples:
            raise ValueError(f"Kit {kit_id} has no samples")

        # 2. Determine project settings
        proj_name = project_name or self.export_service.sanitize_filename(kit.name)
        proj_bpm = project_bpm or await self._auto_detect_bpm(kit_samples)

        # 3. Create output directory
        output_base = output_base or Path("/tmp/sp404_projects")
        project_dir = output_base / proj_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # 4. Export audio samples
        audio_files = await self._export_audio_samples(
            kit_samples,
            project_dir,
            format
        )

        # 5. Build pad configurations from kit data
        pad_configs = await self._build_pad_configs(
            kit_samples,
            audio_files
        )

        # 6. Generate PADCONF.BIN
        project_config = ProjectConfig(
            project_name=proj_name,
            project_bpm=proj_bpm,
            tempo_mode="project"
        )

        padconf_data = self.padconf_service.create_padconf(
            project_config,
            pad_configs
        )

        # 7. Write PADCONF.BIN to disk
        padconf_path = project_dir / "PADCONF.BIN"
        padconf_path.write_bytes(padconf_data)

        logger.info(f"Generated PADCONF.BIN: {padconf_path}")

        # 8. Create manifest file (optional metadata)
        manifest_path = project_dir / "PROJECT_INFO.txt"
        self._write_manifest(manifest_path, kit, pad_configs, project_config)

        # 9. Create ZIP archive
        zip_path = await self._create_zip(project_dir, proj_name)

        # Import here to avoid circular dependency
        from app.schemas.sp404_project import ProjectBuildResult

        return ProjectBuildResult(
            success=True,
            kit_id=kit_id,
            kit_name=kit.name,
            project_name=proj_name,
            project_bpm=proj_bpm,
            sample_count=len(pad_configs),
            output_path=str(project_dir),
            padconf_path=str(padconf_path),
            zip_path=str(zip_path),
            file_size_bytes=zip_path.stat().st_size
        )

    async def _get_kit(self, kit_id: int) -> Kit:
        """Fetch kit from database"""
        stmt = select(Kit).where(Kit.id == kit_id)
        result = await self.db.execute(stmt)
        kit = result.scalar_one_or_none()

        if not kit:
            raise ValueError(f"Kit {kit_id} not found")

        return kit

    async def _get_kit_samples(self, kit_id: int) -> List[tuple[KitSample, Sample]]:
        """Fetch kit samples with pad assignments"""
        stmt = (
            select(KitSample, Sample)
            .join(Sample, KitSample.sample_id == Sample.id)
            .where(KitSample.kit_id == kit_id)
            .order_by(KitSample.pad_bank, KitSample.pad_number)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def _auto_detect_bpm(
        self,
        kit_samples: List[tuple[KitSample, Sample]]
    ) -> float:
        """Auto-detect project BPM from samples"""
        bpms = [sample.bpm for _, sample in kit_samples if sample.bpm]

        if not bpms:
            return 120.0  # Default BPM

        # Use median BPM to avoid outliers
        import statistics
        return statistics.median(bpms)

    async def _export_audio_samples(
        self,
        kit_samples: List[tuple[KitSample, Sample]],
        output_dir: Path,
        format: str
    ) -> dict[int, Path]:
        """
        Export all audio samples to output directory.

        Returns:
            Dict mapping sample_id → output_path
        """
        audio_files = {}

        for kit_sample, sample in kit_samples:
            # Generate filename: pad_XX_samplename.wav
            base_name = Path(sample.file_path).stem
            sanitized_name = self.export_service.sanitize_filename(base_name)

            # Calculate global pad index (1-160)
            bank_index = ord(kit_sample.pad_bank) - ord('A')  # A=0, B=1, etc.
            pad_index = (bank_index * 16) + kit_sample.pad_number

            filename = f"pad_{pad_index:03d}_{sanitized_name}.{format}"
            output_path = output_dir / filename

            # Convert audio
            conversion = await self.export_service.convert_to_sp404_format(
                Path(sample.file_path),
                output_path,
                format
            )

            if conversion.success:
                audio_files[sample.id] = output_path
                logger.info(f"Exported: {filename}")
            else:
                logger.error(f"Failed to export {filename}: {conversion.error_message}")

        return audio_files

    async def _build_pad_configs(
        self,
        kit_samples: List[tuple[KitSample, Sample]],
        audio_files: dict[int, Path]
    ) -> List[PadConfig]:
        """
        Build PadConfig objects from kit samples + AI analysis.

        Uses existing data:
        - BPM from audio_features or AI analysis
        - Volume from kit_sample.volume
        - Pitch from kit_sample.pitch_shift
        """
        pad_configs = []

        for kit_sample, sample in kit_samples:
            if sample.id not in audio_files:
                continue  # Skip failed exports

            # Calculate global pad index (1-160)
            bank_index = ord(kit_sample.pad_bank) - ord('A')
            pad_index = (bank_index * 16) + kit_sample.pad_number

            # Get filename
            filename = audio_files[sample.id].name

            # Build pad config with intelligent defaults
            pad_config = PadConfig(
                pad_index=pad_index,
                filename=filename,

                # From AI analysis
                bpm=sample.bpm,

                # From kit assignment
                volume=int(kit_sample.volume * 127),  # Convert 0-1 to 0-127
                pitch=kit_sample.pitch_shift,

                # Intelligent defaults based on sample type
                gate=False,  # Default off
                loop=self._should_loop(sample),
                bpm_sync=self._should_bpm_sync(sample),

                # Standard defaults
                pan=64,  # Center
                speed=10000,  # 100%
            )

            pad_configs.append(pad_config)

        return pad_configs

    def _should_loop(self, sample: Sample) -> bool:
        """Determine if sample should loop by default"""
        # Loop if tagged as "loop" or if genre suggests looping
        if sample.tags:
            tags_lower = [t.lower() for t in sample.tags]
            if 'loop' in tags_lower or 'ambient' in tags_lower:
                return True

        # Loop if duration > 10 seconds (likely a loop/backing track)
        if sample.duration and sample.duration > 10.0:
            return True

        return False

    def _should_bpm_sync(self, sample: Sample) -> bool:
        """Determine if sample should have BPM sync enabled"""
        # Enable BPM sync if sample has detected BPM
        if sample.bpm and sample.bpm > 0:
            return True

        return False

    def _write_manifest(
        self,
        manifest_path: Path,
        kit: Kit,
        pad_configs: List[PadConfig],
        project_config: ProjectConfig
    ) -> None:
        """Write human-readable project manifest"""
        lines = [
            "# SP-404MK2 Project Manifest",
            "",
            f"Project Name: {project_config.project_name}",
            f"Project BPM: {project_config.project_bpm}",
            f"Source Kit: {kit.name}",
            f"Total Pads: {len(pad_configs)}",
            "",
            "## Pad Assignments",
            ""
        ]

        for pad in sorted(pad_configs, key=lambda p: p.pad_index):
            bank = chr(ord('A') + ((pad.pad_index - 1) // 16))
            pad_num = ((pad.pad_index - 1) % 16) + 1

            lines.append(
                f"Pad {pad.pad_index:03d} (Bank {bank}, Pad {pad_num:02d}): "
                f"{pad.filename} - BPM: {pad.bpm or 'N/A'}"
            )

        manifest_path.write_text('\n'.join(lines))

    async def _create_zip(self, project_dir: Path, project_name: str) -> Path:
        """Create ZIP archive of project"""
        zip_path = project_dir.parent / f"{project_name}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in project_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(project_dir.parent)
                    zf.write(file, arcname)

        logger.info(f"Created ZIP: {zip_path} ({zip_path.stat().st_size} bytes)")

        return zip_path
```

### New Schema: `backend/app/schemas/sp404_project.py`

```python
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectBuildRequest(BaseModel):
    """Request schema for building SP-404MK2 project"""
    project_name: Optional[str] = Field(None, description="Custom project name")
    project_bpm: Optional[float] = Field(None, ge=20.0, le=300.0, description="Project BPM")
    format: str = Field("wav", pattern="^(wav|aiff)$")
    tempo_mode: str = Field("project", pattern="^(project|bank)$")
    include_metadata: bool = Field(True, description="Include PROJECT_INFO.txt")


class ProjectBuildResult(BaseModel):
    """Result of project build operation"""
    success: bool
    kit_id: int
    kit_name: str
    project_name: str
    project_bpm: float
    sample_count: int
    output_path: str
    padconf_path: str
    zip_path: str
    file_size_bytes: int
    generation_time_seconds: float = 0.0
```

### API Endpoint: `backend/app/api/v1/endpoints/sp404_export.py`

**Add new endpoint:**

```python
@router.post("/project/{kit_id}", response_model=ProjectBuildResult)
async def generate_sp404_project(
    kit_id: int,
    request_data: ProjectBuildRequest,
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate complete SP-404MK2 project with PADCONF.BIN.

    Creates downloadable ZIP containing:
    - PADCONF.BIN (binary configuration)
    - Converted audio samples (48kHz/16-bit)
    - PROJECT_INFO.txt (manifest)

    Ready to copy to SD card: /SP-404MKII/IMPORT/
    """
    import time
    from app.services.sp404_project_builder import SP404ProjectBuilder

    start_time = time.time()

    try:
        builder = SP404ProjectBuilder(db)

        result = await builder.build_project(
            kit_id=kit_id,
            project_name=request_data.project_name,
            project_bpm=request_data.project_bpm,
            format=request_data.format
        )

        result.generation_time_seconds = time.time() - start_time

        if hx_request:
            return templates.TemplateResponse("sp404/project-result.html", {
                "request": request,
                "result": result
            })

        return result

    except Exception as e:
        logger.error(f"Project generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/project/{project_id}/download")
async def download_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Download project ZIP file"""
    # Implementation: Return FileResponse with ZIP
    pass
```

### Database Schema Changes (Optional)

**If we want to track generated projects:**

```python
# backend/app/models/sp404_project.py

class SP404Project(Base):
    """Track generated SP-404MK2 projects"""
    __tablename__ = "sp404_projects"

    id = Column(Integer, primary_key=True)
    kit_id = Column(Integer, ForeignKey("kits.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    project_name = Column(String, nullable=False)
    project_bpm = Column(Float)
    sample_count = Column(Integer)

    zip_path = Column(String)
    file_size_bytes = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    kit = relationship("Kit")
    user = relationship("User")
```

### Web UI Components

**Template:** `backend/templates/sp404/project-builder.html`

```html
<!-- Kit details page - add button -->
<div class="card">
  <div class="card-body">
    <h3>Export to SP-404MK2</h3>

    <form hx-post="/api/v1/sp404/project/{{ kit.id }}"
          hx-target="#export-result"
          hx-indicator="#export-loading">

      <div class="form-control">
        <label>Project Name</label>
        <input type="text" name="project_name"
               value="{{ kit.name }}" class="input input-bordered">
      </div>

      <div class="form-control">
        <label>Project BPM</label>
        <input type="number" name="project_bpm"
               step="0.01" min="20" max="300"
               placeholder="Auto-detect" class="input input-bordered">
      </div>

      <div class="form-control">
        <label>Format</label>
        <select name="format" class="select select-bordered">
          <option value="wav">WAV</option>
          <option value="aiff">AIFF</option>
        </select>
      </div>

      <button type="submit" class="btn btn-primary mt-4">
        Generate SP-404MK2 Project
      </button>

      <span id="export-loading" class="loading loading-spinner htmx-indicator"></span>
    </form>

    <div id="export-result" class="mt-4"></div>
  </div>
</div>
```

**Template:** `backend/templates/sp404/project-result.html`

```html
<div class="alert alert-success">
  <h4>Project Generated Successfully!</h4>

  <p>
    <strong>{{ result.project_name }}</strong>
    ({{ result.sample_count }} samples, {{ result.project_bpm }} BPM)
  </p>

  <p>Size: {{ result.file_size_bytes | filesizeformat }}</p>

  <a href="/api/v1/sp404/project/{{ result.kit_id }}/download"
     class="btn btn-success">
    Download ZIP
  </a>

  <details class="mt-4">
    <summary>Installation Instructions</summary>
    <ol>
      <li>Download ZIP file</li>
      <li>Extract to: <code>/SP-404MKII/IMPORT/</code> on SD card</li>
      <li>Insert SD card into SP-404MK2</li>
      <li>Press: MENU → IMPORT → Select project</li>
      <li>Hardware will load samples and PADCONF.BIN</li>
    </ol>
  </details>
</div>
```

### Testing Approach (MVP-Level)

**File:** `backend/tests/test_sp404_project_builder.py`

```python
import pytest
from pathlib import Path
from app.services.sp404_project_builder import SP404ProjectBuilder


@pytest.mark.asyncio
async def test_build_project_basic(db_session, test_kit_with_samples):
    """Test building basic project"""
    builder = SP404ProjectBuilder(db_session)

    result = await builder.build_project(
        kit_id=test_kit_with_samples.id,
        format="wav"
    )

    assert result.success
    assert result.sample_count > 0
    assert Path(result.padconf_path).exists()
    assert Path(result.zip_path).exists()


@pytest.mark.asyncio
async def test_auto_detect_bpm(db_session, test_kit_with_bpm_samples):
    """Test BPM auto-detection"""
    builder = SP404ProjectBuilder(db_session)

    result = await builder.build_project(
        kit_id=test_kit_with_bpm_samples.id
    )

    # Should use median BPM from samples
    assert result.project_bpm > 0


@pytest.mark.asyncio
async def test_padconf_generation(db_session, test_kit_with_samples):
    """Test PADCONF.BIN is valid"""
    builder = SP404ProjectBuilder(db_session)

    result = await builder.build_project(
        kit_id=test_kit_with_samples.id
    )

    # Verify PADCONF.BIN size
    padconf_path = Path(result.padconf_path)
    assert padconf_path.stat().st_size == 52000

    # Verify can be read back
    padconf_service = PadconfService()
    project_config, pad_configs = padconf_service.read_padconf(padconf_path)

    assert project_config.project_name == result.project_name
```

### Hour Estimates - Phase 2

| Task | Hours | Notes |
|------|-------|-------|
| Create `SP404ProjectBuilder` class | 1.0 | Service skeleton |
| Implement `build_project()` | 2.0 | Main orchestration |
| Implement `_export_audio_samples()` | 1.0 | Use existing service |
| Implement `_build_pad_configs()` | 2.0 | AI data integration |
| Implement BPM auto-detection | 0.5 | Statistics logic |
| Implement `_create_zip()` | 0.5 | Standard zipfile |
| Create `ProjectBuildRequest` schema | 0.5 | Pydantic model |
| Create `ProjectBuildResult` schema | 0.5 | Pydantic model |
| Add API endpoint | 1.0 | FastAPI route |
| Create HTML templates | 1.5 | HTMX + DaisyUI |
| Write integration tests | 2.0 | 3-5 tests |
| Manual testing + bug fixes | 2.0 | End-to-end validation |
| **Total Phase 2** | **14.5 hours** | **~2 days** |

---

## Implementation Tasks

### Phase 1: PADCONF Library Checklist

- [ ] Create `backend/app/services/padconf_service.py`
  - [ ] Define `PadConfig` Pydantic model (0.5h)
  - [ ] Define `ProjectConfig` Pydantic model (0.5h)
  - [ ] Implement `PadconfService` class init (0.5h)
  - [ ] Implement `_write_header()` method (1.0h)
  - [ ] Implement `_write_pad_metadata()` method (2.0h)
  - [ ] Implement `_write_pad_filename()` method (0.5h)
  - [ ] Implement `create_padconf()` orchestration (0.5h)
  - [ ] Implement `_read_header()` method (0.5h)
  - [ ] Implement `_read_pad_metadata()` method (1.0h)
  - [ ] Implement `_read_pad_filename()` method (0.5h)
  - [ ] Implement `read_padconf()` orchestration (0.5h)

- [ ] Create `backend/tests/test_padconf_service.py`
  - [ ] Test: Create empty PADCONF.BIN (0.5h)
  - [ ] Test: Write single pad with BPM (0.5h)
  - [ ] Test: Round-trip write/read (0.5h)

**Dependencies:** None (standalone library)

**Total Phase 1:** 8 hours (~1 day)

---

### Phase 2: Project Builder Checklist

- [ ] Create `backend/app/services/sp404_project_builder.py`
  - [ ] Define `SP404ProjectBuilder` class (1.0h)
  - [ ] Implement `build_project()` main method (2.0h)
  - [ ] Implement `_get_kit()` and `_get_kit_samples()` (0.5h)
  - [ ] Implement `_export_audio_samples()` (1.0h)
  - [ ] Implement `_build_pad_configs()` with AI integration (2.0h)
  - [ ] Implement `_auto_detect_bpm()` (0.5h)
  - [ ] Implement `_should_loop()` heuristics (0.5h)
  - [ ] Implement `_should_bpm_sync()` heuristics (0.5h)
  - [ ] Implement `_write_manifest()` (0.5h)
  - [ ] Implement `_create_zip()` (0.5h)

- [ ] Create `backend/app/schemas/sp404_project.py`
  - [ ] Define `ProjectBuildRequest` schema (0.5h)
  - [ ] Define `ProjectBuildResult` schema (0.5h)

- [ ] Modify `backend/app/api/v1/endpoints/sp404_export.py`
  - [ ] Add `generate_sp404_project()` endpoint (1.0h)
  - [ ] Add `download_project()` endpoint (0.5h)
  - [ ] Add HTMX template responses (0.5h)

- [ ] Create Web UI Templates
  - [ ] `templates/sp404/project-builder.html` (1.0h)
  - [ ] `templates/sp404/project-result.html` (0.5h)

- [ ] Testing
  - [ ] Create `tests/test_sp404_project_builder.py` (1.0h)
  - [ ] Write integration test: Basic project build (0.5h)
  - [ ] Write integration test: BPM auto-detection (0.5h)
  - [ ] Write integration test: PADCONF validation (0.5h)
  - [ ] Manual end-to-end testing (2.0h)

**Dependencies:**
- Phase 1 MUST be complete
- Existing `SP404ExportService` (already exists)
- Existing `KitService` (already exists)

**Total Phase 2:** 14.5 hours (~2 days)

---

### Optional: Database Tracking (Post-MVP)

- [ ] Create `backend/app/models/sp404_project.py`
  - [ ] Define `SP404Project` model (0.5h)
  - [ ] Create Alembic migration (0.5h)
  - [ ] Update `ProjectBuilder` to track projects (1.0h)

**Total Optional:** 2 hours

---

## Risk Analysis

### Technical Risks

**Risk 1: Binary Format Complexity**
- **Severity:** MEDIUM
- **Impact:** Bugs in PADCONF generation could corrupt hardware projects
- **Probability:** MEDIUM (20+ parameters, byte alignment)
- **Mitigation:**
  - Reference implementation exists (mk2_bpm_edit.py)
  - Complete specification documented
  - Write comprehensive unit tests
  - Test with actual hardware before production release
  - Implement round-trip read/write validation

**Risk 2: Sample Start/End Offset Rules**
- **Severity:** LOW
- **Impact:** Sample playback might not align perfectly
- **Probability:** LOW (documentation mentions 512/872 offset rules but unclear)
- **Mitigation:**
  - Start with conservative defaults (sample_start=0, sample_end=0)
  - Hardware auto-detects sample boundaries
  - Document as known limitation in v1
  - Iterate based on user feedback

**Risk 3: Hardware Compatibility**
- **Severity:** MEDIUM
- **Impact:** Generated PADCONF.BIN not recognized by hardware
- **Probability:** LOW (format is reverse-engineered from actual files)
- **Mitigation:**
  - Specification is from firmware 5.01
  - Test with actual SP-404MK2 hardware
  - Provide "Download at own risk" disclaimer for v1
  - Collect user feedback for edge cases

**Risk 4: File Size Limits**
- **Severity:** LOW
- **Impact:** Large kits might exceed ZIP size limits
- **Probability:** LOW (160 samples × 2MB avg = 320MB, well within limits)
- **Mitigation:**
  - Implement size checks before ZIP creation
  - Stream ZIP generation for large exports
  - Show progress indicator in UI

---

### Integration Risks

**Risk 5: Existing Export Service Changes**
- **Severity:** LOW
- **Impact:** Changes to `SP404ExportService` could break project builder
- **Probability:** LOW (export service is mature)
- **Mitigation:**
  - Use stable public API only
  - Avoid tight coupling (dependency injection)
  - Test against export service interface

**Risk 6: Database Schema Changes**
- **Severity:** LOW
- **Impact:** Kit/Sample model changes could break pad config generation
- **Probability:** LOW (models are stable)
- **Mitigation:**
  - Use SQLAlchemy ORM (abstracts schema changes)
  - Write integration tests against database
  - Version check for critical fields (bpm, pad_bank, etc.)

---

## Success Metrics

### Phase 1: PADCONF Library

**Definition of Done:**
- [x] `PadconfService.create_padconf()` generates 52,000-byte binary
- [x] All byte offsets match specification exactly
- [x] BPM value correctly encoded (9000 = 90.00 BPM)
- [x] Filenames correctly written to offset 0x6C20+
- [x] Round-trip test passes (write → read → verify)
- [x] 3-5 unit tests passing
- [x] Type checking passes (mypy)

**Testing Requirements:**
- Unit test: Empty PADCONF creation
- Unit test: Single pad with BPM
- Unit test: Round-trip consistency
- Manual verification: Hex dump matches expected offsets

---

### Phase 2: Project Builder

**Definition of Done:**
- [x] API endpoint returns valid `ProjectBuildResult`
- [x] ZIP file contains PADCONF.BIN + audio samples
- [x] PADCONF.BIN is 52,000 bytes
- [x] Audio samples are 48kHz/16-bit WAV
- [x] Pad assignments match kit configuration
- [x] BPM auto-detection works for kits with analyzed samples
- [x] Web UI displays success/error states
- [x] Download link works
- [x] 3-5 integration tests passing

**Testing Requirements:**
- Integration test: Build project from kit
- Integration test: BPM auto-detection
- Integration test: PADCONF validation
- Manual test: Download ZIP, extract, verify contents
- Manual test: Copy to SD card, load on SP-404MK2 (if hardware available)

---

### User Acceptance Criteria

**Must Have (MVP):**
1. User can click "Generate SP-404MK2 Project" on kit page
2. System generates ZIP with PADCONF.BIN + audio files
3. ZIP is downloadable via browser
4. PADCONF.BIN has correct BPM for each pad (from AI analysis)
5. Audio files are named correctly (pad_XXX_samplename.wav)
6. No errors when kit has <160 samples (partial banks)

**Should Have (Post-MVP):**
1. User can customize project name before generation
2. User can override project BPM
3. User can preview pad assignments before generation
4. System validates kit doesn't exceed 160 pads
5. System shows progress indicator for large exports

**Nice to Have (Future):**
1. User can customize per-pad settings (loop, effects routing)
2. User can save project templates
3. User can edit PADCONF.BIN in web UI
4. System provides installation tutorial video

---

## Timeline Summary

| Phase | Tasks | Hours | Days |
|-------|-------|-------|------|
| **Phase 1: PADCONF Library** | Binary format implementation | 8h | 1 day |
| **Phase 2: Project Builder** | API + UI + Integration | 14.5h | 2 days |
| **Total MVP** | | **22.5h** | **2-3 days** |
| **Optional: Database Tracking** | Project history | 2h | +0.5 day |

**Assumptions:**
- Developer has existing codebase knowledge
- No major blockers or architectural changes
- Testing requirements are MVP-level (2-5 tests per feature)
- Hardware testing deferred to post-MVP validation

---

## Integration with Existing Features

### Leverage Current Architecture

**Existing Services (Reuse):**
```python
SP404ExportService       → Audio conversion (48kHz/16-bit)
AudioFeaturesService     → BPM, key detection
OpenRouterService        → AI vibe analysis (not directly used)
KitService               → Kit/sample data access
SampleService            → Sample metadata access
```

**Existing Data Models (Extend):**
```python
Kit                      → Source of project data
KitSample                → Pad assignments (bank, number, volume, pitch)
Sample                   → Audio files + analysis (BPM, genre, tags)
SP404Export              → Track export history (optional: extend for projects)
```

**Existing API Patterns (Follow):**
```python
Dual JSON/HTMX responses → All endpoints support both
Pydantic schemas         → Request/response validation
SQLAlchemy async         → Database access
Background tasks         → For large exports (future)
```

**Existing UI Components (Extend):**
```python
DaisyUI cards            → Project builder form
HTMX forms               → Async submission
Alpine.js                → Client-side interactivity
Loading indicators       → Progress feedback
```

### New Components Required

**Backend:**
1. `PadconfService` - Binary file manipulation
2. `SP404ProjectBuilder` - Project orchestration
3. `ProjectBuildRequest` - Pydantic schema
4. `ProjectBuildResult` - Pydantic schema
5. API endpoint: `POST /api/v1/sp404/project/{kit_id}`
6. API endpoint: `GET /api/v1/sp404/project/{project_id}/download`

**Frontend:**
1. `templates/sp404/project-builder.html` - Form UI
2. `templates/sp404/project-result.html` - Success display
3. Button on Kit details page - "Generate SP-404MK2 Project"

**Database (Optional):**
1. `SP404Project` model - Track generated projects
2. Alembic migration - Create table

---

## Example Usage Flow

**User Perspective:**

1. User browses to Kit details page: `/kits/42`
2. User clicks "Generate SP-404MK2 Project" button
3. Modal/form appears with options:
   - Project name: "Dusty Drums" (pre-filled from kit name)
   - Project BPM: 90.0 (auto-detected, editable)
   - Format: WAV (dropdown)
4. User clicks "Generate"
5. Loading indicator shows (3-5 seconds)
6. Success message displays:
   ```
   Project Generated Successfully!

   Dusty Drums (16 samples, 90.0 BPM)
   Size: 24.5 MB

   [Download ZIP]
   ```
7. User clicks "Download ZIP"
8. Browser downloads `dusty_drums.zip`
9. User extracts ZIP to SD card: `/SP-404MKII/IMPORT/dusty_drums/`
10. User inserts SD card into SP-404MK2
11. User navigates: MENU → IMPORT → dusty_drums
12. Hardware loads PADCONF.BIN + samples
13. User plays samples on hardware pads

**Developer Perspective:**

```python
# User submits form
POST /api/v1/sp404/project/42
{
    "project_name": "Dusty Drums",
    "project_bpm": 90.0,
    "format": "wav"
}

# Backend flow
builder = SP404ProjectBuilder(db)
result = await builder.build_project(
    kit_id=42,
    project_name="Dusty Drums",
    project_bpm=90.0
)

# System generates:
# 1. /tmp/sp404_projects/dusty_drums/PADCONF.BIN
# 2. /tmp/sp404_projects/dusty_drums/pad_001_kick.wav
# 3. /tmp/sp404_projects/dusty_drums/pad_002_snare.wav
# 4. ... (16 samples total)
# 5. /tmp/sp404_projects/dusty_drums/PROJECT_INFO.txt
# 6. /tmp/sp404_projects/dusty_drums.zip

# Response
{
    "success": true,
    "kit_id": 42,
    "project_name": "Dusty Drums",
    "sample_count": 16,
    "download_url": "/api/v1/sp404/project/42/download",
    "file_size_bytes": 25690112
}
```

---

## Documentation Requirements

**User-Facing:**
1. Update `CLAUDE.md` with PADCONF integration status
2. Create `docs/SP404_PROJECT_EXPORT.md` with:
   - Feature overview
   - Step-by-step tutorial
   - Installation instructions (SD card setup)
   - Troubleshooting guide
3. Update `docs/CHANGELOG.md` with feature release

**Developer-Facing:**
1. Docstrings for all public methods
2. Type hints on all function signatures
3. README in `dev/active/sp404-padconf-integration/`
4. API documentation (OpenAPI/Swagger auto-generated)

---

## Next Steps

**After Plan Approval:**

1. **Phase 1 Implementation** (1 day)
   - Create `padconf_service.py`
   - Write unit tests
   - Validate binary format with hex dump

2. **Phase 2 Implementation** (2 days)
   - Create `sp404_project_builder.py`
   - Add API endpoints
   - Create UI templates
   - Write integration tests

3. **Testing & Validation** (included in estimates)
   - Automated test suite
   - Manual end-to-end testing
   - Hardware validation (if available)

4. **Documentation** (0.5 day, included)
   - Update project docs
   - Write user tutorial
   - Update CHANGELOG

5. **Release** (0 day)
   - Merge to main
   - Deploy to production
   - Announce feature to users

---

**Total Estimated Timeline:** 2-3 days for complete MVP implementation

**Status:** Ready for implementation approval
