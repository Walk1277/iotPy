# Smart Accident Prevention Kit

Driver monitoring system with drowsiness detection, accident detection, and automatic emergency reporting.

## System Architecture

- **Python Backend**: Camera-based drowsiness detection, accelerometer monitoring, GPS tracking, emergency reporting
- **JavaFX UI**: Real-time dashboard displaying system status, drowsiness alerts, accident detection, and driving reports

## Quick Start

### 1. Prerequisites

#### Python Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# For Raspberry Pi, install additional packages:
sudo apt-get install python3-picamera2 python3-rpi.gpio
```

#### JavaFX UI
```bash
# Install Java 21 JDK
sudo apt install openjdk-21-jdk

# Verify Java installation
java -version
```

### 2. Running the System

**Important**: Both Python backend and JavaFX UI need to be running simultaneously.

#### Step 1: Start Python Backend

```bash
# Navigate to project directory
cd /path/to/iot_project_OOP

# Start the monitoring system
python main.py start
```

The backend will:
- Initialize camera, accelerometer, GPS, and other sensors
- Start monitoring driver drowsiness and accidents
- Write real-time data to `data/drowsiness.json` and `data/status.json`
- Update log summary to `data/log_summary.json`

#### Step 2: Start JavaFX UI

**In a separate terminal:**

```bash
# Navigate to UI directory
cd ui

# Build and run the UI
./gradlew run

# Or build first, then run
./gradlew build
./gradlew run
```

The UI will:
- Read JSON files from `data/` directory every second
- Display real-time status on dashboard
- Show drowsiness detection, accident detection, and driving reports

### 3. Running on Linux

#### Ubuntu/Debian

**1. Install dependencies:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip openjdk-21-jdk git v4l-utils
```

**2. Setup project:**
```bash
git clone <your-repo-url>
cd iot_project_OOP
pip3 install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew
```

**3. Run:**
```bash
# Terminal 1
./start_backend.sh

# Terminal 2
./start_ui.sh
```

#### Fedora/CentOS

**1. Install dependencies:**
```bash
# Fedora
sudo dnf install -y python3 python3-pip java-21-openjdk-devel git v4l-utils

# CentOS
sudo yum install -y python3 python3-pip git v4l-utils
```

**2. Setup and run:**
```bash
cd /path/to/iot_project_OOP
pip3 install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew

./start_backend.sh  # Terminal 1
./start_ui.sh       # Terminal 2
```

#### Arch Linux

**1. Install dependencies:**
```bash
sudo pacman -S python python-pip jdk-openjdk git v4l-utils
```

**2. Setup and run:**
```bash
cd /path/to/iot_project_OOP
pip install -r requirements.txt
chmod +x start_backend.sh start_ui.sh ui/gradlew

./start_backend.sh  # Terminal 1
./start_ui.sh       # Terminal 2
```

### 4. Running on Raspberry Pi

#### Transfer Files to Raspberry Pi

```bash
# From your development machine
scp -r iot_project_OOP pi@raspberry-pi-ip:/home/pi/
```

Or use Git:
```bash
# On Raspberry Pi
cd /home/pi
git clone <your-repo-url>
cd iot_project_OOP
```

#### Setup on Raspberry Pi

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Java 21
sudo apt update
sudo apt install openjdk-21-jdk

# Install Gradle wrapper (if not included)
cd ui
chmod +x gradlew
```

#### Run on Raspberry Pi

**Terminal 1 - Python Backend:**
```bash
cd /home/pi/iot_project_OOP
python3 main.py start
```

**Terminal 2 - JavaFX UI:**
```bash
cd /home/pi/iot_project_OOP/ui
./gradlew run
```

### 5. Configuration

Edit `config.py` to adjust settings:

```python
# Drowsiness detection
EAR_THRESHOLD = 0.20  # Eye Aspect Ratio threshold

# Accelerometer
ACCEL_THRESHOLD = 4.0  # m/s^2

# GPS
GPS_ENABLED = False  # Set to True to enable GPS module
GPS_SERIAL_PORT = "/dev/ttyUSB0"  # GPS serial port

# SMS Reporting
SMS_ENABLED = False  # Set to True to enable SMS
SMS_API_KEY = "your-api-key"
SMS_API_SECRET = "your-api-secret"
```

### 6. Data Files

The system creates JSON files in the `data/` directory:

- `drowsiness.json`: Real-time drowsiness status (EAR, state, alarm)
- `status.json`: System status (sensors, GPS, impact detection, report status)
- `log_summary.json`: Driving statistics and event counts

### 7. Troubleshooting

#### Python Backend Issues

**Camera not found:**
- Check camera connection: `lsusb` or `v4l2-ctl --list-devices`
- On Raspberry Pi, ensure camera is enabled: `sudo raspi-config`

**GPS not working:**
- Check GPS module connection
- Verify serial port: `ls /dev/ttyUSB*` or `ls /dev/ttyAMA*`
- Set `GPS_ENABLED = True` in `config.py`

**Import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path: `python -c "import sys; print(sys.path)"`

#### JavaFX UI Issues

**UI not showing data:**
- Ensure Python backend is running
- Check if JSON files exist: `ls -la data/`
- Verify JSON file paths in UI code match your setup

**JavaFX not found:**
- Install Java 21: `sudo apt install openjdk-21-jdk`
- Check Java version: `java -version` (should be 21+)

**Build errors:**
- Run `./gradlew clean build`
- Check Gradle wrapper: `chmod +x gradlew`

**"./gradlew: No such file or directory" error:**
- If gradlew file is missing, you need to generate the Gradle wrapper:
  ```bash
  # Install Gradle (if not installed)
  sudo apt install gradle
  
  # Generate gradlew
  cd ui
  gradle wrapper
  chmod +x gradlew
  ```
- Or use `start_all.sh` or `start_ui.sh` scripts which will handle this automatically

### 8. Features

- **Drowsiness Detection**: Real-time EAR calculation and alert
- **Accident Detection**: G-sensor monitoring for impacts
- **GPS Tracking**: Location tracking (simulation or real GPS module)
- **Emergency Reporting**: Automatic SMS reporting with GPS location
- **Driving Reports**: Monthly statistics and event counts
- **Real-time Dashboard**: Live status updates via JavaFX UI

### 9. File Structure

```
iot_project_OOP/
├── main.py                 # Entry point
├── config.py              # Configuration
├── requirements.txt        # Python dependencies
├── driver_monitor/        # Python backend modules
│   ├── camera/           # Camera management
│   ├── fatigue/          # Drowsiness detection
│   ├── sensors/          # Accelerometer, GPS, Speaker
│   ├── report/           # Emergency reporting
│   ├── logging_system/   # Event logging
│   └── data_bridge.py    # UI communication
├── ui/                    # JavaFX UI
│   ├── build.gradle.kts  # Build configuration
│   └── src/main/java/... # UI source code
└── data/                  # JSON data files (created at runtime)
```

### 10. Notes

- **Both systems must run**: Python backend generates data, JavaFX UI displays it
- **Data directory**: JSON files are created in `data/` directory (or `/home/pi/iot/data` on Raspberry Pi)
- **GPS simulation**: By default, GPS runs in simulation mode. Set `GPS_ENABLED = True` for real GPS module
- **SMS reporting**: Requires SOLAPI account and API credentials in `config.py`

## License

[Your License Here]

