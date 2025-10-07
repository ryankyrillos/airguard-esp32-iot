const aedes = require('aedes')();
const net = require('net');

const port = 1883;

const server = net.createServer(aedes.handle);

server.listen(port, () => {
  console.log('🚀 MQTT Broker started');
  console.log(`   Port: ${port}`);
  console.log(`   Broker: mqtt://localhost:${port}`);
});

aedes.on('client', (client) => {
  console.log(`✓ Client connected: ${client.id}`);
});

aedes.on('clientDisconnect', (client) => {
  console.log(`✗ Client disconnected: ${client.id}`);
});

aedes.on('publish', (packet, client) => {
  if (client && packet.topic !== '$SYS/broker/uptime') {
    console.log(`📨 Message: ${packet.topic} (${packet.payload.length} bytes)`);
  }
});

process.on('SIGINT', () => {
  console.log('\nShutting down MQTT broker...');
  server.close(() => {
    console.log('MQTT broker stopped');
    process.exit(0);
  });
});
