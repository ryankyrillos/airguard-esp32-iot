#!/bin/bash
# System health check script

echo "🔍 Airguard System Health Check"
echo "================================"
echo ""

# Check MongoDB
echo "📊 MongoDB Status:"
if command -v mongosh &> /dev/null; then
    mongosh --eval "db.runCommand({ ping: 1 })" --quiet && echo "  ✓ MongoDB is running" || echo "  ✗ MongoDB is not running"
elif command -v mongo &> /dev/null; then
    mongo --eval "db.runCommand({ ping: 1 })" --quiet && echo "  ✓ MongoDB is running" || echo "  ✗ MongoDB is not running"
else
    echo "  ⚠ MongoDB client not found"
fi
echo ""

# Check MQTT Broker
echo "🔌 MQTT Broker Status:"
if command -v mosquitto_sub &> /dev/null; then
    timeout 1 mosquitto_sub -t test -C 1 &> /dev/null && echo "  ✓ MQTT broker is running" || echo "  ✗ MQTT broker not responding"
else
    echo "  ⚠ mosquitto_sub not found"
fi
echo ""

# Check ports
echo "🌐 Port Status:"
check_port() {
    local port=$1
    local name=$2
    if command -v nc &> /dev/null; then
        nc -z localhost $port &> /dev/null && echo "  ✓ Port $port ($name) is open" || echo "  ✗ Port $port ($name) is closed"
    elif command -v netstat &> /dev/null; then
        netstat -an | grep -q ":$port " && echo "  ✓ Port $port ($name) is listening" || echo "  ✗ Port $port ($name) not listening"
    else
        echo "  ⚠ Cannot check port $port (no nc or netstat)"
    fi
}

check_port 8080 "Node Backend HTTP"
check_port 8081 "WebSocket"
check_port 1883 "MQTT"
check_port 27017 "MongoDB"
echo ""

# Check Node processes
echo "⚙️  Node Processes:"
if command -v node &> /dev/null; then
    node_count=$(pgrep -c node 2>/dev/null || echo "0")
    echo "  Running Node.js processes: $node_count"
else
    echo "  ⚠ Node.js not found"
fi
echo ""

# Check Python processes
echo "🐍 Python Processes:"
if command -v python3 &> /dev/null; then
    python_count=$(pgrep -cf "gateway.py" 2>/dev/null || echo "0")
    echo "  Running gateway.py processes: $python_count"
else
    echo "  ⚠ Python3 not found"
fi
echo ""

# Check database
echo "💾 Database Stats:"
if command -v mongosh &> /dev/null; then
    count=$(mongosh airguard --eval "db.samples.countDocuments()" --quiet 2>/dev/null | tail -1)
    echo "  Samples in MongoDB: ${count:-unknown}"
elif command -v mongo &> /dev/null; then
    count=$(mongo airguard --eval "db.samples.countDocuments()" --quiet 2>/dev/null | tail -1)
    echo "  Samples in MongoDB: ${count:-unknown}"
fi

if [ -f "host/python-gateway/airguard.db" ]; then
    if command -v sqlite3 &> /dev/null; then
        count=$(sqlite3 host/python-gateway/airguard.db "SELECT COUNT(*) FROM samples" 2>/dev/null)
        echo "  Samples in SQLite: ${count:-unknown}"
    fi
fi
echo ""

echo "================================"
echo "Health check complete!"
