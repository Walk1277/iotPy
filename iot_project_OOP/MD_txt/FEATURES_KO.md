# 스마트 사고 예방 키트 - 완전한 기능 문서

## 목차
1. [개요](#개요)
2. [핵심 기능](#핵심-기능)
3. [졸음 감지](#졸음-감지)
4. [사고 감지 및 자동 신고](#사고-감지-및-자동-신고)
5. [GPS 기반 주행 감지](#gps-기반-주행-감지)
6. [스피커 제어 시스템](#스피커-제어-시스템)
7. [사용자 인터페이스 (JavaFX)](#사용자-인터페이스-javafx)
8. [시스템 체크 및 진단](#시스템-체크-및-진단)
9. [설정 및 구성](#설정-및-구성)
10. [데이터 로깅 및 리포트](#데이터-로깅-및-리포트)
11. [기술 사양](#기술-사양)

---

## 개요

스마트 사고 예방 키트는 컴퓨터 비전, 센서 데이터, 실시간 알림을 결합하여 사고를 예방하고 비상 상황을 자동으로 신고하는 종합 운전자 모니터링 시스템입니다. 시스템은 센서 처리를 위한 Python 백엔드와 사용자 상호작용을 위한 JavaFX UI로 구성됩니다.

### 시스템 아키텍처
- **백엔드**: OpenCV, MediaPipe 및 센서 라이브러리를 사용하는 Python 3.x
- **프론트엔드**: JavaFX 17.0.2 (라즈베리파이용 ARM 호환)
- **통신**: 백엔드와 UI 간 JSON 기반 파일 통신
- **플랫폼**: 800x440 터치스크린 디스플레이가 있는 라즈베리파이

---

## 핵심 기능

### 1. 실시간 운전자 모니터링
- 연속적인 얼굴 감지 및 눈 추적
- Eye Aspect Ratio (EAR)를 사용한 졸음 감지
- 가속도계 기반 충격 감지
- GPS 기반 위치 추적

### 2. 다중 모달 알림 시스템
- UI의 시각적 알림
- 스피커를 통한 오디오 알림
- SMS 비상 신고
- 응답을 위한 터치스크린 상호작용

### 3. 지능형 응답 시스템
- GPS 기반 주행 상태 감지
- 상황 인식 스피커 활성화
- 자동 비상 신고
- 사용자 응답 처리

---

## 졸음 감지

### 감지 알고리즘
- **방법**: 얼굴 랜드마크를 사용한 Eye Aspect Ratio (EAR) 계산
- **임계값**: 구성 가능한 `EAR_THRESHOLD` (기본값: 0.200188679245283)
- **연속 프레임**: 30 프레임 (30 FPS에서 약 1초)
- **얼굴 랜드마크**: MediaPipe Face Mesh (468 포인트)

### 감지 프로세스
1. **얼굴 감지**: MediaPipe가 카메라 프레임에서 얼굴 감지
2. **랜드마크 추출**: 눈 영역 랜드마크 추출 (좌우 눈)
3. **EAR 계산**: 양쪽 눈에 대한 Eye Aspect Ratio 계산
4. **임계값 비교**: 평균 EAR을 임계값과 비교
5. **상태 결정**: 
   - 30개 이상의 연속 프레임에서 EAR < 임계값 → 졸음 감지됨
   - EAR >= 임계값 → 정상 상태

### 구성
- **파일**: `config.py`
- **매개변수**:
  - `EAR_THRESHOLD`: 졸음 감지 임계값 (float)
  - `CONSEC_FRAMES`: 감지를 위한 연속 프레임 수 (int)
  - `LEFT_EYE_IDXS`: 왼쪽 눈 랜드마크 인덱스
  - `RIGHT_EYE_IDXS`: 오른쪽 눈 랜드마크 인덱스

### 로깅
- 졸음이 감지되면 `driving_events.log`에 이벤트 기록
- 타임스탬프 및 EAR 값 기록

---

## 사고 감지 및 자동 신고

### 감지 로직

#### 1단계: 충격 감지
- **센서**: ADXL345 가속도계
- **임계값**: `ACCEL_THRESHOLD = 2.0` m/s²
- **감지된 이벤트**:
  - 급가속 (양수 X축 > 임계값)
  - 급정거 (음수 X축 < -임계값)

#### 2단계: 충격 후 모니터링
- **지속 시간**: 1분 (`REPORT_IMPACT_MONITORING_DURATION = 60.0` 초)
- **확인 조건** (충격 후 1분 이내):
  1. **눈 감김**: 10초 이상 EAR < 임계값 (`REPORT_EYES_CLOSED_DURATION`)
  2. **얼굴 미감지**: 10초 이상 얼굴이 감지되지 않음 (`REPORT_NO_FACE_DURATION`)

#### 3단계: 알림 및 응답
- **알림 트리거**: 조건 중 하나가 충족되면 시스템이 `ALERT` 상태로 진입
- **응답 타임아웃**: 10초 (`REPORT_RESPONSE_TIMEOUT`)
- **사용자 응답 옵션**:
  - UI 팝업에서 화면 터치
  - 키보드 키 누르기 (모니터 창이 표시된 경우)
- **응답 파일**: 사용자가 화면을 터치하면 `user_response.json` 생성

#### 4단계: 자동 신고
- **트리거**: 10초 이내 사용자 응답 없음
- **동작**: SOLAPI를 통해 자동 SMS 신고 전송
- **SMS 내용**:
  - 비상 메시지 헤더
  - 타임스탬프
  - 충격 감지 시간
  - GPS 위치 (위도, 경도)
  - Google Maps 링크
  - 상태 설명

### UI 팝업 (ResponseRequestModal)
- **표시**: 전체 화면 모달 오버레이
- **기능**:
  - 경고 아이콘 (⚠️)
  - "사고 감지됨!" 제목
  - 카운트다운 타이머 (10초)
  - "화면을 터치하여 신고 취소" 지시사항
  - 실시간 카운트다운 업데이트
  - 남은 시간에 따른 색상 변경 (3초 미만일 때 빨간색)

### 자동 SMS 신고
- **서비스**: SOLAPI (한국 SMS 서비스)
- **구성**: `config.py`
  - `SMS_API_KEY`: SOLAPI API 키
  - `SMS_API_SECRET`: SOLAPI API 시크릿
  - `SMS_FROM_NUMBER`: 발신 전화번호 (SOLAPI에 등록됨)
  - `SMS_TO_NUMBER`: 수신 전화번호
  - `SMS_ENABLED`: SMS 신고 활성화/비활성화
- **메시지 형식**:
  ```
  [비상 신고] 운전자 모니터링 시스템
  시간: YYYY-MM-DD HH:MM:SS
  충격 감지: HH:MM:SS
  위치: 위도: XX.XXXXXX, 경도: XX.XXXXXX
  지도: https://maps.google.com/?q=lat,lon
  상태: 충격 후 1분 이내 10초 이상 눈 감김 또는 얼굴 미감지
  사용자 응답 없음. 비상 상황 감지됨. 지금 신고합니다.
  ```

### 파일 통신
- **사용자 응답**: `user_response.json`
  - 사용자가 화면을 터치할 때 JavaFX UI가 생성
  - 포함 내용: `{"responded": true, "timestamp": "..."}`
  - Python 백엔드가 읽고 처리 후 삭제
- **응답 경로**:
  - `/home/pi/iot/data/user_response.json` (라즈베리파이)
  - `data/user_response.json` (개발)

---

## GPS 기반 주행 감지

### 목적
상황 인식 알림을 활성화하기 위해 차량이 현재 주행 중인지 확인합니다.

### 감지 방법
- **센서**: GPS 모듈 (실제 또는 시뮬레이션)
- **임계값**: `DRIVING_SPEED_THRESHOLD = 5.0` km/h
- **로직**: 
  - 속도 >= 5.0 km/h → 주행 중
  - 속도 < 5.0 km/h → 주행 중 아님 (주차됨)

### GPS 구성
- **파일**: `config.py`
- **매개변수**:
  - `GPS_ENABLED`: GPS 모듈 활성화/비활성화
  - `GPS_SERIAL_PORT`: GPS 모듈용 시리얼 포트 (`/dev/ttyUSB0`)
  - `GPS_BAUD_RATE`: 보드 레이트 (9600)
- **시뮬레이션 모드**: 
  - GPS 모듈을 사용할 수 없을 때 사용
  - 기본 위치: 서울, 대한민국 (37.5665, 126.9780)
  - 시뮬레이션 속도: 0-30 km/h (사인파 패턴)

### 사용
- 스피커 활성화 조건 결정
- 상황 인식 알림 시스템
- 비상 신고를 위한 위치 추적

---

## 스피커 제어 시스템

### 활성화 조건

#### 주행 중일 때:
1. **졸음 감지됨** → 스피커 **즉시** 활성화
2. **얼굴 미감지** → **10초 후** 스피커 활성화 (`NO_FACE_WHILE_DRIVING_TIMEOUT`)

#### 주행 중이 아닐 때:
- **졸음 감지됨** → 스피커 **활성화 안 함** (UI 알림만)
- **얼굴 미감지** → 스피커 **활성화 안 함** (주차 상태)

#### 사고 감지:
- **스피커 활성화 안 함** (UI 팝업만, 오디오 알림 없음)

### 스피커 중지 팝업
- **트리거**: 스피커가 1초 이상 활성화됨
- **표시**: JavaFX Alert 대화상자
- **메시지**: "알람 스피커가 X.X초 동안 활성화되었습니다. 확인을 클릭하여 스피커를 중지하세요."
- **동작**: 사용자가 확인 클릭 → `stop_speaker.json` 파일 생성 → 백엔드가 스피커 중지
- **파일 통신**: `stop_speaker.json` (`user_response.json`과 동일한 경로)

### 스피커 제어 흐름
1. **활성화**: 
   - 주행 중 졸음 감지 → `alarm_start_time` 설정
   - 주행 중 10초 이상 얼굴 미감지 → `alarm_start_time` 설정
2. **지속 시간 추적**: 
   - `alarm_start_time`에서 `alarm_duration` 계산
   - 지속 시간 >= 1.0초 → `show_speaker_popup = True`
3. **UI 팝업**: 
   - 1초 후 JavaFX Alert 대화상자 표시
   - 사용자가 확인 버튼으로 스피커 중지 가능
4. **비활성화**:
   - UI 팝업을 통해 사용자가 중지
   - 졸음 조건이 더 이상 충족되지 않음
   - 차량이 주행 중지 (속도 < 임계값)

### 구성
- **파일**: `config.py`
- **매개변수**:
  - `NO_FACE_WHILE_DRIVING_TIMEOUT = 10.0` 초
  - `DRIVING_SPEED_THRESHOLD = 5.0` km/h

---

## 사용자 인터페이스 (JavaFX)

### 메인 화면 (800x440 픽셀)
4개의 주요 패널이 있는 2x2 그리드 레이아웃:

#### 1. 현재 상태 패널 (왼쪽 상단)
- **표시**: 실시간 운전자 상태
- **상태**:
  - "Good" (녹색) - 정상 주행
  - "Alert" (빨간색) - 졸음 감지됨
  - "Waiting" (회색) - 카메라 확인 중
- **업데이트**: `drowsiness.json`에서 매 1초마다

#### 2. 운전 점수 패널 (오른쪽 상단)
- **표시**: 월간 운전 점수 (0-100점)
- **계산**:
  - 100점에서 시작
  - 이벤트당 5점 차감:
    - 졸음 감지
    - 급가속
    - 급정거
- **업데이트**: `log_summary.json`에서 매 1초마다

#### 3. 사고 감지 패널 (왼쪽 하단)
- **표시**: 
  - 사고 상태 ("No Accident" / "Accident Detected!" / "Response Required!")
  - G-센서 값 (G 단위)
- **업데이트**: `status.json`에서 매 1초마다
- **클릭 동작**: 상세 사고 감지 화면으로 이동

#### 4. 설정 및 로그 확인 패널 (오른쪽 하단)
- **설정 버튼**: 설정 메뉴로 이동
- **로그 확인 영역**: 최근 운전 이벤트 표시
- **새로고침 버튼**: 로그 데이터 다시 로드
- **클릭 동작**: 상세 로그 화면으로 이동

### 상세 화면

#### 상태 화면
- 실시간 카메라 상태
- EAR 값 표시
- 임계값 비교
- 얼굴 감지 상태

#### 운전 리포트 화면
- 월간 점수 차트 (LineChart)
- 일일 점수 (BarChart)
- 이벤트 통계:
  - 총 이벤트
  - 졸음 횟수
  - 급가속 횟수
  - 급정거 횟수
- 리포트 통계:
  - 알림 트리거 횟수
  - 리포트 트리거 횟수
  - 리포트 취소 횟수
  - SMS 전송 횟수

#### 사고 감지 화면
- G-센서 값
- 충격 감지 상태
- GPS 위치
- 테스트 버튼 (사고 감지 테스트용)

#### 설정 화면
여러 하위 화면:

##### 개인 설정
- 사용자 정보 (향후 사용을 위한 플레이스홀더)

##### 졸음 설정
- EAR 임계값 조정
- 실시간 임계값 업데이트
- `config.py`에 저장

##### 자동 신고 설정
- 발신 전화번호 (`SMS_FROM_NUMBER`)
- 수신 전화번호 (`SMS_TO_NUMBER`)
- 자동 신고 활성화/비활성화 체크박스
- `config.py`에 저장

##### 시스템 체크
- 카메라 테스트
- 가속도계 테스트
- GPS 테스트 (실제 신호 감지 포함)
- 스피커 테스트
- SMS 테스트 (GPS 데이터가 포함된 실제 테스트 메시지 전송)
- 상태 아이콘으로 결과 표시 (✅ OK, ⚠️ WARNING, ❌ ERROR)

#### 로그 화면
- 스크롤 가능한 로그 뷰어
- `driving_events.log`에서 최근 운전 이벤트 표시
- 자동 새로고침 기능
- 이벤트 필터링

#### 업데이트 화면
- 시스템 업데이트 기능
- `update_system.sh` 스크립트 실행
- `requirements.txt`에서 Python 패키지 업데이트

### 팝업 모달

#### 사고 응답 요청 모달
- **트리거**: 사고 감지됨 (충격 + 눈 감김/얼굴 미감지)
- **표시**: 전체 화면 오버레이
- **기능**:
  - 경고 아이콘
  - "사고 감지됨!" 제목
  - 카운트다운 타이머 (10초)
  - 터치 지시사항
  - 실시간 카운트다운 업데이트
- **동작**: 사용자가 화면 터치 → `user_response.json` 생성 → 신고 취소

#### 스피커 중지 알림
- **트리거**: 스피커가 1초 이상 활성화됨
- **표시**: JavaFX Alert 대화상자
- **기능**:
  - 경고 유형 알림
  - 지속 시간 표시
  - 스피커 중지를 위한 확인 버튼
- **동작**: 사용자가 확인 클릭 → `stop_speaker.json` 생성 → 스피커 중지

### 데이터 업데이트 시스템
- **업데이트 빈도**: 매 1초
- **데이터 소스**:
  - `drowsiness.json` - 졸음 상태
  - `status.json` - 시스템 상태 및 사고 감지
  - `log_summary.json` - 운전 점수 및 통계
- **업데이트 메커니즘**: `Timeline` (JavaFX)을 사용하는 `DataUpdater` 클래스

### 내비게이션 시스템
- **화면 내비게이터**: `ScreenNavigator` 클래스가 화면 전환 관리
- **뒤로 가기**: 모든 상세 화면에 뒤로 가기 버튼 있음
- **스택 기반**: 화면 관리를 위해 `StackPane` 사용

---

## 시스템 체크 및 진단

### 시스템 체크 스크립트
- **파일**: `check_system.py`
- **목적**: 모든 시스템 구성 요소가 올바르게 작동하는지 확인
- **수행된 테스트**:

#### 1. 카메라 테스트
- 카메라 초기화
- 테스트 프레임 캡처
- 해상도 확인
- 반환: 상태, 메시지, 세부 정보 (해상도)

#### 2. 가속도계 테스트
- ADXL345 센서 초기화
- 가속도계 데이터 읽기 (X, Y, Z)
- 센서 연결 확인
- 반환: 상태, 메시지, 세부 정보 (m/s² 단위의 X, Y, Z 값)

#### 3. GPS 테스트
- GPS 모듈 초기화
- GPS 데이터 여러 번 읽기 (10회 시도)
- 실제 신호 vs 시뮬레이션 감지
- 기본 시뮬레이션 위치 확인
- 반환: 상태, 메시지, 세부 정보 (위도, 경도)

#### 4. 스피커 테스트
- 스피커 컨트롤러 초기화
- 테스트 알람 재생 (0.1초)
- 오디오 출력 확인
- 반환: 상태, 메시지, 세부 정보

#### 5. SMS 테스트
- SMS 서비스 초기화 (SOLAPI)
- API 자격 증명 확인
- 실제 테스트 SMS 메시지 전송
- 메시지에 GPS 위치 포함
- 반환: 상태, 메시지, 세부 정보 (메시지 ID, 수신자)

### 테스트 출력 형식
```json
{
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "checks": {
    "camera": {
      "status": "OK|WARNING|ERROR",
      "message": "...",
      "details": "..."
    },
    "accelerometer": {...},
    "gps": {...},
    "speaker": {...},
    "sms": {...}
  }
}
```

### 상태 유형
- **OK**: 구성 요소가 정상적으로 작동 중
- **WARNING**: 구성 요소가 사용 가능하지만 최적이 아님 (예: GPS 시뮬레이션 모드)
- **ERROR**: 구성 요소가 작동하지 않거나 사용할 수 없음

### UI에서 액세스
- 설정 → 시스템 체크
- 실시간 테스트 실행
- 색상 코딩된 상태 아이콘으로 결과 표시

---

## 설정 및 구성

### 구성 파일
- **파일**: `config.py`
- **위치**: 프로젝트 루트 디렉토리
- **동적 다시 로드**: `importlib.reload()`를 사용하여 런타임에 구성 값 다시 로드

### 구성 가능한 매개변수

#### 졸음 감지
- `EAR_THRESHOLD`: Eye Aspect Ratio 임계값 (기본값: 0.200188679245283)
- `CONSEC_FRAMES`: 감지를 위한 연속 프레임 (기본값: 30)

#### 가속도계
- `ACCEL_THRESHOLD`: m/s² 단위의 충격 감지 임계값 (기본값: 2.0)

#### 리포트 시스템
- `REPORT_IMPACT_MONITORING_DURATION`: 충격 후 모니터링 기간(초) (기본값: 60.0)
- `REPORT_EYES_CLOSED_DURATION`: 알림을 위한 눈 감김 지속 시간(초) (기본값: 10.0)
- `REPORT_NO_FACE_DURATION`: 알림을 위한 얼굴 미감지 지속 시간(초) (기본값: 10.0)
- `REPORT_RESPONSE_TIMEOUT`: 사용자 응답 타임아웃(초) (기본값: 10.0)
- `AUTO_REPORT_ENABLED`: 자동 신고 활성화/비활성화 (기본값: True)

#### SMS 신고 (SOLAPI)
- `SMS_API_KEY`: SOLAPI API 키
- `SMS_API_SECRET`: SOLAPI API 시크릿
- `SMS_FROM_NUMBER`: 발신 전화번호 (SOLAPI에 등록되어야 함)
- `SMS_TO_NUMBER`: 수신 전화번호
- `SMS_ENABLED`: SMS 신고 활성화/비활성화 (기본값: True)

#### GPS
- `GPS_ENABLED`: GPS 모듈 활성화/비활성화 (기본값: True)
- `GPS_SERIAL_PORT`: GPS 시리얼 포트 경로 (기본값: "/dev/ttyUSB0")
- `GPS_BAUD_RATE`: GPS 보드 레이트 (기본값: 9600)
- `DRIVING_SPEED_THRESHOLD`: km/h 단위의 주행 감지 속도 임계값 (기본값: 5.0)
- `NO_FACE_WHILE_DRIVING_TIMEOUT`: 주행 중 얼굴 미감지 시 스피커 활성화 전 타임아웃(초) (기본값: 10.0)

#### 카메라
- `CAM_WIDTH`: 픽셀 단위의 카메라 너비 (기본값: 800)
- `CAM_HEIGHT`: 픽셀 단위의 카메라 높이 (기본값: 480)

#### 로깅
- `LOG_FILE`: 운전 이벤트 로그 파일 이름 (기본값: "driving_events.log")

### 설정 UI 기능

#### 졸음 설정
- **EAR 임계값 입력**: 임계값을 위한 텍스트 필드
- **실시간 업데이트**: `update_config.py`를 통해 즉시 변경 사항 적용
- **저장 버튼**: `config.py`에 저장

#### 자동 신고 설정
- **발신 전화번호**: `SMS_FROM_NUMBER`를 위한 입력 필드
- **수신 전화번호**: `SMS_TO_NUMBER`를 위한 입력 필드
- **자동 신고 활성화**: `AUTO_REPORT_ENABLED`를 위한 체크박스
- **저장 버튼**: 모든 값을 `config.py`에 저장

#### 시스템 로그 초기화
- **버튼**: "시스템 로그 초기화"
- **동작**: 
  - `driving_events.log` 지우기
  - `log_summary.json`을 기본 상태로 재설정 (100점, 0 이벤트)
  - `clear_logs.py` 스크립트 사용

### 구성 업데이트 스크립트
- **파일**: `update_config.py`
- **기능**: `config.py` 값을 프로그래밍 방식으로 업데이트
- **사용**: 설정이 저장될 때 JavaFX UI에서 호출됨
- **방법**: `config.py` 파일에서 문자열 교체

---

## 데이터 로깅 및 리포트

### 이벤트 로깅
- **파일**: `driving_events.log`
- **형식**: 헤더가 있는 CSV
- **열**: Timestamp, EventType
- **이벤트 유형**:
  - `drowsiness`: 졸음 감지됨
  - `sudden acceleration`: 급가속 감지됨
  - `sudden stop`: 급정거 감지됨
  - `report_alert_triggered`: 사고 알림 트리거됨
  - `report_triggered`: 자동 신고 시작됨
  - `report_cancelled`: 사용자가 신고 취소
  - `sms_report_sent`: SMS 신고 전송 성공
  - `sms_report_failed`: SMS 신고 실패
  - `emergency`: 비상 상황 (레거시)
  - `Start program`: 시스템 시작됨
  - `program quit`: 시스템 중지됨

### 로그 요약
- **파일**: `log_summary.json`
- **업데이트 빈도**: 매 2초 (30 FPS에서 60 프레임)
- **내용**:
  ```json
  {
    "total_events": 0,
    "drowsiness_count": 0,
    "sudden_acceleration_count": 0,
    "sudden_stop_count": 0,
    "monthly_score": 100,
    "daily_scores": [
      {
        "date": "YYYY-MM-DD",
        "score": 100,
        "day": DD
      }
    ],
    "event_counts": {
      "sudden_stop": 0,
      "sudden_acceleration": 0,
      "drowsiness": 0
    },
    "report_stats": {
      "alert_triggered": 0,
      "report_triggered": 0,
      "report_cancelled": 0,
      "sms_sent": 0
    }
  }
  ```

### 운전 점수 계산
- **기본 점수**: 100점
- **차감**: 이벤트당 5점
- **계산되는 이벤트 유형**:
  - 졸음 감지
  - 급가속
  - 급정거
- **제외된 이벤트**: 시스템 이벤트 (프로그램 시작, 프로그램 종료 등)
- **공식**: `score = max(0, 100 - (total_events * 5))`

### 일일 점수
- 로그 데이터에서 일별로 계산
- 각 날은 100점에서 시작
- 해당 날의 이벤트당 5점 차감
- UI에서 막대 차트로 표시

### 로그 파서
- **파일**: `driver_monitor/logging_system/log_parser.py`
- **기능**: `driving_events.log`를 pandas DataFrame으로 파싱
- **메서드**:
  - `load_recent_days(days=30)`: 최근 N일의 이벤트 로드
  - 이벤트 데이터 필터링 및 처리
  - 통계 계산

### 로그 지우기
- **스크립트**: `clear_logs.py`
- **기능**: 
  - `driving_events.log`에서 모든 이벤트 지우기
  - `log_summary.json`을 기본 상태로 재설정
- **액세스**: 설정 → 시스템 로그 초기화 버튼

---

## 기술 사양

### 백엔드 아키텍처

#### 주요 구성 요소
1. **DriverMonitor** (`driver_monitor.py`)
   - 메인 모니터링 루프
   - 모든 하위 시스템 조정
   - 프레임 처리 처리

2. **FatigueDetector** (`fatigue/fatigue_detector.py`)
   - MediaPipe를 사용한 얼굴 감지
   - EAR 계산
   - 졸음 상태 결정

3. **AccelerometerDetector** (`sensors/accelerometer_detector.py`)
   - ADXL345 가속도계 인터페이스
   - 충격 감지 (급가속/급정거)
   - 이벤트 로깅

4. **GPSManager** (`sensors/gps_manager.py`)
   - GPS 모듈 인터페이스 (시리얼/UART)
   - 위치 및 속도 읽기
   - 시뮬레이션 모드 지원

5. **SpeakerController** (`sensors/speaker_controller.py`)
   - GPIO 기반 스피커 제어
   - PWM 신호 생성
   - 알람 켜기/끄기 제어

6. **ReportManager** (`report/report_manager.py`)
   - 사고 감지 로직
   - 충격 후 모니터링
   - SMS 신고 전송
   - 사용자 응답 처리

7. **DataBridge** (`data_bridge.py`)
   - UI용 JSON 파일 생성
   - 실시간 상태 업데이트
   - 로그 요약 생성

8. **EventLogger** (`logging_system/event_logger.py`)
   - CSV 파일로 이벤트 로깅
   - 타임스탬프 관리

### 프론트엔드 아키텍처

#### 주요 구성 요소
1. **MainApplication** (`MainApplication.java`)
   - JavaFX 애플리케이션 진입점
   - Stage 및 Scene 설정
   - 데이터 업데이트 타임라인

2. **MainScreenController** (`MainScreenController.java`)
   - 메인 대시보드 관리
   - 패널 생성 및 업데이트
   - 팝업 모달 관리

3. **DataUpdater** (`DataUpdater.java`)
   - 주기적 데이터 업데이트 (1초 간격)
   - JSON 파일 읽기
   - UI 상태 업데이트

4. **화면 컨트롤러** (`controllers/`)
   - `StatusScreenController`: 상태 세부 정보
   - `ReportScreenController`: 차트가 있는 운전 리포트
   - `AccidentScreenController`: 사고 감지 세부 정보
   - `SettingsScreenController`: 모든 설정 화면
   - `LogScreenController`: 로그 뷰어
   - `UpdateScreenController`: 시스템 업데이트

5. **ResponseRequestModal** (`ResponseRequestModal.java`)
   - 전체 화면 사고 응답 모달
   - 카운트다운 타이머
   - 터치 상호작용

6. **데이터 로더**
   - `StatusDataLoader`: `status.json` 로드
   - `JsonDataLoader`: 여러 경로 지원이 있는 일반 JSON 로더

### 데이터 통신

#### JSON 파일
1. **drowsiness.json**
   - 위치: `data/drowsiness.json` 또는 `/home/pi/iot/data/drowsiness.json`
   - 내용:
     ```json
     {
       "ear": 0.25,
       "threshold": 0.2,
       "state": "normal|sleepy|no_face",
       "timestamp": "YYYY-MM-DD HH:MM:SS",
       "face_detected": true,
       "alarm_on": false,
       "alarm_duration": 0.0,
       "show_speaker_popup": false
     }
     ```

2. **status.json**
   - 위치: `data/status.json` 또는 `/home/pi/iot/data/status.json`
   - 내용:
     ```json
     {
       "connection_status": "OK",
       "sensor_status": "...",
       "accel_magnitude": 1.0,
       "accel_data": {"x": 0.0, "y": 0.0, "z": 0.0},
       "gps_position": {"latitude": 37.5665, "longitude": 126.9780},
       "gps_position_string": "(37.5665, 126.9780)",
       "impact_detected": false,
       "report_status": {
         "status": "NORMAL|ALERT|REPORTING",
         "message": "...",
         "remaining_time": 0.0
       },
       "response_requested": false,
       "response_message": "",
       "response_remaining_time": 0.0,
       "timestamp": "YYYY-MM-DD HH:MM:SS"
     }
     ```

3. **log_summary.json**
   - 위치: `data/log_summary.json` 또는 `/home/pi/iot/data/log_summary.json`
   - 내용: (데이터 로깅 및 리포트 섹션 참조)

#### 응답 파일 (UI → 백엔드)
1. **user_response.json**
   - 사용자가 사고 응답 모달을 터치할 때 생성
   - 내용: `{"responded": true, "timestamp": "..."}`
   - 백엔드가 읽고 처리 후 삭제

2. **stop_speaker.json**
   - 사용자가 스피커 중지 알림에서 확인을 클릭할 때 생성
   - 내용: `{"stop": true, "timestamp": "..."}`
   - 백엔드가 읽고 처리 후 삭제

### 파일 경로
- **라즈베리파이**: `/home/pi/iot/data/`
- **개발**: `data/` (프로젝트 루트 기준)
- **폴백**: 여러 경로를 순서대로 시도

### 빌드 시스템
- **Gradle**: 8.10.2
- **Java**: 21.0.9
- **JavaFX**: 17.0.2 (ARM 호환)
- **빌드 파일**: `ui/build.gradle.kts`
- **메인 클래스**: `org.example.iotprojectui.MainApplication`

### 종속성

#### Python
- `opencv-python`: 컴퓨터 비전
- `mediapipe`: 얼굴 감지 및 랜드마크
- `pandas`: 데이터 분석
- `solapi`: SMS 서비스 (SOLAPI)
- `pynmea2`: GPS NMEA 파싱
- `adafruit-circuitpython-adxl34x`: 가속도계 인터페이스
- `RPi.GPIO`: GPIO 제어 (라즈베리파이)

#### Java
- JavaFX 17.0.2 (controls, fxml)
- Jackson (JSON 파싱)
- Gradle wrapper

### 성능
- **프레임 속도**: ~30 FPS (카메라에 따라 다름)
- **UI 업데이트 속도**: 1초
- **로그 요약 업데이트**: 매 2초 (60 프레임)
- **GPS 업데이트**: 매 프레임 (사용 가능한 경우)

### 오류 처리
- **카메라 오류**: 우아한 폴백, 오류 로깅
- **센서 오류**: 시뮬레이션 모드 또는 경고 상태
- **GPS 오류**: 기본 위치가 있는 시뮬레이션 모드
- **SMS 오류**: 오류 로깅, 시스템 크래시 없음
- **파일 I/O 오류**: 여러 경로 폴백

### 보안 고려 사항
- **API 키**: `config.py`에 저장됨 (프로덕션에서는 보안 처리 필요)
- **전화번호**: `config.py`에 저장됨
- **로그 파일**: 민감한 위치 데이터를 포함할 수 있음
- **파일 권한**: 데이터 디렉토리 권한이 자동으로 처리됨

---

## 기능 요약 테이블

| 기능 | 조건 | 동작 | 우선순위 |
|---------|-----------|--------|----------|
| 졸음 감지 | 30 프레임 동안 EAR < 임계값 | 이벤트 기록, 스피커 활성화 (주행 중인 경우) | 높음 |
| 주행 중 얼굴 미감지 | 주행 중 10초 이상 얼굴 미감지 | 타임아웃 후 스피커 활성화 | 높음 |
| 사고 감지 | 충격 + (눈 감김 OR 얼굴 미감지) 10초 이상 | UI 팝업 표시, 10초 동안 응답 대기 | 중요 |
| 자동 신고 | 사고 팝업에 10초 이내 응답 없음 | GPS 위치와 함께 SMS 전송 | 중요 |
| 스피커 (주행 + 졸음) | 주행 중 + 졸음 감지됨 | 즉시 활성화 | 높음 |
| 스피커 (주행 + 얼굴 미감지) | 주행 중 + 10초 동안 얼굴 미감지 | 타임아웃 후 활성화 | 높음 |
| 스피커 (주행 중 아님) | 주행 중 아님 | 활성화 안 함 | 중간 |
| 스피커 (사고) | 사고 감지됨 | 활성화 안 함 | 낮음 |
| 스피커 중지 팝업 | 스피커가 1초 이상 활성화됨 | 팝업 표시, 사용자가 중지 허용 | 중간 |
| 시스템 체크 | 사용자 시작 | 모든 구성 요소 테스트 | 중간 |
| 설정 저장 | 사용자가 설정 변경 | config.py 업데이트 | 중간 |
| 로그 초기화 | 사용자 시작 | 로그 지우기, 점수 재설정 | 낮음 |

---

## 워크플로우 다이어그램

### 졸음 감지 워크플로우
```
카메라 프레임 → 얼굴 감지 → EAR 계산 → 임계값 비교
    ↓
30 프레임 동안 EAR < 임계값?
    ↓ 예
졸음 감지됨
    ↓
주행 상태 확인
    ↓
주행 중? → 예 → 스피커 활성화 → UI 알림 표시
    ↓ 아니오
UI 알림만 표시 (스피커 없음)
```

### 사고 감지 및 자동 신고 워크플로우
```
가속도계 이벤트 (충격)
    ↓
충격 등록 → 1분 모니터링 시작
    ↓
1분 이내:
    - 10초 이상 눈 감김? OR
    - 10초 이상 얼굴 미감지?
    ↓ 예
ALERT 상태 진입 → UI 팝업 표시
    ↓
사용자 응답을 위해 10초 대기
    ↓
사용자 응답? (화면 터치 또는 키보드)
    ↓ 예                    ↓ 아니오
신고 취소           타임아웃 (10초)
    ↓                        ↓
정상 상태          SMS 신고 전송
                   → REPORTING 상태
```

### 스피커 활성화 워크플로우
```
조건 확인:
1. 졸음 감지됨?
2. 주행 중 얼굴 미감지?
3. 주행 상태?
    ↓
주행 중 + 졸음 → 스피커 즉시 활성화
    ↓
주행 중 + 얼굴 미감지 (10초) → 스피커 활성화
    ↓
주행 중 아님 → 활성화 안 함
    ↓
스피커가 1초 이상 활성화됨?
    ↓ 예
중지 팝업 표시 → 사용자가 확인 클릭 → 스피커 중지
```

---

## 구성 예제

### 예제: 졸음 감지 민감도 조정
```python
# config.py
EAR_THRESHOLD = 0.25  # 더 민감함 (더 일찍 감지)
EAR_THRESHOLD = 0.15  # 덜 민감함 (나중에 감지)
```

### 예제: 응답 타임아웃 변경
```python
# config.py
REPORT_RESPONSE_TIMEOUT = 15.0  # 10초 대신 15초
```

### 예제: SMS 신고 비활성화
```python
# config.py
SMS_ENABLED = False  # SMS 비활성화, 다른 기능은 유지
```

### 예제: 주행 속도 임계값 조정
```python
# config.py
DRIVING_SPEED_THRESHOLD = 10.0  # 5 km/h 대신 10 km/h
```

---

## 트러블슈팅

### 일반적인 문제

#### 1. 카메라가 감지되지 않음
- **증상**: "카메라 초기화 실패"
- **해결책**: 카메라 연결 확인, 장치 인덱스 확인 (보통 0)

#### 2. GPS가 작동하지 않음
- **증상**: GPS가 시뮬레이션 모드 표시
- **해결책**: 
  - GPS 모듈 연결 확인
  - 시리얼 포트 확인 (`/dev/ttyUSB0`)
  - config.py에서 `GPS_ENABLED = True` 설정

#### 3. SMS가 전송되지 않음
- **증상**: "SMS 서비스 초기화 실패"
- **해결책**:
  - `solapi` 설치: `pip3 install solapi`
  - `config.py`에서 API 키 확인
  - SOLAPI 계정 잔액 확인
  - 전화번호가 등록되어 있는지 확인

#### 4. 스피커가 작동하지 않음
- **증상**: 소리 출력 없음
- **해결책**:
  - GPIO 핀 연결 확인 (기본값: 핀 21)
  - 스피커 하드웨어 확인
  - 라즈베리파이에서 실행 중인지 확인 (GPIO는 RPi에서만 작동)

#### 5. UI가 업데이트되지 않음
- **증상**: UI가 오래된 데이터 표시
- **해결책**:
  - JSON 파일 경로 확인
  - 데이터 디렉토리 권한 확인
  - 백엔드가 실행 중이고 JSON 파일을 작성하는지 확인

#### 6. 사고 팝업이 표시되지 않음
- **증상**: 사고가 감지되었지만 팝업 없음
- **해결책**:
  - `status.json`에서 `response_requested` 확인
  - UI가 `status.json`을 올바르게 읽는지 확인
  - 팝업 충돌 확인 (스피커 알림이 차단할 수 있음)
  - 콘솔의 디버그 로그 검토

---

## 향후 개선 사항

### 잠재적 개선
1. **머신 러닝**: 사용자 정의 졸음 감지 모델 훈련
2. **클라우드 통합**: 로그 및 리포트를 클라우드 스토리지에 업로드
3. **모바일 앱**: 원격 모니터링을 위한 동반 모바일 앱
4. **음성 알림**: 텍스트-음성 변환 알림
5. **다국어 지원**: 국제화
6. **고급 분석**: 머신 러닝 기반 운전 패턴 분석
7. **통합**: 차량 OBD-II 시스템과 연결
8. **실시간 스트리밍**: 원격 서버로 카메라 피드 스트리밍

---

## 버전 정보
- **최종 업데이트**: 2025-12-12
- **Python 버전**: 3.x
- **Java 버전**: 21.0.9
- **JavaFX 버전**: 17.0.2
- **Gradle 버전**: 8.10.2
- **플랫폼**: 라즈베리파이 (ARM) / Linux

---

## 연락처 및 지원
문제, 질문 또는 기여에 대해서는 메인 README.md 파일을 참조하세요.

