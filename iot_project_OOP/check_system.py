#!/usr/bin/env python3
# check_system.py
"""
System check script to verify all sensors and components are working.
Called from Java UI to test system functionality.
"""
import sys
import os
import json
import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_camera():
    """Check if camera is working."""
    try:
        from driver_monitor.camera.camera_manager import CameraManager
        camera = CameraManager(0)
        camera.initialize()
        
        # Try to capture a frame
        frame, frame_rgb = camera.get_frames()
        if frame is not None and frame_rgb is not None:
            height, width = frame.shape[:2]
            camera.release()
            return {
                "status": "OK",
                "message": f"Camera working normally (Resolution: {width}x{height})",
                "details": f"Frame capture successful"
            }
        else:
            camera.release()
            return {
                "status": "ERROR",
                "message": "Camera frame capture failed",
                "details": "Cannot read frame"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "Camera initialization failed",
            "details": str(e)
        }

def check_accelerometer():
    """Check if accelerometer is working."""
    try:
        from driver_monitor.sensors.accelerometer_detector import AccelerometerDetector
        accel = AccelerometerDetector()
        accel.initialize()
        
        if accel.accel is None:
            return {
                "status": "WARNING",
                "message": "Accelerometer sensor not connected",
                "details": "Not on Raspberry Pi environment or ADXL345 is not connected"
            }
        
        # Try to read accelerometer data
        accel_data, event = accel.read_accel()
        if accel_data is not None:
            x, y, z = accel_data
            return {
                "status": "OK",
                "message": "Accelerometer sensor working normally",
                "details": f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f} m/s²"
            }
        else:
            return {
                "status": "ERROR",
                "message": "Failed to read accelerometer data",
                "details": "Cannot read data from sensor"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "Accelerometer sensor initialization failed",
            "details": str(e)
        }

def check_gps():
    """Check if GPS is working and receiving real signals."""
    try:
        from driver_monitor.sensors.gps_manager import GPSManager
        import config
        import importlib
        importlib.reload(config)
        
        # Use GPS_ENABLED from config to determine simulation
        gps_simulate = not config.GPS_ENABLED
        gps = GPSManager(simulate=gps_simulate)
        gps.initialize()
        
        if gps.simulate:
            return {
                "status": "WARNING",
                "message": "GPS Simulation Mode",
                "details": "No real GPS module connected or GPS_ENABLED is False. Set GPS_ENABLED to True in config.py."
            }
        
        if not gps.is_valid:
            return {
                "status": "ERROR",
                "message": "GPS initialization failed",
                "details": "Cannot initialize GPS module"
            }
        
        # Try to read GPS data multiple times to check for real signal
        real_signal = False
        positions = []
        default_sim_lat = 37.5665  # Seoul default simulation position
        default_sim_lon = 126.9780
        
        for i in range(10):  # More attempts to get real signal
            gps_data = gps.read_gps()
            if gps_data:
                lat, lon, alt, speed = gps_data
                positions.append((lat, lon))
                # Check if position is reasonable (not 0,0 or default simulation values)
                if lat != 0.0 and lon != 0.0:
                    # Check if it's not the default simulation position (Seoul)
                    # Allow some tolerance for actual GPS in Seoul area
                    lat_diff = abs(lat - default_sim_lat)
                    lon_diff = abs(lon - default_sim_lon)
                    # If position is significantly different from default, or if we get multiple different positions, it's real
                    if lat_diff > 0.01 or lon_diff > 0.01 or len(set([(round(p[0], 3), round(p[1], 3)) for p in positions])) > 1:
                        real_signal = True
            import time
            time.sleep(0.3)  # Wait longer for GPS to get signal
        
        gps.close()
        
        if real_signal and len(positions) > 0:
            latest = positions[-1]
            return {
                "status": "OK",
                "message": "GPS working normally (real signal received)",
                "details": f"Latitude: {latest[0]:.6f}, Longitude: {latest[1]:.6f}"
            }
        elif len(positions) > 0:
            # Got position but might be simulation or fixed position
            latest = positions[-1]
            if abs(latest[0] - default_sim_lat) < 0.001 and abs(latest[1] - default_sim_lon) < 0.001:
                return {
                    "status": "WARNING",
                    "message": "GPS simulation data detected",
                    "details": f"Position: {latest[0]:.6f}, {latest[1]:.6f} (default simulation position. Please connect a real GPS module)"
                }
            else:
                return {
                    "status": "WARNING",
                    "message": "GPS signal receiving",
                    "details": f"Position: {latest[0]:.6f}, {latest[1]:.6f} (checking satellite signal)"
                }
        else:
            return {
                "status": "ERROR",
                "message": "GPS signal reception failed",
                "details": "Cannot receive position data from GPS module. Please ensure the GPS module is connected and the antenna is exposed to the outside."
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "GPS check failed",
            "details": str(e)
        }

def check_speaker():
    """Check if speaker is working."""
    try:
        from driver_monitor.sensors.speaker_controller import SpeakerController
        speaker = SpeakerController()
        speaker.initialize()
        
        # Try to play a test sound
        try:
            speaker.alarm_on()
            import time
            time.sleep(0.1)
            speaker.alarm_off()
            speaker.cleanup()
            return {
                "status": "OK",
                "message": "Speaker working normally",
                "details": "Test alarm playback successful"
            }
        except Exception as e:
            speaker.cleanup()
            return {
                "status": "WARNING",
                "message": "Speaker test failed",
                "details": str(e)
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "Speaker initialization failed",
            "details": str(e)
        }

def test_sms():
    """Test SMS sending functionality."""
    try:
        from driver_monitor.report.report_manager import ReportManager
        from driver_monitor.logging_system.event_logger import EventLogger
        from driver_monitor.sensors.gps_manager import GPSManager
        import config
        import importlib
        importlib.reload(config)
        
        if not config.SMS_ENABLED:
            return {
                "status": "WARNING",
                "message": "SMS feature is disabled",
                "details": "Set SMS_ENABLED to True in config.py"
            }
        
        if not config.SMS_FROM_NUMBER or not config.SMS_TO_NUMBER:
            return {
                "status": "WARNING",
                "message": "Phone numbers not set",
                "details": "Please set sender and receiver phone numbers"
            }
        
        # Try to initialize SMS service
        logger = EventLogger()
        # Use GPS_ENABLED from config
        gps_simulate = not config.GPS_ENABLED
        gps = GPSManager(simulate=gps_simulate)
        report_manager = ReportManager(logger=logger, gps_manager=gps)
        
        if report_manager.sms_service is None:
            return {
                "status": "ERROR",
                "message": "SMS service initialization failed",
                "details": "SOLAPI library is not installed or API key is incorrect"
            }
        
        # Test SMS sending (actually send a test message)
        try:
            from solapi.model import RequestMessage
            test_message = RequestMessage(
                from_=config.SMS_FROM_NUMBER,
                to=config.SMS_TO_NUMBER,
                text=f"[System Test] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - System check test message."
            )
            
            response = report_manager.sms_service.send(test_message)
            return {
                "status": "OK",
                "message": "SMS test sending successful",
                "details": f"Message ID: {response.group_info.group_id}, Receiver: {config.SMS_TO_NUMBER}"
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": "SMS sending failed",
                "details": str(e)
            }
    except ImportError:
        return {
            "status": "ERROR",
            "message": "SMS library not found",
            "details": "solapi library is not installed. Run: pip3 install solapi"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "SMS test failed",
            "details": str(e)
        }

def main():
    """Run all system checks."""
    results = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks": {}
    }
    
    print("=== Starting System Check ===", file=sys.stderr)
    
    # Check camera
    print("[1/5] Checking camera...", file=sys.stderr)
    results["checks"]["camera"] = check_camera()
    print(f"Camera: {results['checks']['camera']['status']}", file=sys.stderr)
    
    # Check accelerometer
    print("[2/5] Checking accelerometer...", file=sys.stderr)
    results["checks"]["accelerometer"] = check_accelerometer()
    print(f"Accelerometer: {results['checks']['accelerometer']['status']}", file=sys.stderr)
    
    # Check GPS
    print("[3/5] Checking GPS...", file=sys.stderr)
    results["checks"]["gps"] = check_gps()
    print(f"GPS: {results['checks']['gps']['status']}", file=sys.stderr)
    
    # Check speaker
    print("[4/5] Checking speaker...", file=sys.stderr)
    results["checks"]["speaker"] = check_speaker()
    print(f"Speaker: {results['checks']['speaker']['status']}", file=sys.stderr)
    
    # Test SMS
    print("[5/5] Testing SMS...", file=sys.stderr)
    results["checks"]["sms"] = test_sms()
    print(f"SMS: {results['checks']['sms']['status']}", file=sys.stderr)
    
    # Output JSON result
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Count statuses
    ok_count = sum(1 for check in results["checks"].values() if check["status"] == "OK")
    warning_count = sum(1 for check in results["checks"].values() if check["status"] == "WARNING")
    error_count = sum(1 for check in results["checks"].values() if check["status"] == "ERROR")
    
    print(f"\n=== Check Complete ===", file=sys.stderr)
    print(f"OK: {ok_count}, Warning: {warning_count}, Error: {error_count}", file=sys.stderr)
    
    # Exit with error code if any errors
    sys.exit(0 if error_count == 0 else 1)

if __name__ == '__main__':
    main()

