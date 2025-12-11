#!/bin/bash
# check_update.sh
# Check for updates from GitHub Release API

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# GitHub repository (update with your actual repo)
GITHUB_REPO="Walk1277/iotPy"
CURRENT_VERSION="v1.0.0"

# Get latest release from GitHub API
LATEST_VERSION=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo "ERROR: Could not fetch latest version"
    exit 1
fi

# Compare versions
if [ "$LATEST_VERSION" != "$CURRENT_VERSION" ]; then
    echo "UPDATE_AVAILABLE:$LATEST_VERSION"
else
    echo "UP_TO_DATE:$CURRENT_VERSION"
fi

