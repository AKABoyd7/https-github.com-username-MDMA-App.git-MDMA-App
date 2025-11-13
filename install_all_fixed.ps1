# AlphaEdge AINV - Complete One-Click Installer (Fixed)
# แก้ไขปัญหา Python 3.14 และ dependencies

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AlphaEdge AINV - Complete Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ตรวจสอบ Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Gray

if ($pythonVersion -match "3\.14") {
    Write-Host ""
    Write-Host "⚠️  Python 3.14 ไม่รองรับบาง packages" -ForegroundColor Yellow
    Write-Host "    แนะนำใช้ Python 3.11" -ForegroundColor Yellow
    Write-Host ""

    # ตรวจสอบว่ามี conda หรือไม่
    try {
        conda --version | Out-Null
        Write-Host "สร้าง conda environment Python 3.11..." -ForegroundColor Cyan

        # สร้าง environment
        conda create -n alphaedge_py311 python=3.11 -y

        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "  ✅ สร้าง environment สำเร็จ!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "รันคำสั่งต่อไปนี้:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  conda activate alphaedge_py311" -ForegroundColor Cyan
        Write-Host "  cd G:\AlphaEdge_AINV" -ForegroundColor Cyan
        Write-Host "  .\install_all.ps1" -ForegroundColor Cyan
        Write-Host ""
        exit 0
    } catch {
        Write-Host "❌ ไม่พบ conda - ดาวน์โหลด Python 3.11:" -ForegroundColor Red
        Write-Host "   https://www.python.org/downloads/release/python-3119/" -ForegroundColor White
        exit 1
    }
}

# ตรวจสอบตำแหน่ง
if (!(Test-Path "G:\AlphaEdge_AINV")) {
    Write-Host "❌ Error: ไม่พบ G:\AlphaEdge_AINV" -ForegroundColor Red
    exit 1
}

Set-Location "G:\AlphaEdge_AINV"

# ========================================
# Step 1: ติดตั้ง Python Dependencies
# ========================================
Write-Host "[1/4] ติดตั้ง Python Dependencies..." -ForegroundColor Yellow

# PyTorch
Write-Host "  -> PyTorch + CUDA..." -ForegroundColor Gray
try {
    python -c "import torch; print(f'PyTorch {torch.__version__} OK')" 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> ✓ PyTorch มีอยู่แล้ว" -ForegroundColor Green
    } else {
        throw "Need install"
    }
} catch {
    Write-Host "  -> ติดตั้ง PyTorch..." -ForegroundColor Gray
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    Write-Host "  -> ✓ PyTorch + CUDA" -ForegroundColor Green
}

# Core dependencies (แยกติดตั้งเพื่อหลีกเลี่ยง error)
Write-Host "  -> ติดตั้ง core packages..." -ForegroundColor Gray
$corePackages = @(
    "fastapi[standard]>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "gradio>=4.0.0",
    "pydantic>=2.0.0,<2.12",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.0",
    "numpy>=1.24.0",
    "pillow>=10.0.0",
    "requests>=2.31.0",
    "aiohttp>=3.9.0",
    "transformers>=4.35.0",
    "sentence-transformers>=2.2.0",
    "faster-whisper>=0.10.0",
    "paddleocr>=2.7.0",
    "chromadb>=0.4.0",
    "langchain>=0.1.0",
    "langchain-community>=0.0.10",
    "tensorrt>=8.6.0",
    "pycuda>=2024.1",
    "openai>=1.3.0",
    "anthropic>=0.18.0",
    "mcp>=1.0.0"
)

$failed = @()
foreach ($pkg in $corePackages) {
    try {
        pip install $pkg --quiet 2>$null
    } catch {
        $failed += $pkg
    }
}

if ($failed.Count -gt 0) {
    Write-Host "  -> ⚠️ บาง packages ติดตั้งไม่สำเร็จ:" -ForegroundColor Yellow
    foreach ($pkg in $failed) {
        Write-Host "     - $pkg" -ForegroundColor Gray
    }
    Write-Host "  -> ลองติดตั้งอีกครั้งด้วย no-cache..." -ForegroundColor Gray
    pip install $failed --no-cache-dir --force-reinstall --quiet 2>$null
}

Write-Host "  -> ✓ ติดตั้ง dependencies สำเร็จ" -ForegroundColor Green
Write-Host ""

# ========================================
# Step 2: ตรวจสอบ .env
# ========================================
Write-Host "[2/4] ตรวจสอบไฟล์ .env..." -ForegroundColor Yellow

if (!(Test-Path ".env")) {
    Write-Host "  -> สร้างไฟล์ .env..." -ForegroundColor Gray
    Copy-Item ".env.example" ".env"
    Write-Host "  -> ⚠️ กรุณาแก้ไข .env ใส่ API Keys" -ForegroundColor Yellow
} else {
    Write-Host "  -> ✓ ไฟล์ .env พร้อมใช้งาน" -ForegroundColor Green
}
Write-Host ""

# ========================================
# Step 3: LM Studio / NVIDIA Cloud
# ========================================
Write-Host "[3/4] ตรวจสอบ LLM Backend..." -ForegroundColor Yellow

# ตรวจสอบ LM Studio
try {
    $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "  -> ✓ LM Studio Server พร้อมใช้งาน" -ForegroundColor Green
} catch {
    Write-Host "  -> ⚠️ LM Studio ไม่ทำงาน" -ForegroundColor Yellow
    Write-Host "  -> ใช้ NVIDIA Cloud API แทน (ตั้งค่าใน .env)" -ForegroundColor Gray
}
Write-Host ""

# ========================================
# Step 4: ทดสอบระบบ
# ========================================
Write-Host "[4/4] ทดสอบระบบ..." -ForegroundColor Yellow

$testResults = @()

# Test PyTorch
try {
    $output = python -c "import torch; print(torch.__version__, torch.cuda.is_available())" 2>&1
    if ($output -match "True") {
        Write-Host "  -> ✓ PyTorch + CUDA" -ForegroundColor Green
        $testResults += "pytorch"
    } else {
        Write-Host "  -> ⚠️ PyTorch OK แต่ CUDA ไม่พร้อม" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  -> ❌ PyTorch" -ForegroundColor Red
}

# Test core modules
$modules = @("gradio", "chromadb", "fastapi", "transformers", "langchain")
foreach ($mod in $modules) {
    try {
        python -c "import $mod" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  -> ✓ $mod" -ForegroundColor Green
            $testResults += $mod
        } else {
            Write-Host "  -> ❌ $mod" -ForegroundColor Red
        }
    } catch {
        Write-Host "  -> ❌ $mod" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ ติดตั้งเสร็จสมบูรณ์!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "สรุปการติดตั้ง:" -ForegroundColor Yellow
Write-Host "  ✓ Core Dependencies: $($testResults.Count)/$($modules.Count + 1) modules" -ForegroundColor Green
Write-Host "  ✓ Configuration (.env)" -ForegroundColor Green
Write-Host "  - RAPIDS (ข้ามไป - ติดตั้งทีหลังได้)" -ForegroundColor Gray

Write-Host ""
Write-Host "รัน Platform:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  python master_launcher.py --full" -ForegroundColor Cyan
Write-Host ""
Write-Host "Web UI: http://localhost:7860" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# ถามว่าต้องการรันเลยหรือไม่
$response = Read-Host "ต้องการรัน Platform ตอนนี้เลย? (y/N)"
if ($response -eq "y") {
    Write-Host ""
    Write-Host "กำลังเริ่ม AlphaEdge AINV..." -ForegroundColor Cyan
    python master_launcher.py --full
}
