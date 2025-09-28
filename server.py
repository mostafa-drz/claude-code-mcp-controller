"""
Claude-Code MCP Controller Server

FastMCP-based server that provides MCP tools for controlling Claude-Code sessions
remotely via ChatGPT. Communicates with the local supervisor to manage sessions.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Claude-Code Controller =€")

# Configuration
SUPERVISOR_URL = os.getenv("SUPERVISOR_URL", "http://localhost:8080")
SUPERVISOR_TIMEOUT = 30

# HTTP session for supervisor communication
http_session: Optional[aiohttp.ClientSession] = None


async def get_http_session() -> aiohttp.ClientSession:
    """Get or create HTTP session for supervisor communication."""
    global http_session
    if http_session is None or http_session.closed:
        http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=SUPERVISOR_TIMEOUT)
        )
    return http_session


async def supervisor_request(method: str, endpoint: str, **kwargs) -> Dict:
    """Make a request to the supervisor HTTP API."""
    try:
        session = await get_http_session()
        url = f"{SUPERVISOR_URL}{endpoint}"

        logger.info(f"Making {method} request to supervisor: {url}")

        async with session.request(method, url, **kwargs) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise RuntimeError(f"Supervisor error {response.status}: {error_text}")

            return await response.json()

    except aiohttp.ClientError as e:
        logger.error(f"Failed to connect to supervisor: {e}")
        raise RuntimeError(f"Supervisor communication failed: {str(e)}")


@mcp.tool
async def list_sessions() -> List[Dict]:
    """List all active Claude-Code sessions with their status."""
    try:
        result = await supervisor_request("GET", "/sessions")
        sessions = result.get("sessions", [])

        logger.info(f"Retrieved {len(sessions)} sessions")
        return sessions

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise


@mcp.tool
async def create_session(name: Optional[str] = None, working_dir: Optional[str] = None) -> Dict:
    """
    Create a new Claude-Code session.

    Args:
        name: Optional name for the session (default: auto-generated)
        working_dir: Optional working directory for the session (default: current dir)
    """
    try:
        payload = {}
        if name:
            payload["name"] = name
        if working_dir:
            payload["working_dir"] = working_dir

        result = await supervisor_request("POST", "/sessions", json=payload)

        logger.info(f"Created session: {result.get('session_id')}")
        return result

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise


@mcp.tool
async def send_message(session_id: str, message: str) -> Dict:
    """
    Send a message to a Claude-Code session.

    Args:
        session_id: The ID of the session to send the message to
        message: The message to send to Claude-Code
    """
    try:
        payload = {"message": message}
        result = await supervisor_request("POST", f"/sessions/{session_id}/message", json=payload)

        logger.info(f"Sent message to session {session_id}: {message[:50]}...")
        return result

    except Exception as e:
        logger.error(f"Error sending message to session {session_id}: {e}")
        raise


@mcp.tool
async def get_logs(session_id: str, lines: int = 50) -> Dict:
    """
    Get recent logs from a Claude-Code session.

    Args:
        session_id: The ID of the session to get logs from
        lines: Number of recent log lines to retrieve (default: 50)
    """
    try:
        params = {"lines": lines}
        result = await supervisor_request("GET", f"/sessions/{session_id}/logs", params=params)

        logger.info(f"Retrieved {len(result.get('logs', []))} log lines from session {session_id}")
        return result

    except Exception as e:
        logger.error(f"Error getting logs from session {session_id}: {e}")
        raise


@mcp.tool
async def get_session_status(session_id: str) -> Dict:
    """
    Get detailed status information for a specific session.

    Args:
        session_id: The ID of the session to check
    """
    try:
        result = await supervisor_request("GET", f"/sessions/{session_id}/status")

        logger.info(f"Retrieved status for session {session_id}")
        return result

    except Exception as e:
        logger.error(f"Error getting status for session {session_id}: {e}")
        raise


@mcp.tool
async def terminate_session(session_id: str) -> Dict:
    """
    Terminate a Claude-Code session.

    Args:
        session_id: The ID of the session to terminate
    """
    try:
        result = await supervisor_request("DELETE", f"/sessions/{session_id}")

        logger.info(f"Terminated session {session_id}")
        return result

    except Exception as e:
        logger.error(f"Error terminating session {session_id}: {e}")
        raise


@mcp.tool
async def check_prompts() -> List[Dict]:
    """Check all sessions for interactive prompts that need user attention."""
    try:
        result = await supervisor_request("GET", "/prompts")
        prompts = result.get("prompts", [])

        logger.info(f"Found {len(prompts)} pending prompts")
        return prompts

    except Exception as e:
        logger.error(f"Error checking for prompts: {e}")
        raise


@mcp.tool
async def respond_to_prompt(session_id: str, response: str) -> Dict:
    """
    Respond to an interactive prompt in a Claude-Code session.

    Args:
        session_id: The ID of the session with the prompt
        response: The response to send (e.g., "y", "n", "yes", "no")
    """
    try:
        payload = {"response": response}
        result = await supervisor_request("POST", f"/sessions/{session_id}/respond", json=payload)

        logger.info(f"Sent prompt response to session {session_id}: {response}")
        return result

    except Exception as e:
        logger.error(f"Error responding to prompt in session {session_id}: {e}")
        raise


@mcp.resource(uri="health://supervisor")
async def supervisor_health() -> Dict:
    """Get health status of the supervisor and all sessions."""
    try:
        result = await supervisor_request("GET", "/health")

        return {
            "supervisor_status": "connected",
            "supervisor_health": result,
            "mcp_server_version": "0.1.0",
            "last_check": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error checking supervisor health: {e}")
        return {
            "supervisor_status": "disconnected",
            "error": str(e),
            "mcp_server_version": "0.1.0",
            "last_check": datetime.now().isoformat()
        }


@mcp.resource(uri="sessions://active")
async def active_sessions() -> Dict:
    """Get a summary of all active sessions."""
    try:
        sessions = await list_sessions()

        summary = {
            "total_sessions": len(sessions),
            "active_count": len([s for s in sessions if s.get("status") == "active"]),
            "sessions": sessions,
            "last_updated": datetime.now().isoformat()
        }

        return summary

    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        return {
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }


# Cleanup function for HTTP session
async def cleanup():
    """Cleanup resources when server shuts down."""
    global http_session
    if http_session and not http_session.closed:
        await http_session.close()
        logger.info("HTTP session closed")


if __name__ == "__main__":
    try:
        logger.info(f"Starting Claude-Code MCP Controller")
        logger.info(f"Supervisor URL: {SUPERVISOR_URL}")

        # Register cleanup function
        import atexit
        atexit.register(lambda: asyncio.run(cleanup()) if asyncio.get_event_loop().is_running() else None)

        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        asyncio.run(cleanup())