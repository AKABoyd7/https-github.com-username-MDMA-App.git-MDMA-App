#!/usr/bin/env python3
"""
NVIDIA Integration Module
Supports: Nemotron LLM + NV-CLIP Multimodal

Copyright © 2025 AlphaEdge AINV
"""
import os
import asyncio
from typing import Dict, Any, List, Optional, Union, AsyncIterator
import aiohttp
import base64
from pathlib import Path


class NVIDIANemotron:
    """
    NVIDIA Nemotron LLM Integration
    Supports: Nemotron-3 43B/22B for advanced reasoning
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "meta/llama-3.1-8b-instruct"):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment")

        self.model = model
        self.endpoint = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """
        Chat with Nemotron LLM

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Stream response if True

        Returns:
            Response string or async iterator if streaming
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                headers=self.headers,
                json=payload
            ) as response:
                response.raise_for_status()

                if stream:
                    return self._stream_response(response)
                else:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]

    async def _stream_response(self, response):
        """Stream response chunks"""
        async for line in response.content:
            if line:
                line_text = line.decode('utf-8').strip()
                if line_text.startswith('data: '):
                    chunk = line_text[6:]
                    if chunk != '[DONE]':
                        import json
                        data = json.loads(chunk)
                        if 'choices' in data:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']

    async def reasoning(self, query: str, context: Optional[str] = None) -> str:
        """
        Advanced reasoning task

        Args:
            query: Question or problem to solve
            context: Optional context information

        Returns:
            Reasoning response
        """
        system_prompt = """You are Nemotron, NVIDIA's advanced reasoning AI.
You excel at:
- Complex problem solving
- Business analytics
- Multi-step reasoning
- Context understanding
- Technical analysis

Provide clear, structured reasoning with step-by-step explanations."""

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})

        messages.append({"role": "user", "content": query})

        return await self.chat(messages, temperature=0.7)

    async def rag_query(
        self,
        query: str,
        retrieved_docs: List[str],
        max_docs: int = 5
    ) -> str:
        """
        RAG (Retrieval Augmented Generation) query

        Args:
            query: User query
            retrieved_docs: List of retrieved document chunks
            max_docs: Maximum documents to include

        Returns:
            RAG response
        """
        context = "\n\n".join([
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(retrieved_docs[:max_docs])
        ])

        messages = [
            {
                "role": "system",
                "content": "You are an expert at answering questions based on provided documents. Use only the information from the documents to answer."
            },
            {
                "role": "user",
                "content": f"Documents:\n{context}\n\nQuestion: {query}"
            }
        ]

        return await self.chat(messages, temperature=0.3)


class NVCLIP:
    """
    NVIDIA NV-CLIP Multimodal Integration
    Image-text embedding and zero-shot classification
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment")

        self.endpoint = "https://ai.api.nvidia.com/v1/cv/nvidia/nv-clip"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def encode_image(self, image_path: str) -> List[float]:
        """
        Encode image to embedding vector

        Args:
            image_path: Path to image file

        Returns:
            Embedding vector (list of floats)
        """
        # Read and encode image to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            "input": {
                "image": image_data
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/embed",
                headers=self.headers,
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["data"][0]["embedding"]

    async def encode_text(self, text: str) -> List[float]:
        """
        Encode text to embedding vector

        Args:
            text: Text to encode

        Returns:
            Embedding vector (list of floats)
        """
        payload = {
            "input": {
                "text": text
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/embed",
                headers=self.headers,
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["data"][0]["embedding"]

    async def similarity(
        self,
        image_path: str,
        texts: List[str]
    ) -> Dict[str, float]:
        """
        Calculate similarity between image and texts

        Args:
            image_path: Path to image
            texts: List of text labels/descriptions

        Returns:
            Dict mapping text to similarity score
        """
        import numpy as np

        # Get embeddings
        image_emb = await self.encode_image(image_path)
        text_embs = [await self.encode_text(text) for text in texts]

        # Calculate cosine similarities
        image_vec = np.array(image_emb)
        similarities = {}

        for text, text_emb in zip(texts, text_embs):
            text_vec = np.array(text_emb)
            similarity = np.dot(image_vec, text_vec) / (
                np.linalg.norm(image_vec) * np.linalg.norm(text_vec)
            )
            similarities[text] = float(similarity)

        return similarities

    async def zero_shot_classify(
        self,
        image_path: str,
        labels: List[str]
    ) -> Dict[str, float]:
        """
        Zero-shot image classification

        Args:
            image_path: Path to image
            labels: List of possible class labels

        Returns:
            Dict mapping label to confidence score
        """
        similarities = await self.similarity(image_path, labels)

        # Softmax to get probabilities
        import numpy as np
        scores = np.array(list(similarities.values()))
        exp_scores = np.exp(scores - np.max(scores))
        probs = exp_scores / exp_scores.sum()

        return {
            label: float(prob)
            for label, prob in zip(labels, probs)
        }

    async def image_search(
        self,
        query: str,
        image_paths: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search images by text query

        Args:
            query: Text search query
            image_paths: List of image paths to search
            top_k: Number of top results to return

        Returns:
            List of dicts with 'path' and 'score'
        """
        import numpy as np

        # Get query embedding
        query_emb = await self.encode_text(query)
        query_vec = np.array(query_emb)

        # Get image embeddings and calculate similarities
        results = []
        for image_path in image_paths:
            try:
                image_emb = await self.encode_image(image_path)
                image_vec = np.array(image_emb)

                similarity = np.dot(query_vec, image_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(image_vec)
                )

                results.append({
                    'path': image_path,
                    'score': float(similarity)
                })
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    async def ocr_enhancement(
        self,
        image_path: str,
        ocr_text: str
    ) -> Dict[str, Any]:
        """
        Enhance OCR results with vision understanding

        Args:
            image_path: Path to image
            ocr_text: Raw OCR text

        Returns:
            Enhanced understanding with context
        """
        # Encode image
        image_emb = await self.encode_image(image_path)

        # Check text relevance
        relevance = await self.similarity(image_path, [ocr_text])

        return {
            'ocr_text': ocr_text,
            'image_embedding': image_emb,
            'relevance_score': relevance[ocr_text],
            'image_path': image_path
        }


# Convenience functions
async def ask_nemotron(query: str, context: Optional[str] = None) -> str:
    """Quick Nemotron reasoning query"""
    nemotron = NVIDIANemotron()
    return await nemotron.reasoning(query, context)


async def search_images_by_text(query: str, image_dir: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Quick image search by text"""
    clip = NVCLIP()

    # Get all images in directory
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']:
        image_paths.extend(Path(image_dir).glob(ext))

    image_paths = [str(p) for p in image_paths]

    return await clip.image_search(query, image_paths, top_k)


async def classify_image(image_path: str, labels: List[str]) -> Dict[str, float]:
    """Quick zero-shot image classification"""
    clip = NVCLIP()
    return await clip.zero_shot_classify(image_path, labels)


# CLI for testing
if __name__ == "__main__":
    import sys

    async def test_nemotron():
        print("Testing Nemotron...")
        result = await ask_nemotron(
            "Explain the difference between AI, ML, and Deep Learning in business context"
        )
        print(f"Nemotron: {result}")

    async def test_nvclip():
        print("Testing NV-CLIP...")
        if len(sys.argv) > 1:
            image_path = sys.argv[1]
            labels = ["person", "car", "building", "nature", "technology"]
            result = await classify_image(image_path, labels)
            print(f"Classification: {result}")
        else:
            print("Usage: python nvidia_integration.py <image_path>")

    asyncio.run(test_nemotron())
    # asyncio.run(test_nvclip())
