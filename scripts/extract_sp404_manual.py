#!/usr/bin/env python3
"""
SP-404MK2 Manual Extraction Script

Extracts sections from the SP-404MK2 reference manual PDF and converts them
to markdown files for use in the hardware instruction system.

Based on the table of contents:
- Sampling (SAMPLING): p33-42
- Recording samples by looping (LOOPER): p41
- Creating bass and other sounds (SOUND GENERATOR): p43
- Editing a sample (SAMPLE EDIT): p44
- Combining samples to create a pattern (PATTERN SEQUENCER): p58
- Setting the tempo: p81
- Mixing the samples (DJ MODE): p85
- Using the effects: p27
- Configuring the various settings (UTILITY): p102
- Importing/exporting (using the SD card): p110

Usage:
    python scripts/extract_sp404_manual.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
    import pymupdf as fitz


# Section definitions based on the table of contents
SECTIONS: Dict[str, Tuple[int, int, str]] = {
    "sp404-sampling.md": (
        33, 56,
        """# SP-404MK2 Sampling Guide

This guide covers all sampling operations on the SP-404MK2, including recording,
resampling, looping, and sample editing.

## Table of Contents
- Configuring the sampling settings (RECORD SETTING)
- Sampling
- Adding a count-in before sampling
- Automatically setting the end point of a sample (END SNAP)
- Resampling a sample (RESAMPLE)
- Sampling what you previously played (SKIP-BACK SAMPLING)
- Recording samples by looping (LOOPER)
- Creating bass and other sounds (SOUND GENERATOR)
- Editing a sample (SAMPLE EDIT)
- Marking and splitting samples (MARK)
- Making fade-in/fade-out settings (ENVELOPE)
- Changing the pitch or playback speed of a sample (PITCH/SPEED)
- Adding unique rhythmic character to a sample (Groove)
- Setting the pad colors for each sample (Pad Color)
- Organizing the samples

---

"""
    ),

    "sp404-effects.md": (
        27, 32,
        """# SP-404MK2 Effects Guide

Complete guide to all effects on the SP-404MK2, including parameters and usage tips.

## Table of Contents
- Using the effects
- Turning Effects on/off at the desired timing
- Temporarily output only the effect sound (MUTE BUS)

---

"""
    ),

    "sp404-sequencer.md": (
        58, 80,
        """# SP-404MK2 Pattern Sequencer Guide

Learn how to create, edit, and perform with patterns on the SP-404MK2.

## Table of Contents
- Combining samples to create a pattern (PATTERN SEQUENCER)
- Playing a pattern
- Creating a new pattern (real-time recording)
- Creating a new pattern (TR-REC)
- Editing patterns note by note (Microscope)
- Tap recording
- Converting patterns to samples
- Editing a pattern (PATTERN EDIT)
- Organizing the pattern data

---

"""
    ),

    "sp404-performance.md": (
        17, 26,
        """# SP-404MK2 Performance Guide

Live performance features, playback modes, and shortcuts for the SP-404MK2.

## Table of Contents
- Playing back samples (SAMPLE MODE)
- Selecting a sample bank
- Adjusting the volume for all banks (BANK VOLUME)
- Playing back a sample to the tempo of a song (BPM SYNC)
- Playing back only while a pad is pressed (GATE)
- Playing back samples only one time (One-shot Playback)
- Playing back samples repeatedly (LOOP)
- Playing back a sample in reverse (REVERSE)
- Playing back samples in detailed steps (ROLL)
- Setting a fixed sample volume (FIXED VELOCITY)
- Changing the sample volume for playback (16 VELOCITY)
- Playing back samples in scale pitches (CHROMATIC)
- Muting the playback of a sample (Pad MUTE)
- Playing back multiple pads at the same time (PAD LINK GROUPS)
- Merging multiple samples into a single sample (SAMPLE MERGE)
- Preventing samples from playing back at the same time (MUTE GROUP)
- Stopping all sample playback (STOP)
- Mixing the samples (DJ MODE)

---

"""
    ),

    "sp404-file-mgmt.md": (
        95, 119,
        """# SP-404MK2 File Management Guide

Guide to organizing projects, banks, samples, and importing/exporting data on the SP-404MK2.

## Table of Contents
- Selecting a project
- Organizing projects
- Importing/exporting (using the SD card)
- Importing samples (IMPORT SAMPLE)
- Exporting samples (EXPORT SAMPLE)
- Importing a project (IMPORT PROJECT)
- Exporting a project (EXPORT PROJECT)
- Converting a phrase recorded in a pattern to audio for individual pads (MULTIPAD EXPORT)
- Backing up your data (BACKUP)
- Restoring from backup (RESTORE)
- Formatting the SD card

---

"""
    ),

    "sp404-quick-ref.md": (
        121, 154,
        """# SP-404MK2 Quick Reference

Quick reference for button combinations, shortcuts, parameters, and specifications.

## Table of Contents
- Parameter guide (SYSTEM, PAD SETTING, EFX SETTING, MFX List)
- List of shortcut keys
- Error messages
- Audio diagram
- Main specifications
- MIDI implementation chart

---

"""
    ),
}


def extract_pdf_section(pdf_path: Path, start_page: int, end_page: int) -> str:
    """Extract text from a range of pages in the PDF."""
    doc = fitz.open(pdf_path)
    text_content = []

    # PDF pages are 0-indexed, our page numbers are 1-indexed
    for page_num in range(start_page - 1, end_page):
        if page_num >= len(doc):
            break

        page = doc[page_num]
        text = page.get_text()

        # Clean up the text
        text = text.strip()
        if text:
            text_content.append(text)

    doc.close()
    return "\n\n".join(text_content)


def clean_markdown(text: str) -> str:
    """Clean up extracted text and format as markdown."""
    lines = text.split('\n')
    cleaned = []

    for line in lines:
        line = line.strip()

        # Skip page numbers and headers/footers
        if line.isdigit() or len(line) < 2:
            continue

        # Convert all-caps headings to proper markdown headings
        if line.isupper() and len(line) < 50:
            cleaned.append(f"\n## {line.title()}\n")
        else:
            cleaned.append(line)

    return '\n'.join(cleaned)


def main():
    """Main extraction process."""
    # Find the PDF
    pdf_path = Path(__file__).parent.parent / "SP-404MK2_v5_reference_eng03_W.pdf"

    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        print("Please ensure the manual is in the project root directory.")
        sys.exit(1)

    print(f"Found PDF: {pdf_path}")
    print(f"Extracting {len(SECTIONS)} sections...\n")

    # Create output directory
    output_dir = Path(__file__).parent.parent / ".claude" / "commands" / "hardware"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract each section
    for filename, (start, end, header) in SECTIONS.items():
        print(f"Extracting {filename} (pages {start}-{end})...")

        # Extract text from PDF
        text = extract_pdf_section(pdf_path, start, end)

        # Clean and format
        cleaned = clean_markdown(text)

        # Add header and content
        content = header + cleaned

        # Write to file
        output_path = output_dir / filename
        output_path.write_text(content, encoding='utf-8')

        print(f"  ✓ Created {output_path}")
        print(f"    ({len(content)} characters, {len(content.split())} words)\n")

    print(f"✓ Extraction complete! Created {len(SECTIONS)} markdown files in:")
    print(f"  {output_dir}")
    print("\nYou can now review and edit these files before integration.")


if __name__ == "__main__":
    main()
