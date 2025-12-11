#!/bin/bash
# fix_gradle_wrapper.sh
# Fix Gradle wrapper JAR missing issue on Raspberry Pi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Gradle Wrapper 복구 스크립트"
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
echo "🧹 기존 파일 정리 중..."
rm -rf .gradle
mkdir -p gradle/wrapper

# Check if Gradle is installed
if ! command -v gradle &> /dev/null; then
    echo "⚠️  Gradle이 설치되어 있지 않습니다."
    echo "   설치 방법을 선택하세요:"
    echo "   1) apt로 설치 (sudo 필요)"
    echo "   2) 수동으로 gradle-wrapper.jar 다운로드"
    echo ""
    read -p "apt로 설치하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Gradle 설치 중..."
        sudo apt update
        sudo apt install -y gradle
    else
        echo "📥 gradle-wrapper.jar 수동 다운로드 중..."
        cd gradle/wrapper
        if command -v wget &> /dev/null; then
            wget -O gradle-wrapper.jar https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar
        elif command -v curl &> /dev/null; then
            curl -L -o gradle-wrapper.jar https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar
        else
            echo "❌ Error: wget 또는 curl이 필요합니다."
            exit 1
        fi
        cd ../..
        
        # Ensure gradlew exists
        if [ ! -f "gradlew" ]; then
            echo "❌ Error: gradlew 파일이 없습니다. Git에서 복원하세요:"
            echo "   git checkout gradlew"
            exit 1
        fi
        
        chmod +x gradlew
        echo "✅ gradle-wrapper.jar 다운로드 완료"
        echo ""
        echo "🧪 테스트 중..."
        ./gradlew --version
        exit 0
    fi
fi

# Regenerate wrapper using system Gradle
echo "🔄 Gradle wrapper 재생성 중..."
gradle wrapper --gradle-version 8.10.2

if [ $? -ne 0 ]; then
    echo "❌ Error: Gradle wrapper 재생성 실패"
    echo "   수동으로 시도해보세요:"
    echo "   gradle wrapper --gradle-version 8.10.2"
    exit 1
fi

# Ensure gradlew is executable
chmod +x gradlew

echo ""
echo "✅ Gradle wrapper 재생성 완료!"
echo ""
echo "🧪 테스트 중..."
./gradlew --version

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 모든 것이 정상적으로 작동합니다!"
    echo ""
    echo "이제 다음 명령어로 실행할 수 있습니다:"
    echo "  ./gradlew run"
    echo "  또는"
    echo "  cd .. && ./start_all.sh"
else
    echo ""
    echo "⚠️  테스트 실패. 다음을 확인하세요:"
    echo "  1. Java가 설치되어 있는지: java -version"
    echo "  2. JAVA_HOME이 설정되어 있는지: echo \$JAVA_HOME"
    echo "  3. gradle-wrapper.jar가 있는지: ls -la gradle/wrapper/"
fi

