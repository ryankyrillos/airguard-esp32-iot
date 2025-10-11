# 🛡️ Airguard - ESP32-S3 IoT Sensor System


> **Complete end-to-end IoT solution** for capturing GPS, accelerometer, gyroscope, and temperature data from ESP32-S3 devices and streaming to a cloud dashboard with real-time WebSocket updates.

[![GitHub](https://img.shields.io/badge/GitHub-ryankyrillos%2Fairguard--esp32--iot-blue?logo=github)](https://github.com/ryankyrillos/airguard-esp32-iot)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ESP32](https://img.shields.io/badge/ESP32-S3-red.svg)](https://www.espressif.com/en/products/socs/esp32-s3)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)

---

## 📸 Screenshots

### Real-time Dashboard
![Airguard Dashboard](assets/images/Dashboard.png)
*Live WebSocket updates showing GPS coordinates, sensor data, and sample history*

### System Running
![All Services Running](assets/images/Terminals.png)
*Python gateway, MQTT broker, Node.js backend, and MongoDB bridge in action*

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#️-system-architecture)
- [Hardware Requirements](#-hardware-requirements)
- [Quick Start (5 Minutes)](#-quick-start-5-minutes)
- [Detailed Setup Guide](#-detailed-setup-guide)
- [Project Structure](#-project-structure)
- [Data Flow](#-data-flow)
- [Configuration](#️-configuration)
- [Troubleshooting](#-troubleshooting)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Production Deployment](#-production-deployment)
- [Monitoring & Logs](#-monitoring--logs)
- [Security](#-security)

---

## 🎯 Overview

**Airguard** is a complete IoT sensor data collection and monitoring system that combines:

- **ESP32-S3 Hardware**: Two devices communicating via ESP-NOW wireless protocol
- **Sensors**: GPS (NEO-6M), IMU (MPU6050), Temperature
- **Host Services**: Python gateway, MQTT broker, Node.js backend, MongoDB database
- **Real-time Dashboard**: WebSocket-powered web interface

### ✨ Key Features

✅ **Wireless Data Collection** - ESP-NOW protocol (no WiFi router needed)  
✅ **Multi-Sensor Support** - GPS, Accelerometer, Gyroscope, Temperature  
✅ **Real-time Updates** - WebSocket streaming to browser dashboard  
✅ **Local & Cloud Storage** - SQLite + MongoDB dual database  
✅ **Production Ready** - Systemd services, health checks, monitoring  
✅ **Easy Deployment** - One-command startup script  

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph Hardware["🔧 Hardware Layer"]
        A["ESP32-S3 SENDER<br/>GPS NEO-6M + MPU6050<br/>Button + NeoPixel LED<br/>10-second hold gating"]
        B["ESP32-S3 RECEIVER<br/>JSON + Human-Readable Output"]
    end
    
    subgraph Gateway["🔌 Gateway Layer"]
        C["PYTHON GATEWAY<br/>• Parses Serial Data<br/>• SQLite Storage<br/>• MQTT Publisher<br/>• REST Client"]
    end
    
    subgraph Messaging["📡 Message Broker"]
        D["MQTT BROKER<br/>Aedes - Port 1883<br/>QoS 1"]
    end
    
    subgraph Processing["⚙️ Processing Layer"]
        E["MQTT-MONGODB BRIDGE<br/>• Subscribe espnow/samples<br/>• Insert to MongoDB<br/>• WebSocket Broadcast"]
        F["NODE.JS BACKEND<br/>• REST API Port 8080<br/>• WebSocket Port 8081<br/>• Query MongoDB"]
    end
    
    subgraph Storage["💾 Data Storage"]
        G[("MONGODB<br/>Database: airguard<br/>Collection: samples")]
        H[("SQLite<br/>Local Backup")]
    end
    
    subgraph Frontend["🌐 Frontend"]
        I["WEB DASHBOARD<br/>• Real-time Display<br/>• GPS Mapping<br/>• Historical Data<br/>• Live WebSocket Updates"]
    end
    
    A -->|ESP-NOW Wireless| B
    B -->|USB Serial<br/>115200 baud| C
    C -->|Store| H
    C -->|Publish| D
    C -->|POST /v1/samples| F
    D -->|Subscribe| E
    E -->|Insert| G
    F -->|Query| G
    F -->|WebSocket Stream| I
    E -->|WebSocket Broadcast| I
    
    style A fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style B fill:#ff8787,stroke:#c92a2a,stroke-width:2px,color:#fff
    style C fill:#4dabf7,stroke:#1971c2,stroke-width:2px,color:#fff
    style D fill:#ffd43b,stroke:#f08c00,stroke-width:2px,color:#000
    style E fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style F fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style G fill:#845ef7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style H fill:#845ef7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style I fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
```

---

## 🔧 Hardware Requirements

### ESP32-S3 Devices (x2)

**Sender Device:**
- ESP32-S3 DevKit
- GPS Module: NEO-6M (UART - TX2, RX2)
- IMU Sensor: MPU6050 (I2C - SDA, SCL)
- Button (GPIO with pull-up)
- NeoPixel RGB LED (WS2812)
- Power: USB or Battery

**Receiver Device:**
- ESP32-S3 DevKit
- USB connection to host computer

### Host Computer

- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 1GB free space
- **Ports**: USB port for ESP32 receiver

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

✅ Node.js 18+ installed  
✅ Python 3.9+ installed  
✅ MongoDB installed and running  
✅ Arduino IDE with ESP32-S3 board support  
✅ Both ESP32 devices programmed and connected  

### 1. Upload Firmware (If Not Already Done)

**Sender:**
```
Arduino IDE → Open: esp32s3-gps-mpu-button-sender/esp32s3-gps-mpu-button-sender.ino
Select Board: ESP32-S3 Dev Module
Upload to sender ESP32
```

**Receiver:**
```
Arduino IDE → Open: esp32s3-receiver-json/esp32s3-receiver-json.ino
Select Board: ESP32-S3 Dev Module
Upload to receiver ESP32
```

### 2. Identify COM Ports (Windows)

```powershell
# List all COM ports
[System.IO.Ports.SerialPort]::getportnames()

# Identify which ESP32 is which:
# Sender: Shows [MEASURE], [SEND] messages
# Receiver: Shows GPS/sensor data output
```

### 3. Configure Serial Port

Edit `host/python-gateway/.env`:
```env
SERIAL_PORT=COM12  # Change to your receiver's COM port
```

### 4. Start All Services

```powershell
# Windows
cd C:\Users\Admin\esp32dongle
.\start-services.ps1
```

```bash
# Linux/Mac
cd ~/esp32dongle
chmod +x start-services.sh
./start-services.sh
```

### 5. Open Dashboard

Navigate to `host/dashboard.html` and open with your browser.

### 6. Test!

1. **Press button** on ESP32 sender (hold 10 seconds if first press)
2. **Wait for GPS fix** (LED turns blue when satellites acquired)
3. **Watch data appear** in dashboard!

---

## 💡 LED States (Sender)

| LED | Meaning |
|-----|---------|
| **WHITE steady** | No ESP-NOW link / waiting for receiver |
| **BLUE blinking** | Link OK but not ready (GPS no fix or MPU unhealthy) |
| **BLUE steady** | **READY** (link + GPS fix + MPU healthy) |
| **RED blinking** | Button held <10s |
| **GREEN ×3 blinks** | Button held ≥10s, OK to release |
| **RED ×3 blinks** | Send failed (gating check failed) |

---

## 🔧 Hardware Requirements

### ESP32-S3 Devices (x2)

**Sender Device:**
- ESP32-S3 DevKit
- GPS Module: NEO-6M (UART - TX2, RX2)
- IMU Sensor: MPU6050 (I2C - SDA, SCL)
- Button (GPIO with pull-up)
- NeoPixel RGB LED (WS2812)
- Power: USB or Battery

**Receiver Device:**
- ESP32-S3 DevKit
- USB connection to host computer

### Host Computer

- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 1GB free space
- **Ports**: USB port for ESP32 receiver

---

## 📡 Send Gating Rules

Data is **only sent** when **ALL** conditions are met:

1. ✅ ESP-NOW peer linked and healthy (recent ACK <5s)
2. ✅ MPU6050 healthy (recent read <1.2s)
3. ✅ GPS fix valid (NMEA active, fix valid, sats ≥1, age <2s)
4. ✅ Button held ≥10 seconds

**If any fail:** RED ×3 blinks, packet discarded.

---

## 📦 Packet Format (64 bytes)

```c
typedef struct {
  uint32_t batchId;      // Unique ID (esp_random())
  uint32_t sessionMs;    // Hold duration (ms)
  uint32_t samples;      // IMU samples averaged
  uint32_t dateYMD;      // YYYYMMDD (0 if invalid)
  uint32_t timeHMS;      // HHMMSS   (0 if invalid)
  uint16_t msec;         // Milliseconds
  float lat, lon, alt;   // GPS coordinates
  uint8_t gpsFix, sats;  // Fix status, satellite count
  float ax, ay, az;      // Accel (m/s²)
  float gx, gy, gz;      // Gyro (rad/s)
  float tempC;           // Temperature (°C)
} SensorPacket;
```

```mermaid
sequenceDiagram
    participant S as Sender ESP32
    participant R as Receiver ESP32
    participant P as Python Gateway
    participant M as MQTT Broker
    participant B as MQTT Bridge
    participant D as MongoDB
    participant N as Node Backend
    participant W as Web Dashboard

    S->>S: Button pressed (10s hold)
    S->>S: Collect GPS + IMU data
    S->>S: Validate gating rules
    S->>R: ESP-NOW packet (64 bytes)
    R->>R: Parse packet
    R->>P: Serial output (JSON + Text)
    P->>P: Parse & validate
    par Parallel Storage
        P->>P: Store to SQLite
        P->>M: Publish MQTT
        P->>N: POST /v1/samples
    end
    M->>B: Forward message
    B->>D: Insert document
    B->>W: WebSocket broadcast
    N->>D: Insert document
    N->>W: WebSocket broadcast
    W->>W: Update UI (real-time)
```

---

## 📖 Detailed Setup Guide

### Step 1: Install Dependencies

#### Windows (PowerShell as Administrator)

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Node.js, Python, Git
choco install -y nodejs-lts python git

# Install MongoDB
choco install -y mongodb

# Start MongoDB service
net start MongoDB
```

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.9+
sudo apt install -y python3 python3-pip python3-venv

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install node@18 python@3.9 mongodb-community

# Start MongoDB
brew services start mongodb-community
```

### Step 2: Clone Repository

```bash
git clone https://github.com/ryankyrillos/airguard-esp32-iot.git
cd airguard-esp32-iot
```

### Step 3: Install Python Dependencies

```bash
cd host/python-gateway
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your COM port
```

### Step 4: Install Node Dependencies

```bash
# Node Backend
cd ../../host/node-backend
npm install
cp .env.example .env

# MQTT Broker
cd ../../mqtt-broker
npm install

# MQTT-MongoDB Bridge
cd ../bridges/mqtt-mongo
npm install
cp .env.example .env
```

### Step 5: Upload ESP32 Firmware

1. Open Arduino IDE
2. Install ESP32 board support (File → Preferences → Additional Boards Manager URLs):
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Tools → Board → ESP32 Arduino → ESP32S3 Dev Module
4. Tools → Manage Libraries → Install: `Adafruit NeoPixel`, `Adafruit MPU6050`, `TinyGPSPlus`, `ArduinoJson`

**Upload Sender:**
```
File → Open → esp32s3-gps-mpu-button-sender/esp32s3-gps-mpu-button-sender.ino
Tools → Port → [Select sender port]
Sketch → Upload
```

**Upload Receiver:**
```
File → Open → esp32s3-receiver-json/esp32s3-receiver-json.ino
Tools → Port → [Select receiver port]
Sketch → Upload
```

### Step 6: Find Receiver COM Port

**Windows:**
```powershell
[System.IO.Ports.SerialPort]::getportnames()
```

**Linux:**
```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

**macOS:**
```bash
ls /dev/cu.usbserial-*
```

Open Arduino Serial Monitor on each device to identify which is which:
- **Sender**: Shows `[MEASURE]`, `[SEND]` messages
- **Receiver**: Shows GPS/sensor data output

### Step 7: Configure COM Port

Edit `host/python-gateway/.env`:
```env
SERIAL_PORT=COM12  # Replace with your receiver's port
```

### Step 8: Start Services

**Windows (One Command):**
```powershell
.\start-services.ps1
```

**Linux/Mac (One Command):**
```bash
chmod +x start-services.sh
./start-services.sh
```

**Or start individually:**

```bash
# Terminal 1: MQTT Broker
cd mqtt-broker
node broker.js

# Terminal 2: Node Backend
cd host/node-backend
npm start

# Terminal 3: MQTT-MongoDB Bridge
cd bridges/mqtt-mongo
node bridge.js

# Terminal 4: Python Gateway
cd host/python-gateway
python gateway_enhanced.py
```

### Step 9: Open Dashboard

Navigate to `host/dashboard.html` and open in your browser.

### Step 10: Test!

1. Press and hold button on sender ESP32
2. Wait for LED to turn GREEN (after 10 seconds)
3. Release button
4. Check dashboard for new data!

---

## 🛠️ Troubleshooting

### No Data Appearing in Dashboard

1. **Check COM Port**: Verify receiver is on correct port
   ```powershell
   # Windows
   [System.IO.Ports.SerialPort]::getportnames()
   ```

2. **Check Services**: All 4 services should be running
   ```bash
   # Check health endpoints
   curl http://localhost:8080/health
   ```

3. **Check Serial Output**: Open Arduino Serial Monitor on receiver (115200 baud)
   - Should see data packets when sender transmits

4. **Check MongoDB**: Verify connection
   ```bash
   mongosh
   use airguard
   db.samples.find().limit(1)
   ```

### GPS Not Getting Fix

- **Move outdoors**: GPS needs clear sky view
- **Wait 5-10 minutes**: Cold start takes time
- **Check wiring**: TX2→RX, RX2→TX on ESP32
- **LED Status**: Blue blinking = no fix, Blue steady = fix acquired

### MPU6050 Not Working

- **Check I2C Wiring**: SDA to GPIO21, SCL to GPIO22
- **Check I2C Address**: Should be 0x68 (default)
- **Run I2C Scanner**: Use Arduino I2C scanner sketch
- **Power Cycle**: Unplug and replug ESP32

### ESP-NOW Link Failing

- **Check MAC Address**: Ensure sender has correct receiver MAC
  ```cpp
  uint8_t receiverMAC[6] = {0x48,0xCA,0x43,0x9A,0x48,0xD0};
  ```
- **Get Receiver MAC**: Add this to receiver setup():
  ```cpp
  Serial.print("MAC: ");
  Serial.println(WiFi.macAddress());
  ```
- **Same WiFi Channel**: Both devices must use channel 1
- **Distance**: Keep within 10 meters initially

### MongoDB Connection Failed

**Windows:**
```powershell
# Check if MongoDB service is running
Get-Service MongoDB

# Start if stopped
net start MongoDB
```

**Linux:**
```bash
sudo systemctl status mongod
sudo systemctl start mongod
```

### Port Already in Use

```bash
# Windows - Find process on port
netstat -ano | findstr :8080

# Linux/Mac
lsof -i :8080

# Kill process
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

### Common Issues

**ESP-NOW link failing (WHITE LED):**
- Check receiver is powered and on same channel
- Verify receiver MAC address in sender code
- Check serial output for ESP-NOW init errors

**Sender LED blinks BLUE:**
- Check GPS has clear sky view (satellites visible)
- Verify MPU6050 wiring (SDA=21, SCL=22)
- Check I2C connections

**RED ×3 on send:**
- Press and hold ≥10 seconds (wait for GREEN ×3)
- Ensure GPS has valid fix
- Check MPU6050 is responding

**Python gateway COM port busy:**
- Close Arduino Serial Monitor
- Check Device Manager for correct port
- Restart Arduino IDE

**No data in MongoDB:**
- Check Node backend is running (`npm start`)
- Verify `CLOUD_POST_URL` in gateway .env
- Check network connectivity
- Review gateway logs

---

## 🚀 Production Deployment

### Linux/Jetson (systemd)

#### 1. Install System Dependencies

```bash
# MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Python
sudo apt install -y python3 python3-pip python3-venv
```

#### 2. Install Project Dependencies

```bash
# Python Gateway
cd host/python-gateway
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings

# Node Backend
cd ../../host/node-backend
npm install
cp .env.example .env

# MQTT Broker
cd ../../mqtt-broker
npm install

# MQTT-MongoDB Bridge
cd ../bridges/mqtt-mongo
npm install
cp .env.example .env
```

#### 3. Configure Environment Variables

**Python Gateway** (`host/python-gateway/.env`):
```env
SERIAL_PORT=/dev/ttyUSB0        # Your ESP32 receiver port
CLOUD_POST_URL=http://localhost:8080/v1/samples
MQTT_BROKER=127.0.0.1
MQTT_PORT=1883
MQTT_TOPIC=espnow/samples
SQLITE_DB=airguard.db
```

**Node Backend** (`host/node-backend/.env`):
```env
PORT=8080
MONGO_URI=mongodb://localhost:27017
DB_NAME=airguard
COLLECTION_NAME=samples
WS_PORT=8081
AUTH_TOKEN=your-secure-token-here
CORS_ORIGIN=*
```

**MQTT-MongoDB Bridge** (`bridges/mqtt-mongo/.env`):
```env
MQTT_BROKER=mqtt://127.0.0.1:1883
MQTT_TOPIC=espnow/samples
MONGO_URI=mongodb://localhost:27017
MONGO_DB=airguard
MONGO_COLLECTION=samples
WS_PORT=8081
```

#### 4. Setup Systemd Services

**Python Gateway Service:**
```bash
sudo cp systemd/airguard-gateway.service /etc/systemd/system/
# Edit service file with correct paths/user
sudo systemctl enable airguard-gateway
sudo systemctl start airguard-gateway
```

**MQTT Broker Service:**
```bash
sudo cp systemd/airguard-mqtt-broker.service /etc/systemd/system/
sudo systemctl enable airguard-mqtt-broker
sudo systemctl start airguard-mqtt-broker
```

**Node Backend Service:**
```bash
sudo cp systemd/airguard-backend.service /etc/systemd/system/
sudo systemctl enable airguard-backend
sudo systemctl start airguard-backend
```

**MQTT-MongoDB Bridge Service:**
```bash
sudo cp systemd/airguard-mqtt-bridge.service /etc/systemd/system/
sudo systemctl enable airguard-mqtt-bridge
sudo systemctl start airguard-mqtt-bridge
```

#### 5. Verify Services

```bash
sudo systemctl status airguard-gateway
sudo systemctl status airguard-mqtt-broker
sudo systemctl status airguard-backend
sudo systemctl status airguard-mqtt-bridge
```

#### 6. Monitor Logs

```bash
# Python gateway logs
sudo journalctl -u airguard-gateway -f

# MQTT broker logs
sudo journalctl -u airguard-mqtt-broker -f

# Node backend logs
sudo journalctl -u airguard-backend -f

# MQTT bridge logs
sudo journalctl -u airguard-mqtt-bridge -f
```

### Security Best Practices

- **Set `AUTH_TOKEN`** in Node backend .env
- **Enable MongoDB authentication** in production
- **Use TLS for MQTT** (port 8883 instead of 1883)
- **Reverse proxy** (nginx) for HTTPS on Node backend
- **Restrict CORS origins** in production (not `*`)
- **Firewall rules** to limit port access
- **Regular backups** of MongoDB data

---

## 👨‍💻 Development

### Monitor Sender

```bash
# Arduino Serial Monitor @ 115200 baud
# Or: screen COM14 115200  (Windows)
# Or: screen /dev/ttyACM0 115200  (Linux)
```

### Monitor Receiver

```bash
# Same as above, different port
```

### Test Data Ingestion

```bash
# Send test POST to backend
curl -X POST http://localhost:8080/v1/samples \
  -H "Content-Type: application/json" \
  -d '{
    "batchId": "0xTEST1234",
    "sessionMs": 10000,
    "samples": 1000,
    "lat": 34.05,
    "lon": -118.25,
    "alt": 100.0
  }'
```

### Query MongoDB

```bash
mongosh
use airguard
db.samples.find().limit(5).pretty()
db.samples.countDocuments()
```

---

## 📝 TODO

- [ ] Web dashboard: Add map view for GPS coordinates
- [ ] Node backend: GraphQL API
- [ ] Python gateway: Batch insert for performance
- [ ] ESP32: Deep sleep mode when idle
- [ ] Health metrics endpoints (packets/min, ACK ratio)
- [ ] Unique index on `batchId` + timestamp in MongoDB
- [ ] Windows service wrapper for Python gateway

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Support

For issues, check:
1. Serial monitor output (sender + receiver)
2. Python gateway logs
3. Node backend logs
4. MongoDB connection status
5. MQTT broker status

**Built with ❤️ for reliable embedded IoT telemetry**

---

#### Upload Sender Firmware

1. Open Arduino IDE
2. File → Open → `esp32s3-gps-mpu-button-sender/esp32s3-gps-mpu-button-sender.ino`
3. Tools → Board → ESP32 Arduino → ESP32S3 Dev Module
4. Tools → Port → Select sender's COM port
5. Click Upload (Ctrl+U)

**LED States:**
- **White**: Waiting for GPS fix
- **Blue**: GPS locked, ready to send
- **Red**: Button pressed, collecting data
- **Green**: Data sent successfully

**Important:** First button press requires 10-second hold (safety gate)

#### Receiver Firmware

1. Open Arduino IDE
2. File → Open → `esp32s3-receiver-json/esp32s3-receiver-json.ino`
3. Tools → Board → ESP32 Arduino → ESP32S3 Dev Module
4. Tools → Port → Select receiver's COM port
5. Click Upload (Ctrl+U)

**Receiver Outputs:**
- Human-readable fenced block format (for visual debugging)
- JSON format (for machine parsing)

---

## 📁 Project Structure

```
esp32dongle/
├── README.md                              # ← YOU ARE HERE - Complete documentation
│
├── assets/                                # Project assets
│   └── images/                            # Screenshots and images
│       ├── Dashboard.png                  # Web dashboard screenshot
│       └── Terminals.png                  # System running screenshot
│
├── esp32s3-gps-mpu-button-sender/        # Sender ESP32 firmware
│   └── esp32s3-gps-mpu-button-sender.ino
│
├── esp32s3-receiver-json/                # Receiver ESP32 firmware (JSON output)
│   └── esp32s3-receiver-json.ino
│
├── esp32s3-gps-mpu-button-receiver/      # Original receiver (human-readable only)
│   └── esp32s3-gps-mpu-button-receiver.ino
│
├── host/                                  # Host computer services
│   ├── python-gateway/                    # Serial → MQTT/SQLite gateway
│   │   ├── gateway.py                     # Standard version (fenced block)
│   │   ├── gateway_enhanced.py            # Enhanced with JSON parsing
│   │   ├── test_parser.py                 # Unit tests
│   │   ├── requirements.txt               # Python dependencies
│   │   ├── .env.example                   # Configuration template
│   │   └── .env                           # Your configuration (create from example)
│   │
│   ├── node-backend/                      # REST API + WebSocket server
│   │   ├── src/
│   │   │   └── server.js                  # Main Express server
│   │   ├── package.json                   # Node dependencies
│   │   ├── .env.example                   # Configuration template
│   │   └── .env                           # Your configuration (create from example)
│   │
│   └── dashboard.html                     # Real-time web dashboard
│
├── bridges/                               # Integration services
│   └── mqtt-mongo/                        # MQTT → MongoDB bridge
│       ├── bridge.js                      # Bridge service
│       ├── package.json                   # Node dependencies
│       ├── .env.example                   # Configuration template
│       └── .env                           # Your configuration (create from example)
│
├── mqtt-broker/                           # Lightweight MQTT broker
│   ├── broker.js                          # Aedes MQTT broker
│   └── package.json                       # Node dependencies
│
├── scripts/                               # Utility scripts
│   ├── health-check.ps1                   # Windows health check
│   └── health-check.sh                    # Linux health check
│
├── systemd/                               # Linux service files (for production)
│   ├── airguard-mqtt-broker.service
│   ├── airguard-backend.service
│   ├── airguard-mqtt-bridge.service
│   └── airguard-gateway.service
│
├── start-services.ps1                     # Windows startup script
├── start-services.sh                      # Linux startup script
├── stop-services.ps1                      # Windows shutdown script
└── .gitignore                             # Git ignore rules
```

---

## 🔄 Data Flow

### Complete Packet Journey

1. **Button Press** → User presses button on sender ESP32
   - First press: Must hold 10 seconds (safety gate)
   - Subsequent presses: Instant send

2. **Data Collection** → Sender reads sensors
   - GPS: Latitude, longitude, altitude, satellites, fix status
   - MPU6050: Accelerometer (X, Y, Z), Gyroscope (X, Y, Z), Temperature
   - Session: Batch ID, duration, sample count

3. **ESP-NOW Transmission** → Wireless packet (64 bytes)
   - Sender MAC → Receiver MAC
   - Reliable delivery with ACK
   - <1ms latency

4. **Serial Output** → Receiver outputs dual format
   - **Fenced Block** (human-readable):
     ```
     === Received Data ===
     Batch: 0xAF869913 | Duration: 10853 ms | Samples: 1601
     GPS Fix: 1, Sats: 12 | Date: 20251007 | Time: 081621.000
     Lat: 34.140240  Lon: 35.663094  Alt: 227.60 m
     ...
     ====================
     ```
   - **JSON Line** (machine-readable):
     ```json
     {"batchId":"0xAF869913","sessionMs":10853,"samples":1601,...}
     ```

5. **Python Gateway** → Processes serial data
   - ✅ Parses both formats (prefers JSON for accuracy)
   - ✅ Validates data
   - ✅ Stores to SQLite database (`airguard.db`)
   - ✅ Publishes to MQTT topic (`espnow/samples`)
   - ✅ POSTs to REST API (optional)

6. **MQTT Broker** → Routes messages
   - Receives from Python gateway
   - Distributes to all subscribers
   - QoS 1 (at least once delivery)

7. **MQTT-MongoDB Bridge** → Persists data
   - Subscribes to `espnow/samples`
   - Validates and transforms data
   - Inserts into MongoDB collection
   - Broadcasts to WebSocket clients

8. **MongoDB** → Stores historical data
   - Database: `airguard`
   - Collection: `samples`
   - Indexed by timestamp and batchId

9. **Node.js Backend** → Serves data
   - REST API for queries
   - WebSocket for real-time push
   - CORS enabled for browser access

10. **Web Dashboard** → Displays data
    - Fetches historical samples via REST
    - Receives real-time updates via WebSocket
    - Updates UI dynamically

### Data Formats

#### ESP-NOW Packet Structure (64 bytes)

```c
struct SensorPacket {
  uint32_t batchId;        // Unique batch identifier (hex)
  uint32_t sessionMs;      // Session duration in milliseconds
  uint16_t samples;        // Number of IMU samples collected
  uint8_t dateYMD[3];      // GPS date [year-2000, month, day]
  uint32_t timeHMS;        // GPS time (HHMMSS format)
  uint16_t msec;           // Milliseconds (0-999)
  int32_t lat;             // Latitude * 1,000,000
  int32_t lon;             // Longitude * 1,000,000
  int32_t alt;             // Altitude in centimeters
  uint8_t gpsFix;          // GPS fix status (0=no fix, 1=fix)
  uint8_t sats;            // Number of satellites
  int16_t ax, ay, az;      // Acceleration in milligravity (mg)
  int16_t gx, gy, gz;      // Gyroscope in deg/s * 10
  int16_t tempC;           // Temperature in °C * 100
};
```

#### JSON Output Format

```json
{
  "batchId": "0xAF869913",
  "sessionMs": 10853,
  "samples": 1601,
  "dateYMD": 20251007,
  "timeHMS": 81621,
  "msec": 0,
  "lat": 34.140240,
  "lon": 35.663094,
  "alt": 227.60,
  "gpsFix": 1,
  "sats": 12,
  "ax": -8.23,
  "ay": -4.21,
  "az": -1.29,
  "gx": -0.050,
  "gy": 0.062,
  "gz": -0.232,
  "tempC": 27.75
}
```

---

## ⚙️ Configuration

### Serial Port Detection

**Windows:**
```powershell
# List all COM ports
[System.IO.Ports.SerialPort]::getportnames()

# Detailed device information
Get-CimInstance -ClassName Win32_PnPEntity | Where-Object { $_.Caption -match 'COM' }
```

**Linux:**
```bash
# List USB serial devices
ls -l /dev/ttyUSB* /dev/ttyACM*

# Show device details
dmesg | grep tty

# Check permissions
groups  # Make sure you're in 'dialout' group
sudo usermod -a -G dialout $USER  # Add yourself if needed
```

### MongoDB Configuration

**Check MongoDB status:**
```bash
# Windows
Get-Service MongoDB

# Linux
systemctl status mongod
```

**Start MongoDB:**
```bash
# Windows
Start-Service MongoDB

# Linux
sudo systemctl start mongod
```

**Connect to MongoDB shell:**
```bash
mongosh mongodb://localhost:27017/airguard
```

**Useful MongoDB queries:**
```javascript
// Show all databases
show dbs

// Switch to airguard database
use airguard

// Count samples
db.samples.count()

// Get latest 10 samples
db.samples.find().sort({timestamp: -1}).limit(10)

// Query by batch ID
db.samples.find({batchId: "0xAF869913"})

// Delete all samples (CAREFUL!)
db.samples.deleteMany({})
```

### Environment Variables

All services use `.env` files for configuration. Each service directory has `.env.example`:

```bash
# In each service directory (python-gateway, node-backend, mqtt-mongo)
cp .env.example .env
# Edit .env with your custom settings
```

**Never commit `.env` files to version control!** (Already in `.gitignore`)

---

## 🐛 Troubleshooting

### ESP32 Issues

#### Problem: Sender LED stays white
- **Cause:** GPS has no satellite fix
- **Solution:** 
  - Move outdoors (GPS doesn't work indoors)
  - Wait 2-5 minutes for initial GPS lock
  - Check serial monitor: `sats=0` → should increase to `sats=4+`
  - Verify GPS antenna is connected

#### Problem: Compilation error "redefinition of..."
- **Cause:** Multiple `.ino` files in same folder
- **Explanation:** Arduino IDE compiles ALL `.ino` files in a folder together
- **Solution:** Keep only ONE `.ino` file per folder, or use separate folders

#### Problem: ESP-NOW packets not received
- **Cause:** MAC address mismatch
- **Check:** Print sender MAC in serial monitor
- **Solution:** Update `SENDER_MAC` array in receiver code:
  ```c
  const uint8_t SENDER_MAC[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};  // Your sender's MAC
  ```

#### Problem: Button doesn't trigger send
- **Cause:** First press requires 10-second hold
- **Solution:** Hold button for 10+ seconds on first press (safety gate)
- **After:** Subsequent presses are instant

### Python Gateway Issues

#### Problem: "ModuleNotFoundError: No module named 'serial'"
- **Cause:** Dependencies not installed
- **Solution:**
  ```bash
  cd host/python-gateway
  pip install -r requirements.txt
  ```

#### Problem: "PermissionError: Access is denied (COM port)"
- **Cause:** Another program is using the serial port
- **Common culprits:** Arduino IDE Serial Monitor, PuTTY, other serial terminals
- **Solution:** Close all other serial programs before starting gateway

#### Problem: "No JSON found in line"
- **Cause:** Receiver outputting only human-readable format
- **Check:** Verify you uploaded `esp32s3-receiver-json.ino` (not the original receiver)
- **Solution:** Upload the JSON-enabled receiver firmware

#### Problem: Gateway crashes or stops receiving
- **Cause:** Serial buffer overflow or corrupt data
- **Solution:** 
  - Restart gateway
  - Check receiver is sending valid JSON
  - Reduce baud rate if data corruption persists

### Node.js Backend Issues

#### Problem: "Error: connect ECONNREFUSED 127.0.0.1:27017"
- **Cause:** MongoDB not running
- **Solution:**
  ```bash
  # Windows
  Start-Service MongoDB
  Get-Service MongoDB  # Verify it's running
  
  # Linux
  sudo systemctl start mongod
  sudo systemctl status mongod  # Verify it's running
  ```

#### Problem: "Error: listen EADDRINUSE :::8080"
- **Cause:** Port 8080 or 8081 already in use
- **Find process:**
  ```powershell
  # Windows
  netstat -ano | findstr :8080
  taskkill /PID <PID> /F
  
  # Linux
  lsof -i :8080
  kill <PID>
  ```
- **Or change port:** Edit `PORT` in `host/node-backend/.env`

#### Problem: Backend starts but can't connect to MongoDB
- **Cause:** MongoDB authentication or connection string issue
- **Solution:** Verify `MONGO_URI` in `.env` matches your MongoDB setup

### MQTT Issues

#### Problem: "MQTT setup failed: Connection refused"
- **Cause:** MQTT broker not running
- **Solution:** Start MQTT broker FIRST:
  ```bash
  cd mqtt-broker
  npm start
  ```

#### Problem: Messages published but not received
- **Cause:** Topic mismatch or QoS issue
- **Check:** 
  - Topic must be exactly `espnow/samples`
  - QoS should be 1
  - Both publisher and subscriber must use same broker

#### Problem: Broker crashes under load
- **Cause:** Too many messages too quickly
- **Solution:** Aedes is lightweight; for production consider Mosquitto or HiveMQ

### Dashboard Issues

#### Problem: Dashboard shows "Waiting for data..."
- **Cause:** No data in MongoDB or WebSocket not connected
- **Checks:**
  1. Press ESP32 button to generate data
  2. Open browser console (F12) - check for errors
  3. Verify WebSocket shows "Connected" (green badge)
  4. Check MongoDB has samples: `db.samples.count()`

#### Problem: "Unauthorized" error when accessing REST API
- **Cause:** AUTH_TOKEN mismatch
- **Solution:** Set `AUTH_TOKEN=` (empty) in BOTH:
  - `host/node-backend/.env`
  - `host/python-gateway/.env` (CLOUD_AUTH_TOKEN)
- **Then restart:** Stop and start services

#### Problem: Dashboard shows old data only
- **Cause:** WebSocket connection failed, falling back to REST only
- **Check:** Browser console for WebSocket errors
- **Solution:** Verify WebSocket server is running on port 8081

### General Debugging

#### Check Service Health
```powershell
# Windows
.\scripts\health-check.ps1

# Linux
./scripts/health-check.sh
```

#### View Logs
- **Python Gateway:** Check terminal window or redirect to file
- **Node Services:** Check terminal windows
- **MongoDB:** 
  ```bash
  # Windows
  Get-Content "C:\Program Files\MongoDB\Server\7.0\log\mongod.log" -Tail 50
  
  # Linux
  sudo tail -f /var/log/mongodb/mongod.log
  ```

---

## 🔌 API Reference

### REST API

**Base URL:** `http://localhost:8080`

#### Endpoints

##### GET /v1/samples

Retrieve recent samples from MongoDB.

**Query Parameters:**
- `limit` (optional, default: 100): Number of results
- `skip` (optional, default: 0): Skip N results for pagination

**Example Request:**
```bash
curl "http://localhost:8080/v1/samples?limit=10"
```

**Example Response:**
```json
{
  "samples": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "batchId": "0xAF869913",
      "sessionMs": 10853,
      "samples": 1601,
      "dateYMD": 20251007,
      "timeHMS": 81621,
      "msec": 0,
      "lat": 34.140240,
      "lon": 35.663094,
      "alt": 227.60,
      "gpsFix": 1,
      "sats": 12,
      "ax": -8.23,
      "ay": -4.21,
      "az": -1.29,
      "gx": -0.050,
      "gy": 0.062,
      "gz": -0.232,
      "tempC": 27.75,
      "timestamp": "2025-10-07T08:16:23.027Z"
    }
  ],
  "count": 1
}
```

##### POST /v1/samples

Insert new sample into MongoDB.

**Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "batchId": "0xAF869913",
  "sessionMs": 10853,
  "samples": 1601,
  "lat": 34.140240,
  "lon": 35.663094,
  "alt": 227.60,
  "gpsFix": 1,
  "sats": 12,
  "ax": -8.23,
  "ay": -4.21,
  "az": -1.29,
  "gx": -0.050,
  "gy": 0.062,
  "gz": -0.232,
  "tempC": 27.75
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8080/v1/samples \
  -H "Content-Type: application/json" \
  -d '{"batchId":"0xTEST","lat":34.14,"lon":35.66,"gpsFix":1,"sats":8}'
```

**Success Response:**
```json
{
  "success": true,
  "id": "507f1f77bcf86cd799439011"
}
```

**Error Response:**
```json
{
  "error": "Unauthorized"
}
```

### WebSocket API

**URL:** `ws://localhost:8081`

#### Connection

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8081');

ws.onopen = () => {
  console.log('Connected to Airguard WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New sample received:', data);
  
  // Update UI with new data
  updateDashboard(data.data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
  // Attempt reconnection
  setTimeout(() => {
    connectWebSocket();
  }, 5000);
};
```

#### Message Format

**Sample Update:**
```json
{
  "type": "sample",
  "data": {
    "batchId": "0xAF869913",
    "sessionMs": 10853,
    "samples": 1601,
    "lat": 34.140240,
    "lon": 35.663094,
    "alt": 227.60,
    "gpsFix": 1,
    "sats": 12,
    "ax": -8.23,
    "ay": -4.21,
    "az": -1.29,
    "gx": -0.050,
    "gy": 0.062,
    "gz": -0.232,
    "tempC": 27.75,
    "timestamp": "2025-10-07T08:16:23.027Z"
  }
}
```

---

## 💻 Development

### Running Individual Services

**Python Gateway:**
```bash
cd host/python-gateway
python gateway_enhanced.py
```

**MQTT Broker:**
```bash
cd mqtt-broker
npm start
```

**Node.js Backend:**
```bash
cd host/node-backend
npm start
```

**MQTT-MongoDB Bridge:**
```bash
cd bridges/mqtt-mongo
node bridge.js
```

### Testing

**Test Python Gateway Parsing:**
```bash
cd host/python-gateway
python test_parser.py
```

**Test REST API:**
```bash
# Health check (if implemented)
curl http://localhost:8080/health

# Get samples
curl "http://localhost:8080/v1/samples?limit=5"

# Post sample
curl -X POST http://localhost:8080/v1/samples \
  -H "Content-Type: application/json" \
  -d '{"batchId":"0xTEST1234","lat":34.14,"lon":35.66,"gpsFix":1,"sats":8}'
```

**Test WebSocket:**
Open browser console on dashboard page:
```javascript
const ws = new WebSocket('ws://localhost:8081');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
```

**Test MQTT:**
```bash
# Install mosquitto-clients
sudo apt install mosquitto-clients  # Linux
choco install mosquitto  # Windows

# Subscribe to topic
mosquitto_sub -h localhost -t "espnow/samples" -v

# Publish test message
mosquitto_pub -h localhost -t "espnow/samples" -m '{"batchId":"0xTEST"}'
```

### Code Style

**Python:**
- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings

**JavaScript:**
- Use ES6+ features
- Async/await for asynchronous code
- JSDoc comments for functions

### Adding New Features

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Make changes**
4. **Test thoroughly**
5. **Commit:** `git commit -m 'Add amazing feature'`
6. **Push:** `git push origin feature/amazing-feature`
7. **Open Pull Request**

---

## 🚀 Production Deployment

### Linux (systemd services)

#### 1. Copy Service Files

```bash
sudo cp systemd/*.service /etc/systemd/system/
```

#### 2. Edit Service Files

Update paths in each service file to match your installation:

```bash
sudo nano /etc/systemd/system/airguard-gateway.service
```

Example changes:
```ini
[Service]
WorkingDirectory=/home/youruser/esp32dongle/host/python-gateway
ExecStart=/home/youruser/esp32dongle/host/python-gateway/venv/bin/python gateway_enhanced.py
User=youruser
```

#### 3. Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable airguard-mqtt-broker
sudo systemctl enable airguard-backend
sudo systemctl enable airguard-mqtt-bridge
sudo systemctl enable airguard-gateway

# Start services
sudo systemctl start airguard-mqtt-broker
sudo systemctl start airguard-backend
sudo systemctl start airguard-mqtt-bridge
sudo systemctl start airguard-gateway
```

#### 4. Check Status

```bash
# Check all services
sudo systemctl status airguard-*

# View logs
journalctl -u airguard-gateway -f
journalctl -u airguard-backend -f
```

### Windows (Task Scheduler)

#### 1. Create Startup Task

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. **Name:** "Airguard Services"
4. **Trigger:** At startup
5. **Action:** Start a program
6. **Program:** `powershell.exe`
7. **Arguments:** `-File "C:\Users\Admin\esp32dongle\start-services.ps1"`
8. **Finish**

#### 2. Configure Task Settings

- ✅ Run with highest privileges
- ✅ Run whether user is logged on or not
- ✅ Hidden (optional)

### Docker Deployment

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    container_name: airguard-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    restart: unless-stopped

  mqtt-broker:
    build: ./mqtt-broker
    container_name: airguard-mqtt
    ports:
      - "1883:1883"
    restart: unless-stopped

  backend:
    build: ./host/node-backend
    container_name: airguard-backend
    ports:
      - "8080:8080"
      - "8081:8081"
    environment:
      - MONGO_URI=mongodb://mongodb:27017
      - MONGO_DB=airguard
    depends_on:
      - mongodb
    restart: unless-stopped

  mqtt-bridge:
    build: ./bridges/mqtt-mongo
    container_name: airguard-bridge
    environment:
      - MQTT_BROKER=mqtt://mqtt-broker:1883
      - MONGO_URI=mongodb://mongodb:27017
    depends_on:
      - mongodb
      - mqtt-broker
    restart: unless-stopped

volumes:
  mongo-data:
```

**Build and run:**
```bash
docker-compose up -d
```

**Note:** Python gateway runs on host (needs USB serial access)

---

## 📊 Monitoring & Logs

### Health Check Script

**Windows:**
```powershell
.\scripts\health-check.ps1
```

**Linux:**
```bash
chmod +x scripts/health-check.sh
./scripts/health-check.sh
```

**Expected Output:**
```
[OK] MongoDB: Running (port 27017)
[OK] MQTT Broker: Running (port 1883)
[OK] Node Backend: Running (port 8080)
[OK] WebSocket: Running (port 8081)
[OK] Python Gateway: Running (COM12)
```

### Viewing Logs

**Python Gateway:**
```bash
# Redirect to file
python gateway_enhanced.py > logs/gateway.log 2>&1

# Tail live logs
tail -f logs/gateway.log
```

**Node.js Services:**
```bash
# Backend
cd host/node-backend
npm start > logs/backend.log 2>&1

# MQTT Broker
cd mqtt-broker
npm start > logs/mqtt.log 2>&1

# Bridge
cd bridges/mqtt-mongo
node bridge.js > logs/bridge.log 2>&1
```

**systemd Logs (Linux):**
```bash
# View logs
journalctl -u airguard-gateway -f
journalctl -u airguard-backend -n 100

# Filter by time
journalctl -u airguard-gateway --since "1 hour ago"
```

### Performance Metrics

**MongoDB Stats:**
```bash
mongosh
use airguard
db.samples.stats()
db.samples.count()
db.samples.totalSize()
```

**System Resources:**
```bash
# Linux
htop
# or
top

# Windows
# Task Manager → Performance tab
```

**Network Usage:**
```bash
# Linux
iftop
netstat -i

# Windows
# Resource Monitor → Network tab
```

---

## 🔐 Security

### Production Security Checklist

#### ✅ Authentication & Authorization

1. **Enable AUTH_TOKEN:**
   ```env
   # host/node-backend/.env
   AUTH_TOKEN=your-strong-random-token-here
   
   # host/python-gateway/.env
   CLOUD_AUTH_TOKEN=your-strong-random-token-here
   ```

2. **MongoDB Authentication:**
   ```bash
   # Create admin user
   mongosh
   use admin
   db.createUser({
     user: "airguard_admin",
     pwd: "strong_password_here",
     roles: ["readWrite", "dbAdmin"]
   })
   
   # Update connection string
   MONGO_URI=mongodb://airguard_admin:password@localhost:27017/airguard
   ```

3. **MQTT Username/Password:**
   ```env
   # Configure in .env files
   MQTT_USERNAME=airguard_user
   MQTT_PASSWORD=strong_mqtt_password
   ```

#### ✅ Network Security

1. **Use HTTPS for REST API:**
   - Set up reverse proxy (nginx or Apache)
   - Obtain SSL certificate (Let's Encrypt)
   
   **nginx example:**
   ```nginx
   server {
       listen 443 ssl;
       server_name airguard.example.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location /api/ {
           proxy_pass http://localhost:8080/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Use WSS for WebSocket:**
   ```nginx
   location /ws/ {
       proxy_pass http://localhost:8081/;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

3. **Firewall Rules:**
   ```bash
   # Linux (ufw)
   sudo ufw allow 80/tcp      # HTTP
   sudo ufw allow 443/tcp     # HTTPS
   sudo ufw deny 27017/tcp    # MongoDB (internal only)
   sudo ufw deny 1883/tcp     # MQTT (internal only)
   sudo ufw deny 8080/tcp     # Backend (behind nginx)
   sudo ufw enable
   ```

#### ✅ Database Security

1. **Regular Backups:**
   ```bash
   # MongoDB backup
   mongodump --db airguard --out /backups/$(date +%Y%m%d)
   
   # Automated daily backups (cron)
   0 2 * * * mongodump --db airguard --out /backups/$(date +\%Y\%m\%d)
   ```

2. **Role-Based Access Control:**
   ```javascript
   // Create read-only user for dashboard
   db.createUser({
     user: "dashboard_reader",
     pwd: "readonly_password",
     roles: [{role: "read", db: "airguard"}]
   })
   ```

#### ✅ Application Security

1. **CORS Configuration:**
   ```env
   # Only allow specific domains in production
   CORS_ORIGIN=https://airguard.example.com
   ```

2. **Rate Limiting:**
   Add to `host/node-backend/src/server.js`:
   ```javascript
   const rateLimit = require('express-rate-limit');
   
   const limiter = rateLimit({
     windowMs: 15 * 60 * 1000, // 15 minutes
     max: 100 // limit each IP to 100 requests per windowMs
   });
   
   app.use('/v1/', limiter);
   ```

3. **Input Validation:**
   - Validate all incoming data
   - Sanitize user inputs
   - Use schema validation (Joi, Yup)

---

## 📝 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Airguard Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Create new issue** with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, versions)
   - Relevant logs/screenshots

### Requesting Features

1. **Open issue** with "Feature Request" label
2. **Describe the feature:**
   - Use case
   - Proposed solution
   - Alternatives considered

### Submitting Pull Requests

1. **Fork** the repository
2. **Create branch:** `git checkout -b feature/your-feature-name`
3. **Make changes:**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation
4. **Test thoroughly:**
   - Run all tests
   - Test manually
5. **Commit:** `git commit -m 'Add: Your feature description'`
6. **Push:** `git push origin feature/your-feature-name`
7. **Open Pull Request:**
   - Clear title and description
   - Link related issues
   - Wait for review

---

## 📧 Support

Need help? Here's how to get support:

### Documentation
- **This README** - Comprehensive guide
- **Code comments** - Inline documentation
- **Example files** - `.env.example` templates

### Community
- **GitHub Issues** - Report bugs, request features
- **GitHub Discussions** - Ask questions, share ideas

### Contact
- **Email:** your-email@example.com
- **Discord:** [Your Discord Server]
- **Twitter:** [@YourHandle]

---

## 🎓 Additional Resources

### ESP32 & Arduino
- [ESP32-S3 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_en.pdf)
- [ESP-NOW Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_now.html)
- [Arduino ESP32 Board Support](https://github.com/espressif/arduino-esp32)

### Sensors
- [NEO-6M GPS Datasheet](https://www.u-blox.com/sites/default/files/products/documents/NEO-6_DataSheet_(GPS.G6-HW-09005).pdf)
- [MPU6050 Datasheet](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf)
- [TinyGPS++ Library](http://arduiniana.org/libraries/tinygpsplus/)
- [Adafruit MPU6050 Guide](https://learn.adafruit.com/mpu6050-6-dof-accelerometer-and-gyro)

### Protocols & Standards
- [MQTT v3.1.1 Specification](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html)
- [WebSocket Protocol (RFC 6455)](https://tools.ietf.org/html/rfc6455)
- [JSON Specification](https://www.json.org/json-en.html)

### Backend Technologies
- [Node.js Documentation](https://nodejs.org/en/docs/)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [Python Serial Communications](https://pythonhosted.org/pyserial/)
- [Paho MQTT Python Client](https://pypi.org/project/paho-mqtt/)

### Tutorials
- [ESP-NOW Tutorial](https://randomnerdtutorials.com/esp-now-esp32-arduino-ide/)
- [WebSocket with Node.js](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers)
- [MongoDB with Node.js](https://www.mongodb.com/languages/javascript)

---

## 🙏 Acknowledgments

- **Espressif Systems** - ESP32-S3 platform
- **Arduino Community** - Libraries and examples
- **Node.js & Python Communities** - Excellent documentation
- **Open Source Contributors** - All the amazing libraries used

---

## 📅 Changelog

### v1.0.0 (2025-10-07)
- ✅ Initial release
- ✅ ESP32-S3 firmware (sender + receiver)
- ✅ Python gateway with dual format parsing
- ✅ Node.js backend with REST API + WebSocket
- ✅ MongoDB integration
- ✅ MQTT broker and bridge
- ✅ Real-time web dashboard
- ✅ Comprehensive documentation
- ✅ Windows & Linux support
- ✅ Production deployment guides

---

**Built with ❤️ for IoT sensor data collection**

**Version:** 1.0.0  
**Last Updated:** October 7, 2025  
**Status:** Production Ready ✅
