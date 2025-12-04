# main.py
from camera.camera_manager import CameraManager
from camera.overlay_renderer import OverlayRenderer

from fatigue.fatigue_detector import FatigueDetector

from sensors.accelerometer_detector import AccelerometerDetector
from sensors.speaker_controller import SpeakerController

from logging_system.event_logger import log_event
from logging_system.log_parser import LogParser

from visualization.daily_timeline import show_daily_timeline
from visualization.weekly_stats import show_weekly_stats

from emergency.emergency_manager import EmergencyManager

emergency = EmergencyManager(
    impact_delay=10.0,
    alert_delay=20.0
)

# 센서 읽기 후
accel_x = accelerometer.read_x()

if accel_x > THRESHOLD or accel_x < -THRESHOLD:
    emergency.register_impact(accel_x)

# 매 프레임 업데이트
status = emergency.update(face_detected, ear_low)

if status == "CHECKING_RESPONSE":
    overlay.draw_checking_message()

elif isinstance(status, tuple) and status[0] == "WAITING_RESPONSE":
    remaining = status[1]
    overlay.draw_waiting_timer(remaining)

elif status == "EMERGENCY":
    overlay.draw_emergency_message()
    speaker.play_emergency_tone()



app = typer.Typer()

@app.command()
def start(index: int = typer.Option(0, help="Camera index")):
    monitor = DriverMonitor(cam_index=index)
    monitor.run()

if __name__ == "__main__":
    app()

