# Airguard Full Stack Startup Script
# This script starts all services in the correct order

Write-Host "Starting Airguard Full Stack..." -ForegroundColor Green
Write-Host ""

# Check MongoDB
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
$mongoService = Get-Service MongoDB -ErrorAction SilentlyContinue
if ($mongoService.Status -ne 'Running') {
    Write-Host "Starting MongoDB..." -ForegroundColor Yellow
    Start-Service MongoDB
}
Write-Host "[OK] MongoDB is running" -ForegroundColor Green
Write-Host ""

# Start MQTT Broker
Write-Host "Starting MQTT Broker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Admin\esp32dongle\mqtt-broker; npm start"
Start-Sleep -Seconds 3
Write-Host "[OK] MQTT Broker started on port 1883" -ForegroundColor Green
Write-Host ""

# Start Node.js Backend
Write-Host "Starting Node.js Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Admin\esp32dongle\host\node-backend; npm start"
Start-Sleep -Seconds 3
Write-Host "[OK] Backend started (HTTP:8080, WS:8081)" -ForegroundColor Green
Write-Host ""

# Start MQTT-MongoDB Bridge
Write-Host "Starting MQTT-MongoDB Bridge..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Admin\esp32dongle\bridges\mqtt-mongo; node bridge.js"
Start-Sleep -Seconds 2
Write-Host "[OK] MQTT Bridge started" -ForegroundColor Green
Write-Host ""

# Start Python Gateway
Write-Host "Starting Python Gateway..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Admin\esp32dongle\host\python-gateway; python gateway_enhanced.py"
Start-Sleep -Seconds 2
Write-Host "[OK] Python Gateway started (COM12)" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ALL SERVICES RUNNING!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor Yellow
Write-Host "  MongoDB:        mongodb://localhost:27017" -ForegroundColor White
Write-Host "  MQTT Broker:    mqtt://localhost:1883" -ForegroundColor White
Write-Host "  REST API:       http://localhost:8080/v1/samples" -ForegroundColor White
Write-Host "  WebSocket:      ws://localhost:8081" -ForegroundColor White
Write-Host "  Python Gateway: COM12 at 115200 baud" -ForegroundColor White
Write-Host ""
Write-Host "Dashboard:" -ForegroundColor Yellow
Write-Host "  Open: C:\Users\Admin\esp32dongle\host\dashboard.html" -ForegroundColor White
Write-Host ""
Write-Host "Press button on ESP32 sender to see data flow!" -ForegroundColor Green
