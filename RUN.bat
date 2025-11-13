@echo off
REM AlphaEdge AINV - Simple One-Click Launcher

echo ================================================
echo   AlphaEdge AINV
echo ================================================
echo.

cd /d "%~dp0"

REM Check Python 3.11
set PY311=C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PY311%" (
    echo Python 3.11 not found. Download from:
    echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    pause
    exit /b 1
)

REM First run - setup environment
if not exist "venv311" (
    echo [1/3] Creating environment...
    %PY311% -m venv venv311
    call venv311\Scripts\activate.bat

    echo [2/3] Installing PyTorch...
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu121

    echo [3/3] Installing packages...
    pip install --no-cache-dir fastapi uvicorn gradio chromadb langchain langchain-community transformers sentence-transformers faster-whisper tensorrt pycuda openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil

    echo.
    echo Setup complete!
    echo.
)

REM Run platform
call venv311\Scripts\activate.bat
echo Starting platform...
echo.
python master_launcher.py --full

pause
