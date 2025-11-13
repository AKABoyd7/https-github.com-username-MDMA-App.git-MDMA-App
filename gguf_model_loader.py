"""
AlphaEdge AINV - GGUF Model Loader
Loads and serves GGUF models from G:\Models_Organized using llama-cpp-python
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class GGUFModelLoader:
    """Load and manage GGUF models"""

    def __init__(self, config_path: str = "models_config.yaml"):
        self.config_path = config_path
        self.models: Dict[str, any] = {}
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load models configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def find_gguf_file(self, model_path: str) -> Optional[Path]:
        """
        Find the best GGUF file in a directory
        Priority: Q6 > Q5 > Q4 > Q8 > F16
        """
        model_dir = Path(model_path)

        if not model_dir.exists():
            logger.warning(f"Model directory not found: {model_path}")
            return None

        # Find all GGUF files
        gguf_files = list(model_dir.rglob("*.gguf"))

        if not gguf_files:
            logger.warning(f"No GGUF files found in {model_path}")
            return None

        # Priority order for quantization
        priorities = {
            'Q6': 5,
            'Q5': 4,
            'Q4': 3,
            'Q8': 2,
            'F16': 1,
            'Q3': 0,
            'Q2': -1
        }

        # Score each file
        scored_files = []
        for gguf_file in gguf_files:
            score = 0
            filename = gguf_file.name.upper()

            for quant, priority in priorities.items():
                if quant in filename:
                    score = priority
                    break

            scored_files.append((score, gguf_file))

        # Sort by score (highest first)
        scored_files.sort(key=lambda x: x[0], reverse=True)

        best_file = scored_files[0][1]
        logger.info(f"Selected model: {best_file.name} from {model_path}")

        return best_file

    def load_model(self, model_id: str, **kwargs) -> Optional[object]:
        """
        Load a GGUF model by ID

        Args:
            model_id: Model identifier from models_config.yaml
            **kwargs: Additional arguments for llama-cpp-python

        Returns:
            Loaded model instance or None
        """
        # Check if already loaded
        if model_id in self.models:
            logger.info(f"Model {model_id} already loaded")
            return self.models[model_id]

        # Get model config
        local_models = self.config.get('local_models', {})
        model_config = local_models.get(model_id)

        if not model_config:
            logger.error(f"Model {model_id} not found in config")
            return None

        # Find GGUF file
        model_path = model_config.get('path')
        gguf_file = self.find_gguf_file(model_path)

        if not gguf_file:
            logger.error(f"No GGUF file found for {model_id}")
            return None

        try:
            # Try to import llama-cpp-python
            try:
                from llama_cpp import Llama
            except ImportError:
                logger.error("llama-cpp-python not installed. Installing...")
                import subprocess
                subprocess.run([
                    "pip", "install", "llama-cpp-python",
                    "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu121"
                ], check=True)
                from llama_cpp import Llama

            # Load model with GPU acceleration
            logger.info(f"Loading {model_id} from {gguf_file}...")

            # Default parameters
            params = {
                'model_path': str(gguf_file),
                'n_gpu_layers': -1,  # Use all GPU layers
                'n_ctx': model_config.get('context_length', 8192),
                'n_batch': 512,
                'n_threads': os.cpu_count() // 2,
                'verbose': False,
            }

            # Override with custom parameters
            params.update(kwargs)

            # Load the model
            model = Llama(**params)

            self.models[model_id] = model
            logger.info(f"✓ Model {model_id} loaded successfully")

            return model

        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return None

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """
        Generate text using a loaded model

        Args:
            model_id: Model identifier
            prompt: Input prompt
            **kwargs: Generation parameters (max_tokens, temperature, etc.)

        Returns:
            Generated text
        """
        model = self.load_model(model_id)

        if not model:
            return f"Error: Failed to load model {model_id}"

        try:
            # Get model config for defaults
            model_config = self.config.get('local_models', {}).get(model_id, {})

            # Generation parameters
            params = {
                'max_tokens': model_config.get('max_tokens', 4096),
                'temperature': model_config.get('temperature', 0.7),
                'top_p': 0.95,
                'top_k': 40,
                'repeat_penalty': 1.1,
                'stop': ["</s>", "<|im_end|>", "<|endoftext|>"],
            }

            # Override with custom parameters
            params.update(kwargs)

            # Generate
            response = model(prompt, **params)

            # Extract text
            text = response['choices'][0]['text']

            return text

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"Error: {e}"

    def unload_model(self, model_id: str):
        """Unload a model to free memory"""
        if model_id in self.models:
            del self.models[model_id]
            logger.info(f"Model {model_id} unloaded")

    def list_available_models(self) -> List[str]:
        """List all available local models"""
        local_models = self.config.get('local_models', {})
        return list(local_models.keys())

    def get_model_info(self, model_id: str) -> Optional[dict]:
        """Get information about a model"""
        local_models = self.config.get('local_models', {})
        model_config = local_models.get(model_id)

        if not model_config:
            return None

        # Find GGUF file
        model_path = model_config.get('path')
        gguf_file = self.find_gguf_file(model_path)

        info = {
            'id': model_id,
            'path': model_path,
            'gguf_file': str(gguf_file) if gguf_file else None,
            'size_gb': round(gguf_file.stat().st_size / (1024**3), 2) if gguf_file else None,
            'use_case': model_config.get('use_case', []),
            'context_length': model_config.get('context_length', 'unknown'),
            'loaded': model_id in self.models
        }

        return info


# Global loader instance
_loader = None

def get_loader() -> GGUFModelLoader:
    """Get global GGUF loader instance"""
    global _loader
    if _loader is None:
        _loader = GGUFModelLoader()
    return _loader


# Example usage
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    loader = GGUFModelLoader()

    print("=" * 80)
    print("AlphaEdge AINV - GGUF Model Loader")
    print("=" * 80)
    print()

    # List available models
    models = loader.list_available_models()
    print(f"Found {len(models)} local models:\n")

    for model_id in models:
        info = loader.get_model_info(model_id)
        if info and info['gguf_file']:
            print(f"  ✓ {model_id:30} ({info['size_gb']:6.2f} GB) - {info['context_length']:>6} context")
        else:
            print(f"  ✗ {model_id:30} (not found)")

    print()
    print("=" * 80)

    # Test generation if model ID provided
    if len(sys.argv) > 1:
        model_id = sys.argv[1]
        prompt = sys.argv[2] if len(sys.argv) > 2 else "Hello! How are you?"

        print(f"\nTesting {model_id}...")
        print(f"Prompt: {prompt}")
        print()

        response = loader.generate(model_id, prompt, max_tokens=100)
        print(f"Response: {response}")
