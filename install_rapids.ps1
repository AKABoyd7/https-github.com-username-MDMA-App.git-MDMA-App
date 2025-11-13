# AlphaEdge AINV - RAPIDS Auto Installer (PowerShell)
# รันสคริปต์นี้ใน PowerShell เพื่อติดตั้ง RAPIDS อัตโนมัติใน WSL2

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AlphaEdge AINV - RAPIDS Auto Installer" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ตรวจสอบ WSL2
Write-Host "[0/2] ตรวจสอบ WSL2..." -ForegroundColor Yellow
try {
    $wslVersion = wsl --list --verbose
    if ($LASTEXITCODE -ne 0) {
        throw "WSL2 not installed"
    }
    Write-Host "  -> WSL2 พร้อมใช้งาน" -ForegroundColor Green
} catch {
    Write-Host "  -> ❌ WSL2 ไม่พร้อมใช้งาน" -ForegroundColor Red
    Write-Host "     ติดตั้ง WSL2: wsl --install -d Ubuntu-24.04" -ForegroundColor Yellow
    exit 1
}

# Copy script ไปใน WSL2
Write-Host ""
Write-Host "[1/2] Copy script ไปใน WSL2..." -ForegroundColor Yellow
wsl cp /mnt/g/AlphaEdge_AINV/install_rapids.sh /tmp/install_rapids.sh
wsl chmod +x /tmp/install_rapids.sh
Write-Host "  -> Copy สำเร็จ" -ForegroundColor Green

# รัน installation script ใน WSL2
Write-Host ""
Write-Host "[2/2] เริ่มติดตั้ง RAPIDS ใน WSL2..." -ForegroundColor Yellow
Write-Host "  -> รอ 15-25 นาที..." -ForegroundColor Yellow
Write-Host ""

wsl bash /tmp/install_rapids.sh

# เสร็จสิ้น
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ เสร็จสิ้น!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ใช้งาน RAPIDS:" -ForegroundColor Yellow
Write-Host "  wsl" -ForegroundColor White
Write-Host "  cd /mnt/g/AlphaEdge_AINV" -ForegroundColor White
Write-Host "  source ~/.bashrc" -ForegroundColor White
Write-Host "  conda activate rapids" -ForegroundColor White
Write-Host ""
