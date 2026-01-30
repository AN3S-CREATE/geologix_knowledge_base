# GeoLogix AI - Complete Connectivity Test Script
# Tests all services and connections in the GeoLogix AI system

Write-Host "🔍 GeoLogix AI - Connectivity Test Suite" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BACKEND_URL = "http://localhost:8000"
$UI_URL = "http://localhost:3000"
$AI_MODEL_URL = "http://localhost:1234"

# Test results tracking
$tests = @()
$passed = 0
$failed = 0

# Function to run a test
function Test-Service {
    param(
        [string]$TestName,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null,
        [int]$TimeoutSeconds = 10,
        [hashtable]$Headers = @{}
    )
    
    Write-Host "🧪 Testing: $TestName" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri             = $Url
            Method          = $Method
            TimeoutSec      = $TimeoutSeconds
            UseBasicParsing = $true
            Headers         = $Headers
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        $status = $response.StatusCode
        $content = $response.Content.Substring(0, [Math]::Min(100, $response.Content.Length))
        
        if ($status -ge 200 -and $status -lt 300) {
            Write-Host "✅ PASS ($status)" -ForegroundColor Green
            Write-Host "   Response: $content..." -ForegroundColor Gray
            $script:passed++
            $script:tests += @{Name = $TestName; Status = "PASS"; Status_code = $status; Url = $Url }
            return $true
        }
        else {
            Write-Host "❌ FAIL ($status)" -ForegroundColor Red
            $script:failed++
            $script:tests += @{Name = $TestName; Status = "FAIL"; Status_code = $status; Url = $Url }
            return $false
        }
    }
    catch {
        Write-Host "❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        $script:tests += @{Name = $TestName; Status = "FAIL"; Error = $_.Exception.Message; Url = $Url }
        return $false
    }
}

# Function to test port availability
function Test-Port {
    param(
        [string]$ServiceName,
        [int]$Port
    )
    
    Write-Host "🔌 Testing Port: $ServiceName (Port $Port)" -ForegroundColor Yellow
    
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Host "✅ PASS: Port $Port is open" -ForegroundColor Green
            $script:passed++
            $script:tests += @{Name = "$ServiceName Port"; Status = "PASS"; Port = $Port }
            return $true
        }
        else {
            Write-Host "❌ FAIL: Port $Port is closed" -ForegroundColor Red
            $script:failed++
            $script:tests += @{Name = "$ServiceName Port"; Status = "FAIL"; Port = $Port }
            return $false
        }
    }
    catch {
        Write-Host "❌ FAIL: Cannot check port $Port" -ForegroundColor Red
        $script:failed++
        $script:tests += @{Name = "$ServiceName Port"; Status = "FAIL"; Error = $_.Exception.Message; Port = $Port }
        return $false
    }
}

# Function to test process availability
function Test-Process {
    param(
        [string]$ProcessName,
        [string]$DisplayName
    )
    
    Write-Host "⚙️  Testing Process: $DisplayName" -ForegroundColor Yellow
    
    try {
        $process = Get-Process $ProcessName -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "✅ PASS: $DisplayName is running (PID: $($process.Id))" -ForegroundColor Green
            $script:passed++
            $script:tests += @{Name = "$DisplayName Process"; Status = "PASS"; PID = $process.Id }
            return $true
        }
        else {
            Write-Host "❌ FAIL: $DisplayName is not running" -ForegroundColor Red
            $script:failed++
            $script:tests += @{Name = "$DisplayName Process"; Status = "FAIL" }
            return $false
        }
    }
    catch {
        Write-Host "❌ FAIL: Cannot check process $ProcessName" -ForegroundColor Red
        $script:failed++
        $script:tests += @{Name = "$DisplayName Process"; Status = "FAIL"; Error = $_.Exception.Message }
        return $false
    }
}

# Start testing
Write-Host "🚀 Starting comprehensive connectivity tests..." -ForegroundColor Green
Write-Host ""

# Test 1: Port Availability
Write-Host "📡 Port Availability Tests" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

Test-Port "GeoLogix Backend" 8000
Test-Port "Web Interface" 3000
Test-Port "LM Studio" 1234
Test-Port "Ollama" 11434

# Test 2: Process Availability
Write-Host ""
Write-Host "⚙️  Process Availability Tests" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

Test-Process "python" "Python Backend"
Test-Process "LM Studio" "LM Studio AI"
Test-Process "ngrok" "Ngrok Tunnel"

# Test 3: Backend API Tests
Write-Host ""
Write-Host "🔌 Backend API Tests" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

Test-Service "Backend Health Check" "$BACKEND_URL/api/health"
Test-Service "Backend Stats" "$BACKEND_URL/api/stats"
Test-Service "Backend Search API" "$BACKEND_URL/api/search?query=test&limit=5"

# Test 4: AI Model Tests
Write-Host ""
Write-Host "🤖 AI Model Tests" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

Test-Service "LM Studio Models List" "$AI_MODEL_URL/v1/models"
Test-Service "LM Studio Chat API" "$AI_MODEL_URL/v1/chat/completions" "POST" '{"model": "llama-3.1-8b-instruct", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 10}' 15

# Test 5: Web Interface Tests
Write-Host ""
Write-Host "🌐 Web Interface Tests" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

Test-Service "Main UI Index" "$UI_URL/"
Test-Service "Main UI HTML" "$UI_URL/index.html"
Test-Service "Copilot UI" "$UI_URL/variant-6-copilot.html"
Test-Service "Main CSS" "$UI_URL/styles/main.css"
Test-Service "Variant CSS" "$UI_URL/styles/variant-6.css"
Test-Service "Shared Utils JS" "$UI_URL/scripts/shared-utils.js"
Test-Service "Variant JS" "$UI_URL/scripts/variant-6.js"

# Test 6: Integration Tests
Write-Host ""
Write-Host "🔗 Integration Tests" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Test backend-to-AI model connectivity
Write-Host "🧪 Testing: Backend to AI Model Integration" -ForegroundColor Yellow
try {
    $testBody = @{
        query   = "test query"
        limit   = 3
        sources = @("documents")
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/search" -Method POST -Body $testBody -ContentType "application/json" -TimeoutSec 15 -UseBasicParsing
    Write-Host "✅ PASS: Backend can communicate with AI model" -ForegroundColor Green
    $passed++
    $tests += @{Name = "Backend-AI Integration"; Status = "PASS" }
}
catch {
    Write-Host "❌ FAIL: Backend-AI integration failed" -ForegroundColor Red
    $failed++
    $tests += @{Name = "Backend-AI Integration"; Status = "FAIL"; Error = $_.Exception.Message }
}

# Test file system connectivity
Write-Host "🧪 Testing: File System Connectivity" -ForegroundColor Yellow
$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$requiredPaths = @(
    "$projectRoot\geologix-ai\UI\index.html",
    "$projectRoot\geologix-ai\geologix-backend\Core_System\server.py",
    "$projectRoot\Company_documents",
    "$projectRoot\emails"
)

$allFilesExist = $true
foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        Write-Host "❌ FAIL: Missing file/folder: $path" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-Host "✅ PASS: All required files and folders exist" -ForegroundColor Green
    $passed++
    $tests += @{Name = "File System"; Status = "PASS" }
}
else {
    $failed++
    $tests += @{Name = "File System"; Status = "FAIL" }
}

# Test 7: Performance Tests
Write-Host ""
Write-Host "⚡ Performance Tests" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Backend response time
Write-Host "🧪 Testing: Backend Response Time" -ForegroundColor Yellow
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/api/health" -UseBasicParsing -TimeoutSec 5
    $stopwatch.Stop()
    $responseTime = $stopwatch.ElapsedMilliseconds
    
    if ($responseTime -lt 2000) {
        Write-Host "✅ PASS: Backend response time ${responseTime}ms (< 2s)" -ForegroundColor Green
        $passed++
        $tests += @{Name = "Backend Performance"; Status = "PASS"; ResponseTime = $responseTime }
    }
    elseif ($responseTime -lt 5000) {
        Write-Host "⚠️  WARN: Backend response time ${responseTime}ms (< 5s)" -ForegroundColor Yellow
        $passed++
        $tests += @{Name = "Backend Performance"; Status = "WARN"; ResponseTime = $responseTime }
    }
    else {
        Write-Host "❌ FAIL: Backend response time ${responseTime}ms (> 5s)" -ForegroundColor Red
        $failed++
        $tests += @{Name = "Backend Performance"; Status = "FAIL"; ResponseTime = $responseTime }
    }
}
catch {
    Write-Host "❌ FAIL: Cannot measure backend performance" -ForegroundColor Red
    $failed++
    $tests += @{Name = "Backend Performance"; Status = "FAIL"; Error = $_.Exception.Message }
}

# Generate Summary Report
Write-Host ""
Write-Host "📊 Test Results Summary" -ForegroundColor White
Write-Host "======================" -ForegroundColor White
Write-Host ""

Write-Host "Total Tests: $($tests.Count)" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Success Rate: $([Math]::Round(($passed / $tests.Count) * 100, 1))%" -ForegroundColor $(if ($passed -eq $tests.Count) { 'Green' } elseif ($passed / $tests.Count -gt 0.8) { 'Yellow' } else { 'Red' })

# Detailed Results
Write-Host ""
Write-Host "📋 Detailed Results" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

foreach ($test in $tests) {
    $statusColor = switch ($test.Status) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "[$($test.Status)] $($test.Name)" -ForegroundColor $statusColor
    
    if ($test.Url) {
        Write-Host "   URL: $($test.Url)" -ForegroundColor Gray
    }
    if ($test.Port) {
        Write-Host "   Port: $($test.Port)" -ForegroundColor Gray
    }
    if ($test.PID) {
        Write-Host "   PID: $($test.PID)" -ForegroundColor Gray
    }
    if ($test.ResponseTime) {
        Write-Host "   Response Time: $($test.ResponseTime)ms" -ForegroundColor Gray
    }
    if ($test.Error) {
        Write-Host "   Error: $($test.Error)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Recommendations
Write-Host "💡 Recommendations" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

$failedTests = $tests | Where-Object { $_.Status -eq "FAIL" }
if ($failedTests) {
    Write-Host "❌ Issues Found:" -ForegroundColor Red
    foreach ($test in $failedTests) {
        Write-Host "   • $($test.Name): $($test.Error ?? "Service not responding")" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "🔧 Suggested Actions:" -ForegroundColor Yellow
    Write-Host "   1. Run '.\stop-all-services.ps1' to clean up" -ForegroundColor White
    Write-Host "   2. Run '.\start-all-services.ps1' to restart everything" -ForegroundColor White
    Write-Host "   3. Check individual service windows for error messages" -ForegroundColor White
}
else {
    Write-Host "🎉 All systems are operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ GeoLogix AI is ready for use" -ForegroundColor Green
    Write-Host "   • Main UI: $UI_URL/index.html" -ForegroundColor White
    Write-Host "   • Copilot UI: $UI_URL/variant-6-copilot.html" -ForegroundColor White
    Write-Host "   • Backend API: $BACKEND_URL" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
