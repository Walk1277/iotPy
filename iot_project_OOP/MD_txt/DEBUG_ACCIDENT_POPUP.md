# 사고 감지 팝업 디버깅 가이드

## 단계별 확인 방법

### 1단계: 가속도계 이벤트 발생 확인

#### 확인 명령어
```bash
# backend.log에서 충격 등록 로그 확인
grep "Impact registered for report system" backend.log

# 또는 실시간으로 확인
tail -f backend.log | grep --line-buffered "Impact registered"
```

#### 정상적인 경우
```
[DriverMonitor] Impact registered for report system: HH:MM:SS
[Report] ===== IMPACT REGISTERED =====
[Report] Impact registered at HH:MM:SS. Monitoring for 60s.
```

#### 문제가 있는 경우
- 로그가 없음 → 가속도계 이벤트가 발생하지 않음
- 해결: 가속도계 센서 연결 확인, `check_system.py`로 테스트

---

### 2단계: 모니터링 기간 내 조건 충족 확인

#### 확인 명령어
```bash
# 모니터링 상태 확인
grep "Monitoring:" backend.log | tail -20

# 눈 감김 조건 확인
grep "Eyes closed" backend.log | tail -20

# 얼굴 미감지 조건 확인
grep "No face" backend.log | tail -20
```

#### 정상적인 경우
```
[Report] Monitoring: elapsed=2.3s, eyes_closed=False, no_face=False, face_detected=True, ear=0.250
[Report] Eyes closed detected: EAR=0.180 < threshold=0.200, starting timer
[Report] Eyes closed for 10.5s >= 10s - CONDITION MET!
```

또는

```
[Report] No face detected, starting timer
[Report] No face for 10.2s >= 10s - CONDITION MET!
```

#### 문제가 있는 경우
- `Monitoring:` 로그가 없음 → 모니터링 기간이 지났거나 충격이 등록되지 않음
- 조건이 충족되지 않음 → 10초 이상 지속되지 않음
- 해결: 
  - 충격 후 1분 이내에 조건을 충족해야 함
  - 눈을 감거나 얼굴을 가리고 10초 이상 유지

---

### 3단계: ALERT 상태 반환 확인

#### 확인 명령어
```bash
# ALERT 트리거 확인
grep "ALERT TRIGGERED" backend.log | tail -10

# ALERT 상태 반환 확인
grep "Returning ALERT status" backend.log | tail -10

# 전체 ALERT 관련 로그
grep -i "alert" backend.log | tail -20
```

#### 정상적인 경우
```
[Report] ===== ALERT TRIGGERED =====
[Report] Emergency condition met (eyes closed)! Alert started.
[Report] Impact detected. Monitoring for 60s. Condition: eyes closed
[Report] Returning ALERT status to trigger UI popup
[Report] Alert status: {'status': 'ALERT', 'message': 'Touch screen within 10 seconds to cancel report', 'remaining_time': 10.0}
```

#### 문제가 있는 경우
- `ALERT TRIGGERED` 로그가 없음 → 조건이 충족되지 않음
- 해결: 2단계 확인 후 조건 충족 여부 재확인

---

### 4단계: DataBridge에서 response_requested 설정 확인

#### 확인 명령어
```bash
# DataBridge ALERT 감지 확인
grep "ALERT status detected" backend.log | tail -10

# response_requested 설정 확인
grep "Response requested:" backend.log | tail -10
```

#### 정상적인 경우
```
[DataBridge] ALERT status detected! Response requested: True, message: Touch screen within 10 seconds to cancel report, remaining: 10.0s
```

#### 문제가 있는 경우
- 로그가 없음 → ALERT 상태가 DataBridge에 전달되지 않음
- 해결: `status.json` 파일 직접 확인

#### status.json 직접 확인
```bash
# status.json 파일 확인
cat data/status.json | python3 -m json.tool

# 또는 response_requested만 확인
cat data/status.json | grep -A 2 response_requested
```

정상적인 경우:
```json
{
  "response_requested": true,
  "response_message": "Touch screen within 10 seconds to cancel report",
  "response_remaining_time": 10.0
}
```

---

### 5단계: UI가 status.json을 읽는지 확인

#### 확인 방법 1: UI 터미널 확인
- UI를 실행한 터미널에서 확인
- JavaFX UI가 실행 중인 터미널 창 확인

#### 확인 명령어 (UI 로그가 파일로 저장된 경우)
```bash
# UI 로그 파일이 있다면
grep "Response requested detected" ui.log 2>/dev/null || echo "UI 로그 파일이 없습니다"
```

#### 정상적인 경우 (UI 터미널에서)
```
[DataUpdater] Response requested detected in status.json
[DataUpdater] Showing response modal - message: Touch screen within 10 seconds to cancel report, remaining: 10.0
[MainScreenController] Showing response modal.
```

#### 문제가 있는 경우
- 로그가 없음 → UI가 `status.json`을 읽지 못함
- 해결: 
  - `status.json` 파일 경로 확인
  - UI가 올바른 경로에서 파일을 읽는지 확인
  - 파일 권한 확인

---

## 전체 플로우 한 번에 확인

### 모든 단계를 한 번에 확인하는 스크립트

```bash
#!/bin/bash
# check_accident_detection.sh

echo "=== 1단계: 가속도계 이벤트 확인 ==="
grep "Impact registered for report system" backend.log | tail -3
echo ""

echo "=== 2단계: 모니터링 상태 확인 ==="
grep "Monitoring:" backend.log | tail -5
echo ""

echo "=== 3단계: 조건 충족 확인 ==="
grep -E "Eyes closed for|No face for|CONDITION MET" backend.log | tail -5
echo ""

echo "=== 4단계: ALERT 상태 확인 ==="
grep "ALERT TRIGGERED\|Returning ALERT status" backend.log | tail -5
echo ""

echo "=== 5단계: DataBridge 확인 ==="
grep "ALERT status detected" backend.log | tail -3
echo ""

echo "=== 6단계: status.json 확인 ==="
if [ -f "data/status.json" ]; then
    cat data/status.json | python3 -m json.tool | grep -A 3 response_requested
else
    echo "status.json 파일이 없습니다"
fi
```

### 실시간 모니터링 (권장)

#### 터미널 1: 전체 로그 실시간 확인
```bash
tail -f backend.log
```

#### 터미널 2: 사고 감지 관련만 필터링
```bash
tail -f backend.log | grep --line-buffered -E "IMPACT|ALERT|Monitoring|Eyes closed|No face|CONDITION MET|Response requested"
```

#### 터미널 3: status.json 실시간 확인
```bash
watch -n 1 'cat data/status.json | python3 -m json.tool | grep -A 3 response_requested'
```

---

## 문제 해결 체크리스트

### ✅ 체크리스트

1. **가속도계 이벤트 발생**
   - [ ] `grep "Impact registered" backend.log` 결과가 있음
   - [ ] `[Report] ===== IMPACT REGISTERED =====` 로그 확인

2. **모니터링 기간 내**
   - [ ] 충격 후 1분 이내
   - [ ] `[Report] Monitoring:` 로그가 계속 출력됨

3. **조건 충족**
   - [ ] 눈 감김 10초 이상: `[Report] Eyes closed for 10.Xs >= 10s`
   - [ ] 또는 얼굴 미감지 10초 이상: `[Report] No face for 10.Xs >= 10s`

4. **ALERT 상태 반환**
   - [ ] `[Report] ===== ALERT TRIGGERED =====` 로그 확인
   - [ ] `[Report] Returning ALERT status` 로그 확인

5. **DataBridge 처리**
   - [ ] `[DataBridge] ALERT status detected!` 로그 확인
   - [ ] `status.json`에 `response_requested: true` 확인

6. **UI 읽기**
   - [ ] UI 터미널에 `[DataUpdater] Response requested detected` 로그 확인
   - [ ] `[MainScreenController] Showing response modal` 로그 확인

---

## 빠른 진단 명령어

### 한 줄로 모든 단계 확인
```bash
echo "=== 충격 등록 ===" && grep "Impact registered" backend.log | tail -1 && \
echo "=== ALERT 트리거 ===" && grep "ALERT TRIGGERED" backend.log | tail -1 && \
echo "=== DataBridge ===" && grep "ALERT status detected" backend.log | tail -1 && \
echo "=== status.json ===" && cat data/status.json 2>/dev/null | python3 -m json.tool | grep response_requested
```

### 실시간으로 모든 단계 모니터링
```bash
tail -f backend.log | grep --line-buffered -E "IMPACT REGISTERED|Monitoring:|Eyes closed for|No face for|CONDITION MET|ALERT TRIGGERED|ALERT status detected"
```

---

## 일반적인 문제와 해결책

### 문제 1: 충격이 등록되지 않음
**증상**: `Impact registered` 로그가 없음

**확인**:
```bash
grep "sudden\|acceleration\|stop" backend.log | tail -10
```

**해결**:
- 가속도계 센서 연결 확인
- `check_system.py`로 가속도계 테스트
- `ACCEL_THRESHOLD` 값 확인 (기본값: 2.0 m/s²)

### 문제 2: 조건이 충족되지 않음
**증상**: `CONDITION MET` 로그가 없음

**확인**:
```bash
grep "Monitoring:" backend.log | tail -10
```

**해결**:
- 충격 후 1분 이내에 조건 충족 필요
- 눈 감김: 10초 이상 지속
- 얼굴 미감지: 10초 이상 지속
- 조건이 중간에 리셋되지 않도록 주의

### 문제 3: ALERT 상태가 반환되지 않음
**증상**: `ALERT TRIGGERED` 로그가 없음

**확인**:
```bash
grep -E "eyes_closed_condition|no_face_condition|report_mode" backend.log | tail -10
```

**해결**:
- `AUTO_REPORT_ENABLED`가 `True`인지 확인
- 모니터링 기간이 지나지 않았는지 확인

### 문제 4: DataBridge가 ALERT를 감지하지 않음
**증상**: `ALERT status detected` 로그가 없음

**확인**:
```bash
grep "Report status:" backend.log | tail -10
cat data/status.json | python3 -m json.tool | grep -A 5 report_status
```

**해결**:
- `report_status`가 `status.json`에 제대로 포함되는지 확인
- `data_bridge.py`의 `update_system_status` 호출 확인

### 문제 5: UI가 status.json을 읽지 않음
**증상**: UI 터미널에 로그가 없음

**확인**:
```bash
# status.json 파일 확인
ls -lh data/status.json
cat data/status.json | python3 -m json.tool

# UI가 읽는 경로 확인
# Java 코드에서 여러 경로를 시도하므로 파일이 올바른 위치에 있는지 확인
```

**해결**:
- `data/status.json` 파일이 존재하는지 확인
- 파일 권한 확인: `chmod 644 data/status.json`
- UI가 실행 중인지 확인
- UI 터미널에서 오류 메시지 확인

---

## 테스트 시나리오

### 시나리오 1: 급정거 테스트
1. 시스템 실행
2. 급정거 시뮬레이션 (가속도계 이벤트 발생)
3. 즉시 눈을 감고 10초 이상 유지
4. 각 단계별 로그 확인

### 시나리오 2: 얼굴 미감지 테스트
1. 시스템 실행
2. 급가속 시뮬레이션
3. 즉시 얼굴을 가리고 10초 이상 유지
4. 각 단계별 로그 확인

---

## 로그 파일 위치

- **백엔드 로그**: `backend.log` (프로젝트 루트)
- **이벤트 로그**: `driving_events.log` (프로젝트 루트)
- **상태 JSON**: `data/status.json`
- **UI 로그**: UI 실행 터미널 (파일로 저장되지 않음)

---

## 추가 도움말

더 자세한 로그 확인 방법은 `HOW_TO_VIEW_LOGS.md`를 참조하세요.

