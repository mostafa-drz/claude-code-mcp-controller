"""
Claude-Code MCP Controller Server

FastMCP-based server that provides MCP tools for controlling Claude-Code sessions
remotely via ChatGPT. Communicates with the local supervisor to manage sessions.

Built following FastMCP 2.0 documentation and best practices.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
from fastmcp import FastMCP

from config import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Claude-Code Controller 🚀")

# HTTP session for supervisor communication
http_session: Optional[aiohttp.ClientSession] = None


async def get_http_session() -> aiohttp.ClientSession:
    """Get or create HTTP session for supervisor communication."""
    global http_session
    if http_session is None or http_session.closed:
        # Disable SSL verification for ngrok/local development
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.SUPERVISOR_TIMEOUT),
            connector=connector
        )
    return http_session


async def supervisor_request(method: str, endpoint: str, **kwargs) -> Dict:
    """Make a request to the supervisor HTTP API."""
    try:
        session = await get_http_session()
        url = f"{config.SUPERVISOR_URL}{endpoint}"

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
async def list_sessions() -> Dict:
    """List all active Claude-Code sessions with their status."""
    try:
        result = await supervisor_request("GET", "/sessions")
        sessions = result.get("sessions", [])

        logger.info(f"Retrieved {len(sessions)} sessions")

        # CHATGPT OPTIMIZATION: Format response for conversation
        if len(sessions) == 0:
            return {
                "message": "No active Claude-Code sessions found.",
                "suggestion": "Create a new session by saying: 'Create a session for my project'",
                "sessions": sessions
            }

        # Format sessions for ChatGPT display
        session_summary = []
        for session in sessions:
            summary = {
                "name": session.get("session_id", "unknown").split("_")[0],  # Cleaner display name
                "status": session.get("status", "unknown"),
                "created": session.get("created_at", "unknown"),
                "directory": session.get("working_dir", "").split("/")[-1] if session.get("working_dir") else "unknown",  # Just folder name
                "full_id": session.get("session_id")  # Keep full ID for operations
            }
            session_summary.append(summary)

        return {
            "message": f"Found {len(sessions)} active Claude-Code session{'s' if len(sessions) != 1 else ''}",
            "sessions": session_summary,
            "total_count": len(sessions)
        }

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return {
            "error": "Failed to retrieve sessions",
            "details": str(e),
            "suggestion": "Check if the supervisor is running and try again"
        }


@mcp.tool
async def create_session(name: Optional[str] = None, working_dir: Optional[str] = None) -> Dict:
    """
    Create a new Claude-Code session optimized for ChatGPT responsiveness.

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
        session_id = result.get('session_id')

        logger.info(f"Created session: {session_id}")

        # CHATGPT OPTIMIZATION: Return user-friendly response
        return {
            "message": f"✅ Created new Claude-Code session '{session_id.split('_')[0] if session_id else name or 'session'}'",
            "session_name": session_id.split('_')[0] if session_id else name or 'session',
            "full_session_id": session_id,
            "working_directory": working_dir or "default",
            "status": "starting up",
            "next_steps": "You can now send commands to this session or check its logs"
        }

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return {
            "error": "Failed to create Claude-Code session",
            "details": str(e),
            "suggestion": "Make sure the supervisor is running and the working directory exists"
        }


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
async def get_logs(session_id: str, lines: int = 50, mobile_format: bool = True) -> Dict:
    """
    Get recent logs from a Claude-Code session, formatted for ChatGPT display.

    Args:
        session_id: The ID of the session to get logs from
        lines: Number of recent log lines to retrieve (default: 50)
        mobile_format: Format logs for mobile ChatGPT app (default: True)
    """
    try:
        # Use mobile_friendly parameter for better ChatGPT mobile display
        params = {"lines": lines, "mobile": "true" if mobile_format else "false"}
        result = await supervisor_request("GET", f"/sessions/{session_id}/logs", params=params)

        logs = result.get('logs', [])
        logger.info(f"Retrieved {len(logs)} log lines from session {session_id}")

        # CHATGPT OPTIMIZATION: Format for conversation
        if not logs:
            return {
                "message": f"No recent activity in session '{session_id.split('_')[0]}'",
                "suggestion": "Send a command to the session to see some activity",
                "logs": []
            }

        # Format logs for ChatGPT with markdown for better mobile display
        formatted_logs = "Recent activity:\n```\n" + "\n".join(logs[-10:]) + "\n```"

        return {
            "message": f"Showing last {min(len(logs), 10)} lines from session '{session_id.split('_')[0]}'",
            "formatted_logs": formatted_logs,
            "raw_logs": logs,
            "session_id": session_id.split('_')[0],  # Clean name for display
            "total_lines": len(logs)
        }

    except Exception as e:
        logger.error(f"Error getting logs from session {session_id}: {e}")
        return {
            "error": f"Could not retrieve logs from session '{session_id.split('_')[0] if '_' in session_id else session_id}'",
            "details": str(e),
            "suggestion": "Check if the session exists with 'list_sessions' tool"
        }


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


@mcp.tool
async def search(query: str, limit: int = 10) -> Dict:
    """
    Search Claude-Code sessions and logs for relevant content.
    
    This is a required tool for ChatGPT MCP connector compatibility.

    Args:
        query: Search query to find relevant sessions or content
        limit: Maximum number of results to return (default: 10)
    """
    try:
        # Get all sessions
        sessions_result = await supervisor_request("GET", "/sessions")
        sessions = sessions_result.get("sessions", [])
        
        matching_sessions = []
        
        for session in sessions[:limit]:
            session_id = session.get("session_id", "")
            working_dir = session.get("working_dir", "")
            
            # Simple text matching for now
            if (query.lower() in session_id.lower() or 
                query.lower() in working_dir.lower()):
                matching_sessions.append({
                    "session_id": session_id,
                    "status": session.get("status"),
                    "working_dir": working_dir,
                    "match_reason": f"Found '{query}' in session ID or directory"
                })
        
        return {
            "query": query,
            "results": matching_sessions,
            "total_matches": len(matching_sessions),
            "message": f"Found {len(matching_sessions)} sessions matching '{query}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching sessions: {e}")
        return {
            "query": query,
            "results": [],
            "total_matches": 0,
            "error": f"Search failed: {str(e)}"
        }


@mcp.tool
async def fetch(url: str) -> Dict:
    """
    Fetch content from Claude-Code session logs or status.
    
    This is a required tool for ChatGPT MCP connector compatibility.

    Args:
        url: Session ID or resource identifier to fetch content from
    """
    try:
        # If URL looks like a session ID, fetch session details
        if "_" in url and len(url.split("_")) == 2:
            # Try to get session status
            try:
                status_result = await supervisor_request("GET", f"/sessions/{url}/status")
                logs_result = await supervisor_request("GET", f"/sessions/{url}/logs?lines=20")
                
                return {
                    "url": url,
                    "content": {
                        "status": status_result,
                        "recent_logs": logs_result.get("logs", [])
                    },
                    "content_type": "session_data",
                    "message": f"Fetched data for session {url}"
                }
            except:
                pass
        
        # Fallback: try to list sessions and find matches
        sessions_result = await supervisor_request("GET", "/sessions")
        sessions = sessions_result.get("sessions", [])
        
        matching_session = None
        for session in sessions:
            if url in session.get("session_id", ""):
                matching_session = session
                break
        
        if matching_session:
            return {
                "url": url,
                "content": matching_session,
                "content_type": "session_info",
                "message": f"Found session information for {url}"
            }
        else:
            return {
                "url": url,
                "content": None,
                "content_type": "not_found",
                "message": f"No session found matching {url}"
            }
            
    except Exception as e:
        logger.error(f"Error fetching content for {url}: {e}")
        return {
            "url": url,
            "content": None,
            "content_type": "error",
            "error": f"Fetch failed: {str(e)}"
        }


@mcp.resource("health://supervisor")
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


@mcp.resource("sessions://active")
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
        logger.info(f"Supervisor URL: {config.SUPERVISOR_URL}")

        # Register cleanup function
        import atexit
        atexit.register(lambda: asyncio.run(cleanup()) if asyncio.get_event_loop().is_running() else None)

        # Use FastMCP's run method with default stdio transport
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        asyncio.run(cleanup())