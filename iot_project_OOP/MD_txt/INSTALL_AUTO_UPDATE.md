# 자동 업데이트 설치 가이드

## 부팅 시 자동 업데이트 설정

라즈베리파이에서 부팅할 때 자동으로 시스템 업데이트를 실행하도록 설정할 수 있습니다.

### 방법 1: systemd 서비스 사용 (권장)

1. **서비스 파일 복사:**
```bash
sudo cp iot-update.service /etc/systemd/system/
```

2. **서비스 활성화:**
```bash
sudo systemctl enable iot-update.service
```

3. **서비스 시작 (테스트):**
```bash
sudo systemctl start iot-update.service
```

4. **서비스 상태 확인:**
```bash
sudo systemctl status iot-update.service
```

5. **로그 확인:**
```bash
journalctl -u iot-update.service -f
```

### 방법 2: rc.local 사용

1. **rc.local 편집:**
```bash
sudo nano /etc/rc.local
```

2. **exit 0 전에 다음 줄 추가:**
```bash
# Auto update IoT system
/bin/bash /home/pi/iot_project_OOP/update_system.sh &
```

3. **파일 저장 및 권한 확인:**
```bash
sudo chmod +x /etc/rc.local
```

### 업데이트 스크립트 동작

`update_system.sh` 스크립트는 다음을 수행합니다:

1. `requirements.txt`에서 Python 패키지 목록 읽기
2. `pip3 install --upgrade`로 모든 패키지 업데이트
3. 업데이트 로그를 `update.log` 파일에 기록

### 수동 업데이트

UI에서 "업데이트 실행" 버튼을 클릭하거나:

```bash
cd /home/pi/iot_project_OOP
./update_system.sh
```

### 업데이트 로그 확인

```bash
cat /home/pi/iot_project_OOP/update.log
```

