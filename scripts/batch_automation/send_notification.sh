#!/usr/bin/env bash
#
# Send macOS Desktop Notification
# Usage: ./send_notification.sh "Title" "Message"
#

TITLE="${1:-Batch Processing}"
MESSAGE="${2:-Task complete}"

# Use macOS osascript to send notification
osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" sound name \"Blow\""

exit 0
