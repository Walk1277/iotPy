# event_logger.py
import datetime
import pandas as pd
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

    def load_log(self):
        try:
            df = pd.read_csv(
                self.log_file,
                sep="|",
                names=["Timestamp", "EventType"],
                skipinitialspace=True,
                header=None
            )
            df["Timestamp"] = df["Timestamp"].str.strip()
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%Y %m %d %H %M %S")
            return df
        except Exception:
            return pd.DataFrame()

