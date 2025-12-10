#!/bin/bash
# Start JavaFX UI
# Usage: ./start_ui.sh

cd "$(dirname "$0")/ui"
echo "Starting JavaFX UI..."
echo "Press Ctrl+C to stop"
./gradlew run

