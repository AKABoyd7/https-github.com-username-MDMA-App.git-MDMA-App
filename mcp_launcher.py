#!/usr/bin/env python3
"""
MCP Server Launcher with proper stdio handling for Claude Desktop.

This launcher ensures that:
1. All logging goes to stderr (not stdout)
2. Only JSON-RPC messages go to stdout
3. Python runs in unbuffered mode
4. Working directory and paths are set correctly
"""
import sys
import os

# CRITICAL: Set unbuffered mode for immediate I/O
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=False, write_through=True)
sys.stderr.reconfigure(line_buffering=False, write_through=True)

# Set working directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

# Import and run server
if __name__ == "__main__":
    try:
        import asyncio
        from mcp_server.server import main

        # Run MCP server
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
