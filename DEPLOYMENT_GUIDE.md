# AlphaEdge AINV MCP Server - Deployment Guide

## 🎯 Quick Start for Windows Deployment

### Step 1: Clone to Target Location

```powershell
# Create target directory
mkdir G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV

# Clone this repository
git clone <your-repo-url> .
```

### Step 2: Run Automated Setup

```powershell
python setup.py
```

This will:
- ✅ Check Python 3.10+ is installed
- ✅ Detect NVIDIA GPU
- ✅ Create virtual environment at `G:\AlphaEdge_AINV\venv`
- ✅ Install all dependencies
- ✅ Setup `.env` file from template
- ✅ Create necessary directories
- ✅ Display Claude Desktop configuration

### Step 3: Configure Environment

Edit `G:\AlphaEdge_AINV\.env`:

```env
# Add your NVIDIA API key (get from https://build.nvidia.com/)
NVIDIA_API_KEY=nvapi-your-actual-key-here

# Verify LM Studio URL
LM_STUDIO_URL=http://localhost:1234/v1
```

### Step 4: Setup LM Studio

1. Download and install LM Studio from https://lmstudio.ai/
2. Download recommended models:
   - **Llama 3.3 70B Instruct** (complex reasoning, Thai language)
   - **Qwen 2.5 Coder 32B Instruct** (programming tasks)
   - **Llama 3.1 8B Instruct** (quick responses)
3. Start LM Studio server (Local Server tab → Start Server)

### Step 5: Configure Claude Desktop

Add to `%APPDATA%\Roaming\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "alphaedge-ainv": {
      "command": "G:\\AlphaEdge_AINV\\venv\\Scripts\\python.exe",
      "args": ["G:\\AlphaEdge_AINV\\mcp_server\\server.py"],
      "env": {
        "NVIDIA_API_KEY": "nvapi-your-key-here",
        "LM_STUDIO_URL": "http://localhost:1234/v1"
      }
    }
  }
}
```

### Step 6: Start the Server

```powershell
cd G:\AlphaEdge_AINV\mcp_server
..\venv\Scripts\python.exe server.py
```

You should see:
```
======================================================================
          Starting AlphaEdge AINV MCP Server v1.0.0
======================================================================
[INFO] Tools Registered: 28
[INFO] LM Studio: connected
[INFO] NVIDIA API: enabled
======================================================================
Server ready! Waiting for MCP connections...
```

### Step 7: Test with Claude Desktop

1. **Restart Claude Desktop**
2. **Verify connection** - Look for MCP server indicator
3. **Test commands:**

```
"List available local models"
"Check my GPU status"
"Use Llama 3.3 to explain quantum computing"
"Analyze this image: [image URL]"
"Search for Python files containing 'async def'"
```

## 📊 What You Get

### 28+ Production-Ready Tools

#### 🤖 Local Models (7 tools)
- Chat with Llama 3.3 70B, Qwen 32B, Llama 3.1 8B
- Model management and status monitoring

#### ☁️ NVIDIA API (4 tools)
- Nemotron 70B with automatic local fallback
- Image analysis with vision models
- API quota monitoring
- Content safety guardrails

#### 🎮 GPU Monitoring (5 tools)
- Real-time GPU status (utilization, memory, temperature)
- Process monitoring
- VRAM alerts (ok/warning/critical)
- CUDA environment info
- Performance benchmarking

#### 🛠️ System Tools (8 tools)
- Safe PowerShell execution (whitelisted)
- Sandboxed Python execution
- File operations (read/write/search)
- Directory management

#### 🧠 Memory (2 placeholder tools)
- Future ChromaDB/RAG integration

#### ⚙️ Server Management (3 tools)
- Health monitoring
- Configuration management
- Status reporting

## 🔒 Security Features

- **Path Validation:** All operations restricted to `G:\AlphaEdge_AINV`
- **Command Whitelisting:** Only safe PowerShell cmdlets
- **Python Sandboxing:** Restricted built-ins, no dangerous imports
- **Input Validation:** Pydantic schemas validate all inputs
- **File Safety:** Size limits, extension filtering
- **Error Sanitization:** No sensitive data in errors

## 🧪 Testing

```powershell
# Activate virtual environment
G:\AlphaEdge_AINV\venv\Scripts\activate

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=mcp_server tests/

# Run specific test suite
pytest tests/test_local_models.py -v
```

## 📁 File Structure

```
G:\AlphaEdge_AINV
├── mcp_server/              # Main server package
│   ├── server.py           # MCP server entry point
│   ├── config.py           # Configuration management
│   ├── utils.py            # Utilities and helpers
│   ├── safety.py           # Security guards
│   ├── tools/              # Tool implementations
│   │   ├── local_models.py    # LM Studio (7 tools)
│   │   ├── nvidia_api.py      # NVIDIA APIs (4 tools)
│   │   ├── gpu_monitor.py     # GPU monitoring (5 tools)
│   │   ├── system.py          # System tools (8 tools)
│   │   └── memory.py          # Memory (2 placeholders)
│   └── schemas/            # Pydantic validation
│       └── tool_schemas.py
├── tests/                  # Test suite
├── workspace/              # Safe workspace
├── venv/                   # Virtual environment
├── .env                    # Configuration (gitignored)
├── .env.template          # Configuration template
├── requirements.txt       # Dependencies
├── setup.py              # Automated setup
├── config.json           # Claude Desktop config
└── README.md             # Full documentation
```

## 🔧 Troubleshooting

### LM Studio Not Connected
```powershell
# Test connection
curl http://localhost:1234/v1/models

# Check if LM Studio is running
Get-Process | Where-Object {$_.Name -like "*lm*"}
```

### GPU Not Detected
```powershell
# Check NVIDIA driver
nvidia-smi

# Update drivers from: https://www.nvidia.com/download/index.aspx
```

### Import Errors
```powershell
# Ensure virtual environment is activated
G:\AlphaEdge_AINV\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Issues
- Run PowerShell as Administrator
- Verify all paths point to `G:\AlphaEdge_AINV`
- Check file permissions on project directory

## 📈 Performance Tips

1. **Model Selection:**
   - Use Llama 3.1 8B for quick queries (<2s)
   - Use Qwen 32B for code tasks (3-8s)
   - Use Llama 3.3 70B for complex reasoning (10-20s)

2. **VRAM Management:**
   - Monitor with `vram_monitor` tool
   - Unload unused models
   - Keep usage below 90% for stability

3. **API Usage:**
   - Nemotron falls back to local automatically
   - Check quota with `check_nvidia_quota`
   - Local models = no API costs

## 🚀 Next Steps

1. **Customize:** Edit `.env` for your setup
2. **Extend:** Add new tools in `mcp_server/tools/`
3. **Monitor:** Check `mcp_server.log` for issues
4. **Optimize:** Adjust model selection based on use case

## 📚 Resources

- **Full Documentation:** README.md
- **MCP Protocol:** https://modelcontextprotocol.io/
- **LM Studio:** https://lmstudio.ai/
- **NVIDIA API:** https://build.nvidia.com/
- **Claude Desktop:** https://claude.ai/

## 🎓 Example Use Cases

### Code Development
```
User: "Use Qwen to refactor this Python function to use async/await"
Claude: [Uses chat_qwen to generate async code]
```

### Research & Analysis
```
User: "Use Nemotron to analyze this research paper and summarize key findings"
Claude: [Uses chat_nemotron for deep analysis]
```

### System Monitoring
```
User: "Check GPU status and list processes using VRAM"
Claude: [Uses gpu_status and gpu_processes]
```

### File Operations
```
User: "Search all Python files for TODO comments and list them"
Claude: [Uses search_files with content search]
```

---

**AlphaEdge AINV MCP Server** - Your AI Integration Hub

Built for production. Secured by design. Ready to deploy.
