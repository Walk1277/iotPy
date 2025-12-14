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

class CameraManager:
    def __init__(self, index=0):
        self.index = index
        self.picam2 = None
        self.cap = None

    def initialize(self):
        # Try USB webcam first (works on both Linux and Raspberry Pi)
        # Try multiple indices if default fails
        usb_cam_indices = [self.index]
        if self.index == 0:
            # Also try index 1 if index 0 fails
            usb_cam_indices = [0, 1]
        
        usb_cam_initialized = False
        for idx in usb_cam_indices:
            try:
                self.index = idx
                self._init_usb_cam()
                usb_cam_initialized = True
                print(f"[Camera] USB webcam initialized successfully at index {idx}.")
                break
            except Exception as e:
                print(f"[Camera] USB webcam init failed at index {idx}: {e}")
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                continue
        
        if not usb_cam_initialized:
            print("[Camera] All USB webcam indices failed, trying PiCamera2 fallback...")
            # Fallback to PiCamera2 if available (Raspberry Pi only)
            if IS_RPI:
                try:
                    self.picam2 = Picamera2()
                    self.picam2.preview_configuration.main.size = (CAM_WIDTH, CAM_HEIGHT)
                    self.picam2.preview_configuration.main.format = "RGB888"
                    self.picam2.preview_configuration.align()
                    self.picam2.configure("preview")
                    self.picam2.start()
                    print("[Camera] PiCamera2 initialized (fallback).")
                except Exception as e2:
                    print(f"[Camera] PiCamera2 init also failed: {e2}")
                    raise RuntimeError("No camera available (USB webcam and PiCamera2 both failed)")
            else:
                raise RuntimeError("USB webcam not available and PiCamera2 is not supported on this system")

    def _init_usb_cam(self):
        print(f"[Camera] Attempting to initialize USB webcam (index: {self.index})...")
        self.cap = cv2.VideoCapture(self.index)
        
        if self.cap is None:
            raise RuntimeError(f"Failed to create VideoCapture object for index {self.index}")
        
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            raise RuntimeError(f"USB webcam at index {self.index} is not available or cannot be opened")

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        
        # Verify the camera is still opened after setting properties
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            raise RuntimeError("USB webcam closed unexpectedly after setting properties")
        
        # Test reading a frame to ensure camera is working
        ret, test_frame = self.cap.read()
        if not ret or test_frame is None:
            self.cap.release()
            self.cap = None
            raise RuntimeError("USB webcam cannot read frames")
        
        print(f"[Camera] USB webcam initialized successfully (index: {self.index}).")

    def get_frames(self):
        """
        Get frames from camera (USB webcam or PiCamera2)
        Returns: (frame, frame_rgb) tuple
        """
        # Use PiCamera2 if available and initialized
        if IS_RPI and self.picam2 is not None:
            frame = self.picam2.capture_array()
            frame_rgb = self.picam2.capture_array()
            return frame, frame_rgb

        # Use USB webcam if available and initialized
        elif self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Could not read frame from USB webcam")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame, frame_rgb
        
        else:
            raise RuntimeError("No camera available (neither USB webcam nor PiCamera2 is initialized)")

    def release(self):
        if IS_RPI and self.picam2:
            self.picam2.stop()
            print("[Camera] PiCamera2 stopped.")
        if self.cap:
            self.cap.release()

