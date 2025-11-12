# 🪟 Jareth_AINV - Full Windows OS Control

## Overview

Jareth_AINV now includes **comprehensive Windows OS management capabilities**, allowing Claude Desktop to control processes, services, registry, network, and system resources through natural language commands.

## 🎯 New Capabilities

### Total Tools: **42+** (14 new Windows Management tools)

## 📋 Windows Management Tools (14 Tools)

### 1. Process Management (5 tools)

#### `list_processes`
List all running processes with CPU and memory usage.

**Parameters:**
- `sort_by`: Sort by 'memory', 'cpu', 'name', or 'pid' (default: memory)

**Example:**
```json
{
  "sort_by": "cpu"
}
```

**Response:**
```json
{
  "success": true,
  "processes": [
    {
      "pid": 1234,
      "name": "chrome.exe",
      "username": "User",
      "memory_percent": 15.5,
      "cpu_percent": 8.2,
      "status": "running"
    }
  ],
  "total_count": 150
}
```

#### `get_process_info`
Get detailed information about a specific process.

**Parameters:**
- `pid` (required): Process ID

**Returns:** Full process details including exe path, cmdline, threads, connections

#### `kill_process`
Terminate a process by PID.

**Parameters:**
- `pid` (required): Process ID
- `force`: Use forceful termination (default: false)

**Example:**
```json
{
  "pid": 1234,
  "force": true
}
```

**⚠️ Warning:** Requires appropriate permissions. System processes may require Administrator rights.

#### `suspend_process`
Suspend a running process (freeze execution).

#### `resume_process`
Resume a suspended process.

---

### 2. Service Management (3 tools)

#### `list_services`
List all Windows services with their status.

**Parameters:**
- `status_filter`: Filter by 'running', 'stopped', or 'paused' (optional)

**Example:**
```json
{
  "status_filter": "running"
}
```

**Response:**
```json
{
  "success": true,
  "services": [
    {
      "name": "wuauserv",
      "display_name": "Windows Update",
      "status": "running",
      "start_type": "manual"
    }
  ]
}
```

#### `get_service_info`
Get detailed information about a specific service.

#### `manage_service`
Start, stop, or restart a Windows service.

**Parameters:**
- `service_name` (required): Service name
- `action` (required): 'start', 'stop', or 'restart'

**Example:**
```json
{
  "service_name": "wuauserv",
  "action": "restart"
}
```

**⚠️ Note:** Requires Administrator privileges for most services.

---

### 3. System Information (2 tools)

#### `get_system_info`
Get comprehensive system information.

**Returns:**
```json
{
  "success": true,
  "platform": {
    "system": "Windows",
    "release": "11",
    "version": "10.0.22621",
    "machine": "AMD64",
    "processor": "AMD Ryzen 9 5950X"
  },
  "cpu": {
    "physical_cores": 16,
    "logical_cores": 32,
    "current_freq_mhz": 3400,
    "max_freq_mhz": 4900,
    "usage_percent": 25.5
  },
  "memory": {
    "total_gb": 64.0,
    "available_gb": 32.5,
    "used_gb": 31.5,
    "percent": 49.2
  },
  "disk_c": {
    "total_gb": 500.0,
    "used_gb": 350.0,
    "free_gb": 150.0,
    "percent": 70.0
  },
  "uptime_hours": 48.5
}
```

#### `get_disk_info`
Get information about all disk partitions.

**Returns:** Details for all mounted drives (C:, D:, G:, etc.)

---

### 4. Network Management (2 tools)

#### `get_network_connections`
Get active network connections.

**Parameters:**
- `kind`: Connection type ('all', 'inet', 'tcp', 'udp') (default: all)

**Returns:**
```json
{
  "success": true,
  "connections": [
    {
      "type": "tcp",
      "laddr": "192.168.1.100:50123",
      "raddr": "142.250.185.46:443",
      "status": "ESTABLISHED",
      "pid": 1234
    }
  ]
}
```

#### `get_network_stats`
Get network interface statistics.

**Returns:** Bytes sent/received, packets, errors per interface

---

### 5. Registry Management (2 tools)

#### `read_registry`
Read Windows Registry value.

**Parameters:**
- `key_path` (required): Registry key path
- `value_name` (required): Value name
- `root`: Root key (default: HKEY_LOCAL_MACHINE)

**Example:**
```json
{
  "key_path": "SOFTWARE\\Microsoft\\Windows\\CurrentVersion",
  "value_name": "ProgramFilesDir",
  "root": "HKEY_LOCAL_MACHINE"
}
```

**Supported roots:**
- HKEY_LOCAL_MACHINE (HKLM)
- HKEY_CURRENT_USER (HKCU)
- HKEY_CLASSES_ROOT
- HKEY_USERS
- HKEY_CURRENT_CONFIG

#### `write_registry`
Write Windows Registry value.

**Parameters:**
- `key_path` (required): Registry key path
- `value_name` (required): Value name
- `value` (required): Value to write
- `value_type` (required): 0=String (REG_SZ), 4=DWORD (REG_DWORD)
- `root`: Root key (default: HKEY_CURRENT_USER)

**Example:**
```json
{
  "key_path": "Software\\MyApp",
  "value_name": "Version",
  "value": "1.0.0",
  "value_type": 0,
  "root": "HKEY_CURRENT_USER"
}
```

**⚠️ Warning:** Registry modifications can break Windows. Use with caution and create backups.

---

## 🎮 Usage Examples with Claude

### Process Management

```
User: "Show me the top 10 processes using the most memory"
Claude: [Calls list_processes with sort_by="memory"]
       Here are the top memory-consuming processes:
       1. chrome.exe (PID 1234) - 2.5GB
       2. code.exe (PID 5678) - 1.8GB
       ...

User: "Kill process 1234"
Claude: [Calls kill_process with pid=1234]
       Process chrome.exe (1234) has been terminated.

User: "What processes are using port 8080?"
Claude: [Calls get_network_connections, filters by port]
       Process python.exe (PID 9876) is listening on port 8080
```

### Service Management

```
User: "Is Windows Update service running?"
Claude: [Calls get_service_info with service_name="wuauserv"]
       Windows Update (wuauserv) is currently stopped.
       Start type: Manual

User: "Start the Windows Update service"
Claude: [Calls manage_service with action="start"]
       Service wuauserv started successfully.
```

### System Monitoring

```
User: "What's my current system resource usage?"
Claude: [Calls get_system_info]
       System Status:
       - CPU: 25% (AMD Ryzen 9 5950X, 16 cores)
       - Memory: 31.5GB / 64GB (49%)
       - Disk C: 350GB / 500GB (70%)
       - Uptime: 48.5 hours

User: "Show all disk partitions"
Claude: [Calls get_disk_info]
       Disk Partitions:
       C: - 500GB (70% used)
       D: - 2TB (45% used)
       G: - 1TB (30% used)
```

### Network Diagnostics

```
User: "Show all active network connections"
Claude: [Calls get_network_connections]
       Active Connections:
       1. 192.168.1.100:50123 -> 142.250.185.46:443 (ESTABLISHED)
          Process: chrome.exe (PID 1234)
       2. 192.168.1.100:50124 -> 52.96.132.50:443 (ESTABLISHED)
          Process: teams.exe (PID 5678)

User: "What's my network usage?"
Claude: [Calls get_network_stats]
       Network Statistics:
       Wi-Fi: 5.2GB sent, 15.8GB received
       Ethernet: 1.2GB sent, 3.4GB received
```

### Registry Operations

```
User: "What's the Windows installation path?"
Claude: [Calls read_registry]
       Windows is installed at: C:\Windows

User: "Create a registry key for my app settings"
Claude: [Calls write_registry]
       Registry key created successfully at:
       HKEY_CURRENT_USER\Software\MyApp
```

---

## 🔒 Security & Permissions

### Administrator Rights Required For:

- Killing system processes
- Managing Windows services
- Writing to HKEY_LOCAL_MACHINE
- Suspending/resuming protected processes
- Accessing some network information

### Safety Features:

1. **Process Protection:** Cannot kill critical system processes without force flag
2. **Registry Backup:** Recommend backing up registry before modifications
3. **Service Validation:** Validates service names before operations
4. **Error Handling:** Graceful failures with detailed error messages
5. **Audit Logging:** All operations logged to `mcp_server.log`

### Best Practices:

- ✅ Test commands on non-critical processes first
- ✅ Keep backups before registry changes
- ✅ Use `force=false` for process termination initially
- ✅ Monitor logs for any issues
- ❌ Don't kill system-critical processes (csrss.exe, lsass.exe, etc.)
- ❌ Don't modify registry without understanding the impact

---

## 📊 Complete Tool Count

### Original Tools: 28
- Local Models: 7
- NVIDIA API: 4
- GPU Monitoring: 5
- System Tools: 8
- Memory: 2
- Server Management: 2

### New Windows Management: 14
- Process Management: 5
- Service Management: 3
- System Information: 2
- Network Management: 2
- Registry Management: 2

### **Total: 42+ Tools** 🎉

---

## 🚀 Advanced Use Cases

### 1. **Automated System Maintenance**
```
"Check if any processes are using more than 80% CPU and suspend them"
"Stop all unnecessary services to free up resources"
"Clean up network connections from closed applications"
```

### 2. **Development Environment Management**
```
"Kill all Node.js processes"
"Restart the Docker service"
"Check if port 3000 is in use and by which process"
```

### 3. **Security Monitoring**
```
"List all active network connections"
"Show processes accessing the network"
"Check for suspicious registry entries"
```

### 4. **Resource Optimization**
```
"Show top 5 memory-consuming processes"
"Monitor CPU usage over time"
"Check disk space on all drives"
```

### 5. **Application Troubleshooting**
```
"Get detailed info about process 1234"
"Check if service 'MySQL' is running"
"View all connections from chrome.exe"
```

---

## 🔧 Troubleshooting

### "Access Denied" Errors

**Solution:** Run as Administrator
```powershell
Start-Process powershell -Verb RunAs -ArgumentList "-File install_jareth.ps1"
```

### "Service not found" Errors

**Solution:** Use exact service name (not display name)
```
# Wrong: "Windows Update"
# Correct: "wuauserv"

# Use list_services to find correct names
```

### Process Won't Terminate

**Solution:** Use force flag
```json
{
  "pid": 1234,
  "force": true
}
```

### Registry Key Not Found

**Solution:** Verify path and root
```
# Use RegEdit to verify full path
# Example: HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion
```

---

## 📚 Resources

- **Windows Services List:** `services.msc`
- **Registry Editor:** `regedit`
- **Task Manager:** `taskmgr`
- **Resource Monitor:** `resmon`
- **Event Viewer:** `eventvwr`

---

## ⚡ Performance Notes

- **Process listing:** ~100ms for 200 processes
- **Service operations:** 2-5 seconds (start/stop/restart)
- **Registry read:** <50ms
- **Registry write:** <100ms
- **Network stats:** <200ms
- **System info:** <500ms (includes CPU sampling)

---

## 🎯 What's Next?

Future enhancements planned:
- Task Scheduler integration
- Event Log monitoring
- Performance counter access
- WMI query support
- Scheduled automation
- System restore points
- Firewall rule management

---

**Jareth_AINV** - Your AI-Powered Windows System Administrator

Full OS control. Natural language interface. Production ready.
