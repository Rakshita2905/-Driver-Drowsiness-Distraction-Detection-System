@echo off
title Driver Monitoring System Uninstaller
color 0C

echo ============================================================
echo    Driver Drowsiness Detection System - Uninstaller
echo ============================================================
echo.
echo WARNING: This will remove all project data!
echo.

set /p confirm="Are you sure? (y/n): "
if /i not "%confirm%"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b
)

echo.
echo Removing virtual environment...
if exist venv (
    rmdir /s /q venv
    echo Virtual environment removed
)

echo Removing logs...
if exist logs (
    rmdir /s /q logs
    echo Logs removed
)

echo Removing screenshots...
if exist screenshots (
    rmdir /s /q screenshots
    echo Screenshots removed
)

echo Removing Python cache...
del /s /q *.pyc 2>nul
rmdir /s /q __pycache__ 2>nul

echo.
echo ============================================================
echo Uninstall Complete!
echo ============================================================
pause