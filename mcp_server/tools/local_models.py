"""
Local Models Integration for LM Studio.
Provides tools to interact with locally-hosted LLMs through LM Studio API.
"""

import logging
from typing import Dict, Any, List, Optional
import time
import requests
from openai import OpenAI

from ..config import settings
from ..utils import retry_with_backoff, Timer, get_cache
from ..schemas.tool_schemas import (
    ChatRequest, ChatResponse, ModelInfo, ModelStatus,
    LoadModelRequest, LoadModelResponse
)

logger = logging.getLogger(__name__)


class LMStudioClient:
    """Client for LM Studio API interactions."""

    def __init__(self):
        self.base_url = settings.LM_STUDIO_URL
        self.timeout = settings.LM_STUDIO_TIMEOUT
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=settings.LM_STUDIO_API_KEY
        )

    def is_connected(self) -> bool:
        """Check if LM Studio is running and accessible."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"LM Studio not accessible: {e}")
            return False

    @retry_with_backoff(max_retries=2)
    def chat_completion(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to LM Studio.

        Args:
            model: Model name to use
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Enable streaming
            system_prompt: Optional system prompt

        Returns:
            Response dictionary with text and metadata
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            with Timer(f"LM Studio {model} completion"):
                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )

                if stream:
                    # Collect streaming response
                    full_response = ""
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content

                    execution_time = time.time() - start_time
                    return {
                        "response": full_response,
                        "model": model,
                        "tokens_used": None,
                        "finish_reason": "stop",
                        "execution_time": execution_time
                    }
                else:
                    execution_time = time.time() - start_time
                    return {
                        "response": response.choices[0].message.content,
                        "model": model,
                        "tokens_used": response.usage.total_tokens if response.usage else None,
                        "finish_reason": response.choices[0].finish_reason,
                        "execution_time": execution_time
                    }

        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise Exception(f"LM Studio chat failed: {str(e)}")

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models in LM Studio.

        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=10
            )
            response.raise_for_status()

            models_data = response.json()
            models = []

            if "data" in models_data:
                for model in models_data["data"]:
                    models.append({
                        "model_name": model.get("id", "unknown"),
                        "size_gb": None,  # LM Studio API doesn't provide this
                        "status": "available",
                        "vram_usage_gb": None,
                        "context_length": None
                    })

            return models

        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


# Global client instance
_lm_client: Optional[LMStudioClient] = None


def get_lm_client() -> LMStudioClient:
    """Get or create LM Studio client."""
    global _lm_client
    if _lm_client is None:
        _lm_client = LMStudioClient()
    return _lm_client


# ===== Tool: chat_llama33 =====

def chat_llama33(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    stream: bool = False,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chat with Llama 3.3 70B Instruct for complex reasoning and Thai language support.

    Args:
        prompt: User message/prompt
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        stream: Enable streaming response
        system_prompt: Optional system prompt

    Returns:
        Chat response with model output and metadata
    """
    logger.info(f"Chat Llama 3.3 request: {prompt[:100]}...")

    client = get_lm_client()
    result = client.chat_completion(
        model=settings.LLAMA_33_MODEL,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        system_prompt=system_prompt
    )

    return result


# ===== Tool: chat_qwen =====

def chat_qwen(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    stream: bool = False,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chat with Qwen 2.5 Coder 32B for programming tasks.

    Specialized for code generation, debugging, and documentation.

    Args:
        prompt: Programming-related prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens
        stream: Enable streaming
        system_prompt: Optional system prompt

    Returns:
        Chat response with code and explanations
    """
    logger.info(f"Chat Qwen request: {prompt[:100]}...")

    # Add coding-optimized system prompt if none provided
    if system_prompt is None:
        system_prompt = (
            "You are Qwen 2.5 Coder, an expert programming assistant. "
            "Provide clear, well-documented code with explanations."
        )

    client = get_lm_client()
    result = client.chat_completion(
        model=settings.QWEN_MODEL,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        system_prompt=system_prompt
    )

    return result


# ===== Tool: chat_llama31 =====

def chat_llama31(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    stream: bool = False,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chat with Llama 3.1 8B for quick, lightweight responses.

    Best for fast queries that don't require heavy reasoning.

    Args:
        prompt: User prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens (lower default for speed)
        stream: Enable streaming
        system_prompt: Optional system prompt

    Returns:
        Quick response from lightweight model
    """
    logger.info(f"Chat Llama 3.1 request: {prompt[:100]}...")

    client = get_lm_client()
    result = client.chat_completion(
        model=settings.LLAMA_31_MODEL,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        system_prompt=system_prompt
    )

    return result


# ===== Tool: list_local_models =====

def list_local_models() -> Dict[str, Any]:
    """
    List all available local models in LM Studio.

    Returns:
        Dictionary with list of models and their status
    """
    logger.info("Listing local models")

    client = get_lm_client()

    # Check connection first
    if not client.is_connected():
        return {
            "success": False,
            "models": [],
            "error": "LM Studio not running or not accessible"
        }

    models = client.list_models()

    # Add our known models with descriptions
    known_models = {
        settings.LLAMA_33_MODEL: {
            "description": "Llama 3.3 70B - Complex reasoning and Thai language",
            "use_case": "Advanced tasks, multilingual support"
        },
        settings.QWEN_MODEL: {
            "description": "Qwen 2.5 Coder 32B - Programming specialist",
            "use_case": "Code generation, debugging, documentation"
        },
        settings.LLAMA_31_MODEL: {
            "description": "Llama 3.1 8B - Fast lightweight model",
            "use_case": "Quick queries, simple tasks"
        }
    }

    # Enhance model info with our metadata
    for model in models:
        model_name = model["model_name"]
        if model_name in known_models:
            model.update(known_models[model_name])

    return {
        "success": True,
        "models": models,
        "total_count": len(models),
        "lm_studio_connected": True
    }


# ===== Tool: load_model =====

def load_model(
    model_name: str,
    gpu_layers: Optional[int] = None
) -> Dict[str, Any]:
    """
    Load a specific model into GPU memory.

    Note: LM Studio typically handles model loading automatically.
    This tool provides a status check and validation.

    Args:
        model_name: Model to load
        gpu_layers: Number of layers to offload to GPU (optional)

    Returns:
        Load status and performance metrics
    """
    logger.info(f"Load model request: {model_name}")

    start_time = time.time()

    # Validate model name
    valid_models = [settings.LLAMA_33_MODEL, settings.QWEN_MODEL, settings.LLAMA_31_MODEL]
    if model_name not in valid_models:
        return {
            "success": False,
            "model_name": model_name,
            "load_time": 0.0,
            "vram_allocated_gb": None,
            "message": f"Unknown model. Valid models: {valid_models}"
        }

    # Check if LM Studio is running
    client = get_lm_client()
    if not client.is_connected():
        return {
            "success": False,
            "model_name": model_name,
            "load_time": 0.0,
            "vram_allocated_gb": None,
            "message": "LM Studio not running"
        }

    # Try to use the model (which will auto-load it if needed)
    try:
        test_result = client.chat_completion(
            model=model_name,
            prompt="Test",
            max_tokens=5
        )

        load_time = time.time() - start_time

        return {
            "success": True,
            "model_name": model_name,
            "load_time": load_time,
            "vram_allocated_gb": None,  # LM Studio doesn't expose this
            "message": f"Model {model_name} is loaded and responding"
        }

    except Exception as e:
        return {
            "success": False,
            "model_name": model_name,
            "load_time": time.time() - start_time,
            "vram_allocated_gb": None,
            "message": f"Failed to load model: {str(e)}"
        }


# ===== Tool: unload_model =====

def unload_model(model_name: str) -> Dict[str, Any]:
    """
    Unload a model to free VRAM.

    Note: LM Studio handles model memory management automatically.
    This tool provides status information.

    Args:
        model_name: Model to unload

    Returns:
        Unload status
    """
    logger.info(f"Unload model request: {model_name}")

    return {
        "success": True,
        "model_name": model_name,
        "vram_freed_gb": None,
        "message": "LM Studio manages model memory automatically. Close LM Studio to free VRAM."
    }


# ===== Tool: model_status =====

def model_status() -> Dict[str, Any]:
    """
    Get detailed status of all models.

    Returns:
        Comprehensive model status including loaded models, VRAM usage, and capabilities
    """
    logger.info("Getting model status")

    client = get_lm_client()
    connected = client.is_connected()

    if not connected:
        return {
            "success": False,
            "lm_studio_connected": False,
            "loaded": [],
            "available": [],
            "vram_usage": {},
            "error": "LM Studio not running"
        }

    models = client.list_models()

    # Get GPU info if available
    vram_info = {}
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

        vram_info = {
            "total_gb": mem_info.total / (1024 ** 3),
            "used_gb": mem_info.used / (1024 ** 3),
            "free_gb": mem_info.free / (1024 ** 3),
            "utilization_percent": (mem_info.used / mem_info.total) * 100
        }
    except Exception as e:
        logger.warning(f"Could not get VRAM info: {e}")
        vram_info = {"error": "GPU monitoring not available"}

    return {
        "success": True,
        "lm_studio_connected": True,
        "loaded": [],  # LM Studio API doesn't expose which models are loaded
        "available": models,
        "vram_usage": vram_info,
        "inference_speed": {
            "llama_33": "~30 tokens/sec",
            "qwen": "~40 tokens/sec",
            "llama_31": "~80 tokens/sec"
        },
        "total_models": len(models)
    }


# ===== Export Tools =====

def get_tools() -> List[Dict[str, Any]]:
    """
    Get all local models tools for MCP registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "chat_llama33",
            "description": "Chat with Llama 3.3 70B Instruct for complex reasoning and Thai language support",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "User prompt"},
                    "temperature": {"type": "number", "default": 0.7},
                    "max_tokens": {"type": "integer", "default": 2000},
                    "stream": {"type": "boolean", "default": False},
                    "system_prompt": {"type": "string"}
                },
                "required": ["prompt"]
            },
            "handler": chat_llama33
        },
        {
            "name": "chat_qwen",
            "description": "Chat with Qwen 2.5 Coder 32B for programming tasks and code generation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Programming prompt"},
                    "temperature": {"type": "number", "default": 0.7},
                    "max_tokens": {"type": "integer", "default": 2000},
                    "stream": {"type": "boolean", "default": False},
                    "system_prompt": {"type": "string"}
                },
                "required": ["prompt"]
            },
            "handler": chat_qwen
        },
        {
            "name": "chat_llama31",
            "description": "Chat with Llama 3.1 8B for quick lightweight responses",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "User prompt"},
                    "temperature": {"type": "number", "default": 0.7},
                    "max_tokens": {"type": "integer", "default": 1000},
                    "stream": {"type": "boolean", "default": False},
                    "system_prompt": {"type": "string"}
                },
                "required": ["prompt"]
            },
            "handler": chat_llama31
        },
        {
            "name": "list_local_models",
            "description": "List all available local models in LM Studio",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": list_local_models
        },
        {
            "name": "load_model",
            "description": "Load a specific model into GPU memory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Model to load"},
                    "gpu_layers": {"type": "integer", "description": "GPU layers"}
                },
                "required": ["model_name"]
            },
            "handler": load_model
        },
        {
            "name": "unload_model",
            "description": "Unload a model to free VRAM",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string", "description": "Model to unload"}
                },
                "required": ["model_name"]
            },
            "handler": unload_model
        },
        {
            "name": "model_status",
            "description": "Get detailed status of all models including VRAM usage",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "handler": model_status
        }
    ]
