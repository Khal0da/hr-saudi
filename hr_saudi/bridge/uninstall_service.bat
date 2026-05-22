@echo off
echo ========================================
echo  Biometric Bridge - Windows Service Uninstaller
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
    echo NSSM not found.
    pause
    exit /b 1
)

nssm stop BiometricBridge
nssm remove BiometricBridge confirm

echo.
echo Service removed successfully!
pause
