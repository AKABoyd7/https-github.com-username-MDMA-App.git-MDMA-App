@echo off
REM AlphaEdge AINV - Complete Auto-Install Toolkit

echo ================================================
echo   AlphaEdge AINV - Auto Install Toolkit
echo ================================================
echo.

cd /d "%~dp0"

REM Check Python 3.11
set PY311=C:\Users\admin\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PY311%" (
    echo [ERROR] Python 3.11 not found!
    echo.
    echo Download and install from:
    echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [*] Found Python 3.11: %PY311%
echo.

REM Always recreate venv to ensure clean install
if exist "venv311" (
    echo [*] Removing old environment...
    rmdir /s /q venv311
)

echo [1/4] Creating fresh Python environment...
%PY311% -m venv venv311
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

call venv311\Scripts\activate.bat

echo [2/4] Upgrading pip...
python -m pip install --upgrade pip --no-cache-dir

echo [3/4] Installing PyTorch with CUDA 12.1...
pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
if errorlevel 1 (
    echo [ERROR] PyTorch installation failed
    pause
    exit /b 1
)

echo [4/4] Installing all dependencies...
pip install --no-cache-dir fastapi uvicorn[standard] gradio chromadb langchain langchain-community transformers sentence-transformers faster-whisper openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil
if errorlevel 1 (
    echo [ERROR] Dependency installation failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo Starting AlphaEdge AINV platform...
echo.

python master_launcher.py --full

pause
