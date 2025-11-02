# 🔐 SSH Remote Access Guide

## Accessing Airguard Dashboard via SSH

When working on a headless/remote device (Jetson Nano, Raspberry Pi, cloud server, etc.) accessed via SSH, you cannot directly open the HTML dashboard. Here are the solutions:

---

## 🚀 Quick Solutions

### Option 1: Dashboard Web Server (Simplest)

Start the built-in dashboard web server:

```bash
# Start the dashboard server
python3 serve-dashboard.py
```

**Output:**
```
============================================================
🌐 Airguard Dashboard Server
============================================================

✓ Serving dashboard from: /path/to/host
✓ Server running on port: 8082

📱 Access the dashboard at:
   • Local: http://localhost:8082/dashboard.html
   • Remote: http://<your-server-ip>:8082/dashboard.html

💡 SSH Port Forward:
   ssh -L 8082:localhost:8082 -L 8080:localhost:8080 -L 8081:localhost:8081 user@remote-host
   Then visit: http://localhost:8082/dashboard.html

⏸  Press Ctrl+C to stop the server
============================================================
```

**Then access from your browser:**
- If the server has a public IP: `http://192.168.1.100:8082/dashboard.html`
- If using SSH tunnel (see Option 2): `http://localhost:8082/dashboard.html`

---

### Option 2: SSH Port Forwarding (Most Secure)

Forward the necessary ports through your SSH connection:

```bash
# From your LOCAL machine, connect with port forwarding:
ssh -L 8082:localhost:8082 \
    -L 8080:localhost:8080 \
    -L 8081:localhost:8081 \
    user@remote-host
```

**Port mapping:**
- `8082` → Dashboard web server
- `8080` → REST API backend
- `8081` → WebSocket server

**On the remote device, start services:**
```bash
# Start all services
python3 start-services.py

# Start dashboard server
python3 serve-dashboard.py
```

**On your LOCAL machine's browser:**
```
http://localhost:8082/dashboard.html
```

All data will flow through the encrypted SSH tunnel! 🔒

---

### Option 3: Python's Simple HTTP Server

Quick one-liner using Python's built-in HTTP server:

```bash
# Navigate to the project directory
cd /path/to/airguard-esp32-iot

# Serve on port 8082 (or any available port)
python3 -m http.server 8082 --directory host

# Access at: http://<server-ip>:8082/dashboard.html
```

---

### Option 4: VS Code Remote SSH (Developer-Friendly)

If you use VS Code:

1. Install the "Remote - SSH" extension
2. Connect to your remote host
3. Open the project folder
4. Right-click `dashboard.html` → "Open with Live Server"

---

## 🔧 Firewall Configuration

If accessing via public IP, you may need to open ports:

**Ubuntu/Debian:**
```bash
sudo ufw allow 8082/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8081/tcp
sudo ufw reload
```

**Fedora/CentOS:**
```bash
sudo firewall-cmd --permanent --add-port=8082/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload
```

**Note:** Only open ports if necessary. SSH tunneling (Option 2) is more secure.

---

## 🎯 Complete Workflow Example

**Scenario:** You have a Jetson Nano running Airguard, accessed from your laptop.

**On your laptop:**
```bash
# Connect with port forwarding
ssh -L 8082:localhost:8082 -L 8080:localhost:8080 -L 8081:localhost:8081 jetson@192.168.1.100
```

**On the Jetson (via SSH):**
```bash
# Navigate to project
cd ~/airguard-esp32-iot

# Start all services
python3 start-services.py

# In another terminal (or background), start dashboard server
python3 serve-dashboard.py &
```

**On your laptop's browser:**
```
http://localhost:8082/dashboard.html
```

**Result:** You see the dashboard with real-time data, all traffic encrypted through SSH! ✨

---

## 🛠️ Troubleshooting

### "Connection refused" when accessing dashboard

**Check if the server is running:**
```bash
# On the remote device
ps aux | grep serve-dashboard
netstat -tlnp | grep 8082
```

**Check if ports are open:**
```bash
# On the remote device
sudo lsof -i :8082
sudo lsof -i :8080
sudo lsof -i :8081
```

### WebSocket connection fails

The dashboard needs ports **8080** (REST API) and **8081** (WebSocket) to function.

**Make sure all ports are forwarded:**
```bash
ssh -L 8082:localhost:8082 -L 8080:localhost:8080 -L 8081:localhost:8081 user@host
```

### Dashboard shows "Waiting for data..."

**Check backend services:**
```bash
# On remote device
python3 health-check.py
```

**Verify all services are running:**
- MQTT Broker (port 1883)
- Node Backend (port 8080, 8081)
- MQTT-MongoDB Bridge
- Python Gateway

---

## 🔐 Security Best Practices

1. **Use SSH tunneling** instead of exposing ports publicly
2. **Set up authentication** if you must expose ports:
   ```bash
   # Use nginx reverse proxy with basic auth
   sudo apt install nginx apache2-utils
   ```
3. **Use HTTPS** for production:
   ```bash
   # Use Let's Encrypt with nginx
   sudo apt install certbot python3-certbot-nginx
   ```
4. **Limit IP access** with firewall rules:
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8082
   ```

---

## 📚 Related Documentation

- [README.md](README.md) - Main project documentation
- [SETUP-LINUX.md](SETUP-LINUX.md) - Linux installation guide
- [SCRIPTS.md](SCRIPTS.md) - Cross-platform scripts reference

---

**Built with ❤️ for remote IoT development**
