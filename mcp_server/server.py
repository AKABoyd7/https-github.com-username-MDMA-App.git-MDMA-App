"""
AlphaEdge AINV MCP Server
Enterprise-grade Model Context Protocol server for AI model integration.

Exposes local models (LM Studio), NVIDIA APIs, GPU monitoring, and system tools
through the MCP protocol for Claude Desktop integration.
"""

import logging
import asyncio
from typing import Dict, Any, List
import time
from datetime import datetime

# MCP and FastAPI imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    import sys
    print("ERROR: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    print("Falling back to basic server mode...", file=sys.stderr)
    Server = None
    stdio_server = None

# Local imports
from .config import settings, validate_configuration
from .utils import setup_logging, Timer
from .tools import local_models, nvidia_api, gpu_monitor, system, memory, windows_management

# Setup logging
setup_logging(level=logging.INFO if not settings.DEBUG_MODE else logging.DEBUG)
logger = logging.getLogger(__name__)


class AlphaEdgeMCPServer:
    """Main MCP server for AlphaEdge AINV."""

    def __init__(self):
        self.server_start_time = time.time()
        self.total_requests = 0
        self.error_count = 0
        self.active_connections = 0

        # Initialize MCP server
        if Server is not None:
            self.mcp = Server(settings.SERVER_NAME)
        else:
            self.mcp = None
            logger.error("MCP Server not available - SDK not installed")

        # Tool registry
        self.tools = {}

        # Register all tools
        self._register_tools()

        logger.info(f"AlphaEdge AINV MCP Server initialized with {len(self.tools)} tools")

    def _register_tools(self):
        """Register all tools from modules."""
        logger.info("Registering tools...")

        tool_modules = [
            ("Local Models", local_models),
            ("NVIDIA API", nvidia_api),
            ("GPU Monitor", gpu_monitor),
            ("System", system),
            ("Memory", memory),
            ("Windows Management", windows_management)
        ]

        for category, module in tool_modules:
            try:
                module_tools = module.get_tools()
                logger.info(f"  Registering {len(module_tools)} {category} tools")

                for tool_def in module_tools:
                    tool_name = tool_def["name"]
                    self.tools[tool_name] = tool_def

                    # Register with MCP if available
                    if self.mcp and hasattr(self.mcp, 'list_tools'):
                        # The actual MCP registration happens via decorators
                        # Store tool info for manual calls
                        pass

            except Exception as e:
                logger.error(f"Failed to register {category} tools: {e}")

        logger.info(f"Total tools registered: {len(self.tools)}")

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool execution request.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        self.total_requests += 1
        logger.info(f"Tool call: {tool_name} with args: {arguments}")

        try:
            if tool_name not in self.tools:
                self.error_count += 1
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": list(self.tools.keys())
                }

            tool_def = self.tools[tool_name]
            handler = tool_def["handler"]

            # Execute tool
            with Timer(f"Tool execution: {tool_name}"):
                result = handler(**arguments)

            # Ensure result is JSON serializable
            if not isinstance(result, dict):
                result = {"result": str(result)}

            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"Tool execution failed for {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information."""
        uptime = time.time() - self.server_start_time

        # Check LM Studio connection
        try:
            from .tools.local_models import get_lm_client
            lm_client = get_lm_client()
            lm_status = "connected" if lm_client.is_connected() else "disconnected"
        except:
            lm_status = "error"

        # Check NVIDIA API
        try:
            from .tools.nvidia_api import get_nvidia_client
            nvidia_client = get_nvidia_client()
            nvidia_status = "enabled" if nvidia_client.is_enabled() else "not_configured"
            if nvidia_status == "enabled":
                nvidia_status = "connected" if nvidia_client.is_connected() else "disconnected"
        except:
            nvidia_status = "error"

        return {
            "server_name": settings.SERVER_NAME,
            "version": settings.SERVER_VERSION,
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": self._format_uptime(uptime),
            "active_connections": self.active_connections,
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "tools_registered": len(self.tools),
            "lm_studio_status": lm_status,
            "nvidia_api_status": nvidia_status,
            "timestamp": datetime.now().isoformat()
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return {
            "lm_studio_url": settings.LM_STUDIO_URL,
            "nvidia_api_enabled": settings.is_nvidia_enabled(),
            "project_path": settings.PROJECT_ROOT,
            "workspace_path": settings.WORKSPACE_DIR,
            "enabled_features": [
                "local_models" if True else None,
                "nvidia_api" if settings.is_nvidia_enabled() else None,
                "gpu_monitoring",
                "system_tools",
                "memory_tools (placeholder)"
            ],
            "safety_enabled": True,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "command_timeout": settings.COMMAND_TIMEOUT
        }

    def reload_config(self) -> Dict[str, Any]:
        """Reload configuration from environment."""
        logger.info("Reloading configuration...")

        try:
            from .config import reload_settings
            new_settings = reload_settings()

            # Re-validate
            validation = validate_configuration()

            return {
                "success": True,
                "changes": ["Configuration reloaded from environment"],
                "errors": validation.get("errors", []),
                "warnings": validation.get("warnings", []),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Config reload failed: {e}")
            return {
                "success": False,
                "changes": [],
                "errors": [str(e)],
                "timestamp": datetime.now().isoformat()
            }


# Create global server instance
_server_instance: AlphaEdgeMCPServer = None


def get_server() -> AlphaEdgeMCPServer:
    """Get or create server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = AlphaEdgeMCPServer()
    return _server_instance


# MCP Protocol Implementation
if Server is not None:
    # Create MCP server
    mcp_app = Server(settings.SERVER_NAME)
    server = get_server()

    @mcp_app.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available tools."""
        tools = []
        for tool_name, tool_def in server.tools.items():
            tools.append(Tool(
                name=tool_name,
                description=tool_def["description"],
                inputSchema=tool_def["inputSchema"]
            ))
        return tools

    @mcp_app.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool."""
        result = await server.handle_tool_call(name, arguments)

        # Convert result to MCP TextContent
        import json
        result_text = json.dumps(result, indent=2)

        return [TextContent(
            type="text",
            text=result_text
        )]


async def main():
    """Main entry point for MCP server."""
    logger.info("=" * 70)
    logger.info(f"Starting AlphaEdge AINV MCP Server v{settings.SERVER_VERSION}")
    logger.info("=" * 70)

    # Validate configuration
    validation = validate_configuration()
    if not validation["valid"]:
        logger.error("Configuration validation failed!")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
        return

    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")

    # Initialize server
    server = get_server()

    logger.info(f"Project Root: {settings.PROJECT_ROOT}")
    logger.info(f"LM Studio URL: {settings.LM_STUDIO_URL}")
    logger.info(f"NVIDIA API: {'Enabled' if settings.is_nvidia_enabled() else 'Disabled'}")
    logger.info(f"Tools Registered: {len(server.tools)}")
    logger.info("=" * 70)

    # List all tools
    logger.info("Available Tools:")
    for i, (tool_name, tool_def) in enumerate(server.tools.items(), 1):
        logger.info(f"  {i:2d}. {tool_name:30s} - {tool_def['description'][:80]}")

    logger.info("=" * 70)
    logger.info("Server ready! Waiting for MCP connections...")

    if stdio_server is not None and mcp_app is not None:
        # Run MCP server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await mcp_app.run(
                read_stream,
                write_stream,
                mcp_app.create_initialization_options()
            )
    else:
        logger.error("MCP SDK not available. Install with: pip install mcp")
        logger.info("Server will wait indefinitely...")
        # Keep server running
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            logger.info("Server shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
