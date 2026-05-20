## Raspberry Pi Setup Requirements

### Hardware Components
- Raspberry Pi 4B (or newer)
- MPU-6050 Accelerometer (I2C)
- Neo-6M GPS Module (via UART)
- Pi Camera Module V2
- micro SD card (32GB recommended)
- USB-C power supply

### System Installation

#### 1. Flash Raspberry Pi OS
```bash
# Use Raspberry Pi Imager or balena Etcher to flash the OS to your SD card
# Recommended: Raspberry Pi OS Lite or Desktop
```

#### 2. Enable Required Interfaces
```bash
sudo raspi-config
# Go to: Interfacing Options → I2C → Enable
# Go to: Interfacing Options → Serial → Enable (for GPS)
# Go to: Interfacing Options → Camera → Enable
```

#### 3. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Python Dependencies Installation

#### Install Required Packages
```bash
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y python3-tk  # for Tkinter (GUI)
```

#### Install Python Libraries
```bash
pip install smbus2
pip install opencv-python
pip install pillow
pip install gps-python
sudo apt-get install gpsd gpsd-clients
```

### Hardware Configuration

#### I2C Setup (MPU-6050)
```bash
# Check if I2C device is detected
i2cdetect -y 1

# Should show: 68 (MPU-6050 I2C address)
```

#### GPS Setup (Neo-6M)
```bash
# Start gpsd service
sudo systemctl start gpsd
sudo systemctl enable gpsd  # Auto-start on reboot

# Test GPS connection
gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
gpsctl -s 9600 /dev/ttyAMA0
```

#### Camera Setup
```bash
# Test camera
raspistill -o test.jpg

# Check camera permissions
ls -la /dev/video0
```

### Running the Application

```bash
# Navigate to project directory
cd ~/smart-helmet

# Run the main dashboard
python3 dashboard.py

# Or run individual modules
python3 bump_detection.py
python3 gps_zone.py
python3 rear_camera.py
```

### Troubleshooting

**I2C not detected:**
```bash
sudo i2cdetect -y 1
# If no devices found, check wiring and power
```

**GPS not connecting:**
```bash
# Check if gpsd is running
ps aux | grep gpsd

# Manually test
python3 -c "import gps; g = gps.gps(); print(g.read())"
```

**Camera not opening:**
```bash
# Test camera detection
vcgencmd get_camera
# Should show: supported=1 detected=1