# GeoLogix AI - Quick Start Script for Windows
# Run this script to start the entire system
# Version: 1.0.0

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   🚀 GeoLogix AI System Launcher" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
# Configuration
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backendPath = Join-Path $repoRoot "geologix-ai\geologix-backend"
$uiFilePath = Join-Path $repoRoot "geologix-ai\UI\index.html"
$uiUrl = "http://localhost:8000/"
$healthCheckUrl = "http://localhost:8000/api/health"
$lmStudioUrl = "http://localhost:1234/v1/models"
$ollamaUrl = "http://localhost:11434/api/tags"

$configPath = Join-Path $backendPath "Configuration\config.py"
$aiProvider = "ollama"
if (Test-Path $configPath) {
    try {
        $configText = Get-Content $configPath -Raw -ErrorAction Stop
        $match = [regex]::Match($configText, 'AI_PROVIDER\s*=\s*"([^"]+)"')
        if ($match.Success) {
            $aiProvider = $match.Groups[1].Value
        }
    } catch {
    }
}

$pythonExe = $null
$pythonArgs = @()
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
    $pythonArgs = @("-3")
}

$pythonCmd = $pythonExe
if ($pythonExe -eq "py") {
    $pythonCmd = "py -3"
}

# Check if running as Administrator (recommended but not required)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  Note: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some features may require elevated privileges" -ForegroundColor Gray
    Write-Host ""
}

# Step 1: Check LM Studio
$lmStudioRunning = $false
$ollamaRunning = $false

if ($aiProvider -eq "lmstudio") {
    Write-Host "[1/5] Checking LM Studio..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri $lmStudioUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-Host "      ✅ LM Studio is running and responsive" -ForegroundColor Green
        $lmStudioRunning = $true
    } catch {
        Write-Host "      ⚠️  LM Studio is not running or not responding" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "      Please start LM Studio and:" -ForegroundColor White
        Write-Host "      1. Go to 'Local Server' tab" -ForegroundColor Gray
        Write-Host "      2. Load the Llama 3.1 8B Instruct model" -ForegroundColor Gray
        Write-Host "      3. Click 'Start Server' (port 1234)" -ForegroundColor Gray
        Write-Host ""
        $continue = Read-Host "      Press ENTER when LM Studio is ready, or type 'skip' to continue anyway"
        if ($continue -eq "skip") {
            Write-Host "      ⚠️  Continuing without LM Studio (AI features will not work)" -ForegroundColor Yellow
        } else {
            # Verify again
            try {
                $response = Invoke-WebRequest -Uri $lmStudioUrl -UseBasicParsing -TimeoutSec 3
                Write-Host "      ✅ LM Studio is now running" -ForegroundColor Green
                $lmStudioRunning = $true
            } catch {
                Write-Host "      ❌ Still cannot connect to LM Studio" -ForegroundColor Red
                Write-Host "      Continuing anyway..." -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "[1/5] Checking Ollama..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri $ollamaUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-Host "      ✅ Ollama is running and responsive" -ForegroundColor Green
        $ollamaRunning = $true
    } catch {
        Write-Host "      ⚠️  Ollama is not running or not responding" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "      Please start Ollama (default port 11434)" -ForegroundColor White
        Write-Host "      Command: ollama serve" -ForegroundColor Gray
        Write-Host ""
        $continue = Read-Host "      Press ENTER when Ollama is ready, or type 'skip' to continue anyway"
        if ($continue -eq "skip") {
            Write-Host "      ⚠️  Continuing without Ollama (AI features will not work)" -ForegroundColor Yellow
        } else {
            try {
                $response = Invoke-WebRequest -Uri $ollamaUrl -UseBasicParsing -TimeoutSec 3
                Write-Host "      ✅ Ollama is now running" -ForegroundColor Green
                $ollamaRunning = $true
            } catch {
                Write-Host "      ❌ Still cannot connect to Ollama" -ForegroundColor Red
                Write-Host "      Continuing anyway..." -ForegroundColor Yellow
            }
        }
    }
}
Write-Host ""

# Step 2: Check Python
Write-Host "[2/5] Checking Python environment..." -ForegroundColor Cyan
try {
    if (-not $pythonExe) {
        throw "PythonNotFound"
    }
    $pythonVersion = & $pythonExe @pythonArgs --version 2>&1
    Write-Host "      ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "      Please install Python 3.10+ and add to PATH" -ForegroundColor Red
    Write-Host "      Download from: https://www.python.org/downloads/" -ForegroundColor White
    exit 1
}
Write-Host ""

# Step 3: Check backend directory
Write-Host "[3/5] Verifying backend files..." -ForegroundColor Cyan
if (-not (Test-Path $backendPath)) {
    Write-Host "      ❌ Backend path not found: $backendPath" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "$backendPath\Core_System\server.py")) {
    Write-Host "      ❌ server.py not found" -ForegroundColor Red
    exit 1
}
Write-Host "      ✅ Backend files verified" -ForegroundColor Green
Write-Host ""

# Step 4: Start backend server
Write-Host "[4/5] Starting backend server..." -ForegroundColor Cyan
Write-Host "      Opening new PowerShell window..." -ForegroundColor Gray

# Start backend in new window
$backendStartArgs = "-NoExit", "-Command", @"
`$Host.UI.RawUI.WindowTitle = 'GeoLogix AI - Backend Server'
Write-Host '================================================' -ForegroundColor Cyan
Write-Host '   GeoLogix AI Backend Server' -ForegroundColor Green
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
cd '$backendPath'
$pythonCmd -m uvicorn Core_System.server:app --host 0.0.0.0 --port 8000 --reload
"@

Start-Process powershell -ArgumentList $backendStartArgs

# Wait for server to initialize
Write-Host "      ⏳ Waiting for server to initialize..." -ForegroundColor Yellow
$maxAttempts = 15
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri $healthCheckUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "      ✅ Backend server is running!" -ForegroundColor Green
            $serverReady = $true
            break
        }
    } catch {
        $attempt++
        Write-Host "      ⏳ Attempt $attempt / $maxAttempts..." -ForegroundColor Gray
    }
}

if (-not $serverReady) {
    Write-Host "      ❌ Backend server failed to start within 30 seconds" -ForegroundColor Red
    Write-Host "      Check the PowerShell window for error messages" -ForegroundColor Red
    Write-Host ""
    $continue = Read-Host "Press ENTER to continue anyway, or type 'exit' to abort"
    if ($continue -eq "exit") {
        exit 1
    }
}
Write-Host ""

# Step 5: Open UI
Write-Host "[5/5] Launching user interface..." -ForegroundColor Cyan
if ($serverReady) {
    Start-Process $uiUrl
    Write-Host "      ✅ UI opened in default browser" -ForegroundColor Green
} elseif (Test-Path $uiFilePath) {
    Start-Process $uiFilePath
    Write-Host "      ✅ UI opened in default browser" -ForegroundColor Green
} else {
    Write-Host "      ⚠️  UI file not found: $uiFilePath" -ForegroundColor Yellow
    Write-Host "      You can manually open any HTML file in the UI folder" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   ✅ GeoLogix AI is Now Running!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "System Status:" -ForegroundColor White
Write-Host "  • Backend API:  http://localhost:8000" -ForegroundColor Gray
if ($aiProvider -eq "lmstudio") {
    if ($lmStudioRunning) {
        Write-Host "  • LM Studio:    http://localhost:1234 ✅" -ForegroundColor Green
    } else {
        Write-Host "  • LM Studio:    http://localhost:1234 ⚠️ (not detected)" -ForegroundColor Yellow
    }
} else {
    if ($ollamaRunning) {
        Write-Host "  • Ollama:       http://localhost:11434 ✅" -ForegroundColor Green
    } else {
        Write-Host "  • Ollama:       http://localhost:11434 ⚠️ (not detected)" -ForegroundColor Yellow
    }
}
Write-Host "  • Frontend:     Check your browser" -ForegroundColor Gray
Write-Host ""
Write-Host "Usage Tips:" -ForegroundColor White
Write-Host "  • The backend runs in a separate PowerShell window" -ForegroundColor Gray
Write-Host "  • Press Ctrl+C in that window to stop the server" -ForegroundColor Gray
Write-Host "  • Keep that window open while using GeoLogix AI" -ForegroundColor Gray
Write-Host ""
Write-Host "Need Help?" -ForegroundColor White
Write-Host "  • Check BUILD.md for full documentation" -ForegroundColor Gray
Write-Host "  • Run verify-installation.ps1 to diagnose issues" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
