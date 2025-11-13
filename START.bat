@echo off
REM AlphaEdge AINV - Auto Installer & Launcher
REM Run this ONE file after cloning - it does everything

echo ================================================
echo   AlphaEdge AINV - Automatic Setup
echo ================================================
echo.

REM Step 1: Check if Python 3.11 exists
set PYTHON311=C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe
set PYTHON_CMD=

if exist "%PYTHON311%" (
    echo [1/4] Found Python 3.11
    set PYTHON_CMD=%PYTHON311%
) else (
    echo [1/4] Python 3.11 not found
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo.
    echo After installing, run this script again.
    pause
    exit /b 1
)

cd /d %~dp0

REM Step 2: Create virtual environment
echo [2/4] Creating virtual environment...
if not exist "venv311" (
    %PYTHON_CMD% -m venv venv311
)
call venv311\Scripts\activate.bat

REM Step 3: Install packages
echo [3/4] Installing packages (10-15 min)...
python -m pip install --upgrade pip --quiet
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
pip install fastapi uvicorn gradio chromadb langchain langchain-community transformers sentence-transformers faster-whisper tensorrt pycuda openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil --quiet

REM Step 4: Launch platform
echo [4/4] Starting platform...
echo.
echo ================================================
echo   Platform Starting...
echo ================================================
echo.
echo   Web UI:  http://localhost:7860
echo   API:     http://localhost:8000
echo.

python master_launcher.py --full

pause
