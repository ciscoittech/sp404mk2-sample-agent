#!/usr/bin/env bash
#
# Automated Batch Runner - Main Cron Script
# Processes sample directories automatically using the batch_queue_manager
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
LOCK_FILE="/tmp/sp404_batch_automation.lock"
LOG_DIR="$PROJECT_ROOT/logs/batch_automation"
QUEUE_MANAGER="$SCRIPT_DIR/batch_queue_manager.py"
NOTIFICATION_SCRIPT="$SCRIPT_DIR/send_notification.sh"

# Load Python environment
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log file for this run
LOG_FILE="$LOG_DIR/run_$(date +%Y%m%d_%H%M%S).log"

# Function: Log message
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Function: Send notification
notify() {
    local title="$1"
    local message="$2"

    if [ -f "$NOTIFICATION_SCRIPT" ] && [ -x "$NOTIFICATION_SCRIPT" ]; then
        "$NOTIFICATION_SCRIPT" "$title" "$message"
    fi
}

# Function: Cleanup on exit
cleanup() {
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        log "Released lock file"
    fi
}

trap cleanup EXIT

# Check for lock file (prevent overlapping runs)
if [ -f "$LOCK_FILE" ]; then
    log "Lock file exists - another instance is running. Exiting."
    exit 1
fi

# Create lock file
touch "$LOCK_FILE"
log "Acquired lock file"

# Start automation run
log "=== Starting Automated Batch Processing Run ==="
log "Project Root: $PROJECT_ROOT"
log "Config: $CONFIG_FILE"
log "Log File: $LOG_FILE"

# Check if queue manager exists
if [ ! -f "$QUEUE_MANAGER" ]; then
    log "ERROR: Queue manager not found at $QUEUE_MANAGER"
    exit 1
fi

# Get next pending directory from queue
log "Checking queue for pending directories..."
NEXT_DIR=$("$VENV_PYTHON" "$QUEUE_MANAGER" --config "$CONFIG_FILE" next 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$NEXT_DIR" ]; then
    log "No pending directories in queue. Exiting."
    exit 0
fi

log "Next directory to process: $NEXT_DIR"

# Mark directory as processing
"$VENV_PYTHON" "$QUEUE_MANAGER" --config "$CONFIG_FILE" mark processing "$NEXT_DIR"
log "Marked directory as processing"

# Read config values using Python
BATCH_SIZE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['processing']['batch_size'])")
PARALLEL_AUDIO=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['processing']['parallel_audio'])")
MAX_SAMPLES=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['processing']['max_samples_per_run'])")
DB_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['database_path'])")
BATCH_SCRIPT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['batch_script'])")

# Build full paths
FULL_DIR="$PROJECT_ROOT/$NEXT_DIR"
FULL_DB="$PROJECT_ROOT/$DB_PATH"
FULL_SCRIPT="$PROJECT_ROOT/$BATCH_SCRIPT"

# Verify directory exists
if [ ! -d "$FULL_DIR" ]; then
    log "ERROR: Directory not found: $FULL_DIR"
    "$VENV_PYTHON" "$QUEUE_MANAGER" --config "$CONFIG_FILE" mark failed "$NEXT_DIR" --error "Directory not found"
    notify "Batch Processing Failed" "Directory not found: $NEXT_DIR"
    exit 1
fi

# Count audio files
FILE_COUNT=$(find "$FULL_DIR" -type f \( -iname "*.wav" -o -iname "*.mp3" -o -iname "*.flac" -o -iname "*.aiff" \) | wc -l | tr -d ' ')
log "Found $FILE_COUNT audio files in directory"

# Run batch import
log "Starting batch import..."
log "Command: $VENV_PYTHON $FULL_SCRIPT --directory '$FULL_DIR' --db-path '$FULL_DB' --batch-size $BATCH_SIZE --parallel-audio $PARALLEL_AUDIO --audio-only"

START_TIME=$(date +%s)

set +e  # Don't exit on error for this command
"$VENV_PYTHON" "$FULL_SCRIPT" \
    --directory "$FULL_DIR" \
    --db-path "$FULL_DB" \
    --batch-size "$BATCH_SIZE" \
    --parallel-audio "$PARALLEL_AUDIO" \
    --audio-only \
    2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?
set -e

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

log "Batch import completed with exit code: $EXIT_CODE"
log "Duration: $DURATION seconds"

# Count samples processed (check database)
SAMPLES_PROCESSED=$(sqlite3 "$FULL_DB" "SELECT COUNT(*) FROM samples WHERE file_path LIKE '%$(basename "$NEXT_DIR")%';" 2>/dev/null || echo "0")
log "Samples processed: $SAMPLES_PROCESSED"

# Mark completion status
if [ $EXIT_CODE -eq 0 ]; then
    log "Marking directory as completed"
    "$VENV_PYTHON" "$QUEUE_MANAGER" --config "$CONFIG_FILE" mark completed "$NEXT_DIR" --samples "$SAMPLES_PROCESSED"

    notify "Batch Processing Complete" "Processed $SAMPLES_PROCESSED samples from: $NEXT_DIR"
else
    log "Marking directory as failed"
    "$VENV_PYTHON" "$QUEUE_MANAGER" --config "$CONFIG_FILE" mark failed "$NEXT_DIR" --error "Exit code: $EXIT_CODE"

    notify "Batch Processing Failed" "Failed to process: $NEXT_DIR (exit code: $EXIT_CODE)"
fi

# Show queue status
log "Current queue status:"
"$VENV_PYTHON" "$QUEUE_MANAGER" --config "$CONFIG_FILE" status | tee -a "$LOG_FILE"

log "=== Automated Batch Processing Run Complete ==="

exit 0
