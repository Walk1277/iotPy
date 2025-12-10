# gps_manager.py
"""
GPS Manager for location tracking.
Supports both real GPS modules (Raspberry Pi) and simulation mode (development).
"""
import datetime
import sys
import os
import time

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to import GPS libraries
try:
    import serial
    import pynmea2
    GPS_LIBRARY_AVAILABLE = True
except ImportError:
    GPS_LIBRARY_AVAILABLE = False
    print("[GPS] pynmea2 not available. Using simulation mode.")

from config import GPS_ENABLED, GPS_SERIAL_PORT, GPS_BAUD_RATE


class GPSManager:
    """
    GPS Manager for location tracking.
    Supports real GPS modules via serial/UART and simulation mode.
    """
    
    def __init__(self, simulate=False):
        """
        Args:
            simulate: If True, use simulation mode (for development)
        """
        self.simulate = simulate or not GPS_ENABLED
        self.gps_serial = None
        self.last_position = None
        self.last_update_time = None
        self.is_valid = False
        
        # Simulation data (Seoul, South Korea - default location)
        self.sim_latitude = 37.5665
        self.sim_longitude = 126.9780
        self.sim_altitude = 0.0
        self.sim_speed = 0.0
        
        # For simulation: simulate movement
        self.sim_base_time = time.time()
    
    def initialize(self):
        """Initialize GPS module."""
        if self.simulate:
            print("[GPS] Running in simulation mode.")
            self.is_valid = True
            self.last_position = (self.sim_latitude, self.sim_longitude)
            self.last_update_time = datetime.datetime.now()
            return
        
        if not GPS_LIBRARY_AVAILABLE:
            print("[GPS] GPS libraries not available. Using simulation mode.")
            self.simulate = True
            self.is_valid = True
            self.last_position = (self.sim_latitude, self.sim_longitude)
            self.last_update_time = datetime.datetime.now()
            return
        
        try:
            # Try to open GPS serial port
            self.gps_serial = serial.Serial(
                GPS_SERIAL_PORT,
                GPS_BAUD_RATE,
                timeout=1
            )
            print(f"[GPS] GPS module initialized on {GPS_SERIAL_PORT}")
            self.is_valid = True
        except serial.SerialException as e:
            print(f"[GPS] Failed to open GPS serial port: {e}")
            print("[GPS] Falling back to simulation mode.")
            self.simulate = True
            self.is_valid = True
            self.last_position = (self.sim_latitude, self.sim_longitude)
            self.last_update_time = datetime.datetime.now()
        except Exception as e:
            print(f"[GPS] GPS initialization error: {e}")
            self.simulate = True
            self.is_valid = True
            self.last_position = (self.sim_latitude, self.sim_longitude)
            self.last_update_time = datetime.datetime.now()
    
    def read_gps(self):
        """
        Read current GPS position.
        
        Returns:
            tuple: (latitude, longitude, altitude, speed) or None if not available
        """
        if not self.is_valid:
            return None
        
        if self.simulate:
            return self._read_simulated_gps()
        
        return self._read_real_gps()
    
    def _read_simulated_gps(self):
        """Read simulated GPS data (for development/testing)."""
        # Simulate slight movement for testing
        elapsed = time.time() - self.sim_base_time
        
        # Add small random-like movement (sine wave pattern)
        import math
        lat_offset = math.sin(elapsed / 100.0) * 0.001
        lon_offset = math.cos(elapsed / 100.0) * 0.001
        
        lat = self.sim_latitude + lat_offset
        lon = self.sim_longitude + lon_offset
        alt = self.sim_altitude
        speed = abs(math.sin(elapsed / 50.0)) * 30.0  # 0-30 km/h
        
        self.last_position = (lat, lon)
        self.last_update_time = datetime.datetime.now()
        
        return (lat, lon, alt, speed)
    
    def _read_real_gps(self):
        """Read GPS data from real GPS module."""
        if self.gps_serial is None:
            return None
        
        try:
            # Read NMEA sentences from GPS
            line = self.gps_serial.readline().decode('utf-8', errors='ignore')
            
            if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                msg = pynmea2.parse(line)
                
                if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                    if msg.latitude and msg.longitude:
                        lat = float(msg.latitude)
                        lon = float(msg.longitude)
                        alt = float(msg.altitude) if hasattr(msg, 'altitude') else 0.0
                        speed = float(msg.spd_over_grnd) if hasattr(msg, 'spd_over_grnd') else 0.0
                        
                        self.last_position = (lat, lon)
                        self.last_update_time = datetime.datetime.now()
                        
                        return (lat, lon, alt, speed)
            
            # If no valid data, return last known position
            if self.last_position:
                return (*self.last_position, self.sim_altitude, 0.0)
            
            return None
            
        except Exception as e:
            # On error, return last known position or None
            if self.last_position:
                return (*self.last_position, self.sim_altitude, 0.0)
            return None
    
    def get_position(self):
        """
        Get current position as (latitude, longitude).
        
        Returns:
            tuple: (latitude, longitude) or None
        """
        gps_data = self.read_gps()
        if gps_data:
            return (gps_data[0], gps_data[1])
        return self.last_position
    
    def get_position_string(self):
        """
        Get position as formatted string.
        
        Returns:
            str: Formatted position string like "(37.5665, 126.9780)"
        """
        pos = self.get_position()
        if pos:
            return f"({pos[0]:.4f}, {pos[1]:.4f})"
        return "(-, -)"
    
    def close(self):
        """Close GPS connection."""
        if self.gps_serial:
            try:
                self.gps_serial.close()
                print("[GPS] GPS connection closed.")
            except Exception as e:
                print(f"[GPS] Error closing GPS: {e}")

