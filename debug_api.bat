@echo off
REM Debug API Server
cd /d "%~dp0"
call venv311\Scripts\activate.bat
echo Starting API Server with error output...
python api_server.py
pause
