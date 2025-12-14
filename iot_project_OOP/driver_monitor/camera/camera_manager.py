# camera_manager.py
import cv2
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from picamera2 import Picamera2
    import RPi.GPIO as GPIO
    IS_RPI = True
except ImportError:
    IS_RPI = False

from config import CAM_WIDTH, CAM_HEIGHT

# Try both relative and absolute imports for Raspberry Pi compatibility
try:
    from ..utils.error_handler import ErrorHandler, ErrorType, ErrorSeverity
except ImportError:
    from driver_monitor.utils.error_handler import ErrorHandler, ErrorType, ErrorSeverity

class CameraManager:
    def __init__(self, index=0):
        self.index = index
        self.picam2 = None
        self.cap = None

    def initialize(self):
        if IS_RPI:
            try:
                self.picam2 = Picamera2()
                self.picam2.preview_configuration.main.size = (CAM_WIDTH, CAM_HEIGHT)
                self.picam2.preview_configuration.main.format = "RGB888"
                self.picam2.preview_configuration.align()
                self.picam2.configure("preview")
                self.picam2.start()
                print("[Camera] PiCamera2 initialized.")
                # PiCamera2 성공 시 index는 무시됨 (정상 동작)
            except Exception as e:
                ErrorHandler.handle_camera_error(
                    error=e,
                    context="PiCamera2 initialization",
                    logger=None
                )
                print("[Camera] Falling back to USB webcam...")
                # 라즈베리파이에서 USB 웹캠 폴백 시 인덱스 0을 기본으로 사용
                # (라즈베리파이에서는 USB 웹캠이 보통 인덱스 0)
                fallback_index = 0 if self.index != 0 else self.index
                self._init_usb_cam_with_index(fallback_index)
        else:
            self._init_usb_cam()

    def _init_usb_cam(self, index=None):
        """USB 웹캠 초기화 (기본값: self.index 사용)"""
        if index is None:
            index = self.index
        self._init_usb_cam_with_index(index)
    
    def _init_usb_cam_with_index(self, index):
        """지정된 인덱스로 USB 웹캠 초기화"""
        print(f"[Camera] Using USB webcam (index: {index}).")
        try:
            self.cap = cv2.VideoCapture(index)
            if not self.cap.isOpened():
                raise RuntimeError(f"Webcam not available at index {index}")

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
            print(f"[Camera] USB webcam initialized at index {index}.")
        except Exception as e:
            ErrorHandler.handle_camera_error(
                error=e,
                context="USB webcam initialization",
                logger=None,
                raise_after=True  # Re-raise as this is critical
            )

    def get_frames(self):
        """
        frame = picam2.capture_array()
        frame_rgb = picam2.capture_array()
        """
        if IS_RPI and self.picam2:
            frame = self.picam2.capture_array()
            frame_rgb = self.picam2.capture_array()
            return frame, frame_rgb

        else:
            ret, frame = self.cap.read()
            if not ret:
                error = RuntimeError("Could not read frame")
                ErrorHandler.handle_camera_error(
                    error=error,
                    context="Frame read",
                    logger=None,
                    raise_after=True
                )
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame, frame_rgb

    def release(self):
        if IS_RPI and self.picam2:
            self.picam2.stop()
            print("[Camera] PiCamera2 stopped.")
        if self.cap:
            self.cap.release()

