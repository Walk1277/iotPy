# Running JavaFX UI on Raspberry Pi

## Overview
This project is configured to run JavaFX UI on Raspberry Pi.
JavaFX supports ARM64 architecture from Java 11+.

## System Requirements

### 1. Java Installation (Raspberry Pi)
```bash
# Install OpenJDK 21 (recommended)
sudo apt update
sudo apt install openjdk-21-jdk

# Or use SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install java 21.0.1-tem
```

### 2. Verify Java Version
```bash
java -version
# Output example: openjdk version "21.0.1" ...
```

### 3. Check Architecture
```bash
uname -m
# Output: aarch64 (ARM64) or armv7l (ARM32)
```

## Build and Run

### Build from Development Environment (for Raspberry Pi)
```bash
cd ui
./gradlew build
```

### Build Directly on Raspberry Pi
```bash
cd ui
./gradlew build
./gradlew run
```

### Platform-Specific JAR Generation
Gradle automatically detects the platform and downloads the correct JavaFX native libraries:
- **Raspberry Pi 4 (64-bit)**: `linux-aarch64`
- **Raspberry Pi 3 and below (32-bit)**: `linux-arm32` (limited support in JavaFX 11+)

## JavaFX Platform Support

### Supported Platforms
- ✅ **linux-aarch64** (Raspberry Pi 4, 64-bit OS)
- ✅ **linux-x86_64** (General Linux)
- ✅ **win-x86_64** (Windows)
- ✅ **mac-aarch64** (Apple Silicon)
- ✅ **mac-x86_64** (Intel Mac)

### Notes
- **Raspberry Pi 3 and below (ARM32)**: ARM32 support in JavaFX 11+ is limited.
  - It is recommended to use Raspberry Pi 4 (64-bit) if possible.
  - Alternatively, JavaFX 8 can be used, but you won't be able to use the latest features.

## Performance Optimization

### 1. Display Settings
JavaFX on Raspberry Pi uses hardware acceleration:
```bash
# Increase GPU memory allocation (if needed)
sudo raspi-config
# Advanced Options > Memory Split > 128 (or 256)
```

### 2. Resolution Settings
The current UI is optimized for 800x480 resolution.
Performance may degrade at higher resolutions.

### 3. Run Options
```bash
# Set JVM memory limits
java -Xmx512m -Xms256m -jar app.jar

# Or run with Gradle
./gradlew run --args="-Xmx512m"
```

## Troubleshooting

### JavaFX Module Not Found
```bash
# Manually download JavaFX SDK (if needed)
# Download platform-specific SDK from https://openjfx.io/
```

### Screen Not Displaying
```bash
# Check DISPLAY environment variable
echo $DISPLAY

# Check X11 forwarding (for remote access)
export DISPLAY=:0
```

### Performance Issues
- Remove unnecessary JavaFX modules (javafx.web, javafx.media, etc.)
- Minimize animations
- Adjust update interval (currently 1 second)

## Data Path Configuration

To communicate with Python backend on Raspberry Pi:

1. Run Python backend:
```bash
cd /home/pi/iot_project_OOP
python main.py start
```

2. Check data directory:
```bash
ls -la /home/pi/iot_project_OOP/data/
# drowsiness.json, status.json files should be created
```

3. Run UI:
```bash
cd /home/pi/iot_project_OOP/ui
./gradlew run
```

## References
- [OpenJFX Official Site](https://openjfx.io/)
- [JavaFX ARM Support](https://github.com/openjdk/jfx)
- [Raspberry Pi Java Installation Guide](https://www.raspberrypi.org/documentation/computers/software.html)
