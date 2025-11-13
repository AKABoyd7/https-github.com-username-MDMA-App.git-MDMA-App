#!/usr/bin/env python3
"""
AlphaEdge AINV - Security & Hardening Module
Implements authentication, rate limiting, input validation, and monitoring

Copyright © 2025 AlphaEdge AINV
"""
import os
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import re
from functools import wraps

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# ===== API Key Authentication =====

class APIKeyAuth:
    """API Key Authentication"""

    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        self._load_keys()

    def _load_keys(self):
        """Load API keys from environment or config"""
        # Master API key from environment
        master_key = os.getenv("API_MASTER_KEY")
        if master_key:
            self.api_keys[master_key] = {
                "name": "master",
                "permissions": ["*"],
                "rate_limit": 1000,
                "created_at": datetime.now()
            }

    def generate_key(self, name: str, permissions: List[str] = None, rate_limit: int = 100) -> str:
        """Generate new API key"""
        key = f"aae_{secrets.token_urlsafe(32)}"
        self.api_keys[key] = {
            "name": name,
            "permissions": permissions or ["read"],
            "rate_limit": rate_limit,
            "created_at": datetime.now()
        }
        return key

    def validate_key(self, key: str) -> bool:
        """Validate API key"""
        return key in self.api_keys

    def get_key_info(self, key: str) -> Optional[Dict]:
        """Get API key information"""
        return self.api_keys.get(key)

    async def __call__(self, request: Request) -> str:
        """FastAPI dependency for authentication"""
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key"
            )

        # Extract key (support both "Bearer <key>" and "<key>")
        key = auth_header.replace("Bearer ", "").strip()

        if not self.validate_key(key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        return key


# ===== Rate Limiting =====

class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self):
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": 100,
            "last_update": time.time(),
            "requests": []
        })

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request is within rate limit

        Returns:
            (allowed, error_message)
        """
        bucket = self.buckets[identifier]
        current_time = time.time()

        # Remove old requests outside window
        bucket["requests"] = [
            req_time for req_time in bucket["requests"]
            if current_time - req_time < window_seconds
        ]

        # Check if limit exceeded
        if len(bucket["requests"]) >= max_requests:
            retry_after = window_seconds - (current_time - bucket["requests"][0])
            return False, f"Rate limit exceeded. Retry after {retry_after:.0f} seconds"

        # Add current request
        bucket["requests"].append(current_time)
        return True, None

    async def __call__(self, request: Request):
        """FastAPI dependency for rate limiting"""
        # Use IP address as identifier
        client_ip = request.client.host

        allowed, error = self.check_rate_limit(client_ip, max_requests=100, window_seconds=60)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error
            )


# ===== Input Validation & Sanitization =====

class InputValidator:
    """Input validation and sanitization"""

    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|\;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bUNION\b.*\bSELECT\b)"
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>"
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$()]",
        r"\.\./",
        r"(cat|wget|curl|nc|netcat|bash|sh|cmd|powershell)\s"
    ]

    MAX_INPUT_LENGTH = 10000  # 10KB

    @staticmethod
    def sanitize_string(text: str, max_length: int = None) -> str:
        """Sanitize string input"""
        if not text:
            return ""

        # Limit length
        if max_length:
            text = text[:max_length]
        elif len(text) > InputValidator.MAX_INPUT_LENGTH:
            text = text[:InputValidator.MAX_INPUT_LENGTH]

        # Remove null bytes
        text = text.replace('\x00', '')

        # Normalize whitespace
        text = ' '.join(text.split())

        return text

    @staticmethod
    def validate_no_sql_injection(text: str) -> tuple[bool, Optional[str]]:
        """Check for SQL injection patterns"""
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Potential SQL injection detected"
        return True, None

    @staticmethod
    def validate_no_xss(text: str) -> tuple[bool, Optional[str]]:
        """Check for XSS patterns"""
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Potential XSS attack detected"
        return True, None

    @staticmethod
    def validate_no_command_injection(text: str) -> tuple[bool, Optional[str]]:
        """Check for command injection patterns"""
        for pattern in InputValidator.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                return False, "Potential command injection detected"
        return True, None

    @staticmethod
    def validate_input(text: str, strict: bool = True) -> tuple[bool, Optional[str]]:
        """
        Comprehensive input validation

        Args:
            text: Input text to validate
            strict: If True, apply strict validation

        Returns:
            (is_valid, error_message)
        """
        # Sanitize first
        text = InputValidator.sanitize_string(text)

        # Check length
        if not text:
            return False, "Empty input"

        if strict:
            # Check for SQL injection
            valid, error = InputValidator.validate_no_sql_injection(text)
            if not valid:
                return False, error

            # Check for XSS
            valid, error = InputValidator.validate_no_xss(text)
            if not valid:
                return False, error

            # Check for command injection
            valid, error = InputValidator.validate_no_command_injection(text)
            if not valid:
                return False, error

        return True, None


# ===== Security Headers Middleware =====

class SecurityHeadersMiddleware:
    """Add security headers to responses"""

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

    @staticmethod
    def add_headers(response):
        """Add security headers to response"""
        for header, value in SecurityHeadersMiddleware.SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


# ===== Security Monitoring =====

class SecurityMonitor:
    """Monitor and log security events"""

    def __init__(self):
        self.events: List[Dict] = []
        self.alert_threshold = {
            "failed_auth": 5,
            "rate_limit": 10,
            "validation_error": 20
        }

    def log_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        metadata: Dict = None
    ):
        """Log security event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "severity": severity,
            "message": message,
            "metadata": metadata or {}
        }
        self.events.append(event)

        # Print to console for now
        print(f"[SECURITY] {severity.upper()}: {event_type} - {message}")

        # Check if alert needed
        self._check_alerts(event_type)

    def _check_alerts(self, event_type: str):
        """Check if alert threshold exceeded"""
        recent_events = [
            e for e in self.events[-100:]
            if e["type"] == event_type
            and (datetime.now() - datetime.fromisoformat(e["timestamp"])).seconds < 300
        ]

        threshold = self.alert_threshold.get(event_type, float('inf'))
        if len(recent_events) >= threshold:
            print(f"🚨 ALERT: {event_type} threshold exceeded ({len(recent_events)}/{threshold})")

    def get_recent_events(self, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get recent security events"""
        events = self.events[-limit:]
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events

    def get_statistics(self) -> Dict:
        """Get security statistics"""
        from collections import Counter

        event_types = Counter(e["type"] for e in self.events)
        severities = Counter(e["severity"] for e in self.events)

        return {
            "total_events": len(self.events),
            "event_types": dict(event_types),
            "severities": dict(severities),
            "recent_events": self.get_recent_events(limit=10)
        }


# ===== Global Instances =====

api_key_auth = APIKeyAuth()
rate_limiter = RateLimiter()
input_validator = InputValidator()
security_monitor = SecurityMonitor()


# ===== Helper Functions =====

def require_auth(func: Callable):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request from args/kwargs
        request = kwargs.get('request') or next((arg for arg in args if isinstance(arg, Request)), None)

        if request:
            try:
                await api_key_auth(request)
            except HTTPException as e:
                security_monitor.log_event("failed_auth", "warning", str(e.detail))
                raise

        return await func(*args, **kwargs)

    return wrapper


def validate_input_decorator(func: Callable):
    """Decorator to validate inputs"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Validate string inputs
        for key, value in kwargs.items():
            if isinstance(value, str):
                valid, error = input_validator.validate_input(value)
                if not valid:
                    security_monitor.log_event("validation_error", "warning", error, {"input": key})
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid input: {error}"
                    )

        return await func(*args, **kwargs)

    return wrapper
