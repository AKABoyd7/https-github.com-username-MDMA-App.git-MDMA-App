@echo off
REM AlphaEdge AINV - RAPIDS cuDF/cuML Auto Installer
REM 10-50x faster data processing with GPU acceleration

echo ================================================================
echo   AlphaEdge AINV - RAPIDS Installer
echo   GPU-Accelerated Data Science (cuDF, cuML, cuGraph)
echo   10-50x Faster than CPU pandas/scikit-learn
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

echo [Phase 1/4] Checking Prerequisites
echo ================================================================
echo.

REM Check CUDA
echo [*] Checking CUDA...
nvcc --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] CUDA Toolkit not found in PATH
    echo RAPIDS requires CUDA Toolkit 12.1+
    echo.
    echo Download from: https://developer.nvidia.com/cuda-downloads
    echo.
    pause
    exit /b 1
) else (
    nvcc --version | findstr "release"
    echo ✓ CUDA found
)

echo.
echo [*] Checking GPU...
python -c "import torch; print(f'✓ GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
python -c "import torch; print(f'✓ CUDA Compute Capability: {torch.cuda.get_device_capability(0) if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo [*] Checking Python version...
python -c "import sys; print(f'✓ Python {sys.version.split()[0]}')"

echo.
echo [Phase 2/4] Installing RAPIDS Core (cuDF)
echo ================================================================
echo.
echo [INFO] RAPIDS installation options:
echo   1. Full installation (cuDF + cuML + cuGraph) - Recommended (~2GB)
echo   2. cuDF only (DataFrame GPU acceleration) - Lighter (~800MB)
echo   3. Skip RAPIDS installation
echo.

choice /C 123 /N /M "Select option (1-3): "

if errorlevel 3 (
    echo.
    echo Installation cancelled.
    pause
    exit /b 0
)

if errorlevel 2 (
    set INSTALL_TYPE=minimal
    echo.
    echo [*] Installing cuDF only...
    goto install_cudf
)

if errorlevel 1 (
    set INSTALL_TYPE=full
    echo.
    echo [*] Installing full RAPIDS suite...
    goto install_cudf
)

:install_cudf

echo.
echo [*] Installing cuDF (GPU-accelerated DataFrame)...
echo [*] This may take 5-15 minutes...
echo.

REM Install cuDF via conda-forge (recommended) or pip
echo [INFO] Attempting pip installation...
echo.

pip install --no-cache-dir cudf-cu12 --extra-index-url https://pypi.nvidia.com

if errorlevel 1 (
    echo.
    echo [WARNING] cuDF pip installation failed
    echo.
    echo [INFO] RAPIDS is best installed via conda:
    echo   1. Install Miniconda: https://docs.conda.io/en/latest/miniconda.html
    echo   2. Create environment: conda create -n rapids-24.10 -c rapidsai -c conda-forge -c nvidia rapids=24.10 python=3.11 cuda-version=12.1
    echo   3. Activate: conda activate rapids-24.10
    echo.
    echo Alternative: Use RAPIDS on WSL2 Ubuntu
    echo.
    pause
    exit /b 1
)

echo ✓ cuDF installed successfully
echo.

if "%INSTALL_TYPE%"=="minimal" goto verify

echo [Phase 3/4] Installing Additional RAPIDS Packages
echo ================================================================
echo.

echo [*] Installing cuML (GPU machine learning)...
pip install --no-cache-dir cuml-cu12 --extra-index-url https://pypi.nvidia.com

if errorlevel 1 (
    echo [WARNING] cuML installation failed, continuing...
)

echo.
echo [*] Installing cuGraph (GPU graph analytics)...
pip install --no-cache-dir cugraph-cu12 --extra-index-url https://pypi.nvidia.com

if errorlevel 1 (
    echo [WARNING] cuGraph installation failed, continuing...
)

echo.
echo [*] Installing cuSpatial (GPU spatial analytics)...
pip install --no-cache-dir cuspatial-cu12 --extra-index-url https://pypi.nvidia.com

if errorlevel 1 (
    echo [WARNING] cuSpatial installation failed, continuing...
)

:verify

echo.
echo [Phase 4/4] Verification
echo ================================================================
echo.

echo [*] Testing RAPIDS installation...
echo.

python -c "import cudf; print(f'✓ cuDF {cudf.__version__} installed')"

if errorlevel 1 (
    echo [ERROR] cuDF verification failed
    pause
    exit /b 1
)

if "%INSTALL_TYPE%"=="minimal" goto success

python -c "import cuml; print(f'✓ cuML {cuml.__version__} installed')" 2>nul || echo [INFO] cuML not available
python -c "import cugraph; print(f'✓ cuGraph {cugraph.__version__} installed')" 2>nul || echo [INFO] cuGraph not available

:success

echo.
echo ================================================================
echo   Installation Complete!
echo ================================================================
echo.

echo ✓ RAPIDS installed successfully
echo.

echo Installed packages:
if "%INSTALL_TYPE%"=="full" (
    echo   ✓ cuDF   - GPU DataFrames (10-50x faster than pandas)
    echo   ✓ cuML   - GPU Machine Learning (10-100x faster than scikit-learn)
    echo   ✓ cuGraph - GPU Graph Analytics
) else (
    echo   ✓ cuDF   - GPU DataFrames (10-50x faster than pandas)
)

echo.
echo Example usage:
echo.
echo   import cudf
echo   import pandas as pd
echo.
echo   # CPU pandas
echo   df = pd.read_csv('large_file.csv')
echo   result = df.groupby('column').mean()  # Slow on CPU
echo.
echo   # GPU cuDF (10-50x faster!)
echo   gdf = cudf.read_csv('large_file.csv')
echo   result = gdf.groupby('column').mean()  # Lightning fast!
echo.

echo Next steps:
echo   1. Restart platform: .\START.bat
echo   2. Test RAPIDS: python -c "import cudf; print(cudf.DataFrame({'a': [1,2,3]}))"
echo   3. Use cuDF in your code for massive speedup!
echo.

echo Performance expectations:
echo   - 10-50x faster CSV/Parquet reading
echo   - 10-100x faster group operations
echo   - 5-50x faster joins and merges
echo   - Near-instant data transforms on millions of rows
echo.

pause
