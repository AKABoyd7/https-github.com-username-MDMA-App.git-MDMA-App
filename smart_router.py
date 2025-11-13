"""
Smart Inference Router with Hybrid Fallback
Automatically routes requests to TensorRT or Cloud API
"""
import asyncio
import logging
from typing import Optional, Dict, Any
from enum import Enum

from tensorrt_engine import TensorRTEngine, TensorRTNotReady

logger = logging.getLogger(__name__)


class InferenceBackend(Enum):
    TENSORRT = "tensorrt"
    OLLAMA = "ollama"
    CLOUD = "cloud"


class SmartInferenceRouter:
    """
    Intelligent routing between TensorRT (local) and Cloud API (fallback)

    Features:
    - Automatic failover
    - Health monitoring
    - Performance tracking
    - Smart backend selection
    """

    def __init__(self,
                 tensorrt_model_path: Optional[str] = None,
                 use_ollama: bool = True,
                 enable_cloud_fallback: bool = False):
        """
        Initialize router

        Args:
            tensorrt_model_path: Path to TensorRT engine
            use_ollama: Use Ollama as primary backend
            enable_cloud_fallback: Enable cloud API fallback
        """
        self.tensorrt_engine = None
        self.ollama_available = use_ollama
        self.cloud_fallback = enable_cloud_fallback

        # Try to initialize TensorRT
        if tensorrt_model_path:
            try:
                self.tensorrt_engine = TensorRTEngine(tensorrt_model_path)
                self.tensorrt_engine.initialize()
                logger.info("✅ TensorRT engine ready")
            except Exception as e:
                logger.warning(f"TensorRT initialization failed: {e}")
                self.tensorrt_engine = None

        # Track current backend
        self.current_backend = self._select_backend()
        logger.info(f"Using backend: {self.current_backend.value}")

    def _select_backend(self) -> InferenceBackend:
        """Select best available backend"""
        if self.tensorrt_engine and self.tensorrt_engine.is_healthy():
            return InferenceBackend.TENSORRT
        elif self.ollama_available:
            return InferenceBackend.OLLAMA
        elif self.cloud_fallback:
            return InferenceBackend.CLOUD
        else:
            raise RuntimeError("No inference backend available")

    async def generate(self,
                      prompt: str,
                      max_tokens: int = 512,
                      temperature: float = 0.7,
                      **kwargs) -> Dict[str, Any]:
        """
        Generate response using best available backend

        Args:
            prompt: Input text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Dict with response and metadata
        """
        backend = self.current_backend

        try:
            # Try TensorRT first (fastest)
            if backend == InferenceBackend.TENSORRT:
                response = await self._generate_tensorrt(prompt, max_tokens, temperature)
                return {
                    'response': response,
                    'backend': 'tensorrt',
                    'success': True
                }

            # Fallback to Ollama
            elif backend == InferenceBackend.OLLAMA:
                response = await self._generate_ollama(prompt, max_tokens, temperature)
                return {
                    'response': response,
                    'backend': 'ollama',
                    'success': True
                }

            # Last resort: Cloud API
            elif backend == InferenceBackend.CLOUD:
                response = await self._generate_cloud(prompt, max_tokens, temperature)
                return {
                    'response': response,
                    'backend': 'cloud',
                    'success': True
                }

        except Exception as e:
            logger.error(f"Generation failed with {backend.value}: {e}")

            # Try fallback
            return await self._fallback_generate(prompt, max_tokens, temperature, failed_backend=backend)

    async def _generate_tensorrt(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using TensorRT"""
        if not self.tensorrt_engine or not self.tensorrt_engine.is_healthy():
            raise TensorRTNotReady("TensorRT engine not ready")

        return await self.tensorrt_engine.generate(prompt, max_tokens, temperature)

    async def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Ollama"""
        try:
            from langchain_community.chat_models import ChatOllama
            from langchain_core.messages import HumanMessage

            model = ChatOllama(model="llama3", temperature=temperature)
            response = model.invoke([HumanMessage(content=prompt)])
            return response.content

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def _generate_cloud(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Cloud API (placeholder)"""
        # TODO: Implement cloud API integration
        raise NotImplementedError("Cloud API not implemented yet")

    async def _fallback_generate(self,
                                 prompt: str,
                                 max_tokens: int,
                                 temperature: float,
                                 failed_backend: InferenceBackend) -> Dict[str, Any]:
        """
        Fallback generation when primary backend fails
        """
        logger.warning(f"Attempting fallback from {failed_backend.value}")

        # Try other backends in order
        backends_to_try = []

        if failed_backend != InferenceBackend.OLLAMA and self.ollama_available:
            backends_to_try.append(InferenceBackend.OLLAMA)

        if failed_backend != InferenceBackend.CLOUD and self.cloud_fallback:
            backends_to_try.append(InferenceBackend.CLOUD)

        for backend in backends_to_try:
            try:
                if backend == InferenceBackend.OLLAMA:
                    response = await self._generate_ollama(prompt, max_tokens, temperature)
                elif backend == InferenceBackend.CLOUD:
                    response = await self._generate_cloud(prompt, max_tokens, temperature)

                logger.info(f"✅ Fallback successful with {backend.value}")
                return {
                    'response': response,
                    'backend': backend.value,
                    'success': True,
                    'fallback': True
                }

            except Exception as e:
                logger.error(f"Fallback {backend.value} also failed: {e}")
                continue

        # All backends failed
        return {
            'response': None,
            'backend': None,
            'success': False,
            'error': 'All inference backends failed'
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current router status"""
        return {
            'current_backend': self.current_backend.value,
            'tensorrt_available': self.tensorrt_engine is not None and self.tensorrt_engine.is_healthy(),
            'ollama_available': self.ollama_available,
            'cloud_fallback_enabled': self.cloud_fallback,
            'metrics': self.tensorrt_engine.get_metrics() if self.tensorrt_engine else {}
        }
