"""
Session Manager

Manages multiple Claude-Code sessions and provides the interface
between the MCP server and individual Claude-Code processes.
"""

import asyncio
import logging
import os
import subprocess
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from claude_wrapper import ClaudeWrapper

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages multiple Claude-Code sessions."""

    def __init__(self):
        self.sessions: Dict[str, ClaudeWrapper] = {}
        self._lock = asyncio.Lock()

    async def discover_tmux_sessions(self) -> List[str]:
        """Discover existing tmux sessions named claude-*."""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                logger.info("No tmux sessions found or tmux not running")
                return []

            sessions = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('claude-'):
                    # Extract session name (everything before the first colon)
                    session_name = line.split(':')[0]
                    sessions.append(session_name)
                    logger.info(f"Discovered tmux session: {session_name}")

            return sessions

        except Exception as e:
            logger.error(f"Error discovering tmux sessions: {e}")
            return []

    async def create_session(self, name: Optional[str] = None, working_dir: Optional[str] = None) -> str:
        """Create a new tmux session running Claude-Code."""
        async with self._lock:
            # Use claude- prefix for consistency with discovery
            session_name = f"claude-{name or 'session'}"

            logger.info(f"Creating new tmux session: {session_name}")

            # Create tmux session with claude-code command
            # Try to find claude or claude-code command
            claude_cmd = "claude"  # Default to what the user has installed

            cmd = [
                "tmux", "new-session", "-d", "-s", session_name,
                "-c", working_dir or os.getcwd(),  # Set working directory
                claude_cmd
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                raise RuntimeError(f"Failed to create tmux session {session_name}: {result.stderr}")

            logger.info(f"Tmux session {session_name} created successfully")
            return session_name

    async def list_sessions(self) -> List[Dict]:
        """List all active tmux sessions named claude-* with their status."""
        async with self._lock:
            # Discover existing tmux sessions
            tmux_sessions = await self.discover_tmux_sessions()

            sessions = []
            for session_name in tmux_sessions:
                # Create wrapper for existing session (don't track in self.sessions yet)
                wrapper = ClaudeWrapper(session_name)
                status = await wrapper.get_status()
                sessions.append(status)

            return sessions

    async def get_session(self, session_id: str) -> Optional[ClaudeWrapper]:
        """Get a session by ID from tracked sessions or discover from tmux."""
        # First try tracked sessions
        if session_id in self.sessions:
            return self.sessions[session_id]

        # Check if it's an existing tmux session
        tmux_sessions = await self.discover_tmux_sessions()
        if session_id in tmux_sessions:
            # Create wrapper for existing tmux session
            wrapper = ClaudeWrapper(session_id)
            return wrapper

        return None

    async def send_message(self, session_id: str, message: str) -> Dict:
        """Send a message to a specific session."""
        wrapper = await self.get_session(session_id)
        if not wrapper:
            raise ValueError(f"Session {session_id} not found")

        return await wrapper.send_message(message)

    async def get_logs(self, session_id: str, lines: int = 50, mobile_friendly: bool = False) -> List[str]:
        """Get logs from a specific session with mobile optimization."""
        wrapper = await self.get_session(session_id)
        if not wrapper:
            raise ValueError(f"Session {session_id} not found")

        return await wrapper.get_logs(lines, mobile_friendly)

    async def terminate_session(self, session_id: str) -> bool:
        """Terminate a specific session."""
        async with self._lock:
            wrapper = self.sessions.get(session_id)
            if not wrapper:
                return False

            success = await wrapper.terminate()
            if success:
                del self.sessions[session_id]
                logger.info(f"Session {session_id} terminated and removed")

            return success

    async def check_session_health(self) -> Dict:
        """Check health of all sessions and clean up dead ones."""
        async with self._lock:
            health_report = {
                "total_sessions": len(self.sessions),
                "active_sessions": 0,
                "dead_sessions": 0,
                "cleaned_up": []
            }

            dead_sessions = []

            for session_id, wrapper in self.sessions.items():
                status = await wrapper.get_status()
                if status["status"] == "active":
                    health_report["active_sessions"] += 1
                else:
                    health_report["dead_sessions"] += 1
                    dead_sessions.append(session_id)

            # Clean up dead sessions
            for session_id in dead_sessions:
                del self.sessions[session_id]
                health_report["cleaned_up"].append(session_id)
                logger.info(f"Cleaned up dead session: {session_id}")

            return health_report

    async def check_for_prompts(self) -> List[Dict]:
        """Check all sessions for interactive prompts that need attention."""
        prompts = []

        for session_id, wrapper in self.sessions.items():
            prompt = await wrapper.check_for_prompts()
            if prompt:
                prompts.append({
                    "session_id": session_id,
                    "prompt_text": prompt,
                    "timestamp": datetime.now().isoformat()
                })

        return prompts

    async def respond_to_prompt(self, session_id: str, response: str) -> bool:
        """Respond to an interactive prompt in a session."""
        wrapper = await self.get_session(session_id)
        if not wrapper:
            raise ValueError(f"Session {session_id} not found")

        return await wrapper.respond_to_prompt(response)

    async def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get detailed status of a specific session."""
        wrapper = await self.get_session(session_id)
        if not wrapper:
            return None

        return await wrapper.get_status()

    async def shutdown_all(self) -> Dict:
        """Shutdown all sessions gracefully."""
        shutdown_report = {
            "total_sessions": len(self.sessions),
            "successful_shutdowns": 0,
            "failed_shutdowns": 0,
            "session_results": {}
        }

        for session_id in list(self.sessions.keys()):
            try:
                success = await self.terminate_session(session_id)
                if success:
                    shutdown_report["successful_shutdowns"] += 1
                    shutdown_report["session_results"][session_id] = "success"
                else:
                    shutdown_report["failed_shutdowns"] += 1
                    shutdown_report["session_results"][session_id] = "failed"
            except Exception as e:
                shutdown_report["failed_shutdowns"] += 1
                shutdown_report["session_results"][session_id] = f"error: {str(e)}"
                logger.error(f"Error shutting down session {session_id}: {e}")

        logger.info(f"Shutdown complete: {shutdown_report}")
        return shutdown_report