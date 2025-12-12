# data_bridge.py
"""
Data bridge module for UI communication.
Creates JSON files that the JavaFX UI can read to display real-time status.
"""
import json
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import LOG_FILE
import importlib


class DataBridge:
    """
    Bridge between Python backend and JavaFX UI.
    Writes real-time status data to JSON files that the UI can read.
    """
    
    def __init__(self, data_dir=None):
        """
        Args:
            data_dir: Directory to store JSON files (default: project_root/data)
                     On Raspberry Pi, can be set to /home/pi/iot/data for UI access
        """
        if data_dir is None:
            # Try Raspberry Pi default path first, then fallback to project root
            rpi_path = "/home/pi/iot/data"
            if os.path.exists("/home/pi") and os.path.isdir("/home/pi"):
                data_dir = rpi_path
            else:
                data_dir = os.path.join(project_root, "data")
        
        self.data_dir = data_dir
        self.drowsiness_json_path = os.path.join(data_dir, "drowsiness.json")
        self.status_json_path = os.path.join(data_dir, "status.json")
        self.log_summary_json_path = os.path.join(data_dir, "log_summary.json")
        
        # Create data directory if it doesn't exist
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"[DataBridge] Using data directory: {data_dir}")
        except PermissionError:
            # Fallback to project root if permission denied
            fallback_dir = os.path.join(project_root, "data")
            self.data_dir = fallback_dir
            self.drowsiness_json_path = os.path.join(fallback_dir, "drowsiness.json")
            self.status_json_path = os.path.join(fallback_dir, "status.json")
            self.log_summary_json_path = os.path.join(fallback_dir, "log_summary.json")
            os.makedirs(fallback_dir, exist_ok=True)
            print(f"[DataBridge] Permission denied, using fallback: {fallback_dir}")
    
    def update_drowsiness_status(self, ear=None, face_detected=False, alarm_on=False, state=None, alarm_duration=0.0, show_speaker_popup=False):
        """
        Update drowsiness status JSON file.
        
        Args:
            ear: float or None, Eye Aspect Ratio value
            face_detected: bool, Whether face is detected
            alarm_on: bool, Whether drowsiness alarm is active
            state: str or None, State string ("sleepy" or "normal")
            alarm_duration: float, Duration in seconds that alarm has been on
            show_speaker_popup: bool, Whether to show speaker stop popup in UI
        """
        if state is None:
            if alarm_on:
                state = "sleepy"
            elif face_detected:
                state = "normal"
            else:
                state = "no_face"
        
        # Load current threshold dynamically
        import config
        importlib.reload(config)
        current_threshold = config.EAR_THRESHOLD
        
        data = {
            "ear": ear if ear is not None else 0.0,
            "threshold": current_threshold,
            "state": state,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "face_detected": face_detected,
            "alarm_on": alarm_on,
            "alarm_duration": alarm_duration,
            "show_speaker_popup": show_speaker_popup
        }
        
        self._write_json(self.drowsiness_json_path, data)
    
    def update_system_status(self, 
                            accel_data=None, 
                            impact_detected=False,
                            report_status=None,
                            gps_position=None,
                            connection_status="OK",
                            sensor_status="Camera / Accelerometer: Waiting"):
        """
        Update system status JSON file for dashboard.
        
        Args:
            accel_data: tuple of (x, y, z) or None
            impact_detected: bool, Whether impact was detected
            report_status: dict or None, Report manager status
            gps_position: tuple of (latitude, longitude) or None
            connection_status: str, Connection status message
            sensor_status: str, Sensor status message
        """
        accel_magnitude = 0.0
        if accel_data:
            x, y, z = accel_data
            accel_magnitude = (x**2 + y**2 + z**2) ** 0.5 / 9.8  # Convert to G
        
        # Extract response request status from report_status
        response_requested = False
        response_message = ""
        response_remaining_time = 0.0
        if report_status:
            status = report_status.get('status', 'NORMAL')
            if status == 'ALERT':
                response_requested = True
                response_message = report_status.get('message', 'Touch screen to cancel report')
                response_remaining_time = report_status.get('remaining_time', 0.0)
        
        data = {
            "connection_status": connection_status,
            "sensor_status": sensor_status,
            "accel_magnitude": accel_magnitude,
            "accel_data": {
                "x": accel_data[0] if accel_data else 0.0,
                "y": accel_data[1] if accel_data else 0.0,
                "z": accel_data[2] if accel_data else 0.0
            },
            "gps_position": {
                "latitude": gps_position[0] if gps_position else 0.0,
                "longitude": gps_position[1] if gps_position else 0.0
            },
            "gps_position_string": f"({gps_position[0]:.4f}, {gps_position[1]:.4f})" if gps_position else "(-, -)",
            "impact_detected": impact_detected,
            "report_status": report_status or {},
            "response_requested": response_requested,
            "response_message": response_message,
            "response_remaining_time": response_remaining_time,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self._write_json(self.status_json_path, data)
    
    def update_log_summary(self):
        """
        Update log summary JSON file for report tab.
        Reads driving_events.log and creates summary statistics.
        """
        try:
            from driver_monitor.logging_system.log_parser import LogParser
            import pandas as pd
            
            df = LogParser.load_recent_days(days=30)  # Last 30 days
            
            if df.empty:
                summary = {
                    "total_events": 0,
                    "drowsiness_count": 0,
                    "sudden_acceleration_count": 0,
                    "sudden_stop_count": 0,
                    "monthly_score": 100,
                    "daily_scores": [],
                    "event_counts": {
                        "sudden_stop": 0,
                        "sudden_acceleration": 0,
                        "drowsiness": 0
                    }
                }
            else:
                # Filter only actual driving events (exclude system events like "Start program", "program quit", etc.)
                valid_event_types = ['drowsiness', 'sudden acceleration', 'sudden stop']
                df_driving = df[df['EventType'].isin(valid_event_types)]
                
                # Count events
                drowsiness_count = len(df_driving[df_driving['EventType'] == 'drowsiness'])
                sudden_accel_count = len(df_driving[df_driving['EventType'] == 'sudden acceleration'])
                sudden_stop_count = len(df_driving[df_driving['EventType'] == 'sudden stop'])
                
                # Calculate scores: Start from 100 and deduct points for each event
                # Each event deducts 5 points (can be adjusted)
                total_events = len(df_driving)  # Only count actual driving events
                base_score = 100
                deduction_per_event = 5
                
                # Calculate monthly score: 100 - (total_events * deduction_per_event)
                monthly_score = max(0, base_score - (total_events * deduction_per_event))
                
                # Calculate daily scores: Start from 100 for each day, deduct for events
                daily_scores = []
                for date in df_driving['Timestamp'].dt.date.unique():
                    day_events = df_driving[df_driving['Timestamp'].dt.date == date]
                    event_count = len(day_events)
                    # Each day starts at 100, deducts points for events
                    day_score = max(0, base_score - (event_count * deduction_per_event))
                    daily_scores.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "score": day_score,
                        "day": date.day
                    })
                
                # Count report events (for logging)
                report_events = df[df['EventType'].str.contains('report', case=False, na=False)]
                report_triggered_count = len(report_events[report_events['EventType'].str.contains('report_triggered', case=False, na=False)])
                report_cancelled_count = len(report_events[report_events['EventType'].str.contains('report_cancelled', case=False, na=False)])
                report_alert_count = len(report_events[report_events['EventType'].str.contains('report_alert_triggered', case=False, na=False)])
                sms_sent_count = len(report_events[report_events['EventType'].str.contains('sms_report_sent', case=False, na=False)])
                
                summary = {
                    "total_events": len(df_driving),  # Only count actual driving events
                    "drowsiness_count": int(drowsiness_count),
                    "sudden_acceleration_count": int(sudden_accel_count),
                    "sudden_stop_count": int(sudden_stop_count),
                    "monthly_score": monthly_score,
                    "daily_scores": daily_scores,
                    "event_counts": {
                        "sudden_stop": int(sudden_stop_count),
                        "sudden_acceleration": int(sudden_accel_count),
                        "drowsiness": int(drowsiness_count)
                    },
                    "report_stats": {
                        "alert_triggered": int(report_alert_count),
                        "report_triggered": int(report_triggered_count),
                        "report_cancelled": int(report_cancelled_count),
                        "sms_sent": int(sms_sent_count)
                    }
                }
            
            self._write_json(self.log_summary_json_path, summary)
            
        except Exception as e:
            print(f"[DataBridge] Error updating log summary: {e}")
    
    def _write_json(self, filepath, data):
        """Write data to JSON file atomically."""
        try:
            # Write to temporary file first, then rename (atomic operation)
            temp_path = filepath + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Atomic rename
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_path, filepath)
            
        except Exception as e:
            print(f"[DataBridge] Error writing JSON: {e}")
    
    def get_data_path(self):
        """Get the data directory path."""
        return self.data_dir
