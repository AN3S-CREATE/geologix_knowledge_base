@echo off
title GeoLogix AI + Ngrok Launcher
color 0A

echo.
echo ============================================
echo    GeoLogix AI + Ngrok Launcher
echo ============================================
echo.

REM Check if Python is installed
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found!
        echo Please install Python from https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    ) else (
        echo [OK] Python detected (py launcher)
        set PYTHON_CMD=py
    )
) else (
    echo [OK] Python detected
    set PYTHON_CMD=python
)
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ngrok not found!
    echo Download from: https://ngrok.com/download
    echo.
    pause
    exit /b 1
)
echo [OK] ngrok detected
echo.

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [!] Ollama not running
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] Ollama detected
)

echo.
echo Starting GeoLogix AI with Ngrok...
echo.

REM Kill any existing processes on port 8000
echo Stopping any existing backend...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Killing process %%a
    taskkill /f /pid %%a >nul 2>&1
)

REM Start backend server
echo Starting backend server...
start "GeoLogix Backend" cmd /k "cd /d %~dp0geologix-backend && %PYTHON_CMD% -m uvicorn Core_System.server:app --host 0.0.0.0 --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
:wait
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo Still starting...
    goto wait
)
echo [OK] Backend started

REM Start ngrok
echo Starting ngrok tunnel...
start "GeoLogix Ngrok" cmd /k "ngrok http 8000 --domain=geologix.ngrok.io"

REM Wait for ngrok to start
echo Waiting for ngrok to start...
timeout /t 5 /nobreak >nul

REM Get the ngrok URL
echo Checking ngrok URL...
curl -s http://localhost:4040/api/tunnels >nul 2>&1
if errorlevel 1 (
    echo [!] Ngrok may still be starting...
) else (
    echo [OK] Ngrok tunnel active
)

echo.
echo ============================================
echo GeoLogix AI is ready with Ngrok!
echo ============================================
echo.
echo Local:    http://localhost:8000
echo Public:   https://geologix.ngrok.io
echo.
echo Backend and Ngrok are running in separate windows.
echo Close this window or press any key to exit.
echo.
pause
