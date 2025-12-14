#!/usr/bin/env python3
"""
사용 가능한 카메라 목록 확인 스크립트
"""
import cv2
import sys

def list_available_cameras(max_index=5):
    """사용 가능한 카메라 목록을 확인합니다."""
    print("=" * 50)
    print("사용 가능한 카메라 확인")
    print("=" * 50)
    
    available_cameras = []
    
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # 카메라 정보 가져오기
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # 프레임 읽기 테스트
            ret, frame = cap.read()
            if ret:
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'status': 'OK'
                })
                print(f"✓ Camera {i}: 사용 가능 (해상도: {width}x{height}, FPS: {fps})")
            else:
                print(f"✗ Camera {i}: 열림 하지만 프레임 읽기 실패")
            cap.release()
        else:
            print(f"✗ Camera {i}: 사용 불가")
    
    print("=" * 50)
    if available_cameras:
        print(f"\n총 {len(available_cameras)}개의 카메라가 사용 가능합니다.")
        print("\nconfig.py에서 CAMERA_INDEX를 다음 중 하나로 설정하세요:")
        for cam in available_cameras:
            print(f"  CAMERA_INDEX = {cam['index']}  # 해상도: {cam['width']}x{cam['height']}")
        print("\n또는 명령줄에서 직접 지정:")
        for cam in available_cameras:
            print(f"  python main.py --index {cam['index']}")
    else:
        print("\n⚠ 사용 가능한 카메라가 없습니다.")
        print("카메라가 연결되어 있는지 확인하세요:")
        print("  - USB 웹캠: lsusb")
        print("  - V4L2 디바이스: v4l2-ctl --list-devices")
    
    return available_cameras

if __name__ == "__main__":
    try:
        cameras = list_available_cameras()
        sys.exit(0 if cameras else 1)
    except KeyboardInterrupt:
        print("\n\n취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)

