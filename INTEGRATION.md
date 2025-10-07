# 🔌 Custom Dashboard Integration Guide

> **Complete guide for integrating Airguard data into your own dashboard**

This guide explains how to access and consume data from the Airguard system in your own custom dashboard, whether it's a web app, mobile app, or other visualization platform.

---

## 📊 Table of Contents

1. [Data Access Methods](#data-access-methods)
2. [REST API Integration](#rest-api-integration)
3. [WebSocket Real-time Integration](#websocket-real-time-integration)
4. [Direct Database Access](#direct-database-access)
5. [MQTT Integration](#mqtt-integration)
6. [Data Schemas](#data-schemas)
7. [Example Implementations](#example-implementations)
8. [Deployment Architecture](#deployment-architecture)
9. [Security Configuration](#security-configuration)
10. [Performance Optimization](#performance-optimization)

---

## 🔑 Data Access Methods

The Airguard system provides **4 ways** to access sensor data:

| Method | Use Case | Real-time | Latency | Difficulty |
|--------|----------|-----------|---------|------------|
| **REST API** | Historical data, polling | ❌ No | ~100ms | ⭐ Easy |
| **WebSocket** | Real-time updates | ✅ Yes | <10ms | ⭐⭐ Medium |
| **MongoDB Direct** | Complex queries, analytics | ❌ No | ~50ms | ⭐⭐⭐ Advanced |
| **MQTT Subscribe** | Event-driven updates | ✅ Yes | <5ms | ⭐⭐ Medium |

---

## 🌐 REST API Integration

### Endpoint Overview

**Base URL:** `http://your-server-ip:8080`

#### 1. Get Recent Samples

```http
GET /v1/samples?limit=100&skip=0
```

**Query Parameters:**
- `limit` (optional, default: 100) - Number of records to return
- `skip` (optional, default: 0) - Number of records to skip (pagination)

**Example Request:**
```bash
curl "http://localhost:8080/v1/samples?limit=10"
```

**Response:**
```json
{
  "samples": [
    {
      "_id": "671234abcdef1234567890ab",
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

#### 2. Post New Sample (Optional - if you want to write data)

```http
POST /v1/samples
Content-Type: application/json
```

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

### JavaScript/React Integration

**Using Fetch API:**
```javascript
// Fetch latest 20 samples
async function getLatestSamples() {
  const response = await fetch('http://your-server:8080/v1/samples?limit=20');
  const data = await response.json();
  return data.samples;
}

// Usage in React
import { useEffect, useState } from 'react';

function Dashboard() {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://your-server:8080/v1/samples?limit=50');
        const data = await response.json();
        setSamples(data.samples);
      } catch (error) {
        console.error('Error fetching samples:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Optional: Poll every 5 seconds for updates
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Airguard Sensor Data</h1>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Temperature</th>
            <th>Satellites</th>
          </tr>
        </thead>
        <tbody>
          {samples.map((sample) => (
            <tr key={sample._id}>
              <td>{new Date(sample.timestamp).toLocaleString()}</td>
              <td>{sample.lat.toFixed(6)}</td>
              <td>{sample.lon.toFixed(6)}</td>
              <td>{sample.tempC}°C</td>
              <td>{sample.sats}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

**Using Axios:**
```javascript
import axios from 'axios';

const API_BASE = 'http://your-server:8080';

// Create API client
const airguardAPI = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Get samples with pagination
export const getSamples = async (limit = 100, skip = 0) => {
  const response = await airguardAPI.get('/v1/samples', {
    params: { limit, skip }
  });
  return response.data.samples;
};

// Usage
const samples = await getSamples(20, 0);
```

### Python Integration

```python
import requests
import pandas as pd

class AirguardClient:
    def __init__(self, base_url='http://localhost:8080'):
        self.base_url = base_url
    
    def get_samples(self, limit=100, skip=0):
        """Fetch samples from REST API"""
        url = f"{self.base_url}/v1/samples"
        params = {'limit': limit, 'skip': skip}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()['samples']
    
    def get_dataframe(self, limit=1000):
        """Get samples as pandas DataFrame"""
        samples = self.get_samples(limit=limit)
        df = pd.DataFrame(samples)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df

# Usage
client = AirguardClient('http://your-server:8080')
samples = client.get_samples(limit=50)

# As DataFrame for analysis
df = client.get_dataframe(limit=1000)
print(df.describe())
print(df[['lat', 'lon', 'tempC', 'sats']].head())
```

---

## ⚡ WebSocket Real-time Integration

### Connection Details

**WebSocket URL:** `ws://your-server-ip:8081`

**Message Format:**
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

### JavaScript/React Integration

**Vanilla JavaScript:**
```javascript
class AirguardWebSocket {
  constructor(url = 'ws://localhost:8081') {
    this.url = url;
    this.ws = null;
    this.reconnectDelay = 5000;
    this.listeners = [];
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WebSocket connected to Airguard');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample') {
        this.listeners.forEach(callback => callback(message.data));
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected. Reconnecting...');
      setTimeout(() => this.connect(), this.reconnectDelay);
    };
  }

  onSample(callback) {
    this.listeners.push(callback);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const airguard = new AirguardWebSocket('ws://your-server:8081');
airguard.connect();

airguard.onSample((sample) => {
  console.log('New sample received:', sample);
  
  // Update your dashboard
  updateMap(sample.lat, sample.lon);
  updateTemperature(sample.tempC);
  updateAcceleration(sample.ax, sample.ay, sample.az);
});
```

**React Hook:**
```javascript
import { useEffect, useState } from 'react';

function useAirguardWebSocket(url = 'ws://localhost:8081') {
  const [latestSample, setLatestSample] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample') {
        setLatestSample(message.data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      
      // Reconnect after 5 seconds
      setTimeout(() => {
        window.location.reload(); // Simple reconnect
      }, 5000);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { latestSample, isConnected };
}

// Usage in component
function LiveDashboard() {
  const { latestSample, isConnected } = useAirguardWebSocket('ws://your-server:8081');

  return (
    <div>
      <div>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>
      
      {latestSample && (
        <div>
          <h2>Latest Reading</h2>
          <p>Time: {new Date(latestSample.timestamp).toLocaleString()}</p>
          <p>Location: {latestSample.lat}, {latestSample.lon}</p>
          <p>Temperature: {latestSample.tempC}°C</p>
          <p>Satellites: {latestSample.sats}</p>
        </div>
      )}
    </div>
  );
}
```

**Vue.js Integration:**
```javascript
import { ref, onMounted, onUnmounted } from 'vue';

export function useAirguardWebSocket(url = 'ws://localhost:8081') {
  const latestSample = ref(null);
  const isConnected = ref(false);
  let ws = null;

  const connect = () => {
    ws = new WebSocket(url);

    ws.onopen = () => {
      isConnected.value = true;
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample') {
        latestSample.value = message.data;
      }
    };

    ws.onclose = () => {
      isConnected.value = false;
      setTimeout(connect, 5000); // Reconnect
    };
  };

  onMounted(connect);
  onUnmounted(() => {
    if (ws) ws.close();
  });

  return { latestSample, isConnected };
}
```

### Python Integration

```python
import asyncio
import websockets
import json

async def subscribe_to_airguard():
    uri = "ws://localhost:8081"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to Airguard WebSocket")
        
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('type') == 'sample':
                sample = data['data']
                print(f"New sample: Lat={sample['lat']}, Lon={sample['lon']}, Temp={sample['tempC']}°C")
                
                # Process sample in your application
                process_sample(sample)

def process_sample(sample):
    """Handle incoming sample data"""
    # Update database
    # Trigger alerts
    # Update visualization
    pass

# Run
asyncio.run(subscribe_to_airguard())
```

---

## 🗄️ Direct Database Access

### MongoDB Connection

**Connection String Format:**
```
mongodb://[username:password@]host[:port]/database
```

**Examples:**
```bash
# Local MongoDB (no auth)
mongodb://localhost:27017/airguard

# Local MongoDB (with auth)
mongodb://airguard-app:password@localhost:27017/airguard

# Remote MongoDB
mongodb://airguard-app:password@192.168.1.100:27017/airguard

# MongoDB Atlas (cloud)
mongodb+srv://airguard-app:password@cluster0.xxxxx.mongodb.net/airguard
```

### JavaScript/Node.js Integration

```javascript
const { MongoClient } = require('mongodb');

class AirguardDatabase {
  constructor(uri = 'mongodb://localhost:27017') {
    this.uri = uri;
    this.client = new MongoClient(uri);
    this.db = null;
  }

  async connect() {
    await this.client.connect();
    this.db = this.client.db('airguard');
    console.log('Connected to Airguard database');
  }

  async getLatestSamples(limit = 100) {
    const collection = this.db.collection('samples');
    return await collection
      .find({})
      .sort({ timestamp: -1 })
      .limit(limit)
      .toArray();
  }

  async getSamplesByDateRange(startDate, endDate) {
    const collection = this.db.collection('samples');
    return await collection
      .find({
        timestamp: {
          $gte: new Date(startDate),
          $lte: new Date(endDate)
        }
      })
      .sort({ timestamp: -1 })
      .toArray();
  }

  async getSamplesByLocation(lat, lon, radiusKm) {
    const collection = this.db.collection('samples');
    
    // Convert km to degrees (approximate)
    const radiusDegrees = radiusKm / 111;
    
    return await collection
      .find({
        lat: {
          $gte: lat - radiusDegrees,
          $lte: lat + radiusDegrees
        },
        lon: {
          $gte: lon - radiusDegrees,
          $lte: lon + radiusDegrees
        }
      })
      .toArray();
  }

  async getAggregatedStats() {
    const collection = this.db.collection('samples');
    
    return await collection.aggregate([
      {
        $group: {
          _id: null,
          avgTemp: { $avg: '$tempC' },
          maxTemp: { $max: '$tempC' },
          minTemp: { $min: '$tempC' },
          totalSamples: { $sum: 1 },
          avgSatellites: { $avg: '$sats' }
        }
      }
    ]).toArray();
  }

  async close() {
    await this.client.close();
  }
}

// Usage
const db = new AirguardDatabase('mongodb://localhost:27017');
await db.connect();

const latest = await db.getLatestSamples(50);
const stats = await db.getAggregatedStats();

console.log('Latest samples:', latest);
console.log('Statistics:', stats);

await db.close();
```

### Python Integration (pymongo)

```python
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd

class AirguardDatabase:
    def __init__(self, uri='mongodb://localhost:27017'):
        self.client = MongoClient(uri)
        self.db = self.client['airguard']
        self.samples = self.db['samples']
    
    def get_latest_samples(self, limit=100):
        """Get latest N samples"""
        cursor = self.samples.find().sort('timestamp', -1).limit(limit)
        return list(cursor)
    
    def get_samples_by_date_range(self, start_date, end_date):
        """Get samples within date range"""
        query = {
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date
            }
        }
        cursor = self.samples.find(query).sort('timestamp', -1)
        return list(cursor)
    
    def get_samples_dataframe(self, limit=1000):
        """Get samples as pandas DataFrame"""
        samples = self.get_latest_samples(limit)
        df = pd.DataFrame(samples)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_aggregated_stats(self):
        """Get aggregated statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'avgTemp': {'$avg': '$tempC'},
                    'maxTemp': {'$max': '$tempC'},
                    'minTemp': {'$min': '$tempC'},
                    'totalSamples': {'$sum': 1},
                    'avgSatellites': {'$avg': '$sats'}
                }
            }
        ]
        
        result = list(self.samples.aggregate(pipeline))
        return result[0] if result else None
    
    def close(self):
        """Close database connection"""
        self.client.close()

# Usage
db = AirguardDatabase('mongodb://localhost:27017')

# Get latest samples
samples = db.get_latest_samples(50)

# Get samples from last 24 hours
now = datetime.now()
yesterday = now - timedelta(days=1)
recent_samples = db.get_samples_by_date_range(yesterday, now)

# Get as DataFrame for analysis
df = db.get_samples_dataframe(1000)
print(df.describe())

# Get statistics
stats = db.get_aggregated_stats()
print(f"Average temperature: {stats['avgTemp']:.2f}°C")
print(f"Total samples: {stats['totalSamples']}")

db.close()
```

---

## 📡 MQTT Integration

### Connection Details

**MQTT Broker:** `mqtt://your-server-ip:1883`  
**Topic:** `espnow/samples`  
**QoS:** 1 (at least once delivery)

**Message Payload (JSON):**
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

### JavaScript/Node.js Integration

```javascript
const mqtt = require('mqtt');

class AirguardMQTT {
  constructor(brokerUrl = 'mqtt://localhost:1883') {
    this.client = mqtt.connect(brokerUrl);
    this.handlers = [];
  }

  connect() {
    this.client.on('connect', () => {
      console.log('Connected to MQTT broker');
      this.client.subscribe('espnow/samples', { qos: 1 });
    });

    this.client.on('message', (topic, message) => {
      if (topic === 'espnow/samples') {
        const sample = JSON.parse(message.toString());
        this.handlers.forEach(handler => handler(sample));
      }
    });

    this.client.on('error', (error) => {
      console.error('MQTT error:', error);
    });
  }

  onSample(callback) {
    this.handlers.push(callback);
  }

  disconnect() {
    this.client.end();
  }
}

// Usage
const mqtt = new AirguardMQTT('mqtt://your-server:1883');
mqtt.connect();

mqtt.onSample((sample) => {
  console.log('New MQTT sample:', sample);
  
  // Process in your dashboard
  updateDashboard(sample);
});
```

### Python Integration

```python
import paho.mqtt.client as mqtt
import json

class AirguardMQTT:
    def __init__(self, broker='localhost', port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.handlers = []
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        client.subscribe("espnow/samples", qos=1)
    
    def on_message(self, client, userdata, msg):
        if msg.topic == "espnow/samples":
            sample = json.loads(msg.payload.decode())
            for handler in self.handlers:
                handler(sample)
    
    def on_sample(self, callback):
        """Register callback for new samples"""
        self.handlers.append(callback)
    
    def connect(self):
        """Connect to MQTT broker"""
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
    
    def disconnect(self):
        """Disconnect from broker"""
        self.client.loop_stop()
        self.client.disconnect()

# Usage
def handle_sample(sample):
    print(f"New sample: {sample['batchId']}")
    print(f"Location: {sample['lat']}, {sample['lon']}")
    print(f"Temperature: {sample['tempC']}°C")
    
    # Process in your application
    update_dashboard(sample)

mqtt_client = AirguardMQTT('your-server', 1883)
mqtt_client.on_sample(handle_sample)
mqtt_client.connect()

# Keep running
try:
    while True:
        pass
except KeyboardInterrupt:
    mqtt_client.disconnect()
```

---

## 📋 Data Schemas

### Sample Document Structure

```typescript
interface AirguardSample {
  _id: string;                    // MongoDB ObjectId
  batchId: string;                // Unique batch identifier (hex)
  sessionMs: number;              // Session duration (milliseconds)
  samples: number;                // Number of IMU samples in batch
  dateYMD: number;                // GPS date (YYYYMMDD format)
  timeHMS: number;                // GPS time (HHMMSS format)
  msec: number;                   // Milliseconds (0-999)
  lat: number;                    // Latitude (degrees)
  lon: number;                    // Longitude (degrees)
  alt: number;                    // Altitude (meters)
  gpsFix: number;                 // GPS fix status (0=no fix, 1=fix)
  sats: number;                   // Number of satellites
  ax: number;                     // Acceleration X (m/s²)
  ay: number;                     // Acceleration Y (m/s²)
  az: number;                     // Acceleration Z (m/s²)
  gx: number;                     // Gyroscope X (rad/s)
  gy: number;                     // Gyroscope Y (rad/s)
  gz: number;                     // Gyroscope Z (rad/s)
  tempC: number;                  // Temperature (°C)
  timestamp: string;              // ISO 8601 timestamp (auto-generated)
  createdAt?: Date;               // Optional: creation timestamp
}
```

### Field Descriptions

| Field | Type | Unit | Range | Description |
|-------|------|------|-------|-------------|
| `batchId` | string | - | 0x00000000 - 0xFFFFFFFF | Unique hex identifier for this measurement batch |
| `sessionMs` | number | ms | 0 - ∞ | Duration of measurement session |
| `samples` | number | count | 1 - 65535 | Number of IMU readings averaged |
| `lat` | number | degrees | -90 to 90 | Latitude (WGS84) |
| `lon` | number | degrees | -180 to 180 | Longitude (WGS84) |
| `alt` | number | meters | -1000 to 50000 | Altitude above sea level |
| `gpsFix` | number | - | 0 or 1 | 0=No GPS fix, 1=Valid fix |
| `sats` | number | count | 0 - 32 | Number of GPS satellites |
| `ax`, `ay`, `az` | number | m/s² | -156.96 to 156.96 | Acceleration (±16g range) |
| `gx`, `gy`, `gz` | number | rad/s | -34.91 to 34.91 | Angular velocity (±2000°/s) |
| `tempC` | number | °C | -40 to 85 | MPU6050 die temperature |

---

## 💡 Example Implementations

### 1. Leaflet Map Integration

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
  <div id="map" style="height: 600px;"></div>

  <script>
    // Initialize map
    const map = L.map('map').setView([34.140240, 35.663094], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    // Track markers
    const markers = {};

    // WebSocket connection
    const ws = new WebSocket('ws://your-server:8081');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample' && message.data.gpsFix === 1) {
        const sample = message.data;
        
        // Add/update marker
        if (!markers[sample.batchId]) {
          markers[sample.batchId] = L.marker([sample.lat, sample.lon])
            .addTo(map)
            .bindPopup(`
              <b>Batch: ${sample.batchId}</b><br>
              Temp: ${sample.tempC}°C<br>
              Sats: ${sample.sats}<br>
              Time: ${new Date(sample.timestamp).toLocaleString()}
            `);
        } else {
          markers[sample.batchId].setLatLng([sample.lat, sample.lon]);
        }
        
        // Center map on latest position
        map.setView([sample.lat, sample.lon]);
      }
    };
  </script>
</body>
</html>
```

### 2. Chart.js Temperature Visualization

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <canvas id="tempChart" width="800" height="400"></canvas>

  <script>
    const ctx = document.getElementById('tempChart').getContext('2d');
    const tempData = {
      labels: [],
      datasets: [{
        label: 'Temperature (°C)',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1
      }]
    };

    const chart = new Chart(ctx, {
      type: 'line',
      data: tempData,
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: false
          }
        }
      }
    });

    // WebSocket connection
    const ws = new WebSocket('ws://your-server:8081');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample') {
        const sample = message.data;
        const time = new Date(sample.timestamp).toLocaleTimeString();
        
        // Add data point
        tempData.labels.push(time);
        tempData.datasets[0].data.push(sample.tempC);
        
        // Keep only last 50 points
        if (tempData.labels.length > 50) {
          tempData.labels.shift();
          tempData.datasets[0].data.shift();
        }
        
        chart.update();
      }
    };
  </script>
</body>
</html>
```

### 3. React Dashboard with Multiple Data Sources

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AirguardDashboard() {
  const [latestSample, setLatestSample] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [stats, setStats] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);

  // Fetch historical data on mount
  useEffect(() => {
    const fetchHistory = async () => {
      const response = await axios.get('http://your-server:8080/v1/samples?limit=100');
      setHistoricalData(response.data.samples);
      
      // Calculate stats
      if (response.data.samples.length > 0) {
        const temps = response.data.samples.map(s => s.tempC);
        setStats({
          avgTemp: (temps.reduce((a, b) => a + b) / temps.length).toFixed(2),
          maxTemp: Math.max(...temps).toFixed(2),
          minTemp: Math.min(...temps).toFixed(2),
          totalSamples: response.data.samples.length
        });
      }
    };

    fetchHistory();
  }, []);

  // WebSocket for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://your-server:8081');

    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => setWsConnected(false);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample') {
        setLatestSample(message.data);
        
        // Add to historical data
        setHistoricalData(prev => [message.data, ...prev].slice(0, 100));
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="dashboard">
      <h1>Airguard Dashboard</h1>
      
      {/* Connection Status */}
      <div className="status">
        WebSocket: {wsConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>

      {/* Statistics */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Average Temperature</h3>
            <p>{stats.avgTemp}°C</p>
          </div>
          <div className="stat-card">
            <h3>Max Temperature</h3>
            <p>{stats.maxTemp}°C</p>
          </div>
          <div className="stat-card">
            <h3>Min Temperature</h3>
            <p>{stats.minTemp}°C</p>
          </div>
          <div className="stat-card">
            <h3>Total Samples</h3>
            <p>{stats.totalSamples}</p>
          </div>
        </div>
      )}

      {/* Latest Reading */}
      {latestSample && (
        <div className="latest-reading">
          <h2>Latest Reading</h2>
          <div className="reading-grid">
            <div>Time: {new Date(latestSample.timestamp).toLocaleString()}</div>
            <div>Latitude: {latestSample.lat.toFixed(6)}</div>
            <div>Longitude: {latestSample.lon.toFixed(6)}</div>
            <div>Temperature: {latestSample.tempC}°C</div>
            <div>Satellites: {latestSample.sats}</div>
            <div>Altitude: {latestSample.alt.toFixed(2)}m</div>
          </div>
        </div>
      )}

      {/* Historical Table */}
      <div className="history">
        <h2>Recent Samples</h2>
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Batch ID</th>
              <th>Location</th>
              <th>Temp</th>
              <th>Sats</th>
            </tr>
          </thead>
          <tbody>
            {historicalData.map(sample => (
              <tr key={sample._id}>
                <td>{new Date(sample.timestamp).toLocaleTimeString()}</td>
                <td>{sample.batchId}</td>
                <td>{sample.lat.toFixed(4)}, {sample.lon.toFixed(4)}</td>
                <td>{sample.tempC}°C</td>
                <td>{sample.sats}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AirguardDashboard;
```

---

## 🏗️ Deployment Architecture

### Option 1: Your Dashboard on Same Server

```
┌─────────────────────────────────────────────┐
│           Your Server (192.168.1.100)       │
│                                             │
│  ┌──────────────┐    ┌──────────────┐      │
│  │   Airguard   │───▶│  Your Custom │      │
│  │   Backend    │    │   Dashboard  │      │
│  │  (Port 8080) │    │  (Port 3000) │      │
│  └──────────────┘    └──────────────┘      │
│         │                     │             │
│  ┌──────────────┐    ┌──────────────┐      │
│  │   MongoDB    │    │  WebSocket   │      │
│  │ (Port 27017) │    │  (Port 8081) │      │
│  └──────────────┘    └──────────────┘      │
└─────────────────────────────────────────────┘
```

**Access URLs:**
- REST API: `http://192.168.1.100:8080/v1/samples`
- WebSocket: `ws://192.168.1.100:8081`
- Your Dashboard: `http://192.168.1.100:3000`

### Option 2: Separate Servers

```
┌──────────────────────┐         ┌──────────────────────┐
│  Airguard Server     │         │  Your Dashboard      │
│  (192.168.1.100)     │         │  (192.168.1.200)     │
│                      │         │                      │
│  ┌────────────────┐  │         │  ┌────────────────┐  │
│  │ REST API:8080  │◀─┼─────────┼──│  Your App      │  │
│  │ WebSocket:8081 │  │         │  │  (Calls API)   │  │
│  │ MongoDB:27017  │  │         │  └────────────────┘  │
│  └────────────────┘  │         │                      │
└──────────────────────┘         └──────────────────────┘
```

**Your Dashboard Configuration:**
```javascript
// config.js
export const AIRGUARD_API_BASE = 'http://192.168.1.100:8080';
export const AIRGUARD_WS_URL = 'ws://192.168.1.100:8081';
```

### Option 3: Cloud Deployment

```
┌────────────────────────────────────────────┐
│            Cloud (AWS/Azure/GCP)           │
│                                            │
│  ┌──────────────┐      ┌────────────────┐ │
│  │  Airguard    │      │  MongoDB Atlas │ │
│  │  (EC2/VM)    │─────▶│  (Cloud DB)    │ │
│  └──────────────┘      └────────────────┘ │
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                         │
│  │ Your Custom  │                         │
│  │  Dashboard   │                         │
│  │ (Vercel/     │                         │
│  │  Netlify)    │                         │
│  └──────────────┘                         │
└────────────────────────────────────────────┘
```

**Environment Variables:**
```env
REACT_APP_API_URL=https://airguard.yourdomain.com/api
REACT_APP_WS_URL=wss://airguard.yourdomain.com/ws
```

---

## 🔒 Security Configuration

### Enable Authentication

**1. Set AUTH_TOKEN in Backend:**
```env
# host/node-backend/.env
AUTH_TOKEN=your-secure-random-token-here
```

**2. Include Token in Requests:**
```javascript
// JavaScript
const headers = {
  'Authorization': `Bearer your-secure-random-token-here`,
  'Content-Type': 'application/json'
};

fetch('http://your-server:8080/v1/samples', { headers })
  .then(res => res.json())
  .then(data => console.log(data));
```

```python
# Python
headers = {
    'Authorization': 'Bearer your-secure-random-token-here',
    'Content-Type': 'application/json'
}

response = requests.get(
    'http://your-server:8080/v1/samples',
    headers=headers
)
```

### CORS Configuration

If your dashboard is on a different domain:

**Backend `.env`:**
```env
# Allow specific domain
CORS_ORIGIN=https://yourdashboard.com

# Or multiple domains (comma-separated)
CORS_ORIGIN=https://yourdashboard.com,https://app.yourdomain.com
```

### SSL/TLS (Production)

Use nginx reverse proxy for HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name airguard.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # REST API
    location /api/ {
        proxy_pass http://localhost:8080/;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8081/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Updated URLs:**
- REST API: `https://airguard.yourdomain.com/api/v1/samples`
- WebSocket: `wss://airguard.yourdomain.com/ws`

---

## ⚡ Performance Optimization

### 1. Connection Pooling (MongoDB)

```javascript
const { MongoClient } = require('mongodb');

const client = new MongoClient(uri, {
  maxPoolSize: 50,
  minPoolSize: 10,
  maxIdleTimeMS: 30000
});
```

### 2. Caching (Redis)

```javascript
const redis = require('redis');
const client = redis.createClient();

// Cache latest samples for 10 seconds
async function getLatestSamples() {
  const cached = await client.get('latest_samples');
  if (cached) return JSON.parse(cached);
  
  const samples = await fetchFromDB();
  await client.setEx('latest_samples', 10, JSON.stringify(samples));
  return samples;
}
```

### 3. Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/v1/', limiter);
```

### 4. Data Pagination

```javascript
// Frontend: Load more on scroll
const [page, setPage] = useState(0);
const PAGE_SIZE = 50;

const loadMore = async () => {
  const response = await fetch(
    `http://your-server:8080/v1/samples?limit=${PAGE_SIZE}&skip=${page * PAGE_SIZE}`
  );
  const data = await response.json();
  setSamples(prev => [...prev, ...data.samples]);
  setPage(prev => prev + 1);
};
```

---

## 📚 Complete Example: Full Stack Integration

Here's a complete example combining all methods:

```javascript
// dashboard.js - Complete integration example

class AirguardDataSource {
  constructor(config) {
    this.apiBase = config.apiUrl;
    this.wsUrl = config.wsUrl;
    this.mongoUri = config.mongoUri;
    this.mqttBroker = config.mqttBroker;
    
    this.ws = null;
    this.mqttClient = null;
    this.listeners = {
      sample: [],
      connect: [],
      disconnect: []
    };
  }

  // REST API Methods
  async getLatestSamples(limit = 100) {
    const response = await fetch(`${this.apiBase}/v1/samples?limit=${limit}`);
    return await response.json();
  }

  async getSamplesByDateRange(startDate, endDate) {
    // Implement custom endpoint or use MongoDB direct
    const samples = await this.getLatestSamples(1000);
    return samples.filter(s => {
      const date = new Date(s.timestamp);
      return date >= startDate && date <= endDate;
    });
  }

  // WebSocket Methods
  connectWebSocket() {
    this.ws = new WebSocket(this.wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.emit('connect');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'sample') {
        this.emit('sample', message.data);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.emit('disconnect');
      setTimeout(() => this.connectWebSocket(), 5000);
    };
  }

  // MQTT Methods
  connectMQTT() {
    this.mqttClient = mqtt.connect(this.mqttBroker);

    this.mqttClient.on('connect', () => {
      this.mqttClient.subscribe('espnow/samples', { qos: 1 });
    });

    this.mqttClient.on('message', (topic, message) => {
      if (topic === 'espnow/samples') {
        const sample = JSON.parse(message.toString());
        this.emit('sample', sample);
      }
    });
  }

  // Event handling
  on(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event].push(callback);
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }

  // Cleanup
  disconnect() {
    if (this.ws) this.ws.close();
    if (this.mqttClient) this.mqttClient.end();
  }
}

// Usage
const airguard = new AirguardDataSource({
  apiUrl: 'http://192.168.1.100:8080',
  wsUrl: 'ws://192.168.1.100:8081',
  mongoUri: 'mongodb://localhost:27017',
  mqttBroker: 'mqtt://192.168.1.100:1883'
});

// Fetch historical data
const samples = await airguard.getLatestSamples(100);
console.log('Historical samples:', samples);

// Listen for real-time updates
airguard.connectWebSocket();
airguard.on('sample', (sample) => {
  console.log('New sample:', sample);
  updateDashboard(sample);
});

// Cleanup on exit
window.addEventListener('beforeunload', () => {
  airguard.disconnect();
});
```

---

## 🎯 Summary

### Choose Your Integration Method:

| Your Use Case | Recommended Method | Complexity |
|---------------|-------------------|------------|
| Simple polling dashboard | REST API | ⭐ Easy |
| Real-time visualization | WebSocket | ⭐⭐ Medium |
| Complex analytics | MongoDB Direct | ⭐⭐⭐ Advanced |
| Event-driven system | MQTT | ⭐⭐ Medium |
| Hybrid (best of all) | All Methods | ⭐⭐⭐ Advanced |

### Quick Start Checklist:

- [ ] Start Airguard services (`start-services.ps1` or `.sh`)
- [ ] Note your server IP address
- [ ] Choose integration method (REST/WebSocket/MongoDB/MQTT)
- [ ] Implement client code in your dashboard
- [ ] Test connection with sample data
- [ ] Configure CORS if needed
- [ ] Add authentication tokens
- [ ] Deploy and monitor

---

**Need Help?**
- Check the main [README.md](README.md) for system setup
- Review API endpoints in [Data Schemas](#data-schemas)
- Test with curl/Postman before integrating
- Monitor logs for debugging

**Built with ❤️ for easy integration**
