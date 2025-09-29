"""
Session Manager

Manages multiple Claude-Code sessions and provides the interface
between the MCP server and individual Claude-Code processes.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .claude_wrapper import ClaudeWrapper

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages multiple Claude-Code sessions."""

    def __init__(self):
        self.sessions: Dict[str, ClaudeWrapper] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, name: Optional[str] = None, working_dir: Optional[str] = None) -> str:
        """Create a new Claude-Code session."""
        async with self._lock:
            session_id = f"{name or 'session'}_{str(uuid.uuid4())[:8]}"

            logger.info(f"Creating new session: {session_id}")

            wrapper = ClaudeWrapper(session_id, working_dir)
            success = await wrapper.start()

            if not success:
                raise RuntimeError(f"Failed to start session {session_id}")

            self.sessions[session_id] = wrapper
            logger.info(f"Session {session_id} created successfully")

            return session_id

    async def list_sessions(self) -> List[Dict]:
        """List all active sessions with their status."""
        async with self._lock:
            sessions = []
            for session_id, wrapper in self.sessions.items():
                status = await wrapper.get_status()
                sessions.append(status)

            return sessions

    async def get_session(self, session_id: str) -> Optional[ClaudeWrapper]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

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