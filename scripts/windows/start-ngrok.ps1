# GeoLogix AI - ngrok Tunnel Script
# Exposes local backend to the internet

param(
    [string]$Domain = "geologix.ngrok.io"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GeoLogix AI - ngrok Tunnel" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] ngrok not found in PATH" -ForegroundColor Red
    Write-Host "Install ngrok and ensure 'ngrok' is available on PATH." -ForegroundColor Yellow
    exit 1
}

# Check if backend is running
$backendRunning = $false
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 3 -ErrorAction Stop
    $backendRunning = $true
    Write-Host "[OK] Backend server is running on port 8000" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Backend not detected on port 8000" -ForegroundColor Yellow
    Write-Host "Starting backend server first..." -ForegroundColor Yellow
    # Start backend in background
    $backendPath = Join-Path $PSScriptRoot "geologix-backend"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python -m uvicorn Core_System.server:app --host 0.0.0.0 --port 8000 --reload"
    
    Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
    $maxAttempts = 15
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 2
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 2 -ErrorAction Stop
            $backendRunning = $true
            Write-Host "[OK] Backend server is running on port 8000" -ForegroundColor Green
            break
        } catch {
            $attempt++
        }
    }
}

Write-Host ""
Write-Host "Starting ngrok tunnel to port 8000..." -ForegroundColor Cyan
Write-Host ""

# Start ngrok with custom domain (paid plan)
if ($Domain) {
    ngrok http 8000 --domain=$Domain
} else {
    ngrok http 8000
}

# Note: ngrok will display the public URL in its interface
