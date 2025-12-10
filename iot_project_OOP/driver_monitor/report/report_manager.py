# report_manager.py
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import (
    REPORT_ACCEL_THRESHOLD, 
    REPORT_NO_FACE_DURATION, 
    REPORT_RESPONSE_TIMEOUT,
    SMS_API_KEY,
    SMS_API_SECRET,
    SMS_FROM_NUMBER,
    SMS_TO_NUMBER,
    SMS_ENABLED
)
from driver_monitor.logging_system.event_logger import EventLogger

# Try to import SOLAPI for SMS functionality
try:
    from solapi import SolapiMessageService
    from solapi.model import RequestMessage
    SOLAPI_AVAILABLE = True
except ImportError:
    SOLAPI_AVAILABLE = False
    print("[Report] SOLAPI not available. SMS reporting will be disabled.")


class ReportManager:
    """
    Handles emergency report functionality.
    Conditions:
    1. Accelerometer detects 2g or more
    2. No face detected for 10 seconds
    3. When both conditions are met, show alert and wait for user response
    4. If no response within 10 seconds, proceed with report process
    """

    def __init__(self, logger=None, input_callback=None):
        """
        Args:
            logger: EventLogger instance (optional)
            input_callback: Callback function for user input (optional)
                           Should return True if user responded, False otherwise
                           This allows future UI integration (touch screen)
        """
        self.logger = logger if logger is not None else EventLogger()
        self.input_callback = input_callback  # For future UI integration
        
        # Initialize SMS service if available and enabled
        self.sms_service = None
        if SMS_ENABLED and SOLAPI_AVAILABLE:
            try:
                self.sms_service = SolapiMessageService(
                    api_key=SMS_API_KEY,
                    api_secret=SMS_API_SECRET
                )
                print("[Report] SMS service initialized.")
            except Exception as e:
                print(f"[Report] Failed to initialize SMS service: {e}")
                self.sms_service = None
        
        # State variables
        self.report_mode = False
        self.accel_triggered = False
        self.accel_trigger_time = None
        self.no_face_start_time = None
        self.alert_start_time = None
        self.user_responded = False
        self.sms_sent = False  # Track if SMS has been sent to avoid duplicates

    def check_accelerometer(self, accel_data):
        """
        Check if accelerometer detects 2g or more.
        
        Args:
            accel_data: Tuple of (x, y, z) acceleration values in m/s^2, or None
            
        Returns:
            bool: True if 2g or more detected
        """
        if accel_data is None:
            return False
        
        x, y, z = accel_data
        # Calculate magnitude
        magnitude = (x**2 + y**2 + z**2) ** 0.5
        
        if magnitude >= REPORT_ACCEL_THRESHOLD:
            if not self.accel_triggered:
                self.accel_triggered = True
                self.accel_trigger_time = datetime.datetime.now()
                print(f"[Report] High acceleration detected: {magnitude:.2f} m/s^2 (>= 2g)")
            return True
        else:
            # Reset if acceleration drops below threshold
            if self.accel_triggered:
                self.accel_triggered = False
                self.accel_trigger_time = None
            return False

    def check_no_face(self, face_detected):
        """
        Check if no face has been detected for the required duration.
        
        Args:
            face_detected: bool, True if face is detected
            
        Returns:
            bool: True if no face for required duration
        """
        if not face_detected:
            if self.no_face_start_time is None:
                self.no_face_start_time = datetime.datetime.now()
            
            elapsed = (datetime.datetime.now() - self.no_face_start_time).total_seconds()
            if elapsed >= REPORT_NO_FACE_DURATION:
                return True
        else:
            # Reset if face is detected
            self.no_face_start_time = None
        
        return False

    def update(self, accel_data, face_detected, keyboard_input=None):
        """
        Update report manager state. Called every frame.
        
        Args:
            accel_data: Tuple of (x, y, z) acceleration values, or None
            face_detected: bool, True if face is detected
            keyboard_input: str or None, keyboard input from user (for current implementation)
            
        Returns:
            dict: Status information with keys:
                - 'status': str, one of 'NORMAL', 'CHECKING', 'ALERT', 'REPORTING'
                - 'message': str, message to display
                - 'remaining_time': float, remaining seconds (if in alert mode)
        """
        now = datetime.datetime.now()
        
        # Check conditions
        accel_condition = self.check_accelerometer(accel_data)
        no_face_condition = self.check_no_face(face_detected)
        
        # Both conditions met - enter report mode
        if accel_condition and no_face_condition and not self.report_mode:
            self.report_mode = True
            self.alert_start_time = now
            self.user_responded = False
            self.sms_sent = False  # Reset SMS sent flag for new alert
            self.logger.log("report_alert_triggered")
            print("[Report] Emergency conditions met! Alert started.")
            return {
                'status': 'ALERT',
                'message': 'Press any key within 10 seconds to cancel report',
                'remaining_time': REPORT_RESPONSE_TIMEOUT
            }
        
        # In report mode - check for user response
        if self.report_mode:
            # Check keyboard input (current implementation)
            if keyboard_input is not None:
                self.user_responded = True
                self.report_mode = False
                self.accel_triggered = False
                self.no_face_start_time = None
                self.alert_start_time = None
                self.sms_sent = False  # Reset SMS flag
                self.logger.log("report_cancelled")
                print("[Report] User responded. Report cancelled.")
                return {'status': 'NORMAL', 'message': '', 'remaining_time': 0}
            
            # Check UI callback (for future implementation)
            if self.input_callback is not None:
                if self.input_callback():
                    self.user_responded = True
                    self.report_mode = False
                    self.accel_triggered = False
                    self.no_face_start_time = None
                    self.alert_start_time = None
                    self.sms_sent = False  # Reset SMS flag
                    self.logger.log("report_cancelled")
                    print("[Report] User responded via UI. Report cancelled.")
                    return {'status': 'NORMAL', 'message': '', 'remaining_time': 0}
            
            # Check timeout
            if self.alert_start_time is not None:
                elapsed = (now - self.alert_start_time).total_seconds()
                remaining = REPORT_RESPONSE_TIMEOUT - elapsed
                
                if remaining > 0:
                    return {
                        'status': 'ALERT',
                        'message': f'Press any key within {remaining:.1f} seconds to cancel report',
                        'remaining_time': remaining
                    }
                else:
                    # Timeout - proceed with report
                    self.report_mode = False
                    self.accel_triggered = False
                    self.no_face_start_time = None
                    self.alert_start_time = None
                    self.logger.log("report_triggered")
                    
                    # Send SMS report
                    self._send_sms_report(accel_data)
                    
                    print("[Report] No response received. Report process initiated.")
                    return {
                        'status': 'REPORTING',
                        'message': 'Report process initiated',
                        'remaining_time': 0
                    }
        
        # Reset conditions if they are no longer met
        if not accel_condition or not no_face_condition:
            if self.report_mode:
                self.report_mode = False
                self.alert_start_time = None
                self.user_responded = False
        
        return {'status': 'NORMAL', 'message': '', 'remaining_time': 0}

    def _send_sms_report(self, accel_data=None):
        """
        Send SMS report when emergency conditions are met and no response received.
        
        Args:
            accel_data: Tuple of (x, y, z) acceleration values, or None
        """
        if not SMS_ENABLED or not self.sms_service:
            print("[Report] SMS reporting is disabled or service not available.")
            return
        
        if self.sms_sent:
            print("[Report] SMS already sent. Skipping duplicate.")
            return
        
        try:
            # Create emergency message
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if accel_data:
                x, y, z = accel_data
                magnitude = (x**2 + y**2 + z**2) ** 0.5
                message_text = (
                    f"[긴급신고] 운전자 모니터링 시스템\n"
                    f"시간: {timestamp}\n"
                    f"상태: 가속도 {magnitude:.2f}m/s² 감지, 얼굴 미감지 10초 초과\n"
                    f"사용자 응답 없음. 긴급 상황으로 판단되어 신고합니다."
                )
            else:
                message_text = (
                    f"[긴급신고] 운전자 모니터링 시스템\n"
                    f"시간: {timestamp}\n"
                    f"상태: 얼굴 미감지 10초 초과\n"
                    f"사용자 응답 없음. 긴급 상황으로 판단되어 신고합니다."
                )
            
            # Create message object
            message = RequestMessage(
                from_=SMS_FROM_NUMBER,
                to=SMS_TO_NUMBER,
                text=message_text,
            )
            
            # Send message
            response = self.sms_service.send(message)
            
            print("[Report] SMS sent successfully!")
            print(f"  Group ID: {response.group_info.group_id}")
            print(f"  Total messages: {response.group_info.count.total}")
            print(f"  Success: {response.group_info.count.registered_success}")
            print(f"  Failed: {response.group_info.count.registered_failed}")
            
            self.sms_sent = True
            self.logger.log("sms_report_sent")
            
        except Exception as e:
            print(f"[Report] Failed to send SMS: {str(e)}")
            self.logger.log(f"sms_report_failed: {str(e)}")

    def reset(self):
        """Reset all state variables."""
        self.report_mode = False
        self.accel_triggered = False
        self.accel_trigger_time = None
        self.no_face_start_time = None
        self.alert_start_time = None
        self.user_responded = False
        self.sms_sent = False  # Reset SMS sent flag

