# config_manager.py
"""
Centralized configuration management.
Handles config reloading and provides consistent access to configuration values.
"""
import importlib
import os
import sys
from pathlib import Path

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ConfigManager:
    """
    Singleton configuration manager.
    Provides centralized access to configuration values with automatic reloading.
    """
    _instance = None
    _config = None
    _last_reload_time = None
    _config_file_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the config manager."""
        import config as config_module
        self._config = config_module
        self._config_file_path = os.path.join(project_root, "config.py")
        self._last_reload_time = self._get_file_mtime()
    
    def _get_file_mtime(self):
        """Get config file modification time."""
        try:
            if self._config_file_path and os.path.exists(self._config_file_path):
                return os.path.getmtime(self._config_file_path)
        except (OSError, PermissionError):
            # File access error, return 0 to force reload
            pass
        return 0
    
    def _reload_if_needed(self):
        """Reload config if file has been modified."""
        try:
            current_mtime = self._get_file_mtime()
            if current_mtime > self._last_reload_time:
                importlib.reload(self._config)
                self._last_reload_time = current_mtime
        except Exception as e:
            print(f"[ConfigManager] Warning: Failed to reload config: {e}")
    
    def get(self, key, default=None):
        """
        Get configuration value.
        
        Args:
            key: str, Configuration key name
            default: Any, Default value if key not found
            
        Returns:
            Configuration value or default
        """
        self._reload_if_needed()
        return getattr(self._config, key, default)
    
    def reload(self):
        """Force reload configuration."""
        try:
            importlib.reload(self._config)
            self._last_reload_time = self._get_file_mtime()
        except Exception as e:
            print(f"[ConfigManager] Warning: Failed to reload config: {e}")
    
    def get_config(self):
        """
        Get the config module directly (for backward compatibility).
        
        Returns:
            config module
        """
        self._reload_if_needed()
        return self._config

