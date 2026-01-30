@echo off
title GeoLogix AI One-Click Installer
color 0B

echo.
echo ============================================
echo    GeoLogix AI - One-Click Installer
echo    Version 2.0 - Full Auto Setup
echo ============================================
echo.

REM Check Python
echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set pyver=%%i
echo [OK] %pyver%

REM Install dependencies
echo.
echo [2/7] Installing Python dependencies...
if exist "%~dp0geologix-backend\Configuration\requirements.txt" (
    python -m pip install -r "%~dp0geologix-backend\Configuration\requirements.txt" --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [!] Some packages failed, installing core packages...
        python -m pip install fastapi uvicorn pydantic requests python-multipart httpx psutil aiofiles --quiet --disable-pip-version-check
    )
) else (
    echo [!] requirements.txt not found, installing core packages...
    python -m pip install fastapi uvicorn pydantic requests python-multipart httpx psutil aiofiles --quiet --disable-pip-version-check
)
echo [OK] Dependencies installed

REM Verify modules
echo.
echo [3/7] Verifying modules...
python -c "import fastapi, uvicorn, pydantic, requests, psutil" >nul 2>&1
if errorlevel 1 (
    echo [X] Module verification failed
    pause
    exit /b 1
)
echo [OK] All modules verified

REM Setup Ollama
echo.
echo [4/7] Setting up Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [!] Ollama not running
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
    
    REM Check again
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo [!] Could not start Ollama
        echo Download from: https://ollama.ai
        echo.
        echo Continue anyway? (y/n)
        set /p continue=
        if /i not "%continue%"=="y" goto :skip_ollama
    )
    
    REM Check for models
    echo Checking for models...
    curl -s http://localhost:11434/api/tags | find "llama3.2:1b" >nul
    if errorlevel 1 (
        echo Downloading llama3.2:1b model (1.3GB)...
        ollama pull llama3.2:1b
        echo [OK] Model downloaded
    ) else (
        echo [OK] llama3.2:1b model found
    )
    
    REM Update config
    if exist "%~dp0geologix-backend\Configuration\config.py" (
        echo Updating config...
        powershell -Command "(Get-Content '%~dp0geologix-backend\Configuration\config.py') -replace 'OLLAMA_MODEL = \".*\"', 'OLLAMA_MODEL = \"llama3.2:1b\"' | Set-Content '%~dp0geologix-backend\Configuration\config.py'"
        echo [OK] Config updated
    )
)

:skip_ollama

REM Verify files
echo.
echo [5/7] Verifying files...
if exist "%~dp0geologix-backend\Core_System\server.py" echo [OK] Backend server
if exist "%~dp0geologix-backend\Core_System\knowledge_engine.py" echo [OK] Knowledge engine
if exist "%~dp0UI\variant-6-copilot.html" echo [OK] Copilot UI
if exist "%~dp0UI\index.html" echo [OK] Landing page

REM Start backend
echo.
echo [6/7] Starting backend...
start "GeoLogix Backend" cmd /k "cd /d %~dp0geologix-backend && python -m uvicorn Core_System.server:app --host 0.0.0.0 --port 8000"

REM Wait for backend
echo Waiting for backend...
:wait_backend
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo Still starting...
    goto wait_backend
)
echo [OK] Backend started

REM Test system
echo.
echo [7/7] Testing system...
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo [X] Health check failed
) else (
    echo [OK] API health check passed
)

REM Launch
echo.
echo ============================================
echo    GeoLogix AI is READY!
echo ============================================
echo.
echo Opening in browser...
start http://localhost:8000

echo.
echo Press any key to exit...
pause
