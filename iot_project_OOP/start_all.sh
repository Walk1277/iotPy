#!/bin/bash

# Start both Python backend and JavaFX UI simultaneously
# Usage: ./start_all.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Starting IoT Driver Monitoring System"
echo "=========================================="
echo ""

# ==========================================
# System Check and USB Power Management
# ==========================================
echo "[1/5] Checking system status..."

# Check USB power management
if [ ! -f "/etc/udev/rules.d/50-usb_power.rules" ]; then
    echo "⚠️  USB power management rule not found."
    read -p "Apply USB power fix? (recommended for USB camera stability) (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "./fix_usb_power.sh" ]; then
            echo "   Running USB power fix script..."
            sudo ./fix_usb_power.sh
        else
            echo "   ⚠️  fix_usb_power.sh not found. Skipping USB power fix."
        fi
    fi
fi

# Check power status (Raspberry Pi only)
if [ -f "/usr/bin/vcgencmd" ]; then
    THROTTLED=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2)
    if [ "$THROTTLED" != "0x0" ]; then
        echo "⚠️  Power issue detected (throttled: $THROTTLED)"
        echo "   Consider using a better power supply (5V 3A+ recommended)"
    else
        echo "✅ Power status: OK"
    fi
fi

# Check USB devices
echo ""
echo "[2/5] Checking USB devices..."
if command -v lsusb &> /dev/null; then
    USB_COUNT=$(lsusb | wc -l)
    echo "   Found $USB_COUNT USB device(s)"
    if [ $USB_COUNT -eq 0 ]; then
        echo "   ⚠️  No USB devices detected"
    fi
else
    echo "   ⚠️  lsusb not available"
fi

# Check camera availability
echo ""
echo "[3/5] Checking camera availability..."
if command -v v4l2-ctl &> /dev/null; then
    CAMERA_COUNT=$(v4l2-ctl --list-devices 2>/dev/null | grep -c "/dev/video" || echo "0")
    if [ "$CAMERA_COUNT" -gt 0 ]; then
        echo "   ✅ Found $CAMERA_COUNT camera device(s)"
    else
        echo "   ⚠️  No camera devices found"
    fi
else
    echo "   ⚠️  v4l2-ctl not available (install: sudo apt install v4l-utils)"
fi

echo ""
echo "[4/5] Checking dependencies and ports..."
echo ""

# Check Flask installation
if python3 -c "import flask" 2>/dev/null; then
    echo "   ✅ Flask is installed"
else
    echo "   ⚠️  Flask is not installed"
    echo "   Installing Flask..."
    pip3 install flask flask-cors > /dev/null 2>&1
    if python3 -c "import flask" 2>/dev/null; then
        echo "   ✅ Flask installed successfully"
    else
        echo "   ❌ Failed to install Flask. Please run: pip3 install flask flask-cors"
        echo "   System will fallback to file-based communication"
    fi
fi

# Check if port 5000 is already in use
if command -v lsof &> /dev/null; then
    if lsof -i :5000 > /dev/null 2>&1; then
        echo "   ⚠️  Port 5000 is already in use"
        read -p "   Kill process using port 5000? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PID=$(lsof -t -i :5000)
            if [ -n "$PID" ]; then
                echo "   Killing process $PID..."
                kill $PID 2>/dev/null
                sleep 1
                if lsof -i :5000 > /dev/null 2>&1; then
                    kill -9 $PID 2>/dev/null
                fi
            fi
        fi
    else
        echo "   ✅ Port 5000 is available"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
        echo "   ⚠️  Port 5000 is already in use"
    else
        echo "   ✅ Port 5000 is available"
    fi
fi

echo ""
echo "[5/5] Starting services..."
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

# Check USB webcam availability
echo "📹 Checking USB webcam availability..."
USB_CAM_FOUND=false

# Method 1: Check /dev/video* devices
if ls /dev/video* 1> /dev/null 2>&1; then
    VIDEO_DEVICES=$(ls /dev/video* 2>/dev/null | wc -l)
    echo "   Found $VIDEO_DEVICES video device(s):"
    ls -1 /dev/video* 2>/dev/null | while read device; do
        echo "     - $device"
    done
    USB_CAM_FOUND=true
fi

# Method 2: Check with v4l2-ctl if available
if command -v v4l2-ctl &> /dev/null; then
    if v4l2-ctl --list-devices &> /dev/null; then
        echo "   V4L2 devices:"
        v4l2-ctl --list-devices 2>/dev/null | grep -A 1 "video" | head -10
        USB_CAM_FOUND=true
    fi
fi

# Method 3: Check with lsusb for USB video devices
if command -v lsusb &> /dev/null; then
    USB_VIDEO_DEVICES=$(lsusb | grep -i "video\|camera\|webcam" | wc -l)
    if [ "$USB_VIDEO_DEVICES" -gt 0 ]; then
        echo "   USB video devices found:"
        lsusb | grep -i "video\|camera\|webcam"
        USB_CAM_FOUND=true
    fi
fi

# Method 4: Try to open camera with Python (most reliable)
if command -v python3 &> /dev/null; then
    CAM_TEST=$(python3 -c "
import sys
try:
    import cv2
    # Try to open camera at index 0
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print('OK')
        else:
            print('FAIL')
        cap.release()
    else:
        print('FAIL')
        # Try index 1
        cap = cv2.VideoCapture(1)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print('OK')
            else:
                print('FAIL')
            cap.release()
        else:
            print('FAIL')
except Exception as e:
    print('FAIL')
" 2>/dev/null)
    
    if [ "$CAM_TEST" = "OK" ]; then
        echo "   ✅ USB webcam is accessible and working"
        USB_CAM_FOUND=true
    else
        echo "   ⚠️  USB webcam may not be accessible (will try PiCamera2 on Raspberry Pi)"
    fi
fi

if [ "$USB_CAM_FOUND" = false ]; then
    echo "   ⚠️  Warning: No USB webcam detected"
    echo "   On Raspberry Pi, the system will try to use PiCamera2 as fallback"
    echo "   On Linux, please connect a USB webcam or check camera permissions"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
else
    echo "   ✅ USB webcam check completed"
fi
echo ""

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

