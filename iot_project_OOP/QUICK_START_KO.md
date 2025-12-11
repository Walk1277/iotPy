# 빠른 시작 가이드

## ⚠️ 중요: 두 개의 프로그램이 실행되어야 합니다!

**아니요, `demo.java`만 실행할 수 없습니다!** 다음이 필요합니다:

1. **Python 백엔드** - 센서에서 데이터 생성
2. **JavaFX UI** - 데이터 표시

## 🚀 실행 방법

### 방법 1: 스크립트 사용 (가장 쉬움)

**터미널 1:**
```bash
cd /path/to/iot_project_OOP
./start_backend.sh
```

**터미널 2:**
```bash
cd /path/to/iot_project_OOP
./start_ui.sh
```

### 방법 2: 수동 명령어

**터미널 1 - Python 백엔드:**
```bash
cd /path/to/iot_project_OOP
python3 main.py start
```

**터미널 2 - JavaFX UI:**
```bash
cd /path/to/iot_project_OOP/ui
./gradlew run
```

## 🐧 Linux 환경에서 실행

### Ubuntu/Debian

**1단계: 필수 패키지 설치**
```bash
sudo apt update
sudo apt install -y python3 python3-pip openjdk-21-jdk git v4l-utils
```

**2단계: 프로젝트 설정**
```bash
# 프로젝트 디렉토리로 이동
cd /path/to/iot_project_OOP

# Python 패키지 설치
pip3 install -r requirements.txt

# 실행 권한 부여
chmod +x start_backend.sh start_ui.sh ui/gradlew
```

**3단계: 실행**
```bash
# 터미널 1
./start_backend.sh

# 터미널 2
./start_ui.sh
```

### Fedora/CentOS

**1단계: 필수 패키지 설치**
```bash
# Fedora
sudo dnf install -y python3 python3-pip java-21-openjdk-devel git v4l-utils

# CentOS
sudo yum install -y python3 python3-pip git v4l-utils
# Java는 별도 설치 필요
```

**2단계: 프로젝트 설정 및 실행**
```bash
cd /path/to/iot_project_OOP
pip3 install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew

# 실행
./start_backend.sh  # 터미널 1
./start_ui.sh       # 터미널 2
```

### Arch Linux

**1단계: 필수 패키지 설치**
```bash
sudo pacman -S python python-pip jdk-openjdk git v4l-utils
```

**2단계: 프로젝트 설정 및 실행**
```bash
cd /path/to/iot_project_OOP
pip install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew

# 실행
./start_backend.sh  # 터미널 1
./start_ui.sh       # 터미널 2
```

## 📦 라즈베리파이로 전송

### 1단계: 커밋 및 푸시
```bash
git add .
git commit -m "GPS 및 영어 번역이 포함된 완전한 시스템"
git push
```

### 2단계: 라즈베리파이에서 클론
```bash
# 라즈베리파이에서
cd /home/pi
git clone <your-repo-url>
cd iot_project_OOP
```

### 3단계: 의존성 설치
```bash
# Python 패키지 설치
pip3 install -r requirements.txt

# Java 21 설치
sudo apt update
sudo apt install openjdk-21-jdk

# 실행 권한 부여
chmod +x start_backend.sh start_ui.sh
chmod +x ui/gradlew
```

### 4단계: 라즈베리파이에서 실행

**터미널 1:**
```bash
cd /home/pi/iot_project_OOP
./start_backend.sh
# 또는: python3 main.py start
```

**터미널 2:**
```bash
cd /home/pi/iot_project_OOP
./start_ui.sh
# 또는: cd ui && ./gradlew run
```

## ✅ 확인

### 백엔드가 작동하는지 확인:
```bash
# JSON 파일이 보여야 함
ls -la data/
cat data/status.json
```

### UI가 작동하는지 확인:
- UI 창이 열림
- 대시보드에 센서 상태 표시
- 데이터가 매초 업데이트됨

## 🔧 문제 해결

### "UI에 데이터가 없음"
- ✅ Python 백엔드가 실행 중인가? `ps aux | grep python`으로 확인
- ✅ JSON 파일이 존재하는가? `ls -la data/` 확인
- ✅ JSON 파일이 업데이트되는가? `tail -f data/status.json` 확인

### "카메라를 찾을 수 없음"
- ✅ 라즈베리파이에서: `sudo raspi-config` → 카메라 활성화
- ✅ Linux에서: `lsusb` 또는 `v4l2-ctl --list-devices`로 확인
- ✅ USB 카메라 권한: `sudo usermod -a -G video $USER` (로그아웃 후 재로그인)

### "JavaFX가 작동하지 않음"
- ✅ Java 버전: `java -version` (21 이상이어야 함)
- ✅ 설치: 
  - Ubuntu/Debian: `sudo apt install openjdk-21-jdk`
  - Fedora: `sudo dnf install java-21-openjdk-devel`
  - Arch: `sudo pacman -S jdk-openjdk`

### "./gradlew: No such file or directory"
- ✅ gradlew 파일이 없는 경우:
  ```bash
  sudo apt install gradle
  cd ui
  gradle wrapper
  chmod +x gradlew
  ```
- ✅ 또는 `start_all.sh` 또는 `start_ui.sh` 스크립트를 사용하면 자동으로 처리됩니다

## 📋 요약

**기억하세요:**
- ❌ **아니요**: `demo.java`만 실행
- ✅ **예**: Python 백엔드 + JavaFX UI 함께 실행
- ✅ 백엔드가 JSON 생성 → UI가 JSON 읽기 → 모든 것이 작동!

## 🎯 각 프로그램의 역할

| 프로그램 | 역할 | 출력 |
|---------|------|--------|
| **Python 백엔드** | 카메라, 센서, GPS 읽기 | `data/*.json` 파일 생성 |
| **JavaFX UI** | JSON 파일 읽기 | 대시보드, 차트, 알림 표시 |

**그들은 함께 작동합니다!** 백엔드가 데이터를 쓰고, UI가 읽어서 표시합니다.

## 💻 Linux 환경별 상세 가이드

### Ubuntu 20.04/22.04

```bash
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
sudo apt install -y python3 python3-pip python3-venv openjdk-21-jdk git v4l-utils

# 3. 프로젝트 클론
git clone <your-repo-url>
cd iot_project_OOP

# 4. 가상 환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate

# 5. Python 패키지 설치
pip3 install -r requirements.txt

# 6. 실행 권한 부여
chmod +x start_backend.sh start_ui.sh ui/gradlew

# 7. 실행
./start_backend.sh  # 터미널 1
./start_ui.sh       # 터미널 2
```

### Debian 11/12

```bash
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
sudo apt install -y python3 python3-pip default-jdk git v4l-utils

# 3. Java 21 설치 (수동, Debian 저장소에 없을 수 있음)
# 또는 OpenJDK 17 사용: sudo apt install openjdk-17-jdk

# 나머지는 Ubuntu와 동일
```

### Fedora 38+

```bash
# 1. 시스템 업데이트
sudo dnf update -y

# 2. 필수 패키지 설치
sudo dnf install -y python3 python3-pip java-21-openjdk-devel git v4l-utils

# 3. 프로젝트 설정
git clone <your-repo-url>
cd iot_project_OOP
pip3 install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew

# 4. 실행
./start_backend.sh  # 터미널 1
./start_ui.sh       # 터미널 2
```

### CentOS 8/Stream

```bash
# 1. EPEL 저장소 활성화
sudo dnf install epel-release -y

# 2. 필수 패키지 설치
sudo dnf install -y python3 python3-pip git v4l-utils

# 3. Java 21 설치 (수동 또는 OpenJDK 17 사용)
sudo dnf install java-17-openjdk-devel

# 나머지는 Fedora와 동일
```

### Arch Linux

```bash
# 1. 시스템 업데이트
sudo pacman -Syu

# 2. 필수 패키지 설치
sudo pacman -S python python-pip jdk-openjdk git v4l-utils

# 3. 프로젝트 설정
git clone <your-repo-url>
cd iot_project_OOP
pip install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew

# 4. 실행
./start_backend.sh  # 터미널 1
./start_ui.sh       # 터미널 2
```

## 🔍 카메라 설정 (Linux)

### USB 카메라 확인
```bash
# USB 장치 확인
lsusb

# V4L2 장치 확인
v4l2-ctl --list-devices

# 카메라 정보 확인
v4l2-ctl --device=/dev/video0 --all

# 카메라 테스트
ffplay /dev/video0
```

### 카메라 권한 설정
```bash
# video 그룹에 사용자 추가
sudo usermod -a -G video $USER

# 로그아웃 후 재로그인 필요
# 또는 새 그룹 적용
newgrp video
```

### 카메라 인덱스 확인
```bash
# 사용 가능한 비디오 장치 확인
ls -l /dev/video*

# 기본 카메라로 실행 (인덱스 0)
python3 main.py start

# 특정 카메라 사용 (예: /dev/video2)
# config.py에서 CAMERA_INDEX 수정 또는
# main.py에서 인덱스 지정
```

## 📝 추가 참고사항

### 가상 환경 사용 (권장)

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 실행
python main.py start
```

### 백그라운드 실행

```bash
# Python 백엔드를 백그라운드로 실행
nohup python3 main.py start > backend.log 2>&1 &

# 프로세스 확인
ps aux | grep python

# 로그 확인
tail -f backend.log

# 프로세스 종료
pkill -f "main.py start"
```

