@echo off
setlocal enabledelayedexpansion
title AGRO-VATORS - Setup & Installation Wizard
color 0A

echo =====================================================================
echo           AGRO-VATORS SMART ROVER - AUTOMATED INSTALLER
echo =====================================================================
echo.

:: 1. Detect Python
echo [1/5] Checking Python installation...
set PYTHON_CMD=

where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    color 0C
    echo.
    echo [ERROR] Python was NOT found on this system!
    echo.
    echo Please install Python 3.10, 3.11, or 3.12:
    echo 1. Download from: https://www.python.org/downloads/
    echo 2. IMPORTANT: Check the box "Add Python to PATH" during install!
    echo 3. After installing, run this install.bat again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do echo    Found: %%v

:: 2. Set up Virtual Environment
echo.
echo [2/5] Setting up dedicated Python Virtual Environment (.venv)...
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [WARNING] Failed to create venv. Proceeding with system Python...
        set VENV_PYTHON=%PYTHON_CMD%
    ) else (
        echo    Virtual environment created successfully.
        set VENV_PYTHON=venv\Scripts\python.exe
    )
) else (
    echo    Existing virtual environment found in .\venv.
    set VENV_PYTHON=venv\Scripts\python.exe
)

:: 3. Upgrade pip and install dependencies
echo.
echo [3/5] Installing required dependencies (Torch, YOLOv8, OpenCV, Flask)...
echo    This may take 2-4 minutes depending on your internet connection...
%VENV_PYTHON% -m pip install --upgrade pip
%VENV_PYTHON% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Failed to install dependencies from requirements.txt!
    echo Please check your internet connection and try running install.bat again.
    echo.
    pause
    exit /b 1
)
echo    Dependencies installed successfully!

:: 4. Verify Configuration (.env)
echo.
echo [4/5] Checking configuration (.env)...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo    Created .env configuration file from template.
    ) else (
        echo PORT=5001 > .env
        echo ESP32_MAIN_IP=192.168.93.164 >> .env
        echo ESP32_CAM_IP=192.168.93.28 >> .env
        echo    Generated default .env configuration file.
    )
) else (
    echo    .env configuration file is present.
)

:: 5. Verify YOLOv8 AI Model
echo.
echo [5/5] Verifying YOLOv8 AI Model...
if exist "models\yolov8n.pt" (
    echo    YOLOv8 nano model found at models\yolov8n.pt!
) else (
    echo    Downloading YOLOv8 nano model...
    %VENV_PYTHON% -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); import shutil, os; os.makedirs('models', exist_ok=True); shutil.move('yolov8n.pt', 'models/yolov8n.pt')"
    if exist "models\yolov8n.pt" (
        echo    YOLOv8 model downloaded and saved to models\yolov8n.pt!
    ) else (
        echo    [NOTICE] Model will download automatically on first run.
    )
)

:: CP2102 Driver prompt
if exist "drivers\CP210xVCPInstaller_x64.exe" (
    echo.
    echo ---------------------------------------------------------------------
    echo Optional: CP2102 USB-to-UART Driver for ESP32 COM Port
    echo If you plan to connect the ESP32 via USB cable to this laptop:
    set /p INSTALL_DRIVER="Would you like to install the USB Driver now? (Y/N, default N): "
    if /i "!INSTALL_DRIVER!"=="Y" (
        echo Launching CP2102 driver installer...
        start "" "drivers\CP210xVCPInstaller_x64.exe"
    )
)

color 0A
echo.
echo =====================================================================
echo                INSTALLATION COMPLETED SUCCESSFULLY!
echo =====================================================================
echo.
echo To start the rover dashboard anytime, simply double-click:
echo.
echo                   start_rover.bat
echo.
echo The dashboard will automatically launch at http://localhost:5001
echo and show your Poco F1 mobile connection URL.
echo.
echo =====================================================================
pause

