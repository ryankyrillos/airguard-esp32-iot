// ===============================
// esp32s3-gps-mpu-button-sender.ino — FULL (with I2C log silence)
// ===============================
#include <WiFi.h>
#include <esp_wifi.h>
#include <esp_now.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <TinyGPSPlus.h>
#include <Adafruit_NeoPixel.h>
#include <cstring>
#include "esp_log.h"

// ---- Pins / config ----
#define LED_PIN    48
#define LED_COUNT  1
#define BUTTON_PIN 19
#define WIFI_CHANNEL 1
#define TEN_SEC_MS 10000UL

// I2C (MPU6050)
#define I2C_SDA  8
#define I2C_SCL  9
#define I2C_FREQ 400000

// GPS UART
#define GPS_RX   18
#define GPS_TX   17
#define GPS_BAUD 9600

// Receiver MAC (fixed)
uint8_t receiverMAC[6] = {0x48,0xCA,0x43,0x9A,0x48,0xD0};

// ---- Objects ----
Adafruit_NeoPixel rgb(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
HardwareSerial    GPSSerial(1);
Adafruit_MPU6050  mpu;
TinyGPSPlus       gps;

// ---- Packet (64 bytes) ----
typedef struct __attribute__((packed)) {
  uint32_t batchId, sessionMs, samples, dateYMD, timeHMS;
  uint16_t msec;
  float lat, lon, alt;
  uint8_t gpsFix, sats;
  float ax, ay, az, gx, gy, gz, tempC;
} SensorPacket;
static_assert(sizeof(SensorPacket)==64, "SensorPacket size mismatch");

// ---- State ----
bool peerAdded=false; volatile bool lastSendSuccess=false; unsigned long lastSendSuccessTs=0;
bool mpuReady=false; uint8_t mpuAddr=0; int mpuFailStreak=0, mpuWarmup=0; unsigned long mpuLastOK=0;

struct Avg {
  uint32_t n=0; float ax=0,ay=0,az=0,gx=0,gy=0,gz=0,tC=0;
  double lat=0,lon=0,alt=0; uint8_t sats=0;
  void reset(){ n=0; ax=ay=az=gx=gy=gz=tC=0; lat=lon=alt=0; sats=0; }
} avg;

unsigned long lastGpsCharMs=0, lastGpsUpdateMs=0;
unsigned long lastProbeMs=0, lastPingMs=0;

// ---- LED helpers ----
static inline void setColor(uint8_t r,uint8_t g,uint8_t b){ rgb.setPixelColor(0,rgb.Color(r,g,b)); rgb.show(); }
static inline void blink3(uint8_t r,uint8_t g,uint8_t b){ for(int i=0;i<3;i++){ setColor(r,g,b); delay(140); setColor(0,0,0); delay(140);} }

// ---- ESP-NOW ----
void onSent(const wifi_tx_info_t*, esp_now_send_status_t status){
  lastSendSuccess = (status==ESP_NOW_SEND_SUCCESS);
  if(lastSendSuccess) lastSendSuccessTs = millis();
}

// ---- I2C/MPU helpers ----
static inline bool i2cRead(uint8_t addr,uint8_t reg,uint8_t*val){
  Wire.beginTransmission(addr); Wire.write(reg);
  if(Wire.endTransmission(false)!=0) return false;
  if(Wire.requestFrom((int)addr,1)!=1) return false;
  *val=Wire.read(); return true;
}
static inline bool i2cWrite(uint8_t addr,uint8_t reg,uint8_t val){
  Wire.beginTransmission(addr); Wire.write(reg); Wire.write(val);
  return Wire.endTransmission(true)==0;
}
static bool probeMPU(uint8_t &addrOut){
  uint8_t id=0;
  if(i2cRead(0x68,0x75,&id) && (id==0x68||id==0x69)){ addrOut=0x68; return true; }
  if(i2cRead(0x69,0x75,&id) && (id==0x68||id==0x69)){ addrOut=0x69; return true; }
  return false;
}
static bool reinitMPU(uint8_t addr){
  mpu = Adafruit_MPU6050();
  if(!mpu.begin(addr)) return false;
  i2cWrite(addr,0x6B,0x01);
  mpuAddr=addr; mpuReady=true; mpuFailStreak=0; mpuLastOK=millis(); mpuWarmup=10;
  Serial.printf("[MPU] reinit @0x%02X\n", addr);
  return true;
}
static inline bool readMPU(float&ax,float&ay,float&az,float&gx,float&gy,float&gz,float&tC){
  sensors_event_t a,g,t;
  if(!mpu.getEvent(&a,&g,&t)){ mpuFailStreak++; return false; }
  mpuFailStreak=0; mpuLastOK=millis();
  ax=a.acceleration.x; ay=a.acceleration.y; az=a.acceleration.z;
  gx=g.gyro.x; gy=g.gyro.y; gz=g.gyro.z; tC=t.temperature; return true;
}
static inline void idleMPUUpdate(){
  if(!mpuReady) return;
  static unsigned long last=0; if(millis()-last<25) return; last=millis();
  float ax,ay,az,gx,gy,gz,tC; if(readMPU(ax,ay,az,gx,gy,gz,tC) && mpuWarmup>0) mpuWarmup--;
}
static inline bool mpuHealthy(){ return mpuReady && (millis()-mpuLastOK<1200); }

static inline void serviceMPU(bool duringMeasure){
  if(duringMeasure && mpuReady && mpuFailStreak>=4) mpuReady=false;
  if(millis()-lastProbeMs<1000) return; lastProbeMs=millis();
  uint8_t addr=0; bool present = probeMPU(addr);
  if(!present){ mpuReady=false; return; }
  if(!mpuReady) reinitMPU(addr);
}

// ---- GPS hotplug ----
static inline void pumpGPS(){
  while(GPSSerial.available()){
    lastGpsCharMs = millis();
    if(gps.encode(GPSSerial.read())){
      if(gps.location.isUpdated() || gps.satellites.isUpdated() ||
         gps.altitude.isUpdated() || gps.time.isUpdated() || gps.date.isUpdated()){
        lastGpsUpdateMs = millis();
      }
    }
  }
  if(gps.location.isUpdated()){ avg.lat=gps.location.lat(); avg.lon=gps.location.lng(); }
  if(gps.altitude.isUpdated()) avg.alt=gps.altitude.meters();
  if(gps.satellites.isUpdated()) avg.sats=gps.satellites.value();
}
static inline bool gpsPresent(){ return (millis()-lastGpsCharMs)   < 3000; }
static inline bool gpsFresh()  { return (millis()-lastGpsUpdateMs) < 3000; }
static inline bool gpsFixOK(){
  return gpsPresent() && gpsFresh() && gps.location.isValid() && gps.location.age()<2000 && gps.satellites.value()>=1;
}

// ---- Link heartbeat ----
const uint8_t PING=0xA5;
static inline void maybePing(){
  unsigned long now=millis();
  if(now-lastPingMs>=2000){ lastPingMs=now; if(peerAdded) esp_now_send(receiverMAC,&PING,1); }
}

// ---- Packet build ----
static inline uint32_t packDateYMD(){ if(!gps.date.isValid()) return 0; return (uint32_t)gps.date.year()*10000UL + (uint32_t)gps.date.month()*100UL + (uint32_t)gps.date.day(); }
static inline uint32_t packTimeHMS(){ if(!gps.time.isValid()) return 0; return (uint32_t)gps.time.hour()*10000UL + (uint32_t)gps.time.minute()*100UL + (uint32_t)gps.time.second(); }
static inline uint16_t packMS()     { if(!gps.time.isValid()) return 0; return (uint16_t)(gps.time.centisecond()*10); }
static inline void makePacket(SensorPacket& p,uint32_t dur,uint32_t id){
  p.batchId=id; p.sessionMs=dur; p.samples=avg.n;
  p.dateYMD=packDateYMD(); p.timeHMS=packTimeHMS(); p.msec=packMS();
  p.lat=avg.lat; p.lon=avg.lon; p.alt=avg.alt; p.sats=avg.sats; p.gpsFix=gpsFixOK()?1:0;
  if(avg.n){ p.ax=avg.ax/avg.n; p.ay=avg.ay/avg.n; p.az=avg.az/avg.n; p.gx=avg.gx/avg.n; p.gy=avg.gy/avg.n; p.gz=avg.gz/avg.n; p.tempC=avg.tC/avg.n; }
  else { p.ax=p.ay=p.az=p.gx=p.gy=p.gz=p.tempC=0; }
}

// ---- Setup / Loop ----
bool measuring=false, notified10s=false; unsigned long pressStart=0, lastDebounce=0; bool lastBtn=HIGH;

void setup(){
  Serial.begin(115200);

  // Silence I2C driver logs completely
  esp_log_level_set("*", ESP_LOG_WARN);
  esp_log_level_set("i2c", ESP_LOG_NONE);
  esp_log_level_set("i2c.master", ESP_LOG_NONE);
  esp_log_level_set("i2c_hal", ESP_LOG_NONE);

  Wire.begin(I2C_SDA,I2C_SCL,I2C_FREQ); Wire.setTimeOut(50);
  rgb.begin(); rgb.setBrightness(40); rgb.show();
  pinMode(BUTTON_PIN,INPUT_PULLUP);
  GPSSerial.begin(GPS_BAUD, SERIAL_8N1, GPS_RX, GPS_TX);

  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  if(esp_now_init()==ESP_OK){
    esp_now_register_send_cb(onSent);
    esp_now_peer_info_t peer{}; memcpy(peer.peer_addr,receiverMAC,6);
    peer.channel=WIFI_CHANNEL; peer.encrypt=false;
    if(esp_now_add_peer(&peer)==ESP_OK) peerAdded=true;
  }
  uint8_t addr; if(probeMPU(addr)) reinitMPU(addr);
  Serial.print("[MAC] STA="); Serial.println(WiFi.macAddress());
}

void loop(){
  pumpGPS();
  idleMPUUpdate();

  bool linkOK = peerAdded && (lastSendSuccessTs!=0) && (millis()-lastSendSuccessTs<5000);

  // Status LED (idle)
  if(!measuring){
    if(!peerAdded || !linkOK) setColor(255,255,255);              // WHITE steady
    else if(gpsFixOK() && mpuHealthy()) setColor(0,0,255);        // BLUE steady
    else { bool on=((millis()/300)%2)==0; setColor(0,0,on?255:0);} // BLUE blink
  }

  maybePing();

  // Button (debounced)
  bool btn=digitalRead(BUTTON_PIN);
  if(btn!=lastBtn && millis()-lastDebounce>30){
    lastDebounce=millis(); lastBtn=btn;

    if(btn==LOW && !measuring){ measuring=true; notified10s=false; pressStart=millis(); avg.reset(); }

    if(btn==HIGH && measuring){
      unsigned long dur=millis()-pressStart;
      measuring=false;

      // ---- Hard gate: require link + sensors ready + GPS fix + ≥10s ----
      if(dur < TEN_SEC_MS){ Serial.println("[MEASURE] <10s → discard"); blink3(255,0,0); return; }
      if(!peerAdded || !linkOK){ Serial.println("[SEND] blocked: ESP-NOW not linked"); blink3(255,0,0); return; }
      if(!mpuHealthy()){ Serial.println("[SEND] blocked: MPU not ready"); blink3(255,0,0); return; }
      if(!gpsFixOK()){ Serial.println("[SEND] blocked: GPS no fix"); blink3(255,0,0); return; }

      SensorPacket pkt; makePacket(pkt,dur,esp_random());
      Serial.printf("[MEASURE] %lums, samples=%lu → send\n",dur,(unsigned long)avg.n);
      lastSendSuccess=false; esp_err_t e = esp_now_send(receiverMAC,(uint8_t*)&pkt,sizeof(pkt));
      Serial.printf("[SEND] call=%s\n", e==ESP_OK? "OK":"ERR");
      delay(30); Serial.println(lastSendSuccess? "[SEND] ACK":"[SEND] NO ACK");
    }
  }

  // While holding: RED blink until 10s, then GREEN ×3
  if(measuring){
    unsigned long elapsed=millis()-pressStart;
    if(elapsed<TEN_SEC_MS){ bool on=((millis()/180)%2)==0; setColor(on?255:0,0,0); }
    else if(!notified10s){ blink3(0,255,0); notified10s=true; }

    float ax,ay,az,gx,gy,gz,tC;
    if(mpuReady && readMPU(ax,ay,az,gx,gy,gz,tC)){
      if(mpuWarmup>0) mpuWarmup--;
      else { avg.ax+=ax; avg.ay+=ay; avg.az+=az; avg.gx+=gx; avg.gy+=gy; avg.gz+=gz; avg.tC+=tC; avg.n++; }
    }
  }

  serviceMPU(measuring);
  delay(5);
}
