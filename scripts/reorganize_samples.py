#!/usr/bin/env python3
"""
SP-404MK2 Sample Reorganization Script

Reorganizes cryptic SP-404MK2 folder structures into human-readable formats
while maintaining compatibility with the device's import requirements.
"""

import os
import re
import shutil
import json
import wave
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

import click
from tqdm import tqdm
import libturso_client
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sample_reorganization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class SampleInfo:
    """Data class for sample information"""
    original_path: str
    original_bank: str
    original_pad: int
    source_description: str
    instrument: Optional[str] = None
    subcategory: Optional[str] = None
    bpm: Optional[int] = None
    detection_method: Optional[str] = None
    ai_confidence: Optional[float] = None
    flagged: bool = False
    flag_reason: Optional[str] = None


class SampleReorganizer:
    """Main class for reorganizing SP-404MK2 samples"""
    
    def __init__(self, source_dir: str, turso_url: str, turso_token: str, openrouter_key: Optional[str] = None):
        self.source_dir = Path(source_dir)
        self.session_id = hashlib.md5(f"{source_dir}{datetime.now()}".encode()).hexdigest()[:8]
        
        # Setup database connection
        self.db = libturso_client.create_client(
            url=turso_url,
            auth_token=turso_token
        )
        
        # Setup AI client if key provided
        self.ai_client = None
        if openrouter_key:
            self.ai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key
            )
        
        # Load configuration
        self.samples: List[SampleInfo] = []
        self.errors: List[Dict] = []
        
    def initialize_database(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "db_schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = f.read()
                # Execute schema creation
                for statement in schema.split(';'):
                    if statement.strip():
                        self.db.execute(statement.strip() + ';')
        
    def parse_loops_info(self) -> Dict[Tuple[str, int], str]:
        """Parse LOOPS_INFO.txt to get source descriptions"""
        info_map = {}
        loops_info_path = self.source_dir / "ROLAND" / "SP-404MKII" / "SMPL" / "LOOPS_INFO.txt"
        
        if not loops_info_path.exists():
            logger.warning("LOOPS_INFO.txt not found")
            return info_map
        
        with open(loops_info_path, 'r') as f:
            content = f.read()
        
        # Parse bank sections
        current_bank = None
        for line in content.split('\n'):
            if line.startswith('BANK_'):
                current_bank = line.split()[0]
            elif line.startswith('Pad ') and current_bank:
                match = re.match(r'Pad (\d+): From (.+)', line)
                if match:
                    pad_num = int(match.group(1))
                    source = match.group(2)
                    info_map[(current_bank, pad_num)] = source
        
        return info_map
    
    def detect_instrument_from_filename(self, filename: str, source_desc: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """Detect instrument, subcategory, and BPM from filename and source description"""
        combined_text = f"{filename} {source_desc}".lower()
        
        # Try to extract BPM
        bpm = None
        bpm_match = re.search(r'(\d+)\s*bpm', combined_text)
        if bpm_match:
            bpm = int(bpm_match.group(1))
        
        # Query detection rules from database
        rules = self.db.execute("""
            SELECT pattern, instrument, subcategory 
            FROM instrument_detection_rules 
            ORDER BY priority
        """).fetchall()
        
        for pattern, instrument, subcategory in rules:
            if re.search(pattern, combined_text):
                return instrument, subcategory, bpm
        
        return None, None, bpm
    
    def detect_instrument_with_ai(self, file_path: str, source_desc: str) -> Tuple[str, Optional[str], float]:
        """Use AI to detect instrument type when pattern matching fails"""
        if not self.ai_client:
            return "unknown", None, 0.0
        
        try:
            # Read basic file info
            file_size = os.path.getsize(file_path)
            
            prompt = f"""Analyze this audio sample information and determine the instrument type:
            
Filename: {os.path.basename(file_path)}
Source Description: {source_desc}
File Size: {file_size} bytes

Return ONLY a JSON object with these fields:
- instrument: one of [drums, bass, keys, vocals, brass, strings, atmosphere, unknown]
- subcategory: specific type if applicable (e.g., kick, snare, rhodes)
- confidence: 0.0 to 1.0

Example: {{"instrument": "drums", "subcategory": "kick", "confidence": 0.95}}"""

            response = self.ai_client.chat.completions.create(
                model="google/gemini-flash-1.5-8b",  # Cheap, fast model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            
            result = json.loads(response.choices[0].message.content)
            return result['instrument'], result.get('subcategory'), result['confidence']
            
        except Exception as e:
            logger.error(f"AI detection failed for {file_path}: {e}")
            return "unknown", None, 0.0
    
    def get_wav_info(self, file_path: str) -> Dict:
        """Extract WAV file information"""
        try:
            with wave.open(file_path, 'rb') as wav:
                return {
                    'sample_rate': wav.getframerate(),
                    'bit_depth': wav.getsampwidth() * 8,
                    'duration': wav.getnframes() / wav.getframerate(),
                    'file_size': os.path.getsize(file_path)
                }
        except Exception as e:
            logger.error(f"Error reading WAV file {file_path}: {e}")
            return {}
    
    def scan_samples(self):
        """Scan source directory and collect sample information"""
        logger.info(f"Scanning samples in {self.source_dir}")
        
        # Parse source descriptions
        source_info = self.parse_loops_info()
        
        # Find all WAV files
        wav_files = list(self.source_dir.rglob("*.wav"))
        
        for wav_path in tqdm(wav_files, desc="Scanning samples"):
            # Extract bank and pad info from path
            path_parts = wav_path.parts
            if "BANK_" in str(wav_path):
                bank_idx = next(i for i, p in enumerate(path_parts) if p.startswith("BANK_"))
                bank = path_parts[bank_idx]
                pad_folder = path_parts[bank_idx + 1]
                pad_num = int(pad_folder)
                
                # Get source description
                source_desc = source_info.get((bank, pad_num), "Unknown source")
                
                # Create sample info
                sample = SampleInfo(
                    original_path=str(wav_path),
                    original_bank=bank,
                    original_pad=pad_num,
                    source_description=source_desc
                )
                
                # Detect instrument from filename/source
                instrument, subcategory, bpm = self.detect_instrument_from_filename(
                    wav_path.name, source_desc
                )
                
                if instrument:
                    sample.instrument = instrument
                    sample.subcategory = subcategory
                    sample.bpm = bpm
                    sample.detection_method = 'filename_parse'
                else:
                    # Try AI detection
                    instrument, subcategory, confidence = self.detect_instrument_with_ai(
                        str(wav_path), source_desc
                    )
                    sample.instrument = instrument
                    sample.subcategory = subcategory
                    sample.detection_method = 'ai_analysis'
                    sample.ai_confidence = confidence
                    
                    # Flag low confidence detections
                    if confidence < 0.7:
                        sample.flagged = True
                        sample.flag_reason = f"Low AI confidence: {confidence:.2f}"
                
                self.samples.append(sample)
    
    def create_human_readable_structure(self, output_dir: Path):
        """Create human-readable folder structure organized by instrument"""
        logger.info(f"Creating human-readable structure in {output_dir}")
        
        # Group samples by instrument and style
        organized = defaultdict(lambda: defaultdict(list))
        
        for sample in self.samples:
            if sample.instrument and sample.instrument != 'unknown':
                # Create style key from BPM and source
                style_key = ""
                if sample.bpm:
                    style_key = f"{sample.bpm}BPM"
                if "boom_bap" in sample.source_description.lower():
                    style_key = f"BoomBap_{style_key}" if style_key else "BoomBap"
                elif "jazz" in sample.source_description.lower():
                    style_key = f"Jazz_{style_key}" if style_key else "Jazz"
                elif "soul" in sample.source_description.lower():
                    style_key = f"Soul_{style_key}" if style_key else "Soul"
                
                if not style_key:
                    style_key = "Various"
                
                organized[sample.instrument][style_key].append(sample)
        
        # Create folders and copy files
        for instrument, styles in tqdm(organized.items(), desc="Creating human structure"):
            instrument_dir = output_dir / "By_Instrument" / instrument.title()
            
            for style, samples in styles.items():
                style_dir = instrument_dir / style
                style_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy samples with descriptive names
                for idx, sample in enumerate(samples, 1):
                    src_path = Path(sample.original_path)
                    
                    # Create descriptive filename
                    if sample.subcategory:
                        new_name = f"{sample.subcategory.title()}_{idx:02d}.wav"
                    else:
                        new_name = f"{instrument.title()}_{idx:02d}.wav"
                    
                    dst_path = style_dir / new_name
                    
                    try:
                        shutil.copy2(src_path, dst_path)
                        sample.human_path = str(dst_path)
                        sample.filename_human = new_name
                    except Exception as e:
                        logger.error(f"Error copying {src_path} to {dst_path}: {e}")
                        self.errors.append({
                            'file': str(src_path),
                            'error': str(e),
                            'type': 'copy_error'
                        })
    
    def create_sp404_structure(self, output_dir: Path):
        """Create SP-404MK2 compatible structure with descriptive bank names"""
        logger.info(f"Creating SP-404MK2 structure in {output_dir}")
        
        # Organize samples into banks by instrument
        banks = {
            'BANK_A_Drums': [],
            'BANK_B_Bass': [],
            'BANK_C_Keys': [],
            'BANK_D_Mixed': []
        }
        
        # Assign samples to banks
        for sample in self.samples:
            if sample.instrument == 'drums':
                banks['BANK_A_Drums'].append(sample)
            elif sample.instrument == 'bass':
                banks['BANK_B_Bass'].append(sample)
            elif sample.instrument == 'keys':
                banks['BANK_C_Keys'].append(sample)
            else:
                banks['BANK_D_Mixed'].append(sample)
        
        # Create structure
        sp404_root = output_dir / "ROLAND" / "SP-404MKII" / "SMPL"
        
        for bank_name, samples in tqdm(banks.items(), desc="Creating SP-404 structure"):
            bank_dir = sp404_root / bank_name
            
            # Create all 16 pad folders (maintaining empty ones)
            for pad_num in range(1, 17):
                pad_dir = bank_dir / f"{pad_num:04d}"
                pad_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy sample if available for this pad
                if pad_num <= len(samples):
                    sample = samples[pad_num - 1]
                    src_path = Path(sample.original_path)
                    dst_path = pad_dir / f"{pad_num:04d}_0000.wav"
                    
                    try:
                        shutil.copy2(src_path, dst_path)
                        sample.sp404_path = str(dst_path)
                        sample.new_bank_assignment = bank_name
                        sample.new_pad_position = pad_num
                    except Exception as e:
                        logger.error(f"Error copying to SP-404 structure: {e}")
                        self.errors.append({
                            'file': str(src_path),
                            'error': str(e),
                            'type': 'sp404_copy_error'
                        })
    
    def save_to_database(self):
        """Save all sample information to database"""
        logger.info("Saving to database")
        
        # Create session record
        self.db.execute("""
            INSERT INTO reorganization_sessions 
            (session_id, source_directory, total_samples, status)
            VALUES (?, ?, ?, 'running')
        """, (self.session_id, str(self.source_dir), len(self.samples)))
        
        # Save each sample
        for sample in tqdm(self.samples, desc="Saving to database"):
            wav_info = self.get_wav_info(sample.original_path)
            
            self.db.execute("""
                INSERT INTO sample_reorganization (
                    original_path, original_bank, original_pad, source_description,
                    sp404_path, human_path, instrument, instrument_subcategory,
                    bpm, filename_original, filename_human, file_size_bytes,
                    duration_seconds, sample_rate, bit_depth, detection_method,
                    ai_confidence, flagged_for_review, flag_reason,
                    new_bank_assignment, new_pad_position, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample.original_path, sample.original_bank, sample.original_pad,
                sample.source_description, sample.sp404_path, sample.human_path,
                sample.instrument, sample.subcategory, sample.bpm,
                os.path.basename(sample.original_path), sample.filename_human,
                wav_info.get('file_size'), wav_info.get('duration'),
                wav_info.get('sample_rate'), wav_info.get('bit_depth'),
                sample.detection_method, sample.ai_confidence,
                sample.flagged, sample.flag_reason,
                sample.new_bank_assignment, sample.new_pad_position,
                datetime.now()
            ))
        
        # Update session status
        flagged_count = sum(1 for s in self.samples if s.flagged)
        self.db.execute("""
            UPDATE reorganization_sessions 
            SET processed_samples = ?, flagged_samples = ?, 
                error_count = ?, status = 'completed', completed_at = ?
            WHERE session_id = ?
        """, (len(self.samples), flagged_count, len(self.errors), 
              datetime.now(), self.session_id))
    
    def generate_report(self):
        """Generate summary report"""
        logger.info("Generating report")
        
        report = f"""
SP-404MK2 Sample Reorganization Report
=====================================
Session ID: {self.session_id}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
--------
Total Samples Processed: {len(self.samples)}
Flagged for Review: {sum(1 for s in self.samples if s.flagged)}
Errors: {len(self.errors)}

Instrument Breakdown:
"""
        
        # Count by instrument
        instrument_counts = defaultdict(int)
        for sample in self.samples:
            instrument_counts[sample.instrument or 'unknown'] += 1
        
        for instrument, count in sorted(instrument_counts.items()):
            report += f"  - {instrument.title()}: {count}\n"
        
        if self.errors:
            report += "\nErrors:\n"
            for error in self.errors[:10]:  # Show first 10 errors
                report += f"  - {error['type']}: {error['file']} - {error['error']}\n"
            if len(self.errors) > 10:
                report += f"  ... and {len(self.errors) - 10} more errors\n"
        
        # Save report
        report_path = Path(f"reorganization_report_{self.session_id}.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(report)
        print(f"\nDetailed report saved to: {report_path}")


@click.command()
@click.option('--source', '-s', required=True, help='Source directory containing SP-404MK2 samples')
@click.option('--output-human', '-h', default='./Human_Readable_Samples', help='Output directory for human-readable structure')
@click.option('--output-sp404', '-o', default='./SP404_Import_Ready', help='Output directory for SP-404MK2 structure')
@click.option('--turso-url', envvar='TURSO_URL', required=True, help='Turso database URL')
@click.option('--turso-token', envvar='TURSO_TOKEN', required=True, help='Turso auth token')
@click.option('--openrouter-key', envvar='OPENROUTER_API_KEY', help='OpenRouter API key for AI detection')
@click.option('--dry-run', is_flag=True, help='Preview changes without copying files')
def main(source, output_human, output_sp404, turso_url, turso_token, openrouter_key, dry_run):
    """Reorganize SP-404MK2 samples into human-readable and device-compatible structures"""
    
    if dry_run:
        logger.info("DRY RUN MODE - No files will be copied")
    
    # Initialize reorganizer
    reorganizer = SampleReorganizer(source, turso_url, turso_token, openrouter_key)
    reorganizer.initialize_database()
    
    # Scan samples
    reorganizer.scan_samples()
    
    if not dry_run:
        # Create output directories
        human_dir = Path(output_human)
        sp404_dir = Path(output_sp404)
        
        # Create structures
        reorganizer.create_human_readable_structure(human_dir)
        reorganizer.create_sp404_structure(sp404_dir)
        
        # Save to database
        reorganizer.save_to_database()
    
    # Generate report
    reorganizer.generate_report()


if __name__ == '__main__':
    main()