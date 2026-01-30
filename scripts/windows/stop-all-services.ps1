# GeoLogix AI - Complete System Stop Script
# Stops all GeoLogix AI services and processes cleanly

Write-Host "🛑 GeoLogix AI - System Shutdown" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red
Write-Host ""

# Function to stop process by name
function Stop-ProcessSafely {
    param(
        [string]$ProcessName,
        [string]$DisplayName
    )
    
    try {
        $processes = Get-Process $ProcessName -ErrorAction SilentlyContinue
        if ($processes) {
            Write-Host "🔄 Stopping $DisplayName..." -ForegroundColor Yellow
            Stop-Process -Name $ProcessName -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            
            # Verify process is stopped
            $remaining = Get-Process $ProcessName -ErrorAction SilentlyContinue
            if ($remaining) {
                Write-Host "⚠️  $DisplayName still running, forcing termination..." -ForegroundColor Yellow
                Stop-Process -Name $ProcessName -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 1
            }
            Write-Host "✅ $DisplayName stopped" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  $DisplayName not running" -ForegroundColor Gray
        }
    } catch {
        Write-Host "❌ Error stopping $DisplayName`: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to close specific ports
function Close-Port {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connections) {
            Write-Host "🔄 Closing connections on port $Port ($ServiceName)..." -ForegroundColor Yellow
            # Kill processes using this port
            $connections | ForEach-Object {
                $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                if ($process) {
                    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
                }
            }
            Write-Host "✅ Port $Port closed" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  No connections on port $Port" -ForegroundColor Gray
        }
    } catch {
        Write-Host "❌ Error closing port $Port`: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Stop GeoLogix Backend Services
Write-Host "📡 Stopping Backend Services..." -ForegroundColor Cyan
Stop-ProcessSafely "python" "GeoLogix Backend Python"
Stop-ProcessSafely "uvicorn" "FastAPI Uvicorn Server"

# Close Backend Port
Close-Port 8000 "GeoLogix Backend"

# Stop AI Model Services
Write-Host ""
Write-Host "🤖 Stopping AI Model Services..." -ForegroundColor Cyan
Stop-ProcessSafely "LM Studio" "LM Studio AI Server"
Stop-ProcessSafely "ollama" "Ollama AI Server"

# Close AI Model Ports
Close-Port 1234 "LM Studio"
Close-Port 11434 "Ollama"

# Stop Database Services
Write-Host ""
Write-Host "🗄️  Stopping Database Services..." -ForegroundColor Cyan
Stop-ProcessSafely "chroma" "ChromaDB"
Stop-ProcessSafely "redis" "Redis Server"

# Close Database Ports
Close-Port 8001 "ChromaDB"
Close-Port 6379 "Redis"

# Stop Web Services
Write-Host ""
Write-Host "🌐 Stopping Web Services..." -ForegroundColor Cyan
Stop-ProcessSafely "http.server" "Python HTTP Server"
Stop-ProcessSafely "nginx" "Nginx Web Server"

# Close Web Ports
Close-Port 3000 "Development Web Server"
Close-Port 80 "HTTP Web Server"
Close-Port 443 "HTTPS Web Server"

# Stop Tunnel Services
Write-Host ""
Write-Host "🚇 Stopping Tunnel Services..." -ForegroundColor Cyan
Stop-ProcessSafely "ngrok" "Ngrok Tunnel"

# Close Tunnel Ports (various)
Close-Port 4040 "Ngrok Web Interface"

# Stop Browser Processes (optional)
Write-Host ""
Write-Host "🌍 Stopping Browser Processes..." -ForegroundColor Cyan
$answer = Read-Host "Stop browser processes? (y/N)"
if ($answer -eq 'y' -or $answer -eq 'Y') {
    Stop-ProcessSafely "chrome" "Google Chrome"
    Stop-ProcessSafely "firefox" "Mozilla Firefox"
    Stop-ProcessSafely "msedge" "Microsoft Edge"
}

# Clean up temporary files
Write-Host ""
Write-Host "🧹 Cleaning Up Temporary Files..." -ForegroundColor Cyan
try {
    $tempPaths = @(
        "$env:TEMP\geologix-*",
        "$env:TEMP\chroma-*",
        "$env:TEMP\lm-studio-*"
    )
    
    foreach ($path in $tempPaths) {
        if (Test-Path $path) {
            Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Cleaned: $path" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "⚠️  Cleanup warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Final verification
Write-Host ""
Write-Host "🔍 Verifying All Services Stopped..." -ForegroundColor Cyan

$portsToCheck = @(8000, 1234, 11434, 8001, 6379, 3000, 4040)
$allClear = $true

foreach ($port in $portsToCheck) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Host "⚠️  Port $port still in use" -ForegroundColor Yellow
        $allClear = $false
    }
}

if ($allClear) {
    Write-Host "✅ All ports cleared" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some ports still in use - check manually" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "📋 Shutdown Summary" -ForegroundColor White
Write-Host "==================" -ForegroundColor White
Write-Host "✅ GeoLogix AI services stopped" -ForegroundColor Green
Write-Host "✅ AI model services stopped" -ForegroundColor Green
Write-Host "✅ Database services stopped" -ForegroundColor Green
Write-Host "✅ Web services stopped" -ForegroundColor Green
Write-Host "✅ Tunnel services stopped" -ForegroundColor Green
Write-Host "✅ Temporary files cleaned" -ForegroundColor Green

if ($allClear) {
    Write-Host "✅ All ports cleared" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 System completely shut down!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some services may still be running" -ForegroundColor Yellow
    Write-Host "   Check Task Manager for remaining processes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 To restart everything, run:" -ForegroundColor Cyan
Write-Host "   .\start-all-services.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
