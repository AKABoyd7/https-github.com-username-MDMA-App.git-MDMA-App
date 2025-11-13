# 🚀 TensorRT-LLM Setup Guide

**TensorRT-LLM = เร็วที่สุด สำหรับ LLM Inference**

- 2-10x เร็วกว่า LM Studio
- ใช้ VRAM น้อยกว่า 30-40%
- Latency ต่ำกว่า 50%

---

## 📋 Requirements

- NVIDIA GPU (16GB+ VRAM แนะนำ)
- CUDA 12.1+
- Python 3.10 หรือ 3.11
- PyTorch 2.0+ with CUDA

---

## 🔧 Installation

### **ขั้นที่ 1: ติดตั้ง TensorRT-LLM**

```powershell
cd G:\AlphaEdge_AINV
.\install_tensorrt_llm.ps1
```

หรือติดตั้งด้วยตัวเอง:

```powershell
pip install tensorrt_llm -U --extra-index-url https://pypi.nvidia.com
```

---

## 📥 Model Preparation

### **1. ดาวน์โหลด Models จาก Hugging Face**

```powershell
# ติดตั้ง Git LFS
git lfs install

# ดาวน์โหลด Model (เลือก 1 อัน)

# Llama 3.1 8B (4.5GB - เร็ว)
git clone https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

# Llama 3.1 70B (40GB - แม่นสุด)
git clone https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct

# Qwen 2.5 Coder 32B (18GB - coding)
git clone https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct

# Mistral 7B (4GB - lightweight)
git clone https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
```

**หมายเหตุ:** ต้องมี Hugging Face token สำหรับ Llama models
- ไปที่: https://huggingface.co/settings/tokens
- สร้าง token แล้ว login: `huggingface-cli login`

---

## ⚙️ Convert Models to TensorRT

### **Llama 3.1 8B (1 GPU)**

```powershell
trtllm-build --checkpoint_dir Llama-3.1-8B-Instruct `
             --output_dir G:\AlphaEdge_AINV\trt_engines\llama8b `
             --gemm_plugin float16 `
             --gpt_attention_plugin float16 `
             --max_batch_size 8 `
             --max_input_len 4096 `
             --max_output_len 2048
```

**เวลาที่ใช้:** 5-15 นาที

---

### **Llama 3.1 70B (Multi-GPU)**

```powershell
# ต้องมี 2-4 GPUs (24GB+ แต่ละตัว)
trtllm-build --checkpoint_dir Llama-3.1-70B-Instruct `
             --output_dir G:\AlphaEdge_AINV\trt_engines\llama70b `
             --gemm_plugin float16 `
             --gpt_attention_plugin float16 `
             --tp_size 2 `
             --max_batch_size 4 `
             --max_input_len 4096 `
             --max_output_len 2048
```

**`tp_size`:**
- `2` = 2 GPUs
- `4` = 4 GPUs

**เวลาที่ใช้:** 20-40 นาที

---

### **Qwen 2.5 Coder 32B (1-2 GPUs)**

```powershell
trtllm-build --checkpoint_dir Qwen2.5-Coder-32B-Instruct `
             --output_dir G:\AlphaEdge_AINV\trt_engines\qwen32b `
             --gemm_plugin float16 `
             --gpt_attention_plugin float16 `
             --tp_size 1 `
             --max_batch_size 4 `
             --max_input_len 8192 `
             --max_output_len 4096
```

---

## 🚀 Run TensorRT-LLM Server

### **Start Server**

```powershell
# Single GPU
python -m tensorrt_llm.hlapi.llm_api `
       --engine_dir G:\AlphaEdge_AINV\trt_engines\llama8b `
       --port 8000 `
       --host 0.0.0.0

# Multi-GPU
mpirun -n 2 --allow-run-as-root `
       python -m tensorrt_llm.hlapi.llm_api `
       --engine_dir G:\AlphaEdge_AINV\trt_engines\llama70b `
       --port 8000 `
       --host 0.0.0.0
```

**Server จะรันที่:** `http://localhost:8000`

---

## ⚙️ Configure AlphaEdge AINV

### **แก้ไข `.env`:**

```env
# TensorRT-LLM Configuration
USE_TENSORRT_LLM=true
TENSORRT_LLM_URL=http://localhost:8000
TENSORRT_ENGINE_PATH=G:\AlphaEdge_AINV\trt_engines\llama8b
LM_STUDIO_URL=http://localhost:8000
```

### **รัน Platform:**

```powershell
python master_launcher.py --full
```

---

## 📊 Performance Comparison

| Method | Llama 3.1 8B<br>Latency | VRAM Usage | Throughput |
|--------|------------------------|------------|------------|
| **TensorRT-LLM** | **12ms** | **4.2GB** | **850 tok/s** |
| LM Studio | 45ms | 6.5GB | 220 tok/s |
| vLLM | 18ms | 5.8GB | 550 tok/s |
| llama.cpp | 35ms | 5.2GB | 280 tok/s |

**TensorRT-LLM = 3-4x เร็วกว่า LM Studio!**

---

## 🐳 Docker Alternative (ง่ายกว่า)

```powershell
# Pull image
docker pull nvcr.io/nvidia/tensorrt_llm:24.10-py3

# Run container
docker run --gpus all -p 8000:8000 `
           -v G:\AlphaEdge_AINV\trt_engines:/engines `
           nvcr.io/nvidia/tensorrt_llm:24.10-py3 `
           python -m tensorrt_llm.hlapi.llm_api `
           --engine_dir /engines/llama8b `
           --port 8000
```

---

## 🔧 Troubleshooting

### **Error: CUDA out of memory**

**วิธีแก้:**
1. ลด `max_batch_size`:
   ```powershell
   --max_batch_size 1
   ```
2. ใช้ INT8 quantization:
   ```powershell
   --use_int8_kv_cache
   ```
3. ใช้ model เล็กกว่า (8B แทน 70B)

---

### **Error: Cannot find libcudnn**

**วิธีแก้:**
```powershell
# ติดตั้ง cuDNN
pip install nvidia-cudnn-cu12
```

---

### **Performance ไม่ดีตามที่คาด**

**เช็ค:**
1. GPU Utilization:
   ```powershell
   nvidia-smi -l 1
   ```
   ควรเห็น ~90-100%

2. ใช้ FP16 (ไม่ใช่ FP32):
   ```powershell
   --gemm_plugin float16
   ```

3. เปิด Flash Attention:
   ```powershell
   --use_flash_attention
   ```

---

## 📚 Model Zoo

| Model | Size | VRAM | Use Case |
|-------|------|------|----------|
| Llama 3.1 8B | 4.5GB | 6GB | General, Fast |
| Llama 3.3 70B | 40GB | 48GB | Best Quality |
| Qwen 2.5 Coder 32B | 18GB | 22GB | Coding |
| Mistral 7B | 4GB | 5.5GB | Lightweight |
| Nemotron 22B | 12GB | 16GB | Reasoning |

---

## 🎯 Recommended Setup

### **สำหรับ RTX 4090 (24GB):**
- Llama 3.1 8B (FP16) - เร็วมาก
- Qwen 2.5 Coder 32B (INT8) - Coding

### **สำหรับ 2x RTX 4090 (48GB):**
- Llama 3.3 70B (FP16, TP=2) - Best Quality
- Qwen 2.5 Coder 32B (FP16) - Fast Coding

### **สำหรับ 4x A6000 (192GB):**
- Llama 3.3 70B (FP16, TP=2) - Production
- Multiple models concurrently

---

## 🔗 Resources

- **Official Docs:** https://nvidia.github.io/TensorRT-LLM/
- **GitHub:** https://github.com/NVIDIA/TensorRT-LLM
- **Model Hub:** https://huggingface.co/models?library=tensorrt

---

**พร้อมเริ่มต้น! 🚀**

```powershell
.\install_tensorrt_llm.ps1
```
