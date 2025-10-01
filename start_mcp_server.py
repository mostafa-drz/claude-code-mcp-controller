#!/usr/bin/env python3
"""
Start the FastMCP server in HTTP mode for ChatGPT integration.
"""

from server import mcp
from config import config

if __name__ == "__main__":
    print("Starting FastMCP server for ChatGPT...")
    print(f"Server will be available at: {config.mcp_url}")
    print(f"Use ngrok to expose: ngrok http {config.MCP_PORT}")
    print("\nPress Ctrl+C to stop the server")

    # Run with streamable-http transport for ChatGPT
    # ChatGPT expects the MCP server at the root path "/"
    mcp.run(
        transport="streamable-http",
        host=config.MCP_HOST,
        port=config.MCP_PORT,
        path=config.MCP_PATH
    )