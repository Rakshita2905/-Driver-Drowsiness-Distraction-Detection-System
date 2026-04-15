@echo off
title Driver Drowsiness Detection System
color 0A

echo ============================================================
echo    Driver Drowsiness & Distraction Detection System
echo ============================================================
echo.

echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing requirements...
pip install -r requirements.txt

echo [INFO] Running tests...
python test_system.py

echo.
echo [INFO] Starting main system...
python main.py

pause