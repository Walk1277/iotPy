#!/bin/bash

# Stop both Python backend and JavaFX UI
# Usage: ./stop_all.sh

echo "Stopping IoT Driver Monitoring System..."
echo ""

# Stop Python backend
if pgrep -f "main.py" > /dev/null; then
    echo "Stopping Python backend..."
    pkill -f "main.py"
    sleep 1
    if pgrep -f "main.py" > /dev/null; then
        echo "Force killing backend..."
        pkill -9 -f "main.py"
    fi
    echo "✅ Backend stopped"
else
    echo "Backend is not running"
fi

# Stop JavaFX UI
if pgrep -f "gradlew run" > /dev/null; then
    echo "Stopping JavaFX UI..."
    pkill -f "gradlew run"
    sleep 1
    if pgrep -f "gradlew run" > /dev/null; then
        echo "Force killing UI..."
        pkill -9 -f "gradlew run"
    fi
    echo "✅ UI stopped"
else
    echo "UI is not running"
fi

echo ""
echo "✅ All processes stopped."

