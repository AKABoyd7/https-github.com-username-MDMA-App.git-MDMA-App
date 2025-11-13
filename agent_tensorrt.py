"""
Smart AI Agent with TensorRT-LLM and Hybrid Routing
"""
import os
import warnings
import asyncio
import logging
from typing import Optional

# Suppress compatibility warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from smart_router import SmartInferenceRouter
from model_converter import SmartModelConverter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartAgent:
    """
    AI Agent with intelligent backend selection

    Features:
    - TensorRT-LLM for speed (if available)
    - Ollama fallback
    - Auto model conversion
    - Performance monitoring
    """

    def __init__(self,
                 model_name: str = "llama-3-8b",
                 use_tensorrt: bool = True,
                 auto_convert: bool = True):
        """
        Initialize Smart Agent

        Args:
            model_name: Model to use
            use_tensorrt: Try to use TensorRT
            auto_convert: Auto-convert models if needed
        """
        self.model_name = model_name
        self.converter = SmartModelConverter() if auto_convert else None
        self.router = None

        # Initialize router
        self._initialize_router(use_tensorrt)

    def _initialize_router(self, use_tensorrt: bool):
        """Initialize inference router"""
        tensorrt_path = None

        if use_tensorrt and self.converter:
            try:
                # Try to get/convert model
                logger.info(f"Preparing model: {self.model_name}")
                engine_path = self.converter.convert_if_needed(self.model_name)
                tensorrt_path = str(engine_path)
                logger.info(f"✅ TensorRT model ready at: {tensorrt_path}")

            except Exception as e:
                logger.warning(f"TensorRT setup failed: {e}")
                logger.info("Will use Ollama instead")

        # Create router with available backends
        self.router = SmartInferenceRouter(
            tensorrt_model_path=tensorrt_path,
            use_ollama=True,
            enable_cloud_fallback=False
        )

    async def chat(self, message: str) -> str:
        """
        Send message and get response

        Args:
            message: User message

        Returns:
            AI response
        """
        result = await self.router.generate(
            prompt=message,
            max_tokens=512,
            temperature=0.7
        )

        if result['success']:
            logger.info(f"Response from: {result['backend']}")
            return result['response']
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Generation failed: {error_msg}")
            return f"Error: {error_msg}"

    def get_status(self):
        """Get current agent status"""
        status = self.router.get_status()

        print("\n" + "="*50)
        print("  Smart Agent Status")
        print("="*50)
        print(f"Current Backend: {status['current_backend']}")
        print(f"TensorRT Available: {status['tensorrt_available']}")
        print(f"Ollama Available: {status['ollama_available']}")

        if status['metrics']:
            print("\nPerformance Metrics:")
            for key, value in status['metrics'].items():
                print(f"  {key}: {value}")

        print("="*50 + "\n")


async def main():
    """Main execution loop"""
    print("="*50)
    print("  Smart AI Agent with TensorRT-LLM")
    print("="*50)
    print()
    print("Initializing... This may take a moment")
    print()

    # Initialize agent
    try:
        agent = SmartAgent(
            model_name="llama-3-8b",
            use_tensorrt=True,
            auto_convert=True
        )

        # Show status
        agent.get_status()

        print("Agent ready! Type 'exit' or 'quit' to end")
        print("Type 'status' to see current status")
        print("-" * 50)
        print()

        # Chat loop
        while True:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if user_input.lower() == "status":
                agent.get_status()
                continue

            # Get response
            try:
                response = await agent.chat(user_input)
                print(f"AI: {response}\n")

            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nFatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
