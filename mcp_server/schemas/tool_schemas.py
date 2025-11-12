"""
Pydantic schemas for MCP tool parameters and responses.
Provides validation and type safety for all tool inputs and outputs.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal
from enum import Enum


# ===== Common Types =====

class AlertLevel(str, Enum):
    """Alert level for monitoring tools."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelStatus(str, Enum):
    """Model loading status."""
    LOADED = "loaded"
    UNLOADED = "unloaded"
    LOADING = "loading"
    ERROR = "error"


# ===== Local Models Schemas =====

class ChatRequest(BaseModel):
    """Request for chat with local model."""
    prompt: str = Field(..., description="User prompt/message", min_length=1)
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(2000, ge=1, le=32000, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Enable streaming response")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")


class ChatResponse(BaseModel):
    """Response from chat model."""
    response: str = Field(..., description="Model response")
    model: str = Field(..., description="Model name used")
    tokens_used: Optional[int] = Field(None, description="Total tokens used")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")
    execution_time: float = Field(..., description="Response time in seconds")


class ModelInfo(BaseModel):
    """Information about a model."""
    model_name: str = Field(..., description="Model identifier")
    size_gb: Optional[float] = Field(None, description="Model size in GB")
    status: ModelStatus = Field(..., description="Current status")
    vram_usage_gb: Optional[float] = Field(None, description="VRAM used by model")
    context_length: Optional[int] = Field(None, description="Context window size")


class LoadModelRequest(BaseModel):
    """Request to load a model."""
    model_name: str = Field(..., description="Model to load")
    gpu_layers: Optional[int] = Field(None, ge=0, description="Number of layers to offload to GPU")


class LoadModelResponse(BaseModel):
    """Response from model loading."""
    success: bool = Field(..., description="Whether load succeeded")
    model_name: str = Field(..., description="Model name")
    load_time: float = Field(..., description="Time taken to load in seconds")
    vram_allocated_gb: Optional[float] = Field(None, description="VRAM allocated")
    message: str = Field(..., description="Status message")


# ===== NVIDIA API Schemas =====

class NemotronRequest(BaseModel):
    """Request for NVIDIA Nemotron chat."""
    prompt: str = Field(..., description="User prompt", min_length=1)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(2000, ge=1, le=4096)
    fallback_to_local: bool = Field(True, description="Fallback to local model on failure")


class ImageAnalysisRequest(BaseModel):
    """Request for image analysis."""
    image_source: str = Field(..., description="URL, base64, or file path")
    prompt: Optional[str] = Field(None, description="Optional analysis prompt")
    max_tokens: int = Field(1000, ge=100, le=2000)


class ImageAnalysisResponse(BaseModel):
    """Response from image analysis."""
    description: str = Field(..., description="Image description")
    objects: List[str] = Field(default_factory=list, description="Detected objects")
    text_extracted: Optional[str] = Field(None, description="Text found in image")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")


class NVIDIAQuota(BaseModel):
    """NVIDIA API quota information."""
    requests_used: int = Field(..., description="Requests used this period")
    requests_remaining: Optional[int] = Field(None, description="Remaining requests")
    quota_reset_date: Optional[str] = Field(None, description="When quota resets")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost in USD")


class GuardrailsRequest(BaseModel):
    """Request for content safety check."""
    content: str = Field(..., description="Content to check", min_length=1)
    check_types: List[str] = Field(
        default_factory=lambda: ["jailbreak", "pii", "toxicity"],
        description="Types of checks to perform"
    )


class GuardrailsResponse(BaseModel):
    """Response from guardrails check."""
    safety_score: float = Field(..., ge=0.0, le=100.0, description="Overall safety score")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Detected issues")
    filtered_content: Optional[str] = Field(None, description="Filtered/safe content")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")


# ===== GPU Monitoring Schemas =====

class GPUUtilization(BaseModel):
    """GPU utilization metrics."""
    gpu_percent: float = Field(..., ge=0.0, le=100.0, description="GPU utilization %")
    memory_percent: float = Field(..., ge=0.0, le=100.0, description="Memory utilization %")


class GPUMemory(BaseModel):
    """GPU memory information."""
    total_gb: float = Field(..., description="Total VRAM in GB")
    used_gb: float = Field(..., description="Used VRAM in GB")
    free_gb: float = Field(..., description="Free VRAM in GB")


class GPUClocks(BaseModel):
    """GPU clock speeds."""
    core_mhz: int = Field(..., description="Core clock in MHz")
    memory_mhz: int = Field(..., description="Memory clock in MHz")


class GPUStatus(BaseModel):
    """Complete GPU status."""
    gpu_name: str = Field(..., description="GPU model name")
    driver_version: str = Field(..., description="Driver version")
    cuda_version: str = Field(..., description="CUDA version")
    utilization: GPUUtilization = Field(..., description="Utilization metrics")
    memory: GPUMemory = Field(..., description="Memory status")
    temperature: int = Field(..., description="Temperature in Celsius")
    power_usage: int = Field(..., description="Power usage in Watts")
    fan_speed: int = Field(..., ge=0, le=100, description="Fan speed percentage")
    clocks: GPUClocks = Field(..., description="Clock speeds")


class GPUProcess(BaseModel):
    """Process using GPU."""
    pid: int = Field(..., description="Process ID")
    name: str = Field(..., description="Process name")
    gpu_memory_mb: float = Field(..., description="GPU memory used in MB")
    compute_mode: Optional[str] = Field(None, description="Compute mode")


class VRAMStatus(BaseModel):
    """VRAM monitoring status."""
    current_gb: float = Field(..., description="Current VRAM usage")
    peak_gb: float = Field(..., description="Peak VRAM usage")
    available_gb: float = Field(..., description="Available VRAM")
    alert_level: AlertLevel = Field(..., description="Alert level")
    utilization_percent: float = Field(..., ge=0.0, le=100.0)


class CUDAInfo(BaseModel):
    """CUDA environment information."""
    cuda_version: str = Field(..., description="CUDA version")
    cudnn_version: Optional[str] = Field(None, description="cuDNN version")
    num_gpus: int = Field(..., description="Number of GPUs")
    architecture: str = Field(..., description="GPU architecture")
    compute_capability: str = Field(..., description="Compute capability")


class BenchmarkResults(BaseModel):
    """GPU benchmark results."""
    fp32_tflops: float = Field(..., description="FP32 TFLOPS")
    fp16_tflops: float = Field(..., description="FP16 TFLOPS")
    bandwidth_gbps: float = Field(..., description="Memory bandwidth GB/s")
    score: int = Field(..., description="Overall benchmark score")
    duration_seconds: float = Field(..., description="Benchmark duration")


# ===== System Tools Schemas =====

class CommandRequest(BaseModel):
    """Request to execute command."""
    command: str = Field(..., description="Command to execute", min_length=1)
    timeout: int = Field(30, ge=1, le=300, description="Timeout in seconds")
    working_dir: Optional[str] = Field(None, description="Working directory")


class CommandResponse(BaseModel):
    """Response from command execution."""
    stdout: str = Field(..., description="Standard output")
    stderr: str = Field(..., description="Standard error")
    exit_code: int = Field(..., description="Exit code")
    execution_time: float = Field(..., description="Execution time in seconds")
    success: bool = Field(..., description="Whether command succeeded")


class PythonExecutionRequest(BaseModel):
    """Request to execute Python code."""
    code: str = Field(..., description="Python code to execute", min_length=1)
    timeout: int = Field(30, ge=1, le=300)
    memory_limit_mb: Optional[int] = Field(1024, ge=256, le=4096)


class PythonExecutionResponse(BaseModel):
    """Response from Python execution."""
    output: str = Field(..., description="Execution output")
    errors: str = Field("", description="Error messages")
    execution_time: float = Field(..., description="Execution time")
    memory_used_mb: Optional[float] = Field(None, description="Memory used")
    success: bool = Field(..., description="Whether execution succeeded")


class FileReadRequest(BaseModel):
    """Request to read file."""
    file_path: str = Field(..., description="Path to file", min_length=1)
    encoding: Optional[str] = Field("utf-8", description="File encoding")


class FileReadResponse(BaseModel):
    """Response from file read."""
    content: str = Field(..., description="File contents")
    encoding: str = Field(..., description="Detected encoding")
    size_bytes: int = Field(..., description="File size in bytes")
    lines: int = Field(..., description="Number of lines")


class FileWriteRequest(BaseModel):
    """Request to write file."""
    file_path: str = Field(..., description="Path to file", min_length=1)
    content: str = Field(..., description="Content to write")
    create_backup: bool = Field(True, description="Create backup of existing file")


class FileWriteResponse(BaseModel):
    """Response from file write."""
    success: bool = Field(..., description="Whether write succeeded")
    path: str = Field(..., description="File path")
    backup_path: Optional[str] = Field(None, description="Backup file path")
    bytes_written: int = Field(..., description="Bytes written")


class FileInfo(BaseModel):
    """File metadata."""
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Full path")
    size_bytes: int = Field(..., description="File size")
    modified: str = Field(..., description="Last modified timestamp")
    is_dir: bool = Field(..., description="Whether item is directory")


class ListFilesRequest(BaseModel):
    """Request to list files."""
    path: str = Field(..., description="Directory path")
    pattern: str = Field("*", description="File pattern/glob")
    recursive: bool = Field(False, description="Recursive listing")


class SearchFilesRequest(BaseModel):
    """Request to search files."""
    query: str = Field(..., description="Search query", min_length=1)
    path: str = Field(..., description="Search root path")
    search_type: Literal["filename", "content", "extension"] = Field("filename")
    case_sensitive: bool = Field(False)


class SearchResult(BaseModel):
    """Search result entry."""
    path: str = Field(..., description="File path")
    matches: List[str] = Field(default_factory=list, description="Matching lines")
    line_numbers: List[int] = Field(default_factory=list, description="Line numbers")


class DetailedFileInfo(BaseModel):
    """Detailed file metadata."""
    size: int = Field(..., description="Size in bytes")
    created: str = Field(..., description="Creation timestamp")
    modified: str = Field(..., description="Modification timestamp")
    accessed: str = Field(..., description="Last access timestamp")
    permissions: str = Field(..., description="File permissions")
    md5_hash: Optional[str] = Field(None, description="MD5 hash")


# ===== Memory/Knowledge Schemas =====

class MemorySearchRequest(BaseModel):
    """Request to search memory."""
    query: str = Field(..., description="Search query", min_length=1)
    limit: int = Field(10, ge=1, le=100, description="Maximum results")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Similarity threshold")


class MemoryAddRequest(BaseModel):
    """Request to add to memory."""
    content: str = Field(..., description="Content to add", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    category: Optional[str] = Field(None, description="Category/tag")


# ===== Server Management Schemas =====

class ServerStatus(BaseModel):
    """MCP server status."""
    uptime_seconds: float = Field(..., description="Server uptime")
    active_connections: int = Field(..., description="Active connections")
    total_requests: int = Field(..., description="Total requests served")
    error_count: int = Field(..., description="Total errors")
    tools_registered: int = Field(..., description="Number of tools")
    lm_studio_status: str = Field(..., description="LM Studio connection status")
    nvidia_api_status: str = Field(..., description="NVIDIA API status")


class ServerConfig(BaseModel):
    """Server configuration."""
    lm_studio_url: str = Field(..., description="LM Studio endpoint")
    nvidia_api_enabled: bool = Field(..., description="NVIDIA API enabled")
    project_path: str = Field(..., description="Project root path")
    enabled_features: List[str] = Field(default_factory=list, description="Enabled features")


class ConfigReloadResponse(BaseModel):
    """Response from config reload."""
    success: bool = Field(..., description="Whether reload succeeded")
    changes: List[str] = Field(default_factory=list, description="Configuration changes")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    timestamp: str = Field(..., description="Reload timestamp")


# ===== Error Response Schema =====

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type/category")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    timestamp: str = Field(..., description="Error timestamp")
