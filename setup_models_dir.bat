@echo off
REM Setup Models Directory Structure at G:\

echo ================================================
echo   AlphaEdge AINV - Setup Models Directory
echo ================================================
echo.

REM Create directory structure
echo Creating directory structure at G:\AIModels\...
echo.

mkdir "G:\AIModels" 2>nul
mkdir "G:\AIModels\cache" 2>nul
mkdir "G:\AIModels\tensorrt_engines" 2>nul
mkdir "G:\AIModels\huggingface" 2>nul
mkdir "G:\AIModels\gguf" 2>nul
mkdir "G:\AIModels\downloads" 2>nul

echo [*] Created directories:
echo     G:\AIModels\
echo     ├── cache\              (model cache)
echo     ├── tensorrt_engines\   (TensorRT-LLM engines)
echo     ├── huggingface\        (HuggingFace models)
echo     ├── gguf\               (GGUF quantized models)
echo     └── downloads\          (temp downloads)
echo.

REM Create README
echo Creating README...
(
echo # AlphaEdge AINV - Models Directory
echo.
echo ## Directory Structure:
echo.
echo - **cache/**: Model cache and temporary files
echo - **tensorrt_engines/**: TensorRT-LLM optimized engines ^(2-10x faster^)
echo - **huggingface/**: HuggingFace format models
echo - **gguf/**: GGUF quantized models for local inference
echo - **downloads/**: Temporary download location
echo.
echo ## Estimated Sizes:
echo.
echo ### TensorRT Engines:
echo - Llama 3.1 8B:  ~6 GB
echo - Qwen 2.5 32B:  ~25 GB
echo - Llama 3.3 70B: ~45 GB
echo.
echo ### GGUF Models:
echo - Llama 3.1 8B Q4:  ~5 GB
echo - Mistral 7B Q4:   ~4 GB
echo - Qwen 32B Q5:     ~22 GB
echo - Llama 70B Q4:    ~40 GB
echo.
echo Total recommended space: 100-150 GB
) > "G:\AIModels\README.md"

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Models will be stored at: G:\AIModels\
echo.
echo Next steps:
echo   1. Run TensorRT-LLM installer to download models
echo   2. Models will auto-organize into correct folders
echo.

pause
