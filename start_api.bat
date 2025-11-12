@echo off
REM Start API Server Only
cd /d "%~dp0"

call venv\Scripts\activate.bat
python api_server.py

pause
