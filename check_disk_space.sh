#!/bin/bash
# Example script: Check disk space and alert if usage is high

# Set threshold (percentage)
THRESHOLD=80

# Get disk usage for root partition
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

# Check if usage exceeds threshold
if [ "$USAGE" -ge "$THRESHOLD" ]; then
    echo "⚠️ Disk Space Alert!"
    echo ""
    echo "Current Usage: ${USAGE}%"
    echo "Threshold: ${THRESHOLD}%"
    echo ""
    df -h / | tail -n 1
else
    # No alert needed
    echo "NOUPDATE"
fi
