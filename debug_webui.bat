@echo off
REM Debug Web UI
cd /d "%~dp0"
call venv311\Scripts\activate.bat
echo Starting Web UI with error output...
python web_ui.py
pause
