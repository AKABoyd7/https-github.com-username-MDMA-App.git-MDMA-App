@echo off
echo =======================================
echo   TensorRT-LLM Smart Installation
echo =======================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo [1/5] Checking CUDA...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: NVIDIA GPU or CUDA not detected
    echo TensorRT-LLM requires NVIDIA GPU with CUDA
    pause
)

echo [2/5] Installing Python dependencies...
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate sentencepiece
pip install langchain langgraph langchain-community
pip install nvidia-ml-py

echo.
echo [3/5] Installing TensorRT-LLM...
echo Note: This may take 10-30 minutes
pip install tensorrt-llm --extra-index-url https://pypi.nvidia.com

if %errorlevel% neq 0 (
    echo WARNING: TensorRT-LLM installation failed
    echo You can still use Ollama backend
    echo.
)

echo [4/5] Creating model cache directory...
if not exist "tensorrt_models" mkdir tensorrt_models

echo [5/5] Testing installation...
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

echo.
echo =======================================
echo   Installation Complete!
echo =======================================
echo.
echo Next steps:
echo 1. Run: python agent_tensorrt.py
echo 2. Or: .\START.bat
echo.
pause
