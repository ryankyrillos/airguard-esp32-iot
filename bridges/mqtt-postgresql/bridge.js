import mqtt from 'mqtt';
import pg from 'pg';
import { WebSocket } from 'ws';
import dotenv from 'dotenv';

dotenv.config();

const MQTT_BROKER = process.env.MQTT_BROKER || 'mqtt://127.0.0.1:1883';
const MQTT_TOPIC = process.env.MQTT_TOPIC || 'espnow/samples';
const MQTT_CLIENT_ID = process.env.MQTT_CLIENT_ID || 'airguard-mqtt-bridge';
const MQTT_USERNAME = process.env.MQTT_USERNAME;
const MQTT_PASSWORD = process.env.MQTT_PASSWORD;
const MQTT_QOS = parseInt(process.env.MQTT_QOS) || 1;

const PG_HOST = process.env.PG_HOST || 'localhost';
const PG_PORT = process.env.PG_PORT || 5432;
const PG_DATABASE = process.env.PG_DATABASE || 'airguard';
const PG_USER = process.env.PG_USER || 'airguard_user';
const PG_PASSWORD = process.env.PG_PASSWORD || 'airguard_password';
const PG_SSL = process.env.PG_SSL === 'true';

const WS_PORT = parseInt(process.env.WS_PORT) || 8081;
const WS_ENABLED = process.env.WS_ENABLED === 'true';

const LOG_LEVEL = process.env.LOG_LEVEL || 'info';

// Logger
const log = {
  info: (...args) => LOG_LEVEL !== 'error' && console.log('[INFO]', ...args),
  warn: (...args) => LOG_LEVEL !== 'error' && console.warn('[WARN]', ...args),
  error: (...args) => console.error('[ERROR]', ...args)
};

// PostgreSQL client
const { Client } = pg;
const pgClient = new Client({
  host: PG_HOST,
  port: PG_PORT,
  database: PG_DATABASE,
  user: PG_USER,
  password: PG_PASSWORD,
  ssl: PG_SSL
});

// WebSocket clients (if enabled)
let wsClients = new Set();

// Connect to PostgreSQL
async function connectDB() {
  try {
    await pgClient.connect();
    
    // Create table if it doesn't exist
    await pgClient.query(`
      CREATE TABLE IF NOT EXISTS samples (
        id SERIAL PRIMARY KEY,
        batch_id VARCHAR(50) UNIQUE NOT NULL,
        session_ms INTEGER,
        samples INTEGER,
        date_ymd INTEGER,
        time_hms INTEGER,
        msec INTEGER,
        lat FLOAT,
        lon FLOAT,
        alt FLOAT,
        gps_fix INTEGER,
        sats INTEGER,
        ax FLOAT,
        ay FLOAT,
        az FLOAT,
        gx FLOAT,
        gy FLOAT,
        gz FLOAT,
        temp_c FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // Create indexes for better performance
    await pgClient.query('CREATE INDEX IF NOT EXISTS idx_samples_batch_id ON samples (batch_id)');
    await pgClient.query('CREATE INDEX IF NOT EXISTS idx_samples_created_at ON samples (created_at DESC)');
    
    log.info(`✓ PostgreSQL connected: ${PG_DATABASE}`);
  } catch (error) {
    log.error('PostgreSQL connection failed:', error);
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
    
    // Insert to PostgreSQL (ignore duplicates with ON CONFLICT)
    try {
      const insertQuery = `
        INSERT INTO samples (
          batch_id, session_ms, samples, date_ymd, time_hms, msec,
          lat, lon, alt, gps_fix, sats, ax, ay, az, gx, gy, gz, temp_c,
          created_at, updated_at
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18,
          CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        ) ON CONFLICT (batch_id) DO NOTHING
        RETURNING id
      `;
      
      const values = [
        data.batchId || null,
        data.sessionMs || null,
        data.samples || null,
        data.dateYMD || null,
        data.timeHMS || null,
        data.msec || null,
        data.lat || null,
        data.lon || null,
        data.alt || null,
        data.gpsFix || null,
        data.sats || null,
        data.ax || null,
        data.ay || null,
        data.az || null,
        data.gx || null,
        data.gy || null,
        data.gz || null,
        data.tempC || null
      ];
      
      const result = await pgClient.query(insertQuery, values);
      
      if (result.rows.length > 0) {
        log.info(`✓ Sample stored: ${data.batchId} (ID: ${result.rows[0].id})`);
        
        // Add the database ID to the data for WebSocket broadcast
        data.id = result.rows[0].id;
        data.createdAt = new Date().toISOString();
        data.updatedAt = new Date().toISOString();
        
        // Broadcast to WebSocket clients
        broadcastToWS(data);
      } else {
        log.warn(`Duplicate batch ID: ${data.batchId}`);
      }
      
    } catch (error) {
      if (error.code === '23505') { // unique_violation
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
        message: 'Airguard MQTT → PostgreSQL Bridge',
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

log.info('MQTT → PostgreSQL bridge running');

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down...');
  
  mqttClient.end();
  
  if (WS_ENABLED) {
    wsClients.forEach(client => client.close());
  }
  
  await pgClient.end();
  
  log.info('Bridge stopped');
  process.exit(0);
});