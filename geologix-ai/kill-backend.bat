@echo off
title Kill GeoLogix Backend
color 0C

echo.
echo ============================================
echo    Killing GeoLogix Backend Processes
echo ============================================
echo.

REM Kill processes on port 8000
echo Checking for processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Found process %%a on port 8000 - killing...
    taskkill /f /pid %%a >nul 2>&1
)

REM Also kill python processes that might be uvicorn
echo Checking for uvicorn processes...
tasklist | find "python" >nul 2>&1
if not errorlevel 1 (
    echo Killing python processes...
    taskkill /f /im python.exe >nul 2>&1
)

echo.
echo [OK] Processes killed
echo.
echo You can now restart GeoLogix AI
echo.
pause
