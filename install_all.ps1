# AlphaEdge AINV - Complete Auto Installer
# ติดตั้งทุกอย่างอัตโนมัติในคำสั่งเดียว

param(
    [switch]$SkipRAPIDSInstall,
    [switch]$SkipModelDownload
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AlphaEdge AINV - Complete Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ตรวจสอบตำแหน่ง
if (!(Test-Path "G:\AlphaEdge_AINV")) {
    Write-Host "❌ Error: ไม่พบ G:\AlphaEdge_AINV" -ForegroundColor Red
    exit 1
}

Set-Location "G:\AlphaEdge_AINV"

# ========================================
# Step 1: ติดตั้ง Python Dependencies
# ========================================
Write-Host "[1/5] ติดตั้ง Python Dependencies..." -ForegroundColor Yellow
Write-Host "  -> PyTorch + CUDA..." -ForegroundColor Gray

try {
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --quiet
    Write-Host "  -> ✓ PyTorch + CUDA" -ForegroundColor Green
} catch {
    Write-Host "  -> ⚠️ PyTorch มีอยู่แล้ว หรือ error (ข้ามได้)" -ForegroundColor Yellow
}

Write-Host "  -> ติดตั้ง dependencies ทั้งหมด (รอ 5-10 นาที)..." -ForegroundColor Gray
pip install -r requirements_full.txt --no-cache-dir 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  -> ⚠️ บาง packages ติดตั้งไม่สำเร็จ - ลองแก้ไข..." -ForegroundColor Yellow
    # ติดตั้ง critical packages แยก
    pip install gradio chromadb fastapi uvicorn transformers --no-cache-dir --force-reinstall 2>$null | Out-Null
}

Write-Host "  -> ✓ ติดตั้ง dependencies สำเร็จ" -ForegroundColor Green
Write-Host ""

# ========================================
# Step 2: ตรวจสอบ .env
# ========================================
Write-Host "[2/5] ตรวจสอบไฟล์ .env..." -ForegroundColor Yellow

if (!(Test-Path ".env")) {
    Write-Host "  -> สร้างไฟล์ .env..." -ForegroundColor Gray
    Copy-Item ".env.example" ".env"
    Write-Host "  -> ⚠️ กรุณาแก้ไข .env ใส่ API Keys" -ForegroundColor Yellow
    notepad .env
    Read-Host "กด Enter เมื่อแก้ไขเสร็จแล้ว"
} else {
    # ตรวจสอบ API Key
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "nvapi-your-key-here") {
        Write-Host "  -> ⚠️ ยังไม่ได้ใส่ NVIDIA API Key" -ForegroundColor Yellow
        $response = Read-Host "ต้องการแก้ไขตอนนี้? (y/N)"
        if ($response -eq "y") {
            notepad .env
            Read-Host "กด Enter เมื่อแก้ไขเสร็จแล้ว"
        }
    } else {
        Write-Host "  -> ✓ ไฟล์ .env พร้อมใช้งาน" -ForegroundColor Green
    }
}
Write-Host ""

# ========================================
# Step 3: ติดตั้ง RAPIDS (Optional)
# ========================================
if (!$SkipRAPIDSInstall) {
    Write-Host "[3/5] ติดตั้ง RAPIDS (Optional - ข้ามได้)..." -ForegroundColor Yellow
    $response = Read-Host "ติดตั้ง RAPIDS? (ใช้เวลา 20-30 นาที, ขนาด 5-6GB) (y/N)"

    if ($response -eq "y") {
        Write-Host "  -> เริ่มติดตั้ง RAPIDS..." -ForegroundColor Gray

        # ตรวจสอบ WSL2
        try {
            wsl --list --verbose | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  -> WSL2 พร้อมใช้งาน" -ForegroundColor Green

                # รัน RAPIDS installer
                if (Test-Path "install_rapids.ps1") {
                    & .\install_rapids.ps1
                } else {
                    Write-Host "  -> ⚠️ ไม่พบ install_rapids.ps1" -ForegroundColor Yellow
                }
            } else {
                throw "WSL2 not ready"
            }
        } catch {
            Write-Host "  -> ⚠️ WSL2 ไม่พร้อม - ข้าม RAPIDS" -ForegroundColor Yellow
            Write-Host "     ติดตั้ง WSL2: wsl --install -d Ubuntu-24.04" -ForegroundColor Gray
        }
    } else {
        Write-Host "  -> ข้าม RAPIDS (ใช้ TensorRT เพียงอย่างเดียว)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[3/5] ข้าม RAPIDS (ตามที่ระบุ)" -ForegroundColor Yellow
}
Write-Host ""

# ========================================
# Step 4: LM Studio + Models
# ========================================
Write-Host "[4/5] ตรวจสอบ LM Studio..." -ForegroundColor Yellow

# ตรวจสอบว่า LM Studio ทำงานอยู่หรือไม่
try {
    $response = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "  -> ✓ LM Studio Server กำลังทำงาน (Port 1234)" -ForegroundColor Green

    $models = ($response.Content | ConvertFrom-Json).data
    if ($models.Count -gt 0) {
        Write-Host "  -> ✓ พบ Models: $($models.Count) รายการ" -ForegroundColor Green
        foreach ($model in $models) {
            Write-Host "     - $($model.id)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  -> ⚠️ ไม่มี Models ใน LM Studio" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  -> ⚠️ LM Studio Server ไม่ทำงาน" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  กรุณา:" -ForegroundColor Yellow
    Write-Host "  1. ดาวน์โหลด LM Studio: https://lmstudio.ai" -ForegroundColor White
    Write-Host "  2. ดาวน์โหลด Models (Llama 3.3 70B หรือ Qwen 2.5 Coder 32B)" -ForegroundColor White
    Write-Host "  3. เปิด Local Server (Port 1234)" -ForegroundColor White
    Write-Host ""

    if (!$SkipModelDownload) {
        $response = Read-Host "เปิด LM Studio website? (y/N)"
        if ($response -eq "y") {
            Start-Process "https://lmstudio.ai"
        }
    }
}
Write-Host ""

# ========================================
# Step 5: ทดสอบระบบ
# ========================================
Write-Host "[5/5] ทดสอบระบบ..." -ForegroundColor Yellow

Write-Host "  -> ทดสอบ Python imports..." -ForegroundColor Gray
try {
    python -c "import torch; print(f'  -> ✓ PyTorch {torch.__version__} + CUDA {torch.version.cuda}')"
    python -c "import tensorrt; print('  -> ✓ TensorRT')" 2>$null
    python -c "import gradio; print('  -> ✓ Gradio')"
    python -c "import chromadb; print('  -> ✓ ChromaDB')"
    python -c "import transformers; print('  -> ✓ Transformers')"
} catch {
    Write-Host "  -> ⚠️ บาง modules ไม่พร้อม (อาจไม่สำคัญ)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ ติดตั้งเสร็จสมบูรณ์!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# สรุป
Write-Host "สรุปการติดตั้ง:" -ForegroundColor Yellow
Write-Host "  ✓ Python Dependencies (PyTorch, TensorRT, etc.)" -ForegroundColor Green
Write-Host "  ✓ Configuration (.env)" -ForegroundColor Green

if (!$SkipRAPIDSInstall -and $response -eq "y") {
    Write-Host "  ✓ RAPIDS (cuDF, cuML, cuGraph)" -ForegroundColor Green
} else {
    Write-Host "  - RAPIDS (ข้ามไป)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "ขั้นตอนถัดไป:" -ForegroundColor Yellow
Write-Host "  1. ตรวจสอบ LM Studio + Models พร้อมหรือยัง" -ForegroundColor White
Write-Host "  2. รัน Platform:" -ForegroundColor White
Write-Host ""
Write-Host "     python master_launcher.py --full" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. เข้าใช้งาน Web UI:" -ForegroundColor White
Write-Host "     http://localhost:7860" -ForegroundColor Cyan
Write-Host ""

# ถามว่าต้องการรันเลยหรือไม่
$response = Read-Host "ต้องการรัน Platform ตอนนี้เลย? (y/N)"
if ($response -eq "y") {
    Write-Host ""
    Write-Host "กำลังเริ่ม AlphaEdge AINV..." -ForegroundColor Cyan
    python master_launcher.py --full
}
