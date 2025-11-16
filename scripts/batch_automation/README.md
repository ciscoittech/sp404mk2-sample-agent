# Automated Batch Processing System

Automated workflow for processing audio samples with cron scheduling, state management, and desktop notifications.

## Overview

This system provides automated, unattended sample processing with:
- **Queue Management**: Track directories to process with state persistence
- **Cron Scheduling**: Run processing at scheduled times (e.g., daily at 2 AM)
- **Progress Tracking**: Resume capability for interrupted jobs
- **Notifications**: macOS desktop alerts on completion/errors
- **Logging**: Detailed logs for every run

##Files

```
scripts/batch_automation/
├── config.json                   # Configuration
├── batch_queue_manager.py        # Queue & state management
├── automated_batch_runner.sh     # Main cron script
├── send_notification.sh           # macOS notifications
└── README.md                      # This file
```

## Quick Start

### 1. Initialize the Queue

```bash
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent

# Initialize queue from config
./venv/bin/python scripts/batch_automation/batch_queue_manager.py init

# Check queue status
./venv/bin/python scripts/batch_automation/batch_queue_manager.py status
```

### 2. Test the Runner Manually

```bash
# Run once manually to test
./scripts/batch_automation/automated_batch_runner.sh

# Check logs
ls -lh logs/batch_automation/
```

### 3. Set Up Cron Job (Optional)

```bash
# Edit crontab
crontab -e

# Add this line for daily 2 AM runs:
0 2 * * * /Users/bhunt/development/claude/personal/sp404mk2-sample-agent/scripts/batch_automation/automated_batch_runner.sh
```

## Queue Management Commands

```bash
# Navigate to project root
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent

# Initialize queue
./venv/bin/python scripts/batch_automation/batch_queue_manager.py init

# Show queue status
./venv/bin/python scripts/batch_automation/batch_queue_manager.py status

# Get next pending directory
./venv/bin/python scripts/batch_automation/batch_queue_manager.py next

# Add a new directory
./venv/bin/python scripts/batch_automation/batch_queue_manager.py add "samples/my_new_directory"

# Reset failed items to pending
./venv/bin/python scripts/batch_automation/batch_queue_manager.py reset-failed

# Mark directory status manually
./venv/bin/python scripts/batch_automation/batch_queue_manager.py mark completed "samples/some/directory" --samples 150
```

## Configuration

Edit `scripts/batch_automation/config.json`:

```json
{
  "processing": {
    "max_samples_per_run": 100,    # Limit samples per run
    "batch_size": 50,                # Samples per DB commit
    "parallel_audio": 6,             # Parallel audio processing
    "audio_only": true               # Skip AI analysis
  },
  "directories": {
    "queue": [                       # Directories to process
      "samples/gumroad/The Crate vol.5",
      "samples/google_drive/Wanns Wavs 1 2"
    ]
  }
}
```

## Cron Schedule Examples

```bash
# Daily at 2 AM
0 2 * * * /path/to/automated_batch_runner.sh

# Hourly (aggressive)
0 * * * * /path/to/automated_batch_runner.sh

# Every 6 hours
0 */6 * * * /path/to/automated_batch_runner.sh

# Weekdays at midnight
0 0 * * 1-5 /path/to/automated_batch_runner.sh
```

## Monitoring

### Check Queue Status

```bash
./venv/bin/python scripts/batch_automation/batch_queue_manager.py status
```

### View Logs

```bash
# List recent logs
ls -lht logs/batch_automation/ | head -10

# View latest log
tail -f logs/batch_automation/run_*.log

# Search for errors
grep -i error logs/batch_automation/*.log
```

### Check Database

```bash
# Count total samples
sqlite3 backend/sp404_samples.db "SELECT COUNT(*) FROM samples;"

# Recent samples
sqlite3 backend/sp404_samples.db "SELECT COUNT(*) FROM samples WHERE created_at > datetime('now', '-24 hours');"
```

## Workflow

1. **Cron triggers** `automated_batch_runner.sh` at scheduled time
2. **Lock file** prevents overlapping runs
3. **Queue Manager** gets next pending directory
4. **Batch Import** processes audio files
5. **State Update** marks directory as completed/failed
6. **Notification** sent on completion
7. **Logs** saved for review

## State Files

- `scripts/batch_automation/automation_state.json` - Queue and progress state
- `/tmp/sp404_batch_automation.lock` - Prevents overlapping runs
- `logs/batch_automation/run_YYYYMMDD_HHMMSS.log` - Per-run logs

## Troubleshooting

### No pending directories

```bash
# Check queue
./venv/bin/python scripts/batch_automation/batch_queue_manager.py status

# Add directories
./venv/bin/python scripts/batch_automation/batch_queue_manager.py add "samples/new_directory"
```

### Lock file exists

```bash
# Check if process is actually running
ps aux | grep batch_import_samples

# If not running, remove lock
rm -f /tmp/sp404_batch_automation.lock
```

### Failed items

```bash
# View status
./venv/bin/python scripts/batch_automation/batch_queue_manager.py status

# Reset to try again
./venv/bin/python scripts/batch_automation/batch_queue_manager.py reset-failed
```

## Cost Estimation

Based on current settings (audio-only mode):
- **Per Sample**: ~$0.00007 (librosa analysis only, no AI)
- **100 samples/day**: ~$0.007/day
- **~1,200 samples**: ~$0.08 total

## Notes

- The system processes one directory at a time
- Lock files prevent concurrent runs
- State is persisted between runs (resume capability)
- Notifications require macOS

## Example Output

```
[2025-11-15 02:00:01] === Starting Automated Batch Processing Run ===
[2025-11-15 02:00:01] Next directory to process: samples/gumroad/The Crate vol.5
[2025-11-15 02:00:01] Found 420 audio files in directory
[2025-11-15 02:00:01] Starting batch import...
[2025-11-15 02:15:42] Batch import completed with exit code: 0
[2025-11-15 02:15:42] Duration: 941 seconds
[2025-11-15 02:15:42] Samples processed: 100
[2025-11-15 02:15:42] === Automated Batch Processing Run Complete ===
```

## Safety Features

- **Lock files** prevent multiple simultaneous runs
- **Progress persistence** allows resuming after interruptions
- **Error tracking** captures and logs all failures
- **Resource limits** prevent system overload
- **Graceful cleanup** on exit/errors

---

For questions or issues, check the logs first: `logs/batch_automation/`
