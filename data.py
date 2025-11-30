import typer
import cv2
import numpy as np
import mediapipe as mp
import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates # X축 시간 포맷팅을 위해 추가

# Raspberry Pi GPIO 사용을 위한 임포트 (PC 환경에서는 에러 방지를 위해 try-except 사용)
try:
    import RPi.GPIO as GPIO
    import board # ADXL345
    import busio # ADXL345
    import adafruit_adxl34x # ADXL345
    from picamera2 import Picamera2
    from libcamera import controls # PiCamera2의 AF/AE 제어용

    IS_RPI = True
except ImportError:
    IS_RPI = False
    print("RPi.GPIO 또는 ADXL345 라이브러리를 찾을 수 없습니다. 스피커/센서 기능은 비활성화됩니다.")

# --- GPIO 및 스피커 설정 ---
if IS_RPI:
    SPEAKER_PIN = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPEAKER_PIN, GPIO.OUT)
    # pwm 객체는 process_webcam에서 초기화하여 전역 변수 충돌을 피합니다.
    pwm = None

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
# MediaPipe Face Mesh 및 드로잉 유틸리티 초기화
mp_facemesh = mp.solutions.face_mesh
mp_drawing  = mp.solutions.drawing_utils
# 랜드마크 좌표를 픽셀 좌표로 변환하는 함수
denormalize_coordinates = mp_drawing._normalized_to_pixel_coordinates

# --- 핵심 랜드마크 인덱스 ---
chosen_left_eye_idxs  = [362, 385, 387, 263, 373, 380]
chosen_right_eye_idxs = [33,  160, 158, 133, 153, 144]

# --- 졸음 감지 임계값 및 상태 변수 ---
EAR_THRESHOLD = 0.20  # 눈을 감았다고 판단하는 EAR 임계값
CONSEC_FRAMES = 90    # 눈을 감은 상태가 지속되어야 하는 최소 프레임 수 (약 3초)
# --- 가속도 센서 임계값 (m/s^2) ---
# 일반적으로 급가속/급정거는 9.8m/s^2 (1G)의 0.4G ~ 0.5G 이상으로 설정
ACCEL_THRESHOLD = 4.0 # 전/후방 가속도(|X| 또는 |Y|) 감지 임계값.

# --- 로깅 설정 ---
LOG_FILE = "driving_events.log" # 이벤트 로그 파일 경로

app = typer.Typer()

def log_event(event_type: str):
    """
    이벤트 타입과 현재 시각(YYYY MM DD HH MM SS)을 파일에 기록합니다.
    """
    # 현재 시각을 요청된 형식(YYYY MM DD HH MM SS)으로 포맷
    timestamp = datetime.datetime.now().strftime("%Y %m %d %H %M %S")
    log_entry = f"{timestamp} | {event_type}\n"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(f"[LOG] {event_type} recorded.")
    except IOError as e:
        print(f"Error writing to log file {LOG_FILE}: {e}")

def start_alarm_speaker(pwm_obj):
    if not IS_RPI or not pwm_obj:
        return

    # 이미 켜져 있지 않다면 시작 (중복 실행 방지)
    if not getattr(pwm_obj, 'started', False):
        print("[ALARM] Speaker ON: Drowsiness Detected!")
        pwm_obj.start(50)  # 듀티 사이클 50%로 시작
        pwm_obj.started = True
    else:
        # 알람이 켜져 있는 상태에서 주파수 변경으로 경고 효과
        pwm_obj.ChangeFrequency(880 if pwm_obj.start_frequency == 440 else 440)
        pwm_obj.start_frequency = pwm_obj.get_frequency()

def stop_alarm_speaker(pwm_obj):
    if not IS_RPI or not pwm_obj:
        return

    if getattr(pwm_obj, 'started', False):
        print("[ALARM] Speaker OFF: Alertness Restored.")
        pwm_obj.stop()
        pwm_obj.started = False

def get_driving_data():
    """로그 파일을 읽어 데이터프레임으로 반환합니다."""
    try:
        df = pd.read_csv(LOG_FILE, sep='|', names=['Timestamp', 'EventType'],
                         skipinitialspace=True, header=None)

        df['Timestamp'] = df['Timestamp'].str.strip()

        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format="%Y %m %d %H %M %S")
        return df
    except FileNotFoundError:
        print("Error: 로그 파일(driving_events.log)을 찾을 수 없습니다.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print("Info: 로그 파일에 데이터가 없습니다.")
        return pd.DataFrame()
    except Exception as e:
        # 에러 메시지에 디버깅 정보를 추가하면 좋습니다.
        print(f"Error reading or parsing log file: {e}")
        return pd.DataFrame()


def show_daily_timeline_visualization():
    df = get_driving_data()
    if df.empty:
        return

    # 오늘 날짜의 이벤트만 필터링
    today = datetime.datetime.now().date()
    df_today = df[df['Timestamp'].dt.date == today].copy()

    if df_today.empty:
        print(f"Info: {today} 날짜의 이벤트가 없습니다.")
        return

    # 타임라인 Y축 설정을 위한 이벤트 타입 매핑
    event_mapping = {
        "졸음운전": 4,
        "급가속(가속도 센서로 확인)": 3,
        "급정거(가속도 센서로 확인)": 2,
        "프로그램 시작": 1.5,
        "프로그램 종료": 1
    }
    df_today['Y_Value'] = df_today['EventType'].map(event_mapping)

    # Matplotlib 설정
    plt.ion() # 대화형 모드 켜기: cv2.imshow를 막지 않기 위함
    plt.figure(figsize=(12, 6))

    # 이벤트 타입별 색상 설정
    color_map = {
        4: 'red', # 졸음
        3: 'orange', # 급가속
        2: 'blue', # 급정거
        1.5: 'cyan', # 시작
        1: 'green' # 종료
    }

    # 이벤트 타입별로 Scatter Plot 그리기
    for event_type, y_value in event_mapping.items():
        subset = df_today[df_today['EventType'] == event_type]
        if not subset.empty:
            plt.scatter(
                subset['Timestamp'],
                subset['Y_Value'],
                label=event_type,
                color=color_map[y_value],
                marker='o',
                s=100
            )

    # 그래프 세부 설정
    plt.yticks(list(event_mapping.values()), list(event_mapping.keys()))
    plt.xlabel("하루 시간 (Time of Day)")
    plt.title(f"{today} 일일 운전 이벤트 타임라인")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.legend(loc='lower right')

    # X축 포맷 설정 (시간만 표시)
    import matplotlib.dates as mdates
    formatter = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(formatter)

    # X축 범위를 오늘 하루 전체로 설정 (00:00:00부터 23:59:59까지)
    today_start = pd.to_datetime(f'{today} 00:00:00')
    today_end = pd.to_datetime(f'{today} 23:59:59')
    plt.xlim(today_start, today_end)

    plt.tight_layout()
    plt.show(block=False) # 비디오 루프를 막지 않고 새 창을 띄움
    print("Matplotlib 일일 타임라인 시각화 창을 띄웁니다.")


def show_weekly_event_counts():
    """
    로그 파일을 읽어 지난 7일간의 주요 이벤트(졸음, 급가속, 급정거) 횟수를 막대 그래프로 표시합니다.
    """
    df = get_driving_data()
    if df.empty:
        return

    # 1. 주요 이벤트만 필터링
    key_events = ["졸음운전", "급가속(가속도 센서로 확인)", "급정거(가속도 센서로 확인)"]
    df_key = df[df['EventType'].isin(key_events)].copy()

    if df_key.empty:
        print("Info: 분석할 졸음/급가속/급정거 이벤트가 없습니다.")
        return

    # 2. 날짜별로 그룹화 및 횟수 계산
    df_key['Date'] = df_key['Timestamp'].dt.date
    # 날짜별, 이벤트 유형별 횟수를 계산하고, 없는 값은 0으로 채웁니다.
    weekly_counts = df_key.groupby(['Date', 'EventType']).size().unstack(fill_value=0)

    # 3. 지난 7일 데이터 필터링
    # 현재 날짜로부터 7일 전까지의 날짜 범위를 생성
    today = datetime.date.today()
    date_range = pd.date_range(end=today, periods=7, freq='D').date

    # 지난 7일 데이터만 선택 (모든 날짜를 포함하도록 Reindex)
    weekly_data = weekly_counts.reindex(date_range, fill_value=0).iloc[-7:]

    # 4. 시각화 준비

    # 데이터가 없을 경우를 대비하여 컬럼 확인 및 추가
    for event in key_events:
        if event not in weekly_data.columns:
            weekly_data[event] = 0

    # 시각화할 데이터 (각 이벤트 유형별 카운트)
    drowsiness = weekly_data['졸음운전']
    acceleration = weekly_data['급가속(가속도 센서로 확인)']
    braking = weekly_data['급정거(가속도 센서로 확인)']

    labels = [day.strftime('%m/%d') for day in weekly_data.index]
    x = np.arange(len(labels))  # x축 레이블 위치
    width = 0.25  # 막대 폭

    # 5. Matplotlib 막대 그래프 생성
    plt.ion()
    plt.figure(figsize=(12, 6))

    rects1 = plt.bar(x - width, drowsiness, width, label='졸음운전', color='red')
    rects2 = plt.bar(x, acceleration, width, label='급가속', color='orange')
    rects3 = plt.bar(x + width, braking, width, label='급정거', color='blue')

    # 그래프 세부 설정
    plt.ylabel('발생 횟수 (Count)')
    plt.xlabel('날짜 (Date)')
    plt.title('지난 7일 운전 이벤트 발생 횟수')
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show(block=False)
    print("Matplotlib 주간 이벤트 횟수 시각화 창을 띄웁니다.")


def distance(point_1, point_2):
    """두 점 사이의 유클리드 거리를 계산합니다."""
    dist = sum([(i - j) ** 2 for i, j in zip(point_1, point_2)]) ** 0.5
    return dist

def get_ear(landmarks, refer_idxs, frame_width, frame_height):
    """
    한쪽 눈의 눈 종횡비(Eye Aspect Ratio, EAR)를 계산합니다.
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
    """양쪽 눈의 평균 EAR을 계산합니다."""

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

    # 💡 Picamera2 초기화 💡
    if IS_RPI:
        try:
            picam2 = Picamera2()

            # 카메라 설정: MediapPipe 성능을 위해 낮은 해상도와 BGR 포맷 지정
            # libcamera의 기본 프리뷰 설정 사용
            config = picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "BGR888"},
                # 카메라가 여러 개일 경우 Index를 지정할 수 있음: camera={"index": webcam_index}
            )
            picam2.configure(config)

            # 자동 노출 및 자동 화이트 밸런스를 끈 다음, 적절한 값으로 고정하여 일관성 유지
            picam2.set_controls({
                controls.AwbEnable: False, # 자동 화이트 밸런스 끄기
                controls.AeEnable: False, # 자동 노출 끄기
                controls.AnalogueGain: 1.0, # 아날로그 게인 고정 (선택 사항)
                controls.ExposureValue: 0.0, # 노출 보정 (선택 사항)
            })

            picam2.start()

            # 해상도 가져오기
            imgW, imgH = picam2.preview_configuration()["main"]["size"]
            print(f"PiCamera2 초기화 성공. 해상도: {imgW}x{imgH}")

        except Exception as e:
            print(f"Error: Picamera2 초기화 실패. PiCamera를 사용할 수 없습니다. {e}")
            return

    else:
        # PC 환경일 경우 기존 OpenCV 방식 사용 (경고 메시지 출력)
        print("Info: PiCamera2 환경이 아니므로, 범용 웹캠(cv2.VideoCapture)을 사용합니다.")
        cap = cv2.VideoCapture(webcam_index)
        if not cap.isOpened():
            print(f"Error: 웹캠(Index {webcam_index})을 열 수 없습니다.")
            return
        imgW = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        imgH = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        picam2 = None
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        imgW = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        imgH = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    # 프로그램 시작 이벤트 로깅
    log_event("프로그램 시작")

    # ADXL345 가속도 센서 초기화 (기존 코드 유지)
    accel = None
    if IS_RPI:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            accel = adafruit_adxl34x.ADXL345(i2c)
            print("ADXL345 Accelerometer Initialized.")
        except Exception as e:
            print(f"Error initializing ADXL345: {e}. Accelerometer features disabled.")
            accel = None

    # 스피커 PWM 초기화
    pwm_speaker = None
    if IS_RPI:
        pwm_speaker = GPIO.PWM(SPEAKER_PIN, 440)
        pwm_speaker.start_frequency = 440
        pwm_speaker.started = False

        # --- 상태 변수 초기화 ---
    counter = 0
    alarm_on = False
    prev_alarm_on = False

    # 가속도 감지 상태 표시용 변수
    accel_event_text = ""
    accel_event_time = datetime.datetime.now()

    # FaceMesh 초기화
    face_mesh = mp_facemesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    print(f"웹캠/PiCamera 실시간 졸음 감지 실행 중... 'q', 'd', 'w', 'a', 's' 키 사용 가능")

    while True:

        if IS_RPI and picam2:
            # 💡 Picamera2로 프레임 캡처 💡
            # OpenCV 처리용으로 BGR 포맷의 NumPy 배열을 반환
            frame = picam2.capture_array()
        elif not IS_RPI and 'cap' in locals() and cap.isOpened():
            # PC 환경일 경우 기존 OpenCV read 사용
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다. 종료합니다.")
                break
        else:
            # 카메라를 사용할 수 없는 경우 루프 탈출
            break

            # 프레임은 이미 BGR 포맷의 NumPy 배열이므로, 추가 변환 없이 사용
        # frame.flags.writeable = False (Picamera2에서는 불필요)

        # Mediapipe 처리를 위해 BGR -> RGB 변환 (MediaPipe는 RGB를 기대함)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(frame_rgb)

        # frame.flags.writeable = True (Picamera2에서는 불필요)

        # --- 졸음 감지 및 스피커 제어 로직 ---
        prev_alarm_on = alarm_on
        alarm_on = False

        if results.multi_face_landmarks:

            face_landmarks = results.multi_face_landmarks[0]
            landmarks = face_landmarks.landmark
            EAR, (left_lm_coordinates, right_lm_coordinates) = calculate_avg_ear(
                landmarks, chosen_left_eye_idxs, chosen_right_eye_idxs, imgW, imgH
            )

            # 1. 졸음 감지 로직
            if EAR < EAR_THRESHOLD:
                counter += 1
                if counter >= CONSEC_FRAMES:
                    alarm_on = True
            else:
                counter = 0

            # 2. 졸음 상태 변화에 따른 로깅 및 스피커 제어
            if alarm_on:
                if not prev_alarm_on:
                    log_event("졸음운전")
                start_alarm_speaker(pwm_speaker)
            elif prev_alarm_on:
                stop_alarm_speaker(pwm_speaker)

            # 3. EAR 값 및 랜드마크 표시
            plot_text(frame, f"EAR: {EAR:.2f}", (10, 30), (0, 255, 0))
            lmk_color = (0, 255, 255)
            plot_eye_landmarks(frame, left_lm_coordinates, right_lm_coordinates, lmk_color)

            # 4. 경고 메시지 표시 (X 출력)
            if alarm_on:
                text = "X"
                (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 3.0, 5)
                center_x = (imgW - text_width) // 2
                center_y = (imgH + text_height) // 2
                cv2.putText(frame, text, (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 5, cv2.LINE_AA)
        else:
            plot_text(frame, "얼굴을 찾을 수 없습니다.", (10, 30), (0, 0, 255))

        # 💡 ADXL345 가속도 센서 감지 로직 💡
        if accel:
            try:
                x, y, z = accel.acceleration

                # 급가속 감지
                if x > ACCEL_THRESHOLD:
                    log_event("급가속(가속도 센서로 확인)")
                    accel_event_text = f"급가속 감지: {x:.2f} m/s^2"
                    accel_event_time = datetime.datetime.now()
                # 급정거 감지
                elif x < -ACCEL_THRESHOLD:
                    log_event("급정거(가속도 센서로 확인)")
                    accel_event_text = f"급정거 감지: {x:.2f} m/s^2"
                    accel_event_time = datetime.datetime.now()

                # 3초 동안 가속도 이벤트 메시지 표시
                if (datetime.datetime.now() - accel_event_time).total_seconds() < 3.0 and accel_event_text:
                    plot_text(frame, accel_event_text, (10, imgH - 30), (0, 255, 255), fntScale=0.7)

            except Exception as e:
                plot_text(frame, "센서 오류!", (10, imgH - 30), (0, 0, 255))


        # 화면에 출력
        cv2.imshow("Real-time Drowsiness Detection (EAR) - [D: Daily Timeline, W: Weekly Stats, Q: Quit]", frame)

        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("d"):
            show_daily_timeline_visualization()
        elif key == ord("w"):
            show_weekly_event_counts()
        elif key == ord("a"):
            log_event("급가속(가속도 센서로 확인)")
            plot_text(frame, "급가속 로깅됨 (A키)! (센서 기능 분리)", (imgW-350, imgH-20), (0, 255, 255), fntScale=0.7)
        elif key == ord("s"):
            log_event("급정거(가속도 센서로 확인)")
            plot_text(frame, "급정거 로깅됨 (S키)! (센서 기능 분리)", (imgW-350, imgH-20), (0, 255, 255), fntScale=0.7)

    # 자원 해제
    log_event("프로그램 종료")

    # 💡 Picamera2 종료 💡
    if IS_RPI and picam2:
        picam2.stop()
        print("Picamera2 stopped.")
    elif 'cap' in locals() and cap.isOpened():
        cap.release()

    # 스피커 PWM 정지 및 GPIO 해제
    if IS_RPI:
        if pwm_speaker and getattr(pwm_speaker, 'started', False):
            pwm_speaker.stop()
        GPIO.cleanup()
        print("GPIO cleanup completed.")

    cv2.destroyAllWindows()
    face_mesh.close()
    plt.close('all')
    print("프로그램이 종료되었습니다.")

@app.command()
def webcam(
        index: int = typer.Option(0, help="사용할 웹캠/PiCamera의 인덱스 번호 (PiCamera2에서는 보통 무시됨)"),
):
    typer.echo(f"실시간 졸음 감지 시작 (Camera Index: {index})...")
    process_webcam(webcam_index=index)

if __name__ == "__main__":
    plt.ion()
    app()
