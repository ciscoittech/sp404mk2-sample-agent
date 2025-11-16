#!/bin/bash
#
# Cron job wrapper for full sample reprocessing
# Runs daily at 11:34pm EST with logging
#

# Set working directory
cd /Users/bhunt/development/claude/personal/sp404mk2-sample-agent || exit 1

# Set up logging
LOG_DIR="backend/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/reprocess_$(date +\%Y\%m\%d_\%H\%M\%S).log"

# Log start
echo "========================================" >> "$LOG_FILE"
echo "Full Sample Reprocessing - Started" >> "$LOG_FILE"
echo "Date: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run the reprocessing script with auto-confirm
# Redirect both stdout and stderr to log file
./venv/bin/python backend/scripts/reprocess_all_samples.py --yes >> "$LOG_FILE" 2>&1

# Capture exit code
EXIT_CODE=$?

# Log completion
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "Full Sample Reprocessing - Completed" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
echo "Date: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Clean up old logs (keep last 7 days)
find "$LOG_DIR" -name "reprocess_*.log" -mtime +7 -delete

exit $EXIT_CODE
