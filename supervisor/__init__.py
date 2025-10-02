"""
Claude-Code MCP Controller Supervisor

Local supervisor module for managing existing Claude-Code sessions via tmux.
Provides session discovery, communication, and management for MCP integration.
"""

from .session_manager import SessionManager
from .claude_wrapper import ClaudeWrapper

__version__ = "0.1.0"
__all__ = ["SessionManager", "ClaudeWrapper"]