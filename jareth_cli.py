#!/usr/bin/env python3
"""
Jareth AINV CLI - Standalone Local Mode
รันบนเครื่อง Local โดยไม่ต้องผ่าน Claude Desktop

Usage:
    python jareth_cli.py                          # List all tools
    python jareth_cli.py gpu_status               # Run specific tool
    python jareth_cli.py list_processes           # List processes
    python jareth_cli.py --interactive            # Interactive mode
"""
import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from mcp_server import get_server, AlphaEdgeMCPServer


class JarethCLI:
    """Command-line interface for Jareth AINV"""

    def __init__(self):
        self.server: AlphaEdgeMCPServer = get_server()
        print(f"✓ Jareth AINV initialized with {len(self.server.tools)} tools")

    def list_tools(self):
        """List all available tools"""
        print("\n" + "="*80)
        print("Available Tools:")
        print("="*80)

        # Group by category
        categories = {}
        for name, tool in self.server.tools.items():
            desc = tool['description']
            # Simple categorization based on name prefix
            if 'chat_' in name or 'model' in name:
                cat = "🤖 AI Models"
            elif 'gpu' in name or 'cuda' in name or 'vram' in name:
                cat = "💻 GPU Monitoring"
            elif 'nvidia' in name:
                cat = "🎨 NVIDIA API"
            elif any(x in name for x in ['process', 'service', 'registry', 'network']):
                cat = "🪟 Windows Management"
            elif any(x in name for x in ['file', 'directory']):
                cat = "📁 File Operations"
            elif 'memory' in name:
                cat = "🧠 Memory"
            else:
                cat = "⚙️ System Tools"

            if cat not in categories:
                categories[cat] = []
            categories[cat].append((name, desc))

        # Print by category
        for cat, tools in sorted(categories.items()):
            print(f"\n{cat}:")
            for i, (name, desc) in enumerate(tools, 1):
                desc_short = desc[:70] + "..." if len(desc) > 70 else desc
                print(f"  {name:30s} - {desc_short}")

        print("\n" + "="*80)
        print(f"Total: {len(self.server.tools)} tools")
        print("\nUsage: python jareth_cli.py <tool_name> [args]")
        print("       python jareth_cli.py --interactive")
        print("="*80 + "\n")

    async def run_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """Run a specific tool"""
        arguments = arguments or {}

        if tool_name not in self.server.tools:
            print(f"❌ Error: Tool '{tool_name}' not found")
            print(f"\nDid you mean one of these?")
            # Find similar names
            similar = [t for t in self.server.tools.keys() if tool_name.lower() in t.lower()]
            for s in similar[:5]:
                print(f"  - {s}")
            return None

        print(f"\n⚙️  Running: {tool_name}")
        if arguments:
            print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        print()

        try:
            result = await self.server.handle_tool_call(tool_name, arguments)

            # Pretty print result
            print("✓ Result:")
            print("-" * 80)
            if isinstance(result, dict):
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)
            print("-" * 80)
            print()

            return result

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def interactive_mode(self):
        """Interactive mode - ask for commands"""
        print("\n" + "="*80)
        print("Jareth AINV - Interactive Mode")
        print("="*80)
        print("\nCommands:")
        print("  list           - List all tools")
        print("  run <tool>     - Run a tool")
        print("  status         - Server status")
        print("  config         - Server config")
        print("  exit/quit      - Exit")
        print("="*80 + "\n")

        while True:
            try:
                cmd = input("jareth> ").strip()

                if not cmd:
                    continue

                if cmd in ['exit', 'quit', 'q']:
                    print("Goodbye! 👋")
                    break

                elif cmd == 'list':
                    self.list_tools()

                elif cmd == 'status':
                    status = self.server.get_server_status()
                    print(json.dumps(status, indent=2))

                elif cmd == 'config':
                    config = self.server.get_server_config()
                    print(json.dumps(config, indent=2))

                elif cmd.startswith('run '):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) < 2:
                        print("Usage: run <tool_name>")
                        continue

                    tool_name = parts[1]
                    await self.run_tool(tool_name)

                else:
                    # Assume it's a tool name
                    await self.run_tool(cmd)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main entry point"""
    cli = JarethCLI()

    # Parse arguments
    args = sys.argv[1:]

    if not args:
        # No arguments - show help
        cli.list_tools()
        return

    if args[0] in ['-h', '--help', 'help']:
        cli.list_tools()
        return

    if args[0] in ['-i', '--interactive', 'interactive']:
        await cli.interactive_mode()
        return

    # Run specific tool
    tool_name = args[0]

    # Parse arguments (simple JSON or key=value)
    tool_args = {}
    if len(args) > 1:
        arg_str = ' '.join(args[1:])
        try:
            # Try JSON
            tool_args = json.loads(arg_str)
        except:
            # Try key=value pairs
            for pair in args[1:]:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # Try to parse value
                    try:
                        tool_args[key] = json.loads(value)
                    except:
                        tool_args[key] = value

    await cli.run_tool(tool_name, tool_args)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
