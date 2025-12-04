# driver_monitor/emergency/emergency_manager.py

import datetime
from logging_system.event_logger import log_event


class EmergencyManager:
    """
    Handles impact detection → response check → emergency alert sequence.
    Implements:
      - 10s response check after impact
      - 20s full emergency trigger
    """

    def __init__(self, impact_delay=10.0, alert_delay=20.0):
        self.impact_delay = impact_delay
        self.alert_delay = alert_delay

        self.impact_mode = False     # 충격 감지 후 모드
        self.impact_time = None      # 충격 발생 시간

        self.alert_start_time = None # “응답 확인” 시작 시간

    # -----------------------
    # 1) 충격 발생 시 호출
    # -----------------------
    def register_impact(self, accel_value: float):
        """ADXL345에서 임계값 초과 시 호출"""
        self.impact_mode = True
        self.impact_time = datetime.datetime.now()
        self.alert_start_time = None

        # 로그 기록
        if accel_value > 0:
            log_event("sudden acceleration")
        else:
            log_event("sudden stop")

        print(f"[Emergency] Impact detected: {accel_value:.2f} m/s^2")

    # -----------------------
    # 2) 매 프레임마다 상태 업데이트
    # -----------------------
    def update(self, face_detected: bool, ear_low: bool):
        """
        main.py 루프에서 매 프레임 호출
        face_detected: 얼굴이 보이는지 여부
        ear_low: 졸음 EAR 조건 충족 여부
        """

        if not self.impact_mode:
            return None  # 긴급 상황 없음

        now = datetime.datetime.now()

        # ===========================
        # A) 사용자가 반응함 → 정상으로 복귀
        # ===========================
        # EAR 정상 + 얼굴 감지됨 → 반응한 것
        if face_detected and not ear_low:
            print("[Emergency] User responded after impact.")
            self.reset()
            return None

        # ===========================
        # B) 10초 경과 → 응답 확인 모드 시작
        # ===========================
        if (self.alert_start_time is None and
                (now - self.impact_time).total_seconds() >= self.impact_delay):

            print("[Emergency] No response for 10 seconds → checking user response")
            self.alert_start_time = now

            return "CHECKING_RESPONSE"   # UI/overlay에서 표시 가능

        # ===========================
        # C) 응답 확인 모드 상태 유지
        # ===========================
        if self.alert_start_time is not None:
            elapsed = (now - self.alert_start_time).total_seconds()

            # UI에 남은 시간을 표시 가능
            remaining = self.alert_delay - elapsed

            if remaining > 0:
                return ("WAITING_RESPONSE", remaining)

            # ===========================
            # D) 20초 경과 → 비상 상황
            # ===========================
            print("[Emergency] No response for 20 seconds → EMERGENCY")
            log_event("emergency")
            self.reset()
            return "EMERGENCY"

        return None

    # -----------------------
    # 상태 리셋
    # -----------------------
    def reset(self):
        self.impact_mode = False
        self.impact_time = None
        self.alert_start_time = None

