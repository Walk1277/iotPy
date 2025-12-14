#!/usr/bin/env python3
"""
Script to list available cameras
"""
import cv2
import sys

def list_available_cameras(max_index=5):
    """List available cameras."""
    print("=" * 50)
    print("Checking Available Cameras")
    print("=" * 50)
    
    available_cameras = []
    
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Get camera information
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Test frame reading
            ret, frame = cap.read()
            if ret:
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'status': 'OK'
                })
                print(f"✓ Camera {i}: Available (Resolution: {width}x{height}, FPS: {fps})")
            else:
                print(f"✗ Camera {i}: Opened but frame read failed")
            cap.release()
        else:
            print(f"✗ Camera {i}: Not available")
    
    print("=" * 50)
    if available_cameras:
        print(f"\nTotal {len(available_cameras)} camera(s) available.")
        print("\nSet CAMERA_INDEX in config.py to one of the following:")
        for cam in available_cameras:
            print(f"  CAMERA_INDEX = {cam['index']}  # Resolution: {cam['width']}x{cam['height']}")
        print("\nOr specify directly from command line:")
        for cam in available_cameras:
            print(f"  python main.py --index {cam['index']}")
    else:
        print("\n⚠ No cameras available.")
        print("Please check if cameras are connected:")
        print("  - USB webcam: lsusb")
        print("  - V4L2 devices: v4l2-ctl --list-devices")
    
    return available_cameras

if __name__ == "__main__":
    try:
        cameras = list_available_cameras()
        sys.exit(0 if cameras else 1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError occurred: {e}")
        sys.exit(1)

