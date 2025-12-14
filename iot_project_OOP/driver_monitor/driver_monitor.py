# driver_monitor.py
import cv2
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
# May already be added by main.py, but prepare for direct execution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try both relative and absolute imports for Raspberry Pi compatibility
try:
    # Try relative import (when executed as a package)
    from .camera.camera_manager import CameraManager
    from .camera.overlay_renderer import OverlayRenderer
    from .fatigue.fatigue_detector import FatigueDetector
    from .sensors.accelerometer_detector import AccelerometerDetector
    from .sensors.speaker_controller import SpeakerController
    from .sensors.gps_manager import GPSManager
    from .logging_system.event_logger import EventLogger
    from .logging_system.log_parser import LogParser
    from .report.report_manager import ReportManager
    from .data_bridge import DataBridge
    from .state.drowsiness_state import DrowsinessState
    from .config.config_manager import ConfigManager
    from .processing.frame_processor import FrameProcessor
    from .utils.path_manager import PathManager
    from .utils.error_handler import ErrorHandler, ErrorType, ErrorSeverity
except ImportError:
    # Absolute import (when executed directly)
    from driver_monitor.camera.camera_manager import CameraManager
    from driver_monitor.camera.overlay_renderer import OverlayRenderer
    from driver_monitor.fatigue.fatigue_detector import FatigueDetector
    from driver_monitor.sensors.accelerometer_detector import AccelerometerDetector
    from driver_monitor.sensors.speaker_controller import SpeakerController
    from driver_monitor.sensors.gps_manager import GPSManager
    from driver_monitor.logging_system.event_logger import EventLogger
    from driver_monitor.logging_system.log_parser import LogParser
    from driver_monitor.report.report_manager import ReportManager
    from driver_monitor.data_bridge import DataBridge
    from driver_monitor.state.drowsiness_state import DrowsinessState
    from driver_monitor.config.config_manager import ConfigManager
    from driver_monitor.processing.frame_processor import FrameProcessor
    from driver_monitor.utils.path_manager import PathManager
    from driver_monitor.utils.error_handler import ErrorHandler, ErrorType, ErrorSeverity

# Use absolute import for config at project root (for backward compatibility)
# Note: ConfigManager should be used instead of direct config import
import config


class DriverMonitor:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        
        # Initialize config manager (singleton)
        self.config_manager = ConfigManager()
        
        # Initialize components
        try:
            self.camera = CameraManager(cam_index)
            self.fatigue = FatigueDetector()
            self.accel = AccelerometerDetector()
            
            # Use GPS_ENABLED from config to determine if GPS should be simulated
            gps_simulate = not self.config_manager.get('GPS_ENABLED', True)
            self.gps = GPSManager(simulate=gps_simulate)
            self.speaker = SpeakerController()
            self.overlay = OverlayRenderer()
            self.logger = EventLogger()
            self.report_manager = ReportManager(logger=self.logger, gps_manager=self.gps)
            self.data_bridge = DataBridge()  # For UI communication
            
            # Initialize state managers and processors
            self.drowsiness_state = DrowsinessState(logger=self.logger, config_manager=self.config_manager)
            self.frame_processor = FrameProcessor(overlay_renderer=self.overlay)
        except Exception as e:
            raise

        self.running = True
        self.last_accel_data = None  # 이전 가속도 값 유지 (UI 업데이트용)

    def initialize(self):
        """Initialize all components."""
        try:
            self.camera.initialize()

            # ADXL345
            self.accel.initialize()

            # GPS
            self.gps.initialize()

            # Speaker
            self.speaker.initialize()

            self.logger.log("Start program")
        except Exception as e:
            raise

    def run(self):
        self.initialize()
        
        # Track last registered impact to prevent duplicate registrations
        last_registered_impact_time = None

        # Accelerometer event display text
        accel_event_text = ""
        accel_event_time = datetime.datetime.now()

        print("Press 'q' to quit. UI is available for monitoring.")

        while self.running:

            # =========================================
            # 1) Camera frame capture
            # =========================================
            try:
                frame, frame_rgb = self.camera.get_frames()
            except (RuntimeError, Exception) as e:
                error_info = ErrorHandler.handle_camera_error(
                    error=e,
                    context="Frame capture",
                    logger=self.logger
                )
                if not error_info['can_continue']:
                    print("[DriverMonitor] Camera error is critical. Stopping.")
                    break
                # Try to continue with next frame
                continue

            imgH, imgW = frame.shape[:2]

            # =========================================
            # 2) Face and fatigue detection
            # =========================================
            analyze_result = self.fatigue.analyze(frame_rgb, imgW, imgH)
            face_detected = analyze_result[0]
            ear = analyze_result[1]
            # Handle tuple unpacking safely (Raspberry Pi compatibility)
            pts_tuple = analyze_result[2]
            if pts_tuple is not None:
                left_pts, right_pts = pts_tuple
            else:
                left_pts, right_pts = None, None
            alarm_on = analyze_result[3]
            
            # =========================================
            # 3) Drowsiness alarm handling
            # =========================================
            # Get GPS data to determine if vehicle is driving
            gps_data = self.gps.read_gps()
            gps_speed = 0.0
            is_driving = False
            if gps_data and len(gps_data) >= 4:
                gps_speed = gps_data[3]  # speed in km/h
                speed_threshold = self.config_manager.get('DRIVING_SPEED_THRESHOLD', 5.0)
                is_driving = gps_speed >= speed_threshold
            
            # Update drowsiness state (handles all state management logic)
            state_info = self.drowsiness_state.update(
                face_detected=face_detected,
                alarm_on=alarm_on,
                is_driving=is_driving,
                gps_speed=gps_speed
            )
            should_activate_speaker = state_info['should_activate_speaker']
            alarm_duration = state_info['alarm_duration']
            show_speaker_popup = state_info['show_speaker_popup']
            no_face_duration = state_info['no_face_duration']
            
            # Check for UI request to stop speaker
            stop_speaker_request = self._check_stop_speaker_request()
            if stop_speaker_request:
                was_active = self.drowsiness_state.handle_stop_speaker_request()
                if was_active:
                    self.speaker.alarm_off()
                    should_activate_speaker = False
                    print("[DriverMonitor] Speaker stopped by UI request")
            
            # Control speaker based on state
            if should_activate_speaker and not stop_speaker_request:
                self.speaker.alarm_on()
            else:
                if self.drowsiness_state.prev_alarm_on:
                    self.speaker.alarm_off()
            
            # Update UI data bridge (after calculating alarm_duration and show_speaker_popup)
            # For UI: show alarm_on based on actual drowsiness detection (not just speaker state)
            # This allows UI to show drowsiness alert even when not driving (without speaker)
            ui_alarm_on = alarm_on  # Show drowsiness state in UI regardless of driving status
            self.data_bridge.update_drowsiness_status(
                ear=ear if face_detected else None,
                face_detected=face_detected,
                alarm_on=ui_alarm_on,  # Show drowsiness detection state in UI
                alarm_duration=alarm_duration,
                show_speaker_popup=show_speaker_popup
            )

            # =========================================
            # 4) Frame overlay rendering (will be done later after report status)
            # =========================================

            # =========================================
            # 5) Accelerometer reading
            # =========================================
            accel_data = None
            event = None

            if self.accel.is_available():
                new_accel_data, event = self.accel.read_accel()
                
                # 가속도 센서 읽기 성공 시 값 저장, 실패 시 이전 값 사용
                if new_accel_data is not None:
                    accel_data = new_accel_data
                    self.last_accel_data = new_accel_data  # 성공한 값 저장
                else:
                    # 읽기 실패 시 이전 값 사용 (UI 업데이트 유지)
                    accel_data = self.last_accel_data
                    if accel_data is None:
                        # 처음이거나 이전 값이 없으면 기본값 (정지 상태)
                        accel_data = (0.0, 0.0, 9.8)  # 중력만 (정지 상태)

                if event:
                    self.logger.log(event)
                    accel_event_text = self.accel.last_event_text
                    accel_event_time = self.accel.last_event_time

                    # Register impact for report system (only once per impact event)
                    # Prevent duplicate registrations from the same impact_time
                    impact_time = self.accel.impact_time
                    if impact_time and impact_time != last_registered_impact_time:
                        self.report_manager.register_impact(impact_time)
                        last_registered_impact_time = impact_time
                        print(f"[DriverMonitor] Impact registered for report system: {impact_time.strftime('%H:%M:%S')}")
                    elif impact_time == last_registered_impact_time:
                        # Same impact already registered, skip
                        pass
            else:
                # 가속도 센서가 사용 불가능해도 이전 값 유지 (UI 업데이트 계속)
                accel_data = self.last_accel_data
                if accel_data is None:
                    accel_data = (0.0, 0.0, 9.8)  # 기본값

            # =========================================
            # 5.5) GPS position extraction (reuse data read above)
            # =========================================
            # GPS data already read above for driving detection
            gps_position = None
            if gps_data:
                gps_position = (gps_data[0], gps_data[1])  # (latitude, longitude)
            
            # =========================================
            # 5.6) Report system check (before keyboard input)
            # =========================================
            # Check for UI response (touch screen)
            ui_response = self._check_ui_response()
            
            # Update report manager (initial check without keyboard input)
            # Pass EAR and threshold for eyes closed detection
            # Get current threshold from config (supports runtime updates)
            current_threshold = self.config_manager.get('EAR_THRESHOLD', 0.2)
            
            # Use UI response if available, otherwise use keyboard input
            user_input = ui_response if ui_response is not None else None
            
            report_status = self.report_manager.update(
                face_detected=face_detected,
                ear=ear if face_detected else None,
                ear_threshold=current_threshold,
                keyboard_input=user_input
            )
            
            # Debug: Print report status if ALERT
            if report_status and report_status.get('status') == 'ALERT':
                print(f"[DriverMonitor] Report status ALERT: {report_status}")
            
            # Update system status for UI
            self.data_bridge.update_system_status(
                accel_data=accel_data,
                impact_detected=(event is not None),
                report_status=report_status,
                gps_position=gps_position,
                sensor_status=f"Camera: {'OK' if face_detected else 'Waiting'} / Accelerometer: {'OK' if self.accel.is_available() else 'Waiting'} / GPS: {'OK' if gps_position else 'Waiting'}"
            )
            
            # Update log summary periodically (every 60 frames ~ 2 seconds at 30fps)
            if hasattr(self, '_frame_count'):
                self._frame_count += 1
            else:
                self._frame_count = 0
            
            if self._frame_count % 60 == 0:
                self.data_bridge.update_log_summary()
            
            # =========================================
            # 6) Frame processing and overlay rendering
            # =========================================
            # Process frame with all overlays
            frame = self.frame_processor.process_frame(
                frame=frame,
                frame_rgb=frame_rgb,
                face_detected=face_detected,
                ear=ear,
                left_pts=left_pts,
                right_pts=right_pts,
                alarm_on=alarm_on,
                accel_event_text=accel_event_text,
                accel_event_time=accel_event_time,
                report_status=report_status
            )
            
            # ============================
            # 7) Display and keyboard input
            # ============================
            key = self.frame_processor.display_frame(frame)

            # Handle UI response and keyboard input for report system
            # Check UI response first (touch screen), then keyboard
            # Only process response if status is ALERT (not REPORTING - report already sent)
            ui_response = self._check_ui_response()
            if ui_response is not None:
                if report_status['status'] == 'ALERT':
                    # Get current threshold from config (supports runtime updates)
                    current_threshold = self.config_manager.get('EAR_THRESHOLD', 0.2)
                    
                    report_status = self.report_manager.update(
                        face_detected=face_detected,
                        ear=ear if face_detected else None,
                        ear_threshold=current_threshold,
                        keyboard_input=ui_response
                    )
                    if report_status['status'] == 'NORMAL':
                        self.speaker.alarm_off()
                        print(f"[Report] User responded via UI. Report cancelled.")
                elif report_status['status'] == 'REPORTING':
                    # Report already sent, ignore response
                    print(f"[Report] Report already sent. User response ignored.")
            elif report_status['status'] == 'ALERT' and key != 255 and key != 0:
                # Any key pressed during alert cancels report
                keyboard_input = chr(key) if key != 255 and key != 0 else None
                if keyboard_input:
                    # Get current threshold from config (supports runtime updates)
                    current_threshold = self.config_manager.get('EAR_THRESHOLD', 0.2)
                    
                    report_status = self.report_manager.update(
                        face_detected=face_detected,
                        ear=ear if face_detected else None,
                        ear_threshold=current_threshold,
                        keyboard_input=keyboard_input
                    )
                    if report_status['status'] == 'NORMAL':
                        self.speaker.alarm_off()
                        print(f"[Report] User pressed '{keyboard_input}'. Report cancelled.")

            # Quit on 'q' key
            if key == ord("q"):
                break

        # end
        self.logger.log("program quit")
        self.camera.release()
        self.speaker.cleanup()
        # Only destroy windows if they were created
        if os.environ.get('SHOW_MONITOR_WINDOW', '').lower() in ('1', 'true', 'yes'):
            cv2.destroyAllWindows()
    
    def _check_ui_response(self):
        """
        Check if user responded via UI (touch screen).
        Reads user_response.json file created by JavaFX UI.
        
        Returns:
            str or None: User input if response file exists, None otherwise
        """
        import json
        
        # Try multiple paths (Raspberry Pi and development)
        paths = [
            PathManager.get_user_response_json_path(),
            os.path.join(project_root, "data", "user_response.json"),
            os.path.join(self.data_bridge.get_data_path(), "user_response.json")
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                        if response_data.get('responded', False):
                            # Delete the response file after reading
                            try:
                                os.remove(path)
                            except (OSError, PermissionError) as e:
                                # File may be locked or already deleted, ignore
                                pass
                            return "UI_RESPONSE"  # Return a marker string
                except Exception as e:
                    # File exists but couldn't read it, continue to next path
                    continue
        
        return None
    
    def _check_stop_speaker_request(self):
        """
        Check if UI requested to stop the speaker.
        Reads stop_speaker.json file created by JavaFX UI.
        
        Returns:
            bool: True if stop request exists, False otherwise
        """
        import json
        
        # Try multiple paths (Raspberry Pi and development)
        paths = [
            PathManager.get_stop_speaker_json_path(),
            os.path.join(project_root, "data", "stop_speaker.json"),
            os.path.join(self.data_bridge.get_data_path(), "stop_speaker.json")
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        stop_data = json.load(f)
                        if stop_data.get('stop', False):
                            # Delete the stop request file after reading
                            try:
                                os.remove(path)
                            except (OSError, PermissionError) as e:
                                # File may be locked or already deleted, ignore
                                pass
                            return True
                except Exception as e:
                    # File exists but couldn't read it, continue to next path
                    continue
        
        return False

