@echo off
title Driver Monitoring System Installer
color 0E

echo ============================================================
echo    Driver Drowsiness Detection System - Installer
echo ============================================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
python --version
echo.

echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

echo [4/5] Installing required packages...
pip install --upgrade pip
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.7
pip install numpy==1.24.3
pip install scipy==1.10.3
pip install pygame==2.5.2
pip install imutils==0.5.4
pip install pyttsx3==2.90
pip install pandas==2.0.3
pip install PyYAML==6.0
echo Packages installed
echo.

echo [5/5] Creating directories...
mkdir logs 2>nul
mkdir screenshots 2>nul
mkdir models 2>nul
mkdir datasets 2>nul
echo Directories created
echo.

echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo To run the system:
echo   1. Double-click run.bat
echo   2. OR run: python main.py
echo.
pause