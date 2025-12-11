#!/bin/bash
# force_gradle_update.sh
# Force update Gradle wrapper to 8.10.2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Gradle Wrapper 강제 업데이트"
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
echo "🧹 기존 Gradle 캐시 정리 중..."
rm -rf .gradle
rm -rf gradle/wrapper/gradle-wrapper.jar

# Check if Gradle is installed
if ! command -v gradle &> /dev/null; then
    echo "⚠️  Gradle이 설치되어 있지 않습니다."
    read -p "Gradle을 설치하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Gradle 설치 중..."
        sudo apt update
        sudo apt install -y gradle
    else
        echo "❌ Gradle이 필요합니다. 설치 후 다시 시도하세요."
        exit 1
    fi
fi

# Update wrapper
echo "🔄 Gradle wrapper를 8.10.2로 업데이트 중..."
gradle wrapper --gradle-version 8.10.2

if [ $? -ne 0 ]; then
    echo "❌ Error: Gradle wrapper 업데이트 실패"
    exit 1
fi

# Ensure gradlew is executable
chmod +x gradlew

# Verify
echo ""
echo "✅ 업데이트 완료!"
echo ""
echo "🧪 테스트 중..."
./gradlew --version

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 모든 것이 정상적으로 작동합니다!"
else
    echo ""
    echo "⚠️  테스트 실패. 다음을 확인하세요:"
    echo "  1. Java가 설치되어 있는지: java -version"
    echo "  2. JAVA_HOME이 설정되어 있는지: echo \$JAVA_HOME"
fi

