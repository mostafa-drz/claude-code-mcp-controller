"""
Mock FastMCP implementation for local testing.

This provides a minimal FastMCP-like interface for testing purposes
when the actual FastMCP package is not available.
"""

import asyncio
import json
import logging
from typing import Dict, List, Callable, Any
from aiohttp import web
import aiohttp_cors

logger = logging.getLogger(__name__)


class MockFastMCP:
    """Mock FastMCP server for local testing."""

    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.app = web.Application()
        self.setup_routes()

    def tool(self, func: Callable) -> Callable:
        """Decorator to register a tool."""
        tool_name = func.__name__
        self.tools[tool_name] = {
            "function": func,
            "name": tool_name,
            "description": func.__doc__ or f"Tool: {tool_name}",
        }
        logger.info(f"Registered tool: {tool_name}")
        return func

    def resource(self, uri: str):
        """Decorator to register a resource."""
        def decorator(func: Callable) -> Callable:
            resource_name = uri
            self.resources[resource_name] = {
                "function": func,
                "uri": uri,
                "description": func.__doc__ or f"Resource: {resource_name}",
            }
            logger.info(f"Registered resource: {resource_name}")
            return func
        return decorator

    def setup_routes(self):
        """Setup HTTP routes for MCP server."""
        # CORS setup
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        # MCP endpoints
        self.app.router.add_get('/mcp/tools', self.list_tools)
        self.app.router.add_post('/mcp/tools/{tool_name}', self.call_tool)
        self.app.router.add_get('/mcp/resources', self.list_resources)
        self.app.router.add_get('/mcp/resources/{resource_name}', self.get_resource)
        self.app.router.add_get('/health', self.health_check)

        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def health_check(self, request):
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "server_name": self.name,
            "tools": len(self.tools),
            "resources": len(self.resources)
        })

    async def list_tools(self, request):
        """List available tools."""
        tools_list = []
        for tool_name, tool_info in self.tools.items():
            tools_list.append({
                "name": tool_name,
                "description": tool_info["description"]
            })

        return web.json_response({"tools": tools_list})

    async def call_tool(self, request):
        """Call a specific tool."""
        tool_name = request.match_info['tool_name']

        if tool_name not in self.tools:
            return web.json_response({"error": f"Tool {tool_name} not found"}, status=404)

        try:
            # Get request data
            if request.content_type == 'application/json':
                data = await request.json()
                args = data.get('args', {})
            else:
                args = {}

            tool_func = self.tools[tool_name]["function"]

            # Call the tool function
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)

            return web.json_response({"result": result})

        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def list_resources(self, request):
        """List available resources."""
        resources_list = []
        for resource_name, resource_info in self.resources.items():
            resources_list.append({
                "uri": resource_info["uri"],
                "description": resource_info["description"]
            })

        return web.json_response({"resources": resources_list})

    async def get_resource(self, request):
        """Get a specific resource."""
        resource_name = request.match_info['resource_name']

        # Find resource by URI pattern
        matching_resource = None
        for uri, resource_info in self.resources.items():
            if resource_name in uri or uri.replace("://", "_").replace("/", "_") == resource_name:
                matching_resource = resource_info
                break

        if not matching_resource:
            return web.json_response({"error": f"Resource {resource_name} not found"}, status=404)

        try:
            resource_func = matching_resource["function"]

            # Call the resource function
            if asyncio.iscoroutinefunction(resource_func):
                result = await resource_func()
            else:
                result = resource_func()

            return web.json_response({"result": result})

        except Exception as e:
            logger.error(f"Error getting resource {resource_name}: {e}")
            return web.json_response({"error": str(e)}, status=500)

    def run(self, host: str = "localhost", port: int = 8000):
        """Run the mock MCP server."""
        logger.info(f"Starting {self.name} on http://{host}:{port}")

        async def start_server():
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()

            logger.info(f"Mock MCP server running with {len(self.tools)} tools and {len(self.resources)} resources")

            # Keep running
            try:
                while True:
                    await asyncio.sleep(3600)  # Sleep for 1 hour
            except KeyboardInterrupt:
                logger.info("Shutting down mock MCP server")
            finally:
                await runner.cleanup()

        asyncio.run(start_server())


# Replace the import in server.py
FastMCP = MockFastMCP