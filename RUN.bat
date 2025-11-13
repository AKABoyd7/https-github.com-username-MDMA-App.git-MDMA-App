@echo off
echo ============================================
echo AlphaEdge AINV - Auto Fixer and Launcher
echo ============================================
echo.

REM Find conda
set CONDA_PATH=
if exist "C:\Users\admin\miniconda3\Scripts\conda.exe" set CONDA_PATH=C:\Users\admin\miniconda3
if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" set CONDA_PATH=C:\ProgramData\miniconda3
if exist "C:\miniconda3\Scripts\conda.exe" set CONDA_PATH=C:\miniconda3
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" set CONDA_PATH=%USERPROFILE%\miniconda3

if "%CONDA_PATH%"=="" (
    echo ERROR: Conda not found
    echo Install from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo Found conda: %CONDA_PATH%
echo.

REM Activate environment
echo Activating alphaedge environment...
call "%CONDA_PATH%\Scripts\activate.bat" alphaedge

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo Python version: %PY_VER%

REM Check if gradio installed
python -c "import gradio" 2>nul
if errorlevel 1 (
    echo.
    echo Installing missing packages...
    pip install fastapi uvicorn gradio==4.44.0 chromadb==0.4.24 langchain langchain-community transformers sentence-transformers faster-whisper openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil --quiet
    echo Done.
)

REM Check torch
python -c "import torch" 2>nul
if errorlevel 1 (
    echo.
    echo Installing PyTorch...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    echo Done.
)

echo.
echo ============================================
echo   Starting AlphaEdge AINV...
echo ============================================
echo.

cd /d G:\AlphaEdge_AINV
python master_launcher.py --full

pause
