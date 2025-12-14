#!/bin/bash
# USB 자동 일시정지 비활성화 스크립트
# USB 카메라 연결 안정성을 위해 전력 절약 모드를 비활성화합니다.

echo "=========================================="
echo "USB Power Management Fix"
echo "=========================================="
echo ""
echo "This script will disable USB autosuspend to prevent camera disconnection."
echo ""

# USB 자동 일시정지 비활성화 규칙 생성
RULE_FILE="/etc/udev/rules.d/50-usb_power.rules"

echo "Creating udev rule to disable USB autosuspend..."
sudo bash -c "cat > $RULE_FILE << 'EOF'
# Disable USB autosuspend for all USB devices
# This prevents USB cameras from disconnecting due to power management
SUBSYSTEM==\"usb\", ATTR{power/autosuspend}=\"-1\"
SUBSYSTEM==\"usb\", ATTR{power/control}=\"on\"
EOF"

if [ $? -eq 0 ]; then
    echo "✅ udev rule created successfully."
else
    echo "❌ Failed to create udev rule."
    exit 1
fi

# udev 규칙 재로드
echo ""
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

if [ $? -eq 0 ]; then
    echo "✅ udev rules reloaded successfully."
else
    echo "❌ Failed to reload udev rules."
    exit 1
fi

echo ""
echo "=========================================="
echo "USB Power Management Fix Complete"
echo "=========================================="
echo ""
echo "USB autosuspend has been disabled."
echo "Please reboot your Raspberry Pi for changes to take full effect:"
echo "  sudo reboot"
echo ""

