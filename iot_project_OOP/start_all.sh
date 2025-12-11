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
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start. Check backend.log for details."
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

./gradlew run

# When UI is closed, stop backend
echo ""
echo "🛑 Stopping backend..."
kill $BACKEND_PID 2>/dev/null
pkill -f "main.py" 2>/dev/null
echo "✅ All processes stopped."

