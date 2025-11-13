#!/bin/bash
# AlphaEdge AINV - RAPIDS Auto Installer
# สำหรับ WSL2 Ubuntu - ติดตั้งทุกอย่างอัตโนมัติ

set -e  # Exit on error

echo "=========================================="
echo "AlphaEdge AINV - RAPIDS Auto Installer"
echo "=========================================="

# ตำแหน่งติดตั้ง
INSTALL_DIR="/mnt/g/AlphaEdge_AINV"
MINICONDA_DIR="${INSTALL_DIR}/miniconda3"

cd ${INSTALL_DIR}

# ขั้นที่ 1: ดาวน์โหลด Miniconda
echo ""
echo "[1/5] ดาวน์โหลด Miniconda..."
if [ ! -f "Miniconda3-latest-Linux-x86_64.sh" ]; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
else
    echo "  -> มีไฟล์อยู่แล้ว ข้ามการดาวน์โหลด"
fi

# ขั้นที่ 2: ติดตั้ง Miniconda
echo ""
echo "[2/5] ติดตั้ง Miniconda ใน ${MINICONDA_DIR}..."
if [ ! -d "${MINICONDA_DIR}" ]; then
    bash Miniconda3-latest-Linux-x86_64.sh -b -p ${MINICONDA_DIR}
    echo "  -> ติดตั้งสำเร็จ"
else
    echo "  -> มี Miniconda อยู่แล้ว ข้ามการติดตั้ง"
fi

# ขั้นที่ 3: เปิดใช้งาน conda
echo ""
echo "[3/5] เปิดใช้งาน conda..."
${MINICONDA_DIR}/bin/conda init bash
source ~/.bashrc

# ขั้นที่ 4: Accept Terms of Service
echo ""
echo "[4/5] Accept conda Terms of Service..."
${MINICONDA_DIR}/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main || true
${MINICONDA_DIR}/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r || true

# ขั้นที่ 5: สร้าง environment + ติดตั้ง RAPIDS
echo ""
echo "[5/5] สร้าง environment + ติดตั้ง RAPIDS..."
echo "  -> รอ 15-25 นาที (ดาวน์โหลด ~3-4GB)"

# ตรวจสอบว่ามี environment อยู่แล้วหรือไม่
if ${MINICONDA_DIR}/bin/conda env list | grep -q "^rapids "; then
    echo "  -> Environment 'rapids' มีอยู่แล้ว"
    read -p "ต้องการลบและติดตั้งใหม่? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${MINICONDA_DIR}/bin/conda env remove -n rapids -y
        echo "  -> ลบ environment เดิมแล้ว"
    else
        echo "  -> ข้ามการติดตั้ง RAPIDS"
        exit 0
    fi
fi

# สร้าง environment
${MINICONDA_DIR}/bin/conda create -n rapids python=3.11 -y

# ติดตั้ง RAPIDS
echo ""
echo "กำลังติดตั้ง RAPIDS..."
${MINICONDA_DIR}/bin/conda install -n rapids \
    -c rapidsai -c conda-forge -c nvidia \
    rapids=24.10 python=3.11 cuda-version=12.1 -y

# ทดสอบ
echo ""
echo "=========================================="
echo "ทดสอบ RAPIDS..."
${MINICONDA_DIR}/bin/conda run -n rapids python -c "import cudf; print('✓ cuDF OK')"
${MINICONDA_DIR}/bin/conda run -n rapids python -c "import cuml; print('✓ cuML OK')"
${MINICONDA_DIR}/bin/conda run -n rapids python -c "import cugraph; print('✓ cuGraph OK')"

echo ""
echo "=========================================="
echo "✅ ติดตั้งสำเร็จ!"
echo "=========================================="
echo ""
echo "Activate environment:"
echo "  conda activate rapids"
echo ""
echo "ตำแหน่งติดตั้ง:"
echo "  ${MINICONDA_DIR}"
echo ""
