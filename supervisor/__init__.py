"""
Claude-Code MCP Controller Supervisor

Local supervisor module for managing Claude-Code processes via PTY.
Provides session management, logging, and communication with the MCP server.
"""

from .session_manager import SessionManager
from .claude_wrapper import ClaudeWrapper

__version__ = "0.1.0"
__all__ = ["SessionManager", "ClaudeWrapper"]