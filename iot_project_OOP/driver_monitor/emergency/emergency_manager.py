# driver_monitor/emergency/emergency_manager.py

import datetime
import sys
import os

# 프로젝트 루트를 Python path에 추가 (라즈베리파이 호환성)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from driver_monitor.logging_system.event_logger import EventLogger


class EmergencyManager:
    """
    Handles impact detection → response check → emergency alert sequence.
    Implements:
      - 10s response check after impact
      - 20s full emergency trigger
    """

    def __init__(self, impact_delay=10.0, alert_delay=20.0, logger=None):
        self.impact_delay = impact_delay
        self.alert_delay = alert_delay

        self.impact_mode = False     
        self.impact_time = None      

        self.alert_start_time = None
        
        # Use provided logger or create a new one
        self.logger = logger if logger is not None else EventLogger()

 
    def register_impact(self, accel_value: float):
        """ADXL345에서 임계값 초과 시 호출"""
        self.impact_mode = True
        self.impact_time = datetime.datetime.now()
        self.alert_start_time = None

       
        if accel_value > 0:
            self.logger.log("sudden acceleration")
        else:
            self.logger.log("sudden stop")

        print(f"[Emergency] Impact detected: {accel_value:.2f} m/s^2")

    def update(self, face_detected: bool, ear_low: bool):
        """
        main.py 루프에서 매 프레임 호출
        face_detected: 얼굴이 보이는지 여부
        ear_low: 졸음 EAR 조건 충족 여부
        """

        if not self.impact_mode:
            return None

        now = datetime.datetime.now()

 
        if face_detected and not ear_low:
            print("[Emergency] User responded after impact.")
            self.reset()
            return None

 
        if (self.alert_start_time is None and
                (now - self.impact_time).total_seconds() >= self.impact_delay):

            print("[Emergency] No response for 10 seconds → checking user response")
            self.alert_start_time = now

            return "CHECKING_RESPONSE" 

    
        if self.alert_start_time is not None:
            elapsed = (now - self.alert_start_time).total_seconds()

     
            remaining = self.alert_delay - elapsed

            if remaining > 0:
                return ("WAITING_RESPONSE", remaining)

     
            print("[Emergency] No response for 20 seconds → EMERGENCY")
            self.logger.log("emergency")
            self.reset()
            return "EMERGENCY"

        return None

 
    def reset(self):
        self.impact_mode = False
        self.impact_time = None
        self.alert_start_time = None

