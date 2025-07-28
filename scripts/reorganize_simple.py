#!/usr/bin/env python3
"""
Simplified SP-404MK2 Sample Reorganization Script
Works without database connection for quick testing
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict
import click
from tqdm import tqdm


def parse_loops_info(source_dir):
    """Parse LOOPS_INFO.txt to get source descriptions"""
    info_map = {}
    loops_info_path = source_dir / "ROLAND" / "SP-404MKII" / "SMPL" / "LOOPS_INFO.txt"
    
    if not loops_info_path.exists():
        print("Warning: LOOPS_INFO.txt not found")
        return info_map
    
    with open(loops_info_path, 'r') as f:
        content = f.read()
    
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


def detect_instrument_and_bpm(filename, source_desc):
    """Simple instrument and BPM detection from filename and source"""
    combined_text = f"{filename} {source_desc}".lower()
    
    # Extract BPM
    bpm = None
    bpm_match = re.search(r'(\d+)\s*bpm', combined_text)
    if bpm_match:
        bpm = int(bpm_match.group(1))
    
    # Simple instrument detection
    if any(word in combined_text for word in ['drum', 'kick', 'snare', 'hat', 'boom']):
        return 'drums', bpm
    elif 'bass' in combined_text:
        return 'bass', bpm
    elif any(word in combined_text for word in ['key', 'piano', 'rhodes', 'organ']):
        return 'keys', bpm
    elif any(word in combined_text for word in ['sax', 'saxophone']):
        return 'brass', bpm
    elif any(word in combined_text for word in ['atmosphere', 'atmos', 'ambient']):
        return 'atmosphere', bpm
    else:
        return 'unknown', bpm


@click.command()
@click.option('--source', '-s', required=True, help='Source directory containing SP-404MK2 samples')
@click.option('--output-human', '-h', default='./Human_Readable_Samples', help='Output directory for human-readable structure')
@click.option('--output-sp404', '-o', default='./SP404_Import_Ready', help='Output directory for SP-404MK2 structure')
@click.option('--dry-run', is_flag=True, help='Preview changes without copying files')
def main(source, output_human, output_sp404, dry_run):
    """Reorganize SP-404MK2 samples into human-readable and device-compatible structures"""
    
    source_dir = Path(source)
    if not source_dir.exists():
        click.echo(f"Error: Source directory {source} does not exist")
        return
    
    if dry_run:
        click.echo("DRY RUN MODE - No files will be copied\n")
    
    # Parse source descriptions
    source_info = parse_loops_info(source_dir)
    
    # Find all WAV files
    wav_files = list(source_dir.rglob("*.wav"))
    click.echo(f"Found {len(wav_files)} WAV files\n")
    
    # Analyze samples
    samples = []
    instrument_counts = defaultdict(int)
    
    for wav_path in tqdm(wav_files, desc="Analyzing samples"):
        if "BANK_" in str(wav_path):
            path_parts = wav_path.parts
            bank_idx = next(i for i, p in enumerate(path_parts) if p.startswith("BANK_"))
            bank = path_parts[bank_idx]
            pad_folder = path_parts[bank_idx + 1]
            pad_num = int(pad_folder)
            
            # Get source description
            source_desc = source_info.get((bank, pad_num), "Unknown source")
            
            # Detect instrument and BPM
            instrument, bpm = detect_instrument_and_bpm(wav_path.name, source_desc)
            
            samples.append({
                'path': wav_path,
                'bank': bank,
                'pad': pad_num,
                'source': source_desc,
                'instrument': instrument,
                'bpm': bpm
            })
            
            instrument_counts[instrument] += 1
    
    # Print summary
    click.echo("\nInstrument Summary:")
    for instrument, count in sorted(instrument_counts.items()):
        click.echo(f"  {instrument.title()}: {count}")
    
    if not dry_run:
        # Create human-readable structure
        click.echo(f"\nCreating human-readable structure in {output_human}")
        human_dir = Path(output_human)
        
        # Group by instrument
        by_instrument = defaultdict(list)
        for sample in samples:
            by_instrument[sample['instrument']].append(sample)
        
        for instrument, instrument_samples in tqdm(by_instrument.items(), desc="Creating human structure"):
            # Group by BPM/style
            by_style = defaultdict(list)
            for sample in instrument_samples:
                style_key = ""
                if sample['bpm']:
                    style_key = f"{sample['bpm']}BPM"
                if 'jazz' in sample['source'].lower():
                    style_key = f"Jazz_{style_key}" if style_key else "Jazz"
                elif 'soul' in sample['source'].lower():
                    style_key = f"Soul_{style_key}" if style_key else "Soul"
                elif 'boom' in sample['source'].lower():
                    style_key = f"BoomBap_{style_key}" if style_key else "BoomBap"
                
                if not style_key:
                    style_key = "Various"
                
                by_style[style_key].append(sample)
            
            # Create folders and copy
            for style, style_samples in by_style.items():
                style_dir = human_dir / "By_Instrument" / instrument.title() / style
                style_dir.mkdir(parents=True, exist_ok=True)
                
                for idx, sample in enumerate(style_samples, 1):
                    new_name = f"{instrument.title()}_{idx:02d}.wav"
                    dst_path = style_dir / new_name
                    shutil.copy2(sample['path'], dst_path)
        
        # Create SP-404MK2 structure
        click.echo(f"\nCreating SP-404MK2 structure in {output_sp404}")
        sp404_dir = Path(output_sp404)
        sp404_root = sp404_dir / "ROLAND" / "SP-404MKII" / "SMPL"
        
        # Organize into banks by instrument
        banks = {
            'BANK_A_Drums': [s for s in samples if s['instrument'] == 'drums'],
            'BANK_B_Bass': [s for s in samples if s['instrument'] == 'bass'],
            'BANK_C_Keys': [s for s in samples if s['instrument'] == 'keys'],
            'BANK_D_Mixed': [s for s in samples if s['instrument'] not in ['drums', 'bass', 'keys']]
        }
        
        for bank_name, bank_samples in tqdm(banks.items(), desc="Creating SP-404 structure"):
            bank_dir = sp404_root / bank_name
            
            # Create all 16 pad folders
            for pad_num in range(1, 17):
                pad_dir = bank_dir / f"{pad_num:04d}"
                pad_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy sample if available
                if pad_num <= len(bank_samples):
                    sample = bank_samples[pad_num - 1]
                    dst_path = pad_dir / f"{pad_num:04d}_0000.wav"
                    shutil.copy2(sample['path'], dst_path)
    
    click.echo("\n✅ Reorganization complete!")
    click.echo(f"Human-readable samples: {output_human}")
    click.echo(f"SP-404MK2-ready samples: {output_sp404}")


if __name__ == '__main__':
    main()