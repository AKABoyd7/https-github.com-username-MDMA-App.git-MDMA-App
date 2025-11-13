@echo off
REM AlphaEdge AINV - Quick Start (ไม่ reinstall)

echo ================================================
echo   AlphaEdge AINV - Quick Start
echo ================================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv311" (
    echo [ERROR] venv311 not found!
    echo Please run RUN.bat first to install.
    pause
    exit /b 1
)

REM Activate and start
call venv311\Scripts\activate.bat

echo Starting AlphaEdge AINV platform...
echo.

python master_launcher.py --full

pause
