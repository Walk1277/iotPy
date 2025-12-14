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
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5  # 최대 재연결 시도 횟수

    def initialize(self):
        """
        Initialize camera with priority: USB webcam first, then CSI camera (PiCamera2).
        
        Priority order:
        1. USB webcam (if available)
        2. CSI camera (PiCamera2) - only on Raspberry Pi if USB webcam fails
        """
        # Try USB webcam first
        usb_success = False
        try:
            print(f"[Camera] Attempting to initialize USB webcam (index: {self.index})...")
            self._init_usb_cam()
            usb_success = True
            print("[Camera] USB webcam initialized successfully.")
        except Exception as e:
            print(f"[Camera] USB webcam initialization failed: {e}")
            print("[Camera] Will try CSI camera (PiCamera2) if available...")
            usb_success = False
        
        # If USB webcam failed and we're on Raspberry Pi, try CSI camera
        if not usb_success and IS_RPI:
            try:
                print("[Camera] Attempting to initialize CSI camera (PiCamera2)...")
                self.picam2 = Picamera2()
                self.picam2.preview_configuration.main.size = (CAM_WIDTH, CAM_HEIGHT)
                self.picam2.preview_configuration.main.format = "RGB888"
                self.picam2.preview_configuration.align()
                self.picam2.configure("preview")
                self.picam2.start()
                print("[Camera] PiCamera2 (CSI camera) initialized successfully.")
            except Exception as e:
                ErrorHandler.handle_camera_error(
                    error=e,
                    context="PiCamera2 initialization",
                    logger=None
                )
                print("[Camera] CSI camera initialization also failed.")
                # Both USB and CSI failed, raise the error
                if not usb_success:
                    raise RuntimeError("Both USB webcam and CSI camera initialization failed.")
        elif not usb_success:
            # Not on Raspberry Pi and USB failed
            raise RuntimeError("USB webcam initialization failed and CSI camera is not available (not on Raspberry Pi).")

    def _init_usb_cam(self, index=None):
        """USB 웹캠 초기화 (기본값: self.index 사용)"""
        if index is None:
            index = self.index
        self._init_usb_cam_with_index(index)
    
    def _init_usb_cam_with_index(self, index):
        """지정된 인덱스로 USB 웹캠 초기화"""
        print(f"[Camera] Using USB webcam (index: {index}).")
        try:
            # 기존 연결이 있으면 해제
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
            
            self.cap = cv2.VideoCapture(index)
            if not self.cap.isOpened():
                raise RuntimeError(f"Webcam not available at index {index}")

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
            print(f"[Camera] USB webcam initialized at index {index}.")
            self.reconnect_attempts = 0  # 재연결 성공 시 카운터 리셋
        except Exception as e:
            ErrorHandler.handle_camera_error(
                error=e,
                context="USB webcam initialization",
                logger=None,
                raise_after=True  # Re-raise as this is critical
            )
    
    def _reconnect_usb_cam(self):
        """
        USB 웹캠 재연결 시도
        
        Returns:
            bool: 재연결 성공 여부
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"[Camera] Maximum reconnection attempts ({self.max_reconnect_attempts}) reached.")
            return False
        
        self.reconnect_attempts += 1
        print(f"[Camera] Attempting to reconnect USB webcam (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})...")
        
        try:
            # 기존 연결 해제
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
            
            # 잠시 대기 (USB 버스 안정화)
            import time
            time.sleep(0.5)
            
            # 재연결 시도
            self._init_usb_cam()
            print(f"[Camera] USB webcam reconnected successfully.")
            return True
        except Exception as e:
            print(f"[Camera] Reconnection attempt {self.reconnect_attempts} failed: {e}")
            return False

    def get_frames(self):
        """
        Get frames from camera (PiCamera2 or USB webcam).
        Automatically attempts to reconnect if USB webcam connection is lost.
        
        Returns:
            tuple: (frame, frame_rgb) - BGR frame and RGB frame
            
        Raises:
            RuntimeError: If camera is unavailable and reconnection fails
        """
        if IS_RPI and self.picam2:
            # CSI 카메라는 재연결 불필요 (하드웨어 연결)
            frame = self.picam2.capture_array()
            frame_rgb = self.picam2.capture_array()
            return frame, frame_rgb

        else:
            # USB 웹캠 연결 상태 확인
            if self.cap is None or not self.cap.isOpened():
                print("[Camera] USB camera not available. Attempting to reconnect...")
                if not self._reconnect_usb_cam():
                    raise RuntimeError("USB camera unavailable and reconnection failed")
            
            # 프레임 읽기 시도
            ret, frame = self.cap.read()
            if not ret:
                # 프레임 읽기 실패 - 재연결 시도
                print("[Camera] Frame read failed. Attempting to reconnect...")
                if not self._reconnect_usb_cam():
                    raise RuntimeError("Could not read frame and reconnection failed")
                
                # 재연결 후 다시 시도
                ret, frame = self.cap.read()
                if not ret:
                    raise RuntimeError("Could not read frame after reconnection")
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame, frame_rgb

    def release(self):
        if IS_RPI and self.picam2:
            self.picam2.stop()
            print("[Camera] PiCamera2 stopped.")
        if self.cap:
            self.cap.release()

