# Jareth2 Daemon - Background Service Mode

**Always-On AI Assistant for 24/7 System Management**

---

## 🎯 What is Daemon Mode?

**Jareth2 Daemon** runs in the background, continuously:
- Monitoring system health
- Processing task queue
- Auto-responding to issues
- Accepting new tasks anytime

**Perfect for:**
- Users who need constant assistance
- Automated system monitoring
- Hands-free operation
- Proactive problem solving

---

## 🚀 Quick Start

### Start Daemon
```powershell
.\jareth2_service.bat start
```

### Add Tasks
```powershell
# Add a task to the queue
.\jareth2_service.bat task "Optimize system for gaming"
.\jareth2_service.bat task "Clean temporary files"
```

### Check Status
```powershell
.\jareth2_service.bat status
```

### Stop Daemon
```powershell
.\jareth2_service.bat stop
```

---

## 💡 How It Works

### 1. Background Monitoring (Every 30 seconds)
```
Check System Health:
├── GPU Temperature      → Auto-cool if too hot
├── Memory Usage         → Auto-free if too high
├── CPU Usage            → Auto-optimize if maxed
└── Disk Space           → Auto-clean if low
```

### 2. Task Queue
```
Task Queue:
├── Your Manual Tasks     (added via command)
├── Auto-Created Tasks    (from system monitoring)
└── Scheduled Tasks       (future feature)

Processing:
→ Picks next task
→ Runs autonomous agent
→ Completes and logs result
```

### 3. Auto-Response
```
Problem Detected → Create Task → Agent Fixes It

Example:
GPU Temperature > 85°C
  ↓
Daemon creates task: "Lower GPU usage"
  ↓
Agent closes GPU-intensive apps
  ↓
Problem solved!
```

---

## 📋 Use Cases

### For Accessibility
```powershell
# Start daemon once
.\jareth2_service.bat start

# Then just add tasks whenever needed:
.\jareth2_service.bat task "Read my notifications"
.\jareth2_service.bat task "Check if system is healthy"
.\jareth2_service.bat task "What processes are using most memory"
```

### For System Monitoring
```
Daemon auto-detects and fixes:
✓ High GPU temperature
✓ Memory leaks
✓ Disk space issues
✓ Runaway processes
```

### For Scheduled Maintenance
```powershell
# Add tasks for overnight execution
.\jareth2_service.bat task "Clean temp files at midnight"
.\jareth2_service.bat task "Update all software"
.\jareth2_service.bat task "Backup important files"
```

---

## 🔧 Configuration

### Thresholds

Edit `jareth2_daemon.py`:

```python
self.thresholds = {
    'cpu_high': 90,        # CPU usage %
    'memory_high': 85,     # Memory usage %
    'disk_low': 10,        # Disk space %
    'gpu_temp_high': 85,   # GPU temp °C
}
```

### Monitoring Interval

```python
await asyncio.sleep(30)  # Check every 30 seconds
```

Change to `60` for 1 minute, `300` for 5 minutes, etc.

---

## 📊 Status & Logs

### Check Status
```powershell
.\jareth2_service.bat status
```

Output:
```
✓ Jareth2 Daemon is running (PID: 12345)
  Tasks: 2 pending, 5 completed
```

### View Logs
```powershell
type jareth2_daemon.log
```

### Task Queue
```powershell
type task_queue.json
```

---

## 🎮 Real-World Examples

### Gaming Setup
```powershell
# Start daemon
.\jareth2_service.bat start

# Before gaming session:
.\jareth2_service.bat task "Optimize for gaming - close background apps"

# Let daemon monitor GPU temp during gaming
# It will auto-cool if needed!
```

### Work Setup
```powershell
# Morning routine
.\jareth2_service.bat task "Check system health and report"
.\jareth2_service.bat task "Close all non-work applications"

# Daemon monitors all day
# Auto-fixes any issues
```

### Overnight Maintenance
```powershell
# Before sleep
.\jareth2_service.bat task "Clean temporary files"
.\jareth2_service.bat task "Defragment drives"
.\jareth2_service.bat task "Update Windows"

# Wake up to optimized system!
```

---

## 🔒 Safety

### Sandboxed Execution
- All commands run with safety checks
- Dangerous operations require confirmation
- Undo/rollback capabilities

### Resource Limits
- Max iterations per task: 10
- Timeout per task: 10 minutes
- Memory limit: Respects system resources

### Logging
- Every action is logged
- Full audit trail
- Easy to review what happened

---

## 🆘 Troubleshooting

### Daemon Won't Start
```powershell
# Check if already running
.\jareth2_service.bat status

# If stuck, force stop
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Jareth2 Daemon*"

# Then start again
.\jareth2_service.bat start
```

### Tasks Not Processing
```powershell
# Check logs
type jareth2_daemon.log

# Check queue
type task_queue.json

# Restart daemon
.\jareth2_service.bat stop
.\jareth2_service.bat start
```

### High Resource Usage
```powershell
# Increase monitoring interval (edit jareth2_daemon.py)
await asyncio.sleep(60)  # Change from 30 to 60 seconds

# Reduce max iterations
max_iterations=5  # Change from 10 to 5
```

---

## 🎯 Best Practices

### 1. Start Daemon at Boot
```
Create Windows shortcut:
Target: G:\AlphaEdge_AINV\jareth2_service.bat start
Place in: shell:startup folder
```

### 2. Monitor the Monitor
```powershell
# Periodically check status
.\jareth2_service.bat status
```

### 3. Clear Completed Tasks
```powershell
# Edit task_queue.json to remove old completed tasks
# Or implement auto-cleanup (future feature)
```

### 4. Adjust Thresholds
```
Fine-tune based on your needs:
- Gaming PC: Higher GPU temp threshold
- Work PC: Lower memory threshold
- Server: Very tight thresholds
```

---

## 📈 Roadmap

### Coming Soon
- [ ] Web interface for task management
- [ ] Email/SMS notifications
- [ ] Scheduled tasks (cron-like)
- [ ] Multi-agent collaboration
- [ ] Voice command integration

---

## 🙏 Philosophy

**"An AI that works for you, even when you sleep."**

Jareth2 Daemon embodies true accessibility:
- No manual intervention needed
- Always available
- Proactive problem solving
- Works 24/7 in the background

This is **AI as it should be** - invisible, helpful, and empowering.

---

**Jareth2 Daemon: Your Silent Guardian, Your Watchful Protector.** 🛡️
