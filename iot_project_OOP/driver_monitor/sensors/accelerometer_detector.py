# accelerometer_detector.py
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
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
        self.last_valid_data = None  # Last valid value read (used when read fails)

    def initialize(self):
        if not IS_RPI:
            print("[Accel] Not RPi environment. Accelerometer will not be available.")
            print("[Accel] To use accelerometer, run on Raspberry Pi with ADXL345 connected via I2C.")
            return

        try:
            print("[Accel] Attempting to initialize ADXL345...")
            i2c = busio.I2C(board.SCL, board.SDA)
            print("[Accel] I2C bus initialized.")
            self.accel = adafruit_adxl34x.ADXL345(i2c)
            print("[Accel] ADXL345 initialized successfully.")
        except RuntimeError as e:
            print(f"[Accel] ADXL345 not found on I2C bus: {e}")
            print("[Accel] Please check:")
            print("[Accel]   1. ADXL345 is connected to I2C pins (SDA/SCL)")
            print("[Accel]   2. I2C is enabled: sudo raspi-config -> Interface Options -> I2C -> Enable")
            print("[Accel]   3. Check I2C devices: sudo i2cdetect -y 1")
            self.accel = None
        except Exception as e:
            print(f"[Accel] Initialization failed: {type(e).__name__}: {e}")
            print("[Accel] Accelerometer will not be available.")
            self.accel = None

    def is_available(self):
        """Check if accelerometer is available."""
        return self.accel is not None
    
    def read_accel(self):
        if self.accel is None:
            # Return previous value if sensor is not available (if available)
            return self.last_valid_data, None

        try:
            x, y, z = self.accel.acceleration
            data = (x, y, z)
            self.last_valid_data = data  # Store valid value
            return data, self._detect_event(x)
        except Exception as e:
            # Return previous value on read failure (temporary error handling)
            print(f"[Accel] Read failed: {e}, using last valid data")
            return self.last_valid_data, None

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


