#!/usr/bin/env python3
"""
Vision System Module
CLIP + OCR (Tesseract/PaddleOCR) + Vision Understanding

Copyright © 2025 AlphaEdge AINV
"""
import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import base64

import numpy as np
from PIL import Image


class LocalCLIP:
    """
    Local CLIP for vision-language understanding
    """

    def __init__(self, model_name: str = "openai/clip-vit-large-patch14"):
        """
        Initialize CLIP

        Args:
            model_name: HuggingFace model name
        """
        try:
            from transformers import CLIPProcessor, CLIPModel
            import torch

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)

            print(f"✓ CLIP loaded on {self.device}")

        except ImportError:
            raise ImportError(
                "transformers not installed. "
                "Install with: pip install transformers torch"
            )

    def encode_image(self, image_path: str) -> np.ndarray:
        """
        Encode image to embedding

        Args:
            image_path: Path to image

        Returns:
            Embedding vector
        """
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            embedding = image_features.cpu().numpy()[0]

        return embedding

    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text to embedding

        Args:
            text: Text to encode

        Returns:
            Embedding vector
        """
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)

        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            embedding = text_features.cpu().numpy()[0]

        return embedding

    def similarity(self, image_path: str, texts: List[str]) -> Dict[str, float]:
        """
        Calculate image-text similarities

        Args:
            image_path: Path to image
            texts: List of text labels

        Returns:
            Dict mapping text to similarity score
        """
        image_emb = self.encode_image(image_path)

        similarities = {}
        for text in texts:
            text_emb = self.encode_text(text)

            # Cosine similarity
            similarity = np.dot(image_emb, text_emb) / (
                np.linalg.norm(image_emb) * np.linalg.norm(text_emb)
            )
            similarities[text] = float(similarity)

        return similarities

    def classify(self, image_path: str, labels: List[str]) -> Dict[str, float]:
        """
        Zero-shot classification

        Args:
            image_path: Path to image
            labels: Classification labels

        Returns:
            Dict with label probabilities
        """
        similarities = self.similarity(image_path, labels)

        # Softmax
        scores = np.array(list(similarities.values()))
        exp_scores = np.exp(scores - np.max(scores))
        probs = exp_scores / exp_scores.sum()

        return {label: float(prob) for label, prob in zip(labels, probs)}


class OCREngine:
    """
    OCR Engine with multiple backends
    """

    def __init__(self, backend: str = "paddleocr"):
        """
        Initialize OCR

        Args:
            backend: paddleocr or tesseract
        """
        self.backend = backend

        if backend == "paddleocr":
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    show_log=False
                )
                print("✓ PaddleOCR initialized")
            except ImportError:
                raise ImportError("PaddleOCR not installed. pip install paddleocr")

        elif backend == "tesseract":
            try:
                import pytesseract
                self.ocr = pytesseract
                print("✓ Tesseract initialized")
            except ImportError:
                raise ImportError("pytesseract not installed. pip install pytesseract")

        else:
            raise ValueError(f"Unknown OCR backend: {backend}")

    def extract_text(self, image_path: str, language: str = "eng") -> Dict[str, Any]:
        """
        Extract text from image

        Args:
            image_path: Path to image
            language: Language code (eng, tha, chi, etc.)

        Returns:
            Dict with text and bounding boxes
        """
        if self.backend == "paddleocr":
            result = self.ocr.ocr(image_path, cls=True)

            texts = []
            boxes = []

            if result and result[0]:
                for line in result[0]:
                    box = line[0]
                    text = line[1][0]
                    confidence = line[1][1]

                    texts.append(text)
                    boxes.append({
                        'text': text,
                        'confidence': confidence,
                        'box': box
                    })

            full_text = "\n".join(texts)

            return {
                'text': full_text,
                'boxes': boxes,
                'language': language
            }

        elif self.backend == "tesseract":
            from PIL import Image
            import pytesseract

            image = Image.open(image_path)

            # Get text
            text = pytesseract.image_to_string(image, lang=language)

            # Get bounding boxes
            data = pytesseract.image_to_data(
                image,
                lang=language,
                output_type=pytesseract.Output.DICT
            )

            boxes = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    boxes.append({
                        'text': data['text'][i],
                        'confidence': data['conf'][i] / 100.0,
                        'box': [
                            data['left'][i],
                            data['top'][i],
                            data['left'][i] + data['width'][i],
                            data['top'][i] + data['height'][i]
                        ]
                    })

            return {
                'text': text.strip(),
                'boxes': boxes,
                'language': language
            }


class VisionSystem:
    """
    Complete vision system: CLIP + OCR + Understanding
    """

    def __init__(
        self,
        clip_model: Optional[str] = None,
        ocr_backend: str = "paddleocr",
        use_nvidia_clip: bool = False
    ):
        """
        Initialize vision system

        Args:
            clip_model: Local CLIP model name or None
            ocr_backend: paddleocr or tesseract
            use_nvidia_clip: Use NVIDIA NV-CLIP if True
        """
        self.use_nvidia_clip = use_nvidia_clip

        if use_nvidia_clip:
            from nvidia_integration import NVCLIP
            self.clip = NVCLIP()
            print("✓ Using NVIDIA NV-CLIP")
        else:
            self.clip = LocalCLIP(clip_model or "openai/clip-vit-large-patch14")

        self.ocr = OCREngine(backend=ocr_backend)

    async def analyze_image(
        self,
        image_path: str,
        query: Optional[str] = None,
        labels: Optional[List[str]] = None,
        extract_text: bool = True
    ) -> Dict[str, Any]:
        """
        Complete image analysis

        Args:
            image_path: Path to image
            query: Optional text query
            labels: Optional classification labels
            extract_text: Extract OCR text

        Returns:
            Complete analysis results
        """
        results = {
            'image_path': image_path
        }

        # Classification
        if labels:
            if self.use_nvidia_clip:
                classification = await self.clip.zero_shot_classify(image_path, labels)
            else:
                loop = asyncio.get_event_loop()
                classification = await loop.run_in_executor(
                    None,
                    self.clip.classify,
                    image_path,
                    labels
                )
            results['classification'] = classification

        # Similarity query
        if query:
            if self.use_nvidia_clip:
                similarity = await self.clip.similarity(image_path, [query])
                results['similarity'] = similarity[query]
            else:
                loop = asyncio.get_event_loop()
                similarity = await loop.run_in_executor(
                    None,
                    self.clip.similarity,
                    image_path,
                    [query]
                )
                results['similarity'] = similarity[query]

        # OCR
        if extract_text:
            loop = asyncio.get_event_loop()
            ocr_result = await loop.run_in_executor(
                None,
                self.ocr.extract_text,
                image_path
            )
            results['ocr'] = ocr_result

        return results

    async def search_images(
        self,
        query: str,
        image_dir: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search images by text query

        Args:
            query: Text query
            image_dir: Directory containing images
            top_k: Number of results

        Returns:
            List of matched images with scores
        """
        if self.use_nvidia_clip:
            return await self.clip.image_search(query, image_dir, top_k)

        # Local CLIP search
        image_paths = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']:
            image_paths.extend(Path(image_dir).glob(ext))

        loop = asyncio.get_event_loop()
        query_emb = await loop.run_in_executor(None, self.clip.encode_text, query)

        results = []
        for img_path in image_paths:
            try:
                img_emb = await loop.run_in_executor(
                    None,
                    self.clip.encode_image,
                    str(img_path)
                )

                similarity = np.dot(query_emb, img_emb) / (
                    np.linalg.norm(query_emb) * np.linalg.norm(img_emb)
                )

                results.append({
                    'path': str(img_path),
                    'score': float(similarity)
                })
            except:
                continue

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]


# ===== Convenience Functions =====

_vision_system: Optional[VisionSystem] = None


def get_vision_system() -> VisionSystem:
    """Get global vision system"""
    global _vision_system
    if _vision_system is None:
        use_nvidia = os.getenv("USE_NVIDIA_CLIP", "false").lower() == "true"
        _vision_system = VisionSystem(use_nvidia_clip=use_nvidia)
    return _vision_system


async def analyze_image(
    image_path: str,
    query: Optional[str] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Quick image analysis"""
    vision = get_vision_system()
    return await vision.analyze_image(image_path, query, labels)


async def extract_text_from_image(image_path: str) -> str:
    """Quick OCR"""
    vision = get_vision_system()
    result = await vision.analyze_image(image_path, extract_text=True)
    return result.get('ocr', {}).get('text', '')


# ===== CLI =====

if __name__ == "__main__":
    import sys

    async def test_vision():
        if len(sys.argv) < 2:
            print("Usage: python vision_system.py <image_path>")
            return

        image_path = sys.argv[1]

        print(f"Analyzing: {image_path}\n")

        # Test classification
        labels = ["person", "car", "building", "nature", "animal", "food", "technology"]

        result = await analyze_image(image_path, labels=labels)

        if 'classification' in result:
            print("Classification:")
            for label, score in sorted(result['classification'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {label}: {score:.2%}")

        if 'ocr' in result:
            print(f"\nExtracted Text:\n{result['ocr']['text']}")

    asyncio.run(test_vision())
