# AlphaEdge AINV - Enterprise Platform Documentation

**The Complete AI Operating System**

Copyright © 2025 AlphaEdge AINV. All Rights Reserved.

---

## 🎯 Overview

AlphaEdge AINV is a **complete enterprise AI platform** that runs 100% locally on your infrastructure. It combines:

- **Multiple LLMs** (Llama, Qwen, Mistral, NVIDIA Nemotron)
- **Multimodal AI** (Vision, Voice, Text)
- **RAG & Vector Search** (ChromaDB)
- **Multi-Agent Orchestration**
- **REST API & Web UI**
- **Background Daemon Service**
- **40+ Windows Control Tools**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACES                      │
├─────────────────────────────────────────────────────────┤
│  Web UI (Gradio)  │  REST API  │  CLI  │  Voice I/O    │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                   MODEL ROUTER                          │
│  (Intelligent routing to best LLM for each task)       │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                     AI MODELS                           │
├─────────────────────────────────────────────────────────┤
│  Local LLMs                │  Cloud LLMs                │
│  • Llama 3.3 70B          │  • NVIDIA Nemotron 43B     │
│  • Qwen 2.5 Coder 32B     │  • NVIDIA NV-CLIP          │
│  • Llama 3.1 8B           │                            │
│  • Mistral 7B             │                            │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                MULTIMODAL CAPABILITIES                  │
├─────────────────────────────────────────────────────────┤
│  Vision        │  Voice         │  RAG & Memory         │
│  • NV-CLIP     │  • Whisper STT │  • ChromaDB          │
│  • Local CLIP  │  • Piper TTS   │  • Vector Search     │
│  • OCR         │                │  • Long-term Memory   │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  AGENT FRAMEWORK                        │
├─────────────────────────────────────────────────────────┤
│  • Autonomous Agent (ReAct)                            │
│  • Multi-Agent Orchestration                           │
│  • Background Daemon                                   │
│  • Task Queue & Scheduling                             │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                    TOOLS LAYER                          │
│  (40+ tools for Windows, GPU, Files, Network, etc.)    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

1. **Hardware:**
   - NVIDIA GPU with 8GB+ VRAM (24GB recommended)
   - 16GB+ system RAM (32GB+ recommended)
   - 50GB+ disk space

2. **Software:**
   - Windows 10/11 or Windows Server
   - Python 3.10+
   - CUDA 11.8+ or 12.x
   - LM Studio (for local models)

### Installation

```powershell
# 1. Clone repository
git clone <repo-url> G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements_full.txt

# 4. Install PyTorch with CUDA (if not already installed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 5. Configure
copy .env.template .env
# Edit .env with your API keys (optional)

# 6. Launch
python master_launcher.py
```

### First Launch

1. **Interactive Menu:**
   ```powershell
   python master_launcher.py
   ```
   Select option 1 for full platform

2. **Direct Launch:**
   ```powershell
   python master_launcher.py --full
   ```

3. **Access:**
   - Web UI: http://localhost:7860
   - REST API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## 📦 Components

### 1. Model Router (`model_router.py`)

**Intelligent LLM routing based on task type**

```python
from model_router import get_router

router = get_router()

# Auto-route query
result = await router.route_query(
    "Write a Python function to parse JSON",
    task_type="code"  # Routes to Qwen Coder
)

# Quick helpers
from model_router import ask_code, ask_business, ask_reasoning

response = await ask_code("How do I implement async in Python?")
```

**Supported Models:**
- **Code:** Qwen 2.5 Coder 32B, DeepSeek Coder
- **Business:** NVIDIA Nemotron 43B, Llama 3.3 70B
- **Reasoning:** Nemotron 43B, Llama 3.3 70B
- **Fast:** Llama 3.1 8B, Mistral 7B

### 2. NVIDIA Integration (`nvidia_integration.py`)

**Cloud-powered advanced AI**

```python
from nvidia_integration import NVIDIANemotron, NVCLIP

# Advanced reasoning
nemotron = NVIDIANemotron()
answer = await nemotron.reasoning(
    "Explain the business impact of AI automation"
)

# Multimodal vision
nvclip = NVCLIP()

# Zero-shot classification
result = await nvclip.zero_shot_classify(
    "screenshot.png",
    labels=["error", "success", "warning", "info"]
)

# Image search
results = await nvclip.image_search(
    query="find all screenshots with error messages",
    image_paths=["path/to/images"],
    top_k=5
)
```

### 3. Voice Interface (`voice_interface.py`)

**Speech-to-Text + Text-to-Speech**

```python
from voice_interface import VoiceInterface

voice = VoiceInterface(
    whisper_model="base",  # or "large-v3"
    tts_voice="en_US-lessac-medium"
)

# Transcribe audio
text = await voice.listen("recording.wav")

# Generate speech
audio_path = await voice.speak("Hello, how can I help you?")

# Full conversation turn
async def process_query(text):
    # Your AI processing here
    return "I can help with that!"

result = await voice.conversation_turn(
    audio_input="user_voice.wav",
    response_callback=process_query,
    output_path="response.wav"
)
```

### 4. Vision System (`vision_system.py`)

**CLIP + OCR + Vision Understanding**

```python
from vision_system import VisionSystem

vision = VisionSystem(
    use_nvidia_clip=True,  # Use NV-CLIP
    ocr_backend="paddleocr"  # or "tesseract"
)

# Complete image analysis
result = await vision.analyze_image(
    "screenshot.png",
    query="What error is shown?",
    labels=["critical", "warning", "info"],
    extract_text=True
)

# Classification
print(result['classification'])
# {'critical': 0.85, 'warning': 0.10, 'info': 0.05}

# OCR text
print(result['ocr']['text'])

# Image search
results = await vision.search_images(
    query="screenshots with login buttons",
    image_dir="G:/screenshots",
    top_k=10
)
```

### 5. RAG System (`rag_system.py`)

**ChromaDB + Vector Search + Memory**

```python
from rag_system import get_knowledge_base, get_conversation_memory

# Knowledge base
kb = get_knowledge_base()

# Add knowledge
kb.add_knowledge(
    text="Python 3.11 introduced the tomllib module for TOML parsing",
    category="technical",
    tags=["python", "toml"],
    source="docs"
)

# Query knowledge
results = await kb.query_knowledge(
    "How to parse TOML in Python?",
    category="technical",
    n_results=3
)

# Conversation memory
memory = get_conversation_memory()

# Add conversation
memory.add_turn(
    user_message="How do I use async/await?",
    assistant_message="Async/await is used for..."
)

# Search history
history = await memory.search_history(
    "async programming",
    n_results=5
)
```

### 6. Multi-Agent Orchestration (`multi_agent.py`)

**Coordinate multiple AI agents**

```python
from multi_agent import create_default_team

# Create team
orchestrator = create_default_team()
# Creates: coordinator, coder, analyst, executor

# Define workflow
workflow = [
    {
        'goal': 'Research best Python logging practices',
        'task_type': 'research',
        'priority': 2
    },
    {
        'goal': 'Implement logging in my application',
        'task_type': 'code',
        'priority': 1,
        'dependencies': ['task_0']  # Depends on research
    }
]

# Run workflow
results = await orchestrator.run_workflow(workflow)

# Parallel execution
tasks = [
    {'goal': 'Check system health', 'task_type': 'system'},
    {'goal': 'Analyze logs', 'task_type': 'analysis'},
    {'goal': 'Generate report', 'task_type': 'general'}
]

results = await orchestrator.parallel_execution(tasks)
```

### 7. REST API Server (`api_server.py`)

**FastAPI with WebSocket support**

**Endpoints:**

- `POST /chat` - Chat with AI (auto-routed)
- `POST /vision` - Vision analysis
- `POST /tool` - Execute tool
- `GET /tools` - List tools
- `POST /agent/task` - Run autonomous agent
- `POST /daemon/task` - Add daemon task
- `GET /daemon/tasks` - List daemon tasks
- `GET /models` - List models
- `GET /status` - System status
- `WS /ws` - WebSocket for real-time chat

**Example:**

```python
import requests

# Chat
response = requests.post("http://localhost:8000/chat", json={
    "query": "Write a function to calculate fibonacci",
    "task_type": "code",
    "temperature": 0.3
})

result = response.json()
print(result['response'])
print(f"Model used: {result['model']}")

# Vision analysis
response = requests.post("http://localhost:8000/vision", json={
    "image_path": "screenshot.png",
    "labels": ["error", "success", "warning"],
    "extract_text": True
})

# Execute tool
response = requests.post("http://localhost:8000/tool", json={
    "tool_name": "gpu_status",
    "arguments": {}
})
```

### 8. Web UI (`web_ui.py`)

**Gradio-based web interface**

**Tabs:**
- 💬 **Chat** - Chat with AI (auto-routed)
- 🛠️ **Tools** - Execute tools directly
- 🤖 **Autonomous Agent** - Run goal-oriented tasks
- ⚙️ **Daemon Queue** - 24/7 background tasks
- 👁️ **Vision** - Image analysis with NV-CLIP
- 📊 **System Status** - Monitor system

**Launch:**
```powershell
python web_ui.py
# Access: http://localhost:7860
```

---

## 🔧 Configuration

### `models_config.yaml`

Complete model configuration:

```yaml
local_models:
  llama-3.3-70B:
    path: /models/llama3-3-70B.Q4_K_M.gguf
    engine: lm-studio
    endpoint: http://localhost:1234/v1
    use_case: [reasoning, general, business]

cloud_models:
  nemotron-3-43B:
    engine: nvidia-cloud
    endpoint: https://integrate.api.nvidia.com/v1
    model_name: nvidia/nemotron-3-43b-instruct
    api_key_env: NVIDIA_API_KEY
    use_case: [advanced_reasoning, business, analytics]

multimodal_models:
  nv-clip:
    engine: nvidia-cloud
    model_name: nvidia/nv-clip-vit-h-14
    use_case: [vision, embedding, image_search]

routing:
  code: [qwen-2.5-coder-32B]
  business: [nemotron-3-43B, llama-3.3-70B]
  reasoning: [nemotron-3-43B]
  fast: [llama-3.1-8B]
  vision: [nv-clip]
```

### `.env`

```bash
# LM Studio
LM_STUDIO_URL=http://localhost:1234/v1

# NVIDIA API (optional, for cloud features)
NVIDIA_API_KEY=nvapi-your-key-here

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Feature Flags
USE_NVIDIA_CLIP=false  # true to use NV-CLIP instead of local CLIP
```

---

## 📊 Use Cases

### For Development

```python
# Code generation with best model
from model_router import ask_code

code = await ask_code("""
Write a Python async function that:
1. Fetches data from multiple APIs concurrently
2. Handles errors gracefully
3. Returns combined results
""")
```

### For Business Intelligence

```python
# Advanced reasoning with Nemotron
from nvidia_integration import ask_nemotron

analysis = await ask_nemotron("""
Analyze the business impact of implementing AI automation
in customer service operations. Consider ROI, customer
satisfaction, and operational efficiency.
""")
```

### For Visual Analysis

```python
# Screenshot analysis
from vision_system import analyze_image

result = await analyze_image(
    "error_screenshot.png",
    query="What error occurred and how to fix it?",
    labels=["critical", "warning", "info"]
)

print(f"Error type: {result['classification']}")
print(f"Error text: {result['ocr']['text']}")
```

### For Voice Interaction

```python
# Voice assistant
from voice_interface import VoiceInterface
from model_router import ask

voice = VoiceInterface()

# Listen
user_speech = await voice.listen("user_input.wav")

# Process
response_text = await ask(user_speech)

# Speak
await voice.speak(response_text, "response.wav")
```

### For Long-term Memory

```python
# Store knowledge
from rag_system import get_knowledge_base

kb = get_knowledge_base()

# Add from file
kb.ingest_file("documentation.md", category="docs")

# Query later
results = await kb.query_knowledge(
    "How do I configure the system?",
    category="docs"
)
```

---

## 🎯 Advanced Features

### Multi-Agent Workflows

**Scenario:** Complex research → code → review workflow

```python
from multi_agent import create_default_team

team = create_default_team()

workflow = [
    {
        'goal': 'Research async best practices in Python',
        'task_type': 'research',
        'assigned_agent': 'analyst'
    },
    {
        'goal': 'Implement async system based on research',
        'task_type': 'code',
        'assigned_agent': 'coder',
        'dependencies': ['task_0']
    },
    {
        'goal': 'Review code for issues',
        'task_type': 'review',
        'assigned_agent': 'coordinator',
        'dependencies': ['task_1']
    }
]

results = await team.run_workflow(workflow)
```

### RAG-Enhanced Responses

```python
from rag_system import get_knowledge_base
from model_router import get_router

kb = get_knowledge_base()
router = get_router()

# User query
query = "How do I configure CUDA for this system?"

# Retrieve relevant knowledge
docs = await kb.query_knowledge(query, n_results=3)

# Build context
context = "\n\n".join([doc['text'] for doc in docs])

# Generate response with context
result = await router.route_query(
    query=query,
    context=f"Reference documentation:\n{context}",
    task_type="technical"
)

print(result['response'])
```

---

## 🔒 Security & Privacy

### Local-First Architecture

- **All LLMs run locally** via LM Studio
- **No data sent to cloud** (except optional NVIDIA API)
- **No telemetry or tracking**
- **Full control over data**

### Optional Cloud Features

Only used if explicitly enabled:
- NVIDIA Nemotron (advanced reasoning)
- NVIDIA NV-CLIP (multimodal vision)

### API Security

```python
# Add authentication (example)
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/chat")
async def chat(request: ChatRequest, token: str = Depends(security)):
    # Verify token
    if not verify_token(token):
        raise HTTPException(401, "Invalid token")
    # Process request
    ...
```

---

## 📈 Performance Optimization

### Model Selection

- **Fast queries:** Use Llama 3.1 8B or Mistral 7B
- **Code generation:** Use Qwen 2.5 Coder 32B
- **Complex reasoning:** Use Nemotron 43B or Llama 3.3 70B
- **Vision:** Use NV-CLIP for cloud, local CLIP for offline

### Hardware Recommendations

**Budget Setup:**
- RTX 3090 (24GB) or RTX 4090 (24GB)
- 32GB system RAM
- SSD for model storage

**Enterprise Setup:**
- Dual RTX 4090 (48GB total)
- 64-128GB system RAM
- NVMe SSD array

**Datacenter:**
- NVIDIA A100 (80GB) or H100
- 256GB+ system RAM
- High-speed storage array

---

## 🆘 Troubleshooting

### Models not loading

```powershell
# Check LM Studio is running
curl http://localhost:1234/v1/models

# Verify models are loaded in LM Studio
```

### CUDA errors

```powershell
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### API not starting

```powershell
# Check port availability
netstat -an | findstr "8000"

# Try different port
set API_PORT=8080
python api_server.py
```

### ChromaDB errors

```powershell
# Clear database
rm -r chroma_db

# Reinstall
pip install --upgrade chromadb
```

---

## 📝 License

Copyright © 2025 AlphaEdge AINV. All Rights Reserved.

Licensed under MIT License with additional terms.
See [LICENSE](LICENSE) and [COPYRIGHT_NOTICE.md](COPYRIGHT_NOTICE.md).

**Trademarks:**
- Jareth2™
- AlphaEdge AINV™

---

## 🙏 Philosophy

> **"AI that works for you, not the other way around."**

AlphaEdge AINV is built on principles of:
- **Privacy:** Your data stays on your machine
- **Freedom:** No vendor lock-in, no quotas
- **Accessibility:** AI for everyone, regardless of abilities
- **Transparency:** Open architecture, inspectable code
- **Empowerment:** Full control, full capability

---

**AlphaEdge AINV: Enterprise AI, Your Way.** 🚀
