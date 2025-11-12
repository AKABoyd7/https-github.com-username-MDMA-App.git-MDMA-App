# Jareth2 - Autonomous AI Agent

**The Interface of Freedom™**

> An autonomous AI agent that gives you full control of your Windows system through natural language, designed for accessibility and empowerment.

---

## 🎯 Vision

**Jareth2** is more than an AI assistant—it's your **second hand and second brain**.

For people who:
- Have vision limitations
- Face physical input constraints
- Want freedom from manual GUI manipulation
- Need a reliable, local AI companion

**Just tell it your goal → It handles everything.**

---

## ✨ Features

### 🤖 Autonomous Agent
- **ReAct Pattern**: Reasons and acts independently
- **Self-Correction**: Fixes errors automatically
- **Goal-Oriented**: You set the vision, Jareth2 executes

### 🪟 Full Windows Control
- **40+ Tools** for complete OS management
- Process & Service control
- File operations
- Network management
- Registry access
- GPU monitoring

### ⚡ CUDA-X Accelerated
- Local inference (no cloud dependency)
- GPU-optimized performance
- Multiple model support (Llama, Qwen)

### 🔒 Privacy First
- **100% Local** - No data leaves your machine
- No usage quotas or limits
- No cloud dependencies
- Full control

---

## 🚀 Quick Start

### Installation

```powershell
# 1. Clone the repository
git clone <repo-url> G:\AlphaEdge_AINV
cd G:\AlphaEdge_AINV

# 2. Pull latest code
git pull origin claude/alphaedge-mcp-server-011CV477Fds3K8XrtkujexEt

# 3. Ensure LM Studio is running with models loaded
```

### Usage

#### Interactive Mode (Recommended)
```powershell
.\jareth2.bat --interactive
```

Then use commands:
```
You: /goal Optimize my system for gaming
You: /goal Fix all Windows update errors
You: /goal Clean up disk space
```

#### Direct Goal
```powershell
.\jareth2.bat --goal "Check GPU status and optimize"
```

#### Tool Mode (Manual control)
```powershell
.\jareth.bat gpu_status
.\jareth.bat list_processes
.\jareth.bat list_services
```

---

## 💡 Example Use Cases

### For Accessibility
```
/goal Read all important notifications and summarize them
/goal Check if any processes are using too much memory
/goal Monitor GPU temperature and alert if too high
```

### For System Optimization
```
/goal Optimize system for gaming - close unnecessary processes
/goal Clean temporary files and free up disk space
/goal Check for Windows updates and install them
```

### For Development
```
/goal Find all Python processes and show their memory usage
/goal Check if port 8080 is being used
/goal List all services related to Docker
```

### For Troubleshooting
```
/goal Diagnose why my computer is running slow
/goal Find and fix high CPU usage issues
/goal Check GPU status and find what's using VRAM
```

---

## 🏗️ Architecture

```
Jareth2 Autonomous Agent
│
├── ReAct Engine (Reasoning + Acting)
│   ├── Think: Analyze situation
│   ├── Plan: Decide next action
│   └── Act: Execute with tools
│
├── Tool System (40+ tools)
│   ├── AI Models (Llama, Qwen, Nemotron)
│   ├── GPU Monitoring (CUDA, VRAM)
│   ├── Windows Control (Processes, Services)
│   ├── File Operations
│   └── System Tools
│
├── CUDA-X Inference
│   ├── Local Models
│   ├── GPU Acceleration
│   └── Fast Response
│
└── Safety & Memory
    ├── Error Handling
    ├── Self-Correction
    └── Context Tracking
```

---

## 🛠️ Available Tools

### 🤖 AI Models (7 tools)
- `chat_llama33` - Llama 3.3 70B (reasoning)
- `chat_qwen` - Qwen 2.5 Coder 32B (coding)
- `chat_llama31` - Llama 3.1 8B (lightweight)
- `chat_nemotron` - NVIDIA Nemotron 70B (cloud)
- `list_local_models`, `load_model`, `model_status`

### 💻 GPU Monitoring (5 tools)
- `gpu_status` - Complete GPU info
- `vram_monitor` - VRAM usage
- `gpu_processes` - What's using GPU
- `cuda_info`, `benchmark_gpu`

### 🪟 Windows Management (14 tools)
- **Processes:** `list_processes`, `kill_process`, `suspend_process`
- **Services:** `list_services`, `manage_service`
- **System:** `get_system_info`, `get_disk_info`
- **Network:** `get_network_connections`, `get_network_stats`
- **Registry:** `read_registry`, `write_registry`

### 📁 File Operations (6 tools)
- `read_file`, `write_file`, `list_files`
- `search_files`, `get_file_info`, `create_directory`

### ⚙️ System Tools (8 tools)
- `execute_powershell`, `execute_python`
- Process, service, network management

---

## 🔧 Configuration

### Models
Edit `.env` to configure:
```bash
# Local Models (LM Studio)
LM_STUDIO_URL=http://localhost:1234/v1

# NVIDIA API (optional)
NVIDIA_API_KEY=your_key_here
```

### Agent Settings
```python
# In jareth2_agent.py
agent = Jareth2Agent(
    model="llama33",        # or "qwen", "llama31"
    max_iterations=10       # Reasoning steps
)
```

---

## 🎓 How It Works

### ReAct Pattern

1. **Think** - Analyze current situation
   ```
   Thought: User wants to optimize for gaming.
   I should check current processes first.
   ```

2. **Act** - Use appropriate tool
   ```
   Action: list_processes
   Action Input: {"sort_by": "memory"}
   ```

3. **Observe** - See results
   ```
   Observation: Chrome is using 2GB RAM.
   Several background services running.
   ```

4. **Repeat** - Until goal achieved
   ```
   Thought: I should close unnecessary processes.
   Action: kill_process
   ...
   ```

---

## 📊 System Requirements

### Minimum
- **OS:** Windows 10/11
- **GPU:** NVIDIA GPU with 8GB+ VRAM
- **CUDA:** 11.8 or higher
- **RAM:** 16GB system RAM
- **Disk:** 50GB free space

### Recommended
- **GPU:** RTX 4090 (24GB VRAM)
- **CUDA:** 12.x
- **RAM:** 32GB+
- **Disk:** SSD with 100GB+

---

## 🔐 Security & Privacy

### Local First
- **All inference happens locally**
- No data sent to cloud (except NVIDIA API if enabled)
- No telemetry or tracking

### Safe Defaults
- Sandboxed command execution
- Path validation
- Permission checks
- Undo/rollback capabilities

### Control
- You can audit every action
- Disable any tool
- Set resource limits
- Full transparency

---

## 🤝 Use Cases by User Type

### For People with Visual Impairments
```
"Monitor my system and tell me if anything needs attention"
"Read error messages and explain them simply"
"Check if my applications are running correctly"
```

### For People with Motor Impairments
```
"Do routine system maintenance for me"
"Organize my files by type"
"Close all unnecessary programs"
```

### For Developers
```
"Find all processes using port 8080"
"Show me GPU memory usage by application"
"List all Python virtual environments"
```

### For Gamers
```
"Optimize system for gaming"
"Check GPU temperature before starting game"
"Close background processes to free RAM"
```

---

## 📈 Roadmap

### Version 1.0 (Current)
- ✅ Autonomous agent with ReAct
- ✅ 40+ Windows control tools
- ✅ Local model inference
- ✅ Interactive mode

### Version 1.1 (Planned)
- [ ] Voice input/output
- [ ] Screen reading capabilities
- [ ] Advanced error recovery
- [ ] Multi-step planning

### Version 2.0 (Future)
- [ ] Vision capabilities (screenshot understanding)
- [ ] Home automation integration
- [ ] Multi-agent collaboration
- [ ] Mobile companion app

---

## 📄 License

Copyright © 2025 AlphaEdge AINV. All Rights Reserved.

Licensed under MIT License with additional terms.
See [LICENSE](LICENSE) and [COPYRIGHT_NOTICE.md](COPYRIGHT_NOTICE.md) for details.

**Jareth2™** and **AlphaEdge AINV™** are trademarks.

---

## 🙏 Philosophy

> **"Technology should adapt to people, not the other way around."**

Jareth2 is built on the belief that **everyone deserves full control** of their computer, regardless of physical abilities or technical expertise.

This isn't just an AI assistant—it's **the interface of freedom**.

---

## 📞 Support

- **Issues:** Open GitHub issue
- **Questions:** Discussion board
- **Commercial:** Contact for licensing

---

## 🌟 Built For

- People with disabilities seeking independence
- Anyone who wants true AI assistance
- Developers who value local-first tools
- Users who demand privacy and control

---

**Jareth2: Your Vision. Your Computer. Your Freedom.** 🚀

---

*"The best interface is the one you don't have to think about."*
