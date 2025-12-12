# driver_monitor.py
import cv2
import datetime
import sys
import os
import importlib

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

# Use absolute import for config at project root
# Note: EAR_THRESHOLD is now loaded dynamically in FatigueDetector
import config


class DriverMonitor:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index

        self.camera = CameraManager(cam_index)
        self.fatigue = FatigueDetector()
        self.accel = AccelerometerDetector()
        # Use GPS_ENABLED from config to determine if GPS should be simulated
        import importlib
        importlib.reload(config)
        gps_simulate = not config.GPS_ENABLED  # If GPS_ENABLED is False, use simulation
        self.gps = GPSManager(simulate=gps_simulate)
        self.speaker = SpeakerController()
        self.overlay = OverlayRenderer()
        self.logger = EventLogger()
        self.report_manager = ReportManager(logger=self.logger, gps_manager=self.gps)
        self.data_bridge = DataBridge()  # For UI communication

        self.running = True

    def initialize(self):
        """Initialize all components."""
        self.camera.initialize()

        # ADXL345
        self.accel.initialize()

        # GPS
        self.gps.initialize()

        # Speaker
        self.speaker.initialize()

        self.logger.log("Start program")

    def run(self):

        self.initialize()

        alarm_on = False
        prev_alarm_on = False

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
                print(f"Camera read error: {e}. Stop.")
                break

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
            
            # Update UI data bridge
            self.data_bridge.update_drowsiness_status(
                ear=ear if face_detected else None,
                face_detected=face_detected,
                alarm_on=alarm_on
            )

            # =========================================
            # 3) Drowsiness alarm handling
            # =========================================
            # Check if alarm state changed (from off to on)
            if alarm_on and not prev_alarm_on:
                # Alarm just turned on - log the drowsiness event
                self.logger.log("drowsiness")
                print(f"[DriverMonitor] Drowsiness detected and logged. EAR: {ear:.3f}")
            
            if alarm_on:
                self.speaker.alarm_on()
            else:
                if prev_alarm_on:
                    self.speaker.alarm_off()
            
            # Update prev_alarm_on AFTER checking state change
            prev_alarm_on = alarm_on

            # =========================================
            # 4) Frame overlay rendering
            # =========================================
            if face_detected:
                frame = self.overlay.put_text(
                    frame, f"EAR: {ear:.2f}", (10, 30), (0, 255, 0)
                )
                frame = self.overlay.draw_eye_landmarks(frame, left_pts, right_pts, (0, 255, 255))

                if alarm_on:
                    text = "X"
                    (tw, th), baseline = cv2.getTextSize(
                        text,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        3.0, 5
                    )
                    cx = (imgW - tw) // 2
                    cy = (imgH + th) // 2
                    cv2.putText(
                        frame, text, (cx, cy),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        3.0, (0, 0, 255), 5
                    )
            else:
                frame = self.overlay.put_text(frame, "no face", (10, 30), (0, 0, 255))

            # =========================================
            # 5) Accelerometer reading
            # =========================================
            accel_data = None
            event = None

            if self.accel.accel:
                accel_data, event = self.accel.read_accel()

                if event:
                    self.logger.log(event)
                    accel_event_text = self.accel.last_event_text
                    accel_event_time = self.accel.last_event_time

                    # Register impact for report system
                    impact_time = self.accel.impact_time
                    if impact_time:
                        self.report_manager.register_impact(impact_time)

                # Display accelerometer event text for 3 seconds
                if (datetime.datetime.now() - accel_event_time).total_seconds() < 3:
                    frame = self.overlay.put_text(
                        frame,
                        accel_event_text,
                        (10, imgH - 30),
                        (0, 255, 255),
                        scale=0.7
                    )

            # =========================================
            # 5.5) GPS reading
            # =========================================
            gps_data = self.gps.read_gps()
            gps_position = None
            if gps_data:
                gps_position = (gps_data[0], gps_data[1])  # (latitude, longitude)
            
            # =========================================
            # 5.6) Report system check (before keyboard input)
            # =========================================
            # Update report manager (initial check without keyboard input)
            # Pass EAR and threshold for eyes closed detection
            # Get current threshold from config (supports runtime updates)
            importlib.reload(config)
            current_threshold = config.EAR_THRESHOLD
            
            report_status = self.report_manager.update(
                face_detected=face_detected,
                ear=ear if face_detected else None,
                ear_threshold=current_threshold,
                keyboard_input=None
            )
            
            # Update system status for UI
            self.data_bridge.update_system_status(
                accel_data=accel_data,
                impact_detected=(event is not None),
                report_status=report_status,
                gps_position=gps_position,
                sensor_status=f"Camera: {'OK' if face_detected else 'Waiting'} / Accelerometer: {'OK' if self.accel.accel else 'Waiting'} / GPS: {'OK' if gps_position else 'Waiting'}"
            )
            
            # Update log summary periodically (every 60 frames ~ 2 seconds at 30fps)
            if hasattr(self, '_frame_count'):
                self._frame_count += 1
            else:
                self._frame_count = 0
            
            if self._frame_count % 60 == 0:
                self.data_bridge.update_log_summary()
            
            # Handle report system alerts
            if report_status['status'] == 'ALERT':
                # Show alert message
                message = report_status['message']
                remaining = report_status['remaining_time']
                
                # Display message on screen
                frame = self.overlay.put_text(
                        frame,
                    message,
                    (10, imgH // 2),
                    (0, 0, 255),
                    scale=1.2
                )
                    frame = self.overlay.put_text(
                        frame,
                    f"Time remaining: {remaining:.1f}s",
                    (10, imgH // 2 + 40),
                    (255, 0, 0),
                        scale=1.0
                    )
                
                # Play alert sound
                self.speaker.alarm_on()
                
            elif report_status['status'] == 'REPORTING':
                # Report process initiated
                frame = self.overlay.put_text(
                        frame,
                    "!!! REPORT PROCESS INITIATED !!!",
                    (10, imgH // 2),
                    (0, 0, 255),
                    scale=1.5
                    )
                self.speaker.alarm_on()
                # Stop alarm after showing message
                # (In real implementation, this would trigger actual report process)
                
            elif report_status['status'] == 'NORMAL':
                # Normal state - stop alarm if it was on
                if report_status.get('was_alerting', False):
                    self.speaker.alarm_off()

            # ============================
            # 6) Display and keyboard input
            # ============================
            # Only show window if SHOW_MONITOR_WINDOW environment variable is set
            # On Raspberry Pi, UI is shown separately, so we don't need this window
            if os.environ.get('SHOW_MONITOR_WINDOW', '').lower() in ('1', 'true', 'yes'):
            cv2.imshow("Drowsiness Monitor", frame)
            key = cv2.waitKey(1) & 0xFF
            else:
                # No window display - just process keyboard input from stdin if available
                key = 0

            # Handle keyboard input for report system and quit
            if report_status['status'] == 'ALERT' and key != 255 and key != 0:
                # Any key pressed during alert cancels report
                keyboard_input = chr(key) if key != 255 and key != 0 else None
                if keyboard_input:
                    # Get current threshold from config (supports runtime updates)
                    importlib.reload(config)
                    current_threshold = config.EAR_THRESHOLD
                    
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

