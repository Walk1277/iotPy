# event_logger.py
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import LOG_FILE

class EventLogger:
    def __init__(self):
        self.log_file = LOG_FILE

    def log(self, event_type: str):
        timestamp = datetime.datetime.now().strftime("%Y %m %d %H %M %S")
        entry = f"{timestamp} | {event_type}\n"
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            print(f"[LOG] {event_type}")
        except IOError as e:
            print(f"Error writing log: {e}")

