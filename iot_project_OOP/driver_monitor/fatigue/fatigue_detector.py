# fatigue_detector.py
import mediapipe as mp
import cv2
import sys
import os
import importlib

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import LEFT_EYE_IDXS, RIGHT_EYE_IDXS, CONSEC_FRAMES

# Try both relative and absolute imports for Raspberry Pi compatibility
try:
    from ..config.config_manager import ConfigManager
except ImportError:
    from driver_monitor.config.config_manager import ConfigManager

mp_facemesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
denormalize_coordinates = mp_drawing._normalized_to_pixel_coordinates

class FatigueDetector:
    def __init__(self):
        self.counter = 0
        self.face_mesh = mp_facemesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        # Load EAR_THRESHOLD dynamically
        self._load_threshold()
    
    def _load_threshold(self):
        """Load EAR_THRESHOLD from config.py dynamically."""
        try:
            config_manager = ConfigManager()
            self.ear_threshold = config_manager.get('EAR_THRESHOLD', 0.4)
        except Exception as e:
            # Fallback to default if reload fails
            print(f"[FatigueDetector] Warning: Could not load config: {e}")
            self.ear_threshold = 0.4  # Default fallback

    def _distance(self, p1, p2):
        return ((p1[0]-p2[0]) ** 2 + (p1[1]-p2[1]) ** 2) ** 0.5

    def _get_ear(self, landmarks, idxs, w, h):
        try:
            pts = []
            for i in idxs:
                lm = landmarks[i]
                xy = denormalize_coordinates(lm.x, lm.y, w, h)
                pts.append(xy)

            P2_P6 = self._distance(pts[1], pts[5])
            P3_P5 = self._distance(pts[2], pts[4])
            P1_P4 = self._distance(pts[0], pts[3])
            ear = (P2_P6 + P3_P5) / (2 * P1_P4)
            return ear, pts
        except (IndexError, TypeError, AttributeError) as e:
            # Handle cases where landmarks are invalid or missing
            return 0.0, None

    def analyze(self, frame_rgb, imgW, imgH):
        results = self.face_mesh.process(frame_rgb)
        if not results.multi_face_landmarks:
            return False, None, None, False   # no-face

        lm = results.multi_face_landmarks[0].landmark

        left_ear, left_pts = self._get_ear(lm, LEFT_EYE_IDXS, imgW, imgH)
        right_ear, right_pts = self._get_ear(lm, RIGHT_EYE_IDXS, imgW, imgH)
        ear = (left_ear + right_ear) / 2

        # Reload threshold from config (to support runtime updates)
        self._load_threshold()
        
        alarm = False
        if ear < self.ear_threshold:
            self.counter += 1
            if self.counter >= CONSEC_FRAMES:
                alarm = True
        else:
            self.counter = 0

        return True, ear, (left_pts, right_pts), alarm

