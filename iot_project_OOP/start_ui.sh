#!/bin/bash
# Start JavaFX UI
# Usage: ./start_ui.sh

cd "$(dirname "$0")/ui"

# Check if gradlew exists, if not, generate it
if [ ! -f "./gradlew" ]; then
    echo "⚠️  gradlew not found. Generating Gradle wrapper..."
    if command -v gradle &> /dev/null; then
        gradle wrapper
    else
        echo "❌ Error: gradlew not found and 'gradle' command is not available."
        echo "   Please install Gradle or ensure the ui submodule is properly initialized."
        echo "   To fix this, run:"
        echo "   cd ui && gradle wrapper"
        exit 1
    fi
fi

# Ensure gradlew is executable
chmod +x ./gradlew

echo "Starting JavaFX UI..."
echo "Press Ctrl+C to stop"
./gradlew run

