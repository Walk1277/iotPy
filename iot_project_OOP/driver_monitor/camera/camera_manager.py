# camera_manager.py
import cv2
import sys
import os

# 프로젝트 루트를 Python path에 추가 (라즈베리파이 호환성)
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
            except Exception as e:
                print(f"[Camera] PiCamera2 init failed: {e}")
                self._init_usb_cam()
        else:
            self._init_usb_cam()

    def _init_usb_cam(self):
        print("[Camera] Using USB webcam.")
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            raise RuntimeError("Webcam not available")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        print("[Camera] USB webcam initialized.")

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
                raise RuntimeError("Could not read frame")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame, frame_rgb

    def release(self):
        if IS_RPI and self.picam2:
            self.picam2.stop()
            print("[Camera] PiCamera2 stopped.")
        if self.cap:
            self.cap.release()

