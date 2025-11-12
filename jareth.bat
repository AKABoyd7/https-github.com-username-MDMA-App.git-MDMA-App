@echo off
REM Jareth AINV CLI Launcher for Windows
REM ใช้งาน: jareth.bat <command>

cd /d "%~dp0"
"%~dp0venv\Scripts\python.exe" "%~dp0jareth_cli.py" %*
