# 🐧 Linux Automated Setup Guide

## Complete Linux Environment Setup Script

This document explains the `setup-linux.py` script - a comprehensive automated setup tool for Linux systems that configures the entire Airguard ESP32 IoT environment.

---

## 🎯 What It Does

The `setup-linux.py` script automates **everything** needed to get your Linux machine ready to work with ESP32 devices:

### ✅ Automated Tasks

1. **System Dependency Detection & Installation**
   - Detects Linux distribution (Ubuntu, Debian, Fedora, Arch)
   - Installs Node.js 18+, Python 3.9+, MongoDB, Git
   - Configures package repositories automatically

2. **Serial Port Detection & Configuration**
   - Scans all USB/serial ports
   - Identifies ESP32 devices (CP2102, CH340, FTDI)
   - Tests ports to distinguish sender vs receiver
   - Interactive selection if auto-detection fails

3. **Environment File Creation**
   - Generates `.env` files for all services
   - Configures correct serial port automatically
   - Sets up MongoDB, MQTT, API endpoints

4. **Python Environment Setup**
   - Creates virtual environment
   - Installs all Python dependencies
   - Configures gateway service

5. **Node.js Dependency Installation**
   - Installs npm packages for MQTT broker
   - Installs npm packages for Node backend
   - Installs npm packages for MQTT-MongoDB bridge

6. **MongoDB Configuration**
   - Starts MongoDB service
   - Enables auto-start on boot
   - Tests database connection

7. **Hardware Testing**
   - Verifies ESP32 connectivity
   - Tests serial communication
   - Validates firmware responses

8. **Startup Script Creation**
   - Creates `start-airguard.sh`
   - Creates `stop-airguard.sh`
   - Sets executable permissions

9. **System Health Check**
   - Validates all components
   - Reports configuration status
   - Provides troubleshooting guidance

---

## 📋 Prerequisites

### Before Running the Script

**Hardware:**
- ESP32 sender with firmware uploaded ✅
- ESP32 receiver with firmware uploaded ✅
- Both connected via USB

**Software:**
- Fresh Linux installation (Ubuntu 20.04+, Debian 11+, Fedora 35+, or Arch)
- Internet connection
- sudo privileges

**That's it!** The script handles everything else.

---

## 🚀 Usage

### Quick Start (Recommended)

```bash
# 1. Download or clone the repository
git clone https://github.com/ryankyrillos/airguard-esp32-iot.git
cd airguard-esp32-iot

# 2. Switch to feature branch
git checkout feature/enhancements

# 3. Run the setup script with sudo
sudo python3 setup-linux.py
```

### Alternative: Without sudo (Limited)

If you don't have sudo access, you can run without it, but you'll need to:
- Manually install system dependencies
- Be in the `dialout` group for serial access

```bash
python3 setup-linux.py
```

---

## 📖 Step-by-Step Walkthrough

### Step 1: System Analysis

The script will:
```
🔍 Detecting system...
✓ Detected: Ubuntu 22.04 LTS (ubuntu)
✓ Running as root - full installation available
```

### Step 2: Dependency Installation

```
📦 Installing System Dependencies
ℹ Updating package lists...
ℹ Installing Node.js 18 LTS...
ℹ Installing MongoDB 6.0...
ℹ Installing base packages...
✓ System dependencies installed
```

**Supported Distributions:**
- **Ubuntu/Debian**: Uses apt, installs from official repos
- **Fedora**: Uses dnf
- **Arch**: Uses pacman

### Step 3: Dependency Verification

```
🔍 Verifying Dependencies
✓ Python 3.10.6 found
✓ Node.js 18.17.0 found
✓ npm 9.6.7 found
✓ MongoDB found
✓ Git 2.34.1 found
```

### Step 4: Serial Port Detection

```
🔌 Detecting Serial Ports
ℹ Found: /dev/ttyUSB0
  Description: CP2102 USB to UART Bridge Controller
  Hardware ID: USB VID:PID=10C4:EA60
  Type: ESP32 (CP2102)

ℹ Found: /dev/ttyUSB1
  Description: CP2102 USB to UART Bridge Controller
  Hardware ID: USB VID:PID=10C4:EA60
  Type: ESP32 (CP2102)
```

### Step 5: Port Testing & Identification

The script reads from each port for 5 seconds to identify devices:

```
ℹ Testing /dev/ttyUSB0...
  → [INIT] ESP-NOW receiver ready
  → MAC Address: 48:CA:43:9A:48:D0
  → Waiting for data...
✓ Identified receiver on /dev/ttyUSB0

ℹ Testing /dev/ttyUSB1...
  → [INIT] ESP-NOW initialized
  → [GPS] Searching for satellites...
  → [MPU] MPU6050 initialized
ℹ This appears to be the sender
```

**Interactive Selection** (if auto-detection fails):
```
⚠ Could not automatically identify receiver
ℹ Please select the receiver port:
  1. /dev/ttyUSB0 (unknown) - ✓ Responsive
  2. /dev/ttyUSB1 (unknown) - ✓ Responsive

Enter choice (1-2): 1
```

### Step 6: Environment File Creation

```
📝 Creating Environment Files
✓ Created host/python-gateway/.env
✓ Created host/node-backend/.env
✓ Created bridges/mqtt-mongo/.env
```

**Generated `.env` files contain:**
- Serial port: `/dev/ttyUSB0`
- Baud rate: `115200`
- MongoDB URI: `mongodb://localhost:27017/airguard`
- MQTT broker: `mqtt://localhost:1883`
- API endpoints: `http://localhost:8080`

### Step 7: Python Environment Setup

```
🐍 Setting Up Python Environment
ℹ Creating virtual environment...
✓ Virtual environment created
ℹ Installing Python dependencies...
✓ Python dependencies installed
✓ Script dependencies installed
```

### Step 8: Node.js Dependencies

```
📦 Installing Node.js Dependencies
ℹ Installing dependencies for mqtt-broker...
✓ Dependencies installed for mqtt-broker
ℹ Installing dependencies for host/node-backend...
✓ Dependencies installed for host/node-backend
ℹ Installing dependencies for bridges/mqtt-mongo...
✓ Dependencies installed for bridges/mqtt-mongo
```

### Step 9: MongoDB Configuration

```
🗄️ Configuring MongoDB
ℹ Starting MongoDB service...
✓ MongoDB started via systemd
✓ MongoDB connection successful
```

### Step 10: User Permissions

```
👤 Configuring Serial Port Permissions
ℹ Adding your_username to dialout group...
✓ User added to dialout group
⚠ You need to log out and log back in for this to take effect!
ℹ Or run: newgrp dialout
```

### Step 11: Startup Scripts

```
📜 Creating Startup Scripts
✓ Created start-airguard.sh
✓ Created stop-airguard.sh
```

### Step 12: Health Check

```
🏥 Running System Health Check
✓ MongoDB connection successful
✓ Python virtual environment exists
✓ All Node.js dependencies installed
✓ All .env files created
```

### Final Summary

```
📋 Setup Complete - Summary
✓ All components configured successfully! ✨

System Status:
  ✓ Mongodb
  ✓ Serial Ports
  ✓ Python Env
  ✓ Node Modules
  ✓ Env Files

Configuration:
  Receiver Port: /dev/ttyUSB0
  MongoDB: mongodb://localhost:27017/airguard
  MQTT Broker: mqtt://localhost:1883
  Backend API: http://localhost:8080
  WebSocket: ws://localhost:8081

Next Steps:
  1. Start services: python3 start-services.py
     Or: ./start-airguard.sh
  2. Check health: python3 health-check.py
  3. Open dashboard: xdg-open host/dashboard.html
  4. Test ESP32: Press and hold button on sender for 10 seconds
  5. Stop services: python3 stop-services.py
     Or: ./stop-airguard.sh

════════════════════════════════════════════════════════════════════
🎉 Airguard ESP32 IoT is ready to use!
════════════════════════════════════════════════════════════════════
```

---

## 🔧 Troubleshooting

### Serial Port Access Denied

**Problem:**
```
Permission denied: '/dev/ttyUSB0'
```

**Solution:**
```bash
# Add your user to dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in, or run:
newgrp dialout

# Verify you're in the group
groups
```

### MongoDB Won't Start

**Problem:**
```
Failed to start MongoDB service
```

**Solution:**
```bash
# Check MongoDB status
sudo systemctl status mongod

# View MongoDB logs
sudo journalctl -u mongod -n 50

# Try manual start
sudo systemctl start mongod

# Or start manually with custom data directory
mongod --dbpath ~/.mongodb/data --logpath ~/.mongodb/log/mongod.log --fork
```

### ESP32 Not Detected

**Problem:**
```
No serial ports found!
```

**Solution:**
```bash
# 1. Check USB connection
lsusb

# You should see something like:
# Bus 001 Device 004: ID 10c4:ea60 Silicon Labs CP210x UART Bridge

# 2. Check kernel modules
lsmod | grep usbserial

# 3. Load USB serial drivers if needed
sudo modprobe cp210x
sudo modprobe ch341

# 4. Check dmesg for USB events
dmesg | grep tty

# 5. List all serial devices
ls -la /dev/ttyUSB* /dev/ttyACM*
```

### Node.js Version Too Old

**Problem:**
```
Node.js 14.x found, but 18+ required
```

**Solution:**
```bash
# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Fedora:
sudo dnf module reset nodejs
sudo dnf module install nodejs:18

# Arch:
sudo pacman -S nodejs

# Verify
node --version
```

### Python Version Too Old

**Problem:**
```
Python 3.7 found, but 3.9+ required
```

**Solution:**
```bash
# Ubuntu 20.04+:
sudo apt install -y python3.9 python3.9-venv python3-pip

# Or use deadsnakes PPA:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### Script Fails Midway

**Problem:**
Script crashes or hangs during execution

**Solution:**
```bash
# 1. Check for error messages
# 2. Ensure internet connection is stable
# 3. Run with verbose output
python3 -u setup-linux.py 2>&1 | tee setup.log

# 4. Review the log
cat setup.log

# 5. Run steps manually if needed
```

---

## 🎓 Advanced Usage

### Custom Installation Path

```bash
# The script auto-detects the directory it's in
# To use a specific directory:
cd /opt/airguard
sudo python3 setup-linux.py
```

### Skip System Package Installation

If you've already installed system dependencies:

```bash
# Run without sudo
python3 setup-linux.py
```

### Manual Serial Port Configuration

If auto-detection fails, you can manually specify:

```bash
# After setup, edit the .env file
nano host/python-gateway/.env

# Change this line:
SERIAL_PORT=/dev/ttyUSB0  # ← Your receiver port
```

### Re-run Setup

The script is **idempotent** - safe to run multiple times:

```bash
# Re-run to:
# - Update dependencies
# - Fix configuration issues
# - Re-detect serial ports

sudo python3 setup-linux.py
```

---

## 📊 What Gets Installed

### System Packages

**Ubuntu/Debian:**
```
curl wget git
python3 python3-pip python3-venv
nodejs (v18+)
mongodb-org (v6.0)
```

**Fedora:**
```
curl wget git
python3 python3-pip
nodejs npm
mongodb-org
```

**Arch:**
```
curl wget git
python python-pip
nodejs npm
mongodb-bin
```

### Python Packages

**Virtual Environment** (`host/python-gateway/venv`):
```
pyserial>=3.5
requests>=2.31.0
paho-mqtt>=1.6.1
python-dotenv>=1.0.0
sqlite3 (built-in)
```

**Global** (for scripts):
```
psutil>=5.9.0
pyserial>=3.5
```

### Node.js Packages

**mqtt-broker:**
```
aedes (MQTT broker)
aedes-server-factory
```

**node-backend:**
```
express
mqtt
mongodb
ws (WebSocket)
dotenv
```

**mqtt-mongo:**
```
mqtt
mongodb
dotenv
```

---

## 🔒 Security Considerations

### Permissions

The script requires `sudo` for:
- Installing system packages
- Starting MongoDB service
- Adding user to dialout group

It does **NOT** require root for:
- Python virtual environment
- npm package installation
- Creating .env files

### Network Ports

Services listen on localhost only by default:
- MongoDB: `127.0.0.1:27017`
- MQTT: `127.0.0.1:1883`
- HTTP API: `127.0.0.1:8080`
- WebSocket: `127.0.0.1:8081`

To expose externally, edit `.env` files.

---

## 📁 Files Created

```
airguard-esp32-iot/
├── host/
│   ├── python-gateway/
│   │   ├── .env ✨ (created)
│   │   └── venv/ ✨ (created)
│   └── node-backend/
│       ├── .env ✨ (created)
│       └── node_modules/ ✨ (created)
├── bridges/
│   └── mqtt-mongo/
│       ├── .env ✨ (created)
│       └── node_modules/ ✨ (created)
├── mqtt-broker/
│   └── node_modules/ ✨ (created)
├── start-airguard.sh ✨ (created)
├── stop-airguard.sh ✨ (created)
└── setup-linux.py (this script)
```

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** - script outputs detailed error messages
2. **Run health check** - `python3 health-check.py`
3. **Verify permissions** - ensure you're in `dialout` group
4. **Check USB connections** - `lsusb` and `dmesg | grep tty`
5. **Test MongoDB** - `mongosh` or `mongo`
6. **Review .env files** - ensure correct serial port

---

## 🎯 Success Criteria

After successful setup, you should have:

- ✅ All system dependencies installed
- ✅ Python virtual environment created
- ✅ All npm packages installed
- ✅ MongoDB running and accessible
- ✅ Serial ports detected and configured
- ✅ All `.env` files created with correct values
- ✅ User in `dialout` group
- ✅ Startup scripts created and executable

---

## 🚀 Next Steps

After setup completes:

```bash
# 1. Start all services
python3 start-services.py

# 2. Check system health
python3 health-check.py

# 3. Open dashboard
xdg-open host/dashboard.html
# Or: firefox host/dashboard.html

# 4. Test the system
# Press and hold button on ESP32 sender for 10 seconds
# Watch dashboard for real-time data!

# 5. Stop services when done
python3 stop-services.py
```

---

## 📝 Script Source Code

The script is well-commented and modular. Key functions:

- `install_system_dependencies()` - Installs OS packages
- `detect_serial_ports()` - Finds USB/serial devices
- `test_serial_port()` - Identifies sender vs receiver
- `create_env_files()` - Generates configuration
- `setup_python_environment()` - Creates venv
- `setup_nodejs_dependencies()` - Installs npm packages
- `configure_mongodb()` - Starts database
- `run_system_health_check()` - Validates setup

Feel free to modify for your specific needs!

---

**Happy coding! 🛡️✨**
