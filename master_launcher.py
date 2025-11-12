#!/usr/bin/env python3
"""
AlphaEdge AINV - Master Launcher
Launch all components of the enterprise platform

Copyright © 2025 AlphaEdge AINV
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path
from typing import List, Optional
import signal


class ServiceManager:
    """
    Manage all platform services
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.python = sys.executable
        self.processes: List[subprocess.Popen] = []

        # Ensure we're in project directory
        os.chdir(self.project_root)

    def print_header(self):
        """Print header"""
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         AlphaEdge AINV - Jareth2 Platform                 ║
║         Enterprise AI System                              ║
║                                                            ║
║         Copyright © 2025 AlphaEdge AINV                   ║
║         All Rights Reserved                               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

    def check_dependencies(self) -> bool:
        """Check if dependencies are installed"""
        print("🔍 Checking dependencies...")

        required = [
            'fastapi',
            'uvicorn',
            'gradio',
            'chromadb',
            'transformers',
            'yaml'
        ]

        missing = []

        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if missing:
            print(f"\n❌ Missing dependencies: {', '.join(missing)}")
            print("\nInstall with:")
            print(f"  {self.python} -m pip install -r requirements_full.txt")
            return False

        print("✓ All dependencies installed\n")
        return True

    def check_config(self) -> bool:
        """Check if configuration exists"""
        print("🔍 Checking configuration...")

        config_file = self.project_root / "models_config.yaml"

        if not config_file.exists():
            print("❌ models_config.yaml not found")
            return False

        # Check .env
        env_file = self.project_root / ".env"
        if not env_file.exists():
            print("⚠ .env file not found (optional)")
            print("  Create .env with NVIDIA_API_KEY for cloud features")

        print("✓ Configuration ready\n")
        return True

    def start_service(
        self,
        name: str,
        script: str,
        args: Optional[List[str]] = None
    ) -> subprocess.Popen:
        """
        Start a service

        Args:
            name: Service name
            script: Python script to run
            args: Optional arguments

        Returns:
            Process handle
        """
        cmd = [self.python, script]
        if args:
            cmd.extend(args)

        print(f"🚀 Starting {name}...")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.project_root)
        )

        self.processes.append(process)
        print(f"   PID: {process.pid}")

        return process

    def stop_all(self):
        """Stop all services"""
        print("\n🛑 Stopping all services...")

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()

        print("✓ All services stopped")

    async def launch_api_server(self):
        """Launch REST API server"""
        self.start_service("API Server", "api_server.py")
        await asyncio.sleep(2)
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs\n")

    async def launch_web_ui(self):
        """Launch Web UI"""
        self.start_service("Web UI", "web_ui.py")
        await asyncio.sleep(2)
        print("   Web UI: http://localhost:7860\n")

    async def launch_daemon(self):
        """Launch background daemon"""
        self.start_service("Daemon", "jareth2_daemon.py", ["start"])
        await asyncio.sleep(1)
        print("   Daemon: Running in background\n")

    async def launch_full_platform(self):
        """Launch entire platform"""
        self.print_header()

        # Check dependencies
        if not self.check_dependencies():
            return False

        # Check config
        if not self.check_config():
            return False

        print("=" * 60)
        print("LAUNCHING FULL PLATFORM")
        print("=" * 60)
        print()

        # Launch services
        await self.launch_api_server()
        await self.launch_web_ui()

        print("=" * 60)
        print("✓ PLATFORM READY")
        print("=" * 60)
        print()
        print("Access points:")
        print("  • Web UI:   http://localhost:7860")
        print("  • REST API: http://localhost:8000")
        print("  • API Docs: http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop all services")
        print()

        return True

    async def monitor_services(self):
        """Monitor running services"""
        try:
            while True:
                await asyncio.sleep(5)

                # Check if any process died
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"\n⚠ Service {i} died (exit code: {process.returncode})")

        except KeyboardInterrupt:
            pass


async def main():
    """Main function"""
    manager = ServiceManager()

    # Setup signal handler
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutdown signal received")
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Launch platform
    success = await manager.launch_full_platform()

    if not success:
        return 1

    # Monitor services
    try:
        await manager.monitor_services()
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()

    return 0


def quick_start():
    """Quick start menu"""
    print("""
╔════════════════════════════════════════╗
║   AlphaEdge AINV - Quick Start Menu   ║
╚════════════════════════════════════════╝

Select mode:

1. Full Platform (API + Web UI + Daemon)
2. Web UI Only
3. API Server Only
4. CLI Tool (jareth_cli.py)
5. Autonomous Agent (jareth2_agent.py)
6. Daemon Service (jareth2_daemon.py)

0. Exit
""")

    choice = input("Select (0-6): ").strip()

    manager = ServiceManager()

    if choice == "1":
        # Full platform
        asyncio.run(main())

    elif choice == "2":
        # Web UI only
        manager.print_header()
        asyncio.run(manager.launch_web_ui())
        input("\nPress Enter to stop...")
        manager.stop_all()

    elif choice == "3":
        # API only
        manager.print_header()
        asyncio.run(manager.launch_api_server())
        input("\nPress Enter to stop...")
        manager.stop_all()

    elif choice == "4":
        # CLI tool
        subprocess.run([sys.executable, "jareth_cli.py", "--help"])

    elif choice == "5":
        # Agent
        subprocess.run([sys.executable, "jareth2_agent.py", "--help"])

    elif choice == "6":
        # Daemon
        subprocess.run([sys.executable, "jareth2_daemon.py", "status"])

    elif choice == "0":
        print("Goodbye!")
        return

    else:
        print("Invalid choice")
        quick_start()


if __name__ == "__main__":
    # Check command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            asyncio.run(main())
        elif sys.argv[1] == "--help":
            print("""
AlphaEdge AINV Master Launcher

Usage:
  python master_launcher.py              # Interactive menu
  python master_launcher.py --full       # Launch full platform
  python master_launcher.py --help       # This help

Components:
  • REST API Server (port 8000)
  • Web UI (port 7860)
  • Background Daemon
  • Multi-agent orchestration
  • Voice, Vision, RAG capabilities
""")
        else:
            print("Unknown option. Use --help for usage.")
    else:
        # Interactive menu
        quick_start()
