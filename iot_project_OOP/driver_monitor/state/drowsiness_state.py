# drowsiness_state.py
"""
Drowsiness detection state management.
Handles alarm state, timing, and speaker activation logic.
"""
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try both relative and absolute imports for Raspberry Pi compatibility
try:
    from ..config.config_manager import ConfigManager
except ImportError:
    from driver_monitor.config.config_manager import ConfigManager


class DrowsinessState:
    """
    Manages drowsiness detection state and speaker activation logic.
    """
    
    def __init__(self, logger=None, config_manager=None):
        """
        Args:
            logger: EventLogger instance (optional)
            config_manager: ConfigManager instance (optional, will create singleton if not provided)
        """
        self.logger = logger
        self.config_manager = config_manager or ConfigManager()
        
        # State variables
        self.alarm_on = False
        self.prev_alarm_on = False
        self.alarm_start_time = None
        self.no_face_start_time = None
        
    def update(self, face_detected, alarm_on, is_driving, gps_speed):
        """
        Update drowsiness state based on current conditions.
        
        Args:
            face_detected: bool, Whether face is detected
            alarm_on: bool, Whether drowsiness alarm is active (from fatigue detector)
            is_driving: bool, Whether vehicle is driving
            gps_speed: float, GPS speed in km/h
            
        Returns:
            dict: State information with keys:
                - should_activate_speaker: bool
                - alarm_duration: float
                - show_speaker_popup: bool
                - no_face_duration: float
        """
        self.alarm_on = alarm_on
        
        # Determine if speaker should be active
        # Speaker should be active when:
        # 1. Driving AND (drowsiness detected OR no face for 10+ seconds)
        # 2. Not driving: do NOT activate speaker (parked state)
        should_activate_speaker = False
        no_face_duration = 0.0
        
        if is_driving:
            # When driving: check conditions
            if alarm_on:
                # Drowsiness detected while driving - activate speaker immediately
                should_activate_speaker = True
                self.no_face_start_time = None  # Reset no face timer
            elif not face_detected:
                # No face detected while driving - start timer
                if self.no_face_start_time is None:
                    self.no_face_start_time = datetime.datetime.now()
                
                # Calculate how long no face has been detected
                no_face_duration = (datetime.datetime.now() - self.no_face_start_time).total_seconds()
                timeout = self.config_manager.get('NO_FACE_WHILE_DRIVING_TIMEOUT', 10.0)
                
                # Activate speaker only after timeout
                if no_face_duration >= timeout:
                    should_activate_speaker = True
            else:
                # Face detected - reset no face timer
                self.no_face_start_time = None
        else:
            # When not driving: do NOT activate speaker
            # Even if drowsiness detected or no face, only show alert in UI
            should_activate_speaker = False
            self.no_face_start_time = None  # Reset timer when not driving
        
        # Check if alarm state changed (from off to on)
        if should_activate_speaker and not self.prev_alarm_on:
            # Alarm just turned on - log the event
            if alarm_on:
                if self.logger:
                    self.logger.log("drowsiness")
                print(f"[DrowsinessState] Drowsiness detected and logged.")
            elif not face_detected and is_driving:
                if self.logger:
                    self.logger.log("no_face_while_driving")
                print(f"[DrowsinessState] No face detected for {no_face_duration:.1f}s while driving (Speed: {gps_speed:.1f} km/h)")
            self.alarm_start_time = datetime.datetime.now()
        
        # Calculate alarm duration and check if popup should be shown
        alarm_duration = 0.0
        show_speaker_popup = False
        
        if should_activate_speaker:
            if self.alarm_start_time:
                alarm_duration = (datetime.datetime.now() - self.alarm_start_time).total_seconds()
                if alarm_duration >= 1.0:
                    show_speaker_popup = True
        
        # Update prev_alarm_on AFTER checking state change
        self.prev_alarm_on = should_activate_speaker
        
        return {
            'should_activate_speaker': should_activate_speaker,
            'alarm_duration': alarm_duration,
            'show_speaker_popup': show_speaker_popup,
            'no_face_duration': no_face_duration
        }
    
    def handle_stop_speaker_request(self):
        """
        Handle UI request to stop speaker.
        
        Returns:
            bool: True if speaker was active and should be stopped
        """
        was_active = self.prev_alarm_on
        if was_active:
            self.alarm_start_time = None
            self.prev_alarm_on = False
        return was_active
    
    def reset(self):
        """Reset all state variables."""
        self.alarm_on = False
        self.prev_alarm_on = False
        self.alarm_start_time = None
        self.no_face_start_time = None

