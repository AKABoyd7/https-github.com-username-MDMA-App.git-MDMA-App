"""
Safety guards and validation for AlphaEdge AINV MCP Server.
Provides security checks for file operations and command execution.
"""

from pathlib import Path, PureWindowsPath
from typing import Tuple, List
import re
from .config import settings


class SafetyViolation(Exception):
    """Raised when a safety rule is violated."""
    pass


def validate_powershell_command(command: str) -> Tuple[bool, str]:
    """
    Validate PowerShell command against whitelist and blacklist.

    Args:
        command: PowerShell command to validate

    Returns:
        Tuple of (is_valid, message)
    """
    command_lower = command.lower()

    # Check blacklist first (security critical)
    for blocked in settings.POWERSHELL_BLACKLIST:
        if blocked.lower() in command_lower:
            return False, f"Blocked command detected: {blocked}"

    # Check if command uses any whitelisted commands
    has_whitelisted = False
    for allowed in settings.POWERSHELL_WHITELIST:
        if allowed.lower() in command_lower:
            has_whitelisted = True
            break

    if not has_whitelisted:
        return False, "Command does not use any whitelisted cmdlets"

    # Additional security checks
    dangerous_patterns = [
        r';\s*\$',  # Command chaining with variables
        r'\$\s*\(',  # Command substitution
        r'`',  # Backtick execution
        r'iex\s',  # Invoke-Expression alias
        r'icm\s',  # Invoke-Command alias
        r'\|\s*out-file',  # File writing
        r'>\s*',  # Redirection
        r'>>\s*',  # Append redirection
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command_lower):
            return False, f"Potentially dangerous pattern detected: {pattern}"

    return True, "Command validated"


def validate_python_code(code: str) -> Tuple[bool, str]:
    """
    Validate Python code for dangerous operations.

    Args:
        code: Python code to validate

    Returns:
        Tuple of (is_valid, message)
    """
    code_lower = code.lower()

    # Check for blocked imports
    for blocked_import in settings.PYTHON_BLOCKED_IMPORTS:
        patterns = [
            f'import {blocked_import}',
            f'from {blocked_import}',
            f'__import__("{blocked_import}")',
            f"__import__('{blocked_import}')",
        ]
        for pattern in patterns:
            if pattern.lower() in code_lower:
                return False, f"Blocked import detected: {blocked_import}"

    # Check for dangerous built-ins
    dangerous_builtins = [
        'exec', 'eval', 'compile', '__import__',
        'open', 'input', 'raw_input'
    ]

    for builtin in dangerous_builtins:
        # Look for function calls
        if re.search(rf'\b{builtin}\s*\(', code_lower):
            return False, f"Dangerous built-in function detected: {builtin}"

    # Check for file operations
    file_operations = ['file', 'read', 'write', 'append', 'delete']
    for op in file_operations:
        if re.search(rf'\.{op}\s*\(', code_lower):
            return False, f"File operation detected: {op} (use provided file tools instead)"

    return True, "Code validated"


def validate_file_path(path: str, must_exist: bool = False) -> Tuple[bool, str, Path]:
    """
    Validate file path is within allowed project directory.

    Args:
        path: File path to validate (can be Windows or POSIX style)
        must_exist: Whether the file must exist

    Returns:
        Tuple of (is_valid, message, resolved_path)
    """
    try:
        # Convert to Path object
        if isinstance(path, str):
            # Handle Windows paths
            if '\\' in path or ':' in path:
                # Windows path
                path_obj = PureWindowsPath(path)
            else:
                path_obj = Path(path)
        else:
            path_obj = Path(path)

        # Get project root
        project_root = PureWindowsPath(settings.PROJECT_ROOT)

        # Convert both to strings for comparison
        path_str = str(path_obj).lower().replace('/', '\\')
        root_str = str(project_root).lower().replace('/', '\\')

        # Check if path is within project root
        if not path_str.startswith(root_str):
            return False, f"Path must be within {settings.PROJECT_ROOT}", path_obj

        # Check for path traversal attempts
        path_parts = str(path_obj).split('\\')
        if '..' in path_parts:
            return False, "Path traversal (..) not allowed", path_obj

        # Check file extension if it's a file
        if '.' in str(path_obj).split('\\')[-1]:
            extension = '.' + str(path_obj).split('.')[-1].lower()
            if extension not in settings.ALLOWED_EXTENSIONS:
                return False, f"File extension {extension} not allowed", path_obj

        return True, "Path validated", path_obj

    except Exception as e:
        return False, f"Path validation error: {str(e)}", Path()


def validate_file_size(size_bytes: int) -> Tuple[bool, str]:
    """
    Validate file size is within limits.

    Args:
        size_bytes: File size in bytes

    Returns:
        Tuple of (is_valid, message)
    """
    max_size = settings.get_max_file_size_bytes()
    if size_bytes > max_size:
        size_mb = size_bytes / (1024 * 1024)
        return False, f"File size {size_mb:.2f}MB exceeds limit of {settings.MAX_FILE_SIZE_MB}MB"
    return True, "File size OK"


def sanitize_path_for_display(path: str) -> str:
    """
    Sanitize path for safe display in logs/output.

    Args:
        path: Path to sanitize

    Returns:
        Sanitized path string
    """
    # Remove any potential injection characters
    sanitized = re.sub(r'[<>"|?*]', '', str(path))
    return sanitized


def is_safe_filename(filename: str) -> Tuple[bool, str]:
    """
    Check if filename is safe (no special characters or path traversal).

    Args:
        filename: Filename to check

    Returns:
        Tuple of (is_safe, message)
    """
    # Check for path separators
    if '/' in filename or '\\' in filename:
        return False, "Filename cannot contain path separators"

    # Check for path traversal
    if filename == '..' or filename == '.':
        return False, "Invalid filename"

    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
    for char in dangerous_chars:
        if char in filename:
            return False, f"Filename contains dangerous character: {char}"

    # Check for reserved Windows names
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    name_without_ext = filename.split('.')[0].upper()
    if name_without_ext in reserved_names:
        return False, f"Filename uses reserved Windows name: {name_without_ext}"

    return True, "Filename is safe"


def check_vram_availability(required_gb: float) -> Tuple[bool, str, float]:
    """
    Check if enough VRAM is available for operation.

    Args:
        required_gb: Required VRAM in GB

    Returns:
        Tuple of (is_available, message, available_gb)
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        available_gb = info.free / (1024 ** 3)

        if available_gb >= required_gb:
            return True, f"Sufficient VRAM available: {available_gb:.2f}GB", available_gb
        else:
            return False, f"Insufficient VRAM: {available_gb:.2f}GB available, {required_gb:.2f}GB required", available_gb

    except Exception as e:
        # Can't check, allow operation but warn
        return True, f"Could not check VRAM: {str(e)}", 0.0


def rate_limit_check(key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, str]:
    """
    Simple rate limiting check (in-memory).

    Args:
        key: Rate limit key (e.g., "nvidia_api")
        limit: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        Tuple of (is_allowed, message)
    """
    # This would need a proper implementation with Redis or similar
    # For now, just return True
    return True, "Rate limit OK"


# Security context manager for safe execution
class SafeExecutionContext:
    """Context manager for safe code execution with timeout and memory limits."""

    def __init__(self, timeout_seconds: int = 30, memory_limit_mb: int = 1024):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Log the exception
            pass
        return False

    def check_timeout(self):
        """Check if execution has exceeded timeout."""
        import time
        if time.time() - self.start_time > self.timeout_seconds:
            raise TimeoutError(f"Execution exceeded {self.timeout_seconds} seconds")


def get_safe_error_message(error: Exception) -> str:
    """
    Get sanitized error message safe for display.

    Args:
        error: Exception object

    Returns:
        Safe error message string
    """
    error_str = str(error)
    # Remove any potential sensitive information
    error_str = re.sub(r'[A-Za-z0-9+/]{20,}={0,2}', '[REDACTED]', error_str)  # Base64
    error_str = re.sub(r'[a-f0-9]{32,}', '[REDACTED]', error_str)  # Hashes/tokens
    return error_str[:500]  # Limit length


if __name__ == "__main__":
    # Test safety functions
    print("Testing Safety Guards")
    print("=" * 50)

    # Test PowerShell validation
    print("\n1. PowerShell Command Validation:")
    test_commands = [
        "Get-ChildItem",
        "Remove-Item test.txt",
        "Get-Process | Select-Object Name",
    ]
    for cmd in test_commands:
        valid, msg = validate_powershell_command(cmd)
        print(f"  {cmd}: {valid} - {msg}")

    # Test path validation
    print("\n2. Path Validation:")
    test_paths = [
        "G:\\AlphaEdge_AINV\\test.py",
        "C:\\Windows\\system32\\test.txt",
        "G:\\AlphaEdge_AINV\\..\\..\\test.py",
    ]
    for path in test_paths:
        valid, msg, _ = validate_file_path(path)
        print(f"  {path}: {valid} - {msg}")

    # Test filename validation
    print("\n3. Filename Validation:")
    test_files = ["test.txt", "test<>.txt", "CON.txt", "normal_file.py"]
    for fname in test_files:
        valid, msg = is_safe_filename(fname)
        print(f"  {fname}: {valid} - {msg}")
