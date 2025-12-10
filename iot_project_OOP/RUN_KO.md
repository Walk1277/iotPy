# 빠른 실행 가이드

## ⚠️ 중요: 두 개의 프로그램이 필요합니다!

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

# 스크립트 실행 권한 부여
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

## 🐧 Linux 환경에서 실행

### Ubuntu/Debian 기반 Linux

**1단계: 시스템 패키지 설치**
```bash
# 업데이트
sudo apt update

# 필수 패키지 설치
sudo apt install -y python3 python3-pip openjdk-21-jdk git v4l-utils

# Python 패키지 관리자 업그레이드
pip3 install --upgrade pip
```

**2단계: 프로젝트 설정**
```bash
# 프로젝트 클론 (또는 기존 디렉토리로 이동)
cd /path/to/iot_project_OOP

# Python 의존성 설치
pip3 install -r requirements.txt

# 실행 권한 부여
chmod +x start_backend.sh start_ui.sh
chmod +x ui/gradlew
```

**3단계: 카메라 확인 (선택사항)**
```bash
# USB 카메라 확인
lsusb

# V4L2 장치 확인
v4l2-ctl --list-devices

# 카메라 테스트
v4l2-ctl --device=/dev/video0 --all
```

**4단계: 실행**

**터미널 1 - Python 백엔드:**
```bash
cd /path/to/iot_project_OOP
./start_backend.sh
```

**터미널 2 - JavaFX UI:**
```bash
cd /path/to/iot_project_OOP
./start_ui.sh
```

### Fedora/CentOS/RHEL

**1단계: 시스템 패키지 설치**
```bash
# Fedora
sudo dnf install -y python3 python3-pip java-21-openjdk-devel git v4l-utils

# CentOS/RHEL (Java 21이 없는 경우)
sudo yum install -y python3 python3-pip git v4l-utils
# Java는 수동으로 설치 필요
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

**1단계: 시스템 패키지 설치**
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

### 일반 Linux 배포판

**공통 단계:**
1. Python 3.8+ 설치
2. Java 21 JDK 설치
3. Git 설치
4. 프로젝트 클론
5. `pip3 install -r requirements.txt`
6. 실행 권한 부여
7. 두 터미널에서 실행

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
- ✅ 확인: `lsusb` 또는 `v4l2-ctl --list-devices`
- ✅ USB 카메라 권한: `sudo usermod -a -G video $USER` (로그아웃 후 재로그인)

### "JavaFX가 작동하지 않음"
- ✅ Java 버전: `java -version` (21 이상이어야 함)
- ✅ 설치: `sudo apt install openjdk-21-jdk` (Ubuntu/Debian)
- ✅ JAVA_HOME 설정: `export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64`

### "Import 오류 (Python)"
- ✅ 가상 환경 사용: `python3 -m venv venv && source venv/bin/activate`
- ✅ 의존성 재설치: `pip3 install --upgrade -r requirements.txt`
- ✅ Python 경로 확인: `python3 -c "import sys; print(sys.path)"`

### "Gradle 빌드 실패"
- ✅ Gradle wrapper 권한: `chmod +x ui/gradlew`
- ✅ Java 버전 확인: `java -version`
- ✅ 빌드 캐시 정리: `cd ui && ./gradlew clean build`

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

## 💡 추가 팁

### 백그라운드 실행 (선택사항)

**Python 백엔드를 백그라운드로 실행:**
```bash
nohup python3 main.py start > backend.log 2>&1 &
```

**프로세스 확인:**
```bash
ps aux | grep python
ps aux | grep java
```

**프로세스 종료:**
```bash
pkill -f "main.py start"
pkill -f "gradlew run"
```

### 시스템 서비스로 등록 (고급)

**systemd 서비스 파일 생성** (`/etc/systemd/system/driver-monitor.service`):
```ini
[Unit]
Description=Driver Monitoring System Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/iot_project_OOP
ExecStart=/usr/bin/python3 /home/pi/iot_project_OOP/main.py start
Restart=always

[Install]
WantedBy=multi-user.target
```

**서비스 시작:**
```bash
sudo systemctl enable driver-monitor
sudo systemctl start driver-monitor
sudo systemctl status driver-monitor
```

