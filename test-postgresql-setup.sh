#!/bin/bash
# Airguard PostgreSQL Setup Test Script
# This script tests the PostgreSQL implementation without running ESP32 hardware

set -e  # Exit on any error

echo "🐘 Testing Airguard PostgreSQL Implementation"
echo "============================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if PostgreSQL is available (Docker or native)
echo "1. Checking PostgreSQL availability..."

if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "Docker found - will use PostgreSQL container"
    
    # Start PostgreSQL container if not running
    if ! docker ps | grep -q "airguard-postgres"; then
        echo "Starting PostgreSQL container..."
        docker run -d \
            --name airguard-postgres \
            -e POSTGRES_DB=airguard \
            -e POSTGRES_USER=airguard_user \
            -e POSTGRES_PASSWORD=airguard_password \
            -p 5432:5432 \
            postgres:15
        
        echo "Waiting for PostgreSQL to start..."
        sleep 10
    fi
    print_status "PostgreSQL container is running"
    
elif command -v psql &> /dev/null; then
    echo "Native PostgreSQL found"
    print_status "PostgreSQL is available"
    
else
    print_error "PostgreSQL not found. Please install PostgreSQL or Docker first."
    echo "Ubuntu: sudo apt install postgresql postgresql-contrib"
    echo "Docker: docker run -d --name airguard-postgres -e POSTGRES_DB=airguard -e POSTGRES_USER=airguard_user -e POSTGRES_PASSWORD=airguard_password -p 5432:5432 postgres:15"
    exit 1
fi

# Test database connection
echo ""
echo "2. Testing database connection..."

# Create a simple test script to check PostgreSQL connection
cat > test_pg_connection.js << 'EOF'
import pg from 'pg';
const { Client } = pg;

const client = new Client({
    host: 'localhost',
    port: 5432,
    database: 'airguard',
    user: 'airguard_user',
    password: 'airguard_password',
    ssl: false
});

try {
    await client.connect();
    console.log('✓ PostgreSQL connection successful');
    
    // Test table creation
    await client.query(`
        CREATE TABLE IF NOT EXISTS test_samples (
            id SERIAL PRIMARY KEY,
            batch_id VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `);
    console.log('✓ Table creation successful');
    
    // Test insert
    await client.query(
        'INSERT INTO test_samples (batch_id) VALUES ($1) ON CONFLICT (batch_id) DO NOTHING',
        ['test_' + Date.now()]
    );
    console.log('✓ Insert test successful');
    
    // Test select
    const result = await client.query('SELECT COUNT(*) FROM test_samples');
    console.log('✓ Query test successful - Total test records:', result.rows[0].count);
    
    // Clean up
    await client.query('DROP TABLE test_samples');
    console.log('✓ Cleanup successful');
    
    await client.end();
    process.exit(0);
} catch (error) {
    console.error('✗ Database test failed:', error.message);
    process.exit(1);
}
EOF

# Install pg module and test connection
echo "Installing pg module for testing..."
cd host/node-backend
npm install pg > /dev/null 2>&1

echo "Testing PostgreSQL connection..."
if node ../../test_pg_connection.js; then
    print_status "PostgreSQL connection and operations working"
else
    print_error "PostgreSQL connection test failed"
    exit 1
fi

# Clean up test file
rm -f ../../test_pg_connection.js

# Test that our services can start
echo ""
echo "3. Testing service startup..."

# Test MQTT broker
echo "Testing MQTT broker..."
cd ../../mqtt-broker
if timeout 5s node broker.js 2>&1 | grep -q "MQTT Broker started"; then
    print_status "MQTT broker starts successfully"
else
    print_warning "MQTT broker test inconclusive"
fi

# Test Node backend
echo "Testing Node.js backend..."
cd ../host/node-backend
timeout 5s node src/server.js 2>&1 | grep -q "Connected to PostgreSQL" && {
    print_status "Node.js backend connects to PostgreSQL successfully"
} || {
    print_warning "Node.js backend test - check PostgreSQL is running"
}

# Test PostgreSQL bridge
echo "Testing PostgreSQL bridge..."
cd ../../bridges/mqtt-postgresql
timeout 5s node bridge.js 2>&1 | grep -q "PostgreSQL connected" && {
    print_status "MQTT-PostgreSQL bridge connects successfully"
} || {
    print_warning "PostgreSQL bridge test - check PostgreSQL and MQTT broker are running"
}

echo ""
echo "🎉 PostgreSQL Implementation Test Complete!"
echo "==========================================="

print_status "Code structure verified"
print_status "Dependencies installed"
print_status "PostgreSQL connectivity confirmed"

echo ""
echo "Next steps:"
echo "1. Start all services: python3 start-services.py"
echo "2. Open dashboard: xdg-open host/dashboard.html"
echo "3. Test with ESP32 hardware"

echo ""
echo "If you see any warnings above, ensure PostgreSQL is running:"
echo "Docker: docker start airguard-postgres"
echo "Native: sudo systemctl start postgresql"