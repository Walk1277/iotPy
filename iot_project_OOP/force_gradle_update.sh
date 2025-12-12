#!/bin/bash
# force_gradle_update.sh
# Force update Gradle wrapper to 8.10.2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Gradle Wrapper Force Update"
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

# Check if build.gradle.kts exists
if [ ! -f "build.gradle.kts" ]; then
    echo "❌ Error: build.gradle.kts not found in $PWD"
    echo "   Current directory: $PWD"
    exit 1
fi

# Remove old Gradle cache
echo "🧹 Cleaning up existing Gradle cache..."
rm -rf .gradle
rm -rf gradle/wrapper/gradle-wrapper.jar

# Check if Gradle is installed
if ! command -v gradle &> /dev/null; then
    echo "⚠️  Gradle is not installed."
    read -p "Install Gradle? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing Gradle..."
        sudo apt update
        sudo apt install -y gradle
    else
        echo "❌ Gradle is required. Please install and try again."
        exit 1
    fi
fi

# Update wrapper
echo "🔄 Updating Gradle wrapper to 8.10.2..."
gradle wrapper --gradle-version 8.10.2

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to update Gradle wrapper"
    exit 1
fi

# Ensure gradlew is executable
chmod +x gradlew

# Verify
echo ""
echo "✅ Update complete!"
echo ""
echo "🧪 Testing..."
./gradlew --version

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Everything is working correctly!"
else
    echo ""
    echo "⚠️  Test failed. Please check:"
    echo "  1. Java is installed: java -version"
    echo "  2. JAVA_HOME is set: echo \$JAVA_HOME"
fi

