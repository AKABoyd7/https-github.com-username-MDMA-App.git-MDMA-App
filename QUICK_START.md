# 🚀 Jareth_AINV - Quick Start Guide

## Installation in 5 Minutes

### Step 1: Open PowerShell as Administrator

```powershell
# Right-click PowerShell and select "Run as Administrator"
```

### Step 2: Download and Run Installation Script

```powershell
# Option A: Clone from Git
git clone -b claude/alphaedge-mcp-server-011CV477Fds3K8XrtkujexEt https://github.com/AKABoyd7/https-github.com-username-MDMA-App.git-MDMA-App G:\AlphaEdge_AINV

cd G:\AlphaEdge_AINV

# Run installer
.\install_jareth.ps1

# Option B: Manual Installation
# Download files manually to G:\AlphaEdge_AINV, then run:
.\install_jareth.ps1
```

### Step 3: Configure API Keys (Optional)

```powershell
# Edit .env file
notepad G:\AlphaEdge_AINV\.env

# Add your NVIDIA API key (get from https://build.nvidia.com/)
NVIDIA_API_KEY=nvapi-your-key-here
```

### Step 4: Start LM Studio

1. Download LM Studio from https://lmstudio.ai/
2. Download models:
   - Llama 3.3 70B Instruct
   - Qwen 2.5 Coder 32B Instruct
   - Llama 3.1 8B Instruct
3. Go to "Local Server" tab
4. Click "Start Server"
5. Verify running at http://localhost:1234

### Step 5: Start Jareth Server

```powershell
# Double-click the desktop shortcut "Jareth AINV"
# OR
cd G:\AlphaEdge_AINV
.\START_JARETH_SERVER.bat
```

You should see:
```
======================================================================
          Starting Jareth_AINV MCP Server v1.0.0
======================================================================
[INFO] Tools Registered: 42
[INFO] LM Studio: connected
[INFO] NVIDIA API: enabled
[INFO] GPU: NVIDIA GeForce RTX 3090
======================================================================
Server ready! Waiting for MCP connections...
```

### Step 6: Connect Claude Desktop

1. Open Claude Desktop config:
   - Location: `%APPDATA%\Roaming\Claude\claude_desktop_config.json`

2. Add Jareth server:
```json
{
  "mcpServers": {
    "jareth-ainv": {
      "command": "G:\\AlphaEdge_AINV\\venv\\Scripts\\python.exe",
      "args": ["G:\\AlphaEdge_AINV\\mcp_server\\server.py"],
      "env": {
        "NVIDIA_API_KEY": "your-api-key-here",
        "LM_STUDIO_URL": "http://localhost:1234/v1"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Look for MCP server indicator (should show "jareth-ainv" connected)

---

## ✅ Test Your Installation

Try these commands in Claude Desktop:

### Test Local Models
```
"List available local models"
"Use Llama 3.3 to explain quantum computing in simple terms"
"Use Qwen to write a Python function that calculates fibonacci numbers"
```

### Test GPU Monitoring
```
"Check my GPU status"
"Show GPU temperature and VRAM usage"
"List processes using GPU"
```

### Test Windows Management
```
"Show top 10 processes by memory usage"
"List all running Windows services"
"Get system information"
"Show active network connections"
```

### Test System Tools
```
"List all Python files in the current directory"
"Search for 'TODO' in all files"
"Read the README.md file"
```

---

## 🎯 What You Can Do Now

### 1. **Process Management**
- "Kill process with PID 1234"
- "Show all Chrome processes"
- "Suspend process 5678"
- "Resume process 5678"

### 2. **Service Control**
- "Is Windows Update running?"
- "Start the Windows Update service"
- "List all stopped services"

### 3. **AI Chat**
- "Use Llama 3.3 to write a blog post about AI"
- "Use Qwen to debug this code: [paste code]"
- "Use Nemotron for complex reasoning about [topic]"

### 4. **Image Analysis**
- "Analyze this image: https://example.com/image.jpg"
- "What's in this screenshot?"

### 5. **System Monitoring**
- "What's my CPU and memory usage?"
- "Show disk space on all drives"
- "Check network statistics"

### 6. **File Operations**
- "Search for all .py files containing 'async'"
- "Create a new directory called 'projects'"
- "Read the contents of config.json"

### 7. **Network Diagnostics**
- "Show all TCP connections"
- "What process is using port 8080?"
- "Show network adapter statistics"

### 8. **Registry Operations**
- "Read Windows version from registry"
- "Check registry value for [path]"

---

## 🔧 Troubleshooting

### Server Won't Start

**Check Python:**
```powershell
python --version  # Should be 3.10+
```

**Check Virtual Environment:**
```powershell
G:\AlphaEdge_AINV\venv\Scripts\python.exe --version
```

**Check Dependencies:**
```powershell
cd G:\AlphaEdge_AINV
.\venv\Scripts\pip.exe install -r requirements.txt
```

### LM Studio Not Connected

```powershell
# Test LM Studio endpoint
curl http://localhost:1234/v1/models
```

If fails:
1. Open LM Studio
2. Go to "Local Server" tab
3. Click "Start Server"
4. Verify port is 1234

### GPU Not Detected

```powershell
# Check NVIDIA driver
nvidia-smi
```

If fails:
1. Update NVIDIA drivers from https://www.nvidia.com/download/index.aspx
2. Restart computer
3. Run nvidia-smi again

### Claude Desktop Not Connecting

1. Verify config file location: `%APPDATA%\Roaming\Claude\claude_desktop_config.json`
2. Check JSON syntax is valid
3. Restart Claude Desktop completely (close from system tray)
4. Check server is running (see Step 5)

### Permission Errors

Some operations require Administrator:
- Service management
- Killing system processes
- Registry writes to HKLM
- Suspending protected processes

**Solution:**
```powershell
# Run as Administrator
Start-Process powershell -Verb RunAs
cd G:\AlphaEdge_AINV
.\START_JARETH_SERVER.bat
```

---

## 📊 Feature Summary

### Total: **42+ Tools**

| Category | Tools | Description |
|----------|-------|-------------|
| **Local Models** | 7 | Chat with Llama 3.3, Qwen 2.5, Llama 3.1 |
| **NVIDIA API** | 4 | Nemotron, image analysis, guardrails |
| **GPU Monitoring** | 5 | Status, VRAM, processes, benchmarks |
| **System Tools** | 8 | Files, commands, Python execution |
| **Windows Management** | 14 | Processes, services, registry, network |
| **Memory** | 2 | Future ChromaDB/RAG integration |
| **Server** | 2 | Status, configuration |

**Total:** 42 production-ready tools

---

## 🎓 Learn More

- **Full Documentation:** `README.md`
- **Windows OS Control:** `WINDOWS_OS_CONTROL.md`
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **MCP Protocol:** https://modelcontextprotocol.io/

---

## 💡 Pro Tips

1. **Performance:** Use Llama 3.1 8B for quick queries, Llama 3.3 70B for complex reasoning
2. **VRAM:** Monitor with "check VRAM status" to prevent out-of-memory
3. **API Costs:** Nemotron automatically falls back to local Llama 3.3 if API fails
4. **Safety:** Test commands on non-critical processes first
5. **Logging:** Check `G:\AlphaEdge_AINV\mcp_server.log` for detailed logs

---

## 🎉 You're Ready!

Jareth_AINV is now running with full Windows OS control.

Ask Claude anything - Jareth is ready to serve! 🚀

**Examples to try:**
- "Show me system health"
- "What's consuming the most resources?"
- "Use Llama 3.3 to write a Python script that..."
- "Check if Docker service is running"
- "List all processes sorted by CPU usage"

---

**Need Help?**
- Check logs: `G:\AlphaEdge_AINV\mcp_server.log`
- View documentation: `G:\AlphaEdge_AINV\README.md`
- Report issues: GitHub Issues

**Jareth_AINV** - Your AI-Powered System Administrator
