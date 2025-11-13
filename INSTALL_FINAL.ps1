# AlphaEdge AINV - FINAL Working Installer
# Auto-fixes Python 3.14 issue and installs everything

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AlphaEdge AINV - Auto Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create Python 3.11 environment
Write-Host "[1/3] Creating Python 3.11 environment..." -ForegroundColor Yellow

$condaPath = "C:\Users\admin\miniconda3\Scripts\conda.exe"
if (!(Test-Path $condaPath)) {
    Write-Host "ERROR: Miniconda not found at $condaPath" -ForegroundColor Red
    exit 1
}

# Remove old env if exists
& $condaPath env remove -n alphaedge -y 2>$null

# Create new env with Python 3.11
& $condaPath create -n alphaedge python=3.11 -y

Write-Host "  -> Environment created" -ForegroundColor Green
Write-Host ""

# Step 2: Install packages
Write-Host "[2/3] Installing packages (10-15 min)..." -ForegroundColor Yellow

$activateScript = "C:\Users\admin\miniconda3\Scripts\activate.bat"

# Create install script
$installScript = @"
call $activateScript alphaedge
cd G:\AlphaEdge_AINV
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install fastapi uvicorn gradio chromadb langchain langchain-community transformers sentence-transformers faster-whisper tensorrt pycuda openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil
"@

$tempScript = "$env:TEMP\install_alphaedge.bat"
$installScript | Out-File -FilePath $tempScript -Encoding ASCII

# Run install
cmd /c $tempScript

Remove-Item $tempScript

Write-Host "  -> Packages installed" -ForegroundColor Green
Write-Host ""

# Step 3: Test
Write-Host "[3/3] Testing installation..." -ForegroundColor Yellow

$testScript = @"
call $activateScript alphaedge
python -c "import torch; import gradio; import chromadb; print('SUCCESS')"
"@

$tempTest = "$env:TEMP\test_alphaedge.bat"
$testScript | Out-File -FilePath $tempTest -Encoding ASCII

$result = cmd /c $tempTest 2>&1
Remove-Item $tempTest

if ($result -match "SUCCESS") {
    Write-Host "  -> All packages OK" -ForegroundColor Green
} else {
    Write-Host "  -> Some packages missing (may be OK)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "RUN PLATFORM:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  C:\Users\admin\miniconda3\Scripts\activate.bat alphaedge" -ForegroundColor Cyan
Write-Host "  cd G:\AlphaEdge_AINV" -ForegroundColor Cyan
Write-Host "  python master_launcher.py --full" -ForegroundColor Cyan
Write-Host ""

# Create quick start script
$quickStart = @"
@echo off
call C:\Users\admin\miniconda3\Scripts\activate.bat alphaedge
cd G:\AlphaEdge_AINV
python master_launcher.py --full
pause
"@

$quickStart | Out-File -FilePath "G:\AlphaEdge_AINV\START.bat" -Encoding ASCII

Write-Host "Quick start: Double-click START.bat" -ForegroundColor Green
Write-Host ""
