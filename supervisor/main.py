"""
Supervisor Main Module

Entry point for the local supervisor that manages Claude-Code sessions.
Provides a simple HTTP API for the MCP server to communicate with.
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Dict
import json
from aiohttp import web, WSMsgType
import aiohttp_cors
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import config
from .session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupervisorServer:
    """HTTP/WebSocket server for supervisor communication."""

    def __init__(self, host: str = None, port: int = None):
        self.host = host or config.SUPERVISOR_HOST
        self.port = port or config.SUPERVISOR_PORT
        self.session_manager = SessionManager()
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        """Setup HTTP routes and WebSocket handlers."""
        # Health check
        self.app.router.add_get('/health', self.health_check)

        # Session management
        self.app.router.add_post('/sessions', self.create_session)
        self.app.router.add_get('/sessions', self.list_sessions)
        self.app.router.add_get('/sessions/{session_id}/status', self.get_session_status)
        self.app.router.add_post('/sessions/{session_id}/message', self.send_message)
        self.app.router.add_get('/sessions/{session_id}/logs', self.get_logs)
        self.app.router.add_delete('/sessions/{session_id}', self.terminate_session)

        # Prompt handling
        self.app.router.add_get('/prompts', self.check_prompts)
        self.app.router.add_post('/sessions/{session_id}/respond', self.respond_to_prompt)

        # WebSocket for real-time communication
        self.app.router.add_get('/ws', self.websocket_handler)

        # CORS setup
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def health_check(self, request):
        """Health check endpoint."""
        health = await self.session_manager.check_session_health()
        return web.json_response({
            "status": "healthy",
            "supervisor_version": "0.1.0",
            "session_health": health
        })

    async def create_session(self, request):
        """Create a new Claude-Code session."""
        try:
            data = await request.json() if request.content_type == 'application/json' else {}
            name = data.get('name')
            working_dir = data.get('working_dir')

            session_id = await self.session_manager.create_session(name, working_dir)

            return web.json_response({
                "session_id": session_id,
                "status": "created"
            }, status=201)

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return web.json_response({"error": str(e)}, status=400)

    async def list_sessions(self, request):
        """List all active sessions."""
        try:
            sessions = await self.session_manager.list_sessions()
            return web.json_response({"sessions": sessions})

        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_session_status(self, request):
        """Get status of a specific session."""
        try:
            session_id = request.match_info['session_id']
            status = await self.session_manager.get_session_status(session_id)

            if not status:
                return web.json_response({"error": "Session not found"}, status=404)

            return web.json_response(status)

        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def send_message(self, request):
        """Send a message to a session."""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            message = data.get('message', '')

            if not message:
                return web.json_response({"error": "Message is required"}, status=400)

            result = await self.session_manager.send_message(session_id, message)
            return web.json_response(result)

        except ValueError as e:
            return web.json_response({"error": str(e)}, status=404)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_logs(self, request):
        """Get logs from a session with mobile optimization."""
        try:
            session_id = request.match_info['session_id']
            lines = int(request.query.get('lines', 50))
            mobile = request.query.get('mobile', 'false').lower() == 'true'

            logs = await self.session_manager.get_logs(session_id, lines, mobile_friendly=mobile)
            return web.json_response({"logs": logs, "session_id": session_id, "mobile_optimized": mobile})

        except ValueError as e:
            return web.json_response({"error": str(e)}, status=404)
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def terminate_session(self, request):
        """Terminate a session."""
        try:
            session_id = request.match_info['session_id']
            success = await self.session_manager.terminate_session(session_id)

            if success:
                return web.json_response({"status": "terminated", "session_id": session_id})
            else:
                return web.json_response({"error": "Failed to terminate session"}, status=500)

        except Exception as e:
            logger.error(f"Error terminating session: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def check_prompts(self, request):
        """Check for interactive prompts across all sessions."""
        try:
            prompts = await self.session_manager.check_for_prompts()
            return web.json_response({"prompts": prompts})

        except Exception as e:
            logger.error(f"Error checking prompts: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def respond_to_prompt(self, request):
        """Respond to an interactive prompt."""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            response = data.get('response', '')

            if not response:
                return web.json_response({"error": "Response is required"}, status=400)

            success = await self.session_manager.respond_to_prompt(session_id, response)

            if success:
                return web.json_response({"status": "response_sent", "session_id": session_id})
            else:
                return web.json_response({"error": "Failed to send response"}, status=500)

        except ValueError as e:
            return web.json_response({"error": str(e)}, status=404)
        except Exception as e:
            logger.error(f"Error responding to prompt: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def websocket_handler(self, request):
        """WebSocket handler for real-time communication."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        logger.info("WebSocket connection established")

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    command = data.get('command')

                    if command == 'list_sessions':
                        sessions = await self.session_manager.list_sessions()
                        await ws.send_text(json.dumps({
                            "type": "sessions",
                            "data": sessions
                        }))

                    elif command == 'check_prompts':
                        prompts = await self.session_manager.check_for_prompts()
                        await ws.send_text(json.dumps({
                            "type": "prompts",
                            "data": prompts
                        }))

                except Exception as e:
                    await ws.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))

            elif msg.type == WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")

        logger.info("WebSocket connection closed")
        return ws

    async def start(self):
        """Start the supervisor server."""
        logger.info(f"Starting supervisor server on {self.host}:{self.port}")

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"Supervisor server running on http://{self.host}:{self.port}")

    async def shutdown(self):
        """Shutdown the supervisor gracefully."""
        logger.info("Shutting down supervisor...")
        await self.session_manager.shutdown_all()
        logger.info("Supervisor shutdown complete")


async def main():
    """Main entry point for the supervisor."""
    supervisor = SupervisorServer()

    # Setup signal handlers for graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(supervisor.shutdown())

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    try:
        await supervisor.start()

        # Keep the server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Supervisor error: {e}")
    finally:
        await supervisor.shutdown()


if __name__ == "__main__":
    asyncio.run(main())