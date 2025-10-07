// ===============================
// esp32s3-gps-mpu-button-receiver.ino — Enhanced with JSON output
// Prints every field of the 64B packet in both human-readable and JSON formats.
// ===============================
#include <WiFi.h>
#include <esp_wifi.h>
#include <esp_now.h>
#include <cstring>

#define WIFI_CHANNEL 1
#define EMIT_JSON true  // Set to false to disable JSON output

static const uint8_t HEARTBEAT = 0xA5;
// Lock to a specific sender if desired; zeros = accept any
static const uint8_t SENDER_MAC[6] = {0,0,0,0,0,0};

typedef struct __attribute__((packed)) {
  uint32_t batchId, sessionMs, samples, dateYMD, timeHMS;
  uint16_t msec;
  float    lat, lon, alt;
  uint8_t  gpsFix, sats;
  float    ax, ay, az, gx, gy, gz, tempC;
} SensorPacket;
static_assert(sizeof(SensorPacket)==64, "SensorPacket size mismatch");

static inline bool macOK(const uint8_t src[6]){
  const uint8_t Z[6]={0,0,0,0,0,0};
  if(memcmp(SENDER_MAC,Z,6)==0) return true;
  return memcmp(src,SENDER_MAC,6)==0;
}

void printJSON(const SensorPacket &p) {
  Serial.print("{");
  Serial.printf("\"batchId\":\"0x%08lX\",", (unsigned long)p.batchId);
  Serial.printf("\"sessionMs\":%lu,", (unsigned long)p.sessionMs);
  Serial.printf("\"samples\":%lu,", (unsigned long)p.samples);
  Serial.printf("\"dateYMD\":%lu,", (unsigned long)p.dateYMD);
  Serial.printf("\"timeHMS\":%lu,", (unsigned long)p.timeHMS);
  Serial.printf("\"msec\":%u,", (unsigned)p.msec);
  Serial.printf("\"lat\":%.6f,", p.lat);
  Serial.printf("\"lon\":%.6f,", p.lon);
  Serial.printf("\"alt\":%.2f,", p.alt);
  Serial.printf("\"gpsFix\":%u,", p.gpsFix);
  Serial.printf("\"sats\":%u,", p.sats);
  Serial.printf("\"ax\":%.2f,", p.ax);
  Serial.printf("\"ay\":%.2f,", p.ay);
  Serial.printf("\"az\":%.2f,", p.az);
  Serial.printf("\"gx\":%.3f,", p.gx);
  Serial.printf("\"gy\":%.3f,", p.gy);
  Serial.printf("\"gz\":%.3f,", p.gz);
  Serial.printf("\"tempC\":%.2f", p.tempC);
  Serial.println("}");
}

void onReceive(const esp_now_recv_info_t *info, const uint8_t *data, int len){
  if(!macOK(info->src_addr)) return;
  if(len==1 && data[0]==HEARTBEAT) return;
  if(len!=(int)sizeof(SensorPacket)) { Serial.printf("Unexpected len=%d\n", len); return; }

  SensorPacket p; memcpy(&p,data,sizeof(p));
  
  // Human-readable output (fenced block)
  Serial.println("=== Received Data ===");
  Serial.printf("Batch: 0x%08lX | Duration: %lu ms | Samples: %lu\n",
                (unsigned long)p.batchId, (unsigned long)p.sessionMs, (unsigned long)p.samples);
  Serial.printf("GPS Fix: %u, Sats: %u | Date: %08lu | Time: %06lu.%03u\n",
                p.gpsFix, p.sats, (unsigned long)p.dateYMD, (unsigned long)p.timeHMS, (unsigned)p.msec);
  Serial.printf("Lat: %.6f  Lon: %.6f  Alt: %.2f m\n", p.lat, p.lon, p.alt);
  Serial.printf("Accel [m/s^2] X: %.2f  Y: %.2f  Z: %.2f\n", p.ax, p.ay, p.az);
  Serial.printf("Gyro  [rad/s] X: %.2f  Y: %.2f  Z: %.2f\n", p.gx, p.gy, p.gz);
  Serial.printf("Temp: %.2f °C\n", p.tempC);
  Serial.println("====================");
  
  // JSON output (for easy parsing)
  if (EMIT_JSON) {
    Serial.print("JSON: ");
    printJSON(p);
  }
}

void setup(){
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  if(esp_now_init()!=ESP_OK){ Serial.println("ESP-NOW init failed!"); return; }
  esp_now_register_recv_cb(onReceive);
  Serial.print("[MAC] STA="); Serial.println(WiFi.macAddress());
  Serial.println("Receiver ready");
}

void loop(){ }
