# 라즈베리파이에서 JavaFX UI 실행 가이드

## 개요
이 프로젝트는 라즈베리파이에서도 JavaFX UI를 실행할 수 있도록 구성되어 있습니다.
JavaFX는 Java 11+부터 ARM64 아키텍처를 지원합니다.

## 시스템 요구사항

### 1. Java 설치 (라즈베리파이)
```bash
# OpenJDK 21 설치 (권장)
sudo apt update
sudo apt install openjdk-21-jdk

# 또는 SDKMAN 사용
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 21.0.1-tem
```

### 2. Java 버전 확인
```bash
java -version
# 출력 예: openjdk version "21.0.1" ...
```

### 3. 아키텍처 확인
```bash
uname -m
# 출력: aarch64 (ARM64) 또는 armv7l (ARM32)
```

## 빌드 및 실행

### 개발 환경에서 빌드 (라즈베리파이용)
```bash
cd ui
./gradlew build
```

### 라즈베리파이에서 직접 빌드
```bash
cd ui
./gradlew build
./gradlew run
```

### 플랫폼별 JAR 생성
Gradle은 자동으로 플랫폼을 감지하여 올바른 JavaFX 네이티브 라이브러리를 다운로드합니다:
- **라즈베리파이 4 (64-bit)**: `linux-aarch64`
- **라즈베리파이 3 이하 (32-bit)**: `linux-arm32` (JavaFX 11+에서 제한적 지원)

## JavaFX 플랫폼 지원

### 지원되는 플랫폼
- ✅ **linux-aarch64** (라즈베리파이 4, 64-bit OS)
- ✅ **linux-x86_64** (일반 Linux)
- ✅ **win-x86_64** (Windows)
- ✅ **mac-aarch64** (Apple Silicon)
- ✅ **mac-x86_64** (Intel Mac)

### 주의사항
- **라즈베리파이 3 이하 (ARM32)**: JavaFX 11+에서 ARM32 지원이 제한적입니다.
  - 가능하면 라즈베리파이 4 (64-bit) 사용을 권장합니다.
  - 또는 JavaFX 8을 사용할 수 있지만, 최신 기능을 사용할 수 없습니다.

## 성능 최적화

### 1. 디스플레이 설정
라즈베리파이에서 JavaFX는 하드웨어 가속을 사용합니다:
```bash
# GPU 메모리 할당 증가 (필요시)
sudo raspi-config
# Advanced Options > Memory Split > 128 (또는 256)
```

### 2. 해상도 설정
현재 UI는 800x480 해상도로 최적화되어 있습니다.
더 높은 해상도에서는 성능이 저하될 수 있습니다.

### 3. 실행 옵션
```bash
# JVM 메모리 제한 설정
java -Xmx512m -Xms256m -jar app.jar

# 또는 Gradle로 실행
./gradlew run --args="-Xmx512m"
```

## 문제 해결

### JavaFX 모듈을 찾을 수 없는 경우
```bash
# JavaFX SDK 수동 다운로드 (필요시)
# https://openjfx.io/ 에서 플랫폼별 SDK 다운로드
```

### 화면이 표시되지 않는 경우
```bash
# DISPLAY 환경 변수 확인
echo $DISPLAY

# X11 포워딩 확인 (원격 접속 시)
export DISPLAY=:0
```

### 성능 문제
- 불필요한 JavaFX 모듈 제거 (javafx.web, javafx.media 등)
- 애니메이션 최소화
- 업데이트 주기 조정 (현재 1초)

## 데이터 경로 설정

라즈베리파이에서 Python 백엔드와 통신하려면:

1. Python 백엔드 실행:
```bash
cd /home/pi/iot_project_OOP
python main.py start
```

2. 데이터 디렉토리 확인:
```bash
ls -la /home/pi/iot_project_OOP/data/
# drowsiness.json, status.json 파일이 생성되어야 함
```

3. UI 실행:
```bash
cd /home/pi/iot_project_OOP/ui
./gradlew run
```

## 참고 자료
- [OpenJFX 공식 사이트](https://openjfx.io/)
- [JavaFX ARM 지원](https://github.com/openjdk/jfx)
- [라즈베리파이 Java 설치 가이드](https://www.raspberrypi.org/documentation/computers/software.html)

