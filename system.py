import typer
import cv2
import numpy as np
import mediapipe as mp
import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import time

# Raspberry Pi GPIO
try:
    import RPi.GPIO as GPIO
    import board # ADXL345
    import busio # ADXL345
    import adafruit_adxl34x # ADXL345
    from picamera2 import Picamera2
    IS_RPI = True
except ImportError:
    IS_RPI = False
    print("could not find RPi.GPIO or ADXL345 librarie. sensor off.")

# --- GPIO and SPEAKER setting ---
if IS_RPI:
    SPEAKER_PIN = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPEAKER_PIN, GPIO.OUT)
    pwm = None

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
# MediaPipe Face Mesh and Drowing Utility initialization
mp_facemesh = mp.solutions.face_mesh
mp_drawing  = mp.solutions.drawing_utils
# randmark to pixel
denormalize_coordinates = mp_drawing._normalized_to_pixel_coordinates

# --- main randmark index ---
chosen_left_eye_idxs  = [362, 385, 387, 263, 373, 380]
chosen_right_eye_idxs = [33,  160, 158, 133, 153, 144]

# --- detect_drowsiness parameter ---
EAR_THRESHOLD = 0.20  # eye EAR parameter
CONSEC_FRAMES = 90    # frame

# --- acceleration sensor parameter (m/s^2) ---
ACCEL_THRESHOLD = 4.0

# --- time parameter ---
IMPACT_CHECK_DELAY = 10.0
ALERT_CONFIRM_DELAY = 10.0

# --- logging ---
LOG_FILE = "driving_events.log"

app = typer.Typer()

def log_event(event_type: str):
    # format : (YYYY MM DD HH MM SS)
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

    print("[ALARM] Speaker ON: Drowsiness Detected!")
    pwm_obj.start(50)

def stop_alarm_speaker(pwm_obj):
    if not IS_RPI or not pwm_obj:
        return

    print("[ALARM] Speaker OFF: Alertness Restored.")
    pwm_obj.stop()

def get_driving_data():
    try:
        df = pd.read_csv(LOG_FILE, sep='|', names=['Timestamp', 'EventType'],
                         skipinitialspace=True, header=None)

        df['Timestamp'] = df['Timestamp'].str.strip()

        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format="%Y %m %d %H %M %S")
        return df
    except FileNotFoundError:
        print("Error: could not find driving_events.log file.")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        print("Info: no data in log.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading or parsing log file: {e}")
        return pd.DataFrame()

def show_daily_timeline_visualization():
    df = get_driving_data()
    if df.empty:
        return

    today = datetime.datetime.now().date()
    df_today = df[df['Timestamp'].dt.date == today].copy()

    if df_today.empty:
        print(f"Info: no event in {today}.")
        return

    event_mapping = {
        "drowsiness": 4,
        "sudden acceleration": 3,
        "sudden stop": 2,
        "program start": 1.5,
        "program quit": 1
    }
    df_today['Y_Value'] = df_today['EventType'].map(event_mapping)

    # Matplotlib
    plt.ion()
    plt.figure(figsize=(12, 6))

    color_map = {
        4: 'red',
        3: 'orange',
        2: 'blue',
        1.5: 'cyan',
        1: 'green'
    }

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

    plt.yticks(list(event_mapping.values()), list(event_mapping.keys()))
    plt.xlabel("Time of Day")
    plt.title(f"{today} Daily Driver Event Timeline")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.legend(loc='lower right')

    import matplotlib.dates as mdates
    formatter = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(formatter)

    today_start = pd.to_datetime(f'{today} 00:00:00')
    today_end = pd.to_datetime(f'{today} 23:59:59')
    plt.xlim(today_start, today_end)

    plt.tight_layout()
    plt.show(block=False)
    print("Matplotlib Daily Driver Event Timeline")


def show_weekly_event_counts():
    df = get_driving_data()
    if df.empty:
        return

    key_events = ["drowsiness", "sudden acceleration", "sudden stop"]
    df_key = df[df['EventType'].isin(key_events)].copy()

    if df_key.empty:
        print("Info: no event.")
        return

    df_key['Date'] = df_key['Timestamp'].dt.date
    weekly_counts = df_key.groupby(['Date', 'EventType']).size().unstack(fill_value=0)

    today = datetime.date.today()
    date_range = pd.date_range(end=today, periods=7, freq='D').date
    weekly_data = weekly_counts.reindex(date_range, fill_value=0).iloc[-7:]

    for event in key_events:
        if event not in weekly_data.columns:
            weekly_data[event] = 0

    drowsiness = weekly_data['drowsiness']
    acceleration = weekly_data['sudden acceleration']
    braking = weekly_data['sudden stop']

    labels = [day.strftime('%m/%d') for day in weekly_data.index]
    x = np.arange(len(labels))
    width = 0.25

    plt.ion()
    plt.figure(figsize=(12, 6))

    rects1 = plt.bar(x - width, drowsiness, width, label='drowsiness', color='red')
    rects2 = plt.bar(x, acceleration, width, label='sudden acceleration', color='orange')
    rects3 = plt.bar(x + width, braking, width, label='sudden stop', color='blue')

    plt.ylabel('Count')
    plt.xlabel('Date')
    plt.title('Number of driving events in the past 7 days')
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show(block=False)
    print("Matplotlib Number of driving events in the past 7 days")


def distance(point_1, point_2):
    dist = sum([(i - j) ** 2 for i, j in zip(point_1, point_2)]) ** 0.5
    return dist

def get_ear(landmarks, refer_idxs, frame_width, frame_height):
    try:
        coords_points = []
        for i in refer_idxs:
            lm = landmarks[i]
            coord = denormalize_coordinates(lm.x, lm.y,
                                            frame_width, frame_height)
            coords_points.append(coord)

        # Eye landmark (x, y)-coordinates
        P2_P6 = distance(coords_points[1], coords_points[5])
        P3_P5 = distance(coords_points[2], coords_points[4])
        P1_P4 = distance(coords_points[0], coords_points[3])

        # Compute the eye aspect ratio: (Vertical distances sum) / (2 * Horizontal distance)
        ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)

    except:
        ear = 0.0
        coords_points = None

    return ear, coords_points

def calculate_avg_ear(landmarks, left_eye_idxs, right_eye_idxs, image_w, image_h):
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

    for lm_coordinates in [left_lm_coordinates, right_lm_coordinates]:
        if lm_coordinates:
            for coord in lm_coordinates:
                cv2.circle(frame, coord, 2, color, -1)
    return frame

def plot_text(image, text, origin,
              color, font=cv2.FONT_HERSHEY_SIMPLEX,
              fntScale=0.8, thickness=2
              ):
    image = cv2.putText(image, text, origin, font, fntScale, color, thickness)
    return image


def process_webcam(webcam_index=0):
    # Picamera2 initialization
    if IS_RPI:
        try:
            # [1:34:17.590186964] [5262]  INFO Camera camera_manager.cpp:330 libcamera v0.5.2+99-bfd68f78
            # Error: Picamera2 Initialization failed. PiCamera is not available. list index out of range
            picam2 = Picamera2()
            imgW = 1280
            imgH = 720

            picam2.preview_configuration.main.size = (1280, 720)
            picam2.preview_configuration.main.format = "RGB888"
            picam2.preview_configuration.align()
            picam2.configure("preview")
            picam2.start()

            print(f"PiCamera2 Initialization successful. resolution: {imgW}x{imgH}")

        except Exception as e:
            print(f"Error: Picamera2 Initialization failed. PiCamera is not available. {e}")
            return

    else:
        print("Info: Since this is not a PiCamera2 environment, use a general webcam.")
        cap = cv2.VideoCapture(webcam_index)
        if not cap.isOpened():
            print(f"Error: webcam(Index {webcam_index})is not available.")
            return
        imgW = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        imgH = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        picam2 = None
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        imgW = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        imgH = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


    # Start program
    log_event("Start program")

    accel = None
    if IS_RPI:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            accel = adafruit_adxl34x.ADXL345(i2c)
            print("ADXL345 Accelerometer Initialized.")
        except Exception as e:
            print(f"Error initializing ADXL345: {e}. Accelerometer features disabled.")
            accel = None

    pwm_speaker = None
    current_frequency = 440
    if IS_RPI:
        pwm_speaker = GPIO.PWM(SPEAKER_PIN, current_frequency)

    counter = 0
    alarm_on = False
    prev_alarm_on = False

    accel_event_text = ""
    accel_event_time = datetime.datetime.now()

    impact_check_mode = False
    impact_time = datetime.datetime.min
    alert_start_time = None

    face_mesh = mp_facemesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    print(f"Webcam/PiCamera real-time drowsiness detection running...")
    print("Use 'q', 'd', 'w', 'a', 's' key")

    while True:
        if IS_RPI and picam2:
            frame = picam2.capture_array()
        elif not IS_RPI and 'cap' in locals() and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Could not read frame. Terminating.")
                break
        else:
            break

        frame_rgb = picam2.capture_array()
        results = face_mesh.process(frame_rgb)

        prev_alarm_on = alarm_on
        alarm_on = False
        ear_low = False

        face_detected = bool(results.multi_face_landmarks)

        if results.multi_face_landmarks:

            face_landmarks = results.multi_face_landmarks[0]
            landmarks = face_landmarks.landmark
            EAR, (left_lm_coordinates, right_lm_coordinates) = calculate_avg_ear(
                landmarks, chosen_left_eye_idxs, chosen_right_eye_idxs, imgW, imgH
            )

            if EAR < EAR_THRESHOLD:
                counter += 1
                if counter >= CONSEC_FRAMES:
                    alarm_on = True
            else:
                counter = 0

            if alarm_on:
                if not prev_alarm_on:
                    log_event("drowsiness")
                start_alarm_speaker(pwm_speaker)
            elif prev_alarm_on:
                stop_alarm_speaker(pwm_speaker)

            plot_text(frame, f"EAR: {EAR:.2f}", (10, 30), (0, 255, 0))
            lmk_color = (0, 255, 255)
            plot_eye_landmarks(frame, left_lm_coordinates, right_lm_coordinates, lmk_color)

            if alarm_on:
                text = "X"
                (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 3.0, 5)
                center_x = (imgW - text_width) // 2
                center_y = (imgH + text_height) // 2
                cv2.putText(frame, text, (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 5, cv2.LINE_AA)
        else:
            plot_text(frame, "no face", (10, 30), (0, 0, 255))

        if accel:
            try:
                x, y, z = accel.acceleration

                if x > ACCEL_THRESHOLD:
                    log_event("sudden acceleration")
                    accel_event_text = f"detected sudden acceleration: {x:.2f} m/s^2"
                    accel_event_time = datetime.datetime.now()

                    impact_check_mode = True
                    impact_time = datetime.datetime.now()
                    alert_start_time = None

                elif x < -ACCEL_THRESHOLD:
                    log_event("sudden stop")
                    accel_event_text = f"detected sudden stop: {x:.2f} m/s^2"
                    accel_event_time = datetime.datetime.now()

                    impact_check_mode = True
                    impact_time = datetime.datetime.now()
                    alert_start_time = None

                if (datetime.datetime.now() - accel_event_time).total_seconds() < 3.0 and accel_event_text:
                    plot_text(frame, accel_event_text, (10, imgH - 30), (0, 255, 255), fntScale=0.7)

            except Exception as e:
                plot_text(frame, "sensor error!", (10, imgH - 30), (0, 0, 255))

        current_time = datetime.datetime.now()

        if impact_check_mode:
            is_unresponsive = (counter >= 1) or (not face_detected)

            if not is_unresponsive:
                print("[INFO] pass")
                impact_check_mode = False
                alert_start_time = None

            elif (current_time - impact_time).total_seconds() >= IMPACT_CHECK_DELAY and alert_start_time is None:
                print("[ALERT] no response 10s. open alert.")
                cv2.putText(frame, "!!! checking user response !!!", (50, imgH // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                alert_start_time = current_time

            elif alert_start_time is not None and (current_time - alert_start_time).total_seconds() >= ALERT_CONFIRM_DELAY:
                print("no response 20s")

                cv2.putText(frame, "!!! (EMERGENCY) !!!", (10, imgH // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
                cv2.imshow("Real-time Drowsiness Detection (EAR) - [D: Daily Timeline, W: Weekly Stats, Q: Quit]", frame)
                cv2.waitKey(0)
                current_time = datetime.datetime.now()

        if impact_check_mode:
            is_unresponsive = (counter >= 1) or (not face_detected)

            if not is_unresponsive:
                print("[INFO] checked response after impact.")
                impact_check_mode = False
                alert_start_time = None

            elif (current_time - impact_time).total_seconds() >= IMPACT_CHECK_DELAY and alert_start_time is None:
                print("[ALERT] no response 10s. open alert.")
                cv2.putText(frame, "!!! checking user response !!!", (50, imgH // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                alert_start_time = current_time

            elif alert_start_time is not None and (current_time - alert_start_time).total_seconds() >= ALERT_CONFIRM_DELAY:
                print("no response 20s")

                cv2.putText(frame, "!!! (EMERGENCY) !!!", (10, imgH // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
                cv2.imshow("Real-time Drowsiness Detection (EAR) - [D: Daily Timeline, W: Weekly Stats, Q: Quit]", frame)
                cv2.waitKey(0)
                break

            elif alert_start_time is not None:
                remaining_time = ALERT_CONFIRM_DELAY - (current_time - alert_start_time).total_seconds()
                plot_text(frame, f"waiting for response: {remaining_time:.1f}s", (10, imgH - 60), (0, 165, 255), fntScale=1.0)
                cv2.putText(frame, "!!! waiting for response 10s !!!", (50, imgH // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                break

            elif alert_start_time is not None:
                remaining_time = ALERT_CONFIRM_DELAY - (current_time - alert_start_time).total_seconds()
                plot_text(frame, f"waiting for response: {remaining_time:.1f}s", (10, imgH - 60), (0, 165, 255), fntScale=1.0)
                cv2.putText(frame, "!!! waiting for response !!!", (50, imgH // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        cv2.imshow("Real-time Drowsiness Detection (EAR) - [D: Daily Timeline, W: Weekly Stats, Q: Quit]", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("d"):
            show_daily_timeline_visualization()
        elif key == ord("w"):
            show_weekly_event_counts()
        elif key == ord("a"):
            log_event("sudden acceleration")
            plot_text(frame, "sudden acceleration logging (used key A)", (imgW-350, imgH-20), (0, 255, 255), fntScale=0.7)
        elif key == ord("s"):
            log_event("sudden stop")
            plot_text(frame, "sudden stop logging (used key S)", (imgW-350, imgH-20), (0, 255, 255), fntScale=0.7)

    log_event("program quit")

    if IS_RPI and picam2:
        picam2.stop()
        print("Picamera2 stopped.")
    elif 'cap' in locals() and cap.isOpened():
        cap.release()

    if IS_RPI:
        if pwm_speaker and getattr(pwm_speaker, 'started', False):
            pwm_speaker.stop()
        GPIO.cleanup()
        print("GPIO cleanup completed.")

    cv2.destroyAllWindows()
    face_mesh.close()
    plt.close('all')
    print("quit program.")

@app.command()
def webcam(
        index: int = typer.Option(0, help="Index number of the webcam/PiCamera to use"),
):
    typer.echo(f"Start real-time drowsiness detection (Camera Index: {index})...")
    process_webcam(webcam_index=index)

if __name__ == "__main__":
    plt.ion()
    app()
