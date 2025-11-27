# line 18: 임계값, 잠 유지 시간 설정 || line 176: 잠 인식 했을 때의 동작 추가.
import typer
import cv2
import numpy as np
import mediapipe as mp

# MediaPipe Face Mesh 및 드로잉 유틸리티 초기화
mp_facemesh = mp.solutions.face_mesh
mp_drawing  = mp.solutions.drawing_utils
# 랜드마크 좌표를 픽셀 좌표로 변환하는 함수
denormalize_coordinates = mp_drawing._normalized_to_pixel_coordinates

# --- 핵심 랜드마크 인덱스 (사용자 코드에서 가져옴) ---
# The chosen 12 points for EAR calculation: P1, P2, P3, P4, P5, P6
chosen_left_eye_idxs  = [362, 385, 387, 263, 373, 380]
chosen_right_eye_idxs = [33,  160, 158, 133, 153, 144]

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# --- 졸음 감지 임계값 및 상태 변수 ---
EAR_THRESHOLD = 0.20  # 눈을 감았다고 판단하는 EAR 임계값
# 30fps = 1초
CONSEC_FRAMES = 90    # 눈을 감은 상태가 지속되어야 하는 최소 프레임 수
# 초기 상태 변수는 process_webcam 함수 내에서 관리됩니다.

app = typer.Typer()

def distance(point_1, point_2):
    """Calculate l2-norm between two points"""
    dist = sum([(i - j) ** 2 for i, j in zip(point_1, point_2)]) ** 0.5
    return dist

def get_ear(landmarks, refer_idxs, frame_width, frame_height):
    """
    Calculate Eye Aspect Ratio for one eye.
    """
    try:
        coords_points = []
        for i in refer_idxs:
            lm = landmarks[i]
            # 픽셀 좌표로 변환
            coord = denormalize_coordinates(lm.x, lm.y,
                                            frame_width, frame_height)
            coords_points.append(coord)

        # Eye landmark (x, y)-coordinates
        P2_P6 = distance(coords_points[1], coords_points[5])
        P3_P5 = distance(coords_points[2], coords_points[4])
        P1_P4 = distance(coords_points[0], coords_points[3]) # 수평 거리

        # Compute the eye aspect ratio: (Vertical distances sum) / (2 * Horizontal distance)
        ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)

    except:
        ear = 0.0
        coords_points = None

    return ear, coords_points

def calculate_avg_ear(landmarks, left_eye_idxs, right_eye_idxs, image_w, image_h):
    """Calculate average Eye aspect ratio for both eyes"""

    left_ear, left_lm_coordinates = get_ear(
        landmarks,
        left_eye_idxs,
        image_w,
        image_h
    )
    right_ear, right_lm_coordinates = get_ear(
        landmarks,
        right_eye_idxs,
        image_w,
        image_h
    )
    Avg_EAR = (left_ear + right_ear) / 2.0

    return Avg_EAR, (left_lm_coordinates, right_lm_coordinates)


def plot_eye_landmarks(frame, left_lm_coordinates,
                       right_lm_coordinates, color
                       ):
    """프레임에 눈 랜드마크를 그립니다."""
    for lm_coordinates in [left_lm_coordinates, right_lm_coordinates]:
        if lm_coordinates:
            for coord in lm_coordinates:
                # 점을 그립니다.
                cv2.circle(frame, coord, 2, color, -1)
    return frame

def plot_text(image, text, origin,
              color, font=cv2.FONT_HERSHEY_SIMPLEX,
              fntScale=0.8, thickness=2
              ):
    """프레임에 텍스트를 그립니다."""
    image = cv2.putText(image, text, origin, font, fntScale, color, thickness)
    return image


def process_webcam(webcam_index=0):
    """
    웹캠 영상을 읽어 MediaPipe Face Mesh로 실시간 졸음 감지를 수행합니다.
    """
    cap = cv2.VideoCapture(webcam_index)

    if not cap.isOpened():
        print(f"Error: 웹캠(Index {webcam_index})을 열 수 없습니다.")
        return

    # 웹캠의 해상도 가져오기 (EAR 계산에 필요)
    imgW = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    imgH = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # --- 상태 변수 초기화 ---
    counter = 0      # 눈 감은 상태 지속 프레임 카운터
    alarm_on = False # 경고 상태

    # FaceMesh 초기화
    # refine_landmarks=True를 사용하여 눈 주변 랜드마크의 정확도를 높입니다.
    face_mesh = mp_facemesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    print(f"웹캠(Index {webcam_index}) 실시간 졸음 감지 실행 중... 'q'를 누르면 종료됩니다.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다. 종료합니다.")
            break

        # MediaPipe는 RGB 이미지를 필요로 합니다.
        # cv2.flip(frame, 1) # 웹캠 미러링이 필요할 경우 주석 해제
        frame.flags.writeable = False
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # FaceMesh 추론
        results = face_mesh.process(frame_rgb)

        frame.flags.writeable = True

        # 탐지 결과가 있을 경우
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = face_landmarks.landmark

            # EAR 계산 및 랜드마크 좌표 가져오기
            EAR, (left_lm_coordinates, right_lm_coordinates) = calculate_avg_ear(
                landmarks,
                chosen_left_eye_idxs,
                chosen_right_eye_idxs,
                imgW,
                imgH
            )

            # 1. 졸음 감지 로직
            if EAR < EAR_THRESHOLD:
                counter += 1
                if counter >= CONSEC_FRAMES:
                    alarm_on = True
            else:
                counter = 0
                alarm_on = False

            # 2. 주석 달기 (Annotation)

            # EAR 값 표시
            plot_text(frame, f"EAR: {EAR:.2f}", (10, 30), (0, 255, 0))

            # 눈 랜드마크 표시
            lmk_color = (0, 255, 255) # 노란색
            plot_eye_landmarks(frame, left_lm_coordinates, right_lm_coordinates, lmk_color)

            # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # 3. 경고 메시지 표시
            if alarm_on:
                plot_text(frame, "!!! DO NOT SLEEP !!!", (10, 60), (0, 0, 255), fntScale=1.2, thickness=3)

        # 화면에 출력
        cv2.imshow("Real-time Drowsiness Detection (EAR)", frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()
    # FaceMesh 객체 해제
    face_mesh.close()
    print("프로그램이 종료되었습니다.")

@app.command()
def webcam(
        index: int = typer.Option(0, help="사용할 웹캠의 인덱스 번호 (기본값 0)"),
):
    typer.echo(f"웹캠 실시간 졸음 감지 시작 (Camera Index: {index})...")
    process_webcam(webcam_index=index)

if __name__ == "__main__":
    app()