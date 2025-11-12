"""
Windows Management Tools - Full OS Control
Provides comprehensive Windows OS management capabilities.
"""

import logging
import subprocess
import winreg
from typing import Dict, Any, List, Optional
import psutil
from datetime import datetime

from ..config import settings
from ..utils import Timer
from ..safety import validate_powershell_command

logger = logging.getLogger(__name__)


# ===== Process Management =====

def list_processes(sort_by: str = "memory") -> Dict[str, Any]:
    """
    List all running processes with detailed information.

    Args:
        sort_by: Sort by 'memory', 'cpu', 'name', or 'pid'

    Returns:
        List of processes with details
    """
    logger.info("Listing all processes")

    try:
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent', 'status']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "username": info.get('username', 'N/A'),
                    "memory_percent": round(info.get('memory_percent', 0), 2),
                    "cpu_percent": round(info.get('cpu_percent', 0), 2),
                    "status": info.get('status', 'unknown')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort
        sort_keys = {
            'memory': lambda x: x['memory_percent'],
            'cpu': lambda x: x['cpu_percent'],
            'name': lambda x: x['name'].lower(),
            'pid': lambda x: x['pid']
        }

        if sort_by in sort_keys:
            processes.sort(key=sort_keys[sort_by], reverse=(sort_by in ['memory', 'cpu']))

        return {
            "success": True,
            "processes": processes,
            "total_count": len(processes)
        }

    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        return {"success": False, "error": str(e)}


def get_process_info(pid: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific process.

    Args:
        pid: Process ID

    Returns:
        Detailed process information
    """
    logger.info(f"Getting info for PID {pid}")

    try:
        proc = psutil.Process(pid)

        with proc.oneshot():
            info = {
                "success": True,
                "pid": proc.pid,
                "name": proc.name(),
                "exe": proc.exe() if proc.exe() else "N/A",
                "cmdline": " ".join(proc.cmdline()),
                "status": proc.status(),
                "username": proc.username(),
                "created": datetime.fromtimestamp(proc.create_time()).isoformat(),
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_info": {
                    "rss": proc.memory_info().rss,
                    "vms": proc.memory_info().vms,
                    "percent": proc.memory_percent()
                },
                "num_threads": proc.num_threads(),
                "connections": len(proc.connections())
            }

        return info

    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process {pid} not found"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Access denied to process {pid}"}
    except Exception as e:
        logger.error(f"Failed to get process info: {e}")
        return {"success": False, "error": str(e)}


def kill_process(pid: int, force: bool = False) -> Dict[str, Any]:
    """
    Terminate a process.

    Args:
        pid: Process ID
        force: Use forceful termination (SIGKILL)

    Returns:
        Termination status
    """
    logger.info(f"Killing process {pid} (force={force})")

    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()

        if force:
            proc.kill()  # SIGKILL
        else:
            proc.terminate()  # SIGTERM

        # Wait for process to terminate
        proc.wait(timeout=5)

        return {
            "success": True,
            "pid": pid,
            "name": proc_name,
            "message": f"Process {proc_name} ({pid}) terminated"
        }

    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Process {pid} not found"}
    except psutil.TimeoutExpired:
        return {"success": False, "error": f"Process {pid} did not terminate in time"}
    except psutil.AccessDenied:
        return {"success": False, "error": f"Access denied - may require administrator privileges"}
    except Exception as e:
        logger.error(f"Failed to kill process: {e}")
        return {"success": False, "error": str(e)}


def suspend_process(pid: int) -> Dict[str, Any]:
    """
    Suspend a process.

    Args:
        pid: Process ID

    Returns:
        Suspension status
    """
    logger.info(f"Suspending process {pid}")

    try:
        proc = psutil.Process(pid)
        proc.suspend()

        return {
            "success": True,
            "pid": pid,
            "name": proc.name(),
            "message": f"Process {proc.name()} ({pid}) suspended"
        }

    except Exception as e:
        logger.error(f"Failed to suspend process: {e}")
        return {"success": False, "error": str(e)}


def resume_process(pid: int) -> Dict[str, Any]:
    """
    Resume a suspended process.

    Args:
        pid: Process ID

    Returns:
        Resume status
    """
    logger.info(f"Resuming process {pid}")

    try:
        proc = psutil.Process(pid)
        proc.resume()

        return {
            "success": True,
            "pid": pid,
            "name": proc.name(),
            "message": f"Process {proc.name()} ({pid}) resumed"
        }

    except Exception as e:
        logger.error(f"Failed to resume process: {e}")
        return {"success": False, "error": str(e)}


# ===== Service Management =====

def list_services(status_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    List Windows services.

    Args:
        status_filter: Filter by status ('running', 'stopped', 'paused')

    Returns:
        List of services
    """
    logger.info("Listing Windows services")

    try:
        services = []

        for service in psutil.win_service_iter():
            try:
                info = service.as_dict()

                if status_filter and info['status'].lower() != status_filter.lower():
                    continue

                services.append({
                    "name": info['name'],
                    "display_name": info['display_name'],
                    "status": info['status'],
                    "start_type": info['start_type']
                })
            except Exception:
                continue

        return {
            "success": True,
            "services": services,
            "total_count": len(services)
        }

    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        return {"success": False, "error": str(e)}


def get_service_info(service_name: str) -> Dict[str, Any]:
    """
    Get detailed service information.

    Args:
        service_name: Service name

    Returns:
        Service details
    """
    logger.info(f"Getting info for service: {service_name}")

    try:
        service = psutil.win_service_get(service_name)
        info = service.as_dict()

        return {
            "success": True,
            "name": info['name'],
            "display_name": info['display_name'],
            "status": info['status'],
            "start_type": info['start_type'],
            "username": info.get('username', 'N/A'),
            "pid": info.get('pid', None),
            "description": info.get('description', 'N/A')
        }

    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        return {"success": False, "error": str(e)}


def manage_service(service_name: str, action: str) -> Dict[str, Any]:
    """
    Manage Windows service (start, stop, restart).

    Args:
        service_name: Service name
        action: 'start', 'stop', or 'restart'

    Returns:
        Action status
    """
    logger.info(f"Managing service {service_name}: {action}")

    if action not in ['start', 'stop', 'restart']:
        return {"success": False, "error": f"Invalid action: {action}"}

    try:
        # Use PowerShell for service management
        commands = {
            'start': f"Start-Service -Name '{service_name}'",
            'stop': f"Stop-Service -Name '{service_name}' -Force",
            'restart': f"Restart-Service -Name '{service_name}' -Force"
        }

        result = subprocess.run(
            ["powershell", "-Command", commands[action]],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return {
                "success": True,
                "service": service_name,
                "action": action,
                "message": f"Service {service_name} {action}ed successfully"
            }
        else:
            return {
                "success": False,
                "error": result.stderr or "Service operation failed"
            }

    except Exception as e:
        logger.error(f"Failed to manage service: {e}")
        return {"success": False, "error": str(e)}


# ===== System Information =====

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.

    Returns:
        System details
    """
    logger.info("Getting system information")

    try:
        import platform

        # CPU info
        cpu_freq = psutil.cpu_freq()

        # Memory info
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk info
        disk = psutil.disk_usage('C:\\')

        # Network info
        net_io = psutil.net_io_counters()

        # Boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())

        return {
            "success": True,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "cpu": {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "current_freq_mhz": cpu_freq.current if cpu_freq else 0,
                "max_freq_mhz": cpu_freq.max if cpu_freq else 0,
                "usage_percent": psutil.cpu_percent(interval=1)
            },
            "memory": {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "percent": swap.percent
            },
            "disk_c": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            },
            "boot_time": boot_time.isoformat(),
            "uptime_hours": round((datetime.now() - boot_time).total_seconds() / 3600, 2)
        }

    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {"success": False, "error": str(e)}


def get_disk_info() -> Dict[str, Any]:
    """
    Get information about all disk partitions.

    Returns:
        Disk partition details
    """
    logger.info("Getting disk information")

    try:
        partitions = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                })
            except PermissionError:
                continue

        return {
            "success": True,
            "partitions": partitions,
            "total_partitions": len(partitions)
        }

    except Exception as e:
        logger.error(f"Failed to get disk info: {e}")
        return {"success": False, "error": str(e)}


# ===== Network Management =====

def get_network_connections(kind: str = "all") -> Dict[str, Any]:
    """
    Get active network connections.

    Args:
        kind: Connection type ('all', 'inet', 'inet4', 'inet6', 'tcp', 'udp')

    Returns:
        List of connections
    """
    logger.info(f"Getting network connections: {kind}")

    try:
        connections = []

        for conn in psutil.net_connections(kind=kind):
            connections.append({
                "fd": conn.fd,
                "family": str(conn.family),
                "type": str(conn.type),
                "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                "status": conn.status,
                "pid": conn.pid
            })

        return {
            "success": True,
            "connections": connections,
            "total_count": len(connections)
        }

    except Exception as e:
        logger.error(f"Failed to get network connections: {e}")
        return {"success": False, "error": str(e)}


def get_network_stats() -> Dict[str, Any]:
    """
    Get network interface statistics.

    Returns:
        Network stats per interface
    """
    logger.info("Getting network statistics")

    try:
        stats = {}

        for interface, addrs in psutil.net_if_addrs().items():
            io_counters = psutil.net_io_counters(pernic=True).get(interface)

            stats[interface] = {
                "addresses": [{"family": str(addr.family), "address": addr.address} for addr in addrs],
                "bytes_sent": io_counters.bytes_sent if io_counters else 0,
                "bytes_recv": io_counters.bytes_recv if io_counters else 0,
                "packets_sent": io_counters.packets_sent if io_counters else 0,
                "packets_recv": io_counters.packets_recv if io_counters else 0
            }

        return {
            "success": True,
            "interfaces": stats
        }

    except Exception as e:
        logger.error(f"Failed to get network stats: {e}")
        return {"success": False, "error": str(e)}


# ===== Registry Management =====

def read_registry(key_path: str, value_name: str, root: str = "HKEY_LOCAL_MACHINE") -> Dict[str, Any]:
    """
    Read Windows Registry value.

    Args:
        key_path: Registry key path
        value_name: Value name
        root: Root key (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)

    Returns:
        Registry value
    """
    logger.info(f"Reading registry: {root}\\{key_path}\\{value_name}")

    try:
        root_keys = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
        }

        if root not in root_keys:
            return {"success": False, "error": f"Invalid root key: {root}"}

        key = winreg.OpenKey(root_keys[root], key_path)
        value, value_type = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)

        return {
            "success": True,
            "key_path": f"{root}\\{key_path}",
            "value_name": value_name,
            "value": value,
            "type": value_type
        }

    except FileNotFoundError:
        return {"success": False, "error": "Registry key or value not found"}
    except PermissionError:
        return {"success": False, "error": "Permission denied - requires administrator privileges"}
    except Exception as e:
        logger.error(f"Failed to read registry: {e}")
        return {"success": False, "error": str(e)}


def write_registry(key_path: str, value_name: str, value: Any, value_type: int, root: str = "HKEY_CURRENT_USER") -> Dict[str, Any]:
    """
    Write Windows Registry value.

    Args:
        key_path: Registry key path
        value_name: Value name
        value: Value to write
        value_type: Value type (0=REG_SZ, 1=REG_BINARY, 4=REG_DWORD)
        root: Root key

    Returns:
        Write status
    """
    logger.info(f"Writing registry: {root}\\{key_path}\\{value_name}")

    try:
        root_keys = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT
        }

        if root not in root_keys:
            return {"success": False, "error": f"Invalid root key: {root}"}

        key = winreg.CreateKey(root_keys[root], key_path)
        winreg.SetValueEx(key, value_name, 0, value_type, value)
        winreg.CloseKey(key)

        return {
            "success": True,
            "key_path": f"{root}\\{key_path}",
            "value_name": value_name,
            "message": "Registry value written successfully"
        }

    except PermissionError:
        return {"success": False, "error": "Permission denied - requires administrator privileges"}
    except Exception as e:
        logger.error(f"Failed to write registry: {e}")
        return {"success": False, "error": str(e)}


# ===== Export Tools =====

def get_tools() -> List[Dict[str, Any]]:
    """Get all Windows management tools."""

    return [
        {
            "name": "list_processes",
            "description": "List all running processes with CPU and memory usage",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sort_by": {"type": "string", "enum": ["memory", "cpu", "name", "pid"], "default": "memory"}
                }
            },
            "handler": list_processes
        },
        {
            "name": "get_process_info",
            "description": "Get detailed information about a specific process",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID"}
                },
                "required": ["pid"]
            },
            "handler": get_process_info
        },
        {
            "name": "kill_process",
            "description": "Terminate a process by PID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID"},
                    "force": {"type": "boolean", "default": False, "description": "Force kill"}
                },
                "required": ["pid"]
            },
            "handler": kill_process
        },
        {
            "name": "suspend_process",
            "description": "Suspend a running process",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID"}
                },
                "required": ["pid"]
            },
            "handler": suspend_process
        },
        {
            "name": "resume_process",
            "description": "Resume a suspended process",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID"}
                },
                "required": ["pid"]
            },
            "handler": resume_process
        },
        {
            "name": "list_services",
            "description": "List Windows services with status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status_filter": {"type": "string", "enum": ["running", "stopped", "paused"]}
                }
            },
            "handler": list_services
        },
        {
            "name": "get_service_info",
            "description": "Get detailed information about a Windows service",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "Service name"}
                },
                "required": ["service_name"]
            },
            "handler": get_service_info
        },
        {
            "name": "manage_service",
            "description": "Start, stop, or restart a Windows service",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "Service name"},
                    "action": {"type": "string", "enum": ["start", "stop", "restart"]}
                },
                "required": ["service_name", "action"]
            },
            "handler": manage_service
        },
        {
            "name": "get_system_info",
            "description": "Get comprehensive system information (CPU, memory, disk, network)",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": get_system_info
        },
        {
            "name": "get_disk_info",
            "description": "Get information about all disk partitions",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": get_disk_info
        },
        {
            "name": "get_network_connections",
            "description": "Get active network connections",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["all", "inet", "inet4", "inet6", "tcp", "udp"], "default": "all"}
                }
            },
            "handler": get_network_connections
        },
        {
            "name": "get_network_stats",
            "description": "Get network interface statistics",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": get_network_stats
        },
        {
            "name": "read_registry",
            "description": "Read Windows Registry value",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "key_path": {"type": "string", "description": "Registry key path"},
                    "value_name": {"type": "string", "description": "Value name"},
                    "root": {"type": "string", "default": "HKEY_LOCAL_MACHINE"}
                },
                "required": ["key_path", "value_name"]
            },
            "handler": read_registry
        },
        {
            "name": "write_registry",
            "description": "Write Windows Registry value (requires admin)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "key_path": {"type": "string", "description": "Registry key path"},
                    "value_name": {"type": "string", "description": "Value name"},
                    "value": {"description": "Value to write"},
                    "value_type": {"type": "integer", "description": "0=String, 4=DWORD"},
                    "root": {"type": "string", "default": "HKEY_CURRENT_USER"}
                },
                "required": ["key_path", "value_name", "value", "value_type"]
            },
            "handler": write_registry
        }
    ]
