@echo off
REM AlphaEdge AINV - Scan Local Models
REM Scans G:\Models_Organized for GGUF files and generates config

echo ================================================================================
echo AlphaEdge AINV - Model Scanner
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist "venv311\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run RUN.bat first to create the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/2] Activating Python environment...
call venv311\Scripts\activate.bat

REM Run scanner
echo [2/2] Scanning models...
echo.
python scan_models.py

echo.
echo ================================================================================
echo Scan complete! Check local_models_config.json for results.
echo ================================================================================
echo.
pause
