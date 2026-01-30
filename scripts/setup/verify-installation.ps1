# GeoLogix AI - Installation Verification Script
# Version: 1.0.0
# Checks all prerequisites and dependencies

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   🔍 GeoLogix AI Installation Checker" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true
$warnings = 0
$errors = 0

# Configuration
# Configuration
$basePath = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backendPath = Join-Path $basePath "geologix-ai\geologix-backend"

$pythonExe = $null
$pythonArgs = @()
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
    $pythonArgs = @("-3")
}

# Check 1: Python Installation
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[1/8] Checking Python..." -ForegroundColor Cyan
try {
    if (-not $pythonExe) {
        throw "PythonNotFound"
    }

    $pythonVersion = & $pythonExe @pythonArgs --version 2>&1
    if ($pythonVersion -match "Python 3\.1([0-9])") {
        Write-Host "      ✅ $pythonVersion" -ForegroundColor Green
    }
    elseif ($pythonVersion -match "Python 3\.([0-9])") {
        Write-Host "      ⚠️  $pythonVersion (Python 3.10+ recommended)" -ForegroundColor Yellow
        $warnings++
    }
    else {
        Write-Host "      ⚠️  $pythonVersion (unexpected version)" -ForegroundColor Yellow
        $warnings++
    }
    
    # Check pip
    $pipVersion = & $pythonExe @pythonArgs -m pip --version 2>&1
    Write-Host "      ✅ pip: $($pipVersion.Split(' ')[1])" -ForegroundColor Green
}
catch {
    Write-Host "      ❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "         Install from: https://www.python.org/downloads/" -ForegroundColor Gray
    $allGood = $false
    $errors++
}
Write-Host ""

# Check 2: Required Python Packages
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[2/8] Checking Python packages..." -ForegroundColor Cyan
$missingPackages = @()
$installedCount = 0

if (-not $pythonExe) {
    Write-Host "      ❌ Skipping package check (Python not found)" -ForegroundColor Red
    $allGood = $false
    $errors++
}
else {
    $requiredPackages = @(
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests",
        "python-multipart",
        "httpx",
        "python-jose",
        "passlib",
        "bcrypt",
        "beautifulsoup4",
        "lxml",
        "python-dotenv",
        "psutil"
    )

    foreach ($pkg in $requiredPackages) {
        $null = & $pythonExe @pythonArgs -m pip show $pkg 2>&1
        if ($LASTEXITCODE -eq 0) {
            $installedCount++
        }
        else {
            $missingPackages += $pkg
        }
    }

    if ($missingPackages.Count -eq 0) {
        Write-Host "      ✅ All $($requiredPackages.Count) required packages installed" -ForegroundColor Green
    }
    else {
        Write-Host "      ⚠️  $installedCount / $($requiredPackages.Count) packages installed" -ForegroundColor Yellow
        Write-Host "      Missing packages:" -ForegroundColor Red
        foreach ($pkg in $missingPackages) {
            Write-Host "        • $pkg" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "      Fix: Run the following command:" -ForegroundColor White
        if ($pythonExe -eq "py") {
            Write-Host "      py -3 -m pip install -r `"$backendPath\Configuration\requirements.txt`"" -ForegroundColor Gray
        }
        else {
            Write-Host "      python -m pip install -r `"$backendPath\Configuration\requirements.txt`"" -ForegroundColor Gray
        }
        $warnings++
    }
}
Write-Host ""

# Check 3: File Structure
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[3/8] Checking file structure..." -ForegroundColor Cyan
$requiredPaths = @(
    @{Path = "geologix-ai\geologix-backend\Core_System\server.py"; Desc = "Backend server" },
    @{Path = "geologix-ai\geologix-backend\Core_System\knowledge_engine.py"; Desc = "Knowledge engine" },
    @{Path = "geologix-ai\geologix-backend\Import_Tools"; Desc = "Import tools" },
    @{Path = "geologix-ai\geologix-backend\Configuration"; Desc = "Configuration" },
    @{Path = "geologix-ai\UI\index.html"; Desc = "UI landing page" },
    @{Path = "Company_documents"; Desc = "Company documents" },
    @{Path = "emails"; Desc = "Email archives" },
    @{Path = "knowledge_database"; Desc = "Knowledge database" }
)

$missingPaths = @()
foreach ($item in $requiredPaths) {
    $fullPath = Join-Path $basePath $item.Path
    if (Test-Path $fullPath) {
        Write-Host "      ✅ $($item.Desc)" -ForegroundColor Green
    }
    else {
        Write-Host "      ❌ $($item.Desc) - NOT FOUND" -ForegroundColor Red
        Write-Host "         Path: $fullPath" -ForegroundColor Gray
        $missingPaths += $item
        $errors++
    }
}

if ($missingPaths.Count -eq 0) {
    Write-Host "      ✅ All required files and directories present" -ForegroundColor Green
}
Write-Host ""

# Check 4: Configuration Files
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[4/8] Checking configuration..." -ForegroundColor Cyan
$envPath = Join-Path $backendPath "Configuration\.env"
$envExamplePath = Join-Path $backendPath "Configuration\.env.example"
$requirementsPath = Join-Path $backendPath "Configuration\requirements.txt"

if (Test-Path $requirementsPath) {
    Write-Host "      ✅ requirements.txt found" -ForegroundColor Green
}
else {
    Write-Host "      ❌ requirements.txt not found" -ForegroundColor Red
    $errors++
}

if (Test-Path $envPath) {
    Write-Host "      ✅ .env file configured" -ForegroundColor Green
}
elseif (Test-Path $envExamplePath) {
    Write-Host "      ⚠️  .env file not found (using defaults)" -ForegroundColor Yellow
    Write-Host "         Copy .env.example to .env and configure it" -ForegroundColor Gray
    $warnings++
}
else {
    Write-Host "      ⚠️  No environment configuration found" -ForegroundColor Yellow
    $warnings++
}
Write-Host ""

# Check 5: LM Studio
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[5/8] Checking LM Studio..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "      ✅ LM Studio is running and accessible" -ForegroundColor Green
    
    # Try to get model info
    $modelsData = $response.Content | ConvertFrom-Json
    if ($modelsData.data) {
        Write-Host "      ✅ AI models loaded: $($modelsData.data.Count)" -ForegroundColor Green
    }
}
catch {
    Write-Host "      ⚠️  LM Studio not detected (server not running)" -ForegroundColor Yellow
    Write-Host "         Download from: https://lmstudio.ai/" -ForegroundColor Gray
    Write-Host "         Make sure to load an AI model and start the server" -ForegroundColor Gray
    $warnings++
}
Write-Host ""

# Check 6: Backend Server
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[6/8] Checking backend server..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "      ✅ Backend server is running" -ForegroundColor Green
    
    # Parse response to show stats
    if ($response.StatusCode -eq 200) {
        try {
            $healthData = $response.Content | ConvertFrom-Json
            if ($healthData.status -eq "healthy") {
                Write-Host "      ✅ Server status: healthy" -ForegroundColor Green
            }
        }
        catch {
            # Ignore JSON parse errors
        }
    }
}
catch {
    Write-Host "      ⚠️  Backend server not running" -ForegroundColor Yellow
    Write-Host "         Start with: .\start-geologix.ps1" -ForegroundColor Gray
    $warnings++
}
Write-Host ""

# Check 7: Knowledge Base Data
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[7/8] Checking knowledge base..." -ForegroundColor Cyan

# Check for data in key directories
$emailFiles = @(Get-ChildItem -Path (Join-Path $basePath "emails") -File -Recurse -ErrorAction SilentlyContinue)
$docFiles = @(Get-ChildItem -Path (Join-Path $basePath "Company_documents") -File -Recurse -ErrorAction SilentlyContinue)
$kbFiles = @(Get-ChildItem -Path (Join-Path $basePath "knowledge_database") -File -Recurse -ErrorAction SilentlyContinue)

if ($emailFiles.Count -gt 0) {
    Write-Host "      ✅ Email archives: $($emailFiles.Count) files" -ForegroundColor Green
}
else {
    Write-Host "      ⚠️  Email archives: empty" -ForegroundColor Yellow
}

if ($docFiles.Count -gt 0) {
    Write-Host "      ✅ Company documents: $($docFiles.Count) files" -ForegroundColor Green
}
else {
    Write-Host "      ⚠️  Company documents: empty" -ForegroundColor Yellow
}

if ($kbFiles.Count -gt 0) {
    Write-Host "      ✅ Knowledge database: $($kbFiles.Count) files" -ForegroundColor Green
}
else {
    Write-Host "      ⚠️  Knowledge database: empty" -ForegroundColor Yellow
}

$chromaDbPath = Join-Path $backendPath "Data_Directories\chroma_db"
if (Test-Path $chromaDbPath) {
    Write-Host "      ✅ ChromaDB initialized" -ForegroundColor Green
}
else {
    Write-Host "      ⚠️  ChromaDB not initialized" -ForegroundColor Yellow
    Write-Host "         Run import scripts to populate the knowledge base" -ForegroundColor Gray
    $warnings++
}
Write-Host ""

# Check 8: Disk Space
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "[8/8] Checking system resources..." -ForegroundColor Cyan

$drive = (Get-Item $basePath).PSDrive
$freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
$totalSpaceGB = [math]::Round(($drive.Used + $drive.Free) / 1GB, 2)

Write-Host "      Disk space on $($drive.Name):\ - $freeSpaceGB GB free / $totalSpaceGB GB total" -ForegroundColor Gray

if ($freeSpaceGB -gt 50) {
    Write-Host "      ✅ Sufficient disk space" -ForegroundColor Green
}
elseif ($freeSpaceGB -gt 20) {
    Write-Host "      ⚠️  Low disk space (50GB+ recommended)" -ForegroundColor Yellow
    $warnings++
}
else {
    Write-Host "      ❌ Critical: Very low disk space" -ForegroundColor Red
    $errors++
}

# Check RAM
$ram = Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum
$ramGB = [math]::Round($ram.Sum / 1GB, 2)
Write-Host "      System RAM: $ramGB GB" -ForegroundColor Gray

if ($ramGB -ge 32) {
    Write-Host "      ✅ Excellent RAM capacity" -ForegroundColor Green
}
elseif ($ramGB -ge 16) {
    Write-Host "      ✅ Sufficient RAM" -ForegroundColor Green
}
else {
    Write-Host "      ⚠️  Low RAM (16GB+ recommended)" -ForegroundColor Yellow
    $warnings++
}
Write-Host ""

# Final Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   📊 Verification Summary" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ PERFECT! Installation is complete and ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor White
    Write-Host "  1. Run .\start-geologix.ps1 to launch the system" -ForegroundColor Gray
    Write-Host "  2. Import knowledge with Import_Tools scripts if needed" -ForegroundColor Gray
    Write-Host "  3. Access the UI at http://localhost:8000" -ForegroundColor Gray
}
elseif ($errors -eq 0) {
    Write-Host "⚠️  Installation ready with $warnings warning(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "System is functional but could be improved." -ForegroundColor White
    Write-Host "Review warnings above and fix when convenient." -ForegroundColor White
}
else {
    Write-Host "❌ Installation incomplete: $errors error(s), $warnings warning(s)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the errors above before running GeoLogix AI." -ForegroundColor White
    Write-Host "Check BUILD.md for detailed installation instructions." -ForegroundColor White
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
