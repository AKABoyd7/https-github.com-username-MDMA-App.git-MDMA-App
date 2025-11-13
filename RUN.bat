@echo off
echo ================================================
echo   AlphaEdge AINV - One-Click Launcher
echo ================================================
echo.

cd /d %~dp0

REM Find Python 3.11
set PY311=C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PY311%" (
    echo ERROR: Python 3.11 not found
    echo.
    echo Download: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo Install it, then run this again.
    pause
    exit /b 1
)

REM Create venv if needed
if not exist "venv311" (
    echo Creating environment...
    %PY311% -m venv venv311
    call venv311\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
    pip install fastapi uvicorn gradio chromadb langchain langchain-community transformers sentence-transformers faster-whisper tensorrt pycuda openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil
)

REM Activate and run
call venv311\Scripts\activate.bat
python master_launcher.py --full

pause
