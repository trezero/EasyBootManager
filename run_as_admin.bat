@echo off
REM PyBootManager - Run as Administrator Helper Script

echo Starting PyBootManager...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Run the application with administrator privileges
powershell -Command "Start-Process python -ArgumentList '%~dp0pybootmanager.py' -Verb RunAs"

exit /b 0
