@echo off
REM Jareth2 Daemon Service Manager
REM Copyright (c) 2025 AlphaEdge AINV

cd /d "%~dp0"

if "%1"=="" goto usage
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="status" goto status
if "%1"=="task" goto task
goto usage

:start
echo Starting Jareth2 Daemon...
start "Jareth2 Daemon" /MIN "%~dp0venv\Scripts\python.exe" "%~dp0jareth2_daemon.py" start
timeout /t 2 >nul
goto status

:stop
echo Stopping Jareth2 Daemon...
"%~dp0venv\Scripts\python.exe" "%~dp0jareth2_daemon.py" stop
goto end

:status
"%~dp0venv\Scripts\python.exe" "%~dp0jareth2_daemon.py" status
goto end

:task
if "%2"=="" (
    echo Error: Goal required
    echo Usage: jareth2_service.bat task "Your goal here"
    goto end
)
echo Adding task...
"%~dp0venv\Scripts\python.exe" "%~dp0jareth2_daemon.py" add-task --goal "%~2"
goto end

:usage
echo.
echo Jareth2 Daemon Service Manager
echo ===============================
echo.
echo Usage:
echo   jareth2_service.bat start              - Start daemon
echo   jareth2_service.bat stop               - Stop daemon
echo   jareth2_service.bat status             - Check status
echo   jareth2_service.bat task "goal"        - Add task
echo.
echo Examples:
echo   jareth2_service.bat start
echo   jareth2_service.bat task "Optimize system for gaming"
echo   jareth2_service.bat status
echo.

:end
