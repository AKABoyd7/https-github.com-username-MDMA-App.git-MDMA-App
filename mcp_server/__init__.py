"""
AlphaEdge AINV MCP Server Package
Enterprise-grade Model Context Protocol server for AI integration.
"""

__version__ = "1.0.0"
__author__ = "AlphaEdge AINV Team"

from .server import get_server, AlphaEdgeMCPServer

__all__ = ['get_server', 'AlphaEdgeMCPServer', '__version__']
