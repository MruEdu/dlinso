@echo off
REM Run in PowerShell:  .\test_upstage.bat   (not: test_upstage.bat)
REM Or use:  .\test.ps1  /  .\test_upstage.ps1  /  double-click this file
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo  dlinso v2 - Upstage Solar API Test
echo ========================================
echo  Checks UPSTAGE_API_KEY in .env
echo ========================================
echo.

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

"%PY%" scripts\test_upstage_connection.py
set "EXITCODE=%ERRORLEVEL%"

echo.
if "%EXITCODE%"=="0" (
    echo [OK] Test passed.
) else (
    echo [FAIL] Exit code: %EXITCODE%
    echo  - Check UPSTAGE_API_KEY in .env
    echo  - Billing: https://console.upstage.ai/billing
)
echo.
pause
exit /b %EXITCODE%
