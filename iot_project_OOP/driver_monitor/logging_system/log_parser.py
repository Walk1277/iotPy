# logging_system/log_parser.py

import pandas as pd
import datetime
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import LOG_FILE

class LogParser:
    # Use LOG_FILE from config (no need to duplicate)

    @staticmethod
    def load_log():
        """
        Load the driving_events.log file and return a DataFrame.
        The DataFrame contains two columns:
        - Timestamp (datetime64)
        - EventType (string)
        """

        try:
            df = pd.read_csv(
                LOG_FILE,
                sep='|',
                names=['Timestamp', 'EventType'],
                skipinitialspace=True,
                header=None,
                encoding='utf-8'
            )

            # Strip whitespace
            df['Timestamp'] = df['Timestamp'].astype(str).str.strip()
            df['EventType'] = df['EventType'].astype(str).str.strip()

            # Convert timestamp to datetime
            df['Timestamp'] = pd.to_datetime(
                df['Timestamp'],
                format="%Y %m %d %H %M %S",
                errors='coerce'
            )

            # Remove rows where timestamp failed to parse
            df = df.dropna(subset=['Timestamp'])

            return df

        except FileNotFoundError:
            print("[LogParser] No log file found.")
            return pd.DataFrame()

        except pd.errors.EmptyDataError:
            print("[LogParser] Log file is empty.")
            return pd.DataFrame()

        except Exception as e:
            print(f"[LogParser] Error reading log: {e}")
            return pd.DataFrame()


    @staticmethod
    def load_today():
        """ Return logs only from today """
        df = LogParser.load_log()
        if df.empty:
            return df

        today = datetime.date.today()
        return df[df['Timestamp'].dt.date == today]


    @staticmethod
    def load_recent_days(days=7):
        """ Return logs from the last N days """
        df = LogParser.load_log()
        if df.empty:
            return df

        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)

        return df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= today)]

