# Airguard Services Shutdown Script
# This script stops all running Airguard services

Write-Host "Stopping Airguard services..." -ForegroundColor Yellow
Write-Host ""

# Stop Node.js processes
Write-Host "Stopping Node.js processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "[OK] Node.js processes stopped" -ForegroundColor Green

# Stop Python processes
Write-Host "Stopping Python processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*gateway*" } | Stop-Process -Force
Write-Host "[OK] Python processes stopped" -ForegroundColor Green

Write-Host ""
Write-Host "All services stopped!" -ForegroundColor Green
Write-Host "Run .\start-services.ps1 to restart" -ForegroundColor Cyan
