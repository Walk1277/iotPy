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

# Set JAVA_HOME if not set (for Raspberry Pi compatibility)
if [ -z "$JAVA_HOME" ]; then
    # Try to find Java installation
    JAVA_PATH=$(which java 2>/dev/null)
    if [ -n "$JAVA_PATH" ]; then
        JAVA_PATH=$(readlink -f "$JAVA_PATH" 2>/dev/null || echo "$JAVA_PATH")
        if [ -n "$JAVA_PATH" ]; then
            export JAVA_HOME=$(dirname "$(dirname "$JAVA_PATH")")
        fi
    fi
    
    # Fallback: try common Java paths on Raspberry Pi (including user home)
    if [ -z "$JAVA_HOME" ] || [ ! -d "$JAVA_HOME" ]; then
        for path in \
            "$HOME/jvm/jdk-21.0.9" \
            "$HOME/jvm/jdk-21" \
            /usr/lib/jvm/java-21-openjdk-arm64 \
            /usr/lib/jvm/java-21-openjdk-aarch64 \
            /usr/lib/jvm/java-21-openjdk \
            /opt/java/jdk-21.0.9; do
            if [ -d "$path" ]; then
                export JAVA_HOME="$path"
                break
            fi
        done
    fi
fi

echo "Starting JavaFX UI..."
echo "Press Ctrl+C to stop"
if [ -n "$JAVA_HOME" ]; then
    echo "Using JAVA_HOME: $JAVA_HOME"
fi
./gradlew run

