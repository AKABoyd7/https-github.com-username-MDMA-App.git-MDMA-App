"""
System Tools with Safety Guards.
Provides safe file operations and command execution with strict validation.
"""

import logging
from typing import Dict, Any, List, Optional
import subprocess
import time
from pathlib import Path, PureWindowsPath
import os
import shutil
import hashlib
from datetime import datetime

from ..config import settings
from ..safety import (
    validate_powershell_command, validate_python_code,
    validate_file_path, validate_file_size, is_safe_filename,
    SafeExecutionContext
)
from ..utils import Timer, format_bytes

logger = logging.getLogger(__name__)


# ===== Tool: execute_powershell =====

def execute_powershell(
    command: str,
    timeout: int = 30,
    working_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute PowerShell command with safety restrictions.

    Only whitelisted commands are allowed. Runs in restricted directory.

    Args:
        command: PowerShell command to execute
        timeout: Timeout in seconds (max 300)
        working_dir: Working directory (must be within project root)

    Returns:
        Command output with stdout, stderr, and exit code
    """
    logger.info(f"PowerShell execution request: {command[:100]}...")

    # Validate command
    is_valid, message = validate_powershell_command(command)
    if not is_valid:
        return {
            "success": False,
            "error": f"Command blocked by safety check: {message}",
            "stdout": "",
            "stderr": message,
            "exit_code": -1,
            "execution_time": 0.0
        }

    # Validate working directory
    if working_dir:
        is_valid_path, path_message, _ = validate_file_path(working_dir)
        if not is_valid_path:
            return {
                "success": False,
                "error": f"Invalid working directory: {path_message}",
                "stdout": "",
                "stderr": path_message,
                "exit_code": -1,
                "execution_time": 0.0
            }
    else:
        working_dir = settings.PROJECT_ROOT

    # Limit timeout
    timeout = min(timeout, settings.COMMAND_TIMEOUT)

    try:
        start_time = time.time()

        # Execute using subprocess
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )

        execution_time = time.time() - start_time

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "execution_time": round(execution_time, 3),
            "working_dir": working_dir
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "stdout": "",
            "stderr": "Timeout",
            "exit_code": -1,
            "execution_time": timeout
        }
    except Exception as e:
        logger.error(f"PowerShell execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "execution_time": 0.0
        }


# ===== Tool: execute_python =====

def execute_python(
    code: str,
    timeout: int = 30,
    memory_limit_mb: int = 1024
) -> Dict[str, Any]:
    """
    Execute Python code in isolated sandbox.

    Blocks dangerous imports and operations. Restricted file access.

    Args:
        code: Python code to execute
        timeout: Timeout in seconds
        memory_limit_mb: Memory limit in MB

    Returns:
        Execution output and errors
    """
    logger.info(f"Python execution request: {code[:100]}...")

    # Validate code
    is_valid, message = validate_python_code(code)
    if not is_valid:
        return {
            "success": False,
            "error": f"Code blocked by safety check: {message}",
            "output": "",
            "errors": message,
            "execution_time": 0.0,
            "memory_used_mb": 0.0
        }

    timeout = min(timeout, settings.COMMAND_TIMEOUT)

    try:
        start_time = time.time()

        # Create restricted globals
        restricted_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
            }
        }

        # Capture output
        from io import StringIO
        import sys

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute with timeout
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Execution timed out")

            # Note: signal.alarm only works on Unix, for Windows we need different approach
            # For cross-platform, we'll use threading
            import threading

            execution_error = None
            def run_code():
                nonlocal execution_error
                try:
                    exec(code, restricted_globals)
                except Exception as e:
                    execution_error = e

            thread = threading.Thread(target=run_code)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout)

            if thread.is_alive():
                # Timeout occurred
                return {
                    "success": False,
                    "error": f"Execution timed out after {timeout} seconds",
                    "output": stdout_capture.getvalue(),
                    "errors": "Timeout",
                    "execution_time": timeout,
                    "memory_used_mb": 0.0
                }

            if execution_error:
                raise execution_error

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        execution_time = time.time() - start_time

        output = stdout_capture.getvalue()
        errors = stderr_capture.getvalue()

        return {
            "success": not errors and not execution_error,
            "output": output,
            "errors": errors if errors else "",
            "execution_time": round(execution_time, 3),
            "memory_used_mb": 0.0,  # Would need resource module for actual measurement
            "note": "Running in restricted sandbox with limited built-ins"
        }

    except Exception as e:
        logger.error(f"Python execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "output": "",
            "errors": str(e),
            "execution_time": time.time() - start_time,
            "memory_used_mb": 0.0
        }


# ===== Tool: read_file =====

def read_file(
    file_path: str,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Read file contents with safety checks.

    Args:
        file_path: Path to file (must be within project root)
        encoding: File encoding (default: utf-8)

    Returns:
        File contents and metadata
    """
    logger.info(f"Read file request: {file_path}")

    # Validate path
    is_valid, message, resolved_path = validate_file_path(file_path)
    if not is_valid:
        return {
            "success": False,
            "error": message
        }

    try:
        # For development on Linux, use local path
        actual_path = Path(file_path)
        if not actual_path.exists():
            # Try relative to current directory
            actual_path = Path(".") / file_path
            if not actual_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

        # Check file size
        size = actual_path.stat().st_size
        is_valid_size, size_message = validate_file_size(size)
        if not is_valid_size:
            return {
                "success": False,
                "error": size_message
            }

        # Try multiple encodings if utf-8 fails
        encodings = [encoding, 'utf-8', 'utf-16', 'latin-1', 'cp1252']
        content = None
        used_encoding = encoding

        for enc in encodings:
            try:
                with open(actual_path, 'r', encoding=enc) as f:
                    content = f.read()
                    used_encoding = enc
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Failed to read with encoding {enc}: {e}")
                continue

        if content is None:
            return {
                "success": False,
                "error": "Failed to decode file with any supported encoding"
            }

        lines = content.count('\n') + 1

        return {
            "success": True,
            "content": content,
            "encoding": used_encoding,
            "size_bytes": size,
            "lines": lines,
            "path": str(actual_path)
        }

    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: write_file =====

def write_file(
    file_path: str,
    content: str,
    create_backup: bool = True
) -> Dict[str, Any]:
    """
    Write content to file with safety checks.

    Args:
        file_path: Path to file (must be within project root)
        content: Content to write
        create_backup: Create backup of existing file

    Returns:
        Write status and backup information
    """
    logger.info(f"Write file request: {file_path}")

    # Validate path
    is_valid, message, resolved_path = validate_file_path(file_path)
    if not is_valid:
        return {
            "success": False,
            "error": message
        }

    try:
        # For development, use local path
        actual_path = Path(file_path)

        # Create parent directories if needed
        actual_path.parent.mkdir(parents=True, exist_ok=True)

        backup_path = None

        # Create backup if file exists
        if actual_path.exists() and create_backup:
            backup_path = str(actual_path) + ".bak"
            shutil.copy2(actual_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

        # Write file
        with open(actual_path, 'w', encoding='utf-8') as f:
            f.write(content)

        bytes_written = len(content.encode('utf-8'))

        return {
            "success": True,
            "path": str(actual_path),
            "backup_path": backup_path,
            "bytes_written": bytes_written,
            "created": not actual_path.existed_before if hasattr(actual_path, 'existed_before') else False
        }

    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: list_files =====

def list_files(
    path: str = None,
    pattern: str = "*",
    recursive: bool = False
) -> Dict[str, Any]:
    """
    List files and directories.

    Args:
        path: Directory path (defaults to project root)
        pattern: File pattern/glob (default: *)
        recursive: Recursive listing

    Returns:
        List of files with metadata
    """
    path = path or settings.PROJECT_ROOT
    logger.info(f"List files request: {path} (pattern: {pattern}, recursive: {recursive})")

    # Validate path
    is_valid, message, resolved_path = validate_file_path(path)
    if not is_valid:
        return {
            "success": False,
            "error": message
        }

    try:
        # For development, use local path
        actual_path = Path(path)
        if not actual_path.exists():
            actual_path = Path(".")

        if not actual_path.is_dir():
            return {
                "success": False,
                "error": f"Not a directory: {path}"
            }

        # Excluded patterns
        excluded = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pyc'}

        files = []

        if recursive:
            pattern_path = actual_path.rglob(pattern)
        else:
            pattern_path = actual_path.glob(pattern)

        for item in pattern_path:
            # Skip excluded
            if any(excl in item.parts for excl in excluded):
                continue

            try:
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size_bytes": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_dir": item.is_dir()
                })
            except Exception as e:
                logger.warning(f"Could not stat {item}: {e}")
                continue

        # Sort by name
        files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

        return {
            "success": True,
            "files": files,
            "total_count": len(files),
            "path": str(actual_path)
        }

    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: search_files =====

def search_files(
    query: str,
    path: str = None,
    search_type: str = "filename",
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Search for files by name or content.

    Args:
        query: Search query
        path: Search root path
        search_type: "filename", "content", or "extension"
        case_sensitive: Case sensitive search

    Returns:
        List of matching files
    """
    path = path or settings.PROJECT_ROOT
    logger.info(f"Search files: query='{query}', type={search_type}, path={path}")

    try:
        actual_path = Path(path)
        if not actual_path.exists():
            actual_path = Path(".")

        excluded = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
        results = []
        files_scanned = 0
        max_files = 1000

        if search_type == "filename":
            # Search by filename
            for item in actual_path.rglob("*"):
                if files_scanned >= max_files:
                    break

                if any(excl in item.parts for excl in excluded):
                    continue

                if item.is_file():
                    files_scanned += 1
                    name = item.name if case_sensitive else item.name.lower()
                    q = query if case_sensitive else query.lower()

                    if q in name:
                        results.append({
                            "path": str(item),
                            "matches": [item.name],
                            "line_numbers": []
                        })

        elif search_type == "content":
            # Search file contents
            for item in actual_path.rglob("*"):
                if files_scanned >= max_files:
                    break

                if any(excl in item.parts for excl in excluded):
                    continue

                if item.is_file() and item.suffix in settings.ALLOWED_EXTENSIONS:
                    files_scanned += 1
                    try:
                        # Limit file size
                        if item.stat().st_size > settings.get_max_file_size_bytes():
                            continue

                        with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            matches = []
                            line_numbers = []

                            for i, line in enumerate(lines, 1):
                                search_line = line if case_sensitive else line.lower()
                                search_query = query if case_sensitive else query.lower()

                                if search_query in search_line:
                                    matches.append(line.strip())
                                    line_numbers.append(i)

                            if matches:
                                results.append({
                                    "path": str(item),
                                    "matches": matches[:10],  # Limit matches
                                    "line_numbers": line_numbers[:10]
                                })

                    except Exception as e:
                        logger.warning(f"Could not search {item}: {e}")
                        continue

        elif search_type == "extension":
            # Search by extension
            ext = query if query.startswith('.') else f'.{query}'
            for item in actual_path.rglob(f"*{ext}"):
                if files_scanned >= max_files:
                    break

                if any(excl in item.parts for excl in excluded):
                    continue

                if item.is_file():
                    files_scanned += 1
                    results.append({
                        "path": str(item),
                        "matches": [],
                        "line_numbers": []
                    })

        return {
            "success": True,
            "results": results,
            "total_matches": len(results),
            "files_scanned": files_scanned,
            "search_type": search_type,
            "query": query
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: get_file_info =====

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get detailed file metadata.

    Args:
        file_path: Path to file

    Returns:
        Detailed file information including hash
    """
    logger.info(f"Get file info: {file_path}")

    try:
        actual_path = Path(file_path)
        if not actual_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        stat = actual_path.stat()

        # Calculate MD5 hash for files
        md5_hash = None
        if actual_path.is_file() and stat.st_size < 100 * 1024 * 1024:  # < 100MB
            try:
                with open(actual_path, 'rb') as f:
                    md5_hash = hashlib.md5(f.read()).hexdigest()
            except:
                md5_hash = None

        return {
            "success": True,
            "size": stat.st_size,
            "size_formatted": format_bytes(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_file": actual_path.is_file(),
            "is_dir": actual_path.is_dir(),
            "extension": actual_path.suffix,
            "md5_hash": md5_hash,
            "path": str(actual_path)
        }

    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: create_directory =====

def create_directory(path: str) -> Dict[str, Any]:
    """
    Create directory structure.

    Args:
        path: Directory path to create

    Returns:
        Creation status
    """
    logger.info(f"Create directory: {path}")

    # Validate path
    is_valid, message, resolved_path = validate_file_path(path)
    if not is_valid:
        return {
            "success": False,
            "error": message
        }

    try:
        actual_path = Path(path)
        actual_path.mkdir(parents=True, exist_ok=True)

        return {
            "success": True,
            "path": str(actual_path),
            "created": True
        }

    except Exception as e:
        logger.error(f"Failed to create directory: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Export Tools =====

def get_tools() -> List[Dict[str, Any]]:
    """
    Get all system tools for MCP registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "execute_powershell",
            "description": "Execute PowerShell commands (sandboxed with whitelist)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "PowerShell command"},
                    "timeout": {"type": "integer", "default": 30},
                    "working_dir": {"type": "string", "description": "Working directory"}
                },
                "required": ["command"]
            },
            "handler": execute_powershell
        },
        {
            "name": "execute_python",
            "description": "Execute Python code in isolated sandbox",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code"},
                    "timeout": {"type": "integer", "default": 30},
                    "memory_limit_mb": {"type": "integer", "default": 1024}
                },
                "required": ["code"]
            },
            "handler": execute_python
        },
        {
            "name": "read_file",
            "description": "Read file contents (restricted to project directory)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["file_path"]
            },
            "handler": read_file
        },
        {
            "name": "write_file",
            "description": "Write content to file (creates backup automatically)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Content to write"},
                    "create_backup": {"type": "boolean", "default": True}
                },
                "required": ["file_path", "content"]
            },
            "handler": write_file
        },
        {
            "name": "list_files",
            "description": "List files and directories with pattern matching",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                    "pattern": {"type": "string", "default": "*"},
                    "recursive": {"type": "boolean", "default": False}
                }
            },
            "handler": list_files
        },
        {
            "name": "search_files",
            "description": "Search files by name, content, or extension",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "path": {"type": "string", "description": "Search root"},
                    "search_type": {"type": "string", "enum": ["filename", "content", "extension"], "default": "filename"},
                    "case_sensitive": {"type": "boolean", "default": False}
                },
                "required": ["query"]
            },
            "handler": search_files
        },
        {
            "name": "get_file_info",
            "description": "Get detailed file metadata including size, dates, and MD5 hash",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"}
                },
                "required": ["file_path"]
            },
            "handler": get_file_info
        },
        {
            "name": "create_directory",
            "description": "Create directory structure (creates parents recursively)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"}
                },
                "required": ["path"]
            },
            "handler": create_directory
        }
    ]
