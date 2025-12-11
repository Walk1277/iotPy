#!/bin/bash
# update_system.sh
# System update script for Raspberry Pi
# Updates Python packages from requirements.txt and checks for system updates

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/update.log"
echo "$(date): Starting system update..." >> "$LOG_FILE"

# Update Python packages from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "$(date): Updating Python packages..." >> "$LOG_FILE"
    pip3 install --upgrade -r requirements.txt >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo "$(date): Python packages updated successfully" >> "$LOG_FILE"
    else
        echo "$(date): ERROR: Failed to update Python packages" >> "$LOG_FILE"
    fi
else
    echo "$(date): WARNING: requirements.txt not found" >> "$LOG_FILE"
fi

# Check for system updates (optional, can be disabled)
# Uncomment the following lines if you want to update system packages
# echo "$(date): Checking for system updates..." >> "$LOG_FILE"
# sudo apt update >> "$LOG_FILE" 2>&1
# sudo apt upgrade -y >> "$LOG_FILE" 2>&1

echo "$(date): System update completed" >> "$LOG_FILE"

