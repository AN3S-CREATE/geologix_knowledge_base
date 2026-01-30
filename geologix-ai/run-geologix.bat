@echo off
title GeoLogix AI Launcher
color 0A

echo.
echo ============================================
echo    GeoLogix AI - Quick Launcher
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
echo Starting GeoLogix AI...
echo.

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

echo [OK] Backend is running!
echo.
echo Opening GeoLogix AI in browser...
start http://localhost:8000

echo.
echo ============================================
echo GeoLogix AI is ready!
echo ============================================
echo.
echo Backend is running in a separate window.
echo Close this window or press any key to exit.
echo.
pause
