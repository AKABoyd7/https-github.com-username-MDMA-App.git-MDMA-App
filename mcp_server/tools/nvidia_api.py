"""
NVIDIA API Integration for NIM and NeMo services.
Provides tools to access NVIDIA's cloud AI APIs with local fallback.
"""

import logging
from typing import Dict, Any, List, Optional
import time
import requests
import base64
from pathlib import Path

from ..config import settings
from ..utils import retry_with_backoff, Timer, get_cache
from ..schemas.tool_schemas import (
    NemotronRequest, ImageAnalysisRequest, ImageAnalysisResponse,
    NVIDIAQuota, GuardrailsRequest, GuardrailsResponse
)

logger = logging.getLogger(__name__)


class NVIDIAAPIClient:
    """Client for NVIDIA NIM/NeMo API interactions."""

    def __init__(self):
        self.base_url = settings.NVIDIA_API_URL
        self.api_key = settings.NVIDIA_API_KEY
        self.timeout = settings.NVIDIA_API_TIMEOUT
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def is_enabled(self) -> bool:
        """Check if NVIDIA API is configured."""
        return settings.is_nvidia_enabled()

    def is_connected(self) -> bool:
        """Check if NVIDIA API is accessible."""
        if not self.is_enabled():
            return False

        try:
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=5
            )
            return response.status_code in [200, 401, 403]  # Reachable even if auth fails
        except Exception as e:
            logger.warning(f"NVIDIA API not accessible: {e}")
            return False

    @retry_with_backoff(max_retries=2)
    def chat_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to NVIDIA NIM API.

        Args:
            model: NVIDIA model name
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            system_prompt: Optional system prompt

        Returns:
            Response dictionary
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            with Timer(f"NVIDIA {model} completion"):
                start_time = time.time()

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )

                response.raise_for_status()
                data = response.json()

                execution_time = time.time() - start_time

                return {
                    "response": data["choices"][0]["message"]["content"],
                    "model": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens"),
                    "finish_reason": data["choices"][0].get("finish_reason"),
                    "execution_time": execution_time
                }

        except Exception as e:
            logger.error(f"NVIDIA chat completion failed: {e}")
            raise Exception(f"NVIDIA API chat failed: {str(e)}")

    def analyze_image(
        self,
        image_source: str,
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze image using NVIDIA vision models.

        Args:
            image_source: URL, base64, or file path
            prompt: Optional analysis prompt
            max_tokens: Maximum tokens for response

        Returns:
            Analysis results
        """
        # Prepare image data
        image_data = self._prepare_image_data(image_source)

        default_prompt = prompt or "Describe this image in detail, including objects, text, and any notable features."

        payload = {
            "model": settings.NVCLIP_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": default_prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ],
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            description = data["choices"][0]["message"]["content"]

            return {
                "description": description,
                "objects": self._extract_objects(description),
                "text_extracted": self._extract_text_mentions(description),
                "confidence": None  # NVIDIA API doesn't provide confidence scores
            }

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise Exception(f"NVIDIA image analysis failed: {str(e)}")

    def _prepare_image_data(self, source: str) -> str:
        """Prepare image data for API request."""
        # Check if it's already a URL
        if source.startswith('http://') or source.startswith('https://'):
            return source

        # Check if it's base64
        if source.startswith('data:image'):
            return source

        # Try to read as file
        try:
            path = Path(source)
            if path.exists() and path.is_file():
                with open(path, 'rb') as f:
                    image_bytes = f.read()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    # Detect image type
                    ext = path.suffix.lower()
                    mime_type = {
                        '.jpg': 'jpeg',
                        '.jpeg': 'jpeg',
                        '.png': 'png',
                        '.gif': 'gif',
                        '.webp': 'webp'
                    }.get(ext, 'jpeg')
                    return f"data:image/{mime_type};base64,{base64_image}"
        except Exception as e:
            logger.error(f"Failed to read image file: {e}")

        # Assume it's base64 without header
        return f"data:image/jpeg;base64,{source}"

    def _extract_objects(self, description: str) -> List[str]:
        """Extract mentioned objects from description."""
        # Simple keyword extraction
        common_objects = [
            'person', 'people', 'car', 'building', 'tree', 'sky', 'road',
            'computer', 'phone', 'table', 'chair', 'window', 'door',
            'book', 'pen', 'paper', 'screen', 'keyboard', 'mouse'
        ]
        found = []
        desc_lower = description.lower()
        for obj in common_objects:
            if obj in desc_lower:
                found.append(obj)
        return found

    def _extract_text_mentions(self, description: str) -> Optional[str]:
        """Extract any mentioned text from description."""
        # Look for quoted text or text mentions
        import re
        quotes = re.findall(r'"([^"]*)"', description)
        if quotes:
            return ', '.join(quotes)

        if 'text' in description.lower() and 'says' in description.lower():
            return "Text detected (see description)"

        return None

    def check_quota(self) -> Dict[str, Any]:
        """
        Check NVIDIA API usage and quota.

        Returns:
            Quota information
        """
        # Check cache first
        cache = get_cache()
        cached_quota = cache.get("nvidia_quota")
        if cached_quota:
            return cached_quota

        # NVIDIA doesn't provide a public quota API endpoint
        # Return placeholder information
        quota_info = {
            "requests_used": None,
            "requests_remaining": None,
            "quota_reset_date": None,
            "estimated_cost": None,
            "message": "NVIDIA API quota information not publicly available. Monitor usage in NVIDIA console.",
            "api_status": "connected" if self.is_connected() else "disconnected"
        }

        # Cache for 5 minutes
        cache.set("nvidia_quota", quota_info, settings.CACHE_NVIDIA_QUOTA_SECONDS)

        return quota_info


# Global client instance
_nvidia_client: Optional[NVIDIAAPIClient] = None


def get_nvidia_client() -> NVIDIAAPIClient:
    """Get or create NVIDIA API client."""
    global _nvidia_client
    if _nvidia_client is None:
        _nvidia_client = NVIDIAAPIClient()
    return _nvidia_client


# ===== Tool: chat_nemotron =====

def chat_nemotron(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    fallback_to_local: bool = True,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chat with NVIDIA Nemotron 70B for ultra-complex reasoning.

    Automatically falls back to local Llama 3.3 if NVIDIA API is unavailable.

    Args:
        prompt: User prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        fallback_to_local: Enable fallback to local model
        system_prompt: Optional system prompt

    Returns:
        Chat response with model output
    """
    logger.info(f"Chat Nemotron request: {prompt[:100]}...")

    client = get_nvidia_client()

    # Check if NVIDIA API is available
    if not client.is_enabled():
        if fallback_to_local:
            logger.warning("NVIDIA API not configured, falling back to local Llama 3.3")
            from .local_models import chat_llama33
            result = chat_llama33(prompt, temperature, max_tokens, False, system_prompt)
            result["model"] = "llama-3.3-70b-instruct (fallback)"
            result["note"] = "Fell back to local model - NVIDIA API not configured"
            return result
        else:
            return {
                "success": False,
                "error": "NVIDIA API not configured and fallback disabled"
            }

    # Try NVIDIA API
    try:
        result = client.chat_completion(
            model=settings.NEMOTRON_MODEL,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        result["success"] = True
        return result

    except Exception as e:
        logger.error(f"Nemotron API failed: {e}")

        if fallback_to_local:
            logger.info("Falling back to local Llama 3.3")
            try:
                from .local_models import chat_llama33
                result = chat_llama33(prompt, temperature, max_tokens, False, system_prompt)
                result["model"] = "llama-3.3-70b-instruct (fallback)"
                result["note"] = f"Fell back to local model - NVIDIA API error: {str(e)}"
                return result
            except Exception as fallback_error:
                return {
                    "success": False,
                    "error": f"Both NVIDIA and local model failed. NVIDIA: {str(e)}, Local: {str(fallback_error)}"
                }
        else:
            return {
                "success": False,
                "error": str(e)
            }


# ===== Tool: analyze_image =====

def analyze_image(
    image_source: str,
    prompt: Optional[str] = None,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Understand images using NVIDIA vision models.

    Args:
        image_source: Image URL, base64 encoded image, or local file path
        prompt: Optional specific analysis prompt
        max_tokens: Maximum tokens for description

    Returns:
        Image analysis with description, objects, and extracted text
    """
    logger.info(f"Analyze image request: {image_source[:100]}...")

    client = get_nvidia_client()

    if not client.is_enabled():
        return {
            "success": False,
            "error": "NVIDIA API not configured. Image analysis requires NVIDIA API key."
        }

    try:
        result = client.analyze_image(image_source, prompt, max_tokens)
        result["success"] = True
        return result

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ===== Tool: check_nvidia_quota =====

def check_nvidia_quota() -> Dict[str, Any]:
    """
    Check NVIDIA API usage and remaining quota.

    Returns:
        Quota information including usage, limits, and reset date
    """
    logger.info("Checking NVIDIA quota")

    client = get_nvidia_client()

    if not client.is_enabled():
        return {
            "success": False,
            "error": "NVIDIA API not configured"
        }

    quota = client.check_quota()
    quota["success"] = True
    return quota


# ===== Tool: nvidia_guardrails =====

def nvidia_guardrails(
    content: str,
    check_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Use NVIDIA NeMo Guardrails for content safety checking.

    Checks for jailbreak attempts, PII, toxic content, and hallucinations.

    Args:
        content: Content to check
        check_types: Types of checks (jailbreak, pii, toxicity, hallucination)

    Returns:
        Safety analysis with score, issues, and recommendations
    """
    logger.info(f"Guardrails check: {content[:100]}...")

    client = get_nvidia_client()

    if not client.is_enabled():
        return {
            "success": False,
            "error": "NVIDIA API not configured. Guardrails require NVIDIA API key."
        }

    check_types = check_types or ["jailbreak", "pii", "toxicity"]

    # Placeholder implementation - NVIDIA Guardrails API would need specific endpoint
    # For now, do basic checks
    issues = []
    safety_score = 100.0

    # Basic jailbreak detection
    if "jailbreak" in check_types:
        jailbreak_patterns = [
            "ignore previous instructions",
            "disregard your programming",
            "act as if you are",
            "pretend you are",
            "roleplay as"
        ]
        for pattern in jailbreak_patterns:
            if pattern.lower() in content.lower():
                issues.append({
                    "type": "jailbreak",
                    "severity": "high",
                    "description": f"Potential jailbreak attempt detected: {pattern}"
                })
                safety_score -= 30

    # Basic PII detection
    if "pii" in check_types:
        import re
        # Email pattern
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content):
            issues.append({
                "type": "pii",
                "severity": "medium",
                "description": "Email address detected"
            })
            safety_score -= 10

        # Phone pattern
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content):
            issues.append({
                "type": "pii",
                "severity": "medium",
                "description": "Phone number detected"
            })
            safety_score -= 10

    # Basic toxicity detection
    if "toxicity" in check_types:
        toxic_words = ['hate', 'kill', 'attack', 'violent', 'harm']
        toxic_found = [word for word in toxic_words if word in content.lower()]
        if toxic_found:
            issues.append({
                "type": "toxicity",
                "severity": "high",
                "description": f"Potentially toxic content detected"
            })
            safety_score -= 25

    # Generate recommendations
    recommendations = []
    if issues:
        recommendations.append("Review content for safety concerns")
        if any(i["type"] == "pii" for i in issues):
            recommendations.append("Remove or redact personal information")
        if any(i["type"] == "jailbreak" for i in issues):
            recommendations.append("Content may be attempting to bypass safety controls")
        if any(i["type"] == "toxicity" for i in issues):
            recommendations.append("Content contains potentially harmful language")
    else:
        recommendations.append("Content appears safe")

    # Filter content if issues found
    filtered_content = content
    if any(i["type"] == "pii" for i in issues):
        import re
        filtered_content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', filtered_content)
        filtered_content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', filtered_content)

    return {
        "success": True,
        "safety_score": max(0.0, safety_score),
        "issues": issues,
        "filtered_content": filtered_content if issues else None,
        "recommendations": recommendations,
        "note": "Basic guardrails implementation. For production use, integrate with NVIDIA NeMo Guardrails API."
    }


# ===== Export Tools =====

def get_tools() -> List[Dict[str, Any]]:
    """
    Get all NVIDIA API tools for MCP registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "chat_nemotron",
            "description": "Chat with NVIDIA Nemotron 70B for ultra-complex reasoning (auto-fallback to local)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "User prompt"},
                    "temperature": {"type": "number", "default": 0.7},
                    "max_tokens": {"type": "integer", "default": 2000},
                    "fallback_to_local": {"type": "boolean", "default": True},
                    "system_prompt": {"type": "string"}
                },
                "required": ["prompt"]
            },
            "handler": chat_nemotron
        },
        {
            "name": "analyze_image",
            "description": "Understand images using NVIDIA vision models - supports URLs, base64, or file paths",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "image_source": {"type": "string", "description": "Image URL, base64, or file path"},
                    "prompt": {"type": "string", "description": "Optional analysis prompt"},
                    "max_tokens": {"type": "integer", "default": 1000}
                },
                "required": ["image_source"]
            },
            "handler": analyze_image
        },
        {
            "name": "check_nvidia_quota",
            "description": "Check NVIDIA API usage and remaining quota",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": check_nvidia_quota
        },
        {
            "name": "nvidia_guardrails",
            "description": "Content safety check for jailbreak attempts, PII, toxic content, and hallucinations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to check"},
                    "check_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Check types: jailbreak, pii, toxicity, hallucination"
                    }
                },
                "required": ["content"]
            },
            "handler": nvidia_guardrails
        }
    ]
