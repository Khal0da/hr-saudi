@echo off
echo ========================================
echo  Biometric Bridge - Windows Service Installer
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Run as Administrator
    pause
    exit /b 1
)

where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo NSSM not found. Download from: https://nssm.cc/download
    echo Place nssm.exe in this directory and run again.
    pause
    exit /b 1
)

nssm install BiometricBridge "%~dp0venv\Scripts\python.exe"
nssm set BiometricBridge AppDirectory "%~dp0"
nssm set BiometricBridge AppParameters "bridge.py"
nssm set BiometricBridge Description "ERPNext Biometric Attendance Bridge - ZKTeco"
nssm set BiometricBridge Start SERVICE_AUTO_START
nssm set BiometricBridge AppStdout "%~dp0logs\stdout.log"
nssm set BiometricBridge AppStderr "%~dp0logs\stderr.log"
nssm set BiometricBridge AppRotateFiles 1
nssm set BiometricBridge AppRotateOnline 1
nssm set BiometricBridge AppRotateSeconds 86400
nssm set BiometricBridge AppRotateBytes 1048576

if not exist "%~dp0logs" mkdir "%~dp0logs"

nssm start BiometricBridge

echo.
echo Service installed and started successfully!
echo Check logs in: %~dp0logs\
pause
