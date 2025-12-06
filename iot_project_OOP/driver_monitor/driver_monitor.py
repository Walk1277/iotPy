# driver_monitor.py
import cv2
import datetime
import sys
import os

# 프로젝트 루트를 Python path에 추가 (라즈베리파이 호환성)
# main.py에서 이미 추가되었을 수 있지만, 직접 실행 시를 대비
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from driver_monitor.camera.camera_manager import CameraManager
from driver_monitor.camera.overlay_renderer import OverlayRenderer
from driver_monitor.fatigue.fatigue_detector import FatigueDetector
from driver_monitor.sensors.accelerometer_detector import AccelerometerDetector
from driver_monitor.sensors.speaker_controller import SpeakerController
from driver_monitor.logging_system.event_logger import EventLogger

from config import (
    IMPACT_CHECK_DELAY,
    ALERT_CONFIRM_DELAY
)

# visualization
from driver_monitor.visualization.daily_timeline import show_daily_timeline
from driver_monitor.visualization.weekly_stats import show_weekly_stats


class DriverMonitor:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index

        self.camera = CameraManager(cam_index)
        self.fatigue = FatigueDetector()
        self.accel = AccelerometerDetector()
        self.speaker = SpeakerController()
        self.overlay = OverlayRenderer()
        self.logger = EventLogger()

        self.running = True

    def initialize(self):
      
        self.camera.initialize()

        # ADXL345
        self.accel.initialize()

        # Speaker
        self.speaker.initialize()

        self.logger.log("Start program")

    def run(self):

        self.initialize()

        alarm_on = False
        prev_alarm_on = False

        # EAR
        # impac
        impact_check_mode = False
        impact_time = datetime.datetime.min
        alert_start_time = None

        # acc Text
        accel_event_text = ""
        accel_event_time = datetime.datetime.now()

        print("Use 'q', 'd', 'w', 'a', 's' key")

        while self.running:

            # =========================================
            # 1)
            # =========================================
            try:
                frame, frame_rgb = self.camera.get_frames()
            except:
                print("Camera read error. Stop.")
                break

            imgH, imgW = frame.shape[:2]

            # =========================================
            # 2)
            # =========================================
            face_detected, ear, (left_pts, right_pts), alarm_on = \
                self.fatigue.analyze(frame_rgb, imgW, imgH)

            prev = prev_alarm_on
            prev_alarm_on = alarm_on

            # =========================================
            # 3)
            # =========================================
            if alarm_on:
                if not prev:
                    self.logger.log("drowsiness")
                self.speaker.alarm_on()
            else:
                if prev:
                    self.speaker.alarm_off()

            # =========================================
            # 4)
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
            # 5)
            # =========================================
            accel_data = None
            event = None

            if self.accel.accel:
                accel_data, event = self.accel.read_accel()

                if event:
                    self.logger.log(event)
                    accel_event_text = self.accel.last_event_text
                    accel_event_time = self.accel.last_event_time

                    impact_check_mode = True
                    impact_time = self.accel.impact_time
                    alert_start_time = self.accel.alert_start_time

                # 
                if (datetime.datetime.now() - accel_event_time).total_seconds() < 3:
                    frame = self.overlay.put_text(
                        frame,
                        accel_event_text,
                        (10, imgH - 30),
                        (0, 255, 255),
                        scale=0.7
                    )

            # =====================================================
            # 6) 
            # =====================================================
            if impact_check_mode:
                is_unresponsive = (self.fatigue.counter >= 1) or (not face_detected)

       
                if not is_unresponsive:
                    print("[INFO] pass")
                    impact_check_mode = False
                    alert_start_time = None
                else:
                   
                    if (datetime.datetime.now() - impact_time).total_seconds() >= IMPACT_CHECK_DELAY and alert_start_time is None:
                        print("[ALERT] no response 10s. open alert.")
                        cv2.putText(
                            frame,
                            "!!! checking user response !!!",
                            (50, imgH // 2 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, (0, 0, 255), 3
                        )
                        alert_start_time = datetime.datetime.now()

                    elif alert_start_time is not None and (datetime.datetime.now() - alert_start_time).total_seconds() >= ALERT_CONFIRM_DELAY:
                        print("no response 20s")
                        cv2.putText(
                            frame,
                            "!!! (EMERGENCY) !!!",
                            (10, imgH // 2 + 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 0, 255), 5
                        )
                        cv2.imshow("Drowsiness Monitor", frame)
                        cv2.waitKey(0)
                        break

                    elif alert_start_time is not None:
                        remaining = ALERT_CONFIRM_DELAY - (datetime.datetime.now() - alert_start_time).total_seconds()
                        frame = self.overlay.put_text(
                            frame,
                            f"waiting for response: {remaining:.1f}s",
                            (10, imgH - 60),
                            (0, 165, 255),
                            scale=1.0
                        )
                        cv2.putText(
                            frame,
                            "!!! waiting for response 10s !!!",
                            (50, imgH // 2 + 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, (0, 0, 255), 3
                        )

            # ============================
            # 7)
            # ============================
            cv2.imshow("Drowsiness Monitor", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("d"):
                df = self.logger.load_log()
                show_daily_timeline(df)
            elif key == ord("w"):
                df = self.logger.load_log()
                show_weekly_stats(df)
            elif key == ord("a"):
                self.logger.log("sudden acceleration")
            elif key == ord("s"):
                self.logger.log("sudden stop")

        # end
        self.logger.log("program quit")
        self.camera.release()
        self.speaker.cleanup()
        cv2.destroyAllWindows()

