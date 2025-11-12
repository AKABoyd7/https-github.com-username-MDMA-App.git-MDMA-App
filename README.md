# AlphaEdge AINV MCP Server

**Enterprise-Grade Model Context Protocol Server for AI Integration**

A production-ready MCP server that exposes local AI models (LM Studio), NVIDIA APIs, GPU monitoring, and system tools through the Model Context Protocol, enabling Claude Desktop to control and interact with the entire AlphaEdge AINV ecosystem.

## 🚀 Features

- **🤖 Local AI Models** - Chat with Llama 3.3 70B, Qwen 2.5 Coder 32B, and Llama 3.1 8B via LM Studio
- **☁️ NVIDIA Cloud APIs** - Access NVIDIA Nemotron 70B, vision models, and NeMo Guardrails
- **🎮 GPU Monitoring** - Real-time NVIDIA GPU status, VRAM tracking, and process monitoring
- **🛠️ System Tools** - Safe file operations and command execution with comprehensive safety guards
- **🔮 Memory Integration** - Placeholder for future ChromaDB/RAG implementation
- **🔒 Security First** - Sandboxed execution, path validation, command whitelisting
- **📊 Health Monitoring** - Server status, performance metrics, and logging

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## 🎯 Prerequisites

### Required

- **Windows 10/11** (Primary target platform)
- **Python 3.10 or higher**
- **NVIDIA GPU** with updated drivers (for GPU monitoring and local models)
- **LM Studio** installed and running ([Download](https://lmstudio.ai/))
- **NVIDIA API Key** (Optional, from [NVIDIA Enterprise Program](https://build.nvidia.com/))

### Recommended

- 16GB+ RAM
- 24GB+ VRAM (for running large models locally)
- SSD storage

## 📦 Installation

### Automated Setup

1. **Clone or download this repository to `G:\AlphaEdge_AINV`:**

```powershell
# Create directory
mkdir G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV

# If using Git
git clone <repository-url> .
```

2. **Run the automated setup script:**

```powershell
python setup.py
```

The setup script will:
- ✅ Check Python version
- ✅ Detect NVIDIA GPU
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Setup environment configuration
- ✅ Create necessary directories
- ✅ Display Claude Desktop configuration

### Manual Setup

If you prefer manual installation:

1. **Create virtual environment:**

```powershell
cd G:\AlphaEdge_AINV
python -m venv venv
```

2. **Activate virtual environment:**

```powershell
G:\AlphaEdge_AINV\venv\Scripts\activate
```

3. **Install dependencies:**

```powershell
pip install -r requirements.txt
```

4. **Configure environment:**

```powershell
copy .env.template .env
# Edit .env with your settings
```

## ⚙️ Configuration

### Environment Variables

Edit `G:\AlphaEdge_AINV\.env`:

```env
# NVIDIA API (Optional but recommended)
NVIDIA_API_KEY=nvapi-your-key-here

# LM Studio
LM_STUDIO_URL=http://localhost:1234/v1
LM_STUDIO_TIMEOUT=120

# Server
SERVER_PORT=8000
SERVER_HOST=localhost
DEBUG_MODE=false

# Paths
PROJECT_ROOT=G:\AlphaEdge_AINV
WORKSPACE_DIR=G:\AlphaEdge_AINV\workspace

# Safety Limits
MAX_FILE_SIZE_MB=10
COMMAND_TIMEOUT=30
PYTHON_MEMORY_LIMIT_GB=1
```

### LM Studio Setup

1. **Download and install LM Studio** from [lmstudio.ai](https://lmstudio.ai/)
2. **Download recommended models:**
   - Llama 3.3 70B Instruct (for complex reasoning, Thai language)
   - Qwen 2.5 Coder 32B Instruct (for programming tasks)
   - Llama 3.1 8B Instruct (for quick responses)
3. **Start LM Studio server:**
   - Open LM Studio
   - Go to "Local Server" tab
   - Click "Start Server"
   - Verify it's running at `http://localhost:1234`

### NVIDIA API Setup

1. **Get API Key:**
   - Visit [NVIDIA API Catalog](https://build.nvidia.com/)
   - Sign up for Enterprise Developer Program
   - Generate API key
2. **Add to `.env`:**
   ```env
   NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx
   ```

## 🚀 Usage

### Starting the Server

```powershell
cd G:\AlphaEdge_AINV\mcp_server
..\venv\Scripts\python.exe server.py
```

You should see:

```
======================================================================
          Starting AlphaEdge AINV MCP Server v1.0.0
======================================================================
[INFO] Project Root: G:\AlphaEdge_AINV
[INFO] LM Studio URL: http://localhost:1234/v1
[INFO] NVIDIA API: Enabled
[INFO] Tools Registered: 28
======================================================================
Available Tools:
   1. chat_llama33              - Chat with Llama 3.3 70B Instruct...
   2. chat_qwen                 - Chat with Qwen 2.5 Coder 32B...
   ...
======================================================================
Server ready! Waiting for MCP connections...
```

### Testing the Server

Test individual tools:

```python
# Example: Test local model
from mcp_server.tools.local_models import chat_llama33

result = chat_llama33(
    prompt="Explain quantum computing in simple terms",
    temperature=0.7,
    max_tokens=500
)
print(result['response'])
```

## 🛠️ Available Tools

### 📚 Local Models (7 Tools)

#### 1. `chat_llama33`
Chat with Llama 3.3 70B Instruct for complex reasoning and Thai language support.

**Parameters:**
- `prompt` (required): User message
- `temperature` (0.0-2.0): Sampling temperature (default: 0.7)
- `max_tokens` (1-32000): Maximum tokens (default: 2000)
- `stream` (boolean): Enable streaming (default: false)
- `system_prompt` (optional): System prompt

**Example:**
```json
{
  "prompt": "Explain the theory of relativity",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Returns:**
```json
{
  "response": "...",
  "model": "llama-3.3-70b-instruct",
  "tokens_used": 850,
  "execution_time": 12.5
}
```

#### 2. `chat_qwen`
Chat with Qwen 2.5 Coder 32B for programming tasks.

**Best for:** Code generation, debugging, documentation

#### 3. `chat_llama31`
Chat with Llama 3.1 8B for quick responses.

**Best for:** Fast queries, simple tasks (typically <2s response time)

#### 4. `list_local_models`
List all available models in LM Studio.

**Returns:**
```json
{
  "models": [
    {
      "model_name": "llama-3.3-70b-instruct",
      "description": "Complex reasoning and Thai language",
      "status": "available"
    }
  ]
}
```

#### 5. `load_model`
Load a specific model into GPU memory.

**Parameters:**
- `model_name` (required): Model to load
- `gpu_layers` (optional): GPU layers to offload

#### 6. `unload_model`
Unload a model to free VRAM.

#### 7. `model_status`
Get detailed status of all models including VRAM usage.

### ☁️ NVIDIA API (4 Tools)

#### 8. `chat_nemotron`
Chat with NVIDIA Nemotron 70B for ultra-complex reasoning.

**Features:**
- Automatic fallback to local Llama 3.3 if API unavailable
- Advanced reasoning capabilities
- Enterprise-grade performance

**Parameters:**
- `prompt` (required): User prompt
- `temperature` (0.0-2.0): Default 0.7
- `max_tokens`: Default 2000
- `fallback_to_local` (boolean): Enable fallback (default: true)

#### 9. `analyze_image`
Understand images using NVIDIA vision models.

**Supported formats:**
- Image URL (`https://...`)
- Base64 encoded image (`data:image/jpeg;base64,...`)
- Local file path (`G:\AlphaEdge_AINV\images\photo.jpg`)

**Parameters:**
- `image_source` (required): Image URL, base64, or file path
- `prompt` (optional): Specific analysis prompt
- `max_tokens`: Default 1000

**Returns:**
```json
{
  "description": "A modern office with...",
  "objects": ["computer", "desk", "chair"],
  "text_extracted": "Welcome sign visible",
  "confidence": 0.95
}
```

#### 10. `check_nvidia_quota`
Check NVIDIA API usage and remaining quota.

#### 11. `nvidia_guardrails`
Content safety check for jailbreak attempts, PII, toxic content.

**Check types:**
- `jailbreak`: Prompt injection attempts
- `pii`: Personal information detection
- `toxicity`: Harmful content
- `hallucination`: Factual accuracy

### 🎮 GPU Monitoring (5 Tools)

#### 12. `gpu_status`
Get comprehensive GPU status.

**Returns:**
```json
{
  "gpu_name": "NVIDIA GeForce RTX 3090",
  "driver_version": "560.94",
  "cuda_version": "12.6",
  "utilization": {
    "gpu": 75,
    "memory": 85
  },
  "memory": {
    "total_gb": 24.0,
    "used_gb": 20.4,
    "free_gb": 3.6
  },
  "temperature": 72,
  "power_usage": 350,
  "fan_speed": 65,
  "clocks": {
    "core_mhz": 1950,
    "memory_mhz": 9751
  }
}
```

#### 13. `gpu_processes`
List all processes using GPU with memory usage.

#### 14. `vram_monitor`
Real-time VRAM monitoring with alert levels.

**Alert levels:**
- `ok`: <90% usage
- `warning`: 90-95% usage
- `critical`: >95% usage

#### 15. `cuda_info`
Get CUDA environment information.

**Returns:**
```json
{
  "cuda_version": "12.6",
  "num_gpus": 1,
  "architecture": "Ampere",
  "compute_capability": "8.6"
}
```

#### 16. `benchmark_gpu`
Run quick GPU benchmark (FP32/FP16 performance).

### 🖥️ System Tools (8 Tools)

#### 17. `execute_powershell`
Execute PowerShell commands (sandboxed with whitelist).

**Safety features:**
- Only whitelisted cmdlets allowed (`Get-*`, `Test-*`, etc.)
- Blocked: `Remove-*`, `Delete`, `Format-*`, `Invoke-*`
- Restricted to project directory
- 30-second timeout

**Example:**
```json
{
  "command": "Get-ChildItem *.py | Select-Object Name, Length"
}
```

#### 18. `execute_python`
Execute Python code in isolated sandbox.

**Safety features:**
- Restricted built-ins only
- No dangerous imports (`subprocess`, `os.system`, etc.)
- Memory limit: 1GB
- Timeout: 30 seconds
- No file/network access

#### 19. `read_file`
Read file contents (restricted to project directory).

**Features:**
- Auto-encoding detection (UTF-8, UTF-16, Latin-1)
- Max size: 10MB
- Path validation

#### 20. `write_file`
Write content to file.

**Features:**
- Automatic backup creation
- Parent directory creation
- Path validation

#### 21. `list_files`
List files and directories with pattern matching.

**Parameters:**
- `path`: Directory path
- `pattern`: Glob pattern (default: `*`)
- `recursive`: Recursive listing (default: false)

#### 22. `search_files`
Search files by name, content, or extension.

**Search types:**
- `filename`: Search by name (glob matching)
- `content`: Search file contents (regex)
- `extension`: Search by extension

#### 23. `get_file_info`
Get detailed file metadata including MD5 hash.

#### 24. `create_directory`
Create directory structure (recursive).

### 🧠 Memory/Knowledge (2 Tools - Placeholders)

#### 25. `search_memory`
Search semantic memory (future ChromaDB integration).

**Status:** Placeholder for future RAG implementation

**Planned features:**
- ChromaDB vector database
- Semantic search with embeddings
- Document chunking and indexing
- Conversation history storage

#### 26. `add_to_memory`
Add information to long-term memory (future).

**Status:** Placeholder for future implementation

### ⚙️ Server Management (3 Tools)

#### 27. `get_server_status`
Get MCP server health and statistics.

**Returns:**
```json
{
  "uptime_seconds": 3600,
  "active_connections": 1,
  "total_requests": 150,
  "error_count": 2,
  "tools_registered": 28,
  "lm_studio_status": "connected",
  "nvidia_api_status": "connected"
}
```

#### 28. `get_config`
Get current server configuration.

#### 29. `reload_config`
Reload configuration from `.env` file.

## 🖥️ Claude Desktop Integration

### Setup Configuration

1. **Locate Claude Desktop config file:**

Windows: `%APPDATA%\Roaming\Claude\claude_desktop_config.json`

2. **Add MCP server configuration:**

```json
{
  "mcpServers": {
    "alphaedge-ainv": {
      "command": "G:\\AlphaEdge_AINV\\venv\\Scripts\\python.exe",
      "args": ["G:\\AlphaEdge_AINV\\mcp_server\\server.py"],
      "env": {
        "NVIDIA_API_KEY": "nvapi-xxxxx",
        "LM_STUDIO_URL": "http://localhost:1234/v1",
        "PROJECT_ROOT": "G:\\AlphaEdge_AINV"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Verify connection:**
   - Open Claude Desktop
   - Look for MCP server indicator
   - Try: "List available local models"

### Example Conversations

**Using Local Models:**
```
User: Use Llama 3.3 to explain quantum computing in Thai

Claude: I'll use the chat_llama33 tool...
[Calls chat_llama33 with Thai language request]
```

**GPU Monitoring:**
```
User: Check my GPU status and memory usage

Claude: Let me check your GPU...
[Calls gpu_status and vram_monitor]

Your RTX 3090 is running at 72°C with 20.4GB/24GB VRAM used (85%).
GPU utilization is 75%. Alert level: Normal.
```

**File Operations:**
```
User: Search for all Python files containing "async def"

Claude: I'll search for that...
[Calls search_files with query="async def", search_type="content"]

Found 15 files containing "async def"...
```

## 🔧 Troubleshooting

### Common Issues

#### LM Studio Not Connected

**Symptoms:** `lm_studio_status: "disconnected"`

**Solutions:**
1. Verify LM Studio is running
2. Check server is at `http://localhost:1234`
3. Test with: `curl http://localhost:1234/v1/models`
4. Check firewall settings

#### GPU Not Detected

**Symptoms:** GPU tools return "No NVIDIA GPU available"

**Solutions:**
1. Update NVIDIA drivers: [NVIDIA Drivers](https://www.nvidia.com/download/index.aspx)
2. Verify with: `nvidia-smi`
3. Check CUDA is installed
4. Reinstall `nvidia-ml-py`: `pip install --upgrade nvidia-ml-py`

#### NVIDIA API Authentication Failed

**Symptoms:** `nvidia_api_status: "disconnected"`

**Solutions:**
1. Verify API key in `.env` file
2. Check key format: `nvapi-xxxxx...`
3. Test API: [NVIDIA API Playground](https://build.nvidia.com/)
4. Check quota hasn't been exceeded

#### Import Errors

**Symptoms:** `ModuleNotFoundError: No module named 'mcp'`

**Solutions:**
1. Activate virtual environment:
   ```powershell
   G:\AlphaEdge_AINV\venv\Scripts\activate
   ```
2. Reinstall dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

#### Permission Errors

**Symptoms:** File operations fail with permission errors

**Solutions:**
1. Run as Administrator (if needed)
2. Check file paths are within `G:\AlphaEdge_AINV`
3. Verify `.env` has correct `PROJECT_ROOT`

### Logging

Logs are written to: `G:\AlphaEdge_AINV\mcp_server.log`

Enable debug mode in `.env`:
```env
DEBUG_MODE=true
```

View logs in real-time:
```powershell
Get-Content G:\AlphaEdge_AINV\mcp_server.log -Wait -Tail 50
```

## 🧪 Development

### Running Tests

```powershell
# Activate virtual environment
G:\AlphaEdge_AINV\venv\Scripts\activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_local_models.py

# Run with coverage
pytest --cov=mcp_server tests/
```

### Code Quality

```powershell
# Format code
black mcp_server/

# Lint
flake8 mcp_server/

# Type checking
mypy mcp_server/
```

### Project Structure

```
G:\AlphaEdge_AINV
├── mcp_server/
│   ├── server.py           # Main MCP server
│   ├── config.py           # Configuration management
│   ├── utils.py            # Utilities
│   ├── safety.py           # Safety guards
│   ├── tools/
│   │   ├── local_models.py # LM Studio integration (7 tools)
│   │   ├── nvidia_api.py   # NVIDIA APIs (4 tools)
│   │   ├── gpu_monitor.py  # GPU monitoring (5 tools)
│   │   ├── system.py       # System tools (8 tools)
│   │   └── memory.py       # Memory tools (2 placeholders)
│   └── schemas/
│       └── tool_schemas.py # Pydantic schemas
├── tests/                  # Test files
├── workspace/              # Safe workspace directory
├── .env                    # Environment configuration
├── .env.template           # Environment template
├── requirements.txt        # Python dependencies
├── setup.py               # Setup automation
├── config.json            # Claude Desktop config
└── README.md              # This file
```

## 📊 Performance

### Typical Response Times

| Tool | Response Time | Notes |
|------|--------------|-------|
| `chat_llama31` | 1-3s | Lightweight 8B model |
| `chat_qwen` | 3-8s | 32B model, optimized for code |
| `chat_llama33` | 10-20s | 70B model, high quality |
| `chat_nemotron` | 5-15s | Cloud API, depends on network |
| `gpu_status` | <0.1s | Direct NVML access |
| `file operations` | <0.5s | Depends on file size |

### Resource Usage

- **RAM:** ~2-4GB (server + Python)
- **VRAM:** Depends on loaded models
  - Llama 3.1 8B: ~8GB
  - Qwen 2.5 32B: ~20GB
  - Llama 3.3 70B: ~40GB (quantized)

## 🔒 Security

### Safety Features

1. **Path Validation:** All file operations restricted to `G:\AlphaEdge_AINV`
2. **Command Whitelisting:** Only safe PowerShell cmdlets allowed
3. **Python Sandboxing:** Restricted built-ins, no dangerous imports
4. **Input Validation:** Pydantic schemas validate all inputs
5. **Rate Limiting:** Built-in protection for API calls
6. **Error Sanitization:** Sensitive info removed from error messages

### Best Practices

- Keep NVIDIA API key secure in `.env`
- Don't commit `.env` to version control
- Review logs regularly for suspicious activity
- Update dependencies regularly: `pip install -r requirements.txt --upgrade`

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **Anthropic** - MCP Protocol and Claude
- **LM Studio** - Local model hosting
- **NVIDIA** - GPU APIs and drivers
- **Python Community** - Amazing libraries

## 📞 Support

- **Issues:** [GitHub Issues](your-repo-url/issues)
- **Discussions:** [GitHub Discussions](your-repo-url/discussions)
- **Email:** your-email@example.com

---

**AlphaEdge AINV MCP Server** - Enterprise AI Integration Made Simple

Built with ❤️ for the AI community
