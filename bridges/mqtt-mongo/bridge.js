import mqtt from 'mqtt';
import { MongoClient, ServerApiVersion } from 'mongodb';
import { WebSocket } from 'ws';
import dotenv from 'dotenv';

dotenv.config();

const MQTT_BROKER = process.env.MQTT_BROKER || 'mqtt://127.0.0.1:1883';
const MQTT_TOPIC = process.env.MQTT_TOPIC || 'espnow/samples';
const MQTT_CLIENT_ID = process.env.MQTT_CLIENT_ID || 'airguard-mqtt-bridge';
const MQTT_USERNAME = process.env.MQTT_USERNAME;
const MQTT_PASSWORD = process.env.MQTT_PASSWORD;
const MQTT_QOS = parseInt(process.env.MQTT_QOS) || 1;

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017';
const MONGO_DB = process.env.MONGO_DB || 'airguard';

const WS_PORT = parseInt(process.env.WS_PORT) || 8081;
const WS_ENABLED = process.env.WS_ENABLED === 'true';

const LOG_LEVEL = process.env.LOG_LEVEL || 'info';

// Logger
const log = {
  info: (...args) => LOG_LEVEL !== 'error' && console.log('[INFO]', ...args),
  warn: (...args) => LOG_LEVEL !== 'error' && console.warn('[WARN]', ...args),
  error: (...args) => console.error('[ERROR]', ...args)
};

// MongoDB client
const mongoClient = new MongoClient(MONGO_URI, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});

let db;
let samplesCollection;

// WebSocket clients (if enabled)
let wsClients = new Set();

// Connect to MongoDB
async function connectDB() {
  try {
    await mongoClient.connect();
    db = mongoClient.db(MONGO_DB);
    samplesCollection = db.collection('samples');
    
    // Ensure indexes
    await samplesCollection.createIndex({ batchId: 1 }, { unique: true });
    await samplesCollection.createIndex({ receivedTs: -1 });
    
    log.info(`✓ MongoDB connected: ${MONGO_DB}`);
  } catch (error) {
    log.error('MongoDB connection failed:', error);
    process.exit(1);
  }
}

// Broadcast to WebSocket clients
function broadcastToWS(data) {
  if (!WS_ENABLED || wsClients.size === 0) return;
  
  const payload = JSON.stringify({ type: 'new_sample', data });
  let sent = 0;
  
  wsClients.forEach(client => {
    if (client.readyState === 1) { // OPEN
      try {
        client.send(payload);
        sent++;
      } catch (error) {
        log.error('WS send error:', error);
      }
    }
  });
  
  if (sent > 0) {
    log.info(`→ Broadcast to ${sent} WS client(s)`);
  }
}

// Process MQTT message
async function processSample(payload) {
  try {
    const data = JSON.parse(payload);
    
    // Add timestamps if not present
    if (!data.createdAt) data.createdAt = new Date();
    if (!data.updatedAt) data.updatedAt = new Date();
    
    // Insert to MongoDB (ignore duplicates)
    try {
      await samplesCollection.insertOne(data);
      log.info(`✓ Sample stored: ${data.batchId}`);
      
      // Broadcast to WebSocket clients
      broadcastToWS(data);
      
    } catch (error) {
      if (error.code === 11000) {
        log.warn(`Duplicate batch ID: ${data.batchId}`);
      } else {
        throw error;
      }
    }
    
  } catch (error) {
    log.error('Process error:', error);
  }
}

// MQTT client setup
const mqttOptions = {
  clientId: MQTT_CLIENT_ID,
  clean: true,
  reconnectPeriod: 5000,
};

if (MQTT_USERNAME && MQTT_PASSWORD) {
  mqttOptions.username = MQTT_USERNAME;
  mqttOptions.password = MQTT_PASSWORD;
}

const mqttClient = mqtt.connect(MQTT_BROKER, mqttOptions);

mqttClient.on('connect', () => {
  log.info(`✓ MQTT connected: ${MQTT_BROKER}`);
  
  mqttClient.subscribe(MQTT_TOPIC, { qos: MQTT_QOS }, (err) => {
    if (err) {
      log.error('Subscribe error:', err);
    } else {
      log.info(`✓ Subscribed to: ${MQTT_TOPIC} (QoS ${MQTT_QOS})`);
    }
  });
});

mqttClient.on('message', async (topic, payload) => {
  log.info(`← MQTT message on ${topic}`);
  await processSample(payload.toString());
});

mqttClient.on('error', (error) => {
  log.error('MQTT error:', error);
});

mqttClient.on('offline', () => {
  log.warn('MQTT offline');
});

mqttClient.on('reconnect', () => {
  log.info('MQTT reconnecting...');
});

// Optional WebSocket server for broadcasting
if (WS_ENABLED) {
  import('ws').then(({ WebSocketServer }) => {
    const wss = new WebSocketServer({ port: WS_PORT });
    
    wss.on('connection', (ws) => {
      wsClients.add(ws);
      log.info(`✓ WS client connected (${wsClients.size} total)`);
      
      ws.send(JSON.stringify({ 
        type: 'connected', 
        message: 'Airguard MQTT Bridge',
        timestamp: new Date().toISOString()
      }));
      
      ws.on('close', () => {
        wsClients.delete(ws);
        log.info(`✗ WS client disconnected (${wsClients.size} remaining)`);
      });
      
      ws.on('error', (error) => {
        log.error('WS error:', error);
        wsClients.delete(ws);
      });
    });
    
    log.info(`✓ WebSocket server on port ${WS_PORT}`);
  });
}

// Initialize
await connectDB();

log.info('MQTT → MongoDB bridge running');

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down...');
  
  mqttClient.end();
  
  if (WS_ENABLED) {
    wsClients.forEach(client => client.close());
  }
  
  await mongoClient.close();
  
  log.info('Bridge stopped');
  process.exit(0);
});
