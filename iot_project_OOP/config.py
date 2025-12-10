# config.py

EAR_THRESHOLD = 0.20
CONSEC_FRAMES = 30

ACCEL_THRESHOLD = 4.0

IMPACT_CHECK_DELAY = 10.0
ALERT_CONFIRM_DELAY = 10.0

LEFT_EYE_IDXS = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDXS = [33, 160, 158, 133, 153, 144]

LOG_FILE = "driving_events.log"

CAM_WIDTH = 800
CAM_HEIGHT = 480

# Report system settings
REPORT_ACCEL_THRESHOLD = 19.6  # 2g in m/s^2 (2 * 9.8)
REPORT_NO_FACE_DURATION = 10.0  # seconds
REPORT_RESPONSE_TIMEOUT = 10.0  # seconds to wait for user response

# SMS report settings (SOLAPI)
SMS_API_KEY = "NCSAQFYKNA3STO4Y"  # Replace with your SOLAPI API key
SMS_API_SECRET = "AGRKNIE1BS6VKQQCXYACG6Z9HAW1XKXA"  # Replace with your SOLAPI API secret
SMS_FROM_NUMBER = "010-7220-5917"  # Replace with your registered sender number
SMS_TO_NUMBER = "010-4090-7445"  # Replace with recipient number
SMS_ENABLED = False  # Set to True to enable SMS reporting

