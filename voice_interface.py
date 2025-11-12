#!/usr/bin/env python3
"""
Voice Interface Module
Speech-to-Text (Whisper) + Text-to-Speech (Piper/Coqui)

Copyright © 2025 AlphaEdge AINV
"""
import os
import asyncio
from typing import Optional, Union, Dict, Any
from pathlib import Path
import subprocess
import wave


class WhisperSTT:
    """
    Whisper Speech-to-Text
    Supports: local Whisper models via faster-whisper
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cuda",
        compute_type: str = "float16"
    ):
        """
        Initialize Whisper STT

        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
            device: cuda or cpu
            compute_type: float16, int8, float32
        """
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type
            )
            print(f"✓ Whisper {model_size} loaded on {device}")
        except ImportError:
            print("⚠ faster-whisper not installed. Using whisper fallback.")
            try:
                import whisper
                self.model = whisper.load_model(model_size)
                self.use_original = True
            except ImportError:
                raise ImportError(
                    "Neither faster-whisper nor whisper installed. "
                    "Install with: pip install faster-whisper"
                )
            self.use_original = False

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (en, th, etc.) or None for auto-detect
            task: transcribe or translate

        Returns:
            Dict with text and metadata
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.use_original:
            # Use original whisper
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task
            )
            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', [])
            }
        else:
            # Use faster-whisper
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                task=task
            )

            text = " ".join([segment.text for segment in segments])

            return {
                'text': text.strip(),
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration
            }

    async def transcribe_async(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """Async version of transcribe"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.transcribe,
            audio_path,
            language,
            task
        )


class PiperTTS:
    """
    Piper Text-to-Speech
    Fast, local TTS engine
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        voice: str = "en_US-lessac-medium"
    ):
        """
        Initialize Piper TTS

        Args:
            model_path: Path to Piper model (.onnx)
            voice: Voice name
        """
        self.model_path = model_path
        self.voice = voice

        # Check if piper binary exists
        self.piper_bin = self._find_piper()

        if not self.piper_bin:
            print("⚠ Piper binary not found. TTS unavailable.")
            print("Install: https://github.com/rhasspy/piper")

    def _find_piper(self) -> Optional[str]:
        """Find piper binary"""
        # Check common locations
        locations = [
            "piper",
            "./piper",
            "./piper/piper.exe",
            "G:/piper/piper.exe",
            "/usr/local/bin/piper"
        ]

        for loc in locations:
            try:
                result = subprocess.run(
                    [loc, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return loc
            except:
                continue

        return None

    def synthesize(
        self,
        text: str,
        output_path: str,
        speed: float = 1.0
    ) -> bool:
        """
        Synthesize speech from text

        Args:
            text: Text to speak
            output_path: Output audio file path
            speed: Speech speed multiplier

        Returns:
            Success boolean
        """
        if not self.piper_bin:
            raise RuntimeError("Piper not available")

        try:
            # Build command
            cmd = [self.piper_bin]

            if self.model_path:
                cmd.extend(["--model", self.model_path])
            else:
                cmd.extend(["--model", self.voice])

            cmd.extend(["--output_file", output_path])

            if speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / speed)])

            # Run piper
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"Piper error: {result.stderr}")
                return False

            return Path(output_path).exists()

        except Exception as e:
            print(f"TTS error: {e}")
            return False

    async def synthesize_async(
        self,
        text: str,
        output_path: str,
        speed: float = 1.0
    ) -> bool:
        """Async version of synthesize"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.synthesize,
            text,
            output_path,
            speed
        )


class VoiceInterface:
    """
    Combined Voice Interface
    STT + TTS
    """

    def __init__(
        self,
        whisper_model: str = "base",
        tts_voice: str = "en_US-lessac-medium",
        device: str = "cuda"
    ):
        """
        Initialize voice interface

        Args:
            whisper_model: Whisper model size
            tts_voice: TTS voice name
            device: cuda or cpu
        """
        self.stt = WhisperSTT(
            model_size=whisper_model,
            device=device
        )

        self.tts = PiperTTS(voice=tts_voice)

    async def listen(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> str:
        """
        Listen to audio and transcribe

        Args:
            audio_path: Path to audio file
            language: Language code or None

        Returns:
            Transcribed text
        """
        result = await self.stt.transcribe_async(audio_path, language)
        return result['text']

    async def speak(
        self,
        text: str,
        output_path: str = "output.wav",
        speed: float = 1.0
    ) -> str:
        """
        Speak text

        Args:
            text: Text to speak
            output_path: Output audio path
            speed: Speech speed

        Returns:
            Output file path
        """
        success = await self.tts.synthesize_async(text, output_path, speed)

        if success:
            return output_path
        else:
            raise RuntimeError("TTS failed")

    async def conversation_turn(
        self,
        audio_input: str,
        response_callback,
        output_path: str = "response.wav",
        language: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Full conversation turn: listen -> process -> speak

        Args:
            audio_input: Input audio file path
            response_callback: Async function to generate response from text
            output_path: Output audio path
            language: Input language

        Returns:
            Dict with input_text, response_text, audio_path
        """
        # Listen
        input_text = await self.listen(audio_input, language)

        # Process
        response_text = await response_callback(input_text)

        # Speak
        audio_path = await self.speak(response_text, output_path)

        return {
            'input_text': input_text,
            'response_text': response_text,
            'audio_path': audio_path
        }


# ===== Convenience Functions =====

_voice_interface: Optional[VoiceInterface] = None


def get_voice_interface() -> VoiceInterface:
    """Get global voice interface"""
    global _voice_interface
    if _voice_interface is None:
        _voice_interface = VoiceInterface()
    return _voice_interface


async def transcribe_audio(audio_path: str, language: Optional[str] = None) -> str:
    """Quick transcription"""
    interface = get_voice_interface()
    return await interface.listen(audio_path, language)


async def text_to_speech(text: str, output_path: str = "output.wav") -> str:
    """Quick TTS"""
    interface = get_voice_interface()
    return await interface.speak(text, output_path)


# ===== CLI =====

if __name__ == "__main__":
    import sys

    async def test_stt():
        """Test STT"""
        if len(sys.argv) < 2:
            print("Usage: python voice_interface.py <audio_file>")
            return

        audio_path = sys.argv[1]

        print(f"Transcribing: {audio_path}")
        text = await transcribe_audio(audio_path)
        print(f"\nTranscription:\n{text}")

    async def test_tts():
        """Test TTS"""
        text = "Hello, this is a test of the text to speech system."
        output = "test_output.wav"

        print(f"Synthesizing: {text}")
        result = await text_to_speech(text, output)
        print(f"Saved to: {result}")

    # Run tests
    print("=== Testing Voice Interface ===\n")

    if len(sys.argv) > 1:
        # Test STT with provided file
        asyncio.run(test_stt())
    else:
        # Test TTS
        asyncio.run(test_tts())
