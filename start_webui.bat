@echo off
REM Start Web UI Only
cd /d "%~dp0"

call venv\Scripts\activate.bat
python web_ui.py

pause
