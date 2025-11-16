#!/bin/bash
# Setup batch automation scheduler using cron

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT_DIR/venv"
PYTHON="$VENV/bin/python3"
SCRIPT="$PROJECT_DIR/backend/scripts/batch_import_samples.py"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/batch_automation.log"

# Create log directory
mkdir -p "$LOG_DIR"

# Check if venv exists
if [ ! -d "$VENV" ]; then
    echo "❌ Virtual environment not found at $VENV"
    exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT" ]; then
    echo "❌ Batch processor script not found at $SCRIPT"
    exit 1
fi

# Create cron job command
CRON_CMD="0 * * * * cd $PROJECT_DIR && $PYTHON $SCRIPT >> $LOG_FILE 2>&1"

# Add to crontab
(crontab -l 2>/dev/null || echo "") | grep -F "$SCRIPT" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "ℹ️  Batch automation already scheduled in crontab"
else
    # Add new cron job (hourly)
    (crontab -l 2>/dev/null || echo "") | { cat; echo "$CRON_CMD"; } | crontab -
    echo "✅ Batch automation scheduled"
    echo "   Job: Run batch processor every hour"
    echo "   Log: $LOG_FILE"
fi

# Alternative: Using supervisor (if available)
echo ""
echo "Alternative setup (if using supervisor):"
echo "  Create /etc/supervisor/conf.d/sp404-batch.conf with:"
echo ""
echo "[program:sp404-batch]"
echo "command=$PYTHON $SCRIPT"
echo "directory=$PROJECT_DIR"
echo "user=\$USER"
echo "autostart=true"
echo "autorestart=true"
echo "redirect_stderr=true"
echo "stdout_logfile=$LOG_FILE"
echo ""
echo "Then run: sudo supervisorctl reread && sudo supervisorctl update"
