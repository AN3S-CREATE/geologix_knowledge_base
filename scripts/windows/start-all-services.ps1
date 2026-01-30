# GeoLogix AI - Complete System Start Script
# Starts all GeoLogix AI services and establishes connectivity

Write-Host "🚀 GeoLogix AI - System Startup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Configuration
$PROJECT_ROOT = "Q:\Dev\Google Avinity\geologix_knowledge_base"
$GEOLOGIX_PATH = "$PROJECT_ROOT\geologix-ai"
$BACKEND_PATH = "$GEOLOGIX_PATH\geologix-backend"
$UI_PATH = "$GEOLOGIX_PATH\UI"

# Function to check if port is available
function Test-PortAvailable {
    param([int]$Port)
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $null -eq $connection
    } catch {
        return $true
    }
}

# Function to wait for service to be ready
function Wait-Service {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$TimeoutSeconds = 30
    )
    
    Write-Host "⏳ Waiting for $ServiceName to be ready..." -ForegroundColor Yellow
    
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            Write-Host "✅ $ServiceName is ready!" -ForegroundColor Green
            return $true
        } catch {
            Start-Sleep -Seconds 1
            $elapsed++
        }
    }
    
    Write-Host "❌ $ServiceName failed to start within $TimeoutSeconds seconds" -ForegroundColor Red
    return $false
}

# Function to start process with validation
function Start-ServiceProcess {
    param(
        [string]$Executable,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [string]$ServiceName,
        [int]$Port
    )
    
    if (-not (Test-PortAvailable $Port)) {
        Write-Host "⚠️  Port $Port is already in use" -ForegroundColor Yellow
        $choice = Read-Host "Kill process on port $Port and continue? (y/N)"
        if ($choice -ne 'y' -and $choice -ne 'Y') {
            return $false
        }
        
        # Kill process on port
        try {
            $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
            if ($connection) {
                Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
        } catch {
            Write-Host "❌ Could not kill process on port $Port" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "🔄 Starting $ServiceName..." -ForegroundColor Cyan
    
    try {
        if ($Arguments) {
            Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -WindowStyle Minimized
        } else {
            Start-Process -FilePath $Executable -WorkingDirectory $WorkingDirectory -WindowStyle Minimized
        }
        
        Write-Host "✅ $ServiceName started" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to start $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Step 1: Check prerequisites
Write-Host "🔍 Checking Prerequisites..." -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check project structure
$requiredPaths = @($BACKEND_PATH, $UI_PATH, "$UI_PATH\index.html")
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        Write-Host "❌ Required path not found: $path" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Project structure validated" -ForegroundColor Green

# Step 2: Start AI Model Service
Write-Host ""
Write-Host "🤖 Starting AI Model Service..." -ForegroundColor Cyan
Write-Host ""

# Check for LM Studio
$lmStudioRunning = Get-Process "LM Studio" -ErrorAction SilentlyContinue
if ($lmStudioRunning) {
    Write-Host "✅ LM Studio already running" -ForegroundColor Green
} else {
    Write-Host "🔍 Looking for LM Studio..." -ForegroundColor Yellow
    $lmStudioPaths = @(
        "$env:LOCALAPPDATA\Programs\LM Studio\LM Studio.exe",
        "$env:PROGRAMFILES\LM Studio\LM Studio.exe",
        "LM Studio.exe"
    )
    
    $lmStudioFound = $false
    foreach ($path in $lmStudioPaths) {
        if (Test-Path $path) {
            Write-Host "🚀 Starting LM Studio..." -ForegroundColor Cyan
            Start-Process -FilePath $path -WindowStyle Normal
            Write-Host "✅ LM Studio started" -ForegroundColor Green
            $lmStudioFound = $true
            break
        }
    }
    
    if (-not $lmStudioFound) {
        Write-Host "⚠️  LM Studio not found. Please start LM Studio manually with Llama 3.1 8B model" -ForegroundColor Yellow
        $choice = Read-Host "Continue anyway? (y/N)"
        if ($choice -ne 'y' -and $choice -ne 'Y') {
            exit 1
        }
    }
}

# Wait for LM Studio to be ready
if ($lmStudioFound) {
    if (-not (Wait-Service "http://localhost:1234/v1/models" "LM Studio" 60)) {
        Write-Host "⚠️  LM Studio not ready, but continuing..." -ForegroundColor Yellow
    }
}

# Step 3: Start Backend Service
Write-Host ""
Write-Host "📡 Starting Backend Service..." -ForegroundColor Cyan
Write-Host ""

# Install dependencies if needed
Write-Host "🔧 Checking Python dependencies..." -ForegroundColor Yellow
Set-Location $BACKEND_PATH
try {
    pip show fastapi > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
        pip install -r Configuration\requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ Dependencies already installed" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error checking dependencies" -ForegroundColor Red
    exit 1
}

# Start backend server
Write-Host "🚀 Starting GeoLogix Backend..." -ForegroundColor Cyan
$backendProcess = Start-Process -FilePath "python" -ArgumentList "Core_System\server.py" -WorkingDirectory $BACKEND_PATH -PassThru -WindowStyle Minimized

if ($backendProcess) {
    Write-Host "✅ Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green
    
    # Wait for backend to be ready
    if (Wait-Service "http://localhost:8000/api/health" "GeoLogix Backend" 30) {
        Write-Host "✅ Backend is healthy and ready" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend failed to start properly" -ForegroundColor Red
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
        exit 1
    }
} else {
    Write-Host "❌ Failed to start backend process" -ForegroundColor Red
    exit 1
}

# Step 4: Test Backend Connectivity
Write-Host ""
Write-Host "🔗 Testing Backend Connectivity..." -ForegroundColor Cyan
Write-Host ""

$endpoints = @(
    @{Url="http://localhost:8000/api/health"; Name="Health Check"},
    @{Url="http://localhost:8000/api/stats"; Name="Stats API"},
    @{Url="http://localhost:8000/api/search?query=test&limit=5"; Name="Search API"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ $($endpoint.Name): OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($endpoint.Name): Failed" -ForegroundColor Red
    }
}

# Step 5: Start Web Interface
Write-Host ""
Write-Host "🌐 Starting Web Interface..." -ForegroundColor Cyan
Write-Host ""

# Start simple HTTP server for UI
Set-Location $UI_PATH
$webProcess = Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "3000" -WorkingDirectory $UI_PATH -PassThru -WindowStyle Minimized

if ($webProcess) {
    Write-Host "✅ Web server started (PID: $($webProcess.Id))" -ForegroundColor Green
    Write-Host "🌍 UI available at: http://localhost:3000" -ForegroundColor Cyan
    
    # Wait a moment for web server
    Start-Sleep -Seconds 3
    
    # Test web interface
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        Write-Host "✅ Web interface accessible" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Web interface may not be fully ready yet" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Failed to start web server" -ForegroundColor Red
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

# Step 6: Open Browser
Write-Host ""
Write-Host "🌍 Launching Browser..." -ForegroundColor Cyan

$browserUrls = @(
    "http://localhost:3000/index.html",
    "http://localhost:3000/variant-6-copilot.html"
)

foreach ($url in $browserUrls) {
    try {
        Start-Process $url
        Write-Host "✅ Opened: $url" -ForegroundColor Green
        Start-Sleep -Seconds 1
    } catch {
        Write-Host "⚠️  Could not open browser for: $url" -ForegroundColor Yellow
    }
}

# Step 7: Optional - Start Ngrok Tunnel
Write-Host ""
Write-Host "🚇 External Access Setup..." -ForegroundColor Cyan
$choice = Read-Host "Start Ngrok tunnel for external access? (y/N)"

if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "🔍 Checking for Ngrok..." -ForegroundColor Yellow
    
    $ngrokPaths = @(
        "$env:PROGRAMFILES\ngrok\ngrok.exe",
        "$env:LOCALAPPDATA\ngrok\ngrok.exe",
        "ngrok.exe"
    )
    
    $ngrokFound = $false
    foreach ($path in $ngrokPaths) {
        if (Test-Path $path) {
            Write-Host "🚇 Starting Ngrok tunnel..." -ForegroundColor Cyan
            Start-Process -FilePath $path -ArgumentList "http", "3000", "--log=stdout" -WindowStyle Minimized
            Write-Host "✅ Ngrok started" -ForegroundColor Green
            Write-Host "🌐 Check Ngrok interface for public URL" -ForegroundColor Cyan
            $ngrokFound = $true
            break
        }
    }
    
    if (-not $ngrokFound) {
        Write-Host "⚠️  Ngrok not found. Please install Ngrok or start manually" -ForegroundColor Yellow
    }
}

# Step 8: Final System Check
Write-Host ""
Write-Host "🔍 Final System Check..." -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="GeoLogix Backend"; Port=8000; Url="http://localhost:8000/api/health"},
    @{Name="LM Studio"; Port=1234; Url="http://localhost:1234/v1/models"},
    @{Name="Web Interface"; Port=3000; Url="http://localhost:3000"}
)

$allGood = $true
foreach ($service in $services) {
    $portAvailable = -not (Test-PortAvailable $service.Port)
    $serviceReady = $false
    
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 3
        $serviceReady = $true
    } catch {
        $serviceReady = $false
    }
    
    if ($portAvailable -and $serviceReady) {
        Write-Host "✅ $($service.Name): Running" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Name): Not ready" -ForegroundColor Red
        $allGood = $false
    }
}

# Summary
Write-Host ""
Write-Host "📋 Startup Summary" -ForegroundColor White
Write-Host "==================" -ForegroundColor White

if ($allGood) {
    Write-Host "🎉 All services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor Cyan
    Write-Host "   • Main UI: http://localhost:3000/index.html" -ForegroundColor White
    Write-Host "   • Copilot UI: http://localhost:3000/variant-6-copilot.html" -ForegroundColor White
    Write-Host "   • Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "   • Health Check: http://localhost:8000/api/health" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 To stop all services, run:" -ForegroundColor Cyan
    Write-Host "   .\stop-all-services.ps1" -ForegroundColor White
} else {
    Write-Host "⚠️  Some services may not be running properly" -ForegroundColor Yellow
    Write-Host "   Check the individual service windows for errors" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 Process IDs:" -ForegroundColor Cyan
Write-Host "   • Backend: $($backendProcess.Id)" -ForegroundColor White
Write-Host "   • Web Server: $($webProcess.Id)" -ForegroundColor White

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
