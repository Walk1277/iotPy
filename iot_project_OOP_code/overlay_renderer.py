# overlay_renderer.py
import cv2

class OverlayRenderer:
    def put_text(self, frame, text, pos, color, scale=0.8, thick=2):
        return cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick)

    def draw_eye_landmarks(self, frame, pts_left, pts_right, color):
        for pts in [pts_left, pts_right]:
            if pts:
                for p in pts:
                    cv2.circle(frame, p, 2, color, -1)
        return frame

