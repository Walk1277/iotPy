# frame_processor.py
"""
Frame processing pipeline.
Handles frame overlay rendering and visual feedback.
"""
import cv2
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try both relative and absolute imports for Raspberry Pi compatibility
try:
    from ..camera.overlay_renderer import OverlayRenderer
except ImportError:
    from driver_monitor.camera.overlay_renderer import OverlayRenderer


class FrameProcessor:
    """
    Handles frame processing and overlay rendering.
    """
    
    def __init__(self, overlay_renderer=None):
        """
        Args:
            overlay_renderer: OverlayRenderer instance (optional, will create if not provided)
        """
        self.overlay = overlay_renderer or OverlayRenderer()
        self.show_monitor_window = os.environ.get('SHOW_MONITOR_WINDOW', '').lower() in ('1', 'true', 'yes')
    
    def process_frame(self, frame, frame_rgb, face_detected, ear, left_pts, right_pts, 
                     alarm_on, accel_event_text, accel_event_time, report_status):
        """
        Process frame and add overlays.
        
        Args:
            frame: numpy array, BGR frame
            frame_rgb: numpy array, RGB frame
            face_detected: bool, Whether face is detected
            ear: float or None, Eye Aspect Ratio value
            left_pts: tuple or None, Left eye landmarks
            right_pts: tuple or None, Right eye landmarks
            alarm_on: bool, Whether drowsiness alarm is active
            accel_event_text: str, Accelerometer event text to display
            accel_event_time: datetime, Time when accelerometer event occurred
            report_status: dict, Report manager status with keys: status, message, remaining_time
            
        Returns:
            numpy array: Processed frame with overlays
        """
        imgH, imgW = frame.shape[:2]
        
        # Face and fatigue detection overlay
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
        
        # Accelerometer event overlay
        if accel_event_text:
            import datetime
            if (datetime.datetime.now() - accel_event_time).total_seconds() < 3:
                frame = self.overlay.put_text(
                    frame,
                    accel_event_text,
                    (10, imgH - 30),
                    (0, 255, 255),
                    scale=0.7
                )
        
        # Report system alert overlay (only if monitor window is shown)
        if self.show_monitor_window and report_status:
            status = report_status.get('status', 'NORMAL')
            if status == 'ALERT':
                message = report_status.get('message', '')
                remaining = report_status.get('remaining_time', 0.0)
                
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
            elif status == 'REPORTING':
                frame = self.overlay.put_text(
                    frame,
                    "!!! REPORT PROCESS INITIATED !!!",
                    (10, imgH // 2),
                    (0, 0, 255),
                    scale=1.5
                )
        
        return frame
    
    def display_frame(self, frame, window_name="Drowsiness Monitor"):
        """
        Display frame in window (only if SHOW_MONITOR_WINDOW is enabled).
        
        Args:
            frame: numpy array, Frame to display
            window_name: str, Window name
            
        Returns:
            int: Key code from waitKey (0 if window not shown)
        """
        if self.show_monitor_window:
            cv2.imshow(window_name, frame)
            return cv2.waitKey(1) & 0xFF
        else:
            return 0

