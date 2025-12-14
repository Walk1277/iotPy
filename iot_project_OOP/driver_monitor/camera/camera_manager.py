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
        self.max_reconnect_attempts = 5  # Maximum reconnection attempts
        self.connection_check_counter = 0
        self.connection_check_interval = 30  # Check every 30 frames (approximately 1 second at 30fps)

    def initialize(self):
<<<<<<< HEAD
        """
        Initialize camera with USB webcam priority.
        
        Priority order:
        1. USB webcam (always tried first)
        2. CSI camera (PiCamera2) - only on Raspberry Pi if USB webcam is not available at all
        
        Note: USB webcam is always preferred. CSI camera is only used as fallback
        if USB webcam cannot be detected/initialized.
        """
        # Always try USB webcam first (highest priority)
        print(f"[Camera] Attempting to initialize USB webcam (index: {self.index})...")
        usb_success = False
        
        try:
            self._init_usb_cam()
            usb_success = True
            print("[Camera] USB webcam initialized successfully (USB camera has priority).")
        except Exception as e:
            print(f"[Camera] USB webcam initialization failed: {e}")
            usb_success = False
        
        # Only try CSI camera if USB webcam completely failed AND we're on Raspberry Pi
        # This ensures USB webcam always has priority
        if not usb_success and IS_RPI:
            print("[Camera] USB webcam not available. Falling back to CSI camera (PiCamera2)...")
            try:
                print("[Camera] Attempting to initialize CSI camera (PiCamera2)...")
                self.picam2 = Picamera2()
                self.picam2.preview_configuration.main.size = (CAM_WIDTH, CAM_HEIGHT)
                self.picam2.preview_configuration.main.format = "RGB888"
                self.picam2.preview_configuration.align()
                self.picam2.configure("preview")
                self.picam2.start()
                print("[Camera] PiCamera2 (CSI camera) initialized as fallback.")
            except Exception as e:
                ErrorHandler.handle_camera_error(
                    error=e,
                    context="PiCamera2 initialization",
                    logger=None
                )
                print("[Camera] CSI camera initialization also failed.")
                raise RuntimeError("Both USB webcam and CSI camera initialization failed.")
        elif not usb_success:
            # Not on Raspberry Pi and USB failed - no CSI fallback available
            raise RuntimeError("USB webcam initialization failed and CSI camera is not available (not on Raspberry Pi).")

    def _init_usb_cam(self, index=None):
        """Initialize USB webcam (default: use self.index)"""
        if index is None:
            index = self.index
        self._init_usb_cam_with_index(index)
    
    def _init_usb_cam_with_index(self, index):
        """Initialize USB webcam with specified index"""
        print(f"[Camera] Using USB webcam (index: {index}).")
        try:
            # Release existing connection if present
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
            self.reconnect_attempts = 0  # Reset counter on successful reconnection
        except Exception as e:
            ErrorHandler.handle_camera_error(
                error=e,
                context="USB webcam initialization",
                logger=None,
                raise_after=True  # Re-raise as this is critical
            )
    
    def _reconnect_usb_cam(self):
        """
        Attempt to reconnect USB webcam
        
        Returns:
            bool: Whether reconnection succeeded
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"[Camera] Maximum reconnection attempts ({self.max_reconnect_attempts}) reached.")
            return False
        
        self.reconnect_attempts += 1
        print(f"[Camera] Attempting to reconnect USB webcam (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})...")
        
        try:
            # Release existing connection
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
            
            # Wait briefly (USB bus stabilization)
            import time
            time.sleep(0.5)
            
            # Attempt reconnection
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
            # CSI camera does not need reconnection (hardware connection)
=======
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
>>>>>>> do_the_right_thing
            frame = self.picam2.capture_array()
            frame_rgb = self.picam2.capture_array()
            return frame, frame_rgb

<<<<<<< HEAD
        else:
            # Periodically check connection status (before frame read)
            self.connection_check_counter += 1
            if self.connection_check_counter >= self.connection_check_interval:
                self.connection_check_counter = 0
                if self.cap is None or not self.cap.isOpened():
                    print("[Camera] Periodic check: USB camera disconnected. Reconnecting...")
                    if not self._reconnect_usb_cam():
                        print("[Camera] Reconnection failed during periodic check.")
            
            # Check USB webcam connection status
            if self.cap is None or not self.cap.isOpened():
                print("[Camera] USB camera not available. Attempting to reconnect...")
                if not self._reconnect_usb_cam():
                    raise RuntimeError("USB camera unavailable and reconnection failed")
            
            # Attempt to read frame
            ret, frame = self.cap.read()
            if not ret:
                # Frame read failed - attempt reconnection
                print("[Camera] Frame read failed. Attempting to reconnect...")
                if not self._reconnect_usb_cam():
                    raise RuntimeError("Could not read frame and reconnection failed")
                
                # Retry after reconnection
                ret, frame = self.cap.read()
                if not ret:
                    raise RuntimeError("Could not read frame after reconnection")
            
=======
        # Use USB webcam if available and initialized
        elif self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Could not read frame from USB webcam")
>>>>>>> do_the_right_thing
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

