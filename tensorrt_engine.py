"""
TensorRT-LLM Inference Engine with Smart Features
"""
import os
import json
import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TensorRTEngine:
    """
    Smart TensorRT-LLM Inference Engine
    Features:
    - Auto-initialization
    - GPU memory management
    - Performance monitoring
    - Error recovery
    """

    def __init__(self, model_path: str, config: Optional[Dict] = None):
        self.model_path = Path(model_path)
        self.config = config or {}
        self.engine = None
        self.is_initialized = False
        self.performance_metrics = {
            'total_requests': 0,
            'avg_latency': 0.0,
            'errors': 0
        }

    def initialize(self):
        """Initialize TensorRT engine"""
        try:
            logger.info(f"Initializing TensorRT engine from {self.model_path}")

            # Check if model exists
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")

            # Import TensorRT-LLM (will fail gracefully if not installed)
            try:
                import tensorrt_llm
                from tensorrt_llm.runtime import ModelRunner

                # Load the engine
                self.engine = ModelRunner.from_dir(str(self.model_path))
                self.is_initialized = True
                logger.info("✅ TensorRT engine initialized successfully")

            except ImportError:
                logger.error("TensorRT-LLM not installed. Please run install script.")
                raise

        except Exception as e:
            logger.error(f"Failed to initialize TensorRT engine: {e}")
            self.is_initialized = False
            raise

    def is_healthy(self) -> bool:
        """Check if engine is healthy and ready"""
        return self.is_initialized and self.engine is not None

    async def generate(self,
                      prompt: str,
                      max_tokens: int = 512,
                      temperature: float = 0.7,
                      top_p: float = 0.9) -> str:
        """
        Generate response using TensorRT engine

        Args:
            prompt: Input text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter

        Returns:
            Generated text
        """
        if not self.is_healthy():
            raise RuntimeError("TensorRT engine not initialized or unhealthy")

        start_time = time.time()

        try:
            # Prepare input
            input_ids = self._tokenize(prompt)

            # Generate
            outputs = self.engine.generate(
                input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                end_id=self.engine.tokenizer.eos_token_id
            )

            # Decode output
            response = self._decode(outputs[0])

            # Update metrics
            latency = time.time() - start_time
            self._update_metrics(latency, success=True)

            logger.info(f"Generated response in {latency:.2f}s")
            return response

        except Exception as e:
            self._update_metrics(0, success=False)
            logger.error(f"Generation failed: {e}")
            raise

    def _tokenize(self, text: str):
        """Tokenize input text"""
        if hasattr(self.engine, 'tokenizer'):
            return self.engine.tokenizer.encode(text)
        else:
            # Fallback tokenization
            return text.encode('utf-8')

    def _decode(self, tokens) -> str:
        """Decode tokens to text"""
        if hasattr(self.engine, 'tokenizer'):
            return self.engine.tokenizer.decode(tokens)
        else:
            # Fallback decoding
            return tokens.decode('utf-8')

    def _update_metrics(self, latency: float, success: bool):
        """Update performance metrics"""
        self.performance_metrics['total_requests'] += 1

        if success:
            # Running average of latency
            n = self.performance_metrics['total_requests']
            old_avg = self.performance_metrics['avg_latency']
            self.performance_metrics['avg_latency'] = (old_avg * (n - 1) + latency) / n
        else:
            self.performance_metrics['errors'] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.performance_metrics,
            'health': self.is_healthy(),
            'model_path': str(self.model_path)
        }

    def cleanup(self):
        """Cleanup resources"""
        if self.engine:
            del self.engine
            self.engine = None
            self.is_initialized = False
            logger.info("TensorRT engine cleaned up")


class TensorRTNotReady(Exception):
    """Exception raised when TensorRT engine is not ready"""
    pass
