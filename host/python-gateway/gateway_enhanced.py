#!/usr/bin/env python3
"""
Enhanced gateway that can parse both fenced block and JSON output from receiver
"""

import os
import sys
import json
import time
import sqlite3
import logging
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import serial
import paho.mqtt.client as mqtt
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
SERIAL_PORT = os.getenv('SERIAL_PORT', 'COM14')
SERIAL_BAUD = 115200
SQLITE_DB = os.getenv('SQLITE_DB', 'airguard.db')
CLOUD_POST_URL = os.getenv('CLOUD_POST_URL', '')
CLOUD_AUTH_TOKEN = os.getenv('CLOUD_AUTH_TOKEN', '')
MQTT_BROKER = os.getenv('MQTT_BROKER', '127.0.0.1')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'espnow/samples')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_QOS = int(os.getenv('MQTT_QOS', '1'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('airguard-gateway')


class AirguardGateway:
    """Main gateway class handling serial parsing and data forwarding"""
    
    def __init__(self):
        self.db_conn = None
        self.mqtt_client = None
        self.serial_port = None
        self.setup_database()
        self.setup_mqtt()
        
    def setup_database(self):
        """Initialize SQLite database with schema"""
        try:
            self.db_conn = sqlite3.connect(SQLITE_DB)
            cursor = self.db_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT UNIQUE NOT NULL,
                    session_ms INTEGER,
                    samples INTEGER,
                    date_ymd INTEGER,
                    time_hms INTEGER,
                    msec INTEGER,
                    lat REAL,
                    lon REAL,
                    alt REAL,
                    gps_fix INTEGER,
                    sats INTEGER,
                    ax REAL,
                    ay REAL,
                    az REAL,
                    gx REAL,
                    gy REAL,
                    gz REAL,
                    temp_c REAL,
                    received_ts TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_batch_id ON samples(batch_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_received_ts ON samples(received_ts)')
            self.db_conn.commit()
            logger.info(f"SQLite database initialized: {SQLITE_DB}")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            sys.exit(1)
    
    def setup_mqtt(self):
        """Initialize MQTT client if configured"""
        if not MQTT_BROKER:
            logger.info("MQTT not configured, skipping")
            return
        
        try:
            self.mqtt_client = mqtt.Client(client_id=f"airguard-gateway-{int(time.time())}")
            
            if MQTT_USERNAME and MQTT_PASSWORD:
                self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            logger.info(f"MQTT client connecting to {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            logger.error(f"MQTT setup failed: {e}")
            self.mqtt_client = None
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected successfully")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning(f"MQTT disconnected with code {rc}")
    
    def parse_json_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON line from receiver (faster method)"""
        try:
            if line.startswith('JSON:'):
                line = line[5:].strip()
            
            data = json.loads(line)
            
            # Convert hex batchId to string without 0x prefix
            if 'batchId' in data and isinstance(data['batchId'], str):
                data['batchId'] = data['batchId'].replace('0x', '').replace('0X', '').upper()
            
            data['receivedTs'] = datetime.now(timezone.utc).isoformat()
            return data
            
        except json.JSONDecodeError:
            return None
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            return None
    
    def parse_packet(self, lines: list) -> Optional[Dict[str, Any]]:
        """
        Parse the fenced block output from receiver (legacy method)
        """
        try:
            data = {}
            
            for line in lines:
                line = line.strip()
                
                # Line 1: Batch | Duration | Samples
                if 'Batch:' in line:
                    m = re.search(r'Batch:\s*0x([0-9A-Fa-f]+)', line)
                    if m:
                        data['batchId'] = m.group(1).upper()
                    m = re.search(r'Duration:\s*(\d+)', line)
                    if m:
                        data['sessionMs'] = int(m.group(1))
                    m = re.search(r'Samples:\s*(\d+)', line)
                    if m:
                        data['samples'] = int(m.group(1))
                
                # Line 2: GPS Fix, Sats, Date, Time
                elif 'GPS Fix:' in line:
                    m = re.search(r'GPS Fix:\s*(\d+)', line)
                    if m:
                        data['gpsFix'] = int(m.group(1))
                    m = re.search(r'Sats:\s*(\d+)', line)
                    if m:
                        data['sats'] = int(m.group(1))
                    m = re.search(r'Date:\s*(\d+)', line)
                    if m:
                        data['dateYMD'] = int(m.group(1))
                    m = re.search(r'Time:\s*(\d+)\.(\d+)', line)
                    if m:
                        data['timeHMS'] = int(m.group(1))
                        data['msec'] = int(m.group(2))
                
                # Line 3: Lat, Lon, Alt
                elif 'Lat:' in line:
                    m = re.search(r'Lat:\s*([-\d.]+)', line)
                    if m:
                        data['lat'] = float(m.group(1))
                    m = re.search(r'Lon:\s*([-\d.]+)', line)
                    if m:
                        data['lon'] = float(m.group(1))
                    m = re.search(r'Alt:\s*([-\d.]+)', line)
                    if m:
                        data['alt'] = float(m.group(1))
                
                # Line 4: Accel
                elif 'Accel' in line:
                    m = re.search(r'X:\s*([-\d.]+)\s+Y:\s*([-\d.]+)\s+Z:\s*([-\d.]+)', line)
                    if m:
                        data['ax'] = float(m.group(1))
                        data['ay'] = float(m.group(2))
                        data['az'] = float(m.group(3))
                
                # Line 5: Gyro
                elif 'Gyro' in line:
                    m = re.search(r'X:\s*([-\d.]+)\s+Y:\s*([-\d.]+)\s+Z:\s*([-\d.]+)', line)
                    if m:
                        data['gx'] = float(m.group(1))
                        data['gy'] = float(m.group(2))
                        data['gz'] = float(m.group(3))
                
                # Line 6: Temp
                elif 'Temp:' in line:
                    m = re.search(r'Temp:\s*([-\d.]+)', line)
                    if m:
                        data['tempC'] = float(m.group(1))
            
            # Validate required fields
            required = ['batchId', 'sessionMs', 'samples']
            if all(k in data for k in required):
                data['receivedTs'] = datetime.now(timezone.utc).isoformat()
                return data
            else:
                logger.warning(f"Incomplete packet data: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def store_to_sqlite(self, data: Dict[str, Any]) -> bool:
        """Store parsed packet to SQLite"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO samples (
                    batch_id, session_ms, samples, date_ymd, time_hms, msec,
                    lat, lon, alt, gps_fix, sats,
                    ax, ay, az, gx, gy, gz, temp_c, received_ts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('batchId'),
                data.get('sessionMs'),
                data.get('samples'),
                data.get('dateYMD', 0),
                data.get('timeHMS', 0),
                data.get('msec', 0),
                data.get('lat', 0.0),
                data.get('lon', 0.0),
                data.get('alt', 0.0),
                data.get('gpsFix', 0),
                data.get('sats', 0),
                data.get('ax', 0.0),
                data.get('ay', 0.0),
                data.get('az', 0.0),
                data.get('gx', 0.0),
                data.get('gy', 0.0),
                data.get('gz', 0.0),
                data.get('tempC', 0.0),
                data.get('receivedTs')
            ))
            self.db_conn.commit()
            logger.info(f"SQLite stored: {data['batchId']}")
            return True
        except Exception as e:
            logger.error(f"SQLite insert failed: {e}")
            return False
    
    def post_to_cloud(self, data: Dict[str, Any]) -> bool:
        """POST packet to cloud REST API"""
        if not CLOUD_POST_URL:
            return True  # No-op if not configured
        
        try:
            headers = {'Content-Type': 'application/json'}
            if CLOUD_AUTH_TOKEN:
                headers['Authorization'] = f'Bearer {CLOUD_AUTH_TOKEN}'
            
            response = requests.post(
                CLOUD_POST_URL,
                json=data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code in (200, 201):
                logger.info(f"Cloud POST success: {data['batchId']}")
                return True
            else:
                logger.error(f"Cloud POST failed [{response.status_code}]: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Cloud POST error: {e}")
            return False
    
    def publish_to_mqtt(self, data: Dict[str, Any]) -> bool:
        """Publish packet to MQTT broker"""
        if not self.mqtt_client:
            return True  # No-op if not configured
        
        try:
            payload = json.dumps(data)
            result = self.mqtt_client.publish(MQTT_TOPIC, payload, qos=MQTT_QOS)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"MQTT published: {data['batchId']}")
                return True
            else:
                logger.error(f"MQTT publish failed: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")
            return False
    
    def process_packet(self, data: Dict[str, Any]):
        """Process a complete packet through all pipelines"""
        logger.info(f"Processing packet {data['batchId']} ({data['samples']} samples)")
        
        # Store locally
        self.store_to_sqlite(data)
        
        # Forward to cloud
        self.post_to_cloud(data)
        
        # Publish to MQTT
        self.publish_to_mqtt(data)
    
    def run(self):
        """Main loop: read serial and process packets"""
        try:
            self.serial_port = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
            logger.info(f"Serial port opened: {SERIAL_PORT} @ {SERIAL_BAUD}")
        except Exception as e:
            logger.error(f"Failed to open serial port {SERIAL_PORT}: {e}")
            sys.exit(1)
        
        buffer = []
        in_packet = False
        
        logger.info("Gateway running. Waiting for packets...")
        logger.info("Supports both JSON and fenced block formats")
        
        try:
            while True:
                try:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        continue
                    
                    # Echo to console
                    print(line)
                    
                    # Try JSON first (fast path)
                    if line.startswith('JSON:') or line.startswith('{'):
                        data = self.parse_json_line(line)
                        if data:
                            self.process_packet(data)
                            continue
                    
                    # Fall back to fenced block parsing
                    if line == "=== Received Data ===":
                        in_packet = True
                        buffer = [line]
                    elif in_packet:
                        buffer.append(line)
                        if line == "====================":
                            # Complete packet received
                            in_packet = False
                            data = self.parse_packet(buffer)
                            if data:
                                self.process_packet(data)
                            buffer = []
                    
                except serial.SerialException as e:
                    logger.error(f"Serial error: {e}")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean shutdown"""
        logger.info("Cleaning up...")
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.db_conn:
            self.db_conn.close()
        
        logger.info("Gateway stopped")


def main():
    gateway = AirguardGateway()
    gateway.run()


if __name__ == '__main__':
    main()
