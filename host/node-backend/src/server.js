import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { MongoClient, ServerApiVersion } from 'mongodb';
import dotenv from 'dotenv';
import { createServer } from 'http';

dotenv.config();

const PORT = process.env.PORT || 8080;
const WS_PORT = process.env.WS_PORT || 8081;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017';
const MONGO_DB = process.env.MONGO_DB || 'airguard';
const AUTH_TOKEN = process.env.AUTH_TOKEN;
const CORS_ORIGIN = process.env.CORS_ORIGIN || '*';

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

// WebSocket clients
let wsClients = new Set();

// Connect to MongoDB
async function connectDB() {
  try {
    await mongoClient.connect();
    db = mongoClient.db(MONGO_DB);
    samplesCollection = db.collection('samples');
    
    // Create indexes
    await samplesCollection.createIndex({ batchId: 1 }, { unique: true });
    await samplesCollection.createIndex({ receivedTs: -1 });
    await samplesCollection.createIndex({ createdAt: -1 });
    
    console.log(`✓ Connected to MongoDB: ${MONGO_DB}`);
  } catch (error) {
    console.error('MongoDB connection failed:', error);
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
    mongodb: db ? 'connected' : 'disconnected',
    wsClients: wsClients.size
  });
});

// POST /v1/samples - Insert new sample
app.post('/v1/samples', authenticate, async (req, res) => {
  try {
    const data = req.body;
    
    // Add timestamps
    data.createdAt = new Date();
    data.updatedAt = new Date();
    
    // Insert to MongoDB
    await samplesCollection.insertOne(data);
    
    console.log(`✓ Sample stored: ${data.batchId}`);
    
    // Broadcast to WebSocket clients
    broadcastToWS({ type: 'new_sample', data });
    
    res.status(201).json({ success: true, batchId: data.batchId });
  } catch (error) {
    if (error.code === 11000) {
      // Duplicate key
      console.warn(`Duplicate batch ID: ${req.body.batchId}`);
      return res.status(409).json({ error: 'Duplicate batchId' });
    }
    
    console.error('Insert error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /v1/samples - Retrieve samples
app.get('/v1/samples', authenticate, async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 100, 1000);
    const skip = parseInt(req.query.skip) || 0;
    
    const samples = await samplesCollection
      .find({})
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .toArray();
    
    const total = await samplesCollection.countDocuments();
    
    res.json({
      samples,
      total,
      limit,
      skip
    });
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /v1/samples/:batchId - Get specific sample
app.get('/v1/samples/:batchId', authenticate, async (req, res) => {
  try {
    const sample = await samplesCollection.findOne({ batchId: req.params.batchId });
    
    if (!sample) {
      return res.status(404).json({ error: 'Sample not found' });
    }
    
    res.json(sample);
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Broadcast to WebSocket clients
function broadcastToWS(message) {
  const payload = JSON.stringify(message);
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
    console.log(`→ Broadcast to ${sent} WebSocket client(s)`);
  }
}

// Start HTTP server
const httpServer = createServer(app);

httpServer.listen(PORT, () => {
  console.log(`✓ HTTP server listening on port ${PORT}`);
  console.log(`  REST API: http://localhost:${PORT}/v1/samples`);
});

// WebSocket server
const wss = new WebSocketServer({ port: WS_PORT });

wss.on('connection', (ws, req) => {
  wsClients.add(ws);
  console.log(`✓ WebSocket client connected (${wsClients.size} total)`);
  
  // Send welcome message
  ws.send(JSON.stringify({ 
    type: 'connected', 
    message: 'Airguard WebSocket server',
    timestamp: new Date().toISOString()
  }));
  
  ws.on('close', () => {
    wsClients.delete(ws);
    console.log(`✗ WebSocket client disconnected (${wsClients.size} remaining)`);
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
    wsClients.delete(ws);
  });
});

console.log(`✓ WebSocket server listening on port ${WS_PORT}`);
console.log(`  WS: ws://localhost:${WS_PORT}`);

// Initialize
await connectDB();

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  
  // Close WebSocket connections
  wsClients.forEach(client => client.close());
  wss.close();
  
  // Close MongoDB
  await mongoClient.close();
  
  // Close HTTP server
  httpServer.close(() => {
    console.log('Server stopped');
    process.exit(0);
  });
});
