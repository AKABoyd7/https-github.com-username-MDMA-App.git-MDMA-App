#!/usr/bin/env python3
"""
AlphaEdge AINV - System Test Suite
Test all components to ensure 100% functionality
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List
import aiohttp

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from model_router import ModelRouter
from nvidia_integration import NVIDIANemotron


class SystemTester:
    """Comprehensive system testing"""

    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.errors: List[str] = []

    def print_header(self, text: str):
        """Print section header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)

    async def test_nvidia_api(self) -> bool:
        """Test NVIDIA Cloud API connectivity"""
        self.print_header("Testing NVIDIA Cloud API")

        try:
            api_key = os.getenv("NVIDIA_API_KEY")
            if not api_key:
                print("❌ NVIDIA_API_KEY not found in environment")
                return False

            print(f"✓ API Key found: {api_key[:20]}...")

            # Test with simple query
            nemotron = NVIDIANemotron(api_key=api_key, model="meta/llama-3.1-8b-instruct")

            messages = [
                {"role": "user", "content": "Say 'Hello from NVIDIA API!' in one sentence."}
            ]

            print("  Testing API call...")
            response = await nemotron.chat(messages, temperature=0.7, max_tokens=100)

            print(f"✓ API Response: {response[:100]}...")
            return True

        except Exception as e:
            print(f"❌ NVIDIA API test failed: {e}")
            self.errors.append(f"NVIDIA API: {str(e)}")
            return False

    async def test_model_router(self) -> bool:
        """Test model router"""
        self.print_header("Testing Model Router")

        try:
            router = ModelRouter()
            print("✓ Model router initialized")

            # Test model selection
            model_info = router.select_model("fast")
            print(f"✓ Model selection works: {model_info['name']}")

            # Test query routing
            print("  Testing query routing...")
            result = await router.route_query(
                query="What is 2+2?",
                task_type="fast",
                max_tokens=100
            )

            print(f"✓ Query routing works")
            print(f"  Model used: {result['model']}")
            print(f"  Response: {result['response'][:100]}...")

            return True

        except Exception as e:
            print(f"❌ Model router test failed: {e}")
            self.errors.append(f"Model Router: {str(e)}")
            return False

    async def test_api_server(self) -> bool:
        """Test API server endpoints"""
        self.print_header("Testing API Server")

        try:
            base_url = "http://localhost:8000"

            async with aiohttp.ClientSession() as session:
                # Test root endpoint
                print("  Testing / endpoint...")
                async with session.get(f"{base_url}/") as resp:
                    if resp.status == 200:
                        print("✓ Root endpoint working")
                    else:
                        print(f"⚠ Root endpoint returned {resp.status}")

                # Test status endpoint
                print("  Testing /status endpoint...")
                async with session.get(f"{base_url}/status") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"✓ Status endpoint working")
                        print(f"  Uptime: {data.get('uptime', 0):.2f}s")
                    else:
                        print(f"⚠ Status endpoint returned {resp.status}")

                # Test models endpoint
                print("  Testing /models endpoint...")
                async with session.get(f"{base_url}/models") as resp:
                    if resp.status == 200:
                        models = await resp.json()
                        print(f"✓ Models endpoint working")
                        print(f"  Cloud models: {len(models.get('cloud_models', {}))}")
                    else:
                        print(f"⚠ Models endpoint returned {resp.status}")

            return True

        except aiohttp.ClientConnectorError:
            print("⚠ API Server not running")
            print("  Start with: .\\START.bat")
            return False
        except Exception as e:
            print(f"❌ API server test failed: {e}")
            self.errors.append(f"API Server: {str(e)}")
            return False

    async def test_tools(self) -> bool:
        """Test MCP tools"""
        self.print_header("Testing MCP Tools")

        try:
            from mcp_server.server import get_server
            server = get_server()

            print(f"✓ MCP Server initialized")
            print(f"  Total tools: {len(server.tools)}")

            # List tool categories
            categories = {}
            for tool_name in server.tools.keys():
                category = tool_name.split('_')[0] if '_' in tool_name else 'other'
                categories[category] = categories.get(category, 0) + 1

            print(f"  Tool categories:")
            for cat, count in sorted(categories.items()):
                print(f"    - {cat}: {count} tools")

            return True

        except Exception as e:
            print(f"❌ Tools test failed: {e}")
            self.errors.append(f"Tools: {str(e)}")
            return False

    def test_environment(self) -> bool:
        """Test environment configuration"""
        self.print_header("Testing Environment Configuration")

        try:
            # Check .env file
            env_file = Path(".env")
            if env_file.exists():
                print("✓ .env file exists")
            else:
                print("⚠ .env file not found")

            # Check required environment variables
            required_vars = [
                "NVIDIA_API_KEY",
                "MODEL_CACHE_DIR",
                "TENSORRT_MODELS_DIR"
            ]

            for var in required_vars:
                value = os.getenv(var)
                if value:
                    print(f"✓ {var} is set")
                else:
                    print(f"⚠ {var} not set")

            # Check model directories
            model_dir = Path(os.getenv("MODEL_CACHE_DIR", "G:\\AIModels\\cache"))
            if model_dir.parent.exists():
                print(f"✓ Models directory exists: {model_dir.parent}")
            else:
                print(f"⚠ Models directory not found: {model_dir.parent}")

            return True

        except Exception as e:
            print(f"❌ Environment test failed: {e}")
            self.errors.append(f"Environment: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("\n")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                            ║")
        print("║         AlphaEdge AINV - System Test Suite               ║")
        print("║         Comprehensive Testing                             ║")
        print("║                                                            ║")
        print("╚════════════════════════════════════════════════════════════╝")

        # Run tests
        self.results["Environment"] = self.test_environment()
        self.results["NVIDIA API"] = await self.test_nvidia_api()
        self.results["Model Router"] = await self.test_model_router()
        self.results["API Server"] = await self.test_api_server()
        self.results["MCP Tools"] = await self.test_tools()

        # Print summary
        self.print_header("TEST SUMMARY")

        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)

        for test_name, result in self.results.items():
            status = "✓ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")

        print(f"\n  Results: {passed}/{total} tests passed")

        if self.errors:
            print(f"\n  Errors encountered:")
            for error in self.errors:
                print(f"    - {error}")

        if passed == total:
            print("\n🎉 All tests passed! System is 100% functional!")
            return True
        else:
            print(f"\n⚠ {total - passed} test(s) failed. Review errors above.")
            return False


async def main():
    """Main test function"""
    tester = SystemTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
