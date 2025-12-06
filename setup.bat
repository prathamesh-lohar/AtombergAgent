@echo off
echo ========================================
echo Atomberg Agent - Installation Script
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv .venv

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo IMPORTANT: Before running the agent:
echo 1. Create a .env file with your API key:
echo    api=YOUR_GOOGLE_API_KEY_HERE
echo.
echo 2. Make sure Google Chrome is installed
echo.
echo To run the agent:
echo    .venv\Scripts\activate
echo    python agent.py
echo.
pause