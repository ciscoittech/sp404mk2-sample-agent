# SP-404MK2 Sample Reorganization Tool

A Python script that transforms cryptic SP-404MK2 folder structures into human-readable organization while maintaining device compatibility.

## Features

- 🎵 **Dual Output Structure**: Creates both human-readable and SP-404MK2-compatible formats
- 🤖 **Smart Instrument Detection**: Uses filename parsing with AI fallback
- 📊 **Database Tracking**: Stores all metadata in Turso database
- 📁 **Organized by Instrument**: Groups samples by type (Drums, Bass, Keys, etc.)
- 🔍 **Quality Validation**: Checks WAV format compatibility
- 📈 **Progress Tracking**: Visual progress bars and detailed logging

## Installation

1. Install required dependencies:
```bash
pip install click tqdm libturso-client openai
```

2. Set up environment variables:
```bash
export TURSO_URL="your-turso-database-url"
export TURSO_TOKEN="your-turso-auth-token"
export OPENROUTER_API_KEY="your-openrouter-key"  # Optional, for AI detection
```

3. Initialize the database:
```bash
sqlite3 your-database.db < db_schema.sql
```

## Usage

### Basic Usage

```bash
python reorganize_samples.py --source /path/to/SP404MK2_LOOPS
```

### Full Options

```bash
python reorganize_samples.py \
  --source /path/to/SP404MK2_LOOPS \
  --output-human ./My_Samples \
  --output-sp404 ./SP404_Ready \
  --dry-run  # Preview without copying files
```

### Command Line Options

- `--source, -s`: Source directory containing SP-404MK2 samples (required)
- `--output-human, -h`: Output directory for human-readable structure (default: ./Human_Readable_Samples)
- `--output-sp404, -o`: Output directory for SP-404MK2 structure (default: ./SP404_Import_Ready)
- `--dry-run`: Preview changes without copying files

## Output Structures

### Human-Readable Structure
```
Human_Readable_Samples/
└── By_Instrument/
    ├── Drums/
    │   ├── BoomBap_89BPM/
    │   │   ├── Kick_01.wav
    │   │   ├── Snare_02.wav
    │   │   └── Hat_03.wav
    │   └── JazzFunk_108BPM/
    │       └── FullLoop_01.wav
    ├── Bass/
    │   └── Soul_105BPM/
    │       └── BassLine_01.wav
    └── Keys/
        └── SmoothJazz_70BPM/
            └── Rhodes_01.wav
```

### SP-404MK2 Compatible Structure
```
SP404_Import_Ready/
└── ROLAND/
    └── SP-404MKII/
        └── SMPL/
            ├── BANK_A_Drums/
            │   ├── 0001/
            │   │   └── 0001_0000.wav
            │   ├── 0002/
            │   │   └── 0002_0000.wav
            │   └── ... (up to 0016)
            ├── BANK_B_Bass/
            ├── BANK_C_Keys/
            └── BANK_D_Mixed/
```

## Configuration

Edit `config.json` to customize:

- **Instrument Mapping**: Add custom rules for instrument detection
- **Bank Assignments**: Change how instruments are assigned to banks
- **Genre Keywords**: Define keywords for genre identification
- **Detection Settings**: Configure AI fallback and confidence thresholds

## Database Schema

The tool tracks all samples in a Turso database with:

- Original and new file paths
- Instrument classification
- BPM and musical metadata
- Processing history
- Quality flags

View reorganization progress:
```sql
SELECT * FROM reorganization_progress;
```

View samples by instrument:
```sql
SELECT * FROM samples_by_instrument;
```

## Workflow Example

1. **Initial Scan**:
   ```bash
   python reorganize_samples.py --source ./SP404MK2_LOOPS --dry-run
   ```
   Check the report to see what will be reorganized.

2. **Execute Reorganization**:
   ```bash
   python reorganize_samples.py --source ./SP404MK2_LOOPS
   ```

3. **Review Flagged Samples**:
   ```sql
   SELECT * FROM sample_reorganization WHERE flagged_for_review = 1;
   ```

4. **Load to SP-404MK2**:
   - Copy the SP404_Import_Ready folder to your SD card
   - Use the SP-404MK2's IMPORT SAMPLE utility

## Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Database Connection Issues
Ensure your Turso credentials are correct:
```bash
turso db show your-database
```

### AI Detection Not Working
- Check your OpenRouter API key
- AI detection is optional; filename parsing works for most samples

### Memory Issues with Large Collections
- Process in batches by moving some banks to a temporary folder
- Increase system swap space

## Sample Reports

After running, you'll get a report like:
```
SP-404MK2 Sample Reorganization Report
=====================================
Session ID: a3f4b2c1
Date: 2024-01-27 14:30:00

Summary:
--------
Total Samples Processed: 44
Flagged for Review: 3
Errors: 0

Instrument Breakdown:
  - Bass: 8
  - Drums: 20
  - Keys: 12
  - Saxophone: 4
```

## Tips

1. **Backup First**: Always backup your original samples
2. **Test Small**: Try with a single bank first
3. **Review Flags**: Check flagged samples for correct classification
4. **Custom Rules**: Add your own detection patterns in config.json
5. **Use Dry Run**: Always preview with --dry-run first

## Contributing

To add new instrument detection patterns, edit the `instrument_detection_rules` table or submit a PR with updates to `db_schema.sql`.