"""
SP-404MK2 PADCONF.BIN Service

Handles reading/writing binary PADCONF.BIN files for SP-404MK2 hardware.

PADCONF.BIN Format Specification:
- Total Size: 52,000 bytes
- Header: 160 bytes (project settings, bank BPMs, volumes)
- Pad Metadata: 160 pads × 172 bytes each = 27,520 bytes
- Filenames: 160 pads × 24 bytes each = 3,840 bytes
- Total: 160 + 27,520 + 3,840 = 31,520 bytes used

Reference: https://github.com/gsterlin/sp404mk2-tools/blob/main/padconf/mk2_notes.txt
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PadConfig(BaseModel):
    """Configuration for a single pad (Pads 1-160, Banks A-J)"""

    # Identification
    pad_index: int = Field(
        ...,
        ge=1,
        le=160,
        description="Global pad position (1-160). Bank A: 1-16, Bank B: 17-32, etc."
    )
    filename: str = Field(
        ...,
        max_length=23,
        description="Sample filename (max 23 chars, ASCII only, null-terminated)"
    )

    # Audio Properties
    sample_start: int = Field(
        0,
        ge=0,
        description="Sample start position (offset in samples)"
    )
    sample_end: int = Field(
        0,
        ge=0,
        description="Sample end position (offset in samples)"
    )
    volume: int = Field(
        100,
        ge=0,
        le=127,
        description="Pad volume level (0=silent, 127=max)"
    )

    # Playback Parameters
    bpm: Optional[float] = Field(
        None,
        ge=20.0,
        le=300.0,
        description="Sample BPM (for tempo-synced playback)"
    )
    pitch: int = Field(
        0,
        ge=-12,
        le=12,
        description="Pitch shift in semitones (-12 to +12)"
    )
    fine_tune: int = Field(
        0,
        ge=-50,
        le=50,
        description="Fine tuning in cents"
    )
    speed: int = Field(
        10000,
        ge=5000,
        le=20000,
        description="Playback speed (10000=100%, 5000=50%, 20000=200%)"
    )

    # Mode Switches
    gate: bool = Field(
        False,
        description="Gate mode enabled (sample stops at note-off)"
    )
    loop: bool = Field(
        False,
        description="Loop mode enabled"
    )
    bpm_sync: bool = Field(
        False,
        description="BPM sync enabled (tempo-follows-tempo)"
    )
    vinyl_effect: bool = Field(
        False,
        description="Vinyl simulation effect enabled"
    )

    # Loop Settings
    loop_point: int = Field(
        0,
        ge=0,
        description="Loop start point offset (from sample start)"
    )
    loop_mode: int = Field(
        0,
        ge=0,
        le=2,
        description="Loop type: 0=Off, 1=Loop, 2=Ping-Pong"
    )

    # Effects Routing
    pan: int = Field(
        64,
        ge=0,
        le=127,
        description="Pan position (64=center, 0=left, 127=right)"
    )
    mute_group: int = Field(
        0,
        ge=0,
        le=255,
        description="Mute group assignment (0=none, 1=Group A, etc.)"
    )
    pad_link: int = Field(
        0,
        ge=0,
        le=2,
        description="Pad linking (0=none, 1=Link A, 2=Link B)"
    )
    bus_route: int = Field(
        0,
        ge=0,
        le=2,
        description="Effects bus routing (0=Dry, 1=Bus1, 2=Bus2)"
    )

    # Envelope
    attack: int = Field(
        0,
        ge=0,
        le=127,
        description="Attack time (0=fastest)"
    )
    hold: int = Field(
        0,
        ge=0,
        le=127,
        description="Hold time"
    )
    release: int = Field(
        0,
        ge=0,
        le=127,
        description="Release time"
    )

    # Advanced
    one_shot_mode: int = Field(
        0,
        description="One-shot mode flags (0x20=Gate blink, 0x02=Vari Backing, 0x04=Vari Ensemble)"
    )


class ProjectConfig(BaseModel):
    """Global project configuration"""

    project_name: str = Field(
        "Untitled",
        max_length=31,
        description="Project name (max 31 chars, null-terminated)"
    )
    project_bpm: float = Field(
        120.0,
        ge=20.0,
        le=300.0,
        description="Master project BPM"
    )
    tempo_mode: str = Field(
        "project",
        pattern="^(project|bank)$",
        description="Tempo mode: 'project' (all pads follow project BPM) or 'bank' (per-bank BPMs)"
    )

    # Bank Settings (10 banks: A-J)
    bank_bpms: Dict[str, float] = Field(
        default_factory=dict,
        description="Per-bank BPM overrides (only used when tempo_mode='bank')"
    )
    bank_volumes: Dict[str, int] = Field(
        default_factory=dict,
        description="Per-bank volume settings"
    )


class PadconfService:
    """
    Service for reading/writing SP-404MK2 PADCONF.BIN files.

    Handles:
    - Binary format parsing/generation
    - Byte-level read/write operations
    - 160-pad configuration management
    """

    # File constants
    FILE_SIZE = 52000
    HEADER_SIZE = 160
    PAD_METADATA_SIZE = 172
    PAD_FILENAME_SIZE = 24
    PAD_COUNT = 160

    # Header byte offsets
    HEADER_TEMPO_MODE = 0x12
    HEADER_PROJECT_BPM = 0x13
    HEADER_PROJECT_NAME = 0x81

    # Pad section offsets
    PAD_METADATA_START = 0xA5
    PAD_FILENAME_START = 0x6C20

    def __init__(self):
        """Initialize PADCONF service"""
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

        Raises:
            ValueError: If pad_configs contains invalid pad indices
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

        logger.debug(f"Created PADCONF.BIN: {len(buffer)} bytes, {len(pad_configs)} pads")

        return bytes(buffer)

    def _write_header(
        self,
        buffer: bytearray,
        config: ProjectConfig
    ) -> None:
        """
        Write header section (bytes 0-159).

        Sets:
        - Tempo mode (project vs bank)
        - Project BPM
        - Bank-specific BPMs (A-J)
        - Bank volumes (A-J, interleaved order)
        - Project name (null-terminated)
        """
        # Tempo mode (0x12): 0x01=project, 0x00=bank
        buffer[self.HEADER_TEMPO_MODE] = 0x01 if config.tempo_mode == "project" else 0x00

        # Project BPM (0x13-0x14, big-endian): 90.00 BPM → 9000
        bpm_int = int(config.project_bpm * 100)
        buffer[self.HEADER_PROJECT_BPM:self.HEADER_PROJECT_BPM+2] = bpm_int.to_bytes(2, 'big')

        logger.debug(f"Header: tempo_mode={config.tempo_mode}, project_bpm={config.project_bpm}")

        # Bank BPMs (0x41-0x68): 4 bytes each, big-endian
        # Note: Multiply by 2 due to "div-by-2" rule in specification
        bank_offsets = {
            'A': 0x41, 'B': 0x45, 'C': 0x49, 'D': 0x4D, 'E': 0x51,
            'F': 0x55, 'G': 0x59, 'H': 0x5D, 'I': 0x61, 'J': 0x65
        }
        for bank, offset in bank_offsets.items():
            bpm = config.bank_bpms.get(bank, config.project_bpm)
            # Apply div-by-2 rule: store as (BPM * 100) * 2
            bpm_value = int(bpm * 100) * 2
            buffer[offset:offset+4] = bpm_value.to_bytes(4, 'big')

        # Bank volumes (0x6D-0x80): Interleaved pattern B,A,D,C,F,E,H,G,J,I
        # Each is 2 bytes, default 127 (max volume)
        volume_offsets = {
            'B': 0x6D, 'A': 0x6F, 'D': 0x71, 'C': 0x73, 'F': 0x75,
            'E': 0x77, 'H': 0x79, 'G': 0x7B, 'J': 0x7D, 'I': 0x7F
        }
        for bank, offset in volume_offsets.items():
            volume = config.bank_volumes.get(bank, 127)  # Default: max volume
            buffer[offset:offset+2] = volume.to_bytes(2, 'big')

        # Project name (0x81-0xA0): 32 bytes, null-terminated ASCII
        name_bytes = config.project_name.encode('ascii', errors='ignore')[:31]
        buffer[self.HEADER_PROJECT_NAME:self.HEADER_PROJECT_NAME+len(name_bytes)] = name_bytes
        # Null terminator is already at position len(name_bytes) due to zeroed buffer
        if len(name_bytes) < 31:
            buffer[self.HEADER_PROJECT_NAME+len(name_bytes)] = 0x00

    def _write_pad_metadata(
        self,
        buffer: bytearray,
        pad: PadConfig
    ) -> None:
        """
        Write single pad metadata (172 bytes).

        Formula: offset = 0xA5 + ((pad_index - 1) * 172)

        Writes 20+ fields including sample positions, volume, BPM, effects, routing.
        """
        offset = self.PAD_METADATA_START + ((pad.pad_index - 1) * self.PAD_METADATA_SIZE)

        # Sample start/end (0x00-0x07)
        buffer[offset:offset+4] = pad.sample_start.to_bytes(4, 'big')
        buffer[offset+4:offset+8] = pad.sample_end.to_bytes(4, 'big')

        # Volume (0x08-0x0B): 4-byte integer, range 0x00-0x7F
        buffer[offset+8:offset+12] = pad.volume.to_bytes(4, 'big')

        # Gate (0x0C-0x0F): 0x00000001=On, 0x00000000=Off
        buffer[offset+12:offset+16] = (1 if pad.gate else 0).to_bytes(4, 'big')

        # Loop (0x10-0x13): 0x7FFFFFFF=On, 0x00000000=Off
        loop_value = 0x7FFFFFFF if pad.loop else 0x00000000
        buffer[offset+16:offset+20] = loop_value.to_bytes(4, 'big')

        # Mute group (0x18-0x1B): 0x00=None, 0x01=Group A, etc.
        buffer[offset+24:offset+28] = pad.mute_group.to_bytes(4, 'big')

        # BPM sync (0x1C-0x1F): 0x00000001=On, 0x00000000=Off
        buffer[offset+28:offset+32] = (1 if pad.bpm_sync else 0).to_bytes(4, 'big')

        # BPM value (0x22-0x23) - CRITICAL FIELD
        # 2-byte big-endian: 90.00 BPM → 9000
        if pad.bpm:
            bpm_int = int(pad.bpm * 100)
            buffer[offset+34:offset+36] = bpm_int.to_bytes(2, 'big')
        else:
            buffer[offset+34:offset+36] = (0).to_bytes(2, 'big')

        # Loop point (0x28-0x2B): Offset from sample start
        buffer[offset+40:offset+44] = pad.loop_point.to_bytes(4, 'big')

        # Pitch (0x30-0x33): Semitones, signed
        buffer[offset+48:offset+52] = pad.pitch.to_bytes(4, 'big', signed=True)

        # Fine tune (0x34-0x37): Cents, signed
        buffer[offset+52:offset+56] = pad.fine_tune.to_bytes(4, 'big', signed=True)

        # Loop mode (0x38-0x3B): 0x01=Loop, 0x02=Ping-Pong
        buffer[offset+56:offset+60] = pad.loop_mode.to_bytes(4, 'big')

        # Speed (0x3C-0x3F): 0x2710=100%, 0x1388=50%, 0x5420=200%
        buffer[offset+60:offset+64] = pad.speed.to_bytes(4, 'big')

        # Vinyl effect (0x40-0x43): 0x01=On
        buffer[offset+64:offset+68] = (1 if pad.vinyl_effect else 0).to_bytes(4, 'big')

        # Pan (0x44-0x47): 0x40=center, 0x00=left, 0x7F=right
        buffer[offset+68:offset+72] = pad.pan.to_bytes(4, 'big')

        # Pad link (0x48-0x4B): 0x00=None, 0x01=A, 0x02=B
        buffer[offset+72:offset+76] = pad.pad_link.to_bytes(4, 'big')

        # Bus route (0x4C-0x4F): 0x00=Dry, 0x01=Bus1, 0x02=Bus2
        buffer[offset+76:offset+80] = pad.bus_route.to_bytes(4, 'big')

        # Envelope (0x54-0x5F): Attack, Hold, Release (each 4 bytes)
        buffer[offset+84:offset+88] = pad.attack.to_bytes(4, 'big')
        buffer[offset+88:offset+92] = pad.hold.to_bytes(4, 'big')
        buffer[offset+92:offset+96] = pad.release.to_bytes(4, 'big')

        logger.debug(
            f"Pad {pad.pad_index:03d}: {pad.filename} - "
            f"BPM: {pad.bpm or 'N/A'}, Loop: {pad.loop}, Sync: {pad.bpm_sync}"
        )

    def _write_pad_filename(
        self,
        buffer: bytearray,
        pad: PadConfig
    ) -> None:
        """
        Write pad filename (24 bytes, null-terminated).

        Formula: offset = 0x6C20 + ((pad_index - 1) * 24)

        Sanitizes filename to ASCII, limits to 23 characters.
        """
        offset = self.PAD_FILENAME_START + ((pad.pad_index - 1) * self.PAD_FILENAME_SIZE)

        # Sanitize and encode filename (ASCII only, 23 char max)
        filename_bytes = pad.filename.encode('ascii', errors='ignore')[:23]
        buffer[offset:offset+len(filename_bytes)] = filename_bytes
        # Null terminator already in place due to zeroed buffer

    def read_padconf(self, file_path: Path) -> tuple[ProjectConfig, List[PadConfig]]:
        """
        Read PADCONF.BIN file and parse into configuration objects.

        Args:
            file_path: Path to PADCONF.BIN file

        Returns:
            Tuple of (ProjectConfig, List[PadConfig])

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file size is incorrect
        """
        with open(file_path, 'rb') as f:
            data = f.read()

        if len(data) != self.FILE_SIZE:
            raise ValueError(f"Invalid PADCONF.BIN size: {len(data)} (expected {self.FILE_SIZE})")

        # Parse header
        project_config = self._read_header(data)

        # Parse all 160 pads
        pad_configs = []
        for i in range(1, self.PAD_COUNT + 1):
            pad_config = self._read_pad_metadata(data, i)
            pad_config.filename = self._read_pad_filename(data, i)

            # Only include pads with filenames
            if pad_config.filename:
                pad_configs.append(pad_config)

        logger.debug(f"Read PADCONF.BIN: {len(pad_configs)} pads with filenames")

        return project_config, pad_configs

    def _read_header(self, data: bytes) -> ProjectConfig:
        """Parse header section (bytes 0-159)"""
        # Tempo mode
        tempo_mode = "project" if data[self.HEADER_TEMPO_MODE] == 0x01 else "bank"

        # Project BPM (0x13-0x14): Big-endian, e.g., 9000 → 90.00
        bpm_int = int.from_bytes(data[self.HEADER_PROJECT_BPM:self.HEADER_PROJECT_BPM+2], 'big')
        project_bpm = bpm_int / 100.0 if bpm_int > 0 else 120.0

        # Project name (0x81-0xA0): Null-terminated ASCII
        name_bytes = data[self.HEADER_PROJECT_NAME:self.HEADER_PROJECT_NAME+32]
        project_name = name_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')

        # Bank BPMs (optional for future enhancement)
        bank_bpms = {}

        return ProjectConfig(
            project_name=project_name,
            project_bpm=project_bpm,
            tempo_mode=tempo_mode,
            bank_bpms=bank_bpms
        )

    def _read_pad_metadata(self, data: bytes, pad_index: int) -> PadConfig:
        """Parse single pad metadata (172 bytes)"""
        offset = self.PAD_METADATA_START + ((pad_index - 1) * self.PAD_METADATA_SIZE)

        # Sample start/end
        sample_start = int.from_bytes(data[offset:offset+4], 'big')
        sample_end = int.from_bytes(data[offset+4:offset+8], 'big')

        # Volume
        volume = int.from_bytes(data[offset+8:offset+12], 'big')

        # Gate
        gate = int.from_bytes(data[offset+12:offset+16], 'big') == 1

        # Loop
        loop_value = int.from_bytes(data[offset+16:offset+20], 'big')
        loop = loop_value == 0x7FFFFFFF

        # BPM (offset +0x22): 2-byte big-endian
        bpm_int = int.from_bytes(data[offset+34:offset+36], 'big')
        bpm = bpm_int / 100.0 if bpm_int > 0 else None

        # BPM sync
        bpm_sync = int.from_bytes(data[offset+28:offset+32], 'big') == 1

        # Other fields
        pitch = int.from_bytes(data[offset+48:offset+52], 'big', signed=True)
        speed = int.from_bytes(data[offset+60:offset+64], 'big')
        pan = int.from_bytes(data[offset+68:offset+72], 'big')
        loop_mode = int.from_bytes(data[offset+56:offset+60], 'big')
        vinyl_effect = int.from_bytes(data[offset+64:offset+68], 'big') == 1

        return PadConfig(
            pad_index=pad_index,
            filename="",  # Set separately
            sample_start=sample_start,
            sample_end=sample_end,
            volume=volume,
            bpm=bpm,
            gate=gate,
            loop=loop,
            bpm_sync=bpm_sync,
            pitch=pitch,
            speed=speed,
            pan=pan,
            loop_mode=loop_mode,
            vinyl_effect=vinyl_effect
        )

    def _read_pad_filename(self, data: bytes, pad_index: int) -> str:
        """Parse pad filename (24 bytes, null-terminated ASCII)"""
        offset = self.PAD_FILENAME_START + ((pad_index - 1) * self.PAD_FILENAME_SIZE)
        filename_bytes = data[offset:offset+24]
        return filename_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
