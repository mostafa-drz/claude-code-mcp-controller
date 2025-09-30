#!/usr/bin/env python3
"""
Start the FastMCP server in HTTP mode for ChatGPT integration.
"""

from server import mcp

if __name__ == "__main__":
    print("Starting FastMCP server for ChatGPT...")
    print("Server will be available at: http://localhost:8000/mcp")
    print("Use ngrok to expose: ngrok http 8000")
    print("\nPress Ctrl+C to stop the server")

    # Run with streamable-http transport for ChatGPT
    # ChatGPT expects the MCP server at the root path "/"
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/"  # ChatGPT expects root path, not /mcp
    )