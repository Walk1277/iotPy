# error_handler.py
"""
Standardized error handling.
Provides consistent error handling patterns across the system.
"""
import sys
import os
import traceback
from enum import Enum

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ErrorType(Enum):
    """Error type categories."""
    CAMERA = "camera"
    SENSOR = "sensor"
    GPS = "gps"
    CONFIG = "config"
    FILE = "file"
    NETWORK = "network"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"          # Can continue operation
    MEDIUM = "medium"    # May affect functionality
    HIGH = "high"        # Critical, may need to stop
    CRITICAL = "critical"  # Must stop operation


class ErrorHandler:
    """
    Standardized error handler for consistent error processing.
    """
    
    @staticmethod
    def handle_error(error, error_type=ErrorType.UNKNOWN, severity=ErrorSeverity.MEDIUM, 
                     context=None, logger=None, raise_after=False):
        """
        Handle an error with standardized processing.
        
        Args:
            error: Exception instance
            error_type: ErrorType enum, category of error
            severity: ErrorSeverity enum, severity level
            context: str, additional context information
            logger: EventLogger instance (optional)
            raise_after: bool, whether to re-raise after handling
            
        Returns:
            dict: Error information with keys: handled, can_continue, message
        """
        error_name = type(error).__name__
        error_message = str(error)
        
        # Build context message
        context_msg = f" [{context}]" if context else ""
        
        # Determine if operation can continue
        can_continue = severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
        
        # Format error message
        message = f"[{error_type.value.upper()}] {error_name}: {error_message}{context_msg}"
        
        # Log error
        if logger:
            logger.log(f"error_{error_type.value}: {error_name} - {error_message}")
        
        # Print error based on severity
        if severity == ErrorSeverity.CRITICAL:
            print(f"❌ CRITICAL {message}")
            print(f"   Stack trace:\n{traceback.format_exc()}")
        elif severity == ErrorSeverity.HIGH:
            print(f"⚠️  HIGH {message}")
        elif severity == ErrorSeverity.MEDIUM:
            print(f"⚠️  {message}")
        else:
            print(f"ℹ️  {message}")
        
        # Re-raise if requested
        if raise_after:
            raise
        
        return {
            'handled': True,
            'can_continue': can_continue,
            'message': message,
            'error_type': error_type.value,
            'severity': severity.value
        }
    
    @staticmethod
    def handle_camera_error(error, context=None, logger=None):
        """
        Handle camera-related errors.
        
        Args:
            error: Exception instance
            context: str, additional context
            logger: EventLogger instance (optional)
            
        Returns:
            dict: Error information
        """
        # Camera errors are usually medium severity (can fallback to USB)
        severity = ErrorSeverity.MEDIUM
        if isinstance(error, RuntimeError) and "not available" in str(error).lower():
            severity = ErrorSeverity.HIGH
        
        return ErrorHandler.handle_error(
            error=error,
            error_type=ErrorType.CAMERA,
            severity=severity,
            context=context or "Camera operation",
            logger=logger
        )
    
    @staticmethod
    def handle_sensor_error(error, sensor_name=None, logger=None):
        """
        Handle sensor-related errors.
        
        Args:
            error: Exception instance
            sensor_name: str, name of the sensor (e.g., "accelerometer", "GPS")
            logger: EventLogger instance (optional)
            
        Returns:
            dict: Error information
        """
        context = f"{sensor_name} sensor" if sensor_name else "Sensor"
        severity = ErrorSeverity.MEDIUM
        
        # GPS errors are usually low severity (can use simulation)
        if sensor_name and "gps" in sensor_name.lower():
            severity = ErrorSeverity.LOW
        
        return ErrorHandler.handle_error(
            error=error,
            error_type=ErrorType.SENSOR,
            severity=severity,
            context=context,
            logger=logger
        )
    
    @staticmethod
    def handle_config_error(error, config_key=None, logger=None):
        """
        Handle configuration-related errors.
        
        Args:
            error: Exception instance
            config_key: str, configuration key that caused error
            logger: EventLogger instance (optional)
            
        Returns:
            dict: Error information
        """
        context = f"Config key: {config_key}" if config_key else "Configuration"
        return ErrorHandler.handle_error(
            error=error,
            error_type=ErrorType.CONFIG,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            logger=logger
        )
    
    @staticmethod
    def handle_file_error(error, file_path=None, operation=None, logger=None):
        """
        Handle file operation errors.
        
        Args:
            error: Exception instance
            file_path: str, path to file
            operation: str, operation being performed (e.g., "read", "write")
            logger: EventLogger instance (optional)
            
        Returns:
            dict: Error information
        """
        context_parts = []
        if operation:
            context_parts.append(f"Operation: {operation}")
        if file_path:
            context_parts.append(f"File: {file_path}")
        context = ", ".join(context_parts) if context_parts else "File operation"
        
        severity = ErrorSeverity.MEDIUM
        if isinstance(error, PermissionError):
            severity = ErrorSeverity.HIGH
        
        return ErrorHandler.handle_error(
            error=error,
            error_type=ErrorType.FILE,
            severity=severity,
            context=context,
            logger=logger
        )
    
    @staticmethod
    def handle_network_error(error, endpoint=None, logger=None):
        """
        Handle network-related errors.
        
        Args:
            error: Exception instance
            endpoint: str, network endpoint
            logger: EventLogger instance (optional)
            
        Returns:
            dict: Error information
        """
        context = f"Endpoint: {endpoint}" if endpoint else "Network operation"
        # Network errors are usually low severity (can use fallback)
        return ErrorHandler.handle_error(
            error=error,
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.LOW,
            context=context,
            logger=logger
        )
    
    @staticmethod
    def safe_execute(func, error_type=ErrorType.UNKNOWN, severity=ErrorSeverity.MEDIUM,
                    context=None, logger=None, default_return=None):
        """
        Safely execute a function with error handling.
        
        Args:
            func: callable, function to execute
            error_type: ErrorType enum
            severity: ErrorSeverity enum
            context: str, context information
            logger: EventLogger instance (optional)
            default_return: Any, value to return on error
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func()
        except Exception as e:
            error_info = ErrorHandler.handle_error(
                error=e,
                error_type=error_type,
                severity=severity,
                context=context,
                logger=logger
            )
            return default_return

