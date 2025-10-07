# PowerShell System Health Check for Windows

Write-Host "🔍 Airguard System Health Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check MongoDB
Write-Host "📊 MongoDB Status:" -ForegroundColor Yellow
try {
    $null = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($?) {
        Write-Host "  ✓ MongoDB port 27017 is open" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MongoDB port 27017 is closed" -ForegroundColor Red
    }
} catch {
    Write-Host "  ⚠ Could not check MongoDB" -ForegroundColor Yellow
}
Write-Host ""

# Check MQTT Broker
Write-Host "🔌 MQTT Broker Status:" -ForegroundColor Yellow
try {
    $null = Test-NetConnection -ComputerName localhost -Port 1883 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($?) {
        Write-Host "  ✓ MQTT port 1883 is open" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MQTT port 1883 is closed" -ForegroundColor Red
    }
} catch {
    Write-Host "  ⚠ Could not check MQTT" -ForegroundColor Yellow
}
Write-Host ""

# Check ports
Write-Host "🌐 Port Status:" -ForegroundColor Yellow

$ports = @(
    @{Port=8080; Name="Node Backend HTTP"},
    @{Port=8081; Name="WebSocket"},
    @{Port=1883; Name="MQTT"},
    @{Port=27017; Name="MongoDB"}
)

foreach ($p in $ports) {
    try {
        $result = Test-NetConnection -ComputerName localhost -Port $p.Port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($result) {
            Write-Host "  ✓ Port $($p.Port) ($($p.Name)) is open" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Port $($p.Port) ($($p.Name)) is closed" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ⚠ Could not check port $($p.Port)" -ForegroundColor Yellow
    }
}
Write-Host ""

# Check Node processes
Write-Host "⚙️  Node Processes:" -ForegroundColor Yellow
$nodeProcs = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcs) {
    Write-Host "  Running Node.js processes: $($nodeProcs.Count)" -ForegroundColor Green
} else {
    Write-Host "  No Node.js processes running" -ForegroundColor Yellow
}
Write-Host ""

# Check Python processes
Write-Host "🐍 Python Processes:" -ForegroundColor Yellow
$pythonProcs = Get-Process -Name "python*" -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "  Running Python processes: $($pythonProcs.Count)" -ForegroundColor Green
} else {
    Write-Host "  No Python processes running" -ForegroundColor Yellow
}
Write-Host ""

# Check SQLite database
Write-Host "💾 Database Stats:" -ForegroundColor Yellow
$dbPath = "host\python-gateway\airguard.db"
if (Test-Path $dbPath) {
    $dbSize = (Get-Item $dbPath).Length
    Write-Host "  SQLite database size: $([math]::Round($dbSize/1KB, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "  SQLite database not found" -ForegroundColor Yellow
}
Write-Host ""

# Check COM ports
Write-Host "🔌 Serial Ports:" -ForegroundColor Yellow
$ports = [System.IO.Ports.SerialPort]::getportnames()
if ($ports) {
    Write-Host "  Available COM ports: $($ports -join ', ')" -ForegroundColor Green
} else {
    Write-Host "  No COM ports detected" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Health check complete!" -ForegroundColor Cyan
