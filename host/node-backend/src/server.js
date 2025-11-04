import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import pg from 'pg';
import dotenv from 'dotenv';
import { createServer } from 'http';

dotenv.config();

const PORT = process.env.PORT || 8080;
const WS_PORT = process.env.WS_PORT || 8081;
const PG_HOST = process.env.PG_HOST || 'localhost';
const PG_PORT = process.env.PG_PORT || 5432;
const PG_DATABASE = process.env.PG_DATABASE || 'airguard';
const PG_USER = process.env.PG_USER || 'airguard_user';
const PG_PASSWORD = process.env.PG_PASSWORD || 'airguard_password';
const PG_SSL = process.env.PG_SSL === 'true';
const AUTH_TOKEN = process.env.AUTH_TOKEN;
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';

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

let db;

// WebSocket clients
let wsClients = new Set();

// Connect to PostgreSQL
async function connectDB() {
  try {
    await pgClient.connect();
    db = pgClient;
    
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
    
    // Create indexes
    await pgClient.query('CREATE INDEX IF NOT EXISTS idx_samples_batch_id ON samples (batch_id)');
    await pgClient.query('CREATE INDEX IF NOT EXISTS idx_samples_created_at ON samples (created_at DESC)');
    
    console.log(`✓ Connected to PostgreSQL: ${PG_DATABASE}`);
  } catch (error) {
    console.error('PostgreSQL connection failed:', error);
    process.exit(1);
  }
}

// Express app
const app = express();
app.use(cors({ origin: CORS_ORIGIN }));
app.use(express.json());

// Auth middleware
const authenticate = (req, res, next) => {
  if (!AUTH_TOKEN) return next(); // No auth required if not configured
  
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (token === AUTH_TOKEN) {
    return next();
  }
  
  return res.status(401).json({ error: 'Unauthorized' });
};

// Routes
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    postgresql: db ? 'connected' : 'disconnected',
    wsClients: wsClients.size
  });
});

// Broadcast to WebSocket clients
function broadcastToWS(data) {
  if (wsClients.size === 0) return;
  
  const payload = JSON.stringify(data);
  let sent = 0;
  
  wsClients.forEach(client => {
    if (client.readyState === 1) { // OPEN
      try {
        client.send(payload);
        sent++;
      } catch (error) {
        console.error('WS send error:', error);
      }
    }
  });
  
  if (sent > 0) {
    console.log(`→ Broadcast to ${sent} WS client(s)`);
  }
}

// POST /v1/samples - Insert new sample
app.post('/v1/samples', authenticate, async (req, res) => {
  try {
    const data = req.body;
    
    // Insert to PostgreSQL
    const insertQuery = `
      INSERT INTO samples (
        batch_id, session_ms, samples, date_ymd, time_hms, msec,
        lat, lon, alt, gps_fix, sats, ax, ay, az, gx, gy, gz, temp_c,
        created_at, updated_at
      ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18,
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
      ) ON CONFLICT (batch_id) DO NOTHING
      RETURNING id, created_at, updated_at
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
      console.log(`✓ Sample stored: ${data.batchId} (ID: ${result.rows[0].id})`);
      
      // Add database fields to data for WebSocket broadcast
      data.id = result.rows[0].id;
      data.createdAt = result.rows[0].created_at;
      data.updatedAt = result.rows[0].updated_at;
      
      // Broadcast to WebSocket clients
      broadcastToWS({ type: 'new_sample', data });
      
      res.status(201).json({ success: true, id: result.rows[0].id, batchId: data.batchId });
    } else {
      // Duplicate key
      console.warn(`Duplicate batch ID: ${data.batchId}`);
      return res.status(409).json({ error: 'Duplicate batchId' });
    }
  } catch (error) {
    console.error('Insert error:', error);
    res.status(500).json({ error: 'Database error' });
  }
});

// GET /v1/samples - Get samples with pagination
app.get('/v1/samples', authenticate, async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 100, 1000); // Max 1000
    const skip = parseInt(req.query.skip) || 0;
    const order = req.query.order === 'asc' ? 'ASC' : 'DESC';
    
    // Get samples with limit and offset
    const query = `
      SELECT 
        id, batch_id as "batchId", session_ms as "sessionMs", samples,
        date_ymd as "dateYMD", time_hms as "timeHMS", msec,
        lat, lon, alt, gps_fix as "gpsFix", sats,
        ax, ay, az, gx, gy, gz, temp_c as "tempC",
        created_at as "createdAt", updated_at as "updatedAt"
      FROM samples 
      ORDER BY created_at ${order}
      LIMIT $1 OFFSET $2
    `;
    
    const result = await pgClient.query(query, [limit, skip]);
    
    // Get total count
    const countResult = await pgClient.query('SELECT COUNT(*) as count FROM samples');
    const total = parseInt(countResult.rows[0].count);
    
    res.json({
      samples: result.rows,
      pagination: {
        limit,
        skip,
        total,
        count: result.rows.length
      }
    });
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: 'Database error' });
  }
});

// GET /v1/samples/:batchId - Get specific sample
app.get('/v1/samples/:batchId', authenticate, async (req, res) => {
  try {
    const { batchId } = req.params;
    
    const query = `
      SELECT 
        id, batch_id as "batchId", session_ms as "sessionMs", samples,
        date_ymd as "dateYMD", time_hms as "timeHMS", msec,
        lat, lon, alt, gps_fix as "gpsFix", sats,
        ax, ay, az, gx, gy, gz, temp_c as "tempC",
        created_at as "createdAt", updated_at as "updatedAt"
      FROM samples 
      WHERE batch_id = $1
    `;
    
    const result = await pgClient.query(query, [batchId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Sample not found' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: 'Database error' });
  }
});

// GET /v1/stats - Get database statistics
app.get('/v1/stats', authenticate, async (req, res) => {
  try {
    const queries = await Promise.all([
      pgClient.query('SELECT COUNT(*) as total FROM samples'),
      pgClient.query('SELECT COUNT(DISTINCT batch_id) as unique_batches FROM samples'),
      pgClient.query('SELECT MIN(created_at) as first_sample, MAX(created_at) as last_sample FROM samples'),
      pgClient.query('SELECT AVG(lat) as avg_lat, AVG(lon) as avg_lon FROM samples WHERE lat IS NOT NULL AND lon IS NOT NULL')
    ]);
    
    res.json({
      total_samples: parseInt(queries[0].rows[0].total),
      unique_batches: parseInt(queries[1].rows[0].unique_batches),
      first_sample: queries[2].rows[0].first_sample,
      last_sample: queries[2].rows[0].last_sample,
      average_location: {
        lat: queries[3].rows[0].avg_lat ? parseFloat(queries[3].rows[0].avg_lat) : null,
        lon: queries[3].rows[0].avg_lon ? parseFloat(queries[3].rows[0].avg_lon) : null
      }
    });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({ error: 'Database error' });
  }
});

// WebSocket server
const server = createServer(app);
const wss = new WebSocketServer({ port: WS_PORT });

wss.on('connection', (ws, req) => {
  wsClients.add(ws);
  console.log(`✓ WebSocket client connected (${wsClients.size} total) from ${req.socket.remoteAddress}`);
  
  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Airguard Backend WebSocket',
    timestamp: new Date().toISOString(),
    clients: wsClients.size
  }));
  
  ws.on('close', () => {
    wsClients.delete(ws);
    console.log(`✗ WebSocket client disconnected (${wsClients.size} remaining)`);
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    wsClients.delete(ws);
  });
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('WebSocket message:', data);
      
      // Echo back for now
      ws.send(JSON.stringify({
        type: 'echo',
        original: data,
        timestamp: new Date().toISOString()
      }));
    } catch (error) {
      console.error('WebSocket message parse error:', error);
    }
  });
});

console.log(`✓ WebSocket server listening on port ${WS_PORT}`);
console.log(`  WS: ws://localhost:${WS_PORT}`);

// Start HTTP server
server.listen(PORT, () => {
  console.log(`✓ HTTP server listening on port ${PORT}`);
  console.log(`  REST API: http://localhost:${PORT}/v1/samples`);
});

// Initialize database connection
connectDB();

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  
  // Close WebSocket server
  wss.close();
  
  // Close PostgreSQL
  await pgClient.end();
  
  // Close HTTP server
  server.close();
  
  console.log('Server stopped');
  process.exit(0);
});