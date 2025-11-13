@echo off
REM AlphaEdge AINV - Test Local GGUF Models
REM Tests all local models from G:\Models_Organized

echo ================================================================
echo   AlphaEdge AINV - Local Model Tester
echo   Testing GGUF models from G:\Models_Organized
echo ================================================================
echo.

cd /d "%~dp0"

REM Activate Python environment
if not exist "venv311" (
    echo [ERROR] venv311 not found!
    echo Please run RUN.bat first to create environment
    pause
    exit /b 1
)

call venv311\Scripts\activate.bat

echo [1/3] Checking dependencies...
echo.

REM Check if llama-cpp-python is installed
python -c "import llama_cpp" 2>nul
if errorlevel 1 (
    echo [*] Installing llama-cpp-python with CUDA support...
    echo [*] This may take 5-10 minutes...
    echo.
    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install llama-cpp-python
        echo.
        echo Try manual installation:
        echo   pip install llama-cpp-python --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
        echo.
        pause
        exit /b 1
    )
)

echo ✓ Dependencies ready
echo.

echo [2/3] Scanning local models...
echo.

python gguf_model_loader.py

echo.
echo [3/3] Test Options
echo ================================================================
echo.
echo Choose a model to test:
echo.
echo   Code Models:
echo     1. Qwen3-Next-80B (Flagship - Best overall!)
echo     2. Qwen3-Coder
echo     3. Qwen2.5-Coder
echo     4. DeepSeek-Coder
echo     5. Codestral
echo.
echo   General Models:
echo     6. Llama 3.2
echo     7. Llama 3.1
echo     8. Mistral Nemo
echo     9. Mistral
echo    10. WizardLM2
echo.
echo    11. Quick test all models
echo    12. Skip testing
echo.

choice /C 123456789ABC /N /M "Select option (1-12): "

if errorlevel 12 (
    echo.
    echo Testing cancelled.
    pause
    exit /b 0
)

if errorlevel 11 (
    echo.
    echo [*] Testing all models with quick prompts...
    echo.

    python -c "
from gguf_model_loader import GGUFModelLoader
import logging
logging.basicConfig(level=logging.INFO)

loader = GGUFModelLoader()
models = loader.list_available_models()

print('\n' + '='*80)
print('Quick Test Results:')
print('='*80 + '\n')

for model_id in models[:5]:  # Test first 5 models
    print(f'Testing {model_id}...')
    try:
        response = loader.generate(model_id, 'Say hello in one sentence.', max_tokens=50)
        print(f'  ✓ {model_id}: Working!')
        print(f'  Response: {response[:100]}...\n')
        loader.unload_model(model_id)  # Free memory
    except Exception as e:
        print(f'  ✗ {model_id}: Failed - {e}\n')

print('='*80)
"
    goto end
)

REM Map choice to model ID
set MODEL_ID=
if errorlevel 10 set MODEL_ID=wizardlm2-local
if errorlevel 9 set MODEL_ID=mistral-local
if errorlevel 8 set MODEL_ID=mistral-nemo-local
if errorlevel 7 set MODEL_ID=llama3.1-local
if errorlevel 6 set MODEL_ID=llama3.2-local
if errorlevel 5 set MODEL_ID=codestral-local
if errorlevel 4 set MODEL_ID=deepseek-coder-local
if errorlevel 3 set MODEL_ID=qwen2.5-coder-local
if errorlevel 2 set MODEL_ID=qwen3-coder-local
if errorlevel 1 set MODEL_ID=qwen3-next-80b-local

echo.
echo Testing model: %MODEL_ID%
echo.

REM Interactive test
python -c "
from gguf_model_loader import GGUFModelLoader
import logging
logging.basicConfig(level=logging.INFO)

loader = GGUFModelLoader()
model_id = '%MODEL_ID%'

print('='*80)
print(f'Model: {model_id}')
print('='*80)
print()

# Get model info
info = loader.get_model_info(model_id)
if info:
    print(f'Path: {info[\"path\"]}')
    print(f'GGUF File: {info[\"gguf_file\"]}')
    print(f'Size: {info[\"size_gb\"]} GB')
    print(f'Context: {info[\"context_length\"]} tokens')
    print()

# Test generation
print('Testing generation...')
print()

test_prompt = 'Write a Python function to calculate fibonacci numbers.'

print(f'Prompt: {test_prompt}')
print()
print('Response:')
print('-'*80)

response = loader.generate(model_id, test_prompt, max_tokens=200)
print(response)

print('-'*80)
print()
print('✓ Test complete!')
"

:end

echo.
echo ================================================================
echo   Testing Complete!
echo ================================================================
echo.

echo Next steps:
echo   1. Run platform: .\START.bat
echo   2. Models will be auto-loaded on first use
echo   3. TensorRT engines will be built for 2-10x speedup
echo.

pause
