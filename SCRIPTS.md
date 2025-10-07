# Cross-Platform Scripts Guide

## 🎯 Overview

All Airguard service management scripts are now available as **cross-platform Python scripts** that work on Windows, macOS, and Linux without modification.

---

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements-scripts.txt
```

This installs:
- **psutil**: Process management and monitoring
- **pyserial**: Serial port detection (optional)

---

## 🚀 Available Scripts

### `start-services.py` - Service Launcher

**Cross-platform service starter** that launches all Airguard services in separate terminal windows.

**Usage:**
```bash
python start-services.py
```

**What it does:**
1. ✅ Checks if MongoDB is running (starts it if needed)
2. 🔌 Starts MQTT Broker in new terminal
3. 🌐 Starts Node.js Backend in new terminal
4. 🔗 Starts MQTT-MongoDB Bridge in new terminal
5. 🐍 Starts Python Gateway in new terminal
6. 📊 Displays service summary with URLs

**Platform-specific behavior:**
- **Windows**: Opens new PowerShell windows
- **macOS**: Opens new Terminal.app tabs
- **Linux**: Opens new gnome-terminal/xterm/konsole windows

---

### `stop-services.py` - Service Stopper

**Gracefully stops all Airguard services** with smart process detection.

**Usage:**
```bash
python stop-services.py
```

**What it does:**
1. 🔍 Finds all Airguard-related processes (Node.js, Python, npm)
2. 🛑 Attempts graceful termination (SIGTERM)
3. ⚡ Force kills if graceful shutdown fails (timeout: 3s)
4. 📊 Reports how many processes were stopped

**Process detection:**
- Searches for processes running `broker.js`, `server.js`, `bridge.js`
- Finds Python processes running `gateway_enhanced.py`
- Identifies npm processes managing Node services

---

### `health-check.py` - System Health Monitor

**Comprehensive health check** for all Airguard components.

**Usage:**
```bash
python health-check.py
```

**What it checks:**
- 💻 **System Info**: OS, Python version, timestamp
- 🌐 **Ports**: MongoDB (27017), MQTT (1883), HTTP (8080), WebSocket (8081)
- ⚙️ **Processes**: Running Node.js and Python processes
- 💾 **Database**: SQLite file existence and size
- 🔌 **Serial Ports**: Available COM/ttyUSB ports with ESP32 detection
- ⚙️ **Configuration**: Checks if all .env files exist

**Sample Output:**
```
============================================================
🔍 Airguard System Health Check
============================================================

💻 System Information
  OS: Windows 11
  Python: 3.13.5
  Time: 2025-10-07 23:07:17

🌐 Port Status
  ✓ Port 27017 (MongoDB) is open
  ✓ Port 1883 (MQTT Broker) is open
  ✓ Port 8080 (Node Backend HTTP) is open
  ✓ Port 8081 (WebSocket) is open

⚙️  Process Status
  ✓ Node.js processes running: 3
  ✓ Python processes running: 2

💾 Database Status
  SQLite database size: 24.00 KB

🔌 Serial Ports
  Available ports: COM12, COM14
    → COM12: USB-Enhanced-SERIAL CH343

⚙️  Configuration
  ✓ All .env files present

============================================================
✓ All services appear to be running!
============================================================
```

---

## 🔄 Migration from PowerShell/Shell

### Before (Platform-specific)

**Windows:**
```powershell
.\start-services.ps1
.\stop-services.ps1
.\health-check.ps1
```

**Linux/Mac:**
```bash
./start-services.sh
./health-check.sh
pkill -f node  # Manual stop
```

### After (Cross-platform)

**Any OS:**
```bash
python start-services.py
python stop-services.py
python health-check.py
```

---

## 🎨 Features

### Colored Output

All scripts use ANSI color codes for better readability:

- 🟢 **Green**: Success messages, open ports, running services
- 🟡 **Yellow**: Warnings, section headers
- 🔴 **Red**: Errors, closed ports, missing components
- 🔵 **Cyan**: Informational messages, tips
- ⚪ **White**: Regular text

### Smart Process Management

- **Graceful shutdown**: Tries SIGTERM first
- **Force kill fallback**: Uses SIGKILL after 3s timeout
- **Process filtering**: Only stops Airguard-related processes
- **Status reporting**: Shows which processes were terminated

### Platform Detection

Scripts automatically detect the OS and adapt:

```python
import platform

system = platform.system()
# Returns: 'Windows', 'Darwin' (macOS), or 'Linux'
```

---

## 🛠️ Troubleshooting

### "psutil module not found"

```bash
pip install psutil
```

### Scripts don't have color on Windows

**Windows Terminal** or **PowerShell 7+** required for ANSI colors.

**Alternative:** Use **Windows Subsystem for Linux (WSL)**.

### Terminal windows don't open on Linux

Install a supported terminal emulator:

```bash
# Ubuntu/Debian
sudo apt install gnome-terminal

# Or xterm
sudo apt install xterm

# Or konsole
sudo apt install konsole
```

### "Permission denied" on macOS/Linux

Make scripts executable:

```bash
chmod +x start-services.py stop-services.py health-check.py
```

Then run with:

```bash
./start-services.py
```

---

## 📝 Development Notes

### Adding New Services

To add a service to `start-services.py`:

```python
start_service(
    "Service Name",           # Display name
    "npm start",              # Command to run
    "path/to/service",        # Working directory (relative to project root)
    wait_time=3               # Seconds to wait before continuing
)
```

### Checking Custom Ports

To add port checking in `health-check.py`:

```python
ports = [
    (27017, "MongoDB"),
    (1883, "MQTT Broker"),
    (8080, "Node Backend HTTP"),
    (8081, "WebSocket"),
    (9000, "Your Custom Service"),  # Add your port here
]
```

---

## 🔗 Related Files

- `requirements-scripts.txt` - Python dependencies for scripts
- `.env.example` - Configuration templates
- `systemd/` - Linux systemd service files (production)
- `start-services.ps1` - Legacy Windows PowerShell script
- `start-services.sh` - Legacy Linux/Mac shell script

---

## 🚀 Quick Start

**First time setup:**
```bash
# Install script dependencies
pip install -r requirements-scripts.txt

# Configure environment
cp host/python-gateway/.env.example host/python-gateway/.env
cp host/node-backend/.env.example host/node-backend/.env
cp bridges/mqtt-mongo/.env.example bridges/mqtt-mongo/.env

# Edit .env files with your settings
# (COM port, MongoDB URI, etc.)
```

**Daily use:**
```bash
# Start everything
python start-services.py

# Check status
python health-check.py

# Stop everything
python stop-services.py
```

---

**Built with ❤️ for cross-platform IoT development**
