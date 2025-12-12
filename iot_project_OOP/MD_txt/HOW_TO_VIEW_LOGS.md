# 로그 확인 방법

## 로그 파일 위치

### 1. 백엔드 콘솔 로그 (Python 출력)
- **파일**: `backend.log` (프로젝트 루트 디렉토리)
- **내용**: Python 백엔드의 모든 print() 출력
- **포함 내용**:
  - 사고 감지 관련 로그 (`[Report]`, `[DriverMonitor]`, `[DataBridge]`)
  - 졸음 감지 로그
  - 센서 상태 로그
  - 오류 메시지

### 2. 이벤트 로그 (운전 이벤트 기록)
- **파일**: `driving_events.log` (프로젝트 루트 디렉토리)
- **내용**: 운전 이벤트 기록 (CSV 형식)
- **포함 내용**:
  - 졸음 감지
  - 급가속/급정거
  - 사고 신고 관련 이벤트
  - 시스템 시작/종료

### 3. UI 로그 (JavaFX 출력)
- **위치**: 터미널 (UI 실행 중인 터미널)
- **내용**: JavaFX UI의 System.out.println() 출력
- **포함 내용**:
  - `[DataUpdater]` 로그
  - `[MainScreenController]` 로그
  - JSON 파일 읽기 오류

---

## 로그 확인 방법

### 방법 1: 실시간 로그 확인 (tail 명령어)

#### 백엔드 로그 실시간 확인
```bash
# 프로젝트 루트 디렉토리에서
tail -f backend.log
```

#### 마지막 50줄만 보기
```bash
tail -50 backend.log
```

#### 특정 키워드 필터링 (예: 사고 감지 관련)
```bash
tail -f backend.log | grep -i "report\|alert\|impact"
```

### 방법 2: 전체 로그 파일 보기

#### 백엔드 로그 전체 보기
```bash
cat backend.log
```

#### less 명령어로 스크롤 가능하게 보기
```bash
less backend.log
# 나가기: q 키
# 다음 페이지: 스페이스바
# 이전 페이지: b 키
# 검색: /키워드 입력 후 Enter
```

### 방법 3: 이벤트 로그 확인

#### 이벤트 로그 보기
```bash
cat driving_events.log
```

#### 최근 이벤트만 보기
```bash
tail -20 driving_events.log
```

### 방법 4: 라즈베리파이에서 확인

#### SSH로 접속한 경우
```bash
# 프로젝트 디렉토리로 이동
cd ~/iotPy/iot_project_OOP

# 백엔드 로그 확인
tail -f backend.log

# 또는 실시간으로 필터링
tail -f backend.log | grep "ALERT\|IMPACT\|Report"
```

#### 라즈베리파이 직접 접속한 경우
- 터미널을 열고 프로젝트 디렉토리로 이동
- 위와 동일한 명령어 사용

---

## 주요 로그 키워드

### 사고 감지 관련
- `[Report] ===== IMPACT REGISTERED =====` - 충격 등록됨
- `[Report] ===== ALERT TRIGGERED =====` - 알림 트리거됨
- `[Report] Eyes closed for` - 눈 감김 시간
- `[Report] No face for` - 얼굴 미감지 시간
- `[Report] Monitoring:` - 모니터링 상태
- `[DataBridge] ALERT status detected!` - ALERT 상태 감지됨
- `[DriverMonitor] Impact registered` - 충격 등록됨

### 졸음 감지 관련
- `[DriverMonitor] Drowsiness detected` - 졸음 감지됨
- `[FatigueDetector]` - 졸음 감지기 로그

### 스피커 관련
- `[DriverMonitor] Speaker stopped by UI request` - UI에서 스피커 중지 요청
- `[MainScreenController] Stop speaker request` - 스피커 중지 요청 파일 생성

### UI 관련
- `[DataUpdater] Response requested detected` - 응답 요청 감지됨
- `[DataUpdater] Showing response modal` - 응답 모달 표시
- `[MainScreenController] Showing response modal` - 응답 모달 표시

---

## 로그 검색 예제

### 사고 감지 플로우 전체 추적
```bash
# 백엔드 로그에서 사고 감지 관련 모든 로그 확인
grep -i "impact\|alert\|report\|response" backend.log | tail -50
```

### 특정 시간대 로그 확인
```bash
# 오늘 날짜의 로그만 확인
grep "$(date +%Y-%m-%d)" backend.log
```

### 오류만 확인
```bash
grep -i "error\|failed\|exception" backend.log
```

### ALERT 상태 확인
```bash
grep "ALERT" backend.log | tail -20
```

---

## 실시간 모니터링

### 여러 터미널 사용 (권장)

#### 터미널 1: 백엔드 로그 실시간 확인
```bash
cd ~/iotPy/iot_project_OOP
tail -f backend.log
```

#### 터미널 2: 사고 감지 관련만 필터링
```bash
cd ~/iotPy/iot_project_OOP
tail -f backend.log | grep --line-buffered -i "report\|alert\|impact"
```

#### 터미널 3: 시스템 실행
```bash
cd ~/iotPy/iot_project_OOP
./start_all.sh
```

---

## 로그 파일 크기 관리

### 로그 파일이 너무 커진 경우

#### 백엔드 로그 초기화
```bash
# 백엔드 중지 후
> backend.log  # 파일 내용 지우기
```

#### 이벤트 로그 초기화
```bash
# UI의 설정 → 시스템 로그 초기화 버튼 사용
# 또는 수동으로
> driving_events.log
```

---

## 문제 해결을 위한 로그 확인 순서

### 사고 감지 팝업이 안 뜨는 경우

1. **충격이 등록되었는지 확인**
   ```bash
   grep "IMPACT REGISTERED" backend.log
   ```

2. **모니터링이 진행 중인지 확인**
   ```bash
   grep "Monitoring:" backend.log | tail -10
   ```

3. **조건이 충족되었는지 확인**
   ```bash
   grep "CONDITION MET\|Eyes closed for\|No face for" backend.log | tail -10
   ```

4. **ALERT 상태가 반환되었는지 확인**
   ```bash
   grep "ALERT TRIGGERED\|ALERT status detected" backend.log | tail -10
   ```

5. **UI가 응답 요청을 감지했는지 확인**
   - UI 실행 중인 터미널에서 확인
   - 또는 `status.json` 파일 확인:
   ```bash
   cat data/status.json | grep response_requested
   ```

---

## JSON 상태 파일 확인

### 실시간 상태 확인
```bash
# status.json 확인 (사고 감지 상태)
cat data/status.json | python3 -m json.tool

# drowsiness.json 확인 (졸음 상태)
cat data/drowsiness.json | python3 -m json.tool

# log_summary.json 확인 (운전 점수)
cat data/log_summary.json | python3 -m json.tool
```

### response_requested 확인
```bash
cat data/status.json | grep -A 2 response_requested
```

---

## 로그 레벨별 확인

### 중요 로그만 확인 (ERROR, ALERT)
```bash
grep -E "ERROR|ALERT|FAILED|Exception" backend.log
```

### 정보 로그 확인 (INFO)
```bash
grep -E "\[Report\]|\[DriverMonitor\]|\[DataBridge\]" backend.log | tail -50
```

### 디버그 로그 확인 (DEBUG)
```bash
grep -E "DEBUG|Monitoring:" backend.log | tail -50
```

---

## 라즈베리파이 특별 사항

### 라즈베리파이에서 로그 확인
- 기본 경로: `/home/pi/iotPy/iot_project_OOP/backend.log`
- 또는 프로젝트가 다른 위치에 있다면 해당 경로 확인

### 원격 로그 확인 (SSH)
```bash
# SSH로 접속
ssh pi@raspberrypi-ip

# 프로젝트 디렉토리로 이동
cd ~/iotPy/iot_project_OOP

# 로그 확인
tail -f backend.log
```

---

## 로그 파일 위치 요약

| 로그 타입 | 파일 경로 | 설명 |
|---------|---------|------|
| 백엔드 콘솔 | `backend.log` | Python 백엔드의 모든 출력 |
| 이벤트 로그 | `driving_events.log` | 운전 이벤트 기록 |
| 상태 JSON | `data/status.json` | 시스템 상태 (UI용) |
| 졸음 JSON | `data/drowsiness.json` | 졸음 상태 (UI용) |
| 로그 요약 | `data/log_summary.json` | 운전 점수 및 통계 (UI용) |

---

## 빠른 참조 명령어

```bash
# 실시간 백엔드 로그 확인
tail -f backend.log

# 사고 감지 관련 로그만 실시간 확인
tail -f backend.log | grep --line-buffered -i "report\|alert\|impact"

# 최근 50줄 확인
tail -50 backend.log

# 특정 키워드 검색
grep "키워드" backend.log

# 오류만 확인
grep -i "error\|failed" backend.log

# 오늘 날짜 로그만 확인
grep "$(date +%Y-%m-%d)" backend.log
```

