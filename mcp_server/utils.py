"""
Utility functions for AlphaEdge AINV MCP Server.
Provides common helpers for API calls, retries, logging, and data processing.
"""

import logging
import time
import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from functools import wraps
import json
from datetime import datetime
from pathlib import Path

from .config import settings


# Type variable for generic retry function
T = TypeVar('T')


# ===== Logging Setup =====

def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO):
    """
    Configure logging for the MCP server.

    Args:
        log_file: Optional log file path (defaults to settings.LOG_FILE)
        level: Logging level
    """
    log_file = log_file or settings.LOG_FILE

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (simple format) - MUST use stderr for MCP!
    import sys
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (detailed format) - will work on Windows
    try:
        # For Linux dev environment, use local file
        if not log_file.startswith('G:'):
            log_file = './mcp_server.log'

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")

    return logger


# ===== Retry Logic =====

def retry_with_backoff(
    max_retries: int = None,
    initial_delay: float = None,
    backoff_multiplier: float = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retries (defaults to settings)
        initial_delay: Initial delay in seconds (defaults to settings)
        backoff_multiplier: Backoff multiplier (defaults to settings)
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    max_retries = max_retries or settings.MAX_RETRIES
    initial_delay = initial_delay or settings.RETRY_DELAY_SECONDS
    backoff_multiplier = backoff_multiplier or settings.RETRY_BACKOFF_MULTIPLIER

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logging.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_multiplier
                    else:
                        logging.error(f"All {max_retries + 1} attempts failed for {func.__name__}")

            raise last_exception

        return wrapper
    return decorator


async def async_retry_with_backoff(
    func: Callable,
    max_retries: int = None,
    initial_delay: float = None,
    backoff_multiplier: float = None,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Async retry with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum retries
        initial_delay: Initial delay in seconds
        backoff_multiplier: Backoff multiplier
        exceptions: Exceptions to catch

    Returns:
        Function result
    """
    max_retries = max_retries or settings.MAX_RETRIES
    initial_delay = initial_delay or settings.RETRY_DELAY_SECONDS
    backoff_multiplier = backoff_multiplier or settings.RETRY_BACKOFF_MULTIPLIER

    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logging.warning(f"Async attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= backoff_multiplier
            else:
                logging.error(f"All async attempts failed")

    raise last_exception


# ===== API Helpers =====

def make_api_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Make HTTP API request with error handling.

    Args:
        url: Request URL
        method: HTTP method
        headers: Request headers
        json_data: JSON body data
        timeout: Request timeout

    Returns:
        Response JSON

    Raises:
        Exception: On request failure
    """
    import requests

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise Exception(f"Request to {url} timed out after {timeout}s")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Could not connect to {url}")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise Exception(f"API request failed: {str(e)}")


# ===== Data Processing =====

def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        bytes_value: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_percentage(value: float, total: float) -> str:
    """
    Format value as percentage of total.

    Args:
        value: Current value
        total: Total value

    Returns:
        Percentage string (e.g., "75.5%")
    """
    if total == 0:
        return "0.0%"
    return f"{(value / total * 100):.1f}%"


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.

    Args:
        json_str: JSON string
        default: Default value on error

    Returns:
        Parsed JSON or default
    """
    try:
        return json.loads(json_str)
    except Exception:
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely convert object to JSON string.

    Args:
        obj: Object to serialize
        default: Default value on error

    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return default


# ===== Timing and Performance =====

class Timer:
    """Context manager for timing code execution."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        logging.debug(f"{self.name} took {self.elapsed:.3f}s")

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.elapsed is not None:
            return self.elapsed
        elif self.start_time is not None:
            return time.time() - self.start_time
        return 0.0


def time_function(func: Callable) -> Callable:
    """
    Decorator to log function execution time.

    Args:
        func: Function to time

    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Timer(func.__name__):
            return func(*args, **kwargs)
    return wrapper


# ===== Cache Helpers =====

class SimpleCache:
    """Simple in-memory cache with TTL."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if time.time() < expiry:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL."""
        expiry = time.time() + ttl_seconds
        self._cache[key] = (value, expiry)

    def clear(self):
        """Clear all cached values."""
        self._cache.clear()

    def remove(self, key: str):
        """Remove specific key from cache."""
        if key in self._cache:
            del self._cache[key]


# Global cache instance
_global_cache = SimpleCache()


def get_cache() -> SimpleCache:
    """Get global cache instance."""
    return _global_cache


# ===== String Helpers =====

def sanitize_for_log(text: str, max_length: int = 500) -> str:
    """
    Sanitize text for safe logging.

    Args:
        text: Text to sanitize
        max_length: Maximum length

    Returns:
        Sanitized text
    """
    # Remove potential secrets
    import re
    text = re.sub(r'(api[_-]?key|token|password|secret)(["\s:=]+)([^\s"]+)', r'\1\2[REDACTED]', text, flags=re.IGNORECASE)
    return truncate_string(text, max_length)


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format timestamp to readable string.

    Args:
        timestamp: Unix timestamp (defaults to now)

    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


# ===== Validation Helpers =====

def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def is_valid_json(json_str: str) -> bool:
    """Check if string is valid JSON."""
    try:
        json.loads(json_str)
        return True
    except Exception:
        return False


# ===== System Helpers =====

def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.

    Returns:
        Dictionary with system info
    """
    import platform
    import psutil

    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": psutil.virtual_memory().total / (1024 ** 3),
        "memory_available_gb": psutil.virtual_memory().available / (1024 ** 3),
    }


if __name__ == "__main__":
    # Test utilities
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Testing utilities")

    # Test formatting
    print(format_bytes(1536))
    print(format_bytes(1536000))
    print(format_bytes(1536000000))

    # Test timer
    with Timer("Test operation"):
        time.sleep(0.1)

    # Test cache
    cache = get_cache()
    cache.set("test", "value", 10)
    print(f"Cached value: {cache.get('test')}")

    # Test system info
    print(f"System info: {get_system_info()}")
