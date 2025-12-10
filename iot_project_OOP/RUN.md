# Quick Run Guide

## TL;DR - How to Run

**You need to run TWO programs simultaneously:**

1. **Python Backend** (generates data)
2. **JavaFX UI** (displays data)

## Step-by-Step

### On Your Development Machine

#### Terminal 1 - Start Python Backend:
```bash
cd /path/to/iot_project_OOP
python main.py start
```

#### Terminal 2 - Start JavaFX UI:
```bash
cd /path/to/iot_project_OOP/ui
./gradlew run
```

### On Raspberry Pi

#### Terminal 1 - Start Python Backend:
```bash
cd /home/pi/iot_project_OOP
python3 main.py start
```

#### Terminal 2 - Start JavaFX UI:
```bash
cd /home/pi/iot_project_OOP/ui
./gradlew run
```

## Important Notes

⚠️ **You CANNOT run only `demo.java`** - The Python backend must be running first!

**Why?**
- Python backend reads camera, accelerometer, GPS
- Python backend writes JSON files (`data/drowsiness.json`, `data/status.json`)
- JavaFX UI reads these JSON files to display data
- Without Python backend, UI will show "Waiting" or no data

## What Each Program Does

### Python Backend (`main.py start`)
- ✅ Initializes camera for face detection
- ✅ Monitors accelerometer for impacts
- ✅ Tracks GPS location
- ✅ Detects drowsiness (EAR calculation)
- ✅ Writes real-time data to JSON files
- ✅ Handles emergency reporting (SMS)

### JavaFX UI (`demo.java`)
- ✅ Reads JSON files every second
- ✅ Displays dashboard with real-time status
- ✅ Shows drowsiness alerts
- ✅ Shows accident detection status
- ✅ Displays driving reports and charts

## Transfer to Raspberry Pi

### Option 1: Using Git (Recommended)
```bash
# On Raspberry Pi
cd /home/pi
git clone <your-repo-url>
cd iot_project_OOP
```

### Option 2: Using SCP
```bash
# From your development machine
scp -r iot_project_OOP pi@raspberry-pi-ip:/home/pi/
```

### Option 3: Using USB Drive
1. Copy entire `iot_project_OOP` folder to USB
2. Plug USB into Raspberry Pi
3. Copy folder to `/home/pi/`

## First-Time Setup on Raspberry Pi

```bash
# 1. Install Python dependencies
cd /home/pi/iot_project_OOP
pip3 install -r requirements.txt

# 2. Install Java 21
sudo apt update
sudo apt install openjdk-21-jdk

# 3. Make Gradle executable
cd ui
chmod +x gradlew

# 4. Test build
./gradlew build
```

## Verification

### Check if Python backend is working:
```bash
# Should see JSON files being created
ls -la data/
# Should see: drowsiness.json, status.json, log_summary.json
```

### Check if UI can read data:
```bash
# In UI, you should see:
# - Dashboard showing sensor status
# - Drowsiness tab showing EAR values
# - Accident tab showing G-sensor values
```

## Troubleshooting

### "No data showing in UI"
- ✅ Check Python backend is running
- ✅ Check JSON files exist: `ls -la data/`
- ✅ Check JSON files have content: `cat data/status.json`

### "Camera not found"
- ✅ On Raspberry Pi: `sudo raspi-config` → Enable Camera
- ✅ Check camera: `lsusb` or `v4l2-ctl --list-devices`

### "JavaFX not working"
- ✅ Check Java version: `java -version` (should be 21+)
- ✅ Install Java: `sudo apt install openjdk-21-jdk`

## Summary

**Remember:**
1. ✅ Python backend runs first → generates JSON data
2. ✅ JavaFX UI runs second → reads and displays JSON data
3. ✅ Both must run simultaneously
4. ✅ `demo.java` alone is NOT enough!

