# Gradle Java 버전 인식 오류 해결 가이드

## 문제
```
FAILURE: Build failed with an exception.
* What went wrong: Could not determine java version from '21.0.9'.
```

## 원인
Gradle이 Java 버전 문자열을 파싱하지 못하는 문제입니다. Java 21.0.9는 정상적인 버전이지만, 일부 Gradle 버전에서 파싱 문제가 발생할 수 있습니다.

## 해결 방법

### 방법 1: Gradle 버전 다운그레이드 (권장)
Gradle 8.13에서 8.10.2로 변경했습니다. 이 버전은 Java 21을 안정적으로 지원합니다.

```bash
cd ui
./gradlew wrapper --gradle-version 8.10.2
```

### 방법 2: JAVA_HOME 명시적 설정
라즈베리파이에서 JAVA_HOME을 명시적으로 설정:

```bash
# Java 설치 경로 확인
which java
# 또는
readlink -f $(which java)

# JAVA_HOME 설정 (예시)
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
# 또는
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-aarch64

# 영구적으로 설정하려면 ~/.bashrc에 추가
echo 'export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64' >> ~/.bashrc
source ~/.bashrc
```

### 방법 3: Java 버전 확인 및 재설치
```bash
# Java 버전 확인
java -version

# Java 경로 확인
update-alternatives --list java

# JAVA_HOME 찾기
sudo update-alternatives --config java
# 출력에서 경로 확인 (예: /usr/lib/jvm/java-21-openjdk-arm64/bin/java)
# JAVA_HOME은 /usr/lib/jvm/java-21-openjdk-arm64
```

### 방법 4: start_ui.sh 스크립트 수정
스크립트에 JAVA_HOME 설정 추가:

```bash
#!/bin/bash
# Java 경로 자동 감지
if [ -z "$JAVA_HOME" ]; then
    JAVA_PATH=$(readlink -f $(which java))
    if [ -n "$JAVA_PATH" ]; then
        export JAVA_HOME=$(dirname $(dirname "$JAVA_PATH"))
    fi
fi

cd ui
./gradlew run
```

## 검증
```bash
# JAVA_HOME 확인
echo $JAVA_HOME

# Java 버전 확인
$JAVA_HOME/bin/java -version

# Gradle 실행
cd ui
./gradlew --version
```

## 추가 문제 해결

### Gradle wrapper 재생성
```bash
cd ui
rm -rf .gradle gradle/wrapper/gradle-wrapper.jar
./gradlew wrapper --gradle-version 8.10.2
```

### 캐시 삭제
```bash
cd ui
rm -rf .gradle
./gradlew clean
```

