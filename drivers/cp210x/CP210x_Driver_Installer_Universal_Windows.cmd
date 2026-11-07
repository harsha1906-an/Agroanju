@echo off
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator Privileges...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs"
    exit /b
)
echo This installer is supported on x86, x64, ARM32 and ARM64 systems.
cd /d "%~dp0"
echo Installing CP210x Driver...
pnputil /add-driver silabser.inf /install
pause