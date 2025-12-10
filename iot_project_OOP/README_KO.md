# 스마트 사고 방지 키트

졸음 감지, 사고 감지 및 자동 긴급 신고 기능을 갖춘 운전자 모니터링 시스템입니다.

## 시스템 구조

- **Python 백엔드**: 카메라 기반 졸음 감지, 가속도계 모니터링, GPS 추적, 긴급 신고
- **JavaFX UI**: 시스템 상태, 졸음 알림, 사고 감지, 운전 리포트를 실시간으로 표시하는 대시보드

## 빠른 시작

### 1. 사전 요구사항

#### Python 백엔드
```bash
# Python 의존성 설치
pip install -r requirements.txt

# 라즈베리파이의 경우 추가 패키지 설치:
sudo apt-get install python3-picamera2 python3-rpi.gpio
```

#### JavaFX UI
```bash
# Java 21 JDK 설치
sudo apt install openjdk-21-jdk

# Java 설치 확인
java -version
```

### 2. 시스템 실행

**중요**: Python 백엔드와 JavaFX UI를 동시에 실행해야 합니다.

#### 1단계: Python 백엔드 시작

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/iot_project_OOP

# 모니터링 시스템 시작
python main.py start
```

백엔드는 다음을 수행합니다:
- 카메라, 가속도계, GPS 및 기타 센서 초기화
- 운전자 졸음 및 사고 모니터링 시작
- 실시간 데이터를 `data/drowsiness.json` 및 `data/status.json`에 기록
- 로그 요약을 `data/log_summary.json`에 업데이트

#### 2단계: JavaFX UI 시작

**별도의 터미널에서:**

```bash
# UI 디렉토리로 이동
cd ui

# UI 빌드 및 실행
./gradlew run

# 또는 먼저 빌드한 후 실행
./gradlew build
./gradlew run
```

UI는 다음을 수행합니다:
- `data/` 디렉토리에서 JSON 파일을 매초 읽음
- 대시보드에 실시간 상태 표시
- 졸음 감지, 사고 감지 및 운전 리포트 표시

### 3. 라즈베리파이에서 실행

#### 파일을 라즈베리파이로 전송

```bash
# 개발 머신에서
scp -r iot_project_OOP pi@raspberry-pi-ip:/home/pi/
```

또는 Git 사용:
```bash
# 라즈베리파이에서
cd /home/pi
git clone <your-repo-url>
cd iot_project_OOP
```

#### 라즈베리파이 설정

```bash
# Python 의존성 설치
pip3 install -r requirements.txt

# Java 21 설치
sudo apt update
sudo apt install openjdk-21-jdk

# Gradle wrapper 설치 (포함되지 않은 경우)
cd ui
chmod +x gradlew
```

#### 라즈베리파이에서 실행

**터미널 1 - Python 백엔드:**
```bash
cd /home/pi/iot_project_OOP
python3 main.py start
```

**터미널 2 - JavaFX UI:**
```bash
cd /home/pi/iot_project_OOP/ui
./gradlew run
```

### 4. Linux 환경에서 실행

#### Ubuntu/Debian 기반 Linux

**1단계: 의존성 설치**
```bash
# Python 3 및 pip 설치
sudo apt update
sudo apt install python3 python3-pip

# Java 21 설치
sudo apt install openjdk-21-jdk

# 카메라 지원 (V4L2)
sudo apt install v4l-utils

# Git (프로젝트 클론용)
sudo apt install git
```

**2단계: 프로젝트 클론 및 설정**
```bash
# 프로젝트 클론
git clone <your-repo-url>
cd iot_project_OOP

# Python 패키지 설치
pip3 install -r requirements.txt

# 실행 권한 부여
chmod +x start_backend.sh start_ui.sh
chmod +x ui/gradlew
```

**3단계: 실행**

**터미널 1 - Python 백엔드:**
```bash
cd /path/to/iot_project_OOP
./start_backend.sh
# 또는: python3 main.py start
```

**터미널 2 - JavaFX UI:**
```bash
cd /path/to/iot_project_OOP
./start_ui.sh
# 또는: cd ui && ./gradlew run
```

#### 일반 Linux 배포판 (CentOS, Fedora 등)

**1단계: 의존성 설치**
```bash
# Fedora/CentOS
sudo dnf install python3 python3-pip java-21-openjdk-devel git
# 또는
sudo yum install python3 python3-pip java-21-openjdk-devel git

# Arch Linux
sudo pacman -S python python-pip jdk-openjdk git

# 카메라 확인
v4l2-ctl --list-devices
```

**2단계: 프로젝트 설정 및 실행**
```bash
# 프로젝트 클론
git clone <your-repo-url>
cd iot_project_OOP

# Python 패키지 설치
pip3 install -r requirements.txt

# 실행
python3 main.py start  # 터미널 1
cd ui && ./gradlew run  # 터미널 2
```

### 5. 설정

`config.py`를 편집하여 설정 조정:

```python
# 졸음 감지
EAR_THRESHOLD = 0.20  # Eye Aspect Ratio 임계값

# 가속도계
ACCEL_THRESHOLD = 4.0  # m/s^2

# GPS
GPS_ENABLED = False  # GPS 모듈 활성화하려면 True로 설정
GPS_SERIAL_PORT = "/dev/ttyUSB0"  # GPS 시리얼 포트

# SMS 신고
SMS_ENABLED = False  # SMS 활성화하려면 True로 설정
SMS_API_KEY = "your-api-key"
SMS_API_SECRET = "your-api-secret"
```

### 6. 데이터 파일

시스템은 `data/` 디렉토리에 JSON 파일을 생성합니다:

- `drowsiness.json`: 실시간 졸음 상태 (EAR, 상태, 알람)
- `status.json`: 시스템 상태 (센서, GPS, 충격 감지, 신고 상태)
- `log_summary.json`: 운전 통계 및 이벤트 카운트

### 7. 문제 해결

#### Python 백엔드 문제

**카메라를 찾을 수 없음:**
- 카메라 연결 확인: `lsusb` 또는 `v4l2-ctl --list-devices`
- 라즈베리파이에서 카메라 활성화: `sudo raspi-config`

**GPS가 작동하지 않음:**
- GPS 모듈 연결 확인
- 시리얼 포트 확인: `ls /dev/ttyUSB*` 또는 `ls /dev/ttyAMA*`
- `config.py`에서 `GPS_ENABLED = True` 설정

**Import 오류:**
- 모든 의존성이 설치되었는지 확인: `pip install -r requirements.txt`
- Python 경로 확인: `python -c "import sys; print(sys.path)"`

#### JavaFX UI 문제

**UI에 데이터가 표시되지 않음:**
- Python 백엔드가 실행 중인지 확인
- JSON 파일이 존재하는지 확인: `ls -la data/`
- UI 코드의 JSON 파일 경로가 설정과 일치하는지 확인

**JavaFX를 찾을 수 없음:**
- Java 21 설치: `sudo apt install openjdk-21-jdk`
- Java 버전 확인: `java -version` (21 이상이어야 함)

**빌드 오류:**
- `./gradlew clean build` 실행
- Gradle wrapper 확인: `chmod +x gradlew`

### 8. 기능

- **졸음 감지**: 실시간 EAR 계산 및 알림
- **사고 감지**: 충격 모니터링을 위한 G-센서
- **GPS 추적**: 위치 추적 (시뮬레이션 또는 실제 GPS 모듈)
- **긴급 신고**: GPS 위치가 포함된 자동 SMS 신고
- **운전 리포트**: 월간 통계 및 이벤트 카운트
- **실시간 대시보드**: JavaFX UI를 통한 실시간 상태 업데이트

### 9. 파일 구조

```
iot_project_OOP/
├── main.py                 # 진입점
├── config.py              # 설정
├── requirements.txt        # Python 의존성
├── driver_monitor/        # Python 백엔드 모듈
│   ├── camera/           # 카메라 관리
│   ├── fatigue/          # 졸음 감지
│   ├── sensors/          # 가속도계, GPS, 스피커
│   ├── report/           # 긴급 신고
│   ├── logging_system/   # 이벤트 로깅
│   └── data_bridge.py    # UI 통신
├── ui/                    # JavaFX UI
│   ├── build.gradle.kts  # 빌드 설정
│   └── src/main/java/... # UI 소스 코드
└── data/                  # JSON 데이터 파일 (실행 시 생성)
```

### 10. 참고사항

- **두 시스템 모두 실행 필요**: Python 백엔드가 데이터를 생성하고, JavaFX UI가 표시합니다
- **데이터 디렉토리**: JSON 파일은 `data/` 디렉토리에 생성됩니다 (또는 라즈베리파이의 `/home/pi/iot/data`)
- **GPS 시뮬레이션**: 기본적으로 GPS는 시뮬레이션 모드로 실행됩니다. 실제 GPS 모듈을 사용하려면 `GPS_ENABLED = True` 설정
- **SMS 신고**: SOLAPI 계정 및 `config.py`의 API 자격 증명이 필요합니다

## 라이선스

[라이선스 정보]

