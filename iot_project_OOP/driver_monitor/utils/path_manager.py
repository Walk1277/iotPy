# path_manager.py
"""
Centralized path management.
Handles all file paths for data files, logs, and UI communication.
"""
import os
import sys

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class PathManager:
    """
    Centralized path management for all data files.
    """
    
    # Raspberry Pi default paths
    RPI_DATA_DIR = "/home/pi/iot/data"
    RPI_HOME_DIR = "/home/pi"
    
    @staticmethod
    def _is_raspberry_pi():
        """Check if running on Raspberry Pi."""
        return os.path.exists(PathManager.RPI_HOME_DIR) and os.path.isdir(PathManager.RPI_HOME_DIR)
    
    @staticmethod
    def get_data_dir():
        """
        Get data directory path.
        Tries Raspberry Pi path first, then falls back to project root.
        
        Returns:
            str: Data directory path
        """
        if PathManager._is_raspberry_pi():
            return PathManager.RPI_DATA_DIR
        return os.path.join(project_root, "data")
    
    @staticmethod
    def get_drowsiness_json_path():
        """Get drowsiness.json file path."""
        return os.path.join(PathManager.get_data_dir(), "drowsiness.json")
    
    @staticmethod
    def get_status_json_path():
        """Get status.json file path."""
        return os.path.join(PathManager.get_data_dir(), "status.json")
    
    @staticmethod
    def get_log_summary_json_path():
        """Get log_summary.json file path."""
        return os.path.join(PathManager.get_data_dir(), "log_summary.json")
    
    @staticmethod
    def get_user_response_json_path():
        """Get user_response.json file path."""
        return os.path.join(PathManager.get_data_dir(), "user_response.json")
    
    @staticmethod
    def get_stop_speaker_json_path():
        """Get stop_speaker.json file path."""
        return os.path.join(PathManager.get_data_dir(), "stop_speaker.json")
    
    @staticmethod
    def get_log_file_path():
        """Get driving_events.log file path."""
        # Log file is typically in project root, not data directory
        return os.path.join(project_root, "driving_events.log")
    
    @staticmethod
    def get_all_data_paths():
        """
        Get all data file paths as a list (for fallback scenarios).
        
        Returns:
            list: List of possible paths to try
        """
        data_dir = PathManager.get_data_dir()
        return [
            data_dir,
            os.path.join(project_root, "data"),
            "data"
        ]
    
    @staticmethod
    def ensure_data_dir():
        """
        Ensure data directory exists.
        
        Returns:
            str: Data directory path (created if needed)
        """
        data_dir = PathManager.get_data_dir()
        try:
            os.makedirs(data_dir, exist_ok=True)
        except PermissionError:
            # Fallback to project root if permission denied
            fallback_dir = os.path.join(project_root, "data")
            os.makedirs(fallback_dir, exist_ok=True)
            return fallback_dir
        return data_dir

