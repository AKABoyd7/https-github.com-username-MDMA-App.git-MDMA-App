# Project Jareth v1

> Advanced Conversational AI System with Memory Management

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Langgraph](https://img.shields.io/badge/Langgraph-0.0.30+-purple.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Codename**: MDMA App (Memory-Driven Multi-Agent Application)

## 🚀 Features

- ✅ **RESTful API** - FastAPI-based web server
- ✅ **Conversational Memory** - Langgraph state management
- ✅ **Multi-user Support** - Isolated conversation threads
- ✅ **GPU Acceleration** - CUDA support for fast inference
- ✅ **Health Monitoring** - Auto-healing and system monitoring
- ✅ **Network Utilities** - Built-in network repair tools
- ✅ **Production Ready** - Scalable architecture

## 📋 Prerequisites

### Required

- **Python 3.8+**
- **Ollama** - Local LLM server ([Download](https://ollama.ai))
- **CUDA** (Optional) - For GPU acceleration

### Ollama Models

Download the required model:

```bash
# Option 1: Llama 3.3 70B (Recommended)
ollama pull llama3.3:70b

# Option 2: Llama 3 (Fallback)
ollama pull llama3
```

## 🔧 Installation

### Windows (PowerShell)

```powershell
# Clone the repository
git clone <repository-url>
cd MDMA-App

# Run the launcher (handles everything)
./run.ps1
```

### Linux/Mac

```bash
# Clone the repository
git clone <repository-url>
cd MDMA-App

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

## 🎯 Quick Start

### 1. Start the Server

```powershell
./run.ps1
```

The server will start on `http://localhost:8500`

### 2. Check Health

```bash
curl http://localhost:8500/health
```

Response:
```json
{
  "status": "healthy",
  "mode": "local",
  "model": "Meta Llama-3.3-70B-Instruct",
  "gpu": "NVIDIA RTX 3090 Ti",
  "cpu_usage": 15.2,
  "ram_usage": 45.3
}
```

### 3. Start Chatting

```bash
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, who are you?",
    "thread_id": "user-123"
  }'
```

Response:
```json
{
  "response": "I am Jareth AiNV, an advanced AI assistant...",
  "thread_id": "user-123",
  "timestamp": "2025-11-12T10:30:00"
}
```

## 📚 API Documentation

### Interactive Docs

Visit `http://localhost:8500/docs` for interactive API documentation (Swagger UI)

### Endpoints

#### 🏠 Root

```
GET /
```

Returns API information and available endpoints.

#### 💚 Health Check

```
GET /health
```

Returns system status, GPU info, CPU/RAM usage.

#### 💬 Chat (with Memory!)

```
POST /chat
```

**Request Body:**
```json
{
  "message": "Your message here",
  "thread_id": "optional-thread-id"
}
```

**Response:**
```json
{
  "response": "AI response",
  "thread_id": "thread-id",
  "timestamp": "ISO-8601 timestamp"
}
```

**Features:**
- Automatic thread creation if `thread_id` not provided
- Conversation memory across requests
- Context-aware responses

#### 📜 Get Conversation History

```
GET /conversation/{thread_id}
```

**Response:**
```json
{
  "thread_id": "user-123",
  "messages": [
    {
      "role": "system",
      "content": "You are Jareth AiNV..."
    },
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "Hi there!"
    }
  ],
  "message_count": 3
}
```

#### 🗑️ Clear Conversation

```
DELETE /conversation/{thread_id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation user-123 cleared",
  "thread_id": "user-123"
}
```

#### 🔧 Network Repair (Windows Only)

```
POST /repair_network
```

Executes:
- `ipconfig /flushdns`
- `netsh winsock reset`
- `netsh int ip reset`

## 🏗️ Architecture

### Hybrid Design

```
┌─────────────────────────────────────┐
│      FastAPI REST Server            │
│         (Port 8500)                 │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐  │
│  │   Langgraph State Manager    │  │
│  │   - Conversation Memory      │  │
│  │   - Multi-thread Support     │  │
│  │   - Context Awareness        │  │
│  └──────────────────────────────┘  │
├─────────────────────────────────────┤
│  Ollama Backend (Llama 3.3 70B)    │
│     http://localhost:11434          │
└─────────────────────────────────────┘
```

### Key Components

1. **FastAPI Server** - REST API interface
2. **Langgraph** - Conversation state management
3. **Ollama** - Local LLM inference
4. **MemorySaver** - Conversation persistence
5. **Auto-Monitor** - Background health monitoring

## 📖 Usage Examples

### Python Client

```python
import requests

API_BASE = "http://localhost:8500"

# Start a conversation
response = requests.post(f"{API_BASE}/chat", json={
    "message": "Explain quantum computing in simple terms",
    "thread_id": "quantum-discussion"
})

data = response.json()
print(f"AI: {data['response']}")

# Continue the conversation
response = requests.post(f"{API_BASE}/chat", json={
    "message": "Can you give me an example?",
    "thread_id": "quantum-discussion"  # Same thread = remembers context
})

data = response.json()
print(f"AI: {data['response']}")

# Get full conversation history
history = requests.get(f"{API_BASE}/conversation/quantum-discussion")
print(history.json())
```

### JavaScript Client

```javascript
const API_BASE = "http://localhost:8500";

async function chat(message, threadId = null) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, thread_id: threadId })
  });

  return await response.json();
}

// Usage
const result = await chat("Hello!", "my-thread");
console.log(result.response);
```

### cURL Examples

```bash
# Health check
curl http://localhost:8500/health

# Chat
curl -X POST http://localhost:8500/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a joke", "thread_id": "jokes-thread"}'

# Get conversation
curl http://localhost:8500/conversation/jokes-thread

# Clear conversation
curl -X DELETE http://localhost:8500/conversation/jokes-thread
```

## ⚙️ Configuration

Edit `config_local.yml`:

```yaml
# AI Model
model: meta-llama-3.3-70b-instruct

# GPU Settings
gpu_backend: cuda
device: "NVIDIA RTX 3090 Ti"

# Auto-healing
auto_heal: true
heal_cpu_threshold: 90
heal_memory_threshold: 90

# API Server
api_host: "0.0.0.0"
api_port: 8500

# Ollama
ollama_host: "http://localhost:11434"
ollama_timeout: 60
```

## 🔍 Monitoring

### Auto-Healing

The system automatically monitors:
- CPU usage (threshold: 90%)
- RAM usage (threshold: 90%)

When thresholds are exceeded, auto-healing triggers cleanup.

### Health Endpoint

Monitor system health:

```bash
watch -n 5 'curl -s http://localhost:8500/health | jq'
```

## 🛠️ Troubleshooting

### Issue: "Failed to connect to Ollama"

**Solution:**
1. Check Ollama is running: `ollama list`
2. Start Ollama: `ollama serve`
3. Pull model: `ollama pull llama3.3:70b`

### Issue: "No GPU detected"

**Solution:**
1. Install CUDA-enabled PyTorch:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```
2. Verify CUDA: `nvidia-smi`

### Issue: Port 8500 already in use

**Solution:**
Change port in `config_local.yml`:
```yaml
api_port: 8501  # Use different port
```

## 📁 Project Structure

```
MDMA-App/
├── main.py                 # FastAPI + Langgraph application
├── agent.py                # Legacy CLI version (v1)
├── requirements.txt        # Python dependencies
├── config_local.yml        # Configuration
├── run.ps1                 # PowerShell launcher
├── DESIGN.md              # Architecture documentation
└── README.md              # This file
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Langgraph](https://github.com/langchain-ai/langgraph) - State management
- [Ollama](https://ollama.ai) - Local LLM inference
- [Meta](https://ai.meta.com/) - Llama models

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the [DESIGN.md](DESIGN.md) for architecture details
- Visit API docs at `http://localhost:8500/docs`

---

**Project Jareth v1** - Built with ❤️ using FastAPI & Langgraph

*Last Updated: 2025-11-12*
