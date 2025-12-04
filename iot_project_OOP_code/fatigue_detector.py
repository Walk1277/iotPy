# fatigue_detector.py
import mediapipe as mp
import cv2
from config import LEFT_EYE_IDXS, RIGHT_EYE_IDXS, EAR_THRESHOLD, CONSEC_FRAMES

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
        except:
            return 0.0, None

    def analyze(self, frame_rgb, imgW, imgH):
        results = self.face_mesh.process(frame_rgb)
        if not results.multi_face_landmarks:
            return False, None, None, False   # no-face

        lm = results.multi_face_landmarks[0].landmark

        left_ear, left_pts = self._get_ear(lm, LEFT_EYE_IDXS, imgW, imgH)
        right_ear, right_pts = self._get_ear(lm, RIGHT_EYE_IDXS, imgW, imgH)
        ear = (left_ear + right_ear) / 2

        alarm = False
        if ear < EAR_THRESHOLD:
            self.counter += 1
            if self.counter >= CONSEC_FRAMES:
                alarm = True
        else:
            self.counter = 0

        return True, ear, (left_pts, right_pts), alarm

