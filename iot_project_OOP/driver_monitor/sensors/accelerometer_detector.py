# accelerometer_detector.py
import datetime
import sys
import os

# 프로젝트 루트를 Python path에 추가 (라즈베리파이 호환성)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import board
    import busio
    import adafruit_adxl34x
    IS_RPI = True
except ImportError:
    IS_RPI = False

from config import ACCEL_THRESHOLD, IMPACT_CHECK_DELAY, ALERT_CONFIRM_DELAY

class AccelerometerDetector:
    def __init__(self):
        self.accel = None
        self.impact_check_mode = False
        self.impact_time = datetime.datetime.min
        self.alert_start_time = None
        self.last_event_time = datetime.datetime.now()
        self.last_event_text = ""

    def initialize(self):
        if not IS_RPI:
            print("[Accel] Not RPi environment.")
            return

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.accel = adafruit_adxl34x.ADXL345(i2c)
            print("[Accel] ADXL345 initialized.")
        except Exception as e:
            print(f"[Accel] init failed: {e}")
            self.accel = None

    def read_accel(self):
        if self.accel is None:
            return None, None

        x, y, z = self.accel.acceleration
        return (x, y, z), self._detect_event(x)

    def _detect_event(self, x):
        t_now = datetime.datetime.now()
        event = None

        if x > ACCEL_THRESHOLD:
            event = "sudden acceleration"
        elif x < -ACCEL_THRESHOLD:
            event = "sudden stop"

        if event:
            self.last_event_time = t_now
            self.last_event_text = f"{event}: {x:.2f} m/s^2"
            self.impact_check_mode = True
            self.impact_time = t_now
            self.alert_start_time = None

        return event


