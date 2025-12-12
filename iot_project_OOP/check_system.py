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
                "message": f"카메라 정상 작동 (해상도: {width}x{height})",
                "details": f"프레임 캡처 성공"
            }
        else:
            camera.release()
            return {
                "status": "ERROR",
                "message": "카메라 프레임 캡처 실패",
                "details": "프레임을 읽을 수 없습니다"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "카메라 초기화 실패",
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
                "message": "가속도 센서가 연결되지 않음",
                "details": "라즈베리파이 환경이 아니거나 ADXL345가 연결되지 않았습니다"
            }
        
        # Try to read accelerometer data
        accel_data, event = accel.read_accel()
        if accel_data is not None:
            x, y, z = accel_data
            return {
                "status": "OK",
                "message": "가속도 센서 정상 작동",
                "details": f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f} m/s²"
            }
        else:
            return {
                "status": "ERROR",
                "message": "가속도 센서 데이터 읽기 실패",
                "details": "센서에서 데이터를 읽을 수 없습니다"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "가속도 센서 초기화 실패",
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
                "message": "GPS 시뮬레이션 모드",
                "details": "실제 GPS 모듈이 연결되지 않았거나 GPS_ENABLED가 False입니다. config.py에서 GPS_ENABLED를 True로 설정하세요."
            }
        
        if not gps.is_valid:
            return {
                "status": "ERROR",
                "message": "GPS 초기화 실패",
                "details": "GPS 모듈을 초기화할 수 없습니다"
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
                "message": "GPS 정상 작동 (실제 신호 수신)",
                "details": f"위도: {latest[0]:.6f}, 경도: {latest[1]:.6f}"
            }
        elif len(positions) > 0:
            # Got position but might be simulation or fixed position
            latest = positions[-1]
            if abs(latest[0] - default_sim_lat) < 0.001 and abs(latest[1] - default_sim_lon) < 0.001:
                return {
                    "status": "WARNING",
                    "message": "GPS 시뮬레이션 데이터 감지",
                    "details": f"위치: {latest[0]:.6f}, {latest[1]:.6f} (기본 시뮬레이션 위치입니다. 실제 GPS 모듈을 연결하세요)"
                }
            else:
                return {
                    "status": "WARNING",
                    "message": "GPS 신호 수신 중",
                    "details": f"위치: {latest[0]:.6f}, {latest[1]:.6f} (위성 신호 확인 중)"
                }
        else:
            return {
                "status": "ERROR",
                "message": "GPS 신호 수신 실패",
                "details": "GPS 모듈에서 위치 데이터를 받을 수 없습니다. GPS 모듈이 연결되어 있고 안테나가 외부에 노출되어 있는지 확인하세요."
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "GPS 체크 실패",
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
                "message": "스피커 정상 작동",
                "details": "테스트 알람 재생 성공"
            }
        except Exception as e:
            speaker.cleanup()
            return {
                "status": "WARNING",
                "message": "스피커 테스트 실패",
                "details": str(e)
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "스피커 초기화 실패",
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
                "message": "SMS 기능이 비활성화됨",
                "details": "config.py에서 SMS_ENABLED를 True로 설정하세요"
            }
        
        if not config.SMS_FROM_NUMBER or not config.SMS_TO_NUMBER:
            return {
                "status": "WARNING",
                "message": "전화번호가 설정되지 않음",
                "details": "송신 및 수신 전화번호를 설정하세요"
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
                "message": "SMS 서비스 초기화 실패",
                "details": "SOLAPI 라이브러리가 설치되지 않았거나 API 키가 잘못되었습니다"
            }
        
        # Test SMS sending (actually send a test message)
        try:
            from solapi.model import RequestMessage
            test_message = RequestMessage(
                from_=config.SMS_FROM_NUMBER,
                to=config.SMS_TO_NUMBER,
                text=f"[시스템 테스트] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 시스템 체크 테스트 메시지입니다."
            )
            
            response = report_manager.sms_service.send(test_message)
            return {
                "status": "OK",
                "message": "SMS 테스트 발송 성공",
                "details": f"메시지 ID: {response.group_info.group_id}, 수신 번호: {config.SMS_TO_NUMBER}"
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "message": "SMS 발송 실패",
                "details": str(e)
            }
    except ImportError:
        return {
            "status": "ERROR",
            "message": "SMS 라이브러리 없음",
            "details": "solapi 라이브러리가 설치되지 않았습니다. pip3 install solapi 실행"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": "SMS 테스트 실패",
            "details": str(e)
        }

def main():
    """Run all system checks."""
    results = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks": {}
    }
    
    print("=== 시스템 체크 시작 ===", file=sys.stderr)
    
    # Check camera
    print("[1/5] 카메라 체크 중...", file=sys.stderr)
    results["checks"]["camera"] = check_camera()
    print(f"카메라: {results['checks']['camera']['status']}", file=sys.stderr)
    
    # Check accelerometer
    print("[2/5] 가속도 센서 체크 중...", file=sys.stderr)
    results["checks"]["accelerometer"] = check_accelerometer()
    print(f"가속도 센서: {results['checks']['accelerometer']['status']}", file=sys.stderr)
    
    # Check GPS
    print("[3/5] GPS 체크 중...", file=sys.stderr)
    results["checks"]["gps"] = check_gps()
    print(f"GPS: {results['checks']['gps']['status']}", file=sys.stderr)
    
    # Check speaker
    print("[4/5] 스피커 체크 중...", file=sys.stderr)
    results["checks"]["speaker"] = check_speaker()
    print(f"스피커: {results['checks']['speaker']['status']}", file=sys.stderr)
    
    # Test SMS
    print("[5/5] SMS 테스트 중...", file=sys.stderr)
    results["checks"]["sms"] = test_sms()
    print(f"SMS: {results['checks']['sms']['status']}", file=sys.stderr)
    
    # Output JSON result
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Count statuses
    ok_count = sum(1 for check in results["checks"].values() if check["status"] == "OK")
    warning_count = sum(1 for check in results["checks"].values() if check["status"] == "WARNING")
    error_count = sum(1 for check in results["checks"].values() if check["status"] == "ERROR")
    
    print(f"\n=== 체크 완료 ===", file=sys.stderr)
    print(f"정상: {ok_count}, 경고: {warning_count}, 오류: {error_count}", file=sys.stderr)
    
    # Exit with error code if any errors
    sys.exit(0 if error_count == 0 else 1)

if __name__ == '__main__':
    main()

