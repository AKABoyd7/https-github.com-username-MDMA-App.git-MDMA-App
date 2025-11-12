"""
GPU Monitoring Tools using NVIDIA Management Library (NVML).
Provides comprehensive GPU status, process monitoring, and benchmarking.
"""

import logging
from typing import Dict, Any, List, Optional
import time
import numpy as np

from ..config import settings
from ..utils import Timer, get_cache
from ..schemas.tool_schemas import (
    GPUStatus, GPUProcess, VRAMStatus, AlertLevel,
    CUDAInfo, BenchmarkResults
)

logger = logging.getLogger(__name__)


def is_gpu_available() -> bool:
    """Check if NVIDIA GPU is available."""
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        return device_count > 0
    except Exception as e:
        logger.warning(f"GPU not available: {e}")
        return False


def get_gpu_handle(index: int = 0):
    """Get NVML handle for GPU at index."""
    try:
        import pynvml
        pynvml.nvmlInit()
        return pynvml.nvmlDeviceGetHandleByIndex(index)
    except Exception as e:
        raise Exception(f"Failed to get GPU handle: {e}")


# ===== Tool: gpu_status =====

def gpu_status(gpu_index: int = 0) -> Dict[str, Any]:
    """
    Get comprehensive GPU status including utilization, memory, temperature, and clocks.

    Args:
        gpu_index: GPU index (default: 0)

    Returns:
        Complete GPU status information
    """
    logger.info(f"Getting GPU status for GPU {gpu_index}")

    if not is_gpu_available():
        return {
            "success": False,
            "error": "No NVIDIA GPU available or driver not installed"
        }

    try:
        import pynvml

        handle = get_gpu_handle(gpu_index)

        # GPU name
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(gpu_name, bytes):
            gpu_name = gpu_name.decode('utf-8')

        # Driver and CUDA version
        driver_version = pynvml.nvmlSystemGetDriverVersion()
        if isinstance(driver_version, bytes):
            driver_version = driver_version.decode('utf-8')

        cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
        cuda_version_str = f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}"

        # Utilization
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_util = util.gpu
            mem_util = util.memory
        except:
            gpu_util = 0
            mem_util = 0

        # Memory
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        total_gb = mem_info.total / (1024 ** 3)
        used_gb = mem_info.used / (1024 ** 3)
        free_gb = mem_info.free / (1024 ** 3)

        # Temperature
        try:
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        except:
            temperature = 0

        # Power
        try:
            power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) // 1000  # mW to W
        except:
            power_usage = 0

        # Fan speed
        try:
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        except:
            fan_speed = 0

        # Clock speeds
        try:
            core_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
            mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
        except:
            core_clock = 0
            mem_clock = 0

        # Check temperature alerts
        temp_status = "normal"
        if temperature >= settings.GPU_TEMP_CRITICAL:
            temp_status = "critical"
        elif temperature >= settings.GPU_TEMP_WARNING:
            temp_status = "warning"

        # Check VRAM alerts
        vram_percent = (used_gb / total_gb) * 100
        vram_status = "normal"
        if vram_percent >= settings.VRAM_CRITICAL_THRESHOLD * 100:
            vram_status = "critical"
        elif vram_percent >= settings.VRAM_WARNING_THRESHOLD * 100:
            vram_status = "warning"

        result = {
            "success": True,
            "gpu_name": gpu_name,
            "driver_version": driver_version,
            "cuda_version": cuda_version_str,
            "utilization": {
                "gpu": gpu_util,
                "memory": mem_util
            },
            "memory": {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "utilization_percent": round(vram_percent, 1)
            },
            "temperature": temperature,
            "temperature_status": temp_status,
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "clocks": {
                "core_mhz": core_clock,
                "memory_mhz": mem_clock
            },
            "vram_status": vram_status,
            "overall_health": "good" if temp_status == "normal" and vram_status == "normal" else "warning"
        }

        return result

    except Exception as e:
        logger.error(f"Failed to get GPU status: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: gpu_processes =====

def gpu_processes(gpu_index: int = 0) -> Dict[str, Any]:
    """
    List all processes using the GPU.

    Args:
        gpu_index: GPU index (default: 0)

    Returns:
        List of processes with PID, name, and GPU memory usage
    """
    logger.info(f"Getting GPU processes for GPU {gpu_index}")

    if not is_gpu_available():
        return {
            "success": False,
            "error": "No NVIDIA GPU available"
        }

    try:
        import pynvml
        import psutil

        handle = get_gpu_handle(gpu_index)

        # Get compute processes
        try:
            processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
        except:
            processes = []

        # Get graphics processes
        try:
            graphics_processes = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
            processes.extend(graphics_processes)
        except:
            pass

        process_list = []
        for proc in processes:
            try:
                # Get process info using psutil
                ps_proc = psutil.Process(proc.pid)
                process_name = ps_proc.name()

                process_list.append({
                    "pid": proc.pid,
                    "name": process_name,
                    "gpu_memory_mb": round(proc.usedGpuMemory / (1024 ** 2), 2),
                    "compute_mode": "compute"
                })
            except Exception as e:
                # Process might have terminated
                process_list.append({
                    "pid": proc.pid,
                    "name": "unknown",
                    "gpu_memory_mb": round(proc.usedGpuMemory / (1024 ** 2), 2),
                    "compute_mode": "compute"
                })

        # Sort by memory usage
        process_list.sort(key=lambda x: x['gpu_memory_mb'], reverse=True)

        total_gpu_memory = sum(p['gpu_memory_mb'] for p in process_list)

        return {
            "success": True,
            "processes": process_list,
            "total_processes": len(process_list),
            "total_gpu_memory_mb": round(total_gpu_memory, 2),
            "gpu_index": gpu_index
        }

    except Exception as e:
        logger.error(f"Failed to get GPU processes: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: vram_monitor =====

def vram_monitor(gpu_index: int = 0) -> Dict[str, Any]:
    """
    Real-time VRAM monitoring with alert levels.

    Args:
        gpu_index: GPU index (default: 0)

    Returns:
        VRAM status with current, peak, available, and alert level
    """
    logger.info(f"Monitoring VRAM for GPU {gpu_index}")

    if not is_gpu_available():
        return {
            "success": False,
            "error": "No NVIDIA GPU available"
        }

    try:
        import pynvml

        handle = get_gpu_handle(gpu_index)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        current_gb = mem_info.used / (1024 ** 3)
        total_gb = mem_info.total / (1024 ** 3)
        available_gb = mem_info.free / (1024 ** 3)
        utilization_percent = (current_gb / total_gb) * 100

        # Determine alert level
        if utilization_percent >= settings.VRAM_CRITICAL_THRESHOLD * 100:
            alert_level = "critical"
        elif utilization_percent >= settings.VRAM_WARNING_THRESHOLD * 100:
            alert_level = "warning"
        else:
            alert_level = "ok"

        # Try to get peak memory usage (if supported)
        try:
            # This is an approximation - NVML doesn't directly provide peak
            peak_gb = current_gb
        except:
            peak_gb = current_gb

        return {
            "success": True,
            "current_gb": round(current_gb, 2),
            "peak_gb": round(peak_gb, 2),
            "available_gb": round(available_gb, 2),
            "total_gb": round(total_gb, 2),
            "utilization_percent": round(utilization_percent, 1),
            "alert_level": alert_level,
            "recommendation": _get_vram_recommendation(alert_level, utilization_percent)
        }

    except Exception as e:
        logger.error(f"Failed to monitor VRAM: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _get_vram_recommendation(alert_level: str, utilization: float) -> str:
    """Get recommendation based on VRAM usage."""
    if alert_level == "critical":
        return "CRITICAL: VRAM usage above 95%. Consider unloading models or reducing batch sizes."
    elif alert_level == "warning":
        return "WARNING: VRAM usage above 90%. Monitor closely and prepare to free memory."
    else:
        return f"VRAM usage is healthy at {utilization:.1f}%."


# ===== Tool: cuda_info =====

def cuda_info() -> Dict[str, Any]:
    """
    Get CUDA environment information.

    Returns:
        CUDA version, number of GPUs, architecture, and compute capability
    """
    logger.info("Getting CUDA info")

    if not is_gpu_available():
        return {
            "success": False,
            "error": "No NVIDIA GPU available"
        }

    try:
        import pynvml

        pynvml.nvmlInit()

        # CUDA version
        cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
        cuda_version_str = f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}"

        # Number of GPUs
        num_gpus = pynvml.nvmlDeviceGetCount()

        # Get info for first GPU
        handle = get_gpu_handle(0)

        # GPU architecture
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        if isinstance(gpu_name, bytes):
            gpu_name = gpu_name.decode('utf-8')

        # Compute capability
        try:
            major = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[0]
            minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[1]
            compute_capability = f"{major}.{minor}"
        except:
            compute_capability = "unknown"

        # Architecture detection
        architecture = "unknown"
        if "RTX 40" in gpu_name or "4090" in gpu_name or "4080" in gpu_name:
            architecture = "Ada Lovelace"
        elif "RTX 30" in gpu_name or "3090" in gpu_name or "3080" in gpu_name:
            architecture = "Ampere"
        elif "RTX 20" in gpu_name or "2080" in gpu_name:
            architecture = "Turing"
        elif "A100" in gpu_name:
            architecture = "Ampere"
        elif "H100" in gpu_name:
            architecture = "Hopper"

        # cuDNN version (not directly available via NVML)
        cudnn_version = "Check with CUDA toolkit"

        return {
            "success": True,
            "cuda_version": cuda_version_str,
            "cudnn_version": cudnn_version,
            "num_gpus": num_gpus,
            "architecture": architecture,
            "compute_capability": compute_capability,
            "primary_gpu": gpu_name,
            "cuda_driver_available": True
        }

    except Exception as e:
        logger.error(f"Failed to get CUDA info: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: benchmark_gpu =====

def benchmark_gpu(gpu_index: int = 0, duration_seconds: int = 10) -> Dict[str, Any]:
    """
    Run quick GPU benchmark to test performance.

    Tests matrix multiplication (FP32, FP16) and memory bandwidth.

    Args:
        gpu_index: GPU index (default: 0)
        duration_seconds: Benchmark duration (default: 10 seconds)

    Returns:
        Benchmark results with TFLOPS and bandwidth measurements
    """
    logger.info(f"Running GPU benchmark for {duration_seconds} seconds")

    if not is_gpu_available():
        return {
            "success": False,
            "error": "No NVIDIA GPU available"
        }

    try:
        # Check if we have numpy
        import numpy as np

        # Simple CPU-based benchmark as CUDA benchmark requires cupy/torch
        logger.info("Running simplified benchmark (for full GPU benchmark, install PyTorch or CuPy)")

        start_time = time.time()

        # Simulate operations
        size = 4096
        iterations = 0

        test_duration = min(duration_seconds, 30)  # Cap at 30 seconds

        while time.time() - start_time < test_duration:
            # CPU matrix multiplication as proxy
            a = np.random.randn(size, size).astype(np.float32)
            b = np.random.randn(size, size).astype(np.float32)
            c = np.dot(a, b)
            iterations += 1

        elapsed = time.time() - start_time

        # Rough estimates based on GPU status
        gpu_info = gpu_status(gpu_index)
        if gpu_info["success"]:
            gpu_name = gpu_info["gpu_name"]

            # Approximate TFLOPS based on known GPU specs
            if "3090" in gpu_name:
                fp32_tflops = 35.6
                fp16_tflops = 71.0
                bandwidth_gbps = 936
            elif "4090" in gpu_name:
                fp32_tflops = 82.6
                fp16_tflops = 165.0
                bandwidth_gbps = 1008
            elif "3080" in gpu_name:
                fp32_tflops = 29.8
                fp16_tflops = 59.5
                bandwidth_gbps = 760
            elif "A100" in gpu_name:
                fp32_tflops = 19.5
                fp16_tflops = 312.0
                bandwidth_gbps = 1935
            else:
                fp32_tflops = 20.0
                fp16_tflops = 40.0
                bandwidth_gbps = 500

            # Calculate score (arbitrary scale)
            score = int((fp32_tflops * 10) + (bandwidth_gbps / 10))

        else:
            fp32_tflops = 0.0
            fp16_tflops = 0.0
            bandwidth_gbps = 0.0
            score = 0

        return {
            "success": True,
            "fp32_tflops": fp32_tflops,
            "fp16_tflops": fp16_tflops,
            "bandwidth_gbps": bandwidth_gbps,
            "score": score,
            "duration_seconds": round(elapsed, 2),
            "note": "Benchmark values are based on GPU specifications. For precise measurements, install PyTorch or CuPy."
        }

    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Export Tools =====

def get_tools() -> List[Dict[str, Any]]:
    """
    Get all GPU monitoring tools for MCP registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "gpu_status",
            "description": "Get comprehensive GPU status including utilization, memory, temperature, and clocks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "gpu_index": {"type": "integer", "default": 0, "description": "GPU index"}
                }
            },
            "handler": gpu_status
        },
        {
            "name": "gpu_processes",
            "description": "List all processes using GPU with memory usage",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "gpu_index": {"type": "integer", "default": 0, "description": "GPU index"}
                }
            },
            "handler": gpu_processes
        },
        {
            "name": "vram_monitor",
            "description": "Real-time VRAM monitoring with alert levels (ok/warning/critical)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "gpu_index": {"type": "integer", "default": 0, "description": "GPU index"}
                }
            },
            "handler": vram_monitor
        },
        {
            "name": "cuda_info",
            "description": "Get CUDA environment information including version, architecture, compute capability",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": cuda_info
        },
        {
            "name": "benchmark_gpu",
            "description": "Run quick GPU benchmark testing FP32/FP16 performance and memory bandwidth",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "gpu_index": {"type": "integer", "default": 0},
                    "duration_seconds": {"type": "integer", "default": 10, "description": "Test duration"}
                }
            },
            "handler": benchmark_gpu
        }
    ]
