@echo off
setlocal enabledelayedexpansion
title AGRO-VATORS Smart Farming Rover Server
color 0B

:: 1. Select Python Interpreter
if exist "venv\Scripts\python.exe" (
    set PYTHON_EXEC=venv\Scripts\python.exe
) else (
    set PYTHON_EXEC=python
)

:: 2. Detect Local IP Address
set LOCAL_IP=127.0.0.1
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" /c:"IP Address"') do (
    for /f "tokens=1 delims= " %%b in ("%%a") do (
        set LOCAL_IP=%%b
    )
)

echo =====================================================================
echo                AGRO-VATORS SMART FARMING ROVER
echo                AI Pathology & Rover Control Hub
echo =====================================================================
echo.
echo   Local Dashboard   : http://localhost:5001
echo   Poco F1 Mobile App: http://!LOCAL_IP!:5001
echo.
echo   WiFi Hotspot Name : phone1
echo   Hotspot Password  : 12345678
echo.
echo =====================================================================
echo Starting Flask Server with Central Camera Worker + YOLOv8 AI...
echo (Opening dashboard in your web browser...)
echo.

:: Open browser after a brief delay
start "" http://localhost:5001

:: Run main server
%PYTHON_EXEC% app.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Server exited with an error.
    echo If this is your first time, please run install.bat first!
    echo.
    pause
)

