#!/usr/bin/env python3
# clear_logs.py
"""
Clear driving events log file.
Called from Java UI to reset logs.
"""
import sys
import os

def clear_logs():
    """
    Clear the driving_events.log file.
    """
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, 'driving_events.log')
    
    try:
        # Clear the log file (create if doesn't exist)
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('')  # Empty file
        
        # Also clear log summary JSON (create if doesn't exist)
        import json
        log_summary_path = os.path.join(script_dir, 'data', 'log_summary.json')
        os.makedirs(os.path.dirname(log_summary_path), exist_ok=True)
        
        # Reset to default empty state
        default_summary = {
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
            },
            "report_stats": {
                "alert_triggered": 0,
                "report_triggered": 0,
                "report_cancelled": 0,
                "sms_sent": 0
            }
        }
        with open(log_summary_path, 'w', encoding='utf-8') as f:
            json.dump(default_summary, f, indent=2, ensure_ascii=False)
        
        print("SUCCESS: Logs cleared successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to clear logs: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = clear_logs()
    sys.exit(0 if success else 1)

