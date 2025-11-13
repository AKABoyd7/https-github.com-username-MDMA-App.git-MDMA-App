# AlphaEdge AINV - TensorRT-LLM Installer
# ติดตั้ง TensorRT-LLM สำหรับ inference เร็วสุด (2-10x faster)

param(
    [string]$ModelPath = "",
    [int]$TensorParallel = 1,
    [string]$ModelType = "llama"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  TensorRT-LLM Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ========================================
# Step 1: ตรวจสอบ Python & CUDA
# ========================================
Write-Host "[1/5] ตรวจสอบ Python & CUDA..." -ForegroundColor Yellow

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "  -> Python: $pythonVersion" -ForegroundColor Gray

if ($pythonVersion -match "3\.14") {
    Write-Host "  -> ⚠️ Python 3.14 อาจมีปัญหา - แนะนำ 3.10 หรือ 3.11" -ForegroundColor Yellow
}

# Check CUDA
try {
    $cudaVersion = python -c "import torch; print(torch.version.cuda)" 2>&1
    Write-Host "  -> CUDA: $cudaVersion" -ForegroundColor Gray

    if ($cudaVersion -notmatch "12") {
        Write-Host "  -> ⚠️ TensorRT-LLM ต้องการ CUDA 12.x" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  -> ❌ ไม่พบ PyTorch/CUDA" -ForegroundColor Red
    Write-Host "     รันก่อน: pip install torch --index-url https://download.pytorch.org/whl/cu121" -ForegroundColor Yellow
    exit 1
}

Write-Host "  -> ✓ Python & CUDA พร้อม" -ForegroundColor Green
Write-Host ""

# ========================================
# Step 2: ติดตั้ง TensorRT-LLM
# ========================================
Write-Host "[2/5] ติดตั้ง TensorRT-LLM..." -ForegroundColor Yellow
Write-Host "  -> ดาวน์โหลด + compile (รอ 10-20 นาที)..." -ForegroundColor Gray

try {
    # ติดตั้ง TensorRT-LLM
    pip install tensorrt_llm -U --extra-index-url https://pypi.nvidia.com --quiet

    Write-Host "  -> ✓ TensorRT-LLM ติดตั้งสำเร็จ" -ForegroundColor Green
} catch {
    Write-Host "  -> ❌ ติดตั้งไม่สำเร็จ" -ForegroundColor Red
    Write-Host "     ลองใช้ Docker:" -ForegroundColor Yellow
    Write-Host "     docker pull nvcr.io/nvidia/tensorrt_llm:24.10-py3" -ForegroundColor White
    exit 1
}

Write-Host ""

# ========================================
# Step 3: สร้างโฟลเดอร์สำหรับ engines
# ========================================
Write-Host "[3/5] สร้างโฟลเดอร์..." -ForegroundColor Yellow

$engineDir = "G:\AlphaEdge_AINV\trt_engines"
if (!(Test-Path $engineDir)) {
    New-Item -ItemType Directory -Path $engineDir -Force | Out-Null
    Write-Host "  -> ✓ สร้าง $engineDir" -ForegroundColor Green
} else {
    Write-Host "  -> ✓ $engineDir มีอยู่แล้ว" -ForegroundColor Green
}

Write-Host ""

# ========================================
# Step 4: แนะนำการ convert model
# ========================================
Write-Host "[4/5] การ Convert Models..." -ForegroundColor Yellow
Write-Host ""

Write-Host "TensorRT-LLM ต้อง convert model ก่อนใช้งาน:" -ForegroundColor White
Write-Host ""

Write-Host "1. ดาวน์โหลด Model (Hugging Face):" -ForegroundColor Cyan
Write-Host "   git lfs install" -ForegroundColor White
Write-Host "   git clone https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct" -ForegroundColor White
Write-Host ""

Write-Host "2. Convert เป็น TensorRT Engine:" -ForegroundColor Cyan
Write-Host "   # Llama 8B (1 GPU)" -ForegroundColor Gray
Write-Host "   trtllm-build --checkpoint_dir Llama-3.1-8B-Instruct \" -ForegroundColor White
Write-Host "                --output_dir $engineDir\llama8b \" -ForegroundColor White
Write-Host "                --gemm_plugin float16 \" -ForegroundColor White
Write-Host "                --max_batch_size 8" -ForegroundColor White
Write-Host ""

Write-Host "   # Llama 70B (Multi-GPU - ถ้ามี 2+ GPUs)" -ForegroundColor Gray
Write-Host "   trtllm-build --checkpoint_dir Llama-3.1-70B-Instruct \" -ForegroundColor White
Write-Host "                --output_dir $engineDir\llama70b \" -ForegroundColor White
Write-Host "                --gemm_plugin float16 \" -ForegroundColor White
Write-Host "                --tp_size 2 \" -ForegroundColor White
Write-Host "                --max_batch_size 4" -ForegroundColor White
Write-Host ""

Write-Host "3. รัน TensorRT-LLM Server:" -ForegroundColor Cyan
Write-Host "   python -m tensorrt_llm.hlapi.llm_api \" -ForegroundColor White
Write-Host "          --engine_dir $engineDir\llama8b \" -ForegroundColor White
Write-Host "          --port 8000 \" -ForegroundColor White
Write-Host "          --host 0.0.0.0" -ForegroundColor White
Write-Host ""

# ========================================
# Step 5: อัพเดท .env
# ========================================
Write-Host "[5/5] อัพเดท Configuration..." -ForegroundColor Yellow

$envPath = "G:\AlphaEdge_AINV\.env"

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw

    # เช็คว่ามี TensorRT-LLM config หรือยัง
    if ($envContent -notmatch "USE_TENSORRT_LLM") {
        # เพิ่ม config
        $newConfig = @"

# ============================================
# TensorRT-LLM Configuration
# ============================================

USE_TENSORRT_LLM=true
TENSORRT_LLM_URL=http://localhost:8000
TENSORRT_ENGINE_PATH=$engineDir/llama8b
TENSORRT_MAX_BATCH_SIZE=8
"@
        Add-Content -Path $envPath -Value $newConfig
        Write-Host "  -> ✓ เพิ่ม TensorRT-LLM config ใน .env" -ForegroundColor Green
    } else {
        Write-Host "  -> ✓ .env มี TensorRT-LLM config อยู่แล้ว" -ForegroundColor Green
    }
} else {
    Write-Host "  -> ⚠️ ไม่พบไฟล์ .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ ติดตั้ง TensorRT-LLM สำเร็จ!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "ขั้นตอนถัดไป:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. ดาวน์โหลด Model จาก Hugging Face" -ForegroundColor White
Write-Host "2. Convert เป็น TensorRT Engine (ใช้คำสั่งด้านบน)" -ForegroundColor White
Write-Host "3. รัน TensorRT-LLM Server" -ForegroundColor White
Write-Host "4. รัน AlphaEdge AINV:" -ForegroundColor White
Write-Host ""
Write-Host "   python master_launcher.py --full" -ForegroundColor Cyan
Write-Host ""

Write-Host "Performance:" -ForegroundColor Yellow
Write-Host "  - TensorRT-LLM: 2-10x เร็วกว่า LM Studio" -ForegroundColor Green
Write-Host "  - Latency: ต่ำกว่า 50%" -ForegroundColor Green
Write-Host "  - VRAM: ประหยัดกว่า 30-40%" -ForegroundColor Green
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  https://nvidia.github.io/TensorRT-LLM/" -ForegroundColor Cyan
Write-Host ""
