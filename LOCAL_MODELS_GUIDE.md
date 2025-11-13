# AlphaEdge AINV - Local Models Deployment Guide

## 🎯 Overview

Your AlphaEdge AINV platform now supports **11 powerful local GGUF models** from `G:\Models_Organized`:

### 🏆 Flagship Model
- **Qwen3-Next-80B-A3B-Instruct** (80B parameters!)
  - Best overall performance
  - Advanced reasoning and coding
  - 32K context window

### 💻 Code Generation Models
- **Qwen3-Coder** - Latest Qwen coder (32K context)
- **Qwen2.5-Coder** - Proven coding model (32K context)
- **DeepSeek-Coder** - Fast code completion (16K context)
- **Codestral** - Mistral's coding model (32K context)

### 🧠 General Purpose Models
- **Llama 3.2** - Latest Meta model (128K context!)
- **Llama 3.1** - Stable reasoning (128K context)
- **Mistral Nemo** - Fast inference (128K context!)
- **Mistral** - Lightweight (32K context)
- **NVIDIA Nemotron** - Advanced reasoning (32K context)
- **WizardLM2** - Complex tasks (32K context)

---

## 🚀 Quick Start

### 1. Scan Your Models
```bash
.\SCAN_MODELS.bat
```
This will:
- Scan `G:\Models_Organized\lmstudio-community\`
- Find all GGUF files
- Generate `local_models_config.json`
- Show recommended models for TensorRT conversion

### 2. Test Models
```bash
.\TEST_MODELS.bat
```
This will:
- Install `llama-cpp-python` with CUDA support
- List all available models
- Let you test individual models or all at once

### 3. Install TensorRT-LLM (Optional - for 2-10x speedup)
```bash
.\install_tensorrt_llm.bat
```
Choose option **1** to use existing models from `G:\Models_Organized`

### 4. Install RAPIDS (Optional - for 10-50x data processing)
```bash
.\install_rapids.bat
```
Choose **Full installation** for complete GPU acceleration

---

## 📊 Model Selection Strategy

### For Code Tasks
**Priority order:**
1. `qwen3-next-80b-local` 🏆 (Best!)
2. `qwen3-coder-local`
3. `qwen2.5-coder-local`
4. `deepseek-coder-local`
5. `codestral-local`

### For Business/Reasoning
**Priority order:**
1. `qwen3-next-80b-local` 🏆 (Best!)
2. `llama3.2-local` (128K context)
3. `llama3.1-local` (128K context)
4. `wizardlm2-local`

### For Fast Inference
**Priority order:**
1. `mistral-nemo-local` (128K context!)
2. `mistral-local`

---

## 🔧 How It Works

### GGUF Model Loading
The platform uses `llama-cpp-python` with CUDA acceleration:

```python
from gguf_model_loader import get_loader

loader = get_loader()

# Generate text
response = loader.generate(
    model_id="qwen3-next-80b-local",
    prompt="Write a Python function for...",
    max_tokens=2048,
    temperature=0.2
)
```

### Automatic Model Selection
The platform automatically routes requests to the best model:

```python
# Code request → Qwen3-Next-80B or Qwen3-Coder
# Business request → Qwen3-Next-80B or Llama 3.2
# Fast request → Mistral Nemo
```

### TensorRT Optimization (When installed)
- First use: Builds optimized TensorRT engine (~30-90 min)
- Subsequent uses: **2-10x faster inference!**
- Engines cached in `G:\AIModels\tensorrt_engines\`

---

## 📁 Directory Structure

```
G:\Models_Organized\lmstudio-community\
├── Qwen3-Next-80B-A3B-Instruct\     # 🏆 Flagship 80B
│   └── *.gguf
├── qwen3-coder\
│   └── *.gguf
├── qwen2.5-coder\
│   └── *.gguf
├── deepseek-coder\
│   └── *.gguf
├── codestral\
│   └── *.gguf
├── llama3.2\
│   └── *.gguf
├── llama3.1\
│   └── *.gguf
├── Mistral-Nemo-Instruct-2407-GGUF\
│   └── *.gguf
├── mistral\
│   └── *.gguf
├── nemotron\
│   └── *.gguf
└── wizardlm2\
    └── *.gguf

G:\AIModels\                         # Created by installers
├── tensorrt_engines\                # TensorRT optimized engines
├── huggingface\                     # Downloaded HF models
├── cache\                           # Model cache
└── downloads\                       # Temporary downloads
```

---

## ⚙️ Configuration

All models are configured in `models_config.yaml`:

```yaml
local_models:
  qwen3-next-80b-local:
    path: G:\Models_Organized\lmstudio-community\Qwen3-Next-80B-A3B-Instruct
    engine: gguf
    use_case: [advanced_reasoning, code, research, flagship]
    max_tokens: 16384
    temperature: 0.7
    context_length: 32768
```

### Routing (Local-first strategy):
```yaml
routing:
  code:
    - qwen3-next-80b-local       # Try flagship first
    - qwen3-coder-local          # Then specialized coders
    - llama-3.1-70B-cloud        # Cloud fallback
```

---

## 🎮 Usage Examples

### Example 1: Test Specific Model
```bash
.\TEST_MODELS.bat
# Choose option 1 for Qwen3-Next-80B
```

### Example 2: Programmatic Usage
```python
from gguf_model_loader import get_loader

loader = get_loader()

# List available models
models = loader.list_available_models()
print(f"Found {len(models)} models")

# Get model info
info = loader.get_model_info("qwen3-next-80b-local")
print(f"Size: {info['size_gb']} GB")
print(f"Context: {info['context_length']}")

# Generate
response = loader.generate(
    "qwen3-next-80b-local",
    "Explain quantum computing",
    max_tokens=1000
)
print(response)
```

### Example 3: Integrate with Platform
```python
# In your code, models are automatically loaded via model router
from model_router import ModelRouter

router = ModelRouter()

# Automatic model selection
response = await router.chat(
    "Write a FastAPI endpoint for user authentication",
    task_type="code"  # Will use qwen3-next-80b-local or qwen3-coder-local
)
```

---

## 🚀 Performance Tips

### 1. Quantization Selection
The loader automatically selects the best quantization:
- **Q6** - Best quality (largest)
- **Q5** - Great quality (balanced)
- **Q4** - Good quality (smaller)
- **Q8/F16** - Highest quality (very large)

### 2. GPU Layers
All models use `n_gpu_layers=-1` (full GPU offload) for maximum speed.

### 3. Context Length
- Use appropriate context for your task
- Longer context = more memory
- Models support up to 128K tokens (Llama 3.2, Mistral Nemo)

### 4. Batch Processing
```python
# Process multiple prompts efficiently
prompts = [...]
for prompt in prompts:
    response = loader.generate(model_id, prompt)
    # Process...
```

---

## 🐛 Troubleshooting

### Model Not Found
```bash
# Re-scan models
.\SCAN_MODELS.bat

# Check directory structure
dir "G:\Models_Organized\lmstudio-community\" /b /ad
```

### Out of Memory
- Use smaller quantization (Q4 instead of Q6)
- Reduce `n_ctx` (context length)
- Unload unused models: `loader.unload_model(model_id)`

### Slow Generation
- Install TensorRT-LLM for 2-10x speedup: `.\install_tensorrt_llm.bat`
- Ensure GPU drivers are up to date
- Check CUDA version: `nvcc --version`

### llama-cpp-python Installation Failed
```bash
# Manual installation
pip install llama-cpp-python --force-reinstall --no-cache-dir ^
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

---

## 📈 Next Steps

1. ✅ **Scan models**: `.\SCAN_MODELS.bat`
2. ✅ **Test models**: `.\TEST_MODELS.bat`
3. ⚡ **Install TensorRT**: `.\install_tensorrt_llm.bat` (2-10x faster)
4. 🚀 **Install RAPIDS**: `.\install_rapids.bat` (10-50x data processing)
5. 🎯 **Run platform**: `.\START.bat`

---

## 🎉 Benefits

### vs Cloud API
- ✅ **100% Private** - No data sent to cloud
- ✅ **No API costs** - Free inference
- ✅ **No rate limits** - Unlimited requests
- ✅ **Lower latency** - No network overhead
- ✅ **Works offline** - No internet required

### vs LM Studio
- ✅ **Automatic routing** - Best model for each task
- ✅ **TensorRT optimization** - 2-10x faster
- ✅ **Integrated platform** - Works with 40 MCP tools
- ✅ **RAPIDS acceleration** - GPU data processing
- ✅ **Scalable** - Multi-GPU support

---

**Questions?** Check `INSTALLATION_GUIDE.md` or test with `.\TEST_MODELS.bat`
