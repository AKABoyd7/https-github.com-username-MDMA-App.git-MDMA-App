# Project Jareth v1 - PowerShell Launcher
# ================================================

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 58 -NoNewline -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host "  🚀 Launching Project Jareth v1 [Local Mode]" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 58 -NoNewline -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "📁 Working Directory: $ScriptDir" -ForegroundColor Yellow
Write-Host ""

# Check Python installation
Write-Host "🐍 Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Check if virtual environment exists
$venvPath = Join-Path $ScriptDir "venv"
if (Test-Path $venvPath) {
    Write-Host "🔧 Virtual environment found" -ForegroundColor Cyan
    Write-Host "   Activating..." -ForegroundColor Yellow
    & "$venvPath\Scripts\Activate.ps1"
    Write-Host "   ✅ Activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "   ✅ Created" -ForegroundColor Green
    Write-Host "   Activating..." -ForegroundColor Yellow
    & "$venvPath\Scripts\Activate.ps1"
    Write-Host "   ✅ Activated" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
}
Write-Host ""

# GPU Detection
Write-Host "🎮 GPU Detection..." -ForegroundColor Cyan
python -c @"
import torch
import sys
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    print(f'   ✅ GPU Detected: {gpu_name}')
    print(f'   ✅ CUDA Version: {torch.version.cuda}')
else:
    print('   ⚠️  No GPU detected - Running on CPU')
    print('   ℹ️  Install CUDA-enabled PyTorch for GPU support')
"@
Write-Host ""

# Check Ollama
Write-Host "🤖 Checking Ollama..." -ForegroundColor Cyan
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   ✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Ollama not detected" -ForegroundColor Yellow
    Write-Host "   ℹ️  Make sure Ollama is running: https://ollama.ai" -ForegroundColor Gray
    Write-Host "   ℹ️  Required model: llama3-3-70b or llama3" -ForegroundColor Gray
}
Write-Host ""

# Start the application
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 58 -NoNewline -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host "  🌐 Starting API Server..." -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 58 -NoNewline -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 API Documentation: http://localhost:8500/docs" -ForegroundColor Cyan
Write-Host "💚 Health Check:     http://localhost:8500/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run the main application
python main.py
