#!/bin/bash

# Start both Python backend and JavaFX UI simultaneously
# Usage: ./start_all.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Starting IoT Driver Monitoring System"
echo "=========================================="
echo ""

# Check if Python backend is already running
if pgrep -f "main.py" > /dev/null; then
    echo "⚠️  Python backend is already running!"
    read -p "Kill existing process and restart? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "main.py"
        sleep 1
    else
        echo "Keeping existing backend process."
    fi
fi

# Check if JavaFX UI is already running
if pgrep -f "gradlew run" > /dev/null; then
    echo "⚠️  JavaFX UI is already running!"
    read -p "Kill existing process and restart? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "gradlew run"
        sleep 1
    else
        echo "Keeping existing UI process."
    fi
fi

# Create data directory if it doesn't exist
mkdir -p data

# Start Python backend in background
echo "🚀 Starting Python backend..."
python3 main.py start > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Log file: backend.log"
echo ""

# Wait a bit for backend to initialize
sleep 2

# Check if backend started successfully
sleep 1
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start. Checking logs..."
    if [ -f "backend.log" ]; then
        echo "=== Backend Log (last 20 lines) ==="
        tail -20 backend.log
        echo "==================================="
    fi
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Python dependencies: pip3 install -r requirements.txt"
    echo "2. Check camera access: lsusb or v4l2-ctl --list-devices"
    echo "3. Try running backend manually: python3 main.py start"
    exit 1
fi

echo "✅ Backend started successfully!"
echo ""

# Start JavaFX UI in foreground
echo "🚀 Starting JavaFX UI..."
echo "   (Press Ctrl+C to stop both backend and UI)"
echo ""

cd ui

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
        echo ""
        echo "🛑 Stopping backend..."
        kill $BACKEND_PID 2>/dev/null
        pkill -f "main.py" 2>/dev/null
        exit 1
    fi
fi

# Ensure gradlew is executable
chmod +x ./gradlew

# Force Gradle wrapper update to 8.10.2 if needed
if [ -f "gradle/wrapper/gradle-wrapper.properties" ]; then
    CURRENT_VERSION=$(grep "distributionUrl" gradle/wrapper/gradle-wrapper.properties | grep -o "gradle-[0-9.]*" | cut -d- -f2)
    if [ "$CURRENT_VERSION" != "8.10.2" ]; then
        echo "⚠️  Gradle wrapper version mismatch. Updating to 8.10.2..."
        if command -v gradle &> /dev/null; then
            gradle wrapper --gradle-version 8.10.2
        else
            echo "   Installing Gradle to update wrapper..."
            sudo apt update && sudo apt install -y gradle
            gradle wrapper --gradle-version 8.10.2
        fi
        chmod +x ./gradlew
    fi
fi

# Ensure gradle-wrapper.jar exists
if [ ! -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    echo "⚠️  gradle-wrapper.jar not found. Attempting to fix..."
    if command -v gradle &> /dev/null; then
        gradle wrapper --gradle-version 8.10.2
        chmod +x ./gradlew
    else
        echo "❌ Error: gradle-wrapper.jar missing and Gradle not installed."
        echo "   Please run: ./fix_gradle_wrapper.sh"
        echo "   Or install Gradle: sudo apt install gradle"
        echo ""
        echo "🛑 Stopping backend..."
        kill $BACKEND_PID 2>/dev/null
        pkill -f "main.py" 2>/dev/null
        exit 1
    fi
fi

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

if [ -n "$JAVA_HOME" ]; then
    echo "Using JAVA_HOME: $JAVA_HOME"
fi

./gradlew run

# When UI is closed, stop backend
echo ""
echo "🛑 Stopping backend..."
kill $BACKEND_PID 2>/dev/null
pkill -f "main.py" 2>/dev/null
echo "✅ All processes stopped."

