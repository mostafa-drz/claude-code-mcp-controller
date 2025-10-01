"""
Configuration for Claude-Code MCP Controller

Simple configuration management with environment variable overrides.
"""

import os
from typing import Optional


class Config:
    """Configuration settings with environment variable overrides."""
    
    # Supervisor settings
    SUPERVISOR_HOST: str = os.getenv("SUPERVISOR_HOST", "localhost")
    SUPERVISOR_PORT: int = int(os.getenv("SUPERVISOR_PORT", "8080"))
    SUPERVISOR_URL: str = os.getenv("SUPERVISOR_URL", f"http://{SUPERVISOR_HOST}:{SUPERVISOR_PORT}")
    SUPERVISOR_TIMEOUT: int = int(os.getenv("SUPERVISOR_TIMEOUT", "30"))
    
    # MCP Server settings
    MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))
    MCP_PATH: str = os.getenv("MCP_PATH", "/")
    
    # Ngrok settings
    NGROK_PORT: int = int(os.getenv("NGROK_PORT", "8000"))
    
    # Session settings
    DEFAULT_WORKING_DIR: str = os.getenv("DEFAULT_WORKING_DIR", os.getcwd())
    MAX_LOG_LINES: int = int(os.getenv("MAX_LOG_LINES", "1000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Authentication
    API_KEY: str = os.getenv("CLAUDE_REMOTE_API_KEY", "claude-remote-dev-key-2025")
    
    @property
    def supervisor_url(self) -> str:
        """Get the supervisor URL."""
        return f"http://{self.SUPERVISOR_HOST}:{self.SUPERVISOR_PORT}"
    
    @property
    def mcp_url(self) -> str:
        """Get the MCP server URL."""
        return f"http://{self.MCP_HOST}:{self.MCP_PORT}{self.MCP_PATH}"
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"""Configuration:
  Supervisor: {self.SUPERVISOR_URL}
  MCP Server: {self.mcp_url}
  Ngrok Port: {self.NGROK_PORT}
  Log Level: {self.LOG_LEVEL}
"""


# Global configuration instance
config = Config()
