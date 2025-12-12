# Smart Accident Prevention Kit - Complete Features Documentation

## Table of Contents
1. [Overview](#overview)
2. [Core Features](#core-features)
3. [Drowsiness Detection](#drowsiness-detection)
4. [Accident Detection & Auto-Report](#accident-detection--auto-report)
5. [GPS-Based Driving Detection](#gps-based-driving-detection)
6. [Speaker Control System](#speaker-control-system)
7. [User Interface (JavaFX)](#user-interface-javafx)
8. [System Check & Diagnostics](#system-check--diagnostics)
9. [Settings & Configuration](#settings--configuration)
10. [Data Logging & Reports](#data-logging--reports)
11. [Technical Specifications](#technical-specifications)

---

## Overview

The Smart Accident Prevention Kit is a comprehensive driver monitoring system that combines computer vision, sensor data, and real-time alerts to prevent accidents and automatically report emergencies. The system consists of a Python backend for sensor processing and a JavaFX UI for user interaction.

### System Architecture
- **Backend**: Python 3.x with OpenCV, MediaPipe, and sensor libraries
- **Frontend**: JavaFX 17.0.2 (ARM-compatible for Raspberry Pi)
- **Communication**: JSON-based file communication between backend and UI
- **Platform**: Raspberry Pi with 800x440 touchscreen display

---

## Core Features

### 1. Real-time Driver Monitoring
- Continuous face detection and eye tracking
- Drowsiness detection using Eye Aspect Ratio (EAR)
- Accelerometer-based impact detection
- GPS-based location tracking

### 2. Multi-modal Alert System
- Visual alerts on UI
- Audio alerts via speaker
- SMS emergency reporting
- Touch-screen interaction for response

### 3. Intelligent Response System
- GPS-based driving state detection
- Context-aware speaker activation
- Automatic emergency reporting
- User response handling

---

## Drowsiness Detection

### Detection Algorithm
- **Method**: Eye Aspect Ratio (EAR) calculation using facial landmarks
- **Threshold**: Configurable `EAR_THRESHOLD` (default: 0.200188679245283)
- **Consecutive Frames**: 30 frames (approximately 1 second at 30 FPS)
- **Facial Landmarks**: MediaPipe Face Mesh (468 points)

### Detection Process
1. **Face Detection**: MediaPipe detects face in camera frame
2. **Landmark Extraction**: Extracts eye region landmarks (left and right eyes)
3. **EAR Calculation**: Computes Eye Aspect Ratio for both eyes
4. **Threshold Comparison**: Compares average EAR to threshold
5. **State Determination**: 
   - EAR < threshold for 30+ consecutive frames → Drowsiness detected
   - EAR >= threshold → Normal state

### Configuration
- **File**: `config.py`
- **Parameters**:
  - `EAR_THRESHOLD`: Drowsiness detection threshold (float)
  - `CONSEC_FRAMES`: Number of consecutive frames for detection (int)
  - `LEFT_EYE_IDXS`: Left eye landmark indices
  - `RIGHT_EYE_IDXS`: Right eye landmark indices

### Logging
- Event logged to `driving_events.log` when drowsiness is detected
- Timestamp and EAR value recorded

---

## Accident Detection & Auto-Report

### Detection Logic

#### Step 1: Impact Detection
- **Sensor**: ADXL345 Accelerometer
- **Threshold**: `ACCEL_THRESHOLD = 2.0` m/s²
- **Events Detected**:
  - Sudden acceleration (positive X-axis > threshold)
  - Sudden stop (negative X-axis < -threshold)

#### Step 2: Post-Impact Monitoring
- **Duration**: 1 minute (`REPORT_IMPACT_MONITORING_DURATION = 60.0` seconds)
- **Conditions Checked** (within 1 minute after impact):
  1. **Eyes Closed**: EAR < threshold for 10+ seconds (`REPORT_EYES_CLOSED_DURATION`)
  2. **No Face Detected**: Face not detected for 10+ seconds (`REPORT_NO_FACE_DURATION`)

#### Step 3: Alert & Response
- **Alert Trigger**: When either condition is met, system enters `ALERT` state
- **Response Timeout**: 10 seconds (`REPORT_RESPONSE_TIMEOUT`)
- **User Response Options**:
  - Touch screen on UI popup
  - Press any keyboard key (if monitor window is shown)
- **Response File**: `user_response.json` created when user touches screen

#### Step 4: Automatic Reporting
- **Trigger**: No user response within 10 seconds
- **Action**: Automatic SMS report sent via SOLAPI
- **SMS Content**:
  - Emergency message header
  - Timestamp
  - Impact detection time
  - GPS location (latitude, longitude)
  - Google Maps link
  - Status description

### UI Popup (ResponseRequestModal)
- **Display**: Full-screen modal overlay
- **Features**:
  - Warning icon (⚠️)
  - "ACCIDENT DETECTED!" title
  - Countdown timer (10 seconds)
  - "TOUCH THE SCREEN TO CANCEL REPORT" instruction
  - Real-time countdown updates
  - Color changes based on remaining time (red when < 3 seconds)

### Automatic SMS Report
- **Service**: SOLAPI (Korean SMS service)
- **Configuration**: `config.py`
  - `SMS_API_KEY`: SOLAPI API key
  - `SMS_API_SECRET`: SOLAPI API secret
  - `SMS_FROM_NUMBER`: Sender phone number (registered with SOLAPI)
  - `SMS_TO_NUMBER`: Receiver phone number
  - `SMS_ENABLED`: Enable/disable SMS reporting
- **Message Format**:
  ```
  [EMERGENCY REPORT] Driver Monitoring System
  Time: YYYY-MM-DD HH:MM:SS
  Impact detected: HH:MM:SS
  Location: Latitude: XX.XXXXXX, Longitude: XX.XXXXXX
  Map: https://maps.google.com/?q=lat,lon
  Status: Eyes closed or no face detected for 10+ seconds within 1 minute after impact
  No user response. Emergency situation detected. Reporting now.
  ```

### File Communication
- **User Response**: `user_response.json`
  - Created by JavaFX UI when user touches screen
  - Contains: `{"responded": true, "timestamp": "..."}`
  - Read by Python backend and deleted after processing
- **Response Paths**:
  - `/home/pi/iot/data/user_response.json` (Raspberry Pi)
  - `data/user_response.json` (Development)

---

## GPS-Based Driving Detection

### Purpose
Determine if the vehicle is currently driving to enable context-aware alerts.

### Detection Method
- **Sensor**: GPS module (real or simulated)
- **Threshold**: `DRIVING_SPEED_THRESHOLD = 5.0` km/h
- **Logic**: 
  - Speed >= 5.0 km/h → Driving
  - Speed < 5.0 km/h → Not driving (parked)

### GPS Configuration
- **File**: `config.py`
- **Parameters**:
  - `GPS_ENABLED`: Enable/disable GPS module
  - `GPS_SERIAL_PORT`: Serial port for GPS module (`/dev/ttyUSB0`)
  - `GPS_BAUD_RATE`: Baud rate (9600)
- **Simulation Mode**: 
  - Used when GPS module not available
  - Default location: Seoul, South Korea (37.5665, 126.9780)
  - Simulated speed: 0-30 km/h (sine wave pattern)

### Usage
- Determines speaker activation conditions
- Context-aware alert system
- Location tracking for emergency reports

---

## Speaker Control System

### Activation Conditions

#### When Driving:
1. **Drowsiness Detected** → Speaker activates **immediately**
2. **No Face Detected** → Speaker activates after **10 seconds** (`NO_FACE_WHILE_DRIVING_TIMEOUT`)

#### When Not Driving:
- **Drowsiness Detected** → Speaker **does NOT activate** (UI alert only)
- **No Face Detected** → Speaker **does NOT activate** (parked state)

#### Accident Detection:
- **Speaker does NOT activate** (UI popup only, no audio alert)

### Speaker Stop Popup
- **Trigger**: Speaker active for 1+ seconds
- **Display**: JavaFX Alert dialog
- **Message**: "The alarm speaker has been active for X.X seconds. Click OK to stop the speaker."
- **Action**: User clicks OK → `stop_speaker.json` file created → Backend stops speaker
- **File Communication**: `stop_speaker.json` (same paths as `user_response.json`)

### Speaker Control Flow
1. **Activation**: 
   - Drowsiness detected while driving → `alarm_start_time` set
   - No face for 10+ seconds while driving → `alarm_start_time` set
2. **Duration Tracking**: 
   - `alarm_duration` calculated from `alarm_start_time`
   - If duration >= 1.0 seconds → `show_speaker_popup = True`
3. **UI Popup**: 
   - JavaFX shows Alert dialog after 1 second
   - User can stop speaker via OK button
4. **Deactivation**:
   - User stops via UI popup
   - Drowsiness condition no longer met
   - Vehicle stops driving (speed < threshold)

### Configuration
- **File**: `config.py`
- **Parameters**:
  - `NO_FACE_WHILE_DRIVING_TIMEOUT = 10.0` seconds
  - `DRIVING_SPEED_THRESHOLD = 5.0` km/h

---

## User Interface (JavaFX)

### Main Screen (800x440 pixels)
2x2 grid layout with 4 main panels:

#### 1. Current Status Panel (Top-Left)
- **Displays**: Real-time driver status
- **States**:
  - "Good" (green) - Normal driving
  - "Alert" (red) - Drowsiness detected
  - "Waiting" (gray) - Checking camera
- **Updates**: Every 1 second from `drowsiness.json`

#### 2. Driving Score Panel (Top-Right)
- **Displays**: Monthly driving score (0-100 points)
- **Calculation**:
  - Starts at 100 points
  - Deducts 5 points per event:
    - Drowsiness detection
    - Sudden acceleration
    - Sudden stop
- **Updates**: Every 1 second from `log_summary.json`

#### 3. Accident Detection Panel (Bottom-Left)
- **Displays**: 
  - Accident status ("No Accident" / "Accident Detected!" / "Response Required!")
  - G-sensor value (in G units)
- **Updates**: Every 1 second from `status.json`
- **Click Action**: Navigate to detailed accident detection screen

#### 4. Settings & Log Check Panel (Bottom-Right)
- **Settings Button**: Navigate to settings menu
- **Log Check Area**: Shows recent driving events
- **Refresh Button**: Reload log data
- **Click Action**: Navigate to detailed log screen

### Detailed Screens

#### Status Screen
- Real-time camera status
- EAR value display
- Threshold comparison
- Face detection status

#### Driving Report Screen
- Monthly score chart (LineChart)
- Daily scores (BarChart)
- Event statistics:
  - Total events
  - Drowsiness count
  - Sudden acceleration count
  - Sudden stop count
- Report statistics:
  - Alert triggered count
  - Report triggered count
  - Report cancelled count
  - SMS sent count

#### Accident Detection Screen
- G-sensor value
- Impact detection status
- GPS position
- Test button (for testing accident detection)

#### Settings Screen
Multiple sub-screens:

##### Personal Settings
- User information (placeholder for future use)

##### Drowsiness Settings
- EAR Threshold adjustment
- Real-time threshold update
- Save to `config.py`

##### Auto Report Settings
- Sender phone number (`SMS_FROM_NUMBER`)
- Receiver phone number (`SMS_TO_NUMBER`)
- Auto report enable/disable checkbox
- Save to `config.py`

##### System Check
- Camera test
- Accelerometer test
- GPS test (with real signal detection)
- Speaker test
- SMS test (sends actual test message with GPS data)
- Results displayed with status icons (✅ OK, ⚠️ WARNING, ❌ ERROR)

#### Log Screen
- Scrollable log viewer
- Displays recent driving events from `driving_events.log`
- Auto-refresh capability
- Event filtering

#### Update Screen
- System update functionality
- Runs `update_system.sh` script
- Updates Python packages from `requirements.txt`

### Popup Modals

#### Accident Response Request Modal
- **Trigger**: Accident detected (impact + eyes closed/no face)
- **Display**: Full-screen overlay
- **Features**:
  - Warning icon
  - "ACCIDENT DETECTED!" title
  - Countdown timer (10 seconds)
  - Touch instruction
  - Real-time countdown updates
- **Action**: User touches screen → `user_response.json` created → Report cancelled

#### Speaker Stop Alert
- **Trigger**: Speaker active for 1+ seconds
- **Display**: JavaFX Alert dialog
- **Features**:
  - Warning type alert
  - Duration display
  - OK button to stop speaker
- **Action**: User clicks OK → `stop_speaker.json` created → Speaker stopped

### Data Update System
- **Update Frequency**: Every 1 second
- **Data Sources**:
  - `drowsiness.json` - Drowsiness status
  - `status.json` - System status and accident detection
  - `log_summary.json` - Driving score and statistics
- **Update Mechanism**: `DataUpdater` class with `Timeline` (JavaFX)

### Navigation System
- **Screen Navigator**: `ScreenNavigator` class manages screen transitions
- **Back Navigation**: All detailed screens have back button
- **Stack-based**: Uses `StackPane` for screen management

---

## System Check & Diagnostics

### System Check Script
- **File**: `check_system.py`
- **Purpose**: Verify all system components are working correctly
- **Tests Performed**:

#### 1. Camera Test
- Initializes camera
- Captures test frame
- Verifies resolution
- Returns: Status, message, details (resolution)

#### 2. Accelerometer Test
- Initializes ADXL345 sensor
- Reads accelerometer data (X, Y, Z)
- Verifies sensor connection
- Returns: Status, message, details (X, Y, Z values in m/s²)

#### 3. GPS Test
- Initializes GPS module
- Reads GPS data multiple times (10 attempts)
- Detects real signal vs. simulation
- Checks for default simulation position
- Returns: Status, message, details (latitude, longitude)

#### 4. Speaker Test
- Initializes speaker controller
- Plays test alarm (0.1 seconds)
- Verifies audio output
- Returns: Status, message, details

#### 5. SMS Test
- Initializes SMS service (SOLAPI)
- Verifies API credentials
- Sends actual test SMS message
- Includes GPS location in message
- Returns: Status, message, details (message ID, receiver)

### Test Output Format
```json
{
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "checks": {
    "camera": {
      "status": "OK|WARNING|ERROR",
      "message": "...",
      "details": "..."
    },
    "accelerometer": {...},
    "gps": {...},
    "speaker": {...},
    "sms": {...}
  }
}
```

### Status Types
- **OK**: Component working normally
- **WARNING**: Component available but not optimal (e.g., GPS simulation mode)
- **ERROR**: Component not working or not available

### Access from UI
- Settings → System Check
- Real-time test execution
- Results displayed with color-coded status icons

---

## Settings & Configuration

### Configuration File
- **File**: `config.py`
- **Location**: Project root directory
- **Dynamic Reloading**: Configuration values are reloaded at runtime using `importlib.reload()`

### Configurable Parameters

#### Drowsiness Detection
- `EAR_THRESHOLD`: Eye Aspect Ratio threshold (default: 0.200188679245283)
- `CONSEC_FRAMES`: Consecutive frames for detection (default: 30)

#### Accelerometer
- `ACCEL_THRESHOLD`: Impact detection threshold in m/s² (default: 2.0)

#### Report System
- `REPORT_IMPACT_MONITORING_DURATION`: Monitoring period after impact in seconds (default: 60.0)
- `REPORT_EYES_CLOSED_DURATION`: Eyes closed duration for alert in seconds (default: 10.0)
- `REPORT_NO_FACE_DURATION`: No face duration for alert in seconds (default: 10.0)
- `REPORT_RESPONSE_TIMEOUT`: User response timeout in seconds (default: 10.0)
- `AUTO_REPORT_ENABLED`: Enable/disable automatic reporting (default: True)

#### SMS Reporting (SOLAPI)
- `SMS_API_KEY`: SOLAPI API key
- `SMS_API_SECRET`: SOLAPI API secret
- `SMS_FROM_NUMBER`: Sender phone number (must be registered with SOLAPI)
- `SMS_TO_NUMBER`: Receiver phone number
- `SMS_ENABLED`: Enable/disable SMS reporting (default: True)

#### GPS
- `GPS_ENABLED`: Enable/disable GPS module (default: True)
- `GPS_SERIAL_PORT`: GPS serial port path (default: "/dev/ttyUSB0")
- `GPS_BAUD_RATE`: GPS baud rate (default: 9600)
- `DRIVING_SPEED_THRESHOLD`: Speed threshold for driving detection in km/h (default: 5.0)
- `NO_FACE_WHILE_DRIVING_TIMEOUT`: Timeout before speaker activation when no face detected while driving in seconds (default: 10.0)

#### Camera
- `CAM_WIDTH`: Camera width in pixels (default: 800)
- `CAM_HEIGHT`: Camera height in pixels (default: 480)

#### Logging
- `LOG_FILE`: Driving events log file name (default: "driving_events.log")

### Settings UI Features

#### Drowsiness Settings
- **EAR Threshold Input**: Text field for threshold value
- **Real-time Update**: Changes applied immediately via `update_config.py`
- **Save Button**: Saves to `config.py`

#### Auto Report Settings
- **Sender Phone Number**: Input field for `SMS_FROM_NUMBER`
- **Receiver Phone Number**: Input field for `SMS_TO_NUMBER`
- **Auto Report Enable**: Checkbox for `AUTO_REPORT_ENABLED`
- **Save Button**: Saves all values to `config.py`

#### System Log Reset
- **Button**: "Reset System Logs"
- **Action**: 
  - Clears `driving_events.log`
  - Resets `log_summary.json` to default state (100 score, 0 events)
  - Uses `clear_logs.py` script

### Configuration Update Script
- **File**: `update_config.py`
- **Function**: Programmatically updates `config.py` values
- **Usage**: Called from JavaFX UI when settings are saved
- **Method**: String replacement in `config.py` file

---

## Data Logging & Reports

### Event Logging
- **File**: `driving_events.log`
- **Format**: CSV with headers
- **Columns**: Timestamp, EventType
- **Event Types**:
  - `drowsiness`: Drowsiness detected
  - `sudden acceleration`: Sudden acceleration detected
  - `sudden stop`: Sudden stop detected
  - `report_alert_triggered`: Accident alert triggered
  - `report_triggered`: Automatic report initiated
  - `report_cancelled`: User cancelled report
  - `sms_report_sent`: SMS report sent successfully
  - `sms_report_failed`: SMS report failed
  - `emergency`: Emergency situation (legacy)
  - `Start program`: System started
  - `program quit`: System stopped

### Log Summary
- **File**: `log_summary.json`
- **Update Frequency**: Every 2 seconds (60 frames at 30 FPS)
- **Contents**:
  ```json
  {
    "total_events": 0,
    "drowsiness_count": 0,
    "sudden_acceleration_count": 0,
    "sudden_stop_count": 0,
    "monthly_score": 100,
    "daily_scores": [
      {
        "date": "YYYY-MM-DD",
        "score": 100,
        "day": DD
      }
    ],
    "event_counts": {
      "sudden_stop": 0,
      "sudden_acceleration": 0,
      "drowsiness": 0
    },
    "report_stats": {
      "alert_triggered": 0,
      "report_triggered": 0,
      "report_cancelled": 0,
      "sms_sent": 0
    }
  }
  ```

### Driving Score Calculation
- **Base Score**: 100 points
- **Deduction**: 5 points per event
- **Event Types Counted**:
  - Drowsiness detection
  - Sudden acceleration
  - Sudden stop
- **Excluded Events**: System events (Start program, program quit, etc.)
- **Formula**: `score = max(0, 100 - (total_events * 5))`

### Daily Scores
- Calculated per day from log data
- Each day starts at 100 points
- Deducts 5 points per event on that day
- Displayed as bar chart in UI

### Log Parser
- **File**: `driver_monitor/logging_system/log_parser.py`
- **Function**: Parses `driving_events.log` into pandas DataFrame
- **Methods**:
  - `load_recent_days(days=30)`: Loads last N days of events
  - Filters and processes event data
  - Calculates statistics

### Log Clearing
- **Script**: `clear_logs.py`
- **Function**: 
  - Clears all events from `driving_events.log`
  - Resets `log_summary.json` to default state
- **Access**: Settings → System Log Reset button

---

## Technical Specifications

### Backend Architecture

#### Main Components
1. **DriverMonitor** (`driver_monitor.py`)
   - Main monitoring loop
   - Coordinates all subsystems
   - Handles frame processing

2. **FatigueDetector** (`fatigue/fatigue_detector.py`)
   - Face detection using MediaPipe
   - EAR calculation
   - Drowsiness state determination

3. **AccelerometerDetector** (`sensors/accelerometer_detector.py`)
   - ADXL345 accelerometer interface
   - Impact detection (sudden acceleration/stop)
   - Event logging

4. **GPSManager** (`sensors/gps_manager.py`)
   - GPS module interface (serial/UART)
   - Position and speed reading
   - Simulation mode support

5. **SpeakerController** (`sensors/speaker_controller.py`)
   - GPIO-based speaker control
   - PWM signal generation
   - Alarm on/off control

6. **ReportManager** (`report/report_manager.py`)
   - Accident detection logic
   - Post-impact monitoring
   - SMS report sending
   - User response handling

7. **DataBridge** (`data_bridge.py`)
   - JSON file generation for UI
   - Real-time status updates
   - Log summary generation

8. **EventLogger** (`logging_system/event_logger.py`)
   - Event logging to CSV file
   - Timestamp management

### Frontend Architecture

#### Main Components
1. **MainApplication** (`MainApplication.java`)
   - JavaFX application entry point
   - Stage and scene setup
   - Data update timeline

2. **MainScreenController** (`MainScreenController.java`)
   - Main dashboard management
   - Panel creation and updates
   - Popup modal management

3. **DataUpdater** (`DataUpdater.java`)
   - Periodic data updates (1 second interval)
   - JSON file reading
   - UI state updates

4. **Screen Controllers** (`controllers/`)
   - `StatusScreenController`: Status details
   - `ReportScreenController`: Driving report with charts
   - `AccidentScreenController`: Accident detection details
   - `SettingsScreenController`: All settings screens
   - `LogScreenController`: Log viewer
   - `UpdateScreenController`: System update

5. **ResponseRequestModal** (`ResponseRequestModal.java`)
   - Full-screen accident response modal
   - Countdown timer
   - Touch interaction

6. **Data Loaders**
   - `StatusDataLoader`: Loads `status.json`
   - `JsonDataLoader`: Generic JSON loader with multiple path support

### Data Communication

#### JSON Files
1. **drowsiness.json**
   - Location: `data/drowsiness.json` or `/home/pi/iot/data/drowsiness.json`
   - Contents:
     ```json
     {
       "ear": 0.25,
       "threshold": 0.2,
       "state": "normal|sleepy|no_face",
       "timestamp": "YYYY-MM-DD HH:MM:SS",
       "face_detected": true,
       "alarm_on": false,
       "alarm_duration": 0.0,
       "show_speaker_popup": false
     }
     ```

2. **status.json**
   - Location: `data/status.json` or `/home/pi/iot/data/status.json`
   - Contents:
     ```json
     {
       "connection_status": "OK",
       "sensor_status": "...",
       "accel_magnitude": 1.0,
       "accel_data": {"x": 0.0, "y": 0.0, "z": 0.0},
       "gps_position": {"latitude": 37.5665, "longitude": 126.9780},
       "gps_position_string": "(37.5665, 126.9780)",
       "impact_detected": false,
       "report_status": {
         "status": "NORMAL|ALERT|REPORTING",
         "message": "...",
         "remaining_time": 0.0
       },
       "response_requested": false,
       "response_message": "",
       "response_remaining_time": 0.0,
       "timestamp": "YYYY-MM-DD HH:MM:SS"
     }
     ```

3. **log_summary.json**
   - Location: `data/log_summary.json` or `/home/pi/iot/data/log_summary.json`
   - Contents: (See Data Logging & Reports section)

#### Response Files (UI → Backend)
1. **user_response.json**
   - Created when user touches accident response modal
   - Contents: `{"responded": true, "timestamp": "..."}`
   - Read by backend and deleted after processing

2. **stop_speaker.json**
   - Created when user clicks OK on speaker stop alert
   - Contents: `{"stop": true, "timestamp": "..."}`
   - Read by backend and deleted after processing

### File Paths
- **Raspberry Pi**: `/home/pi/iot/data/`
- **Development**: `data/` (relative to project root)
- **Fallback**: Multiple paths tried in order

### Build System
- **Gradle**: 8.10.2
- **Java**: 21.0.9
- **JavaFX**: 17.0.2 (ARM-compatible)
- **Build File**: `ui/build.gradle.kts`
- **Main Class**: `org.example.iotprojectui.MainApplication`

### Dependencies

#### Python
- `opencv-python`: Computer vision
- `mediapipe`: Face detection and landmarks
- `pandas`: Data analysis
- `solapi`: SMS service (SOLAPI)
- `pynmea2`: GPS NMEA parsing
- `adafruit-circuitpython-adxl34x`: Accelerometer interface
- `RPi.GPIO`: GPIO control (Raspberry Pi)

#### Java
- JavaFX 17.0.2 (controls, fxml)
- Jackson (JSON parsing)
- Gradle wrapper

### Performance
- **Frame Rate**: ~30 FPS (camera dependent)
- **UI Update Rate**: 1 second
- **Log Summary Update**: Every 2 seconds (60 frames)
- **GPS Update**: Every frame (if available)

### Error Handling
- **Camera Errors**: Graceful fallback, error logging
- **Sensor Errors**: Simulation mode or warning status
- **GPS Errors**: Simulation mode with default location
- **SMS Errors**: Error logging, no system crash
- **File I/O Errors**: Multiple path fallbacks

### Security Considerations
- **API Keys**: Stored in `config.py` (should be secured in production)
- **Phone Numbers**: Stored in `config.py`
- **Log Files**: May contain sensitive location data
- **File Permissions**: Data directory permissions handled automatically

---

## Feature Summary Table

| Feature | Condition | Action | Priority |
|---------|-----------|--------|----------|
| Drowsiness Detection | EAR < threshold for 30 frames | Log event, activate speaker (if driving) | High |
| No Face While Driving | No face for 10+ seconds while driving | Activate speaker after timeout | High |
| Accident Detection | Impact + (eyes closed OR no face) for 10+ seconds | Show UI popup, wait 10s for response | Critical |
| Auto Report | No response to accident popup within 10s | Send SMS with GPS location | Critical |
| Speaker (Driving + Drowsy) | Driving + drowsiness detected | Activate immediately | High |
| Speaker (Driving + No Face) | Driving + no face for 10s | Activate after timeout | High |
| Speaker (Not Driving) | Not driving | Do NOT activate | Medium |
| Speaker (Accident) | Accident detected | Do NOT activate | Low |
| Speaker Stop Popup | Speaker active for 1+ seconds | Show popup, allow user to stop | Medium |
| System Check | User initiated | Test all components | Medium |
| Settings Save | User changes settings | Update config.py | Medium |
| Log Reset | User initiated | Clear logs, reset score | Low |

---

## Workflow Diagrams

### Drowsiness Detection Workflow
```
Camera Frame → Face Detection → EAR Calculation → Threshold Comparison
    ↓
EAR < Threshold for 30 frames?
    ↓ Yes
Drowsiness Detected
    ↓
Check Driving Status
    ↓
Driving? → Yes → Activate Speaker → Show UI Alert
    ↓ No
Show UI Alert Only (No Speaker)
```

### Accident Detection & Auto-Report Workflow
```
Accelerometer Event (Impact)
    ↓
Register Impact → Start 1-minute monitoring
    ↓
Within 1 minute:
    - Eyes closed for 10+ seconds? OR
    - No face for 10+ seconds?
    ↓ Yes
Enter ALERT State → Show UI Popup
    ↓
Wait 10 seconds for user response
    ↓
User Response? (Touch screen or keyboard)
    ↓ Yes                    ↓ No
Cancel Report          Timeout (10s)
    ↓                        ↓
Normal State          Send SMS Report
                       → REPORTING State
```

### Speaker Activation Workflow
```
Check Conditions:
1. Drowsiness detected?
2. No face while driving?
3. Driving status?
    ↓
Driving + Drowsiness → Activate Speaker Immediately
    ↓
Driving + No Face (10s) → Activate Speaker
    ↓
Not Driving → Do NOT Activate
    ↓
Speaker Active for 1+ seconds?
    ↓ Yes
Show Stop Popup → User Clicks OK → Stop Speaker
```

---

## Configuration Examples

### Example: Adjusting Drowsiness Sensitivity
```python
# config.py
EAR_THRESHOLD = 0.25  # More sensitive (detects earlier)
EAR_THRESHOLD = 0.15  # Less sensitive (detects later)
```

### Example: Changing Response Timeout
```python
# config.py
REPORT_RESPONSE_TIMEOUT = 15.0  # 15 seconds instead of 10
```

### Example: Disabling SMS Reporting
```python
# config.py
SMS_ENABLED = False  # Disable SMS, but keep other features
```

### Example: Adjusting Driving Speed Threshold
```python
# config.py
DRIVING_SPEED_THRESHOLD = 10.0  # 10 km/h instead of 5 km/h
```

---

## Troubleshooting

### Common Issues

#### 1. Camera Not Detected
- **Symptom**: "Camera initialization failed"
- **Solution**: Check camera connection, verify device index (usually 0)

#### 2. GPS Not Working
- **Symptom**: GPS shows simulation mode
- **Solution**: 
  - Check GPS module connection
  - Verify serial port (`/dev/ttyUSB0`)
  - Set `GPS_ENABLED = True` in config.py

#### 3. SMS Not Sending
- **Symptom**: "SMS service initialization failed"
- **Solution**:
  - Install `solapi`: `pip3 install solapi`
  - Verify API keys in `config.py`
  - Check SOLAPI account balance
  - Verify phone numbers are registered

#### 4. Speaker Not Working
- **Symptom**: No sound output
- **Solution**:
  - Check GPIO pin connection (default: pin 21)
  - Verify speaker hardware
  - Check if running on Raspberry Pi (GPIO only works on RPi)

#### 5. UI Not Updating
- **Symptom**: UI shows stale data
- **Solution**:
  - Check JSON file paths
  - Verify data directory permissions
  - Check backend is running and writing JSON files

#### 6. Accident Popup Not Showing
- **Symptom**: Accident detected but no popup
- **Solution**:
  - Check `response_requested` in `status.json`
  - Verify UI is reading `status.json` correctly
  - Check for popup conflicts (speaker alert may block it)
  - Review debug logs in console

---

## Future Enhancements

### Potential Improvements
1. **Machine Learning**: Train custom drowsiness detection model
2. **Cloud Integration**: Upload logs and reports to cloud storage
3. **Mobile App**: Companion mobile app for remote monitoring
4. **Voice Alerts**: Text-to-speech alerts
5. **Multi-language Support**: Internationalization
6. **Advanced Analytics**: Machine learning-based driving pattern analysis
7. **Integration**: Connect with vehicle OBD-II system
8. **Real-time Streaming**: Stream camera feed to remote server

---

## Version Information
- **Last Updated**: 2025-12-12
- **Python Version**: 3.x
- **Java Version**: 21.0.9
- **JavaFX Version**: 17.0.2
- **Gradle Version**: 8.10.2
- **Platform**: Raspberry Pi (ARM) / Linux

---

## Contact & Support
For issues, questions, or contributions, please refer to the main README.md file.

