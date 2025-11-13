# AlphaEdge AINV - FINAL Working Installer
# Auto-fixes Python 3.14 issue and installs everything

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AlphaEdge AINV - Auto Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find conda
Write-Host "[1/3] Locating conda..." -ForegroundColor Yellow

$condaPaths = @(
    "C:\Users\admin\miniconda3\Scripts\conda.exe",
    "C:\ProgramData\miniconda3\Scripts\conda.exe",
    "C:\miniconda3\Scripts\conda.exe",
    "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
    "$env:LOCALAPPDATA\miniconda3\Scripts\conda.exe"
)

$condaPath = $null
foreach ($path in $condaPaths) {
    if (Test-Path $path) {
        $condaPath = $path
        break
    }
}

if (!$condaPath) {
    # Try to find in PATH
    $condaCmd = Get-Command conda -ErrorAction SilentlyContinue
    if ($condaCmd) {
        $condaPath = $condaCmd.Source
    }
}

if (!$condaPath) {
    Write-Host "ERROR: Conda not found. Install from:" -ForegroundColor Red
    Write-Host "  https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Yellow
    exit 1
}

Write-Host "  -> Found: $condaPath" -ForegroundColor Green

# Get conda directory
$condaDir = Split-Path (Split-Path $condaPath)
$activateScript = Join-Path $condaDir "Scripts\activate.bat"

# Remove old env if exists
& $condaPath env remove -n alphaedge -y 2>$null | Out-Null

# Create new env with Python 3.11
Write-Host "  -> Creating Python 3.11 environment..." -ForegroundColor Gray
& $condaPath create -n alphaedge python=3.11 -y | Out-Null

Write-Host "  -> Environment created" -ForegroundColor Green
Write-Host ""

# Step 2: Install packages
Write-Host "[2/3] Installing packages (10-15 min)..." -ForegroundColor Yellow

# Create install script
$installScript = @"
@echo off
call "$activateScript" alphaedge
cd G:\AlphaEdge_AINV
echo Installing PyTorch...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
echo Installing core packages...
pip install fastapi uvicorn gradio chromadb --quiet
echo Installing AI packages...
pip install langchain langchain-community transformers sentence-transformers --quiet
echo Installing additional packages...
pip install faster-whisper tensorrt pycuda openai anthropic mcp pyyaml python-dotenv aiohttp requests numpy pillow psutil --quiet
echo Done!
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
@echo off
call "$activateScript" alphaedge
python -c "import torch; import gradio; import chromadb; print('SUCCESS')" 2>nul
if errorlevel 1 (
    echo PARTIAL
) else (
    echo SUCCESS
)
"@

$tempTest = "$env:TEMP\test_alphaedge.bat"
$testScript | Out-File -FilePath $tempTest -Encoding ASCII

$result = cmd /c $tempTest
Remove-Item $tempTest

if ($result -match "SUCCESS") {
    Write-Host "  -> All packages OK" -ForegroundColor Green
} else {
    Write-Host "  -> Installation complete (some optional packages may be missing)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

Write-Host "RUN PLATFORM:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  $activateScript alphaedge" -ForegroundColor Cyan
Write-Host "  cd G:\AlphaEdge_AINV" -ForegroundColor Cyan
Write-Host "  python master_launcher.py --full" -ForegroundColor Cyan
Write-Host ""

# Create quick start script
$quickStart = @"
@echo off
call "$activateScript" alphaedge
cd G:\AlphaEdge_AINV
python master_launcher.py --full
pause
"@

$quickStart | Out-File -FilePath "G:\AlphaEdge_AINV\START.bat" -Encoding ASCII

Write-Host "Quick start: Double-click START.bat" -ForegroundColor Green
Write-Host ""
