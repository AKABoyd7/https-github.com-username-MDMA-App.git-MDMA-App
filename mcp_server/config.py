"""
Configuration management for AlphaEdge AINV MCP Server.
Handles environment variables and settings with Windows G:\ drive paths.
"""

from pydantic_settings import BaseSettings
from pathlib import Path, PureWindowsPath
from typing import List
import os


class Settings(BaseSettings):
    """Server configuration with validation."""

    # ===== Paths (Windows G: drive) =====
    PROJECT_ROOT: str = "G:\\AlphaEdge_AINV"
    WORKSPACE_DIR: str = "G:\\AlphaEdge_AINV\\workspace"
    LOG_FILE: str = "G:\\AlphaEdge_AINV\\mcp_server.log"

    # ===== LM Studio Configuration =====
    LM_STUDIO_URL: str = "http://localhost:1234/v1"
    LM_STUDIO_TIMEOUT: int = 120
    LM_STUDIO_API_KEY: str = "lm-studio"  # Default for LM Studio

    # ===== NVIDIA API Configuration =====
    NVIDIA_API_KEY: str = ""
    NVIDIA_API_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_API_TIMEOUT: int = 60
    NVIDIA_RATE_LIMIT: int = 10  # requests per minute

    # ===== Server Configuration =====
    SERVER_PORT: int = 8000
    SERVER_HOST: str = "localhost"
    SERVER_NAME: str = "alphaedge-ainv"
    SERVER_VERSION: str = "1.0.0"
    DEBUG_MODE: bool = False

    # ===== Safety Configuration =====
    MAX_FILE_SIZE_MB: int = 10
    COMMAND_TIMEOUT: int = 30
    PYTHON_MEMORY_LIMIT_GB: int = 1
    ALLOWED_EXTENSIONS: List[str] = [
        ".py", ".txt", ".md", ".json", ".yaml", ".yml",
        ".toml", ".ini", ".cfg", ".conf", ".log",
        ".csv", ".tsv", ".xml", ".html", ".css", ".js"
    ]

    # ===== PowerShell Whitelist =====
    POWERSHELL_WHITELIST: List[str] = [
        "Get-ChildItem", "Get-Content", "Get-Process", "Get-Service",
        "Get-Item", "Get-Location", "Get-Date", "Get-Host",
        "Test-Path", "Select-Object", "Where-Object", "ForEach-Object",
        "Sort-Object", "Group-Object", "Measure-Object",
        "Write-Output", "Write-Host", "Out-String"
    ]

    POWERSHELL_BLACKLIST: List[str] = [
        "Remove-", "Delete", "Format-", "Clear-Host", "Clear-Content",
        "Invoke-WebRequest", "Invoke-RestMethod", "Invoke-Expression",
        "Start-Process", "Stop-Process", "Stop-Computer", "Restart-Computer",
        "Set-ExecutionPolicy", "New-Item", "Move-Item", "Copy-Item",
        "Rename-Item", "Set-Content", "Add-Content"
    ]

    # ===== Python Sandbox Blocked Imports =====
    PYTHON_BLOCKED_IMPORTS: List[str] = [
        "os.system", "subprocess", "socket", "urllib", "requests",
        "http", "ftplib", "telnetlib", "asyncio", "multiprocessing",
        "threading", "ctypes", "pty", "imp", "importlib"
    ]

    # ===== GPU Configuration =====
    VRAM_WARNING_THRESHOLD: float = 0.90  # 90%
    VRAM_CRITICAL_THRESHOLD: float = 0.95  # 95%
    GPU_TEMP_WARNING: int = 80  # Celsius
    GPU_TEMP_CRITICAL: int = 85  # Celsius

    # ===== Model Configuration =====
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2000
    DEFAULT_TOP_P: float = 0.9

    # Local Models
    LLAMA_33_MODEL: str = "llama-3.3-70b-instruct"
    QWEN_MODEL: str = "qwen2.5-coder-32b-instruct"
    LLAMA_31_MODEL: str = "llama-3.1-8b-instruct"

    # NVIDIA Models
    NEMOTRON_MODEL: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    NVCLIP_MODEL: str = "nvidia/nv-embedqa-e5-v5"

    # ===== Cache Configuration =====
    CACHE_NVIDIA_QUOTA_SECONDS: int = 300  # 5 minutes
    CACHE_GPU_STATUS_SECONDS: int = 2  # 2 seconds

    # ===== Retry Configuration =====
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 2
    RETRY_BACKOFF_MULTIPLIER: float = 2.0

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

    def get_windows_path(self, path_str: str) -> Path:
        """Convert string to Windows Path object."""
        return Path(path_str)

    @property
    def project_root_path(self) -> Path:
        """Get project root as Path object."""
        return self.get_windows_path(self.PROJECT_ROOT)

    @property
    def workspace_path(self) -> Path:
        """Get workspace directory as Path object."""
        return self.get_windows_path(self.WORKSPACE_DIR)

    def is_nvidia_enabled(self) -> bool:
        """Check if NVIDIA API is configured."""
        return bool(self.NVIDIA_API_KEY and self.NVIDIA_API_KEY != "")

    def get_max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def get_python_memory_limit_bytes(self) -> int:
        """Get Python memory limit in bytes."""
        return self.PYTHON_MEMORY_LIMIT_GB * 1024 * 1024 * 1024


# Global settings instance
settings = Settings()


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings


def validate_configuration() -> dict:
    """
    Validate current configuration and return status.

    Returns:
        dict: Validation results with status and messages
    """
    results = {
        "valid": True,
        "warnings": [],
        "errors": []
    }

    # Check LM Studio URL
    if not settings.LM_STUDIO_URL:
        results["errors"].append("LM_STUDIO_URL not configured")
        results["valid"] = False

    # Check NVIDIA API (warning only)
    if not settings.is_nvidia_enabled():
        results["warnings"].append("NVIDIA_API_KEY not configured - NVIDIA tools will be unavailable")

    # Check paths exist (for runtime, not build time)
    # Note: These checks should be done at runtime on Windows

    return results


if __name__ == "__main__":
    # Test configuration
    print("AlphaEdge AINV MCP Server Configuration")
    print("=" * 50)
    print(f"Project Root: {settings.PROJECT_ROOT}")
    print(f"LM Studio URL: {settings.LM_STUDIO_URL}")
    print(f"NVIDIA Enabled: {settings.is_nvidia_enabled()}")
    print(f"Server: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"Max File Size: {settings.MAX_FILE_SIZE_MB}MB")
    print("\nValidation:")
    validation = validate_configuration()
    print(f"Valid: {validation['valid']}")
    if validation['warnings']:
        print("Warnings:", validation['warnings'])
    if validation['errors']:
        print("Errors:", validation['errors'])
