# driver_monitor.py
import cv2
import datetime
import numpy as np
import time

from camera_manager import CameraManager
from fatigue_detector import FatigueDetector
from accelerometer_detector import AccelerometerDetector
from speaker_controller import SpeakerController
from overlay_renderer import OverlayRenderer
from event_logger import EventLogger

from config import (
    IMPACT_CHECK_DELAY,
    ALERT_CONFIRM_DELAY
)

# 시각화
from visualization.daily_timeline import show_daily_timeline
from visualization.weekly_stats import show_weekly_stats


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
        # 카메라 초기화
        self.camera.initialize()

        # ADXL345 초기화 (RPi에서만)
        self.accel.initialize()

        # Speaker 초기화 (RPi에서만)
        self.speaker.initialize()

        # 시작 로그
        self.logger.log("Start program")

    def impact_response_check_block(self, frame, imgH, face_detected, ear_counter,
                                    impact_mode, impact_time, alert_start):
        """
        ⚠ 원본 코드의 impact_check_mode 블록 구성과 동일하게 유지
        """

        current_time = datetime.datetime.now()

        # 1) is_unresponsive 판별
        is_unresponsive = (ear_counter >= 1) or (not face_detected)

        if not is_unresponsive:
            print("[INFO] checked response after impact.")
            return False, None   # impact_mode False, alert_start None

        # 2) impact_time 이후 IMPACT_CHECK_DELAY 초 경과 (alert_start 없음)
        if (current_time - impact_time).total_seconds() >= IMPACT_CHECK_DELAY and alert_start is None:
            print("[ALERT] no response 10s. open alert.")
            cv2.putText(
                frame,
                "!!! checking user response !!!",
                (50, imgH // 2 + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )
            return True, current_time   # alert_start = current_time

        # 3) alert_start가 존재하고 ALERT_CONFIRM_DELAY초 경과
        if alert_start is not None and (current_time - alert_start).total_seconds() >= ALERT_CONFIRM_DELAY:
            print("no response 20s")
            cv2.putText(
                frame,
                "!!! (EMERGENCY) !!!",
                (10, imgH // 2 + 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 0, 255),
                5
            )
            cv2.imshow("Drowsiness Monitor", frame)
            cv2.waitKey(0)
            return False, None   # impact_mode False (break trigger)

        # 4) alert_start가 존재하여, 아직 20초는 안 된 상태
        if alert_start is not None:
            remaining = ALERT_CONFIRM_DELAY - (current_time - alert_start).total_seconds()
            self.overlay.put_text(frame, f"waiting for response: {remaining:.1f}s",
                                  (10, imgH - 60), (0, 165, 255), scale=1.0)
            cv2.putText(
                frame,
                "!!! waiting for response !!!",
                (50, imgH // 2 + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )
            return True, alert_start

        return True, alert_start

    def run(self):

        self.initialize()

        # 상태 변수 (원본 코드 그대로 유지)
        alarm_on = False
        prev_alarm_on = False

        # EAR 카운트는 fatigue_detector 내부에서 관리됨
        # impact 모드용 변수
        impact_check_mode = False
        impact_time = datetime.datetime.min
        alert_start_time = None

        # 가속도 Text
        accel_event_text = ""
        accel_event_time = datetime.datetime.now()

        print("Use 'q', 'd', 'w', 'a', 's' key")

        while self.running:

            # =========================================
            # 1) 카메라 입력 (원본처럼 2회 캡처)
            # =========================================
            try:
                frame, frame_rgb = self.camera.get_frames()
            except:
                print("Camera read error. Stop.")
                break

            imgH, imgW = frame.shape[:2]

            # =========================================
            # 2) FACE + EAR 분석
            # =========================================
            face_detected, ear, (left_pts, right_pts), alarm_on = \
                self.fatigue.analyze(frame_rgb, imgW, imgH)

            prev = prev_alarm_on
            prev_alarm_on = alarm_on

            # =========================================
            # 3) 졸음 알람
            # =========================================
            if alarm_on:
                if not prev:
                    self.logger.log("drowsiness")
                self.speaker.alarm_on()
            else:
                if prev:
                    self.speaker.alarm_off()

            # =========================================
            # 4) EAR 출력 + 랜드마크 출력
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
            # 5) 가속도 센서 처리
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

                # 최근 이벤트 3초 동안 텍스트 표시
                if (datetime.datetime.now() - accel_event_time).total_seconds() < 3:
                    frame = self.overlay.put_text(
                        frame,
                        accel_event_text,
                        (10, imgH - 30),
                        (0, 255, 255),
                        scale=0.7
                    )

            # =====================================================
            # 6) 원본 코드: impact_check_mode 블록 두 번 실행되는 구조
            # =====================================================
            if impact_check_mode:
                is_unresponsive = (self.fatigue.counter >= 1) or (not face_detected)

                # (1) 정상 반응 → 종료
                if not is_unresponsive:
                    print("[INFO] pass")
                    impact_check_mode = False
                    alert_start_time = None
                else:
                    # 원본과 동일한 구조: delay 체크 후 alert 발생
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

            # ========== impact_check_mode 두 번째 블록 (원본 코드 그대로) ==========
            if impact_check_mode:
                is_unresponsive = (self.fatigue.counter >= 1) or (not face_detected)

                if not is_unresponsive:
                    print("[INFO] checked response after impact.")
                    impact_check_mode = False
                    alert_start_time = None

                elif (datetime.datetime.now() - impact_time).total_seconds() >= IMPACT_CHECK_DELAY and alert_start_time is None:
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
                        "!!! waiting for response !!!",
                        (50, imgH // 2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 0, 255), 3
                    )

            # ============================
            # 7) 키 입력 처리
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

        # 종료 처리
        self.logger.log("program quit")
        self.camera.release()
        self.speaker.cleanup()
        cv2.destroyAllWindows()

