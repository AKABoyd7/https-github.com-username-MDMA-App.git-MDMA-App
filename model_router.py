#!/usr/bin/env python3
"""
Model Router - Intelligent Model Selection
Routes queries to optimal LLM based on task type

Copyright © 2025 AlphaEdge AINV
"""
import os
import yaml
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import aiohttp
from nvidia_integration import NVIDIANemotron, NVCLIP


class ModelRouter:
    """
    Intelligent routing between multiple LLMs
    - Local models (LM Studio)
    - Cloud models (NVIDIA Nemotron)
    - Multimodal models (NV-CLIP)
    """

    def __init__(self, config_path: str = "models_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Initialize model clients
        self.local_endpoint = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")

        # Cache for model clients
        self._nemotron_client: Optional[NVIDIANemotron] = None
        self._nvclip_client: Optional[NVCLIP] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def get_nemotron(self) -> NVIDIANemotron:
        """Get or create Nemotron client"""
        if self._nemotron_client is None:
            self._nemotron_client = NVIDIANemotron(
                api_key=self.nvidia_api_key,
                model="nvidia/nemotron-3-43b-instruct"
            )
        return self._nemotron_client

    def get_nvclip(self) -> NVCLIP:
        """Get or create NV-CLIP client"""
        if self._nvclip_client is None:
            self._nvclip_client = NVCLIP(api_key=self.nvidia_api_key)
        return self._nvclip_client

    def select_model(self, task_type: str) -> Dict[str, Any]:
        """
        Select best model for task type

        Args:
            task_type: One of: code, business, reasoning, fast, vision

        Returns:
            Model config dict
        """
        routing = self.config.get('routing', {})
        defaults = self.config.get('defaults', {})

        # Get recommended models for task
        recommended = routing.get(task_type, [defaults.get('llm')])

        # Get first available model
        model_name = recommended[0] if recommended else defaults.get('llm')

        # Check if local or cloud
        if model_name in self.config.get('local_models', {}):
            return {
                'name': model_name,
                'type': 'local',
                'config': self.config['local_models'][model_name]
            }
        elif model_name in self.config.get('cloud_models', {}):
            return {
                'name': model_name,
                'type': 'cloud',
                'config': self.config['cloud_models'][model_name]
            }
        elif model_name in self.config.get('multimodal_models', {}):
            return {
                'name': model_name,
                'type': 'multimodal',
                'config': self.config['multimodal_models'][model_name]
            }
        else:
            raise ValueError(f"Model not found: {model_name}")

    async def chat_local(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Chat with local LM Studio model

        Args:
            model_name: Model identifier
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Response text
        """
        model_config = self.config['local_models'].get(model_name)
        if not model_config:
            raise ValueError(f"Local model not found: {model_name}")

        endpoint = model_config.get('endpoint', self.local_endpoint)

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{endpoint}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LM Studio error: {error_text}")

                data = await response.json()
                return data["choices"][0]["message"]["content"]

    async def chat_cloud(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Chat with cloud model (Nemotron)

        Args:
            model_name: Model identifier
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Response text
        """
        nemotron = self.get_nemotron()
        return await nemotron.chat(messages, temperature, max_tokens)

    async def route_query(
        self,
        query: str,
        task_type: Optional[str] = None,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Route query to best model

        Args:
            query: User query
            task_type: Optional task type hint (code, business, reasoning, fast)
            context: Optional context
            temperature: Sampling temperature
            max_tokens: Max tokens

        Returns:
            Dict with response and metadata
        """
        # Auto-detect task type if not provided
        if task_type is None:
            task_type = self._detect_task_type(query)

        # Select model
        model_info = self.select_model(task_type)

        # Build messages
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": query})

        # Route to appropriate handler
        if model_info['type'] == 'local':
            response = await self.chat_local(
                model_info['name'],
                messages,
                temperature,
                max_tokens
            )
        elif model_info['type'] == 'cloud':
            response = await self.chat_cloud(
                model_info['name'],
                messages,
                temperature,
                max_tokens
            )
        else:
            raise ValueError(f"Unsupported model type: {model_info['type']}")

        return {
            'response': response,
            'model': model_info['name'],
            'model_type': model_info['type'],
            'task_type': task_type
        }

    def _detect_task_type(self, query: str) -> str:
        """
        Auto-detect task type from query

        Args:
            query: User query

        Returns:
            Detected task type
        """
        query_lower = query.lower()

        # Code keywords
        code_keywords = ['code', 'function', 'class', 'python', 'javascript',
                        'debug', 'error', 'bug', 'implement', 'refactor']
        if any(kw in query_lower for kw in code_keywords):
            return 'code'

        # Business keywords
        business_keywords = ['business', 'analytics', 'report', 'analysis',
                            'strategy', 'market', 'revenue', 'profit']
        if any(kw in query_lower for kw in business_keywords):
            return 'business'

        # Reasoning keywords
        reasoning_keywords = ['explain', 'analyze', 'compare', 'why', 'how',
                             'reason', 'logic', 'deduce', 'infer']
        if any(kw in query_lower for kw in reasoning_keywords):
            return 'reasoning'

        # Default to general reasoning
        return 'reasoning'

    async def vision_query(
        self,
        image_path: str,
        query: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Vision query using NV-CLIP

        Args:
            image_path: Path to image
            query: Optional text query
            labels: Optional classification labels

        Returns:
            Vision results
        """
        nvclip = self.get_nvclip()

        results = {
            'image_path': image_path
        }

        # Classification if labels provided
        if labels:
            classification = await nvclip.zero_shot_classify(image_path, labels)
            results['classification'] = classification

        # Similarity if query provided
        if query:
            similarity = await nvclip.similarity(image_path, [query])
            results['similarity'] = similarity[query]

        # Always get embedding
        embedding = await nvclip.encode_image(image_path)
        results['embedding'] = embedding

        return results

    def list_models(self, model_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available models

        Args:
            model_type: Filter by type (local, cloud, multimodal)

        Returns:
            Dict of model lists by type
        """
        models = {
            'local': list(self.config.get('local_models', {}).keys()),
            'cloud': list(self.config.get('cloud_models', {}).keys()),
            'multimodal': list(self.config.get('multimodal_models', {}).keys())
        }

        if model_type:
            return {model_type: models.get(model_type, [])}

        return models


# Convenience functions
_router: Optional[ModelRouter] = None

def get_router() -> ModelRouter:
    """Get global router instance"""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


async def ask(
    query: str,
    task_type: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """
    Quick query with auto-routing

    Args:
        query: User query
        task_type: Optional task type
        context: Optional context

    Returns:
        Response text
    """
    router = get_router()
    result = await router.route_query(query, task_type, context)
    return result['response']


async def ask_code(query: str) -> str:
    """Quick code query"""
    return await ask(query, task_type='code')


async def ask_business(query: str) -> str:
    """Quick business query"""
    return await ask(query, task_type='business')


async def ask_reasoning(query: str) -> str:
    """Quick reasoning query"""
    return await ask(query, task_type='reasoning')


# CLI for testing
if __name__ == "__main__":
    import sys

    async def test_router():
        router = ModelRouter()

        # List models
        print("Available models:")
        models = router.list_models()
        for model_type, model_list in models.items():
            print(f"  {model_type}: {', '.join(model_list)}")

        # Test query
        if len(sys.argv) > 1:
            query = ' '.join(sys.argv[1:])
            print(f"\nQuery: {query}")

            result = await router.route_query(query)
            print(f"\nModel: {result['model']} ({result['model_type']})")
            print(f"Task: {result['task_type']}")
            print(f"\nResponse:\n{result['response']}")
        else:
            # Default test
            print("\nTesting code query...")
            result = await router.route_query(
                "Write a Python function to calculate fibonacci numbers"
            )
            print(f"Model: {result['model']}")
            print(f"Response: {result['response'][:200]}...")

    asyncio.run(test_router())
