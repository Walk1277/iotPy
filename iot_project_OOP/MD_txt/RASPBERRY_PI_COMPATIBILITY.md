# 라즈베리파이 호환성 검증 가이드

## ✅ 검증된 기능

### 1. Python 백엔드
- ✅ 카메라: PiCamera2 자동 감지 및 폴백 (USB 카메라)
- ✅ 가속도계: ADXL345 자동 감지 (IS_RPI 플래그)
- ✅ GPS: 시뮬레이션 모드 및 실제 GPS 모듈 지원
- ✅ 경로 처리: `/home/pi` 자동 감지 및 폴백
- ✅ 데이터 브리지: `/home/pi/iot/data` 자동 사용

### 2. JavaFX UI
- ✅ ARM64/ARM32 지원: Gradle이 자동으로 플랫폼 감지
- ✅ 해상도: 800x480 최적화
- ✅ JSON 파일 경로: 여러 경로 시도 (라즈베리파이 우선)
- ✅ JavaFX 모듈: 최소화 (controls, fxml만)

### 3. 스크립트 파일
- ✅ 경로 처리: 상대 경로 사용으로 유연성 확보
- ✅ 실행 권한: chmod +x 처리

## ⚠️ 검증 필요 사항

### 1. UI에서 Python 스크립트 호출
**잠재적 문제:**
- `user.dir`이 `ui` 디렉토리일 수 있음
- 라즈베리파이에서 `python3` 경로 확인 필요

**현재 처리:**
- `user.dir`에 "ui"가 포함되면 부모 디렉토리로 이동
- `python3` 명령어 사용

**검증 방법:**
```bash
# 라즈베리파이에서
cd /home/pi/iot_project_OOP/ui
./gradlew run
# UI에서 설정 저장 테스트
```

### 2. JavaFX 차트
**잠재적 문제:**
- 라즈베리파이에서 JavaFX 차트 성능
- 메모리 사용량

**검증 방법:**
- 운전 리포트 화면에서 차트 표시 확인
- 메모리 사용량 모니터링

### 3. 업데이트 스크립트
**잠재적 문제:**
- `pip3` vs `pip` - 라즈베리파이에서는 `pip3` 사용
- 네트워크 연결 필요

**현재 처리:**
- `pip3` 명령어 사용
- 오류 처리 포함

### 4. 부팅 시 자동 실행
**잠재적 문제:**
- systemd 서비스 권한
- 네트워크 준비 시간

**현재 처리:**
- `After=network.target` 설정
- `User=pi` 설정

## 🔧 라즈베리파이에서 테스트 체크리스트

### 필수 테스트:
1. ✅ Python 백엔드 실행
2. ✅ JavaFX UI 실행
3. ✅ 데이터 파일 생성 확인
4. ✅ UI에서 데이터 표시 확인
5. ⚠️ 설정 저장 기능 테스트
6. ⚠️ 업데이트 기능 테스트
7. ⚠️ 차트 표시 확인

### 테스트 명령어:
```bash
# 1. 백엔드 실행
cd /home/pi/iot_project_OOP
python3 main.py start

# 2. UI 실행 (다른 터미널)
cd /home/pi/iot_project_OOP/ui
./gradlew run

# 3. 데이터 파일 확인
ls -la /home/pi/iot_project_OOP/data/
cat /home/pi/iot_project_OOP/data/status.json

# 4. 설정 저장 테스트
python3 /home/pi/iot_project_OOP/update_config.py EAR_THRESHOLD 0.25

# 5. 업데이트 스크립트 테스트
bash /home/pi/iot_project_OOP/update_system.sh
```

## 📝 알려진 제한사항

1. **JavaFX 차트 성능**: 라즈베리파이에서 성능이 낮을 수 있음
2. **네트워크 의존성**: 업데이트 기능은 인터넷 연결 필요
3. **권한**: 일부 기능은 sudo 권한 필요 (systemd 서비스 설치)

## 🚀 권장 사항

1. **실제 라즈베리파이에서 테스트**: 개발 환경과 다를 수 있음
2. **메모리 모니터링**: JavaFX UI 메모리 사용량 확인
3. **성능 최적화**: 필요시 차트 업데이트 주기 조정

