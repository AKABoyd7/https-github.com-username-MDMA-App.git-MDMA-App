@echo off
REM AlphaEdge AINV - Platform Launcher
REM Copyright (c) 2025 AlphaEdge AINV

cd /d "%~dp0"

echo.
echo ========================================
echo  AlphaEdge AINV - Enterprise Platform
echo  Copyright (c) 2025 AlphaEdge AINV
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Activate venv and run master launcher
call venv\Scripts\activate.bat

python master_launcher.py --full

pause
