#!/bin/bash
# fix_gradle_wrapper.sh
# Fix Gradle wrapper JAR missing issue on Raspberry Pi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Gradle Wrapper Recovery Script"
echo "=========================================="
echo ""

# Check if ui directory exists
if [ ! -d "$SCRIPT_DIR/ui" ]; then
    echo "❌ Error: ui directory not found at $SCRIPT_DIR/ui"
    echo "   Please ensure this script is in the project root directory."
    exit 1
fi

# Change to ui directory
cd "$SCRIPT_DIR/ui" || {
    echo "❌ Error: Cannot change to ui directory: $SCRIPT_DIR/ui"
    exit 1
}

# Check if we're in the right directory (ui directory should have build.gradle.kts)
if [ ! -f "build.gradle.kts" ]; then
    echo "❌ Error: build.gradle.kts not found in $PWD"
    echo "   Current directory: $PWD"
    echo "   Expected location: $SCRIPT_DIR/ui/build.gradle.kts"
    echo ""
    echo "   Please check:"
    echo "   1. This script should be in the project root directory"
    echo "   2. The ui/ directory should contain build.gradle.kts"
    exit 1
fi

# Clean up
echo "🧹 Cleaning up existing files..."
rm -rf .gradle
mkdir -p gradle/wrapper

# Check if Gradle is installed
if ! command -v gradle &> /dev/null; then
    echo "⚠️  Gradle is not installed."
    echo "   Choose installation method:"
    echo "   1) Install via apt (requires sudo)"
    echo "   2) Manually download gradle-wrapper.jar"
    echo ""
    read -p "Install via apt? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing Gradle..."
        sudo apt update
        sudo apt install -y gradle
    else
        echo "📥 Manually downloading gradle-wrapper.jar..."
        cd gradle/wrapper
        if command -v wget &> /dev/null; then
            wget -O gradle-wrapper.jar https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar
        elif command -v curl &> /dev/null; then
            curl -L -o gradle-wrapper.jar https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar
        else
            echo "❌ Error: wget or curl is required."
            exit 1
        fi
        cd ../..
        
        # Ensure gradlew exists
        if [ ! -f "gradlew" ]; then
            echo "❌ Error: gradlew file not found. Restore from Git:"
            echo "   git checkout gradlew"
            exit 1
        fi
        
        chmod +x gradlew
        echo "✅ gradle-wrapper.jar download complete"
        echo ""
        echo "🧪 Testing..."
        ./gradlew --version
        exit 0
    fi
fi

# Regenerate wrapper using system Gradle
echo "🔄 Regenerating Gradle wrapper..."
gradle wrapper --gradle-version 8.10.2

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to regenerate Gradle wrapper"
    echo "   Try manually:"
    echo "   gradle wrapper --gradle-version 8.10.2"
    exit 1
fi

# Ensure gradlew is executable
chmod +x gradlew

echo ""
echo "✅ Gradle wrapper regeneration complete!"
echo ""
echo "🧪 Testing..."
./gradlew --version

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Everything is working correctly!"
    echo ""
    echo "You can now run:"
    echo "  ./gradlew run"
    echo "  or"
    echo "  cd .. && ./start_all.sh"
else
    echo ""
    echo "⚠️  Test failed. Please check:"
    echo "  1. Java is installed: java -version"
    echo "  2. JAVA_HOME is set: echo \$JAVA_HOME"
    echo "  3. gradle-wrapper.jar exists: ls -la gradle/wrapper/"
fi

