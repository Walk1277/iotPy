# Quick Start Guide

## ⚠️ Important: You Need TWO Programs Running!

**NO, you cannot run only `demo.java`!** You need both:

1. **Python Backend** - Generates data from sensors
2. **JavaFX UI** - Displays the data

## 🚀 How to Run

### Option 1: Using Scripts (Easiest)

**Terminal 1:**
```bash
cd /path/to/iot_project_OOP
./start_backend.sh
```

**Terminal 2:**
```bash
cd /path/to/iot_project_OOP
./start_ui.sh
```

### Option 2: Manual Commands

**Terminal 1 - Python Backend:**
```bash
cd /path/to/iot_project_OOP
python3 main.py start
```

**Terminal 2 - JavaFX UI:**
```bash
cd /path/to/iot_project_OOP/ui
./gradlew run
```

## 📦 Transfer to Raspberry Pi

### Step 1: Commit and Push
```bash
git add .
git commit -m "Complete system with GPS and English translation"
git push
```

### Step 2: Clone on Raspberry Pi
```bash
# On Raspberry Pi
cd /home/pi
git clone <your-repo-url>
cd iot_project_OOP
```

### Step 3: Install Dependencies
```bash
# Install Python packages
pip3 install -r requirements.txt

# Install Java 21
sudo apt update
sudo apt install openjdk-21-jdk

# Make scripts executable
chmod +x start_backend.sh start_ui.sh
chmod +x ui/gradlew
```

### Step 4: Run on Raspberry Pi

**Terminal 1:**
```bash
cd /home/pi/iot_project_OOP
./start_backend.sh
# or: python3 main.py start
```

**Terminal 2:**
```bash
cd /home/pi/iot_project_OOP
./start_ui.sh
# or: cd ui && ./gradlew run
```

## ✅ Verification

### Check if Backend is Working:
```bash
# Should see JSON files
ls -la data/
cat data/status.json
```

### Check if UI is Working:
- UI window should open
- Dashboard should show sensor status
- Data should update every second

## 🔧 Troubleshooting

### "No data in UI"
- ✅ Is Python backend running? Check with `ps aux | grep python`
- ✅ Do JSON files exist? Check `ls -la data/`
- ✅ Are JSON files updating? Check `tail -f data/status.json`

### "Camera not found"
- ✅ On Raspberry Pi: `sudo raspi-config` → Enable Camera
- ✅ Check: `lsusb` or `v4l2-ctl --list-devices`

### "JavaFX not working"
- ✅ Java version: `java -version` (should be 21+)
- ✅ Install: `sudo apt install openjdk-21-jdk`

## 📋 Summary

**Remember:**
- ❌ **NOT**: Run only `demo.java`
- ✅ **YES**: Run Python backend + JavaFX UI together
- ✅ Backend generates JSON → UI reads JSON → Everything works!

## 🎯 What Each Program Does

| Program | What It Does | Output |
|---------|-------------|--------|
| **Python Backend** | Reads camera, sensors, GPS | Creates `data/*.json` files |
| **JavaFX UI** | Reads JSON files | Displays dashboard, charts, alerts |

**They work together!** Backend writes data, UI reads and displays it.

