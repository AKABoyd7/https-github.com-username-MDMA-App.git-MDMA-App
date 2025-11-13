# Smart AI Agent with TensorRT-LLM

AI Agent with intelligent backend selection and automatic failover.

## Features

### 🚀 Smart Routing
- **TensorRT-LLM** (fastest - 2-10x speedup)
- **Ollama** (fallback - easy setup)
- **Automatic failover** between backends

### 🔧 Auto Model Conversion
- Converts HuggingFace models to TensorRT automatically
- Caches converted models
- Only converts once

### 📊 Performance Monitoring
- Real-time metrics
- Latency tracking
- Error monitoring

### 🛡️ Robust Error Handling
- Automatic fallback on errors
- Health monitoring
- Graceful degradation

## Installation

### Quick Start (Windows)

```batch
# Run the installer
.\install_tensorrt.bat

# Start the agent
python agent_tensorrt.py
```

### Manual Installation

```bash
# 1. Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2. Install TensorRT-LLM
pip install tensorrt-llm --extra-index-url https://pypi.nvidia.com

# 3. Install other dependencies
pip install transformers accelerate sentencepiece
pip install langchain langgraph langchain-community
pip install nvidia-ml-py

# 4. Run
python agent_tensorrt.py
```

## Usage

### Basic Usage

```python
from smart_router import SmartInferenceRouter

# Initialize router
router = SmartInferenceRouter(
    tensorrt_model_path="./tensorrt_models/llama-3-8b/engine",
    use_ollama=True
)

# Generate response
result = await router.generate(
    prompt="Hello, how are you?",
    max_tokens=512
)

print(result['response'])
print(f"Backend used: {result['backend']}")
```

### Model Conversion

```python
from model_converter import SmartModelConverter

converter = SmartModelConverter()

# Convert model (only if not already cached)
engine_path = converter.convert_if_needed("llama-3-8b")

# List converted models
models = converter.list_converted_models()
print(f"Available models: {models}")

# Get cache info
info = converter.get_cache_info()
print(f"Cache size: {info['cache_size_gb']:.2f} GB")
```

### Interactive Agent

```bash
python agent_tensorrt.py
```

Commands:
- Type your message to chat
- `status` - Show current backend and metrics
- `exit` or `quit` - Exit

## Architecture

```
User Input
    ↓
SmartInferenceRouter
    ├─→ TensorRT Engine (fastest)
    │   ├─ Success → Response
    │   └─ Fail → Fallback ↓
    │
    ├─→ Ollama (fallback)
    │   ├─ Success → Response
    │   └─ Fail → Fallback ↓
    │
    └─→ Cloud API (optional)
        └─ Response
```

## File Structure

```
MDMA-App/
├── agent_tensorrt.py       # Smart agent with TensorRT
├── smart_router.py          # Hybrid routing system
├── tensorrt_engine.py       # TensorRT inference engine
├── model_converter.py       # Auto model conversion
├── install_tensorrt.bat     # Installation script
├── requirements.txt         # Dependencies
└── tensorrt_models/         # Cached models
    └── llama-3-8b/
        └── engine/
            └── rank0.engine
```

## Requirements

### Hardware
- NVIDIA GPU (RTX 3000/4000 series or better)
- 16GB+ RAM
- 50GB+ disk space

### Software
- Python 3.10+
- CUDA 12.1+
- Windows 10/11 or Linux

## Supported Models

| Model | Size | VRAM Required | Speed |
|-------|------|---------------|-------|
| Llama 3 8B | 16GB | 8GB | ⚡⚡⚡ |
| Llama 3.1 8B | 16GB | 8GB | ⚡⚡⚡ |
| Qwen 2.5 7B | 14GB | 7GB | ⚡⚡⚡ |

## Performance

**Typical latency:**
- TensorRT-LLM: 50-200ms
- Ollama: 200-500ms
- Cloud API: 500-2000ms

**Speedup vs Ollama:** 2-10x faster

## Troubleshooting

### TensorRT not working?
→ Agent will automatically use Ollama fallback

### Out of memory?
→ Use smaller model or reduce max_batch_size

### CUDA errors?
→ Update GPU drivers and CUDA toolkit

### Slow conversion?
→ First conversion takes time, but cached afterward

## License

MIT

## Credits

- TensorRT-LLM: NVIDIA
- Llama: Meta
- Langgraph: LangChain
