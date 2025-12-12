# Fix SMS Service Initialization Error

## Error Message
```
"status": "ERROR",
"message": "SMS service initialization failed",
"details": "SOLAPI library is not installed or API key is incorrect"
```

## Solution Steps

### 1. Install SOLAPI Library
```bash
pip3 install solapi
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

### 2. Verify Installation
```bash
python3 -c "from solapi import SolapiMessageService; print('SOLAPI installed successfully')"
```

### 3. Check API Credentials in config.py
Make sure the following are set correctly in `config.py`:
```python
SMS_API_KEY = "your-api-key-here"
SMS_API_SECRET = "your-api-secret-here"
SMS_ENABLED = True
SMS_FROM_NUMBER = "010-xxxx-xxxx"
SMS_TO_NUMBER = "010-xxxx-xxxx"
```

### 4. Verify API Key and Secret
- Log in to [SOLAPI Console](https://console.solapi.com/)
- Go to "API 인증키" (API Keys) section
- Verify that your API key and secret are correct
- Make sure the API key is active and not expired

### 5. Test SMS Service Manually
```bash
python3 -c "
from solapi import SolapiMessageService
from config import SMS_API_KEY, SMS_API_SECRET
try:
    service = SolapiMessageService(api_key=SMS_API_KEY, api_secret=SMS_API_SECRET)
    print('SMS service initialized successfully!')
except Exception as e:
    print(f'Error: {e}')
"
```

### 6. Common Issues

#### Issue: "SOLAPI library is not installed"
**Solution:** Install solapi library
```bash
pip3 install solapi
```

#### Issue: "API key is incorrect"
**Solution:** 
1. Check `config.py` for correct API key and secret
2. Verify credentials in SOLAPI console
3. Make sure there are no extra spaces or quotes

#### Issue: "Failed to initialize SMS service"
**Solution:**
1. Check internet connection (SOLAPI requires network access)
2. Verify API key permissions in SOLAPI console
3. Check if your SOLAPI account has sufficient credits

### 7. Re-run System Check
After fixing the issues, run the system check again:
```bash
python3 check_system.py
```

## Troubleshooting Commands

Check if solapi is installed:
```bash
pip3 list | grep solapi
```

Check config.py values:
```bash
python3 -c "import config; print(f'API Key: {config.SMS_API_KEY[:10]}...'); print(f'API Secret: {config.SMS_API_SECRET[:10]}...'); print(f'SMS Enabled: {config.SMS_ENABLED}')"
```

Test SMS service initialization:
```bash
python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())
from driver_monitor.report.report_manager import ReportManager
from driver_monitor.logging_system.event_logger import EventLogger
from driver_monitor.sensors.gps_manager import GPSManager

logger = EventLogger()
gps = GPSManager(simulate=True)
report_manager = ReportManager(logger=logger, gps_manager=gps)

if report_manager.sms_service:
    print('✅ SMS service initialized successfully!')
else:
    print('❌ SMS service initialization failed')
    print('Check:')
    print('  1. solapi library: pip3 install solapi')
    print('  2. API credentials in config.py')
    print('  3. Internet connection')
"
```

