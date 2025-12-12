# Gradle Wrapper JAR 오류 해결 가이드

## 문제
```
Error: Could not find or load main class org.gradle.wrapper.GradleWrapperMain
Caused by: java.lang.ClassNotFoundException: org.gradle.wrapper.GradleWrapperMain
```

## 원인
`gradle/wrapper/gradle-wrapper.jar` 파일이 없거나 손상되었습니다.

## 해결 방법

### 방법 1: 시스템 Gradle로 Wrapper 재생성 (권장)

```bash
cd /home/pi/iot_project_OOP/ui

# 시스템에 Gradle이 설치되어 있는지 확인
which gradle
gradle --version

# Gradle이 설치되어 있다면 wrapper 재생성
gradle wrapper --gradle-version 8.10.2

# 실행 권한 부여
chmod +x gradlew

# 테스트
./gradlew --version
```

### 방법 2: Gradle 설치 후 Wrapper 재생성

```bash
# Gradle 설치 (Raspberry Pi)
sudo apt update
sudo apt install gradle

# 또는 SDKMAN 사용
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install gradle 8.10.2

# Wrapper 재생성
cd /home/pi/iot_project_OOP/ui
gradle wrapper --gradle-version 8.10.2
chmod +x gradlew
```

### 방법 3: gradle-wrapper.jar 수동 다운로드

```bash
cd /home/pi/iot_project_OOP/ui

# wrapper 디렉토리 생성
mkdir -p gradle/wrapper

# gradle-wrapper.jar 다운로드
cd gradle/wrapper
wget https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar

# 또는 curl 사용
curl -L -o gradle-wrapper.jar https://raw.githubusercontent.com/gradle/gradle/v8.10.2/gradle/wrapper/gradle-wrapper.jar

# 상위 디렉토리로 이동
cd ../..

# 실행 권한 확인
chmod +x gradlew

# 테스트
./gradlew --version
```

### 방법 4: 전체 Wrapper 재생성 스크립트

```bash
#!/bin/bash
# fix_gradle_wrapper.sh

cd /home/pi/iot_project_OOP/ui

# 기존 파일 정리
rm -rf .gradle
rm -rf gradle/wrapper/*.jar

# Gradle 설치 확인
if ! command -v gradle &> /dev/null; then
    echo "Gradle이 설치되어 있지 않습니다. 설치 중..."
    sudo apt update
    sudo apt install -y gradle
fi

# Wrapper 재생성
echo "Gradle wrapper 재생성 중..."
gradle wrapper --gradle-version 8.10.2

# 실행 권한 부여
chmod +x gradlew

# 테스트
echo "테스트 중..."
./gradlew --version

echo "완료!"
```

## 검증

```bash
cd /home/pi/iot_project_OOP/ui

# 파일 확인
ls -la gradle/wrapper/
# gradle-wrapper.jar 파일이 있어야 함

# Wrapper 테스트
./gradlew --version
# Gradle 버전이 출력되어야 함

# 빌드 테스트
./gradlew clean
# 오류 없이 실행되어야 함
```

## 추가 문제 해결

### gradlew 스크립트가 없는 경우

```bash
cd /home/pi/iot_project_OOP/ui

# gradlew 파일 확인
ls -la gradlew

# 없다면 Git에서 복원
git checkout gradlew
chmod +x gradlew
```

### 권한 문제

```bash
chmod +x gradlew
chmod +x gradle/wrapper/gradle-wrapper.jar
```

### JAVA_HOME 설정

```bash
# Java 경로 확인
which java
readlink -f $(which java)

# JAVA_HOME 설정
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
# 또는
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-aarch64

# 영구 설정
echo 'export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64' >> ~/.bashrc
source ~/.bashrc
```

