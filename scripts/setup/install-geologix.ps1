# GeoLogix AI - One-Click Install & Setup Script
# Version: 2.0.0
# This script installs all dependencies, downloads AI models, and starts the system

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   GeoLogix AI - One-Click Installer" -ForegroundColor Green
Write-Host "   Version 2.0 - Full Auto Setup" -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = $PSScriptRoot
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")
$backendPath = Join-Path $repoRoot "geologix-ai\geologix-backend"
$requirementsPath = Join-Path $backendPath "Configuration\requirements.txt"
$configPath = Join-Path $backendPath "Configuration\config.py"

# Track status
$errors = @()
$warnings = @()

# ============================================
# STEP 1: Check Python
# ============================================
Write-Host "[1/7] Checking Python installation..." -ForegroundColor Yellow

$pythonExe = $null
$pythonArgs = @()

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
    $pythonArgs = @("-3")
}

if (-not $pythonExe) {
    Write-Host "      [X] Python not found!" -ForegroundColor Red
    Write-Host "          Please install Python 3.10+ from https://www.python.org/downloads/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

$pythonVersion = & $pythonExe @pythonArgs --version 2>&1
Write-Host "      [OK] $pythonVersion" -ForegroundColor Green

# ============================================
# STEP 2: Install Python Dependencies
# ============================================
Write-Host ""
Write-Host "[2/7] Installing Python dependencies..." -ForegroundColor Yellow

if (Test-Path $requirementsPath) {
    Write-Host "      Installing from requirements.txt..." -ForegroundColor Gray
    & $pythonExe @pythonArgs -m pip install -r $requirementsPath --quiet --disable-pip-version-check 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      [OK] Dependencies installed" -ForegroundColor Green
    }
    else {
        Write-Host "      [!] Some packages may have failed - trying individually..." -ForegroundColor Yellow
        $corePackages = @("fastapi", "uvicorn", "pydantic", "requests", "python-multipart", "httpx", "python-jose", "passlib", "bcrypt", "beautifulsoup4", "lxml", "python-dotenv", "psutil", "aiofiles")
        foreach ($pkg in $corePackages) {
            & $pythonExe @pythonArgs -m pip install $pkg --quiet --disable-pip-version-check 2>&1 | Out-Null
        }
        Write-Host "      [OK] Core packages installed" -ForegroundColor Green
    }
}
else {
    Write-Host "      [!] requirements.txt not found, installing core packages..." -ForegroundColor Yellow
    & $pythonExe @pythonArgs -m pip install fastapi uvicorn pydantic requests python-multipart httpx psutil aiofiles --quiet 2>&1 | Out-Null
    Write-Host "      [OK] Core packages installed" -ForegroundColor Green
}

# ============================================
# STEP 3: Verify Core Modules
# ============================================
Write-Host ""
Write-Host "[3/7] Verifying core modules..." -ForegroundColor Yellow

$moduleCheck = & $pythonExe @pythonArgs -c "import fastapi, uvicorn, pydantic, requests, psutil; print('OK')" 2>&1
if ($moduleCheck -match "OK") {
    Write-Host "      [OK] All core modules verified" -ForegroundColor Green
}
else {
    Write-Host "      [X] Module verification failed" -ForegroundColor Red
    $errors += "Core modules failed to import"
}

# ============================================
# STEP 4: Setup Ollama & Download Model
# ============================================
Write-Host ""
Write-Host "[4/7] Setting up AI provider (Ollama)..." -ForegroundColor Yellow

$ollamaAvailable = $false
$ollamaModel = $null

# Check if Ollama is installed
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "      [OK] Ollama installed" -ForegroundColor Green
    
    # Check if Ollama service is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        $ollamaAvailable = $true
    }
    catch {
        Write-Host "      [i] Starting Ollama service..." -ForegroundColor Gray
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            $ollamaAvailable = $true
            Write-Host "      [OK] Ollama service started" -ForegroundColor Green
        }
        catch {
            Write-Host "      [!] Could not start Ollama service" -ForegroundColor Yellow
        }
    }
    
    if ($ollamaAvailable) {
        # Get available models
        $models = ($response.Content | ConvertFrom-Json).models
        $modelNames = @()
        if ($models) {
            $modelNames = $models | ForEach-Object { $_.name }
        }
        
        # Preferred models in order (smaller first for memory efficiency)
        $preferredModels = @("llama3.2:1b", "llama3.2:3b", "llama3:latest", "mistral:latest")
        
        # Find first available preferred model
        foreach ($pref in $preferredModels) {
            if ($modelNames -contains $pref) {
                $ollamaModel = $pref
                Write-Host "      [OK] Found model: $ollamaModel" -ForegroundColor Green
                break
            }
        }
        
        # If no preferred model found, download llama3.2:1b (smallest, works with limited RAM)
        if (-not $ollamaModel) {
            Write-Host "      [i] No suitable model found. Downloading llama3.2:1b (1.3GB)..." -ForegroundColor Yellow
            Write-Host "          This is a smaller model that works with limited RAM" -ForegroundColor Gray
            
            $pullProcess = Start-Process "ollama" -ArgumentList "pull llama3.2:1b" -PassThru -Wait -NoNewWindow
            
            if ($pullProcess.ExitCode -eq 0) {
                $ollamaModel = "llama3.2:1b"
                Write-Host "      [OK] Model downloaded: $ollamaModel" -ForegroundColor Green
            }
            else {
                Write-Host "      [X] Failed to download model" -ForegroundColor Red
                $errors += "Failed to download Ollama model"
            }
        }
        
        # Test the model actually works (memory check)
        if ($ollamaModel) {
            Write-Host "      [i] Testing model (checking memory)..." -ForegroundColor Gray
            $testResult = & $pythonExe @pythonArgs -c "import requests; r = requests.post('http://localhost:11434/api/chat', json={'model': '$ollamaModel', 'messages': [{'role': 'user', 'content': 'Hi'}], 'stream': False}, timeout=60); print('OK' if r.status_code == 200 else r.json().get('error', 'FAIL'))" 2>&1
            
            if ($testResult -match "OK") {
                Write-Host "      [OK] Model tested successfully" -ForegroundColor Green
            }
            elseif ($testResult -match "memory") {
                Write-Host "      [!] Not enough memory for $ollamaModel" -ForegroundColor Yellow
                
                # Try downloading even smaller model or suggest closing apps
                if ($ollamaModel -ne "llama3.2:1b") {
                    Write-Host "      [i] Trying smaller model llama3.2:1b..." -ForegroundColor Gray
                    Start-Process "ollama" -ArgumentList "pull llama3.2:1b" -PassThru -Wait -NoNewWindow | Out-Null
                    $ollamaModel = "llama3.2:1b"
                }
                else {
                    Write-Host "      [!] Please close other applications to free up RAM" -ForegroundColor Yellow
                    $warnings += "Low memory - close other apps for better AI performance"
                }
            }
            else {
                Write-Host "      [!] Model test returned: $testResult" -ForegroundColor Yellow
            }
        }
        
        # Update config.py with the working model
        if ($ollamaModel -and (Test-Path $configPath)) {
            $configContent = Get-Content $configPath -Raw
            if ($configContent -match 'OLLAMA_MODEL = "[^"]*"') {
                $configContent = $configContent -replace 'OLLAMA_MODEL = "[^"]*"', "OLLAMA_MODEL = `"$ollamaModel`""
                Set-Content $configPath -Value $configContent -NoNewline
                Write-Host "      [OK] Config updated to use $ollamaModel" -ForegroundColor Green
            }
        }
    }
}
else {
    Write-Host "      [!] Ollama not installed" -ForegroundColor Yellow
    Write-Host "          Download from: https://ollama.ai" -ForegroundColor Gray
    $warnings += "Ollama not installed - download from https://ollama.ai"
    
    # Check LM Studio as fallback
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "      [OK] LM Studio detected as fallback" -ForegroundColor Green
    }
    catch {
        $warnings += "No AI provider available"
    }
}

# ============================================
# STEP 5: Verify File Structure
# ============================================
Write-Host ""
Write-Host "[5/7] Verifying file structure..." -ForegroundColor Yellow

$requiredFiles = @(
    @{Path = "geologix-backend\Core_System\server.py"; Name = "Backend server" },
    @{Path = "geologix-backend\Core_System\knowledge_engine.py"; Name = "Knowledge engine" },
    @{Path = "geologix-backend\Core_System\mcp_tools.py"; Name = "MCP tools" },
    @{Path = "UI\variant-6-copilot.html"; Name = "Copilot UI" },
    @{Path = "UI\index.html"; Name = "Landing page" }
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $scriptDir $file.Path
    if (Test-Path $fullPath) {
        Write-Host "      [OK] $($file.Name)" -ForegroundColor Green
    }
    else {
        Write-Host "      [X] $($file.Name) - MISSING" -ForegroundColor Red
        $errors += "Missing: $($file.Path)"
    }
}

# ============================================
# STEP 6: Start Backend Server
# ============================================
Write-Host ""
Write-Host "[6/7] Starting backend server..." -ForegroundColor Yellow

# Check if already running
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "      [OK] Backend already running on port 8000" -ForegroundColor Green
    }
}
catch {
    # Not running, start it
    Write-Host "      [i] Starting backend server..." -ForegroundColor Gray
    
    $backendScript = @"
cd '$backendPath'
& '$pythonExe' $($pythonArgs -join ' ') -m uvicorn Core_System.server:app --host 0.0.0.0 --port 8000
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal
    
    # Wait for backend to start
    $maxAttempts = 15
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 1
        $attempt++
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $backendRunning = $true
                Write-Host "      [OK] Backend started successfully" -ForegroundColor Green
                break
            }
        }
        catch {
            Write-Host "      [i] Waiting for backend... ($attempt/$maxAttempts)" -ForegroundColor Gray
        }
    }
    
    if (-not $backendRunning) {
        Write-Host "      [!] Backend may still be starting..." -ForegroundColor Yellow
        $warnings += "Backend startup slow - check the backend window"
    }
}

# ============================================
# STEP 7: Test Full System
# ============================================
Write-Host ""
Write-Host "[7/7] Testing full system..." -ForegroundColor Yellow

if ($backendRunning) {
    # Test API endpoints
    try {
        $healthCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 5
        Write-Host "      [OK] API health check passed" -ForegroundColor Green
    }
    catch {
        Write-Host "      [X] API health check failed" -ForegroundColor Red
    }
    
    try {
        $statsCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/stats" -UseBasicParsing -TimeoutSec 5
        $stats = $statsCheck.Content | ConvertFrom-Json
        Write-Host "      [OK] Knowledge base: $($stats.total_items) items indexed" -ForegroundColor Green
    }
    catch {
        Write-Host "      [!] Could not get knowledge base stats" -ForegroundColor Yellow
    }
    
    try {
        $aiCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/ai/status" -UseBasicParsing -TimeoutSec 5
        $aiStatus = $aiCheck.Content | ConvertFrom-Json
        if ($aiStatus.available) {
            Write-Host "      [OK] AI provider: $($aiStatus.provider) ($($aiStatus.model))" -ForegroundColor Green
        }
        else {
            Write-Host "      [!] AI provider not available" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "      [!] Could not check AI status" -ForegroundColor Yellow
    }
}

# ============================================
# SUMMARY & LAUNCH
# ============================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Installation Complete" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "[OK] GeoLogix AI is READY!" -ForegroundColor Green
    
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "Warnings:" -ForegroundColor Yellow
        foreach ($w in $warnings) {
            Write-Host "   [!] $w" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Opening GeoLogix AI in your browser..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
    
}
else {
    Write-Host "[X] Installation had $($errors.Count) error(s):" -ForegroundColor Red
    foreach ($e in $errors) {
        Write-Host "   [X] $e" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please fix the errors above and run this script again." -ForegroundColor White
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
