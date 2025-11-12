# 📦 Installation Guide - AlphaEdge AINV Enterprise Platform

**คู่มือติดตั้งแบบ Step-by-Step**

Copyright © 2025 AlphaEdge AINV

---

## 📋 สิ่งที่ต้องเตรียม

### ✅ ความต้องการระบบ (System Requirements)

#### Hardware (ฮาร์ดแวร์):
- **CPU:** Intel/AMD 4+ cores (แนะนำ 8+ cores)
- **RAM:** 16GB ขึ้นไป (แนะนำ 32GB+)
- **GPU:** NVIDIA RTX 3060 ขึ้นไป (12GB+ VRAM)
  - แนะนำ: RTX 3090/4090, A100, H100
- **Storage:** 50GB+ พื้นที่ว่าง (แนะนำ SSD)

#### Software (ซอฟต์แวร์):
- **OS:** Windows 10/11 Pro หรือ Windows Server 2019+
- **Python:** 3.10 หรือ 3.11 (ห้ามใช้ 3.12+)
- **CUDA:** 11.8+ หรือ 12.x
- **Git:** ล่าสุด
- **7-Zip:** สำหรับ backup (optional)

---

## 🔧 ขั้นตอนที่ 1: ติดตั้ง Python

### A. ตรวจสอบ Python ที่มีอยู่

```powershell
# เปิด PowerShell
python --version
```

**ถ้าได้ผลลพธ์:** `Python 3.10.x` หรือ `Python 3.11.x` → ข้ามไปขั้นตอนที่ 2
**ถ้าไม่มี Python หรือเวอร์ชันผิด:** → ติดตั้งใหม่

### B. ติดตั้ง Python 3.11

```powershell
# ดาวน์โหลด Python 3.11.9
# ไปที่: https://www.python.org/downloads/release/python-3119/

# เลือก: Windows installer (64-bit)
# ไฟล์: python-3.11.9-amd64.exe

# ขณะติดตั้ง:
# ✅ เลือก "Add Python to PATH"
# ✅ เลือก "Install for all users"
# ✅ Customize installation
#    ✅ pip
#    ✅ tcl/tk and IDLE
#    ✅ Python test suite
#    ✅ py launcher
```

### C. ยืนยันการติดตั้ง

```powershell
# เปิด PowerShell ใหม่
python --version
# ควรได้: Python 3.11.9

pip --version
# ควรได้: pip 24.x.x
```

---

## 🎮 ขั้นตอนที่ 2: ติดตั้ง CUDA Toolkit

### A. ตรวจสอบ GPU และ Driver

```powershell
# ตรวจสอบ GPU
nvidia-smi

# ควรเห็นข้อมูล GPU และ CUDA Version
# ตัวอย่าง:
# | NVIDIA-SMI 552.44       Driver Version: 552.44       CUDA Version: 12.4 |
```

### B. ติดตั้ง CUDA (ถ้ายังไม่มี)

```powershell
# ดาวน์โหลด CUDA Toolkit
# ไปที่: https://developer.nvidia.com/cuda-downloads

# เลือก:
# - Operating System: Windows
# - Architecture: x86_64
# - Version: 10 หรือ 11
# - Installer Type: exe (network)

# ดาวน์โหลดและติดตั้ง
# ขนาดประมาณ 3-4 GB
```

### C. ยืนยัน CUDA

```powershell
nvcc --version
# ควรเห็น CUDA compilation tools
```

---

## 📥 ขั้นตอนที่ 3: Clone Repository

### A. ติดตั้ง Git (ถ้ายังไม่มี)

```powershell
# ดาวน์โหลด Git
# ไปที่: https://git-scm.com/download/win
# ติดตั้งด้วยค่า default ทั้งหมด
```

### B. Clone โปรเจค

```powershell
# สร้างโฟลเดอร์
mkdir G:\
cd G:\

# Clone (แทน URL ด้วย repo จริงของคุณ)
git clone https://github.com/your-username/MDMA-App.git AlphaEdge_AINV

# เข้าไปในโฟลเดอร์
cd AlphaEdge_AINV

# เช็ค branch
git branch -a

# Checkout ไปที่ production branch (ถ้ามี)
git checkout main
# หรือ
git checkout production-internal
```

---

## 🐍 ขั้นตอนที่ 4: สร้าง Virtual Environment

### A. สร้าง venv

```powershell
# อยู่ใน G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV

# สร้าง virtual environment
python -m venv venv

# ควรเห็นโฟลเดอร์ venv สร้างขึ้นมา
```

### B. Activate venv

```powershell
# Activate (Windows)
venv\Scripts\activate

# ควรเห็น (venv) หน้า command prompt
# ตัวอย่าง: (venv) PS G:\AlphaEdge_AINV>
```

### C. Upgrade pip

```powershell
# Upgrade pip ให้เป็นเวอร์ชันล่าสุด
python -m pip install --upgrade pip
```

---

## 📦 ขั้นตอนที่ 5: ติดตั้ง Dependencies

### A. ติดตั้ง PyTorch (สำคัญมาก!)

```powershell
# ติดตั้ง PyTorch พร้อม CUDA support
# เลือก CUDA version ให้ตรงกับที่ติดตั้งไว้

# สำหรับ CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# สำหรับ CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# ใช้เวลาประมาณ 5-10 นาที
```

### B. ยืนยัน PyTorch + CUDA

```powershell
# Test PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
# ควรได้: PyTorch: 2.x.x+cu121

# Test CUDA
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
# ควรได้: CUDA available: True

# Test GPU
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
# ควรได้: GPU: NVIDIA GeForce RTX xxxx
```

### C. ติดตั้ง Dependencies หลัก

```powershell
# ติดตั้งจาก requirements_full.txt
pip install -r requirements_full.txt

# ใช้เวลาประมาณ 10-15 นาที
# จะติดตั้ง:
# - FastAPI, Gradio
# - Transformers, Sentence-transformers
# - ChromaDB
# - PaddleOCR
# - Faster-whisper
# - และอื่นๆ อีกมาก
```

### D. ติดตั้ง PaddlePaddle (สำหรับ OCR)

```powershell
# PaddlePaddle with GPU support
python -m pip install paddlepaddle-gpu -i https://pypi.tuna.tsinghua.edu.cn/simple

# หรือถ้าใช้ CPU อย่างเดียว
pip install paddlepaddle
```

---

## 🎤 ขั้นตอนที่ 6: ติดตั้ง Piper TTS (Optional)

### A. ดาวน์โหลด Piper

```powershell
# ดาวน์โหลดจาก GitHub
# ไปที่: https://github.com/rhasspy/piper/releases

# เลือก:
# - piper_windows_amd64.zip (สำหรับ Windows 64-bit)

# แตกไฟล์ไปที่:
G:\piper\
```

### B. ดาวน์โหลด Voice Model

```powershell
# ดาวน์โหลด voice model
# ไปที่: https://huggingface.co/rhasspy/piper-voices/tree/main

# เลือก:
# - en/en_US/lessac/medium/en_US-lessac-medium.onnx
# - en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# ดาวน์โหลดไปที่:
G:\piper\models\
```

### C. ทดสอบ Piper

```powershell
cd G:\piper

.\piper.exe --model models\en_US-lessac-medium.onnx --output_file test.wav
# พิมพ์: Hello, this is a test.
# กด Ctrl+Z แล้ว Enter

# ควรได้ไฟล์ test.wav
```

---

## 🖥️ ขั้นตอนที่ 7: ติดตั้ง LM Studio

### A. ดาวน์โหลด LM Studio

```powershell
# ไปที่: https://lmstudio.ai/
# ดาวน์โหลด LM Studio for Windows
# ติดตั้งตามปกติ
```

### B. ดาวน์โหลด Models

เปิด LM Studio แล้วดาวน์โหลด models:

```
1. Llama 3.3 70B (แนะนำ Q4_K_M)
   - ค้นหา: "llama-3.3-70b"
   - เลือก: bartowski/Llama-3.3-70B-Instruct-GGUF
   - เลือก quantization: Q4_K_M (ประมาณ 40GB)

2. Qwen 2.5 Coder 32B (แนะนำ Q5_K_M)
   - ค้นหา: "qwen2.5-coder-32b"
   - เลือก: Qwen/Qwen2.5-Coder-32B-Instruct-GGUF
   - เลือก quantization: Q5_K_M (ประมาณ 25GB)

3. Llama 3.1 8B (แนะนำ Q4_K_M)
   - ค้นหา: "llama-3.1-8b"
   - เลือก: Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
   - ขนาด: ประมาณ 4.5GB
```

### C. เปิด Server Mode

```
1. ใน LM Studio คลิก "Local Server" (ซ้ายมือ)
2. เลือก model (เช่น Llama 3.3 70B)
3. คลิก "Start Server"
4. ควรเห็น: Server running on http://localhost:1234
```

---

## ⚙️ ขั้นตอนที่ 8: Configuration

### A. สร้างไฟล์ .env

```powershell
# อยู่ใน G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV

# สร้างไฟล์ .env
notepad .env

# พิมพ์ข้อมูลต่อไปนี้:
```

```bash
# LM Studio (Local LLMs)
LM_STUDIO_URL=http://localhost:1234/v1

# NVIDIA API (Optional - สำหรับ Nemotron และ NV-CLIP)
# ไปขอ API key ที่: https://build.nvidia.com/
NVIDIA_API_KEY=nvapi-your-key-here

# API Server Settings
API_HOST=0.0.0.0
API_PORT=8000

# Feature Flags
USE_NVIDIA_CLIP=false

# Logging
LOG_LEVEL=INFO
```

### B. แก้ไข models_config.yaml (Optional)

```powershell
notepad models_config.yaml

# ตรวจสอบ paths ให้ตรงกับเครื่องคุณ
# โดยเฉพาะ:
# - endpoint: http://localhost:1234/v1
# - model paths (ถ้าใช้งานจริง)
```

---

## 🚀 ขั้นตอนที่ 9: ทดสอบการติดตั้ง

### A. ทดสอบ Basic Import

```powershell
# ทดสอบว่า packages ติดตั้งครบ
python -c "import fastapi; print('FastAPI OK')"
python -c "import gradio; print('Gradio OK')"
python -c "import chromadb; print('ChromaDB OK')"
python -c "import transformers; print('Transformers OK')"
python -c "from faster_whisper import WhisperModel; print('Whisper OK')"
python -c "import paddleocr; print('PaddleOCR OK')"
```

### B. ทดสอบ GPU Access

```powershell
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### C. ทดสอบ Model Router

```powershell
python -c "from model_router import ModelRouter; r = ModelRouter(); print('Model Router OK')"
```

---

## 🎯 ขั้นตอนที่ 10: เปิดใช้งาน Platform

### A. เปิด LM Studio Server

```
1. เปิด LM Studio
2. Local Server → เลือก Model
3. Start Server
4. ตรวจสอบ: http://localhost:1234
```

### B. เปิด Platform (เลือกวิธีใดวิธีหนึ่ง)

#### วิธีที่ 1: Full Platform (แนะนำ)

```powershell
cd G:\AlphaEdge_AINV
venv\Scripts\activate
python master_launcher.py --full

# หรือ
start_platform.bat
```

#### วิธีที่ 2: Web UI อย่างเดียว

```powershell
python web_ui.py

# หรือ
start_webui.bat
```

#### วิธีที่ 3: API Server อย่างเดียว

```powershell
python api_server.py

# หรือ
start_api.bat
```

### C. เข้าใช้งาน

เปิดเบราว์เซอร์:

```
Web UI:   http://localhost:7860
API:      http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

## ✅ ขั้นตอนที่ 11: Verification Checklist

ตรวจสอบว่าทุกอย่างทำงาน:

```
✅ Python 3.10/3.11 ติดตั้งแล้ว
✅ CUDA ติดตั้งแล้ว (nvidia-smi ใช้งานได้)
✅ Virtual environment สร้างแล้ว
✅ PyTorch + CUDA ติดตั้งแล้ว (torch.cuda.is_available() = True)
✅ Dependencies ทั้งหมดติดตั้งแล้ว
✅ LM Studio ติดตั้งและมี models
✅ LM Studio server รันอยู่ (port 1234)
✅ ไฟล์ .env สร้างแล้ว
✅ Platform เปิดได้ (Web UI หรือ API)
✅ เข้า Web UI ได้ (http://localhost:7860)
```

---

## 🐛 Troubleshooting (แก้ปัญหา)

### ปัญหา 1: Python ไม่พบ

```powershell
# แก้ไข:
# 1. Reinstall Python
# 2. ✅ เลือก "Add to PATH"
# 3. Restart PowerShell
```

### ปัญหา 2: CUDA ไม่ทำงาน

```powershell
# ตรวจสอบ:
nvidia-smi

# ถ้าไม่มี:
# 1. Update NVIDIA Driver
# 2. Reinstall CUDA Toolkit
```

### ปัญหา 3: torch.cuda.is_available() = False

```powershell
# แก้ไข:
# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### ปัญหา 4: Package ติดตั้งไม่ได้

```powershell
# แก้ไข:
# Upgrade pip
python -m pip install --upgrade pip

# ลองติดตั้งอีกครั้ง
pip install -r requirements_full.txt
```

### ปัญหา 5: LM Studio ไม่ connect

```powershell
# ตรวจสอบ:
curl http://localhost:1234/v1/models

# ถ้าไม่ได้:
# 1. ตรวจสอบ LM Studio server ทำงานอยู่
# 2. ตรวจสอบ port 1234 ไม่ถูกใช้
# 3. Restart LM Studio
```

### ปัญหา 6: Web UI ไม่เปิด

```powershell
# ตรวจสอบ:
# 1. Port 7860 ถูกใช้หรือไม่
netstat -an | findstr "7860"

# 2. Firewall block หรือไม่
# Windows Firewall → Allow app

# 3. ดู error log
python web_ui.py
```

### ปัญหา 7: Out of Memory (GPU)

```
แก้ไข:
1. ใช้ model ที่เล็กกว่า (Q4 แทน Q5)
2. ลด batch size
3. ปิด programs อื่นที่ใช้ GPU
```

---

## 📊 ความต้องการ Disk Space

```
Minimum Setup (เล็กสุด):
- Python + CUDA: 5GB
- Virtual Environment: 1GB
- Dependencies: 10GB
- Model (Llama 3.1 8B): 5GB
Total: ~21GB

Recommended Setup (แนะนำ):
- Python + CUDA: 5GB
- Virtual Environment: 1GB
- Dependencies: 15GB
- Models:
  - Llama 3.3 70B: 40GB
  - Qwen 2.5 Coder 32B: 25GB
  - Llama 3.1 8B: 5GB
Total: ~91GB

Full Setup (เต็มรูปแบบ):
- Above +
  - CLIP models: 2GB
  - Whisper models: 3GB
  - ChromaDB data: 5GB+
  - Logs & cache: 5GB
Total: ~106GB+
```

---

## 🚀 Quick Start Commands

```powershell
# เปิดทุกครั้ง:
cd G:\AlphaEdge_AINV
venv\Scripts\activate

# เปิด LM Studio → Start Server

# เปิด Platform:
python master_launcher.py --full

# เข้าใช้:
# http://localhost:7860 (Web UI)
# http://localhost:8000 (API)
```

---

## 📖 อ่านเพิ่มเติม

- `ENTERPRISE_PLATFORM.md` - ฟีเจอร์ทั้งหมด
- `IMPLEMENTATION_SUMMARY.md` - สรุปสิ่งที่มี
- `SECURITY_DEPLOYMENT.md` - ความปลอดภัย
- `README_JARETH2.md` - Agent documentation

---

## 🆘 ขอความช่วยเหลือ

หากติดปัญหา:

1. อ่าน Troubleshooting ด้านบน
2. ตรวจสอบ logs ใน `logs/`
3. ตรวจสอบ .env configuration
4. ลองรัน component ทีละตัว

---

## ✅ Installation Complete!

ถ้าทุกอย่างผ่าน → **พร้อมใช้งาน AlphaEdge AINV แล้ว!** 🎉

Access:
- 🌐 Web UI: http://localhost:7860
- 🔌 REST API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

---

**Copyright © 2025 AlphaEdge AINV. All Rights Reserved.**
