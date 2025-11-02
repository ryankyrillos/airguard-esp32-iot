# 📌 ESP32-S3 Pin Connections Guide

## Complete Wiring Diagram for Airguard Sender

Based on `esp32s3-gps-mpu-button-sender.ino`

---

## 🎯 Quick Reference Table

| Component | Component Pin | ESP32-S3 Pin | GPIO | Notes |
|-----------|---------------|--------------|------|-------|
| **GPS (NEO-6M)** | TX | RX | **GPIO 18** | GPS transmits, ESP32 receives |
| **GPS (NEO-6M)** | RX | TX | **GPIO 17** | ESP32 transmits, GPS receives |
| **GPS (NEO-6M)** | VCC | 3.3V or 5V | - | Check GPS module voltage |
| **GPS (NEO-6M)** | GND | GND | - | Common ground |
| **MPU6050** | SDA | SDA | **GPIO 8** | I2C Data line |
| **MPU6050** | SCL | SCL | **GPIO 9** | I2C Clock line |
| **MPU6050** | VCC | 3.3V | - | Power supply |
| **MPU6050** | GND | GND | - | Common ground |
| **MPU6050** | AD0 | GND or 3.3V | - | I2C address select (see below) |
| **NeoPixel LED** | DIN | LED_PIN | **GPIO 48** | WS2812 data input |
| **NeoPixel LED** | VCC | 5V or 3.3V | - | Power (check LED spec) |
| **NeoPixel LED** | GND | GND | - | Common ground |
| **Button** | One side | BUTTON_PIN | **GPIO 19** | Input with internal pull-up |
| **Button** | Other side | GND | - | Button grounds the pin when pressed |

---

## 🔌 Detailed Connections

### 1. GPS Module (NEO-6M) - UART Connection

```
GPS NEO-6M          ESP32-S3
┌─────────────┐     ┌──────────┐
│             │     │          │
│  VCC    ────┼─────┤ 3.3V/5V  │  (Check GPS voltage requirement)
│  GND    ────┼─────┤ GND      │
│  TX     ────┼─────┤ GPIO 18  │  (RX on ESP32)
│  RX     ────┼─────┤ GPIO 17  │  (TX on ESP32)
│             │     │          │
└─────────────┘     └──────────┘
```

**Code reference:**
```cpp
#define GPS_RX   18    // ESP32 receives on GPIO 18
#define GPS_TX   17    // ESP32 transmits on GPIO 17
#define GPS_BAUD 9600  // Baud rate

HardwareSerial GPSSerial(1);  // Uses UART1
```

**UART Configuration:**
- **Baud Rate:** 9600
- **Hardware Serial:** UART1
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1

---

### 2. MPU6050 IMU Sensor - I2C Connection

```
MPU6050             ESP32-S3
┌─────────────┐     ┌──────────┐
│             │     │          │
│  VCC    ────┼─────┤ 3.3V     │
│  GND    ────┼─────┤ GND      │
│  SDA    ────┼─────┤ GPIO 8   │
│  SCL    ────┼─────┤ GPIO 9   │
│  AD0    ────┼─────┤ GND      │  (For 0x68 address)
│             │     │          │
└─────────────┘     └──────────┘
```

**Code reference:**
```cpp
#define I2C_SDA  8       // I2C Data
#define I2C_SCL  9       // I2C Clock
#define I2C_FREQ 400000  // 400kHz (Fast Mode)
```

**I2C Configuration:**
- **Frequency:** 400 kHz (Fast Mode)
- **Default Address:** 0x68 (AD0 to GND)
- **Alternate Address:** 0x69 (AD0 to 3.3V)
- **Protocol:** I2C (TWI)

**Pull-up Resistors:**
- Most MPU6050 breakout boards have built-in 4.7kΩ pull-ups
- If not, add 4.7kΩ resistors from SDA/SCL to 3.3V

---

### 3. NeoPixel RGB LED (WS2812)

```
NeoPixel            ESP32-S3
┌─────────────┐     ┌──────────┐
│             │     │          │
│  VCC    ────┼─────┤ 5V/3.3V  │  (Check LED voltage)
│  GND    ────┼─────┤ GND      │
│  DIN    ────┼─────┤ GPIO 48  │  (Data input)
│             │     │          │
└─────────────┘     └──────────┘
```

**Code reference:**
```cpp
#define LED_PIN   48     // NeoPixel data pin
#define LED_COUNT 1      // Number of LEDs

Adafruit_NeoPixel rgb(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
```

**Configuration:**
- **Type:** WS2812 / WS2812B
- **Protocol:** NEO_GRB + NEO_KHZ800
- **Count:** 1 LED
- **Data Pin:** GPIO 48

**Optional:** Add a 470Ω resistor between GPIO 48 and DIN for signal protection.

---

### 4. Button (Momentary Push Button)

```
Button              ESP32-S3
┌─────────────┐     ┌──────────┐
│             │     │          │
│  Terminal 1 ┼─────┤ GPIO 19  │  (Internal pull-up enabled)
│  Terminal 2 ┼─────┤ GND      │
│             │     │          │
└─────────────┘     └──────────┘
```

**Code reference:**
```cpp
#define BUTTON_PIN 19

pinMode(BUTTON_PIN, INPUT_PULLUP);  // Internal pull-up resistor
```

**Configuration:**
- **Type:** Momentary (normally open)
- **Pin Mode:** INPUT_PULLUP
- **Logic:** Active LOW (pressed = LOW, released = HIGH)

**No external resistor needed** - uses internal pull-up.

---

## ⚡ Power Supply Recommendations

### Power Requirements

| Component | Voltage | Current | Notes |
|-----------|---------|---------|-------|
| ESP32-S3 | 3.3V (5V USB) | ~200-500mA | Peak current during WiFi/ESP-NOW |
| GPS NEO-6M | 3.3V - 5V | ~30-50mA | Check module specifications |
| MPU6050 | 3.3V - 5V | ~3.5mA | Very low power |
| NeoPixel | 5V (or 3.3V) | ~60mA per LED (max) | At full white brightness |
| **Total** | **5V USB** | **~300-650mA** | **Typical operation** |

### Power Options

**Option 1: USB Power (Recommended for development)**
```
USB 5V → ESP32-S3 Dev Board
  ├─ 3.3V regulator → MPU6050 (VCC)
  ├─ 3.3V regulator → GPS (VCC) if 3.3V module
  ├─ 5V → GPS (VCC) if 5V module
  └─ 5V or 3.3V → NeoPixel (VCC)
```

**Option 2: Battery Power**
```
LiPo 3.7V → ESP32-S3 VBAT pin
  └─ Use onboard 3.3V regulator for sensors
```

---

## 🧪 I2C Address Configuration

The MPU6050 supports two I2C addresses:

### Address 0x68 (Default)
```
MPU6050 AD0 pin → GND
```

### Address 0x69 (Alternate)
```
MPU6050 AD0 pin → 3.3V
```

**The code automatically detects both:**
```cpp
static bool probeMPU(uint8_t &addrOut){
  uint8_t id=0;
  if(i2cRead(0x68,0x75,&id) && (id==0x68||id==0x69)){ addrOut=0x68; return true; }
  if(i2cRead(0x69,0x75,&id) && (id==0x68||id==0x69)){ addrOut=0x69; return true; }
  return false;
}
```

---

## 🔧 ESP-NOW Configuration

### Receiver MAC Address

The sender is configured to communicate with a specific receiver:

```cpp
// Hardcoded receiver MAC address
uint8_t receiverMAC[6] = {0x48,0xCA,0x43,0x9A,0x48,0xD0};
```

**To find your receiver's MAC address:**
1. Upload the receiver firmware
2. Open Serial Monitor (115200 baud)
3. Look for: `MAC Address: XX:XX:XX:XX:XX:XX`
4. Update the `receiverMAC` array in sender code

**WiFi Channel:**
```cpp
#define WIFI_CHANNEL 1  // Both devices must use same channel
```

---

## 📊 Complete Pinout Summary

### ESP32-S3 Sender Pin Allocation

```
ESP32-S3 DevKit
┌─────────────────────────────────────┐
│                                     │
│  GPIO 48  →  NeoPixel LED (DIN)     │
│  GPIO 19  →  Button (INPUT_PULLUP)  │
│  GPIO 18  →  GPS RX (UART1 RX)      │
│  GPIO 17  →  GPS TX (UART1 TX)      │
│  GPIO 8   →  MPU6050 SDA (I2C)      │
│  GPIO 9   →  MPU6050 SCL (I2C)      │
│                                     │
│  3.3V     →  MPU6050 VCC            │
│  3.3V/5V  →  GPS VCC                │
│  5V/3.3V  →  NeoPixel VCC           │
│  GND      →  All GND pins           │
│                                     │
└─────────────────────────────────────┘
```

---

## 🛠️ Wiring Tips

### Do's ✅

1. **Use solid connections** - Breadboard or soldered connections
2. **Keep I2C wires short** - Minimize interference (< 20cm ideal)
3. **Common ground** - All components share GND with ESP32
4. **Check voltages** - Verify GPS and sensors voltage requirements
5. **Secure GPS antenna** - For best satellite reception
6. **Test incrementally** - Add one component at a time

### Don'ts ❌

1. **Don't cross-wire** - Double-check TX→RX, RX→TX
2. **Don't exceed voltage** - Use 3.3V for 3.3V devices
3. **Don't share I2C addresses** - Each I2C device needs unique address
4. **Don't power from GPIO** - Use dedicated power pins
5. **Don't skip pull-ups** - I2C requires pull-up resistors
6. **Don't use long wires** - Keep connections short and neat

---

## 🧪 Testing Individual Components

### Test GPS (Serial Monitor @ 115200)

```cpp
void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, 18, 17);  // RX=18, TX=17
}

void loop() {
  while(Serial2.available()) {
    Serial.write(Serial2.read());
  }
}
```

**Expected output:** NMEA sentences like `$GPGGA,...`

### Test MPU6050 (I2C Scanner)

```cpp
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(8, 9);  // SDA=8, SCL=9
  
  Serial.println("Scanning I2C...");
  for(uint8_t addr=1; addr<127; addr++) {
    Wire.beginTransmission(addr);
    if(Wire.endTransmission() == 0) {
      Serial.printf("Found device at 0x%02X\n", addr);
    }
  }
}
```

**Expected output:** `Found device at 0x68` (or 0x69)

### Test NeoPixel

```cpp
#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel rgb(1, 48, NEO_GRB + NEO_KHZ800);

void setup() {
  rgb.begin();
  rgb.setPixelColor(0, rgb.Color(255, 0, 0));  // Red
  rgb.show();
}
```

**Expected output:** LED glows red

---

## 📷 Visual Wiring Diagram

```
                    ESP32-S3 Dev Board
                    ┌──────────────┐
                    │              │
                    │    USB-C     │
                    │      ║       │
    ┌───────────────┼──────║───────┼───────────────┐
    │               │              │               │
    │  GPS NEO-6M   │              │   MPU6050     │
    │  ┌────────┐   │              │   ┌────────┐  │
    │  │ TX  ───┼───┼─ GPIO 18     │   │ SDA ───┼──┼─ GPIO 8
    │  │ RX  ───┼───┼─ GPIO 17     │   │ SCL ───┼──┼─ GPIO 9
    │  │ VCC ───┼───┼─ 3.3V/5V     │   │ VCC ───┼──┼─ 3.3V
    │  │ GND ───┼───┼─ GND         │   │ GND ───┼──┼─ GND
    │  └────────┘   │              │   └────────┘  │
    │               │              │               │
    │  NeoPixel     │              │   Button      │
    │  ┌────────┐   │              │   ┌────────┐  │
    │  │ DIN ───┼───┼─ GPIO 48     │   │  Pin1──┼──┼─ GPIO 19
    │  │ VCC ───┼───┼─ 5V/3.3V     │   │  Pin2──┼──┼─ GND
    │  │ GND ───┼───┼─ GND         │   └────────┘  │
    │  └────────┘   │              │               │
    └───────────────┼──────────────┼───────────────┘
                    │              │
                    └──────────────┘
```

---

## 🔍 Troubleshooting

### GPS Issues

**No GPS data / LED stays white:**
- ✅ Check TX/RX not swapped
- ✅ Verify baud rate (9600)
- ✅ GPS needs clear sky view
- ✅ Cold start can take 5-10 minutes

### MPU6050 Issues

**MPU not detected / I2C errors:**
- ✅ Check SDA/SCL connections
- ✅ Verify power (3.3V on VCC)
- ✅ Check pull-up resistors present
- ✅ Try alternate address (0x69)

### NeoPixel Issues

**LED not lighting up:**
- ✅ Check power (5V recommended)
- ✅ Verify GPIO 48 connection
- ✅ Add 470Ω resistor if needed
- ✅ Check common ground

### Button Issues

**Button not responding:**
- ✅ Verify GPIO 19 connection
- ✅ Check button connects to GND
- ✅ Test button continuity
- ✅ First press needs 10-second hold

---

## 📚 Component Datasheets

- **ESP32-S3:** [Espressif Documentation](https://www.espressif.com/en/products/socs/esp32-s3)
- **NEO-6M GPS:** [u-blox NEO-6 Datasheet](https://www.u-blox.com/en/product/neo-6-series)
- **MPU6050:** [InvenSense Datasheet](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/)
- **WS2812:** [WorldSemi WS2812 Datasheet](https://cdn-shop.adafruit.com/datasheets/WS2812.pdf)

---

**Built with ❤️ for reliable IoT sensor integration**
