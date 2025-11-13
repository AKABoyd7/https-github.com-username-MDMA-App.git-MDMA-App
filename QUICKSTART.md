# 🚀 AlphaEdge AINV - Quick Start Guide

## ติดตั้งทุกอย่างในคำสั่งเดียว

### **Windows (แนะนำ)**

```powershell
cd G:\AlphaEdge_AINV
git pull
.\install_all.ps1
```

**เวลาที่ใช้:** 10-15 นาที (ไม่รวม RAPIDS)
**เวลาที่ใช้:** 30-40 นาที (รวม RAPIDS)

---

## สิ่งที่จะติดตั้ง

### **1. Python Dependencies (จำเป็น)**
- PyTorch 2.9+ with CUDA 12.1
- TensorRT 10.14+ (2-5x faster inference)
- Transformers, Gradio, ChromaDB
- FastAPI, LangChain, Whisper
- PaddleOCR, Sentence Transformers

### **2. Configuration (จำเป็น)**
- สร้าง/ตรวจสอบไฟล์ `.env`
- ตั้งค่า NVIDIA API Key
- ตั้งค่า LM Studio endpoint

### **3. RAPIDS (Optional - แนะนำ)**
- cuDF - GPU DataFrame (10-50x faster)
- cuML - GPU Machine Learning (20-100x faster)
- cuGraph - GPU Graph Analytics
- ติดตั้งใน WSL2 (Ubuntu)

### **4. LM Studio (จำเป็น)**
- ดาวน์โหลดจาก: https://lmstudio.ai
- ดาวน์โหลด Models:
  - Llama 3.3 70B (40GB) - Best reasoning
  - Qwen 2.5 Coder 32B (22GB) - Best coding
  - Llama 3.1 8B (4.5GB) - Fast & lightweight

---

## ขั้นตอนการติดตั้ง

### **1. Clone Repository (ถ้ายังไม่มี)**

```powershell
git clone <repository-url> G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV
git checkout claude/alphaedge-mcp-server-011CV477Fds3K8XrtkujexEt
```

### **2. รัน Installer**

```powershell
.\install_all.ps1
```

**สคริปต์จะ:**
1. ติดตั้ง PyTorch + CUDA
2. ติดตั้ง dependencies ทั้งหมด
3. สร้าง/ตรวจสอบ `.env`
4. (Optional) ติดตั้ง RAPIDS ใน WSL2
5. ตรวจสอบ LM Studio
6. ทดสอบระบบ

### **3. ตั้งค่า LM Studio**

1. ดาวน์โหลด: https://lmstudio.ai
2. ดาวน์โหลด Model อย่างน้อย 1 ตัว
3. เปิด **Local Server** → Port **1234**

### **4. รัน Platform**

```powershell
python master_launcher.py --full
```

**หรือรันแยกส่วน:**

```powershell
# API Server only
python master_launcher.py --api

# Web UI only
python master_launcher.py --ui

# Autonomous Agent
python master_launcher.py --agent
```

### **5. เข้าใช้งาน**

- **Web UI:** http://localhost:7860
- **API Docs:** http://localhost:8000/docs
- **LM Studio:** http://localhost:1234

---

## การติดตั้งแบบ Custom

### **ข้าม RAPIDS**

```powershell
.\install_all.ps1 -SkipRAPIDSInstall
```

### **ติดตั้งเฉพาะ RAPIDS**

```powershell
.\install_rapids.ps1
```

### **ติดตั้งด้วยตัวเอง**

```powershell
# 1. PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 2. Dependencies
pip install -r requirements_full.txt

# 3. Copy .env
copy .env.example .env
notepad .env  # แก้ไข API Keys

# 4. รัน
python master_launcher.py --full
```

---

## Troubleshooting

### **Error: Missing NVIDIA API Key**

1. ไปที่: https://build.nvidia.com/explore/discover
2. สมัคร/Login (ฟรี)
3. Copy API Key
4. แก้ไข `.env`:
   ```
   NVIDIA_API_KEY=nvapi-xxxxxxxx
   ```

### **Error: LM Studio not running**

1. เปิด LM Studio
2. คลิก **"Local Server"** (ด้านซ้าย)
3. เลือก Model
4. คลิก **"Start Server"**
5. ตรวจสอบ Port 1234 เป็นสีเขียว

### **Error: RAPIDS installation failed**

**สาเหตุ:** WSL2 disk I/O error, พื้นที่ไม่พอ

**วิธีแก้:**
1. ข้าม RAPIDS ไปก่อน (ใช้ TensorRT เพียงอย่างเดียว)
2. หรือติดตั้งใน Docker:
   ```powershell
   docker pull rapidsai/rapidsai:24.10-cuda12.1-runtime-ubuntu22.04-py3.11
   ```

### **Error: CUDA not available**

1. ตรวจสอบ NVIDIA Driver:
   ```powershell
   nvidia-smi
   ```
2. อัพเดท Driver: https://www.nvidia.com/Download/index.aspx
3. ติดตั้ง PyTorch ใหม่:
   ```powershell
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
   ```

---

## System Requirements

### **ขั้นต่ำ**
- Windows 10/11 (64-bit)
- Python 3.10 - 3.12
- NVIDIA GPU (8GB+ VRAM)
- CUDA 11.8 / 12.1
- 32GB RAM
- 50GB Storage

### **แนะนำ**
- Windows 11 (64-bit)
- Python 3.11
- NVIDIA RTX GPU (16GB+ VRAM)
- CUDA 12.1
- 64GB+ RAM
- 100GB+ SSD Storage

### **สำหรับ RAPIDS**
- WSL2 (Ubuntu 22.04 / 24.04)
- 15GB free space (C:\ or custom location)
- 64GB+ RAM

---

## Next Steps

หลังติดตั้งเสร็จ:

1. **ทดสอบ API:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **ทดสอบ LLM:**
   - เปิด Web UI: http://localhost:7860
   - ไปที่แท็บ "Chat"
   - พิมพ์คำถาม

3. **ทดสอบ Voice:**
   - แท็บ "Voice Interface"
   - คลิก "Start Recording"

4. **ทดสอบ Vision:**
   - แท็บ "Vision & OCR"
   - อัพโหลดรูปภาพ

5. **ทดสอบ RAG:**
   - แท็บ "RAG System"
   - อัพโหลดเอกสาร

---

## Support

- **Documentation:** `INSTALLATION.md`, `CUDA_X_GUIDE.md`
- **Issues:** GitHub Issues
- **API Docs:** http://localhost:8000/docs

---

## Performance Optimization

### **เปิดใช้งาน CUDA-X**

แก้ไข `.env`:
```env
USE_TENSORRT=true      # 2-5x faster inference
USE_RAPIDS=true        # 10-50x faster data processing
USE_MULTI_GPU=true     # Linear scaling (if multiple GPUs)
```

### **เลือก Model ให้เหมาะสม**

- **Fast queries:** Llama 3.1 8B, Mistral 7B
- **Complex reasoning:** Llama 3.3 70B, Nemotron 43B
- **Coding:** Qwen 2.5 Coder 32B
- **Business/RAG:** Nemotron 43B

### **Cache Settings**

```env
ENABLE_CACHE=true
CACHE_TTL=3600         # 1 hour
```

---

**พร้อมเริ่มต้นแล้ว! 🚀**

```powershell
.\install_all.ps1
```
